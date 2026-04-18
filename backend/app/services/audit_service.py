from sqlalchemy.orm import Session

from app.models.audit_log import AuditAction, AuditLog
from app.models.user import User


class AuditService:
    def __init__(self, db: Session):
        self.db = db

    def record(
        self,
        *,
        action: AuditAction,
        summary: str,
        ticket_id: int | None = None,
        actor: User | None = None,
        previous_value: dict | None = None,
        new_value: dict | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            ticket_id=ticket_id,
            actor_user_id=actor.id if actor else None,
            action_type=action,
            previous_value=previous_value,
            new_value=new_value,
            summary=summary,
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry
