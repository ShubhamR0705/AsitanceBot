import pytest

from app.repositories.user_repository import UserRepository
from app.services.chat_intent_service import ChatIntentService, ChatIntentType
from app.services.chat_service import ChatService
from app.services.diagnostic_playbooks import DiagnosticField
from app.services.guided_question_service import GuidedQuestionService


SCENARIOS = [
    ("hi", ChatIntentType.GREETING),
    ("hello", ChatIntentType.GREETING),
    ("hey there", ChatIntentType.GREETING),
    ("good morning", ChatIntentType.GREETING),
    ("how are you", ChatIntentType.SMALL_TALK),
    ("what can you do", ChatIntentType.SMALL_TALK),
    ("who are you", ChatIntentType.SMALL_TALK),
    ("thanks", ChatIntentType.SMALL_TALK),
    ("tell me a joke", ChatIntentType.IRRELEVANT),
    ("what is the weather", ChatIntentType.IRRELEVANT),
    ("who is president", ChatIntentType.IRRELEVANT),
    ("give me a recipe", ChatIntentType.IRRELEVANT),
    ("asdf", ChatIntentType.EMPTY),
    ("", ChatIntentType.EMPTY),
    ("     ", ChatIntentType.EMPTY),
    ("this is useless", ChatIntentType.ABUSIVE),
    ("connect me to human", ChatIntentType.SUPPORT_REQUEST),
    ("give me a technician", ChatIntentType.SUPPORT_REQUEST),
    ("hi vpn not working", ChatIntentType.SUPPORT_REQUEST),
    ("hello my outlook is stuck", ChatIntentType.SUPPORT_REQUEST),
    ("vpn conection not wrking", ChatIntentType.SUPPORT_REQUEST),
    ("outlok not syncng", ChatIntentType.SUPPORT_REQUEST),
    ("password not taking", ChatIntentType.SUPPORT_REQUEST),
    ("account locked", ChatIntentType.SUPPORT_REQUEST),
    ("wifi keeps dropping", ChatIntentType.SUPPORT_REQUEST),
    ("internet is there but company apps are not opening", ChatIntentType.SUPPORT_REQUEST),
    ("laptop hangs again and again", ChatIntentType.SUPPORT_REQUEST),
    ("system slow and outlook also not opening", ChatIntentType.SUPPORT_REQUEST),
    ("printer offline", ChatIntentType.SUPPORT_REQUEST),
    ("print queue stuck", ChatIntentType.SUPPORT_REQUEST),
    ("browser not loading payroll portal", ChatIntentType.SUPPORT_REQUEST),
    ("chrome keeps looping on login", ChatIntentType.SUPPORT_REQUEST),
    ("software install failed", ChatIntentType.SUPPORT_REQUEST),
    ("Teams app crashed", ChatIntentType.SUPPORT_REQUEST),
    ("access denied to HR portal", ChatIntentType.SUPPORT_REQUEST),
    ("payroll access blocked", ChatIntentType.SUPPORT_REQUEST),
    ("ethernet not working", ChatIntentType.SUPPORT_REQUEST),
    ("dns issue with intranet", ChatIntentType.SUPPORT_REQUEST),
    ("security issue malware popup", ChatIntentType.SUPPORT_REQUEST),
    ("my laptop was stolen", ChatIntentType.SUPPORT_REQUEST),
    ("CEO cannot login", ChatIntentType.SUPPORT_REQUEST),
    ("all users cannot access email", ChatIntentType.SUPPORT_REQUEST),
    ("cannot work since morning", ChatIntentType.SUPPORT_REQUEST),
    ("app says license expired", ChatIntentType.SUPPORT_REQUEST),
    ("scanner cannot send to email", ChatIntentType.SUPPORT_REQUEST),
    ("office login problem", ChatIntentType.SUPPORT_REQUEST),
    ("company portal says 403", ChatIntentType.SUPPORT_REQUEST),
    ("websites work but internal site fails", ChatIntentType.SUPPORT_REQUEST),
    ("mfa prompt not coming", ChatIntentType.SUPPORT_REQUEST),
    ("mail attachment stuck", ChatIntentType.SUPPORT_REQUEST),
]


