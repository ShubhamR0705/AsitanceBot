from datetime import datetime, timedelta

from app.core.security import hash_password
from app.models.notification import Notification
from app.models.ticket import TicketPriority, TicketStatus
from app.models.user import UserRole
from app.repositories.knowledge_repository import KnowledgeRepository
from app.repositories.user_repository import UserRepository
from app.services.chat_service import ChatService
from app.services.kb_retrieval_service import KBRetrievalService
from app.services.notification_service import NotificationService
from app.services.ticket_service import TicketService


def _escalated_ticket(db, text: str = "I need human support now"):
    user = UserRepository(db).get_by_email("user@company.com")
    conversation = ChatService(db).create_conversation(user)
    result = ChatService(db).submit_message(user, conversation.id, text)
    return user, TicketService(db).get_visible_ticket(user, result.ticket.id)


def test_critical_priority_sla_and_audit_created_on_security_escalation(db):
    _, ticket = _escalated_ticket(db, "security issue malware on my laptop")

    assert ticket.priority == TicketPriority.CRITICAL
    assert ticket.routing_group in {"endpoint", "general"}
    assert ticket.sla_due_at is not None
    assert ticket.audit_logs
    assert {entry.action_type.value for entry in ticket.audit_logs} >= {"TICKET_CREATED", "ESCALATION_TRIGGERED"}


def test_technician_assignment_sets_first_response_audit_and_notifications(db):
    _, ticket = _escalated_ticket(db)
    technician = UserRepository(db).get_by_email("tech@company.com")

    updated = TicketService(db).update_ticket(technician, ticket, {"status": TicketStatus.IN_PROGRESS})

    assert updated.technician_id == technician.id
    assert updated.first_response_at is not None
    assert any(entry.action_type.value == "TICKET_ASSIGNED" for entry in updated.audit_logs)
    assert any(notification.recipient_user_id == technician.id for notification in updated.notifications)


def test_notifications_are_role_scoped_after_critical_escalation(db):
    user, ticket = _escalated_ticket(db, "security issue suspicious login detected")
    technician = UserRepository(db).get_by_email("tech@company.com")
    admin = UserRepository(db).get_by_email("admin@company.com")
    notifications = NotificationService(db)

    user_titles = [notification.title for notification in notifications.list_for_user(user)]
    technician_titles = [notification.title for notification in notifications.list_for_user(technician)]
    admin_titles = [notification.title for notification in notifications.list_for_user(admin)]

    assert any("created" in title.lower() for title in user_titles)
    assert not any("new escalated ticket" in title.lower() for title in user_titles)
    assert any("new escalated ticket" in title.lower() for title in technician_titles)
    assert not any("your issue was escalated" in notification.body.lower() for notification in notifications.list_for_user(technician))
    assert any("critical ticket" in title.lower() for title in admin_titles)
    assert not any(title.startswith("Ticket #") and "created" in title.lower() for title in admin_titles)


def test_notification_mark_read_blocks_cross_role_access(db):
    user, _ = _escalated_ticket(db)
    technician = UserRepository(db).get_by_email("tech@company.com")
    notification = NotificationService(db).list_for_user(user)[0]

    assert NotificationService(db).mark_read(technician, notification.id) is None


def test_user_does_not_see_notification_for_another_users_ticket(db):
    user, ticket = _escalated_ticket(db)
    other_user = UserRepository(db).create(
        email="other.user@company.com",
        full_name="Other User",
        hashed_password=hash_password("OtherPass123!"),
        role=UserRole.USER,
    )
    db.add(
        Notification(
            recipient_user_id=other_user.id,
            ticket_id=ticket.id,
            title="Mis-targeted ticket update",
            body="This should be filtered because the ticket belongs to another user.",
        )
    )
    db.commit()

    assert NotificationService(db).list_for_user(other_user) == []
    assert NotificationService(db).list_for_user(user)


def test_sla_breach_notifies_technician_and_admin_not_user(db):
    user, ticket = _escalated_ticket(db)
    technician = UserRepository(db).get_by_email("tech@company.com")
    admin = UserRepository(db).get_by_email("admin@company.com")
    service = TicketService(db)
    assigned = service.update_ticket(technician, ticket, {"status": TicketStatus.IN_PROGRESS})
    assigned.sla_due_at = datetime.utcnow() - timedelta(hours=1)
    db.add(assigned)
    db.commit()
    db.refresh(assigned)

    service.update_ticket(technician, assigned, {"internal_notes": "Checking breached ticket."})

    user_titles = [notification.title for notification in NotificationService(db).list_for_user(user)]
    technician_titles = [notification.title for notification in NotificationService(db).list_for_user(technician)]
    admin_titles = [notification.title for notification in NotificationService(db).list_for_user(admin)]
    assert not any("sla breached" in title.lower() for title in user_titles)
    assert any("sla breached" in title.lower() for title in technician_titles)
    assert any("sla breached" in title.lower() for title in admin_titles)


def test_reopen_flow_preserves_history_and_tracks_audit(db):
    user, ticket = _escalated_ticket(db)
    technician = UserRepository(db).get_by_email("tech@company.com")
    service = TicketService(db)

    resolved = service.update_ticket(technician, ticket, {"status": TicketStatus.RESOLVED, "resolution_notes": "Reset completed."})
    reopened = service.reopen_ticket(user, resolved, "Still cannot access payroll.")

    assert reopened.status == TicketStatus.REOPENED
    assert reopened.reopen_count == 1
    assert reopened.last_reopened_at is not None
    assert any(entry.action_type.value == "TICKET_REOPENED" for entry in reopened.audit_logs)


def test_message_helpfulness_feedback_is_stored(db):
    user, _ = _escalated_ticket(db)
    conversation = ChatService(db).list_user_conversations(user)[0]
    assistant_message = next(message for message in conversation.messages if message.sender.value == "ASSISTANT")

    feedback = ChatService(db).record_message_feedback(user, assistant_message.id, helpful=False, note="Needed a person")

    assert feedback.helpful is False
    assert feedback.message_id == assistant_message.id


def test_knowledge_base_usage_and_delete(db):
    repository = KnowledgeRepository(db)
    entry = repository.create("VPN", "Temporary VPN route", "Reconnect with the approved VPN client.", "vpn,route")

    repository.increment_usage([entry])
    updated = repository.get(entry.id)
    assert updated.usage_count == 1

    repository.delete(updated)
    assert repository.get(entry.id) is None


def test_enriched_knowledge_base_seed_has_real_world_coverage(db):
    entries = KnowledgeRepository(db).list_active()
    categories = {entry.category for entry in entries}

    assert len(entries) >= 55
    assert {"ACCESS", "PASSWORD", "VPN", "WIFI", "NETWORK", "EMAIL", "DEVICE_PERFORMANCE", "BROWSER", "SOFTWARE", "PRINTER", "GENERAL"}.issubset(categories)
    assert any("Subcategory:" in entry.content and "Escalate when:" in entry.content for entry in entries)


def test_enriched_knowledge_base_retrieves_specific_scenarios(db):
    retrieval = KBRetrievalService(db)

    cases = [
        ("reset link not received", "PASSWORD", "Password reset email or link not received"),
        ("vpn disconnecting every few minutes", "VPN", "VPN disconnects every few minutes"),
        ("ubuntu wifi networks not showing", "WIFI", "No WiFi networks visible"),
        ("payroll portal access issue", "GENERAL", "Payroll portal access issue"),
    ]
    for query, category, expected_title in cases:
        titles = [entry.title for entry in retrieval.retrieve(query, category, limit=3)]
        assert expected_title in titles
