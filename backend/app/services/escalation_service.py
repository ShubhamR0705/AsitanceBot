from sqlalchemy.orm import Session

from app.models.audit_log import AuditAction
from app.models.conversation import Conversation, MessageSender
from app.models.ticket import Ticket
from app.repositories.user_repository import UserRepository
from app.repositories.ticket_repository import TicketRepository
from app.services.audit_service import AuditService
from app.services.notification_service import NotificationService
from app.services.support_operations_service import SupportOperationsService
from app.services.chat_intent_service import ChatIntentService, ChatIntentType


class EscalationService:
    def __init__(self, db: Session):
        self.db = db
        self.ticket_repository = TicketRepository(db)
        self.operations = SupportOperationsService()
        self.audit = AuditService(db)
        self.notifications = NotificationService(db)
        self.intent_router = ChatIntentService()

    def escalate(self, conversation: Conversation, summary: str | None = None) -> Ticket:
        issue_summary = self._issue_summary(conversation)
        title = self._build_title(conversation.category or "GENERAL", issue_summary)
        description = self._build_description(conversation, issue_summary, summary)
        priority = self.operations.determine_priority(
            category=conversation.category or "GENERAL",
            text=f"{issue_summary}\n{summary or ''}",
            triage=conversation.last_triage,
        )
        ticket = self.ticket_repository.create_escalated(
            conversation_id=conversation.id,
            user_id=conversation.user_id,
            category=conversation.category or "GENERAL",
            title=title,
            description=description,
            priority=priority,
            routing_group=self.operations.routing_group_for_category(conversation.category or "GENERAL"),
            sla_due_at=self.operations.sla_due_at(priority),
        )
        self.audit.record(
            action=AuditAction.TICKET_CREATED,
            ticket_id=ticket.id,
            summary="Ticket created from AI escalation.",
            new_value={"status": ticket.status.value, "priority": ticket.priority.value, "routing_group": ticket.routing_group},
        )
        self.audit.record(
            action=AuditAction.ESCALATION_TRIGGERED,
            ticket_id=ticket.id,
            summary="AI support flow escalated this conversation.",
            new_value={"failure_count": conversation.failure_count, "category": conversation.category},
        )
        user = UserRepository(self.db).get(conversation.user_id)
        if user:
            self.notifications.notify(
                recipient=user,
                ticket=ticket,
                title=f"Ticket #{ticket.id} created",
                body="Your issue was escalated with the conversation context attached.",
                email=True,
            )
        return ticket

    def _build_title(self, category: str, issue_summary: str) -> str:
        clean_summary = " ".join(issue_summary.split())
        return f"{category.replace('_', ' ').title()}: {clean_summary[:110]}"

    def _issue_summary(self, conversation: Conversation) -> str:
        fallback = "IT support issue"
        for message in reversed(conversation.messages):
            if message.sender != MessageSender.USER:
                continue
            fallback = message.content or fallback
            intent = self.intent_router.route(message.content or "")
            if intent.intent_type == ChatIntentType.SUPPORT_REQUEST:
                return intent.cleaned_text or message.content or fallback
        return fallback

    def _build_description(self, conversation: Conversation, issue_summary: str, summary: str | None = None) -> str:
        history = "\n".join(
            f"{message.sender.value}: {message.content}"
            for message in conversation.messages
        )
        handoff_summary = summary or conversation.escalation_summary
        return (
            f"AI escalation after {conversation.failure_count} unresolved attempts.\n\n"
            f"Category: {conversation.category or 'GENERAL'}\n"
            f"Original issue: {issue_summary}\n\n"
            f"Technician summary:\n{handoff_summary or 'No structured summary available.'}\n\n"
            f"Conversation history:\n{history}"
        )