@pytest.mark.parametrize(("query", "expected_intent"), SCENARIOS)
def test_intent_router_handles_real_world_inputs(query, expected_intent):
    result = ChatIntentService().route(query)

    assert result.intent_type == expected_intent


def test_greeting_does_not_enter_support_feedback_flow(db):
    user = UserRepository(db).get_by_email("user@company.com")
    service = ChatService(db)
    conversation = service.create_conversation(user)

    result = service.submit_message(user, conversation.id, "hello")

    assert result.escalated is False
    assert result.assistant_message.meta["intent_type"] == "GREETING"
    assert result.assistant_message.meta["support_response"] is False
    assert result.kb_titles == []


def test_mixed_greeting_issue_enters_support_flow(db):
    user = UserRepository(db).get_by_email("user@company.com")
    service = ChatService(db)
    conversation = service.create_conversation(user)

    result = service.submit_message(user, conversation.id, "hi vpn not working")

    assert result.category == "VPN"
    assert result.assistant_message.meta["intent_type"] == "SUPPORT_REQUEST"


def test_clarification_response_includes_guided_question_options(db):
    user = UserRepository(db).get_by_email("user@company.com")
    service = ChatService(db)
    conversation = service.create_conversation(user)

    result = service.submit_message(user, conversation.id, "vpn not working")

    assert result.assistant_message.meta["type"] == "question"
    assert result.assistant_message.meta["input_type"] == "single_select"
    assert result.assistant_message.meta["options"]
    questions = result.assistant_message.meta["structured_questions"]
    assert questions
    assert questions[0]["type"] == "question"
    assert questions[0]["input_type"] in {"single_select", "multi_select"}
    assert questions[0]["options"]
    assert "1." not in result.assistant_message.content
    assert "Reply with whatever you know" not in result.assistant_message.content


def test_structured_answer_is_stored_in_conversation_context(db):
    user = UserRepository(db).get_by_email("user@company.com")
    service = ChatService(db)
    conversation = service.create_conversation(user)
    service.submit_message(user, conversation.id, "vpn not working")

    result = service.submit_message(
        user,
        conversation.id,
        "",
        {
            "field": "internet_working",
            "value": "yes",
            "label": "Yes - normal websites work",
            "input_type": "single_select",
            "question": "Can you browse normal websites without the VPN connected?",
        },
    )

    user_message = [message for message in result.conversation.messages if message.sender.value == "USER"][-1]
    assert result.conversation.collected_context["internet_working"] == "yes"
    assert result.conversation.collected_context["structured_inputs"]["internet_working"] == "yes"
    assert user_message.meta["structured_response"]["field"] == "internet_working"
    assert "normal websites work" in user_message.content


def test_email_clarification_uses_email_client_options(db):
    user = UserRepository(db).get_by_email("user@company.com")
    service = ChatService(db)
    conversation = service.create_conversation(user)

    result = service.submit_message(user, conversation.id, "email not syncing")

    assert result.assistant_message.meta["field"] == "email_client"
    assert [option["label"] for option in result.assistant_message.meta["options"]][:3] == ["Outlook", "Webmail", "Apple Mail"]


def test_login_clarification_uses_service_options(db):
    user = UserRepository(db).get_by_email("user@company.com")
    service = ChatService(db)
    conversation = service.create_conversation(user)

    result = service.submit_message(user, conversation.id, "having problem while logging in")

    assert result.category == "ACCESS"
    assert result.assistant_message.meta["field"] == "affected_app"
    labels = [option["label"] for option in result.assistant_message.meta["options"]]
    assert labels[:5] == ["Email (Outlook/Gmail)", "VPN", "Company Portal", "Internal Tool", "HR System"]
    assert "Yes" not in labels
    assert "No" not in labels
    assert "Not sure" not in labels


