from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.conversation import Conversation
from app.models.ticket import Ticket, TicketApprovalStatus, TicketPriority, TicketRequestType, TicketStatus
from app.models.ticket_message import TicketMessage


class TicketRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, ticket_id: int) -> Ticket | None:
        return self.db.scalar(
            select(Ticket)
            .options(
                selectinload(Ticket.conversation),
                selectinload(Ticket.conversation).selectinload(Conversation.messages),
                selectinload(Ticket.user),
                selectinload(Ticket.technician),
                selectinload(Ticket.approved_by),
                selectinload(Ticket.ticket_messages).selectinload(TicketMessage.sender),
                selectinload(Ticket.audit_logs),
            )
            .where(Ticket.id == ticket_id)
        )

    def get_by_conversation_id(self, conversation_id: int) -> Ticket | None:
        return self.db.scalar(select(Ticket).where(Ticket.conversation_id == conversation_id))

    def list_for_user(self, user_id: int) -> list[Ticket]:
        return list(
            self.db.scalars(
                select(Ticket)
                .options(selectinload(Ticket.conversation), selectinload(Ticket.technician), selectinload(Ticket.approved_by))
                .where(Ticket.user_id == user_id)
                .order_by(Ticket.updated_at.desc())
            )
        )

    def list_queue(self) -> list[Ticket]:
        actionable = [TicketStatus.OPEN, TicketStatus.ESCALATED, TicketStatus.REOPENED, TicketStatus.IN_PROGRESS, TicketStatus.WAITING_FOR_USER]
        return list(
            self.db.scalars(
                select(Ticket)
                .options(selectinload(Ticket.user), selectinload(Ticket.technician), selectinload(Ticket.approved_by))
                .where(Ticket.status.in_(actionable))
                .order_by(Ticket.created_at.desc())
            )
        )

    def list_all(self) -> list[Ticket]:
        return list(
            self.db.scalars(
                select(Ticket)
                .options(selectinload(Ticket.user), selectinload(Ticket.technician), selectinload(Ticket.approved_by))
                .order_by(Ticket.created_at.desc())
            )
        )

    def create_escalated(
        self,
        *,
        conversation_id: int,
        user_id: int,
        category: str,
        title: str,
        description: str,
        priority: TicketPriority = TicketPriority.MEDIUM,
        routing_group: str = "general",
        sla_due_at: datetime | None = None,
        request_type: TicketRequestType = TicketRequestType.SUPPORT,
        requested_software: str | None = None,
        request_reason: str | None = None,
        request_device: str | None = None,
        approval_required: bool = False,
        approval_status: TicketApprovalStatus = TicketApprovalStatus.NOT_REQUIRED,
    ) -> Ticket:
        existing = self.get_by_conversation_id(conversation_id)
        if existing:
            return existing

        ticket = Ticket(
            conversation_id=conversation_id,
            user_id=user_id,
            category=category,
            title=title[:180],
            description=description,
            status=TicketStatus.ESCALATED,
            priority=priority,
            routing_group=routing_group,
            sla_due_at=sla_due_at,
            request_type=request_type,
            requested_software=requested_software,
            request_reason=request_reason,
            request_device=request_device,
            approval_required=approval_required,
            approval_status=approval_status,
        )
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def create(
        self,
        *,
        user_id: int,
        category: str,
        title: str,
        description: str,
        status: TicketStatus = TicketStatus.OPEN,
        priority: TicketPriority = TicketPriority.MEDIUM,
        routing_group: str = "general",
        sla_due_at: datetime | None = None,
        request_type: TicketRequestType = TicketRequestType.SUPPORT,
        requested_software: str | None = None,
        request_reason: str | None = None,
        request_device: str | None = None,
        approval_required: bool = False,
        approval_status: TicketApprovalStatus = TicketApprovalStatus.NOT_REQUIRED,
        conversation_id: int | None = None,
    ) -> Ticket:
        ticket = Ticket(
            conversation_id=conversation_id,
            user_id=user_id,
            category=category,
            title=title[:180],
            description=description,
            status=status,
            priority=priority,
            routing_group=routing_group,
            sla_due_at=sla_due_at,
            request_type=request_type,
            requested_software=requested_software,
            request_reason=request_reason,
            request_device=request_device,
            approval_required=approval_required,
            approval_status=approval_status,
        )
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def update(self, ticket: Ticket, data: dict) -> Ticket:
        status = data.get("status")
        if status is not None:
            ticket.status = status
            if status in {TicketStatus.RESOLVED, TicketStatus.CLOSED} and ticket.resolved_at is None:
                ticket.resolved_at = datetime.utcnow()
        if "technician_id" in data:
            ticket.technician_id = data["technician_id"]
        for field in (
            "assignment_source",
            "assigned_at",
            "request_type",
            "requested_software",
            "request_reason",
            "request_device",
            "approval_required",
            "approval_status",
            "approved_by_id",
            "approved_at",
            "approval_notes",
            "internal_notes",
            "resolution_notes",
            "priority",
            "routing_group",
            "sla_due_at",
            "sla_breached",
            "first_response_at",
            "resolved_at",
            "reopen_count",
            "last_reopened_at",
            "reopened_from_ticket_id",
        ):
            if field in data:
                setattr(ticket, field, data[field])
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket
