from app.repositories.user_repository import UserRepository
from app.services.chat_service import ChatService
from app.services.openai_response_service import GeneratedSupportResponse


class FakeOpenAIResponseGenerator:
    def generate_support_response(self, **kwargs):
        return GeneratedSupportResponse(content="OpenAI generated KB-grounded answer.", source="openai")

    def generate_escalation_summary(self, **kwargs):
        return GeneratedSupportResponse(content=None, source="deterministic_fallback", error="not_configured")


def test_chat_escalates_after_two_unresolved_attempts(db):
    user = UserRepository(db).get_by_email("user@company.com")
    service = ChatService(db)
    conversation = service.create_conversation(user)

    message_result = service.submit_message(user, conversation.id, "VPN is not connecting")
    assert message_result.category == "VPN"
    assert message_result.escalated is False
    assert message_result.assistant_message.meta["triage_action"] == "ASK_CLARIFYING_QUESTIONS"

    fix_result = service.submit_message(
        user,
        conversation.id,
        "Windows laptop. Internet works without VPN. No MFA prompt appears. Error says connection failed.",
    )
    assert fix_result.assistant_message.meta["triage_action"] == "SUGGEST_FIX"

    first_feedback = service.record_feedback(user, conversation.id, resolved=False)
    assert first_feedback.conversation.failure_count == 1
    assert first_feedback.escalated is False

    second_feedback = service.record_feedback(user, conversation.id, resolved=False)
    assert second_feedback.conversation.failure_count == 2
    assert second_feedback.escalated is True
    assert second_feedback.ticket is not None
    assert second_feedback.ticket.status.value == "ESCALATED"


def test_chat_uses_openai_response_generator_when_available(db):
    user = UserRepository(db).get_by_email("user@company.com")
    service = ChatService(db, response_generator=FakeOpenAIResponseGenerator())
    conversation = service.create_conversation(user)

    result = service.submit_message(
        user,
        conversation.id,
        "VPN on Windows. Internet works without VPN. MFA prompt appears. Error says connection failed.",
    )

    assert result.assistant_message.content == "OpenAI generated KB-grounded answer."
    assert result.assistant_message.meta["response_source"] == "openai"
