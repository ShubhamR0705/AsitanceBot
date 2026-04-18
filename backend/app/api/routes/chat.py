from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_roles
from app.models.user import User, UserRole
from app.schemas.conversation import (
    ChatMessageCreate,
    ChatResponse,
    ConversationRead,
    FeedbackRequest,
    FeedbackResponse,
    MessageFeedbackRead,
    MessageFeedbackRequest,
)
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/conversations", response_model=ConversationRead, status_code=status.HTTP_201_CREATED)
def create_conversation(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.USER)),
):
    return ChatService(db).create_conversation(current_user)


@router.get("/conversations", response_model=list[ConversationRead])
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.USER)),
):
    return ChatService(db).list_user_conversations(current_user)


@router.get("/conversations/{conversation_id}", response_model=ConversationRead)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.USER)),
):
    conversation = ChatService(db).get_user_conversation(current_user, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conversation


@router.post("/conversations/{conversation_id}/messages", response_model=ChatResponse)
def send_message(
    conversation_id: int,
    payload: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.USER)),
):
    try:
        result = ChatService(db).submit_message(
            current_user,
            conversation_id,
            payload.content,
            payload.structured_response.model_dump() if payload.structured_response else None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ChatResponse(
        conversation=result.conversation,
        assistant_message=result.assistant_message,
        category=result.category,
        kb_titles=result.kb_titles,
        escalated=result.escalated,
        ticket_id=result.ticket.id if result.ticket else None,
    )


@router.post("/conversations/{conversation_id}/feedback", response_model=FeedbackResponse)
def submit_feedback(
    conversation_id: int,
    payload: FeedbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.USER)),
):
    try:
        result = ChatService(db).record_feedback(current_user, conversation_id, payload.resolved)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return FeedbackResponse(
        conversation=result.conversation,
        assistant_message=result.assistant_message,
        escalated=result.escalated,
        ticket_id=result.ticket.id if result.ticket else None,
    )


@router.post("/messages/{message_id}/helpfulness", response_model=MessageFeedbackRead, status_code=status.HTTP_201_CREATED)
def submit_message_helpfulness(
    message_id: int,
    payload: MessageFeedbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.USER)),
):
    try:
        return ChatService(db).record_message_feedback(current_user, message_id, payload.helpful, payload.note)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
