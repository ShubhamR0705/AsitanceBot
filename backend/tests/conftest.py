import os
from collections.abc import Generator

import pytest

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["AUTO_CREATE_TABLES"] = "false"
os.environ["SEED_DEMO_DATA"] = "true"

from app.db.base import Base  # noqa: E402
from app.db.init_db import seed_demo_users, seed_knowledge_base  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402


@pytest.fixture
def db() -> Generator:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        seed_knowledge_base(session)
        seed_demo_users(session)
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
