from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.ticket import TicketPriority, TicketStatus
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

    model_config = ConfigDict(from_attributes=True)


class TicketDetail(TicketRead):
    conversation: ConversationRead | None = None
    audit_logs: list[AuditLogRead] = []


class TicketUpdate(BaseModel):
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    technician_id: int | None = None
    routing_group: str | None = Field(default=None, max_length=80)
    internal_notes: str | None = Field(default=None, max_length=5000)
    resolution_notes: str | None = Field(default=None, max_length=5000)


class TicketReopenRequest(BaseModel):
    note: str | None = Field(default=None, max_length=1000)
