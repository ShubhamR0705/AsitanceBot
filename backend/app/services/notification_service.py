import logging

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.notification import Notification, NotificationChannel
from app.models.ticket import Ticket
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository

logger = logging.getLogger("assistiq.notifications")


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def list_for_user(self, user: User) -> list[Notification]:
        notifications = list(
            self.db.scalars(
                select(Notification)
                .options(selectinload(Notification.ticket))
                .where(Notification.recipient_user_id == user.id)
                .order_by(Notification.created_at.desc())
                .limit(100)
            )
        )
        return [notification for notification in notifications if self._is_visible_to_user(notification, user)][:50]

    def unread_count(self, user: User) -> int:
        return len([notification for notification in self.list_for_user(user) if not notification.is_read])

    def mark_read(self, user: User, notification_id: int) -> Notification | None:
        notification = self.db.get(Notification, notification_id)
        if notification is None or notification.recipient_user_id != user.id:
            return None
        notification.is_read = True
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def notify(
        self,
        *,
        recipient: User,
        title: str,
        body: str,
        ticket: Ticket | None = None,
        actor: User | None = None,
        email: bool = True,
    ) -> Notification:
        notification = Notification(
            recipient_user_id=recipient.id,
            actor_user_id=actor.id if actor else None,
            ticket_id=ticket.id if ticket else None,
            channel=NotificationChannel.IN_APP,
            title=title,
            body=body,
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        if email:
            self._send_mock_email(recipient=recipient, title=title, body=body, ticket=ticket)
        return notification

    def notify_role(
        self,
        *,
        role: UserRole,
        title: str,
        body: str,
        ticket: Ticket | None = None,
        actor: User | None = None,
        exclude_user_ids: set[int] | None = None,
        email: bool = False,
    ) -> list[Notification]:
        notifications: list[Notification] = []
        exclude_user_ids = exclude_user_ids or set()
        for recipient in UserRepository(self.db).list_by_roles([role]):
            if recipient.id in exclude_user_ids:
                continue
            notifications.append(
                self.notify(
                    recipient=recipient,
                    actor=actor,
                    ticket=ticket,
                    title=title,
                    body=body,
                    email=email,
                )
            )
        return notifications

    def notify_admins(self, *, title: str, body: str, ticket: Ticket | None = None, actor: User | None = None) -> list[Notification]:
        return self.notify_role(role=UserRole.ADMIN, title=title, body=body, ticket=ticket, actor=actor, email=False)

    def notify_technicians(
        self,
        *,
        title: str,
        body: str,
        ticket: Ticket | None = None,
        actor: User | None = None,
        exclude_user_ids: set[int] | None = None,
    ) -> list[Notification]:
        return self.notify_role(
            role=UserRole.TECHNICIAN,
            title=title,
            body=body,
            ticket=ticket,
            actor=actor,
            exclude_user_ids=exclude_user_ids,
            email=False,
        )

    def _send_mock_email(self, *, recipient: User, title: str, body: str, ticket: Ticket | None) -> None:
        logger.info(
            "mock_email_notification recipient=%s ticket_id=%s title=%s body=%s",
            recipient.email,
            ticket.id if ticket else None,
            title,
            body,
        )

    def _is_visible_to_user(self, notification: Notification, user: User) -> bool:
        if notification.recipient_user_id != user.id:
            return False
        ticket = notification.ticket
        if ticket is None:
            return True
        if user.role == UserRole.ADMIN:
            return True
        if user.role == UserRole.USER:
            return ticket.user_id == user.id
        if user.role == UserRole.TECHNICIAN:
            return ticket.technician_id in {None, user.id}
        return False
