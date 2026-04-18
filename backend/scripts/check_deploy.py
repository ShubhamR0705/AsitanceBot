from __future__ import annotations

import os
from pathlib import Path
import sys

import httpx
from sqlalchemy import text

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings
from app.db.session import SessionLocal, engine
from app.models.knowledge_base import KnowledgeBase
from app.models.ticket import Ticket
from app.models.user import User


def check_environment() -> list[str]:
    settings = get_settings()
    errors: list[str] = []
    for key in ["DATABASE_URL", "SECRET_KEY"]:
        if not os.getenv(key):
            errors.append(f"{key} is not set.")
    if not settings.cors_origin_list and not settings.cors_origin_regex:
        errors.append("CORS_ORIGINS or CORS_ORIGIN_REGEX must be set.")
    if settings.environment.lower() in {"production", "staging"}:
        try:
            settings.validate_for_runtime()
        except RuntimeError as exc:
            errors.append(str(exc))
    return errors


def check_database() -> list[str]:
    errors: list[str] = []
    try:
        with engine.connect() as connection:
            connection.execute(text("select 1"))
    except Exception as exc:
        errors.append(f"Database connection failed: {exc}")
    return errors


def check_seed_data() -> list[str]:
    errors: list[str] = []
    db = SessionLocal()
    try:
        if db.query(User).count() < 3:
            errors.append("Expected at least 3 demo users.")
        if db.query(KnowledgeBase).count() < 10:
            errors.append("Expected rich knowledge base seed data.")
        if db.query(Ticket).count() < 3:
            errors.append("Expected demo tickets for dashboard testing.")
    finally:
        db.close()
    return errors


def check_public_health() -> list[str]:
    url = os.getenv("BACKEND_HEALTH_URL")
    if not url:
        return []
    errors: list[str] = []
    try:
        response = httpx.get(url, timeout=10)
        response.raise_for_status()
        if response.json().get("status") != "ok":
            errors.append(f"Health endpoint returned unexpected body: {response.text}")
    except Exception as exc:
        errors.append(f"Health endpoint failed: {exc}")
    return errors


def main() -> int:
    checks = [
        ("environment", check_environment),
        ("database", check_database),
        ("seed_data", check_seed_data),
        ("public_health", check_public_health),
    ]
    all_errors: list[str] = []
    for name, check in checks:
        errors = check()
        if errors:
            all_errors.extend(f"{name}: {error}" for error in errors)
        else:
            print(f"ok: {name}")

    if all_errors:
        for error in all_errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    print("Deployment check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
