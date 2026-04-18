import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class TicketStatus(str, enum.Enum):
    OPEN = "OPEN"
    ESCALATED = "ESCALATED"
    IN_PROGRESS = "IN_PROGRESS"
    WAITING_FOR_USER = "WAITING_FOR_USER"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    REOPENED = "REOPENED"


class TicketPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TicketRequestType(str, enum.Enum):
    SUPPORT = "SUPPORT"
    SOFTWARE_INSTALL = "SOFTWARE_INSTALL"


class TicketApprovalStatus(str, enum.Enum):
    NOT_REQUIRED = "NOT_REQUIRED"
    REQUESTED = "REQUESTED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    conversation_id: Mapped[int | None] = mapped_column(ForeignKey("conversations.id", ondelete="SET NULL"), unique=True, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    technician_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    category: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    routing_group: Mapped[str] = mapped_column(String(80), default="general", nullable=False, index=True)
    status: Mapped[TicketStatus] = mapped_column(
        Enum(TicketStatus, native_enum=False),
        default=TicketStatus.OPEN,
        nullable=False,
        index=True,
    )
    priority: Mapped[TicketPriority] = mapped_column(Enum(TicketPriority, native_enum=False), default=TicketPriority.MEDIUM, nullable=False, index=True)
    request_type: Mapped[TicketRequestType] = mapped_column(Enum(TicketRequestType, native_enum=False), default=TicketRequestType.SUPPORT, nullable=False, index=True)
    assignment_source: Mapped[str | None] = mapped_column(String(20), nullable=True)
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    requested_software: Mapped[str | None] = mapped_column(String(180), nullable=True)
    request_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    request_device: Mapped[str | None] = mapped_column(String(160), nullable=True)
    approval_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    approval_status: Mapped[TicketApprovalStatus] = mapped_column(
        Enum(TicketApprovalStatus, native_enum=False),
        default=TicketApprovalStatus.NOT_REQUIRED,
        nullable=False,
        index=True,
    )
    approved_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    approval_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    internal_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    first_response_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    sla_due_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)
    sla_breached: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)
    reopened_from_ticket_id: Mapped[int | None] = mapped_column(ForeignKey("tickets.id", ondelete="SET NULL"), nullable=True)
    reopen_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_reopened_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    conversation = relationship("Conversation", back_populates="ticket")
    user = relationship("User", back_populates="tickets", foreign_keys=[user_id])
    technician = relationship("User", back_populates="assigned_tickets", foreign_keys=[technician_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    ticket_messages = relationship("TicketMessage", back_populates="ticket", cascade="all, delete-orphan", order_by="TicketMessage.created_at")
    audit_logs = relationship("AuditLog", back_populates="ticket", cascade="all, delete-orphan", order_by="AuditLog.created_at")
    notifications = relationship("Notification", back_populates="ticket")
