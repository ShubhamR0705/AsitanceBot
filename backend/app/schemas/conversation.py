from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.conversation import ConversationStage, ConversationStatus, MessageSender


class ChatActionRead(BaseModel):
    label: str
    type: Literal["link", "internal_route", "trigger"]
    url: str | None = None
    route: str | None = None
    trigger: str | None = None


class MessageRead(BaseModel):
    id: int
    conversation_id: int
    sender: MessageSender
    content: str
    meta: dict | None = None
    actions: list[ChatActionRead] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationRead(BaseModel):
    id: int
    user_id: int
    category: str | None
    status: ConversationStatus
    failure_count: int
    triage_stage: ConversationStage
    collected_context: dict | None = None
    last_triage: dict | None = None
    escalation_summary: str | None = None
    created_at: datetime
    updated_at: datetime
    messages: list[MessageRead] = []

    model_config = ConfigDict(from_attributes=True)


class StructuredResponse(BaseModel):
    field: str = Field(min_length=1, max_length=80)
    value: str | list[str]
    label: str | None = Field(default=None, max_length=240)
    input_type: Literal["single_select", "multi_select"] = "single_select"
    question: str | None = Field(default=None, max_length=500)

    @field_validator("value")
    @classmethod
    def validate_value(cls, value: str | list[str]) -> str | list[str]:
        if isinstance(value, list):
            cleaned = [str(item).strip() for item in value if str(item).strip()]
            if not cleaned:
                raise ValueError("At least one selected value is required")
            return cleaned
        cleaned = str(value).strip()
        if not cleaned:
            raise ValueError("Selected value is required")
        return cleaned


class ChatMessageCreate(BaseModel):
    content: str = Field(default="", max_length=4000)
    structured_response: StructuredResponse | None = None


class FeedbackRequest(BaseModel):
    resolved: bool


class MessageFeedbackRequest(BaseModel):
    helpful: bool
    note: str | None = Field(default=None, max_length=1000)


class MessageFeedbackRead(BaseModel):
    id: int
    message_id: int
    conversation_id: int
    user_id: int
    helpful: bool
    note: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatResponse(BaseModel):
    conversation: ConversationRead
    assistant_message: MessageRead
    category: str
    kb_titles: list[str]
    escalated: bool = False
    ticket_id: int | None = None


class FeedbackResponse(BaseModel):
    conversation: ConversationRead
    assistant_message: MessageRead | None = None
    escalated: bool
    ticket_id: int | None = None
