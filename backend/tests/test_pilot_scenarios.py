import pytest

from app.models.conversation import ConversationStatus
from app.repositories.user_repository import UserRepository
from app.services.chat_intent_service import ChatIntentService, ChatIntentType
from app.services.chat_service import ChatService


SCENARIOS = [
    ("hi", ChatIntentType.GREETING, set(), False),
    ("hello, what can you do?", ChatIntentType.SMALL_TALK, set(), False),
    ("tell me a joke", ChatIntentType.IRRELEVANT, set(), False),
    ("having problem while logging in", ChatIntentType.SUPPORT_REQUEST, {"ACCESS"}, False),
    ("account locked after too many attempts", ChatIntentType.SUPPORT_REQUEST, {"PASSWORD", "ACCESS"}, True),
    ("mfa code not working", ChatIntentType.SUPPORT_REQUEST, {"ACCESS"}, False),
    ("access denied for internal portal", ChatIntentType.SUPPORT_REQUEST, {"ACCESS"}, False),
    ("forgot password", ChatIntentType.SUPPORT_REQUEST, {"PASSWORD"}, False),
    ("reset link not received", ChatIntentType.SUPPORT_REQUEST, {"PASSWORD"}, False),
    ("password reset but still cannot login", ChatIntentType.SUPPORT_REQUEST, {"PASSWORD", "ACCESS"}, False),
    ("vpn not working", ChatIntentType.SUPPORT_REQUEST, {"VPN"}, False),
    ("vpn connected but internal sites not opening", ChatIntentType.SUPPORT_REQUEST, {"VPN"}, False),
    ("vpn disconnecting every few minutes", ChatIntentType.SUPPORT_REQUEST, {"VPN"}, False),
    ("wifi not working", ChatIntentType.SUPPORT_REQUEST, {"WIFI"}, False),
    ("connected but no internet", ChatIntentType.SUPPORT_REQUEST, {"NETWORK", "WIFI"}, False),
    ("ubuntu wifi networks not showing", ChatIntentType.SUPPORT_REQUEST, {"WIFI"}, False),
    ("internet slow only on office laptop", ChatIntentType.SUPPORT_REQUEST, {"NETWORK", "DEVICE_PERFORMANCE"}, False),
    ("outlook not syncing", ChatIntentType.SUPPORT_REQUEST, {"EMAIL"}, False),
    ("cannot send mail", ChatIntentType.SUPPORT_REQUEST, {"EMAIL"}, False),
    ("not receiving emails since morning", ChatIntentType.SUPPORT_REQUEST, {"EMAIL"}, False),
    ("laptop very slow", ChatIntentType.SUPPORT_REQUEST, {"DEVICE_PERFORMANCE"}, False),
    ("system hangs again and again", ChatIntentType.SUPPORT_REQUEST, {"DEVICE_PERFORMANCE"}, False),
    ("app crashing on startup", ChatIntentType.SUPPORT_REQUEST, {"SOFTWARE"}, False),
    ("internal website not opening", ChatIntentType.SUPPORT_REQUEST, {"BROWSER", "NETWORK", "VPN"}, False),
    ("hr portal not loading", ChatIntentType.SUPPORT_REQUEST, {"ACCESS", "BROWSER", "GENERAL"}, False),
    ("company app install failed", ChatIntentType.SUPPORT_REQUEST, {"SOFTWARE"}, False),
    ("i cannot work, please help urgently", ChatIntentType.SUPPORT_REQUEST, {"GENERAL"}, True),
    ("my account is locked and i need payroll access", ChatIntentType.SUPPORT_REQUEST, {"PASSWORD", "ACCESS"}, True),
    ("connect me to a human now", ChatIntentType.SUPPORT_REQUEST, {"GENERAL"}, True),
    ("security issue, suspicious login detected", ChatIntentType.SUPPORT_REQUEST, {"ACCESS", "GENERAL"}, True),
]


@pytest.mark.parametrize(("query", "expected_intent", "expected_categories", "expected_escalated"), SCENARIOS)
def test_pilot_chat_scenarios(db, query, expected_intent, expected_categories, expected_escalated):
    routed = ChatIntentService().route(query)
    assert routed.intent_type == expected_intent

    user = UserRepository(db).get_by_email("user@company.com")
    service = ChatService(db)
    conversation = service.create_conversation(user)
    result = service.submit_message(user, conversation.id, query)

    assert result.assistant_message.content.strip()
    if expected_intent == ChatIntentType.SUPPORT_REQUEST:
        assert result.category in expected_categories
        assert result.escalated is expected_escalated
        if expected_escalated:
            assert result.ticket is not None
            assert result.conversation.status == ConversationStatus.ESCALATED
        else:
            assert result.assistant_message.meta.get("triage_action") in {"ASK_CLARIFYING_QUESTIONS", "SUGGEST_FIX"}
            if result.assistant_message.meta.get("triage_action") == "ASK_CLARIFYING_QUESTIONS":
                assert result.assistant_message.meta.get("structured_questions") or result.assistant_message.meta.get("questions")
            else:
                assert result.kb_titles
    else:
        assert result.escalated is False
        assert result.kb_titles == []
        assert result.assistant_message.meta["intent_type"] == expected_intent.value
