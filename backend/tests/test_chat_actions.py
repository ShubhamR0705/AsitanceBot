import pytest

from app.repositories.user_repository import UserRepository
from app.services.action_registry import ActionRegistry
from app.services.chat_service import ChatService


@pytest.mark.parametrize(
    ("query", "expected_labels"),
    [
        ("forgot password", {"Reset Password"}),
        ("vpn not working", {"Open VPN Setup", "Download VPN Client"}),
        ("email not working", {"Open Webmail"}),
        ("wifi issue", {"Open Network Troubleshooter"}),
    ],
)
def test_chat_attaches_contextual_actions(db, query, expected_labels):
    user = UserRepository(db).get_by_email("user@company.com")
    service = ChatService(db)
    conversation = service.create_conversation(user)

    result = service.submit_message(user, conversation.id, query)

    labels = {action["label"] for action in result.assistant_message.actions}
    assert expected_labels.issubset(labels)
    assert result.assistant_message.meta["actions"] == result.assistant_message.actions


def test_escalation_response_includes_connect_to_technician_action(db):
    user = UserRepository(db).get_by_email("user@company.com")
    service = ChatService(db)
    conversation = service.create_conversation(user)

    result = service.submit_message(user, conversation.id, "my account is locked")

    assert result.escalated is True
    assert result.ticket is not None
    assert result.assistant_message.actions == [
        {
            "label": "Connect to Technician",
            "type": "internal_route",
            "route": f"/user/tickets/{result.ticket.id}",
        }
    ]


def test_action_registry_rejects_untrusted_links():
    registry = ActionRegistry()

    assert registry.validate({"label": "Bad", "type": "link", "url": "https://evil.example/reset"}) is None
    assert registry.validate({"label": "Bad", "type": "link", "url": "http://company.com/reset-password"}) is None
    assert registry.validate({"label": "Reset Password", "type": "link", "url": "https://company.com/reset-password"}) == {
        "label": "Reset Password",
        "type": "link",
        "url": "https://company.com/reset-password",
    }
