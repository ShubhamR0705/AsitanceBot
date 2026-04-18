from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.ticket import Ticket, TicketStatus
from app.models.user import User, UserRole


class AssignmentService:
    OPEN_STATUSES = {
        TicketStatus.OPEN,
        TicketStatus.ESCALATED,
        TicketStatus.REOPENED,
        TicketStatus.IN_PROGRESS,
        TicketStatus.WAITING_FOR_USER,
    }

    def __init__(self, db: Session):
        self.db = db

    def auto_assign(self, ticket: Ticket) -> Ticket:
        technician = self._least_loaded_technician()
        if technician is None:
            return ticket
        ticket.technician_id = technician.id
        ticket.assigned_at = datetime.utcnow()
        ticket.assignment_source = "auto"
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def _least_loaded_technician(self) -> User | None:
        technicians = list(
            self.db.scalars(
                select(User)
                .where(User.role == UserRole.TECHNICIAN, User.is_active.is_(True))
                .order_by(User.full_name.asc())
            )
        )
        if not technicians:
            return None

        counts = dict(
            self.db.execute(
                select(Ticket.technician_id, func.count(Ticket.id))
                .where(Ticket.technician_id.is_not(None), Ticket.status.in_(self.OPEN_STATUSES))
                .group_by(Ticket.technician_id)
            ).all()
        )
        return min(technicians, key=lambda user: (counts.get(user.id, 0), user.created_at, user.id))
