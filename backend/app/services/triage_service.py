import re
from dataclasses import dataclass, field
from enum import Enum

from app.models.conversation import Conversation, ConversationStage
from app.services.classification_service import ClassificationResult
from app.services.diagnostic_playbooks import DiagnosticField, get_playbook
from app.services.guided_question_service import GuidedQuestionService
from app.services.issue_understanding_service import IssueUnderstanding


class TriageAction(str, Enum):
    ASK_CLARIFYING_QUESTIONS = "ASK_CLARIFYING_QUESTIONS"
    SUGGEST_FIX = "SUGGEST_FIX"
    ESCALATE = "ESCALATE"


@dataclass(frozen=True)
class TriageDecision:
    action: TriageAction
    category: str
    stage: ConversationStage
    collected_context: dict
    missing_fields: list[str]
    questions: list[str]
    confidence: float
    reason: str
    urgency_level: str = "low"
    urgency_signals: list[str] | None = None
    issue_summary: str | None = None
    secondary_category: str | None = None
    explicit_human_requested: bool = False
    security_sensitive: bool = False
    business_impact: str | None = None
    source: str = "deterministic"
    structured_questions: list[dict] = field(default_factory=list)

    def to_meta(self) -> dict:
        return {
            "triage_action": self.action.value,
            "triage_stage": self.stage.value,
            "missing_fields": self.missing_fields,
            "questions": self.questions,
            "confidence": self.confidence,
            "reason": self.reason,
            "urgency_level": self.urgency_level,
            "urgency_signals": self.urgency_signals or [],
            "issue_summary": self.issue_summary,
            "secondary_category": self.secondary_category,
            "explicit_human_requested": self.explicit_human_requested,
            "security_sensitive": self.security_sensitive,
            "business_impact": self.business_impact,
            "source": self.source,
            "collected_context": self.collected_context,
            "structured_questions": self.structured_questions,
        }


