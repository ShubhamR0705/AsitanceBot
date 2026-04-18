from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.ticket import TicketApprovalStatus, TicketPriority, TicketRequestType, TicketStatus
from app.models.ticket_message import TicketMessageSenderRole
from app.schemas.conversation import ConversationRead
from app.schemas.user import UserRead


class AuditLogRead(BaseModel):
    id: int
    ticket_id: int | None
    actor_user_id: int | None
    action_type: str
    previous_value: dict | None
    new_value: dict | None
    summary: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TicketMessageRead(BaseModel):
    id: int
    ticket_id: int
    sender_id: int | None
    sender_role: TicketMessageSenderRole
    content: str
    created_at: datetime
    sender: UserRead | None = None

    model_config = ConfigDict(from_attributes=True)


class TicketRead(BaseModel):
    id: int
    conversation_id: int | None
    user_id: int
    technician_id: int | None
    category: str
    title: str
    description: str
    routing_group: str
    status: TicketStatus
    priority: TicketPriority
    request_type: TicketRequestType
    assignment_source: str | None
    assigned_at: datetime | None
    requested_software: str | None
    request_reason: str | None
    request_device: str | None
    approval_required: bool
    approval_status: TicketApprovalStatus
    approved_by_id: int | None
    approved_at: datetime | None
    approval_notes: str | None
    internal_notes: str | None
    resolution_notes: str | None
    first_response_at: datetime | None
    sla_due_at: datetime | None
    sla_breached: bool
    reopened_from_ticket_id: int | None
    reopen_count: int
    last_reopened_at: datetime | None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None
    user: UserRead | None = None
    technician: UserRead | None = None
    approved_by: UserRead | None = None

    model_config = ConfigDict(from_attributes=True)


class TicketDetail(TicketRead):
    conversation: ConversationRead | None = None
    audit_logs: list[AuditLogRead] = []
    ticket_messages: list[TicketMessageRead] = []


class TicketUpdate(BaseModel):
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    technician_id: int | None = None
    routing_group: str | None = Field(default=None, max_length=80)
    internal_notes: str | None = Field(default=None, max_length=5000)
    resolution_notes: str | None = Field(default=None, max_length=5000)


class TicketReopenRequest(BaseModel):
    note: str | None = Field(default=None, max_length=1000)


class TicketMessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=4000)


class TicketApprovalUpdate(BaseModel):
    approval_status: TicketApprovalStatus
    approval_notes: str | None = Field(default=None, max_length=2000)
