import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class ConversationStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    RESOLVED = "RESOLVED"
    ESCALATED = "ESCALATED"


class ConversationStage(str, enum.Enum):
    INTAKE = "INTAKE"
    CLARIFYING = "CLARIFYING"
    SUGGESTING_FIX = "SUGGESTING_FIX"
    WAITING_FOR_FEEDBACK = "WAITING_FOR_FEEDBACK"
    RESOLVED = "RESOLVED"
    ESCALATED = "ESCALATED"


class MessageSender(str, enum.Enum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"
    TECHNICIAN = "TECHNICIAN"
    SYSTEM = "SYSTEM"


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    status: Mapped[ConversationStatus] = mapped_column(
        Enum(ConversationStatus, native_enum=False),
        default=ConversationStatus.ACTIVE,
        nullable=False,
        index=True,
    )
    failure_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    triage_stage: Mapped[ConversationStage] = mapped_column(
        Enum(ConversationStage, native_enum=False),
        default=ConversationStage.INTAKE,
        nullable=False,
        index=True,
    )
    collected_context: Mapped[dict | None] = mapped_column(JSON, default=dict, nullable=True)
    last_triage: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    escalation_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")
    ticket = relationship("Ticket", back_populates="conversation", uselist=False)


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    sender: Mapped[MessageSender] = mapped_column(Enum(MessageSender, native_enum=False), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    meta: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    conversation = relationship("Conversation", back_populates="messages")
    feedback = relationship("MessageFeedback", back_populates="message", cascade="all, delete-orphan")
