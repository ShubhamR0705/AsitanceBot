import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class TicketMessageSenderRole(str, enum.Enum):
    USER = "USER"
    TECHNICIAN = "TECHNICIAN"
    ADMIN = "ADMIN"


class TicketMessage(Base):
    __tablename__ = "ticket_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    sender_role: Mapped[TicketMessageSenderRole] = mapped_column(Enum(TicketMessageSenderRole, native_enum=False), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    ticket = relationship("Ticket", back_populates="ticket_messages")
    sender = relationship("User")
