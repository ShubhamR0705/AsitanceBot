import pytest

from app.api.routes.admin import create_user, deactivate_user, update_user
from app.core.security import hash_password
from app.models.ticket import TicketApprovalStatus, TicketRequestType, TicketStatus
from app.models.user import UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.user import AdminUserCreate, AdminUserUpdate
from app.services.chat_service import ChatService
from app.services.notification_service import NotificationService
from app.services.ticket_service import TicketService


def _escalated_ticket(db, text: str = "I need human support now"):
    user = UserRepository(db).get_by_email("user@company.com")
    result = ChatService(db).submit_message(user, ChatService(db).create_conversation(user).id, text)
    return user, result.ticket


def test_ticket_auto_assigns_to_lowest_loaded_technician(db):
    repository = UserRepository(db)
    user = repository.get_by_email("user@company.com")
    first_technician = repository.get_by_email("tech@company.com")
    second_technician = repository.create(
        email="second.tech@company.com",
        full_name="Second Technician",
        hashed_password=hash_password("TechPass123!"),
        role=UserRole.TECHNICIAN,
    )

    first = ChatService(db).submit_message(user, ChatService(db).create_conversation(user).id, "security issue suspicious login on my account").ticket
    second = ChatService(db).submit_message(user, ChatService(db).create_conversation(user).id, "security issue unauthorized login detected").ticket

    assert first.technician_id == first_technician.id
    assert first.assignment_source == "auto"
    assert first.assigned_at is not None
    assert second.technician_id == second_technician.id


def test_ticket_remains_unassigned_when_no_active_technicians_exist(db):
    repository = UserRepository(db)
    technician = repository.get_by_email("tech@company.com")
    repository.update(technician, {"is_active": False})

    _, ticket = _escalated_ticket(db)

    assert ticket.technician_id is None
    assert ticket.assignment_source is None


def test_admin_can_create_update_and_deactivate_user(db):
    admin = UserRepository(db).get_by_email("admin@company.com")

    created = create_user(
        AdminUserCreate(email="new.tech@company.com", full_name="New Tech", password="StrongPass123!", role=UserRole.TECHNICIAN),
        db,
        admin,
    )
    assert created.role == UserRole.TECHNICIAN

    updated = update_user(created.id, AdminUserUpdate(full_name="New Support Tech", role=UserRole.USER), db, admin)
    assert updated.full_name == "New Support Tech"
    assert updated.role == UserRole.USER

    deactivated = deactivate_user(created.id, db, admin)
    assert deactivated.is_active is False


def test_user_and_assigned_technician_can_chat_on_ticket(db):
    user, ticket = _escalated_ticket(db)
    technician = ticket.technician
    service = TicketService(db)

    user_message = service.add_ticket_message(user, ticket, "I am still blocked.")
    tech_message = service.add_ticket_message(technician, ticket, "I am checking your account now.")
    refreshed = service.get_visible_ticket(user, ticket.id)
    user_titles = [notification.title for notification in NotificationService(db).list_for_user(user)]
    tech_titles = [notification.title for notification in NotificationService(db).list_for_user(technician)]

    assert user_message.sender_role.value == "USER"
    assert tech_message.sender_role.value == "TECHNICIAN"
    assert len(refreshed.ticket_messages) == 2
    assert any("Support replied" in title for title in user_titles)
    assert any("User replied" in title for title in tech_titles)


def test_ticket_chat_blocks_unauthorized_users_and_closed_tickets(db):
    user, ticket = _escalated_ticket(db)
    other_user = UserRepository(db).create(
        email="other.chat@company.com",
        full_name="Other Chat",
        hashed_password=hash_password("UserPass123!"),
        role=UserRole.USER,
    )
    service = TicketService(db)

    with pytest.raises(ValueError):
        service.add_ticket_message(other_user, ticket, "Can I see this?")

    resolved = service.update_ticket(ticket.technician, ticket, {"status": TicketStatus.RESOLVED, "resolution_notes": "Done."})
    with pytest.raises(ValueError):
        service.add_ticket_message(user, resolved, "One more thing")


def test_software_install_request_creates_approval_ticket_and_requires_admin_approval(db):
    user = UserRepository(db).get_by_email("user@company.com")
    admin = UserRepository(db).get_by_email("admin@company.com")
    service = ChatService(db)
    conversation = service.create_conversation(user)

    result = service.submit_message(user, conversation.id, "I need Photoshop installed for design work on my Windows laptop")
    ticket = result.ticket

    assert result.escalated is True
    assert ticket.request_type == TicketRequestType.SOFTWARE_INSTALL
    assert ticket.approval_required is True
    assert ticket.approval_status == TicketApprovalStatus.PENDING_APPROVAL
    assert ticket.requested_software == "Photoshop"
    assert ticket.technician_id is not None

    with pytest.raises(ValueError):
        TicketService(db).update_ticket(ticket.technician, ticket, {"status": TicketStatus.IN_PROGRESS})

    approved = TicketService(db).update_approval(admin, ticket, TicketApprovalStatus.APPROVED, "Approved for design project.")
    assert approved.approval_status == TicketApprovalStatus.APPROVED

    in_progress = TicketService(db).update_ticket(approved.technician, approved, {"status": TicketStatus.IN_PROGRESS})
    assert in_progress.status == TicketStatus.IN_PROGRESS
    assert in_progress.approval_status == TicketApprovalStatus.IN_PROGRESS
