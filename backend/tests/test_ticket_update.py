from app.models.ticket import TicketStatus
from app.repositories.user_repository import UserRepository
from app.services.chat_service import ChatService
from app.services.ticket_service import TicketService


def create_escalated_ticket(db):
    user = UserRepository(db).get_by_email("user@company.com")
    chat = ChatService(db)
    conversation = chat.create_conversation(user)
    chat.submit_message(user, conversation.id, "Outlook email will not sync on my laptop")
    chat.submit_message(user, conversation.id, "I use Outlook. Webmail works. It is a sync issue. Error says sync failed.")
    chat.record_feedback(user, conversation.id, resolved=False)
    escalation = chat.record_feedback(user, conversation.id, resolved=False)
    return escalation.ticket


def test_technician_updates_ticket_status_and_resolution(db):
    ticket = create_escalated_ticket(db)
    technician = UserRepository(db).get_by_email("tech@company.com")
    service = TicketService(db)

    progress = service.update_ticket(
        technician,
        ticket,
        {"status": TicketStatus.IN_PROGRESS, "internal_notes": "Checking mail profile state."},
    )
    assert progress.status == TicketStatus.IN_PROGRESS
    assert progress.technician_id == technician.id

    resolved = service.update_ticket(
        technician,
        progress,
        {"status": TicketStatus.RESOLVED, "resolution_notes": "Rebuilt the mail profile and confirmed sync."},
    )
    assert resolved.status == TicketStatus.RESOLVED
    assert "Rebuilt" in resolved.resolution_notes
