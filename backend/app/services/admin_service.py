from collections import Counter

from sqlalchemy.orm import Session

from app.models.conversation import Conversation, ConversationStatus
from app.models.message_feedback import MessageFeedback
from app.models.ticket import Ticket, TicketStatus
from app.models.user import User


class AdminService:
    def __init__(self, db: Session):
        self.db = db

    def analytics(self) -> dict:
        tickets = self.db.query(Ticket).all()
        conversations = self.db.query(Conversation).all()
        total_users = self.db.query(User).count()
        status_breakdown = Counter(ticket.status.value for ticket in tickets)
        category_breakdown = Counter(ticket.category for ticket in tickets)
        approval_breakdown = Counter(ticket.approval_status.value for ticket in tickets if ticket.approval_required)
        stage_breakdown = Counter(conversation.triage_stage.value for conversation in conversations)
        urgency_breakdown = Counter((conversation.last_triage or {}).get("urgency_level", "unknown") for conversation in conversations)
        escalation_reason_breakdown = Counter(
            (conversation.last_triage or {}).get("reason", "Not escalated")
            for conversation in conversations
            if conversation.status == ConversationStatus.ESCALATED
        )
        technician_workload = Counter(
            ticket.technician.email if ticket.technician else "Unassigned"
            for ticket in tickets
            if ticket.status in {TicketStatus.OPEN, TicketStatus.ESCALATED, TicketStatus.REOPENED, TicketStatus.IN_PROGRESS, TicketStatus.WAITING_FOR_USER}
        )
        technician_workload_detail: dict[str, dict[str, int]] = {}
        for ticket in tickets:
            assignee = ticket.technician.email if ticket.technician else "Unassigned"
            bucket = technician_workload_detail.setdefault(assignee, {"open": 0, "resolved": 0, "total": 0})
            bucket["total"] += 1
            if ticket.status in {TicketStatus.RESOLVED, TicketStatus.CLOSED}:
                bucket["resolved"] += 1
            else:
                bucket["open"] += 1
        low_confidence_conversations = sum(
            1 for conversation in conversations if float((conversation.last_triage or {}).get("confidence", 1.0) or 1.0) < 0.5
        )
        clarification_requested = stage_breakdown.get("CLARIFYING", 0)
        kb_article_usage: Counter[str] = Counter()
        kb_article_outcomes: dict[str, dict[str, int]] = {}
        kb_shown_conversations = 0
        kb_escalated_conversations = 0
        for conversation in conversations:
            titles_seen_in_conversation: set[str] = set()
            for message in conversation.messages:
                if not message.meta:
                    continue
                for title in message.meta.get("kb_titles", []) or []:
                    kb_article_usage[title] += 1
                    titles_seen_in_conversation.add(title)
            for title in titles_seen_in_conversation:
                kb_shown_conversations += 1
                if conversation.status == ConversationStatus.ESCALATED:
                    kb_escalated_conversations += 1
                outcome = kb_article_outcomes.setdefault(title, {"shown": 0, "resolved": 0, "escalated": 0, "unresolved_feedback": 0})
                outcome["shown"] += 1
                if conversation.status == ConversationStatus.RESOLVED:
                    outcome["resolved"] += 1
                if conversation.status == ConversationStatus.ESCALATED:
                    outcome["escalated"] += 1
                if conversation.failure_count > 0:
                    outcome["unresolved_feedback"] += 1
        resolved_durations = [
            (ticket.resolved_at - ticket.created_at).total_seconds() / 3600
            for ticket in tickets
            if ticket.resolved_at is not None
        ]
        feedback = self.db.query(MessageFeedback).all()
        message_feedback = {
            "helpful": sum(1 for item in feedback if item.helpful),
            "not_helpful": sum(1 for item in feedback if not item.helpful),
        }
        return {
            "total_users": total_users,
            "total_tickets": len(tickets),
            "open_tickets": status_breakdown.get(TicketStatus.OPEN.value, 0),
            "escalated_tickets": status_breakdown.get(TicketStatus.ESCALATED.value, 0),
            "resolved_tickets": status_breakdown.get(TicketStatus.RESOLVED.value, 0),
            "assigned_tickets": sum(1 for ticket in tickets if ticket.technician_id is not None),
            "unassigned_tickets": sum(1 for ticket in tickets if ticket.technician_id is None),
            "pending_approvals": approval_breakdown.get("PENDING_APPROVAL", 0),
            "active_conversations": sum(1 for conversation in conversations if conversation.status == ConversationStatus.ACTIVE),
            "avg_resolution_hours": round(sum(resolved_durations) / len(resolved_durations), 2) if resolved_durations else None,
            "kb_failure_rate": round(kb_escalated_conversations / kb_shown_conversations, 2) if kb_shown_conversations else 0.0,
            "low_confidence_conversations": low_confidence_conversations,
            "clarification_requested": clarification_requested,
            "status_breakdown": dict(status_breakdown),
            "category_breakdown": dict(category_breakdown),
            "approval_breakdown": dict(approval_breakdown),
            "stage_breakdown": dict(stage_breakdown),
            "urgency_breakdown": dict(urgency_breakdown),
            "escalation_reason_breakdown": dict(escalation_reason_breakdown),
            "kb_article_usage": dict(kb_article_usage),
            "kb_article_outcomes": kb_article_outcomes,
            "technician_workload": dict(technician_workload),
            "technician_workload_detail": technician_workload_detail,
            "message_feedback": message_feedback,
        }
