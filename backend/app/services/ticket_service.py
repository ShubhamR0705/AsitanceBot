from datetime import datetime

from sqlalchemy.orm import Session

from app.models.audit_log import AuditAction
from app.models.conversation import ConversationStatus, MessageSender
from app.models.ticket import Ticket, TicketPriority, TicketStatus
from app.models.user import User, UserRole
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.ticket_repository import TicketRepository
from app.repositories.user_repository import UserRepository
from app.services.audit_service import AuditService
from app.services.notification_service import NotificationService
from app.services.support_operations_service import SupportOperationsService


class TicketService:
    def __init__(self, db: Session):
        self.db = db
        self.tickets = TicketRepository(db)
        self.conversations = ConversationRepository(db)
        self.users = UserRepository(db)
        self.audit = AuditService(db)
        self.notifications = NotificationService(db)
        self.operations = SupportOperationsService()

    def list_for_user(self, user: User) -> list[Ticket]:
        return self.tickets.list_for_user(user.id)

    def list_queue(self) -> list[Ticket]:
        return self.tickets.list_queue()

    def list_all(self) -> list[Ticket]:
        return self.tickets.list_all()

    def get_visible_ticket(self, current_user: User, ticket_id: int) -> Ticket | None:
        ticket = self.tickets.get(ticket_id)
        if ticket is None:
            return None
        if current_user.role == UserRole.USER and ticket.user_id != current_user.id:
            return None
        return ticket

    def update_ticket(self, current_user: User, ticket: Ticket, data: dict) -> Ticket:
        previous = self._snapshot(ticket)
        if data.get("technician_id") is not None:
            data["technician_id"] = self._authorized_technician_id(current_user, data["technician_id"])
        elif current_user.role == UserRole.TECHNICIAN and ticket.technician_id is None:
            data["technician_id"] = current_user.id

        if data.get("priority") is not None:
            data["sla_due_at"] = self.operations.sla_due_at(data["priority"], ticket.created_at)
            data["sla_breached"] = False

        if self._is_first_response_action(data) and ticket.first_response_at is None:
            data["first_response_at"] = datetime.utcnow()

        updated = self.tickets.update(
            ticket,
            data,
            technician_id=data.get("technician_id"),
        )
        was_breached = previous["sla_breached"]
        is_breached = self.operations.refresh_sla_state(updated)
        if is_breached != was_breached:
            updated = self.tickets.update(updated, {"sla_breached": is_breached})
            if is_breached:
                self.audit.record(
                    action=AuditAction.SLA_BREACHED,
                    ticket_id=updated.id,
                    actor=current_user,
                    previous_value={"sla_breached": was_breached},
                    new_value={"sla_breached": True},
                    summary="Ticket breached its SLA target.",
                )
                self._notify_sla_breach(updated, current_user)
        self._record_update_audit(current_user, updated, previous, data)
        self._send_update_notifications(current_user, updated, previous, data)
        if updated.conversation_id and data.get("resolution_notes"):
            conversation = self.conversations.get(updated.conversation_id)
            if conversation:
                self.conversations.add_message(
                    conversation,
                    sender=MessageSender.TECHNICIAN,
                    content=data["resolution_notes"],
                    meta={"ticket_id": updated.id, "status": updated.status.value},
                )
        if updated.conversation_id and updated.status in {TicketStatus.RESOLVED, TicketStatus.CLOSED}:
            conversation = self.conversations.get(updated.conversation_id)
            if conversation and conversation.status.value != "RESOLVED":
                self.conversations.update_state(conversation, status=ConversationStatus.RESOLVED)
        return self.tickets.get(updated.id) or updated

    def reopen_ticket(self, current_user: User, ticket: Ticket, note: str | None = None) -> Ticket:
        if current_user.role == UserRole.USER and ticket.user_id != current_user.id:
            raise ValueError("Ticket not found")
        if ticket.status not in {TicketStatus.RESOLVED, TicketStatus.CLOSED}:
            raise ValueError("Only resolved or closed tickets can be reopened")

        previous = self._snapshot(ticket)
        updated = self.tickets.update(
            ticket,
            {
                "status": TicketStatus.REOPENED,
                "resolved_at": None,
                "reopen_count": ticket.reopen_count + 1,
                "last_reopened_at": datetime.utcnow(),
                "sla_due_at": self.operations.sla_due_at(ticket.priority),
                "sla_breached": False,
                "internal_notes": ticket.internal_notes,
            },
        )
        if updated.conversation_id:
            conversation = self.conversations.get(updated.conversation_id)
            if conversation:
                self.conversations.update_state(conversation, status=ConversationStatus.ESCALATED)
                if note:
                    self.conversations.add_message(
                        conversation,
                        sender=MessageSender.USER if current_user.role == UserRole.USER else MessageSender.TECHNICIAN,
                        content=f"Reopen note: {note}",
                        meta={"ticket_id": updated.id, "reopened": True},
                    )
        self.audit.record(
            action=AuditAction.TICKET_REOPENED,
            ticket_id=updated.id,
            actor=current_user,
            previous_value=previous,
            new_value=self._snapshot(updated),
            summary="Ticket reopened for follow-up.",
        )
        self.notifications.notify(
            recipient=updated.user,
            actor=current_user,
            ticket=updated,
            title=f"Ticket #{updated.id} reopened",
            body="The ticket was reopened and support can continue from the existing history.",
        )
        if updated.technician:
            self.notifications.notify(
                recipient=updated.technician,
                actor=current_user,
                ticket=updated,
                title=f"Ticket #{updated.id} reopened",
                body="A previously resolved ticket was reopened for follow-up.",
            )
        else:
            self.notifications.notify_technicians(
                actor=current_user,
                ticket=updated,
                title=f"Ticket #{updated.id} reopened in queue",
                body="A previously resolved ticket was reopened and is waiting in the support queue.",
            )
        if updated.priority == TicketPriority.CRITICAL:
            self.notifications.notify_admins(
                actor=current_user,
                ticket=updated,
                title=f"Critical ticket #{updated.id} reopened",
                body="A critical ticket was reopened and may need operational review.",
            )
        return self.tickets.get(updated.id) or updated

    def _authorized_technician_id(self, current_user: User, technician_id: int) -> int:
        if current_user.role == UserRole.TECHNICIAN:
            if technician_id != current_user.id:
                raise ValueError("Technicians can only assign tickets to themselves")
            return current_user.id
        technician = self.users.get(technician_id)
        if technician is None or technician.role != UserRole.TECHNICIAN:
            raise ValueError("Technician not found")
        return technician.id

    def _is_first_response_action(self, data: dict) -> bool:
        return any(data.get(field) is not None for field in ["status", "internal_notes", "resolution_notes", "technician_id"])

    def _snapshot(self, ticket: Ticket) -> dict:
        return {
            "status": ticket.status.value,
            "priority": ticket.priority.value,
            "technician_id": ticket.technician_id,
            "routing_group": ticket.routing_group,
            "sla_breached": ticket.sla_breached,
            "reopen_count": ticket.reopen_count,
        }

    def _record_update_audit(self, current_user: User, ticket: Ticket, previous: dict, data: dict) -> None:
        current = self._snapshot(ticket)
        if previous.get("technician_id") != current.get("technician_id"):
            self.audit.record(
                action=AuditAction.TICKET_ASSIGNED,
                ticket_id=ticket.id,
                actor=current_user,
                previous_value={"technician_id": previous.get("technician_id")},
                new_value={"technician_id": current.get("technician_id")},
                summary="Ticket assignment changed.",
            )
        if previous.get("status") != current.get("status"):
            self.audit.record(
                action=AuditAction.STATUS_UPDATED,
                ticket_id=ticket.id,
                actor=current_user,
                previous_value={"status": previous.get("status")},
                new_value={"status": current.get("status")},
                summary="Ticket status updated.",
            )
        if previous.get("priority") != current.get("priority"):
            self.audit.record(
                action=AuditAction.PRIORITY_UPDATED,
                ticket_id=ticket.id,
                actor=current_user,
                previous_value={"priority": previous.get("priority")},
                new_value={"priority": current.get("priority")},
                summary="Ticket priority updated.",
            )
        if data.get("internal_notes"):
            self.audit.record(
                action=AuditAction.NOTES_ADDED,
                ticket_id=ticket.id,
                actor=current_user,
                new_value={"internal_notes_added": True},
                summary="Internal notes added.",
            )
        if data.get("resolution_notes"):
            self.audit.record(
                action=AuditAction.RESOLUTION_ADDED,
                ticket_id=ticket.id,
                actor=current_user,
                new_value={"resolution_notes_added": True},
                summary="Resolution or user-facing note added.",
            )

    def _send_update_notifications(self, current_user: User, ticket: Ticket, previous: dict, data: dict) -> None:
        if previous.get("technician_id") != ticket.technician_id and ticket.technician:
            self.notifications.notify(
                recipient=ticket.technician,
                actor=current_user,
                ticket=ticket,
                title=f"Ticket #{ticket.id} assigned",
                body=f"You were assigned a {ticket.priority.value.lower()} priority {ticket.category.replace('_', ' ').lower()} ticket.",
            )
        if previous.get("status") != ticket.status.value:
            self.notifications.notify(
                recipient=ticket.user,
                actor=current_user,
                ticket=ticket,
                title=f"Ticket #{ticket.id} status changed",
                body=f"Status changed from {previous.get('status')} to {ticket.status.value}.",
            )
            if ticket.technician and current_user.id != ticket.technician_id:
                self.notifications.notify(
                    recipient=ticket.technician,
                    actor=current_user,
                    ticket=ticket,
                    title=f"Ticket #{ticket.id} status changed",
                    body=f"Status changed from {previous.get('status')} to {ticket.status.value}.",
                    email=False,
                )
        if data.get("resolution_notes"):
            self.notifications.notify(
                recipient=ticket.user,
                actor=current_user,
                ticket=ticket,
                title=f"Ticket #{ticket.id} updated",
                body="Support added a resolution or next step to your ticket.",
            )
        if data.get("priority") == TicketPriority.CRITICAL and previous.get("priority") != TicketPriority.CRITICAL.value:
            self.notifications.notify_admins(
                actor=current_user,
                ticket=ticket,
                title=f"Ticket #{ticket.id} marked critical",
                body="A ticket priority was raised to critical.",
            )

    def _notify_sla_breach(self, ticket: Ticket, actor: User) -> None:
        title = f"SLA breached for ticket #{ticket.id}"
        body = "This ticket is past its SLA target and needs operational attention."
        if ticket.technician:
            self.notifications.notify(recipient=ticket.technician, actor=actor, ticket=ticket, title=title, body=body, email=False)
        else:
            self.notifications.notify_technicians(actor=actor, ticket=ticket, title=title, body=body)
        self.notifications.notify_admins(actor=actor, ticket=ticket, title=title, body=body)