class TriageService:
    def __init__(self) -> None:
        self.guided_questions = GuidedQuestionService()

    def decide(
        self,
        *,
        conversation: Conversation,
        issue_text: str,
        category: str,
        classification: ClassificationResult,
        understanding: IssueUnderstanding | None = None,
    ) -> TriageDecision:
        existing_context = dict(conversation.collected_context or {})
        collected_context = self._extract_context(issue_text, existing_context)
        if understanding:
            collected_context = self._merge_understanding_context(collected_context, understanding)
        playbook = get_playbook(category)
        missing_fields = [field.key for field in playbook.required_fields if not collected_context.get(field.key)]
        if understanding:
            missing_fields = sorted(set(missing_fields + [slot for slot in understanding.missing_slots if not collected_context.get(slot)]))

        confidence = understanding.confidence_score if understanding else classification.confidence
        escalation_reason = self._escalation_reason(issue_text, understanding)
        if not escalation_reason and conversation.triage_stage == ConversationStage.CLARIFYING and category == "GENERAL" and confidence < 0.45:
            escalation_reason = "Issue remains too ambiguous after clarification."
        if escalation_reason:
            return TriageDecision(
                action=TriageAction.ESCALATE,
                category=category,
                stage=ConversationStage.ESCALATED,
                collected_context=collected_context,
                missing_fields=missing_fields,
                questions=[],
                confidence=max(classification.confidence, understanding.confidence_score if understanding else 0.0, 0.9),
                reason=escalation_reason,
                urgency_level=understanding.urgency_level if understanding else "critical",
                urgency_signals=understanding.urgency_signals if understanding else [],
                issue_summary=understanding.short_issue_summary if understanding else None,
                secondary_category=understanding.secondary_category if understanding else None,
                explicit_human_requested=understanding.explicit_human_requested if understanding else False,
                security_sensitive=understanding.security_sensitive if understanding else True,
                business_impact=understanding.business_impact if understanding else None,
                source=understanding.source if understanding else "deterministic",
            )

        recommended_next_action = understanding.recommended_next_action if understanding else None
        needs_required_context = len(missing_fields) >= 3 or (
            len(missing_fields) >= 2 and (confidence < 0.9 or recommended_next_action == "ask_clarification")
        )
        should_ask = (
            conversation.triage_stage == ConversationStage.INTAKE
            and conversation.failure_count == 0
            and needs_required_context
        )
        if should_ask:
            questions = self._questions_for_missing(playbook.required_fields, missing_fields)
            structured_questions = self.guided_questions.build(
                fields=playbook.required_fields,
                missing_fields=missing_fields,
                questions=questions,
            )
            return TriageDecision(
                action=TriageAction.ASK_CLARIFYING_QUESTIONS,
                category=category,
                stage=ConversationStage.CLARIFYING,
                collected_context=collected_context,
                missing_fields=missing_fields,
                questions=questions,
                confidence=confidence,
                reason="More context is needed before suggesting a targeted fix.",
                urgency_level=understanding.urgency_level if understanding else "low",
                urgency_signals=understanding.urgency_signals if understanding else [],
                issue_summary=understanding.short_issue_summary if understanding else None,
                secondary_category=understanding.secondary_category if understanding else None,
                explicit_human_requested=understanding.explicit_human_requested if understanding else False,
                security_sensitive=understanding.security_sensitive if understanding else False,
                business_impact=understanding.business_impact if understanding else None,
                source=understanding.source if understanding else "deterministic",
                structured_questions=structured_questions,
            )

        return TriageDecision(
            action=TriageAction.SUGGEST_FIX,
            category=category,
            stage=ConversationStage.WAITING_FOR_FEEDBACK,
            collected_context=collected_context,
            missing_fields=missing_fields,
            questions=[],
            confidence=confidence,
            reason="Ready to suggest KB-grounded troubleshooting.",
            urgency_level=understanding.urgency_level if understanding else "low",
            urgency_signals=understanding.urgency_signals if understanding else [],
            issue_summary=understanding.short_issue_summary if understanding else None,
            secondary_category=understanding.secondary_category if understanding else None,
            explicit_human_requested=understanding.explicit_human_requested if understanding else False,
            security_sensitive=understanding.security_sensitive if understanding else False,
            business_impact=understanding.business_impact if understanding else None,
            source=understanding.source if understanding else "deterministic",
        )

    def build_clarifying_response(self, category: str, questions: list[str]) -> str:
        label = category.replace("_", " ").title()
        numbered_questions = "\n".join(f"{index}. {question}" for index, question in enumerate(questions, start=1))
        return (
            f"I categorized this as {label}. I need a little more detail so I can avoid generic steps.\n\n"
            f"{numbered_questions}\n\n"
            "Reply with whatever you know, and I will use it to give a targeted fix."
        )

    def _questions_for_missing(self, fields: tuple[DiagnosticField, ...], missing_fields: list[str]) -> list[str]:
        generic_questions = {
            "device_type": "Which device are you using, such as laptop, phone, or desktop?",
            "device_os": "Which operating system are you using, such as Windows or macOS?",
            "application": "Which application or company service is affected?",
            "affected_app": "Which application or company service is affected?",
            "error_message": "What exact error message do you see?",
            "business_impact": "Is this blocking your work or affecting multiple people?",
            "urgency": "How urgent is this for your work today?",
        }
        questions = [field.question for field in fields if field.key in missing_fields]
        for field in missing_fields:
            if field not in {known_field.key for known_field in fields} and field in generic_questions:
                questions.append(generic_questions[field])
        return questions[:3]

    def _merge_understanding_context(self, context: dict, understanding: IssueUnderstanding) -> dict:
        merged = dict(context)
        if understanding.short_issue_summary:
            merged.setdefault("issue_summary", understanding.short_issue_summary)
        if understanding.business_impact:
            merged["business_impact"] = understanding.business_impact
        if understanding.urgency_level and understanding.urgency_level != "low":
            merged["urgency_level"] = understanding.urgency_level
        if understanding.urgency_signals:
            merged["urgency_signals"] = understanding.urgency_signals
        return merged

    def _escalation_reason(self, issue_text: str, understanding: IssueUnderstanding | None) -> str | None:
        lower = issue_text.lower()
        if understanding:
            if understanding.security_sensitive:
                return "Security-sensitive wording requires human review."
            if understanding.explicit_human_requested:
                return "User explicitly requested human support."
            if understanding.urgency_level == "critical":
                return "Critical urgency signal requires human review."
            if understanding.recommended_next_action == "escalate" and understanding.confidence_score < 0.45:
                return "Issue confidence is too low to continue safely."
        if self._is_security_critical(issue_text):
            return "Security-sensitive wording requires human review."
        if "locked out" in lower or ("account" in lower and "locked" in lower):
            return "Access lockout requires human review."
        if any(phrase in lower for phrase in ["human", "technician", "agent", "need support now", "talk to someone"]):
            return "User explicitly requested human support."
        if any(phrase in lower for phrase in ["cannot work", "can't work", "payroll", "ceo cannot", "production down"]):
            return "Critical business impact requires human review."
        return None

    def _extract_context(self, text: str, existing_context: dict) -> dict:
        context = dict(existing_context)
        lower = text.lower()

        device_os = self._detect_device_os(lower)
        if device_os:
            context["device_os"] = device_os

        if re.search(r"\b(outlook|gmail|apple mail|webmail|mail app)\b", lower):
            context["email_client"] = re.search(r"\b(outlook|gmail|apple mail|webmail|mail app)\b", lower).group(1)

        if re.search(r"\b(vpn|wifi|wi-fi|outlook|gmail|teams|slack|browser|chrome|edge|laptop|desktop)\b", lower):
            context.setdefault("affected_app", re.search(r"\b(vpn|wifi|wi-fi|outlook|gmail|teams|slack|browser|chrome|edge|laptop|desktop)\b", lower).group(1))

        if "internet works" in lower or "websites work" in lower or "normal websites" in lower:
            context["internet_working"] = "yes"
        elif "no internet" in lower or "internet does not work" in lower:
            context["internet_working"] = "no"

        if "no mfa" in lower or "mfa never" in lower or "not receiving mfa" in lower or "no prompt" in lower:
            context["mfa_prompt"] = "no"
        elif "mfa" in lower or "authenticator" in lower:
            context["mfa_prompt"] = "yes"
            context["mfa_available"] = "yes"

        if "locked" in lower:
            context["account_locked"] = "yes"
        if "reset" in lower:
            context["reset_attempted"] = "yes"
        if "access denied" in lower or "permission denied" in lower:
            context["account_locked"] = "access_denied"

        if "webmail works" in lower or "browser works" in lower:
            context["webmail_works"] = "yes"
        elif "webmail" in lower and ("not" in lower or "doesn't" in lower or "does not" in lower):
            context["webmail_works"] = "no"

        if "send" in lower or "sending" in lower:
            context["send_receive_scope"] = "sending"
        elif "receive" in lower or "receiving" in lower:
            context["send_receive_scope"] = "receiving"
        elif "sync" in lower:
            context["send_receive_scope"] = "sync"
        elif "attachment" in lower:
            context["send_receive_scope"] = "attachments"

        if "other devices work" in lower or "phone works" in lower:
            context["other_devices_working"] = "yes"
        elif "all devices" in lower or "multiple devices" in lower:
            context["other_devices_working"] = "no"

        network_match = re.search(r"(?:network|ssid|wifi|wi-fi)\s+(?:is\s+|named\s+|called\s+)?['\"]?([a-z0-9 _-]{3,40})['\"]?", lower)
        if network_match:
            context["network_name"] = network_match.group(1).strip()

        if "restarted" in lower or "restart done" in lower:
            context["restart_done"] = "yes"
        if re.search(r"\b(chrome|edge|firefox|safari|browser)\b", lower):
            context["browser"] = re.search(r"\b(chrome|edge|firefox|safari|browser)\b", lower).group(1)
        if "private window" in lower or "incognito" in lower or "cleared cache" in lower or "clear cache" in lower:
            context["cache_cleared"] = "yes"
        if re.search(r"\b(printer|print|printing|scanner|scan)\b", lower):
            context.setdefault("affected_app", "printer")
        printer_match = re.search(r"(?:printer|queue)\s+(?:is\s+|named\s+|called\s+)?['\"]?([a-z0-9 _-]{3,40})['\"]?", lower)
        if printer_match:
            context["printer_name"] = printer_match.group(1).strip()
        if "ethernet" in lower or "lan" in lower:
            context["connection_type"] = "ethernet"
        elif "hotspot" in lower:
            context["connection_type"] = "hotspot"
        elif "wifi" in lower or "wi-fi" in lower:
            context["connection_type"] = "wifi"
        if "all websites" in lower or "everything is down" in lower:
            context["scope"] = "all_sites"
        elif "internal" in lower or "company" in lower or "intranet" in lower:
            context["scope"] = "company_services"
        if "other people" in lower or "multiple people" in lower or "everyone" in lower:
            context["other_users_affected"] = "yes"
        if "install" in lower or "update" in lower:
            context["recent_change"] = self._shorten(text)

        if "blocking" in lower or "cannot work" in lower or "urgent" in lower:
            context["business_impact"] = "blocking work"

        if any(token in lower for token in ["started", "since", "today", "yesterday", "morning", "afternoon"]):
            context.setdefault("when_started", self._shorten(text))

        error_message = self._detect_error_message(text)
        if error_message:
            context["error_message"] = error_message

        return context

    def _detect_device_os(self, lower: str) -> str | None:
        if "windows" in lower or "win 11" in lower or "win11" in lower:
            return "Windows"
        if "mac" in lower or "macos" in lower or "macbook" in lower:
            return "macOS"
        if "linux" in lower or "ubuntu" in lower:
            return "Linux"
        if "iphone" in lower or "ios" in lower:
            return "iOS"
        if "android" in lower:
            return "Android"
        return None

    def _detect_error_message(self, text: str) -> str | None:
        quoted = re.search(r"['\"]([^'\"]{4,160})['\"]", text)
        if quoted:
            return quoted.group(1).strip()

        lower = text.lower()
        error_index = lower.find("error")
        if error_index >= 0:
            return self._shorten(text[error_index:])
        if "says" in lower:
            return self._shorten(text[lower.find("says"):])
        return None

    def _shorten(self, text: str, limit: int = 180) -> str:
        compact = " ".join(text.split())
        return compact[:limit]

    def _is_security_critical(self, text: str) -> bool:
        lower = text.lower()
        security_terms = [
            "phishing",
            "clicked suspicious",
            "suspicious email",
            "malware",
            "ransomware",
            "data breach",
            "account compromised",
            "unauthorized login",
            "stolen laptop",
            "laptop was stolen",
            "device stolen",
            "stolen device",
            "lost laptop",
            "lost device",
        ]
        return any(term in lower for term in security_terms)
