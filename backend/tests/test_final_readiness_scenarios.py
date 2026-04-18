from app.models.conversation import ConversationStatus
from app.models.ticket import TicketApprovalStatus, TicketRequestType, TicketStatus
from app.repositories.user_repository import UserRepository
from app.services.chat_intent_service import ChatIntentService, ChatIntentType
from app.services.chat_service import ChatService
from app.services.notification_service import NotificationService
from app.services.ticket_service import TicketService


def _user(db):
    return UserRepository(db).get_by_email("user@company.com")


def _submit(db, text: str):
    user = _user(db)
    service = ChatService(db)
    conversation = service.create_conversation(user)
    return user, service.submit_message(user, conversation.id, text)


def test_final_non_support_inputs_are_bounded_and_do_not_create_tickets(db):
    cases = [
        ("hi", ChatIntentType.GREETING),
        ("hello, what can you do?", ChatIntentType.SMALL_TALK),
        ("tell me a joke", ChatIntentType.IRRELEVANT),
    ]
    for query, expected_intent in cases:
        _, result = _submit(db, query)
        assert result.assistant_message.meta["intent_type"] == expected_intent.value
        assert result.escalated is False
        assert result.ticket is None
        assert result.kb_titles == []


def test_final_contextual_guided_questions_do_not_use_generic_yes_no_for_login(db):
    _, result = _submit(db, "having problem while logging in")

    assert result.category == "ACCESS"
    assert result.assistant_message.meta["triage_action"] == "ASK_CLARIFYING_QUESTIONS"
    question = result.assistant_message.meta["structured_questions"][0]
    assert question["field"] == "affected_app"
    labels = {option["label"] for option in question["options"]}
    assert {"Email (Outlook/Gmail)", "VPN", "Company Portal", "Internal Tool", "HR System"}.issubset(labels)
    assert {"Yes", "No", "Not sure"}.isdisjoint(labels)


def test_final_common_support_scenarios_have_relevant_actions_or_guidance(db):
    cases = [
        ("forgot password", "PASSWORD", {"Reset Password"}),
        ("vpn not working", "VPN", {"Open VPN Setup", "Download VPN Client"}),
        ("email not working", "EMAIL", {"Open Webmail"}),
        ("wifi issue", "WIFI", {"Open Network Troubleshooter"}),
    ]
    for query, expected_category, expected_actions in cases:
        _, result = _submit(db, query)
        assert result.category == expected_category
        actions = {action["label"] for action in result.assistant_message.actions}
        assert expected_actions & actions
        assert result.assistant_message.meta["triage_action"] in {"ASK_CLARIFYING_QUESTIONS", "SUGGEST_FIX"}


def test_final_explicit_human_security_and_urgent_cases_escalate_with_assignment_and_notifications(db):
    cases = [
        "connect me to a human now",
        "security issue suspicious login detected",
        "i cannot work, please help urgently",
        "account locked and payroll access blocked",
    ]
    for query in cases:
        user, result = _submit(db, query)
        ticket = result.ticket
        assert result.escalated is True
        assert ticket is not None
        assert ticket.status == TicketStatus.ESCALATED
        assert ticket.technician_id is not None
        assert ticket.assignment_source == "auto"
        assert result.conversation.status == ConversationStatus.ESCALATED
        assert {"Connect to Technician"} <= {action["label"] for action in result.assistant_message.actions}
        titles = [notification.title for notification in NotificationService(db).list_for_user(user)]
        assert any(f"Ticket #{ticket.id}" in title for title in titles)


def test_final_software_install_approval_scenarios_create_real_request_tickets(db):
    cases = [
        ("need VS Code installed", "VS Code"),
        ("need admin rights to install software", "Software not specified"),
        ("need Photoshop approved for client design work", "Photoshop"),
        ("need approval to install VPN client", "Vpn Client"),
    ]
    for query, expected_software in cases:
        _, result = _submit(db, query)
        ticket = result.ticket
        assert result.escalated is True
        assert ticket is not None
        assert ticket.request_type == TicketRequestType.SOFTWARE_INSTALL
        assert ticket.approval_required is True
        assert ticket.approval_status == TicketApprovalStatus.PENDING_APPROVAL
        assert ticket.requested_software == expected_software
        assert "pending admin approval" in result.assistant_message.content.lower()


def test_final_assigned_ticket_chat_and_approval_flow_are_role_safe(db):
    user, result = _submit(db, "need Photoshop installed for design work")
    admin = UserRepository(db).get_by_email("admin@company.com")
    technician = result.ticket.technician
    service = TicketService(db)

    service.add_ticket_message(user, result.ticket, "This is for the design team laptop.")
    service.add_ticket_message(technician, result.ticket, "I will proceed after approval.")
    before_approval = service.get_visible_ticket(technician, result.ticket.id)
    assert len(before_approval.ticket_messages) == 2

    try:
        service.update_ticket(technician, before_approval, {"status": TicketStatus.IN_PROGRESS})
        assert False, "Technician should not proceed before software approval"
    except ValueError:
        pass

    approved = service.update_approval(admin, before_approval, TicketApprovalStatus.APPROVED, "Approved for design project.")
    updated = service.update_ticket(technician, approved, {"status": TicketStatus.IN_PROGRESS})

    assert updated.status == TicketStatus.IN_PROGRESS
    assert updated.approval_status == TicketApprovalStatus.IN_PROGRESS
    user_titles = [notification.title for notification in NotificationService(db).list_for_user(user)]
    tech_titles = [notification.title for notification in NotificationService(db).list_for_user(technician)]
    assert any("approval approved" in title.lower() for title in user_titles)
    assert any("User replied" in title for title in tech_titles)
