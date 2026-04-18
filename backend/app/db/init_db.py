from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import engine
from app.knowledge.seed import KNOWLEDGE_BASE_SEED
from app.models.knowledge_base import KnowledgeBase
from app.models.user import User, UserRole


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def seed_knowledge_base(db: Session) -> None:
    existing_titles = {title for (title,) in db.query(KnowledgeBase.title).all()}

    for entry in KNOWLEDGE_BASE_SEED:
        if entry["title"] not in existing_titles:
            db.add(KnowledgeBase(**entry))
    db.commit()


def seed_demo_users(db: Session) -> None:
    settings = get_settings()
    users = [
        (
            settings.demo_admin_email,
            settings.demo_admin_password,
            "Avery Admin",
            UserRole.ADMIN,
        ),
        (
            settings.demo_technician_email,
            settings.demo_technician_password,
            "Taylor Technician",
            UserRole.TECHNICIAN,
        ),
        (
            settings.demo_user_email,
            settings.demo_user_password,
            "Jordan User",
            UserRole.USER,
        ),
    ]

    for email, password, full_name, role in users:
        if db.query(User).filter(User.email == email).first():
            continue
        db.add(
            User(
                email=email,
                full_name=full_name,
                hashed_password=hash_password(password),
                role=role,
            )
        )
    db.commit()


def init_db(db: Session) -> None:
    settings = get_settings()
    if settings.seed_demo_data:
        seed_knowledge_base(db)
        seed_demo_users(db)
