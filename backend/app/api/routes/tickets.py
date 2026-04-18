from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.models.user import User, UserRole
from app.schemas.ticket import TicketDetail, TicketRead, TicketReopenRequest, TicketUpdate
from app.services.ticket_service import TicketService

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("/mine", response_model=list[TicketRead])
def my_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.USER)),
):
    return TicketService(db).list_for_user(current_user)


@router.get("/queue", response_model=list[TicketRead])
def ticket_queue(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.TECHNICIAN, UserRole.ADMIN)),
):
    return TicketService(db).list_queue()


@router.get("/all", response_model=list[TicketRead])
def all_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    return TicketService(db).list_all()


@router.get("/{ticket_id}", response_model=TicketDetail)
def ticket_detail(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = TicketService(db).get_visible_ticket(current_user, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return ticket


@router.patch("/{ticket_id}", response_model=TicketDetail)
def update_ticket(
    ticket_id: int,
    payload: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.TECHNICIAN, UserRole.ADMIN)),
):
    service = TicketService(db)
    ticket = service.get_visible_ticket(current_user, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    try:
        return service.update_ticket(current_user, ticket, payload.model_dump(exclude_unset=True))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/{ticket_id}/reopen", response_model=TicketDetail)
def reopen_ticket(
    ticket_id: int,
    payload: TicketReopenRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TicketService(db)
    ticket = service.get_visible_ticket(current_user, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    try:
        return service.reopen_ticket(current_user, ticket, payload.note)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
