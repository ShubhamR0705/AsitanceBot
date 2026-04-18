from dataclasses import dataclass
from typing import Any

from app.core.config import get_settings
from app.models.knowledge_base import KnowledgeBase
from app.services.azure_openai_client import AzureOpenAIClient, AzureOpenAIClientError
from app.services.llm_prompts import (
    ESCALATION_SUMMARY_SYSTEM_PROMPT,
    SUPPORT_RESPONSE_SYSTEM_PROMPT,
    build_escalation_summary_user_prompt,
    build_support_response_user_prompt,
)


@dataclass(frozen=True)
class GeneratedSupportResponse:
    content: str | None
    source: str
    error: str | None = None


class OpenAIResponseService:
    """Generate KB-grounded assistant responses with an OpenAI-compatible chat endpoint."""

    def __init__(self, llm_client: AzureOpenAIClient | None = None) -> None:
        self.settings = get_settings()
        self.llm_client = llm_client or AzureOpenAIClient()

    @property
    def is_configured(self) -> bool:
        return self.llm_client.is_configured

    def generate_support_response(
        self,
        *,
        issue_text: str,
        category: str,
        entries: list[KnowledgeBase],
        attempt: int,
        collected_context: dict | None = None,
        triage_reason: str | None = None,
        is_retry: bool = False,
    ) -> GeneratedSupportResponse:
        if not self.is_configured:
            return GeneratedSupportResponse(content=None, source="deterministic_fallback", error="openai_not_configured")

        payload = self._build_payload(
            issue_text=issue_text,
            category=category,
            entries=entries,
            attempt=attempt,
            collected_context=collected_context or {},
            triage_reason=triage_reason,
            is_retry=is_retry,
        )
        try:
            content = self.llm_client.chat_completion(
                messages=payload["messages"],
                max_completion_tokens=payload["max_completion_tokens"],
                temperature=payload.get("temperature"),
            )
        except AzureOpenAIClientError as exc:
            return GeneratedSupportResponse(content=None, source="deterministic_fallback", error=str(exc))

        if not content:
            return GeneratedSupportResponse(content=None, source="deterministic_fallback", error="empty_openai_response")

        return GeneratedSupportResponse(content=content.strip(), source="openai")

    def generate_escalation_summary(
        self,
        *,
        category: str,
        collected_context: dict,
        conversation_history: str,
        failure_count: int,
    ) -> GeneratedSupportResponse:
        if not self.is_configured:
            return GeneratedSupportResponse(content=None, source="deterministic_fallback", error="openai_not_configured")

        payload: dict[str, Any] = {
            "messages": [
                {"role": "system", "content": ESCALATION_SUMMARY_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": build_escalation_summary_user_prompt(
                        category=category,
                        collected_context=collected_context,
                        conversation_history=conversation_history,
                        failure_count=failure_count,
                    ),
                },
            ],
            "max_completion_tokens": min(self.settings.azure_openai_max_completion_tokens, 700),
        }
        if self.settings.azure_openai_temperature is not None:
            payload["temperature"] = self.settings.azure_openai_temperature

        try:
            content = self.llm_client.chat_completion(
                messages=payload["messages"],
                max_completion_tokens=payload["max_completion_tokens"],
                temperature=payload.get("temperature"),
            )
        except AzureOpenAIClientError as exc:
            return GeneratedSupportResponse(content=None, source="deterministic_fallback", error=str(exc))

        if not content:
            return GeneratedSupportResponse(content=None, source="deterministic_fallback", error="empty_openai_response")
        return GeneratedSupportResponse(content=content.strip(), source="openai")

    def _build_payload(
        self,
        *,
        issue_text: str,
        category: str,
        entries: list[KnowledgeBase],
        attempt: int,
        collected_context: dict,
        triage_reason: str | None,
        is_retry: bool,
    ) -> dict[str, Any]:
        context = "\n\n".join(
            f"KB Article {index}\nTitle: {entry.title}\nCategory: {entry.category}\nContent: {entry.content}"
            for index, entry in enumerate(entries, start=1)
        )

        payload: dict[str, Any] = {
            "messages": [
                {"role": "system", "content": SUPPORT_RESPONSE_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": build_support_response_user_prompt(
                        issue_text=issue_text,
                        category=category,
                        attempt=attempt,
                        collected_context=collected_context,
                        triage_reason=triage_reason,
                        is_retry=is_retry,
                        kb_context=context,
                    ),
                },
            ],
            "max_completion_tokens": self.settings.azure_openai_max_completion_tokens,
        }
        if self.settings.azure_openai_temperature is not None:
            payload["temperature"] = self.settings.azure_openai_temperature
        return payload
