from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_roles
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.repositories.knowledge_repository import KnowledgeRepository
from app.repositories.user_repository import UserRepository
from app.schemas.admin import AnalyticsResponse
from app.schemas.knowledge import KnowledgeBaseCreate, KnowledgeBaseRead, KnowledgeBaseUpdate
from app.schemas.user import AdminUserCreate, AdminUserUpdate, UserRead, UserRoleUpdate
from app.models.audit_log import AuditAction
from app.services.audit_service import AuditService
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/analytics", response_model=AnalyticsResponse)
def analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    return AdminService(db).analytics()


@router.get("/users", response_model=list[UserRead])
def list_users(
    role: UserRole | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    return UserRepository(db).list_filtered(role=role, is_active=is_active)


@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: AdminUserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    repository = UserRepository(db)
    if repository.get_by_email(payload.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already in use")
    user = repository.create(
        email=str(payload.email),
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    if user.is_active != payload.is_active:
        user = repository.update(user, {"is_active": payload.is_active})
    AuditService(db).record(
        action=AuditAction.STATUS_UPDATED,
        actor=current_user,
        summary=f"Admin created user {user.email}.",
        new_value={"user_id": user.id, "role": user.role.value, "is_active": user.is_active},
    )
    return user


@router.patch("/users/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    payload: AdminUserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    repository = UserRepository(db)
    user = repository.get(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    data = payload.model_dump(exclude_unset=True)
    if "email" in data and repository.get_by_email(str(data["email"])) and repository.get_by_email(str(data["email"])).id != user.id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already in use")
    if user.id == current_user.id and data.get("is_active") is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admins cannot deactivate their own account")
    previous = {"email": user.email, "full_name": user.full_name, "role": user.role.value, "is_active": user.is_active}
    updated = repository.update(user, data)
    AuditService(db).record(
        action=AuditAction.STATUS_UPDATED,
        actor=current_user,
        summary=f"Admin updated user {updated.email}.",
        previous_value=previous,
        new_value={"email": updated.email, "full_name": updated.full_name, "role": updated.role.value, "is_active": updated.is_active},
    )
    return updated


@router.patch("/users/{user_id}/role", response_model=UserRead)
def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    repository = UserRepository(db)
    user = repository.get(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return repository.update_role(user, payload.role)


@router.delete("/users/{user_id}", response_model=UserRead)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    repository = UserRepository(db)
    user = repository.get(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admins cannot deactivate their own account")
    previous = {"is_active": user.is_active}
    updated = repository.deactivate(user)
    AuditService(db).record(
        action=AuditAction.STATUS_UPDATED,
        actor=current_user,
        summary=f"Admin deactivated user {updated.email}.",
        previous_value=previous,
        new_value={"is_active": updated.is_active},
    )
    return updated


@router.get("/knowledge-base", response_model=list[KnowledgeBaseRead])
def list_knowledge_base(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    return KnowledgeRepository(db).list_all()


@router.post("/knowledge-base", response_model=KnowledgeBaseRead, status_code=status.HTTP_201_CREATED)
def create_knowledge_base_entry(
    payload: KnowledgeBaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    entry = KnowledgeRepository(db).create(**payload.model_dump())
    AuditService(db).record(
        action=AuditAction.KB_CREATED,
        actor=current_user,
        summary=f"Knowledge base article created: {entry.title}",
        new_value={"id": entry.id, "category": entry.category, "title": entry.title},
    )
    return entry


@router.patch("/knowledge-base/{entry_id}", response_model=KnowledgeBaseRead)
def update_knowledge_base_entry(
    entry_id: int,
    payload: KnowledgeBaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    repository = KnowledgeRepository(db)
    entry = repository.get(entry_id)
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge base entry not found")
    previous = {"category": entry.category, "title": entry.title, "is_active": entry.is_active}
    updated = repository.update(entry, payload.model_dump(exclude_unset=True))
    AuditService(db).record(
        action=AuditAction.KB_UPDATED,
        actor=current_user,
        summary=f"Knowledge base article updated: {updated.title}",
        previous_value=previous,
        new_value={"category": updated.category, "title": updated.title, "is_active": updated.is_active},
    )
    return updated


@router.delete("/knowledge-base/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_knowledge_base_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    repository = KnowledgeRepository(db)
    entry = repository.get(entry_id)
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge base entry not found")
    previous = {"id": entry.id, "category": entry.category, "title": entry.title}
    repository.delete(entry)
    AuditService(db).record(
        action=AuditAction.KB_DELETED,
        actor=current_user,
        summary=f"Knowledge base article deleted: {previous['title']}",
        previous_value=previous,
    )
    return None
