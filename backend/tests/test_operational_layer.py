from app.models.ticket import TicketPriority, TicketStatus
from app.repositories.knowledge_repository import KnowledgeRepository
from app.repositories.user_repository import UserRepository
from app.services.chat_service import ChatService
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