def test_vpn_clarification_uses_vpn_issue_options(db):
    user = UserRepository(db).get_by_email("user@company.com")
    service = ChatService(db)
    conversation = service.create_conversation(user)

    result = service.submit_message(user, conversation.id, "vpn not working")

    assert result.assistant_message.meta["field"] == "vpn_issue_type"
    assert [option["label"] for option in result.assistant_message.meta["options"]][:4] == [
        "Cannot connect",
        "Connected but no internet",
        "Slow connection",
        "Disconnecting frequently",
    ]
    assert "Yes" not in [option["label"] for option in result.assistant_message.meta["options"]]
    assert "No" not in [option["label"] for option in result.assistant_message.meta["options"]]
    assert "Not sure" not in [option["label"] for option in result.assistant_message.meta["options"]]


def test_wifi_clarification_uses_wifi_issue_options(db):
    user = UserRepository(db).get_by_email("user@company.com")
    service = ChatService(db)
    conversation = service.create_conversation(user)

    result = service.submit_message(user, conversation.id, "wifi issue")

    assert result.assistant_message.meta["field"] == "wifi_issue_type"
    assert [option["label"] for option in result.assistant_message.meta["options"]][:4] == [
        "No networks visible",
        "Connected but no internet",
        "Slow internet",
        "Frequent disconnect",
    ]
    assert "Yes" not in [option["label"] for option in result.assistant_message.meta["options"]]
    assert "No" not in [option["label"] for option in result.assistant_message.meta["options"]]
    assert "Not sure" not in [option["label"] for option in result.assistant_message.meta["options"]]


def test_guided_question_generation_skips_free_text_fields():
    service = GuidedQuestionService()

    questions = service.build(
        fields=(DiagnosticField("error_message", "Exact error", "What exact error message do you see?"),),
        missing_fields=["error_message"],
        questions=["What exact error message do you see?"],
        category="ACCESS",
    )

    assert questions == []


def test_guided_question_sanitizer_repairs_bad_access_options():
    service = GuidedQuestionService()

    questions = service.sanitize_all(
        [
            {
                "type": "question",
                "question": "Which application or company service are you trying to access?",
                "field": "affected_app",
                "input_type": "single_select",
                "options": [
                    {"label": "Yes", "value": "yes"},
                    {"label": "No", "value": "no"},
                    {"label": "Not sure", "value": "unknown"},
                    {"label": "Other", "value": "other", "requires_text": True},
                ],
            }
        ],
        "ACCESS",
    )

    labels = [option["label"] for option in questions[0]["options"]]
    assert labels[:5] == ["Email (Outlook/Gmail)", "VPN", "Company Portal", "Internal Tool", "HR System"]
    assert "Yes" not in labels
    assert "No" not in labels
    assert "Not sure" not in labels


def test_irrelevant_input_is_redirected_without_kb(db):
    user = UserRepository(db).get_by_email("user@company.com")
    service = ChatService(db)
    conversation = service.create_conversation(user)

    result = service.submit_message(user, conversation.id, "tell me a joke")

    assert result.assistant_message.meta["intent_type"] == "IRRELEVANT"
    assert result.kb_titles == []


def test_human_request_without_issue_creates_controlled_handoff_ticket(db):
    user = UserRepository(db).get_by_email("user@company.com")
    service = ChatService(db)
    conversation = service.create_conversation(user)

    result = service.submit_message(user, conversation.id, "connect me to human")

    assert result.escalated is True
    assert result.ticket is not None
    assert result.assistant_message.meta["intent_type"] == "SUPPORT_REQUEST"


def test_human_request_with_existing_support_context_escalates(db):
    user = UserRepository(db).get_by_email("user@company.com")
    service = ChatService(db)
    conversation = service.create_conversation(user)
    service.submit_message(user, conversation.id, "VPN on Windows. Internet works. MFA prompt appears. Error says connection failed.")

    result = service.submit_message(user, conversation.id, "connect me to human")

    assert result.escalated is True
    assert result.ticket is not None
