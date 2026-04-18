import re

from sqlalchemy.orm import Session

from app.models.knowledge_base import KnowledgeBase
from app.repositories.knowledge_repository import KnowledgeRepository


class KBRetrievalService:
    def __init__(self, db: Session):
        self.repository = KnowledgeRepository(db)

    def retrieve(
        self,
        issue_text: str,
        category: str,
        limit: int = 2,
        secondary_category: str | None = None,
        exclude_ids: set[int] | None = None,
    ) -> list[KnowledgeBase]:
        entries = self.repository.list_active()
        issue_tokens = set(re.findall(r"[a-z0-9-]+", issue_text.lower()))
        exclude_ids = exclude_ids or set()
        scored: list[tuple[int, KnowledgeBase]] = []

        for entry in entries:
            if entry.id in exclude_ids:
                continue
            keywords = {keyword.strip().lower() for keyword in entry.keywords.split(",")}
            keyword_hits = len(issue_tokens.intersection(keywords))
            category_score = 5 if entry.category == category else 3 if secondary_category and entry.category == secondary_category else 0
            general_score = 1 if entry.category == "GENERAL" else 0
            title_hits = sum(2 for token in issue_tokens if token and token in entry.title.lower())
            content_hits = sum(1 for token in issue_tokens if token and token in entry.content.lower())
            score = category_score + general_score + keyword_hits * 3 + min(title_hits, 4) + min(content_hits, 4)
            if score > 0:
                scored.append((score, entry))

        scored.sort(key=lambda item: item[0], reverse=True)
        selected = [entry for _, entry in scored[:limit]]
        if selected:
            return selected

        return [entry for entry in entries if entry.category == "GENERAL" and entry.id not in exclude_ids][:limit]

    def track_usage(self, entries: list[KnowledgeBase]) -> None:
        if entries:
            self.repository.increment_usage(entries)
