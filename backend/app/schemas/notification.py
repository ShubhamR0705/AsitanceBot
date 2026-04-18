from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.notification import NotificationChannel


class NotificationRead(BaseModel):
    id: int
    recipient_user_id: int
    actor_user_id: int | None
    ticket_id: int | None
    channel: NotificationChannel
    title: str
    body: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    unread_count: int
    notifications: list[NotificationRead]
