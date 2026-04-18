from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.knowledge_base import KnowledgeBase


class KnowledgeRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_active(self) -> list[KnowledgeBase]:
        return list(
            self.db.scalars(
                select(KnowledgeBase)
                .where(KnowledgeBase.is_active.is_(True))
                .order_by(KnowledgeBase.category.asc(), KnowledgeBase.title.asc())
            )
        )

    def list_all(self) -> list[KnowledgeBase]:
        return list(self.db.scalars(select(KnowledgeBase).order_by(KnowledgeBase.category.asc(), KnowledgeBase.title.asc())))

    def get(self, kb_id: int) -> KnowledgeBase | None:
        return self.db.get(KnowledgeBase, kb_id)

    def create(self, category: str, title: str, content: str, keywords: str, is_active: bool = True) -> KnowledgeBase:
        entry = KnowledgeBase(
            category=category.upper(),
            title=title,
            content=content,
            keywords=keywords,
            is_active=is_active,
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def update(self, entry: KnowledgeBase, data: dict) -> KnowledgeBase:
        for field, value in data.items():
            if value is not None:
                setattr(entry, field, value)
        if entry.category:
            entry.category = entry.category.upper()
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def increment_usage(self, entries: list[KnowledgeBase]) -> None:
        for entry in entries:
            entry.usage_count += 1
            self.db.add(entry)
        self.db.commit()

    def delete(self, entry: KnowledgeBase) -> None:
        self.db.delete(entry)
        self.db.commit()
