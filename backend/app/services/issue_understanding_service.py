import json
import re
from typing import Literal

from pydantic import BaseModel, Field, ValidationError, field_validator

from app.services.azure_openai_client import AzureOpenAIClient, AzureOpenAIClientError
from app.services.classification_service import CATEGORY_KEYWORDS, PHRASE_HINTS, ClassificationResult, ClassificationService
from app.services.llm_prompts import ISSUE_UNDERSTANDING_SYSTEM_PROMPT, build_issue_understanding_user_prompt


Category = Literal["VPN", "PASSWORD", "ACCESS", "WIFI", "NETWORK", "EMAIL", "DEVICE_PERFORMANCE", "SOFTWARE", "BROWSER", "PRINTER", "GENERAL"]
UrgencyLevel = Literal["low", "medium", "high", "critical"]
NextAction = Literal["ask_clarification", "suggest_fix", "escalate"]


class IssueUnderstanding(BaseModel):
    primary_category: Category
    secondary_category: Category | None = None
    confidence_score: float = Field(ge=0.0, le=1.0)
    missing_slots: list[str] = Field(default_factory=list)
    urgency_level: UrgencyLevel = "low"
    urgency_signals: list[str] = Field(default_factory=list)
    user_intent: str = "get_support"
    short_issue_summary: str
    recommended_next_action: NextAction
    explicit_human_requested: bool = False
    security_sensitive: bool = False
    business_impact: str | None = None
    source: str = "deterministic"

    @field_validator("missing_slots", "urgency_signals")
    @classmethod
    def normalize_string_list(cls, values: list[str]) -> list[str]:
        return [str(value).strip() for value in values if str(value).strip()]


