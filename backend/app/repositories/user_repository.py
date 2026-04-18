from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User, UserRole


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email.lower()))

    def list(self) -> list[User]:
        return list(self.db.scalars(select(User).order_by(User.created_at.desc())))

    def list_filtered(self, *, role: UserRole | None = None, is_active: bool | None = None) -> list[User]:
        statement = select(User)
        if role is not None:
            statement = statement.where(User.role == role)
        if is_active is not None:
            statement = statement.where(User.is_active.is_(is_active))
        return list(self.db.scalars(statement.order_by(User.created_at.desc())))

    def list_by_roles(self, roles: list[UserRole]) -> list[User]:
        return list(self.db.scalars(select(User).where(User.role.in_(roles), User.is_active.is_(True)).order_by(User.full_name.asc())))

    def create(self, email: str, full_name: str, hashed_password: str, role: UserRole = UserRole.USER) -> User:
        user = User(
            email=email.lower(),
            full_name=full_name.strip(),
            hashed_password=hashed_password,
            role=role,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_role(self, user: User, role: UserRole) -> User:
        user.role = role
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User, data: dict) -> User:
        for field in ("email", "full_name", "role", "is_active"):
            if field in data and data[field] is not None:
                value = data[field]
                if field == "email":
                    value = str(value).lower()
                if field == "full_name":
                    value = str(value).strip()
                setattr(user, field, value)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def deactivate(self, user: User) -> User:
        user.is_active = False
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
