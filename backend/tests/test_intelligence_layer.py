import json

from app.repositories.user_repository import UserRepository
from app.services.classification_service import ClassificationService
from app.services.chat_service import ChatService
from app.services.issue_understanding_service import IssueUnderstandingService


class FakeLLMClient:
    def __init__(self, content: str):
        self.content = content
        self.is_configured = True

    def chat_completion(self, **kwargs):
        return self.content


def test_llm_issue_understanding_handles_typo_heavy_email_query():
    service = IssueUnderstandingService(
        llm_client=FakeLLMClient(
            json.dumps(
                {
                    "primary_category": "EMAIL",
                    "secondary_category": None,
                    "confidence_score": 0.88,
                    "missing_slots": ["email_client", "error_message"],
                    "urgency_level": "medium",
                    "urgency_signals": [],
                    "user_intent": "get_email_sync_help",
                    "short_issue_summary": "User says Outlook mail is not syncing.",
                    "recommended_next_action": "ask_clarification",
                    "explicit_human_requested": False,
                    "security_sensitive": False,
                    "business_impact": None,
                }
            )
        )
    )

    result = service.understand(
        issue_text="outlok not syncng",
        conversation_history="",
        existing_context={},
    )

    assert result.primary_category == "EMAIL"
    assert result.confidence_score == 0.88
    assert result.source == "azure_openai"


def test_invalid_llm_understanding_falls_back_to_deterministic():
    service = IssueUnderstandingService(llm_client=FakeLLMClient("not json"))

    result = service.understand(
        issue_text="outlok not syncng",
        conversation_history="",
        existing_context={},
    )

    assert result.primary_category == "EMAIL"
    assert result.source == "deterministic"


def test_llm_escalation_recommendation_is_guardrailed_by_deterministic_signals():
    service = IssueUnderstandingService(
        llm_client=FakeLLMClient(
            json.dumps(
                {
                    "primary_category": "VPN",
                    "secondary_category": None,
                    "confidence_score": 0.82,
                    "missing_slots": [],
                    "urgency_level": "critical",
                    "urgency_signals": ["critical"],
                    "user_intent": "get_support",
                    "short_issue_summary": "User cannot connect to VPN.",
                    "recommended_next_action": "escalate",
                    "explicit_human_requested": False,
                    "security_sensitive": True,
                    "business_impact": "unknown",
                }
            )
        )
    )

    result = service.understand(
        issue_text="vpn not working",
        conversation_history="USER: hello",
        existing_context={},
    )

    assert result.security_sensitive is False
    assert result.urgency_level == "low"
    assert result.recommended_next_action != "escalate"


def test_messy_real_world_phrasing_classifies_to_expected_categories():
    classifier = ClassificationService()

    scenarios = {
        "vpn conection not wrking": "VPN",
        "mail stuck": "EMAIL",
        "cant login since morning": "PASSWORD",
        "internet is there but company apps are not opening": "VPN",
    }

    for text, expected_category in scenarios.items():
        result = classifier.classify(text)
        assert result.category == expected_category


def test_compound_issue_identifies_secondary_category_without_llm():
    service = IssueUnderstandingService(llm_client=FakeLLMClient("not json"))

    result = service.understand(
        issue_text="laptop very slow and outlook also not opening",
        conversation_history="",
        existing_context={},
    )

    assert result.primary_category == "DEVICE_PERFORMANCE"
    assert result.secondary_category == "EMAIL"
    assert result.source == "deterministic"


def test_explicit_human_request_escalates_immediately(db):
    user = UserRepository(db).get_by_email("user@company.com")
    service = ChatService(db)
    conversation = service.create_conversation(user)

    result = service.submit_message(user, conversation.id, "I need human support now")

    assert result.escalated is True
    assert result.ticket is not None
    assert result.assistant_message.meta["explicit_human_requested"] is True


def test_account_locked_escalates_immediately(db):
    user = UserRepository(db).get_by_email("user@company.com")
    service = ChatService(db)
    conversation = service.create_conversation(user)

    result = service.submit_message(user, conversation.id, "my account is locked")

    assert result.escalated is True
    assert result.ticket is not None
    assert "lockout" in result.assistant_message.meta["reason"].lower()


def test_stolen_laptop_escalates_as_security_sensitive(db):
    user = UserRepository(db).get_by_email("user@company.com")
    service = ChatService(db)
    conversation = service.create_conversation(user)

    result = service.submit_message(user, conversation.id, "my laptop was stolen")

    assert result.escalated is True
    assert result.ticket is not None
    assert result.assistant_message.meta["security_sensitive"] is True


def test_escalated_ticket_title_uses_support_issue_not_prior_greeting(db):
    user = UserRepository(db).get_by_email("user@company.com")
    service = ChatService(db)
    conversation = service.create_conversation(user)

    service.submit_message(user, conversation.id, "hello")
    result = service.submit_message(user, conversation.id, "my account is locked")

    assert result.escalated is True
    assert result.ticket is not None
    assert "account is locked" in result.ticket.title.lower()
    assert "hello" not in result.ticket.title.lower()


def test_ambiguous_query_escalates_if_still_unknown_after_clarification(db):
    user = UserRepository(db).get_by_email("user@company.com")
    service = ChatService(db)
    conversation = service.create_conversation(user)

    first = service.submit_message(user, conversation.id, "not working")
    assert first.assistant_message.meta["triage_action"] == "ASK_CLARIFYING_QUESTIONS"

    second = service.submit_message(user, conversation.id, "still not working")

    assert second.escalated is True
    assert second.ticket is not None
    assert "ambiguous" in second.assistant_message.meta["reason"].lower()