class IssueUnderstandingService:
    def __init__(self, llm_client: AzureOpenAIClient | None = None) -> None:
        self.llm_client = llm_client or AzureOpenAIClient()
        self.classifier = ClassificationService()

    def understand(
        self,
        *,
        issue_text: str,
        conversation_history: str,
        existing_context: dict,
        deterministic_classification: ClassificationResult | None = None,
    ) -> IssueUnderstanding:
        fallback = self._deterministic_understanding(issue_text, deterministic_classification)
        if not self.llm_client.is_configured:
            return fallback

        try:
            content = self.llm_client.chat_completion(
                messages=[
                    {"role": "system", "content": ISSUE_UNDERSTANDING_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": build_issue_understanding_user_prompt(
                            issue_text=issue_text,
                            conversation_history=conversation_history,
                            existing_context=existing_context,
                        ),
                    },
                ],
                max_completion_tokens=500,
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            parsed = self._parse_json(content)
            understanding = IssueUnderstanding.model_validate(parsed)
            understanding.source = "azure_openai"
            return self._merge_with_guardrails(understanding, fallback)
        except (AzureOpenAIClientError, ValidationError, json.JSONDecodeError, TypeError, ValueError):
            return fallback

    def _parse_json(self, content: str) -> dict:
        stripped = content.strip()
        if stripped.startswith("```"):
            stripped = re.sub(r"^```(?:json)?", "", stripped).strip()
            stripped = re.sub(r"```$", "", stripped).strip()
        return json.loads(stripped)

    def _merge_with_guardrails(self, understanding: IssueUnderstanding, fallback: IssueUnderstanding) -> IssueUnderstanding:
        if understanding.secondary_category in {None, "GENERAL", understanding.primary_category}:
            understanding.secondary_category = fallback.secondary_category
        if understanding.confidence_score < 0.2 and fallback.confidence_score > understanding.confidence_score:
            understanding.primary_category = fallback.primary_category
            understanding.confidence_score = fallback.confidence_score
        if not fallback.security_sensitive:
            understanding.security_sensitive = False
        if not fallback.explicit_human_requested:
            understanding.explicit_human_requested = False
        if fallback.urgency_level != "critical" and understanding.urgency_level == "critical":
            understanding.urgency_level = fallback.urgency_level
        if understanding.recommended_next_action == "escalate" and not (
            fallback.security_sensitive
            or fallback.explicit_human_requested
            or fallback.urgency_level == "critical"
        ):
            understanding.recommended_next_action = fallback.recommended_next_action
        if fallback.security_sensitive:
            understanding.security_sensitive = True
            understanding.recommended_next_action = "escalate"
            understanding.urgency_level = "critical"
        if fallback.explicit_human_requested:
            understanding.explicit_human_requested = True
            understanding.recommended_next_action = "escalate"
        return understanding

    def _deterministic_understanding(
        self,
        issue_text: str,
        deterministic_classification: ClassificationResult | None,
    ) -> IssueUnderstanding:
        classification = deterministic_classification or self.classifier.classify(issue_text)
        lower = issue_text.lower()
        urgency_signals = self._urgency_signals(lower)
        explicit_human = self._explicit_human_requested(lower)
        security_sensitive = self._security_sensitive(lower)
        critical = security_sensitive or any(signal in urgency_signals for signal in ["cannot work", "payroll", "ceo", "production down"])
        urgency: UrgencyLevel = "critical" if critical else "high" if urgency_signals else "low"
        next_action: NextAction = "escalate" if critical or explicit_human else "ask_clarification" if classification.confidence < 0.5 else "suggest_fix"

        return IssueUnderstanding(
            primary_category=classification.category,  # type: ignore[arg-type]
            secondary_category=self._secondary_category(issue_text, classification.category),
            confidence_score=classification.confidence,
            missing_slots=self._missing_slots_for_text(lower),
            urgency_level=urgency,
            urgency_signals=urgency_signals,
            user_intent="request_human_support" if explicit_human else "get_support",
            short_issue_summary=self._summarize(issue_text, classification.category),
            recommended_next_action=next_action,
            explicit_human_requested=explicit_human,
            security_sensitive=security_sensitive,
            business_impact="blocking work" if "cannot work" in lower or "can't work" in lower else None,
            source="deterministic",
        )

    def _secondary_category(self, text: str, primary: str) -> Category | None:
        lower = text.lower()
        scores: list[tuple[str, int]] = []
        for category in ["VPN", "PASSWORD", "ACCESS", "WIFI", "NETWORK", "EMAIL", "DEVICE_PERFORMANCE", "SOFTWARE", "BROWSER", "PRINTER"]:
            if category == primary:
                continue
            keywords = CATEGORY_KEYWORDS[category]
            keyword_score = sum(1 for keyword in keywords if keyword in lower)
            phrase_score = sum(2 for phrase, phrase_category in PHRASE_HINTS.items() if phrase_category == category and phrase in lower)
            score = keyword_score + phrase_score
            if score:
                scores.append((category, score))
        scores.sort(key=lambda item: item[1], reverse=True)
        return scores[0][0] if scores else None  # type: ignore[return-value]

    def _missing_slots_for_text(self, lower: str) -> list[str]:
        missing = []
        if not any(token in lower for token in ["windows", "mac", "laptop", "phone", "android", "iphone"]):
            missing.append("device_type")
        if "error" not in lower and "says" not in lower and "message" not in lower:
            missing.append("error_message")
        if not any(token in lower for token in ["urgent", "blocking", "cannot work", "can't work", "affecting"]):
            missing.append("business_impact")
        return missing

    def _urgency_signals(self, lower: str) -> list[str]:
        signals = []
        phrases = ["urgent", "cannot work", "can't work", "blocked", "production down", "payroll", "ceo", "all users", "multiple people"]
        for phrase in phrases:
            if phrase in lower:
                signals.append(phrase)
        return signals

    def _explicit_human_requested(self, lower: str) -> bool:
        return any(phrase in lower for phrase in ["human", "agent", "technician", "call support", "need support now", "talk to someone"])

    def _security_sensitive(self, lower: str) -> bool:
        terms = [
            "phishing",
            "malware",
            "ransomware",
            "stolen laptop",
            "laptop was stolen",
            "device stolen",
            "stolen device",
            "lost laptop",
            "lost device",
            "account compromised",
            "unauthorized login",
            "suspicious login",
            "data breach",
        ]
        return any(term in lower for term in terms)

    def _summarize(self, issue_text: str, category: str) -> str:
        compact = " ".join(issue_text.split())
        if len(compact) > 160:
            compact = compact[:157] + "..."
        return f"{category.replace('_', ' ').title()} issue: {compact}"
