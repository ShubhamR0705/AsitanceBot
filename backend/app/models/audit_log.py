import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class AuditAction(str, enum.Enum):
    TICKET_CREATED = "TICKET_CREATED"
    TICKET_ASSIGNED = "TICKET_ASSIGNED"
    STATUS_UPDATED = "STATUS_UPDATED"
    PRIORITY_UPDATED = "PRIORITY_UPDATED"
    NOTES_ADDED = "NOTES_ADDED"
    RESOLUTION_ADDED = "RESOLUTION_ADDED"
    TICKET_MESSAGE_ADDED = "TICKET_MESSAGE_ADDED"
    ESCALATION_TRIGGERED = "ESCALATION_TRIGGERED"
    TICKET_REOPENED = "TICKET_REOPENED"
    APPROVAL_REQUESTED = "APPROVAL_REQUESTED"
    APPROVAL_UPDATED = "APPROVAL_UPDATED"
    SLA_BREACHED = "SLA_BREACHED"
    KB_CREATED = "KB_CREATED"
    KB_UPDATED = "KB_UPDATED"
    KB_DELETED = "KB_DELETED"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ticket_id: Mapped[int | None] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"), nullable=True, index=True)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action_type: Mapped[AuditAction] = mapped_column(Enum(AuditAction, native_enum=False), nullable=False, index=True)
    previous_value: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    new_value: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    summary: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    ticket = relationship("Ticket", back_populates="audit_logs")
    actor = relationship("User")
