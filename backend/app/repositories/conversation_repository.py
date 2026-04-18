from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.conversation import Conversation, ConversationStage, ConversationStatus, Message, MessageSender


class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int) -> Conversation:
        conversation = Conversation(user_id=user_id)
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def get(self, conversation_id: int) -> Conversation | None:
        return self.db.scalar(
            select(Conversation)
            .options(selectinload(Conversation.messages), selectinload(Conversation.ticket))
            .where(Conversation.id == conversation_id)
        )

    def list_for_user(self, user_id: int) -> list[Conversation]:
        return list(
            self.db.scalars(
                select(Conversation)
                .options(selectinload(Conversation.messages), selectinload(Conversation.ticket))
                .where(Conversation.user_id == user_id)
                .order_by(Conversation.updated_at.desc())
            )
        )

    def add_message(self, conversation: Conversation, sender: MessageSender, content: str, meta: dict | None = None) -> Message:
        message = Message(conversation_id=conversation.id, sender=sender, content=content, meta=meta)
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        self.db.refresh(conversation)
        return message

    def update_state(
        self,
        conversation: Conversation,
        *,
        category: str | None = None,
        status: ConversationStatus | None = None,
        failure_count: int | None = None,
        triage_stage: ConversationStage | None = None,
        collected_context: dict | None = None,
        last_triage: dict | None = None,
        escalation_summary: str | None = None,
    ) -> Conversation:
        if category is not None:
            conversation.category = category
        if status is not None:
            conversation.status = status
        if failure_count is not None:
            conversation.failure_count = failure_count
        if triage_stage is not None:
            conversation.triage_stage = triage_stage
        if collected_context is not None:
            conversation.collected_context = collected_context
        if last_triage is not None:
            conversation.last_triage = last_triage
        if escalation_summary is not None:
            conversation.escalation_summary = escalation_summary
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation
