from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.init_db import seed_knowledge_base
from app.db.session import SessionLocal
from app.models.audit_log import AuditAction, AuditLog
from app.models.conversation import Conversation, ConversationStage, ConversationStatus, Message, MessageSender
from app.models.message_feedback import MessageFeedback
from app.models.notification import Notification, NotificationChannel
from app.models.ticket import Ticket, TicketPriority, TicketStatus
from app.models.user import User, UserRole


def ensure_user(db, *, email: str, password: str, full_name: str, role: UserRole) -> User:
    user = db.query(User).filter(User.email == email).first()
    if user:
        changed = False
        if user.role != role:
            user.role = role
            changed = True
        if not user.is_active:
            user.is_active = True
            changed = True
        if changed:
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    user = User(
        email=email,
        full_name=full_name,
        hashed_password=hash_password(password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def ensure_demo_users(db) -> tuple[User, User, User]:
    settings = get_settings()
    admin = ensure_user(
        db,
        email=settings.demo_admin_email,
        password=settings.demo_admin_password,
        full_name="Avery Admin",
        role=UserRole.ADMIN,
    )
    technician = ensure_user(
        db,
        email=settings.demo_technician_email,
        password=settings.demo_technician_password,
        full_name="Taylor Technician",
        role=UserRole.TECHNICIAN,
    )
    user = ensure_user(
        db,
        email=settings.demo_user_email,
        password=settings.demo_user_password,
        full_name="Jordan User",
        role=UserRole.USER,
    )
    return admin, technician, user


def add_message(db, *, conversation: Conversation, sender: MessageSender, content: str, meta: dict | None = None) -> Message:
    message = Message(conversation_id=conversation.id, sender=sender, content=content, meta=meta or {})
    db.add(message)
    db.flush()
    return message


def ensure_demo_ticket(
    db,
    *,
    user: User,
    technician: User | None,
    title: str,
    category: str,
    description: str,
    status: TicketStatus,
    priority: TicketPriority,
    routing_group: str,
    urgency_level: str,
    failure_count: int,
    messages: list[tuple[MessageSender, str, dict | None]],
    resolution_notes: str | None = None,
    internal_notes: str | None = None,
    sla_breached: bool = False,
) -> Ticket:
    existing = db.query(Ticket).filter(Ticket.title == title, Ticket.user_id == user.id).first()
    if existing:
        return existing

    now = datetime.utcnow()
    created_at = now - timedelta(hours=6 + failure_count)
    resolved_at = now - timedelta(hours=1) if status in {TicketStatus.RESOLVED, TicketStatus.CLOSED} else None
    conversation = Conversation(
        user_id=user.id,
        category=category,
        status=ConversationStatus.RESOLVED if resolved_at else ConversationStatus.ESCALATED,
        failure_count=failure_count,
        triage_stage=ConversationStage.RESOLVED if resolved_at else ConversationStage.ESCALATED,
        collected_context={"demo_seed": True},
        last_triage={
            "primary_category": category,
            "confidence_score": 0.82,
            "urgency_level": urgency_level,
            "short_issue_summary": title,
        },
        escalation_summary=f"Demo handoff: {description}",
        created_at=created_at,
    )
    db.add(conversation)
    db.flush()

    assistant_for_feedback: Message | None = None
    for sender, content, meta in messages:
        message = add_message(db, conversation=conversation, sender=sender, content=content, meta=meta)
        if sender == MessageSender.ASSISTANT and assistant_for_feedback is None:
            assistant_for_feedback = message

    ticket = Ticket(
        conversation_id=conversation.id,
        user_id=user.id,
        technician_id=technician.id if technician else None,
        category=category,
        title=title,
        description=description,
        routing_group=routing_group,
        status=status,
        priority=priority,
        internal_notes=internal_notes,
        resolution_notes=resolution_notes,
        first_response_at=created_at + timedelta(minutes=35) if technician else None,
        sla_due_at=created_at + timedelta(hours=2 if priority == TicketPriority.CRITICAL else 8 if priority == TicketPriority.HIGH else 24),
        sla_breached=sla_breached,
        created_at=created_at,
        resolved_at=resolved_at,
    )
    db.add(ticket)
    db.flush()

    db.add_all(
        [
            AuditLog(
                ticket_id=ticket.id,
                actor_user_id=None,
                action_type=AuditAction.TICKET_CREATED,
                previous_value=None,
                new_value={"status": ticket.status.value, "priority": ticket.priority.value},
                summary=f"Demo ticket created: {ticket.title}",
            ),
            AuditLog(
                ticket_id=ticket.id,
                actor_user_id=None,
                action_type=AuditAction.ESCALATION_TRIGGERED,
                previous_value={"conversation_status": "ACTIVE"},
                new_value={"conversation_status": "ESCALATED"},
                summary="AI escalated after guided troubleshooting context was collected.",
            ),
        ]
    )
    if technician:
        db.add(
            AuditLog(
                ticket_id=ticket.id,
                actor_user_id=technician.id,
                action_type=AuditAction.TICKET_ASSIGNED,
                previous_value={"technician_id": None},
                new_value={"technician_id": technician.id},
                summary=f"Assigned to {technician.full_name}.",
            )
        )
        db.add(
            Notification(
                recipient_user_id=technician.id,
                actor_user_id=None,
                ticket_id=ticket.id,
                channel=NotificationChannel.IN_APP,
                title="Ticket assigned",
                body=f"{ticket.title} is ready for review.",
            )
        )
    db.add(
        Notification(
            recipient_user_id=user.id,
            actor_user_id=technician.id if technician else None,
            ticket_id=ticket.id,
            channel=NotificationChannel.IN_APP,
            title="Ticket update",
            body=f"{ticket.title} is {ticket.status.value.replace('_', ' ').title()}.",
        )
    )
    if assistant_for_feedback:
        db.add(
            MessageFeedback(
                message_id=assistant_for_feedback.id,
                conversation_id=conversation.id,
                user_id=user.id,
                helpful=status in {TicketStatus.RESOLVED, TicketStatus.CLOSED},
                note="Demo feedback seeded for analytics.",
            )
        )
    db.commit()
    db.refresh(ticket)
    return ticket


def seed_demo_tickets(db, *, admin: User, technician: User, user: User) -> None:
    _ = admin
    ensure_demo_ticket(
        db,
        user=user,
        technician=technician,
        title="VPN will not connect from home",
        category="VPN",
        description="User cannot connect to VPN from a Windows laptop. MFA prompt appears but the tunnel fails after approval.",
        status=TicketStatus.IN_PROGRESS,
        priority=TicketPriority.HIGH,
        routing_group="network",
        urgency_level="high",
        failure_count=2,
        internal_notes="Check VPN gateway health and MFA registration before asking the user to reinstall the client.",
        messages=[
            (MessageSender.USER, "hi vpn not working and I cannot access files", None),
            (
                MessageSender.ASSISTANT,
                "I found VPN guidance and need the device context first.",
                {"kb_titles": ["VPN cannot connect"], "structured_questions": [{"field": "device_os", "value": "windows"}]},
            ),
            (MessageSender.USER, "Windows laptop", {"structured_response": {"field": "device_os", "value": "windows", "label": "Windows laptop"}}),
            (MessageSender.USER, "Not resolved", {"feedback": "not_resolved"}),
        ],
    )
    ensure_demo_ticket(
        db,
        user=user,
        technician=technician,
        title="Outlook email not syncing",
        category="EMAIL",
        description="Outlook desktop client is stuck on syncing. Webmail still works, so the likely issue is local profile state.",
        status=TicketStatus.WAITING_FOR_USER,
        priority=TicketPriority.MEDIUM,
        routing_group="communication",
        urgency_level="medium",
        failure_count=1,
        internal_notes="Waiting for screenshot of the sync error.",
        messages=[
            (MessageSender.USER, "my office mail is stuck", None),
            (
                MessageSender.ASSISTANT,
                "Try webmail first, then restart Outlook and confirm whether the desktop client is the only affected app.",
                {"kb_titles": ["Email send or sync failures", "Outlook profile or calendar issue"]},
            ),
        ],
    )
    ensure_demo_ticket(
        db,
        user=user,
        technician=technician,
        title="Account locked after password attempts",
        category="PASSWORD",
        description="User was locked out after repeated password attempts and could not complete MFA.",
        status=TicketStatus.RESOLVED,
        priority=TicketPriority.HIGH,
        routing_group="access",
        urgency_level="high",
        failure_count=2,
        resolution_notes="Verified identity, unlocked account, and confirmed successful sign-in.",
        messages=[
            (MessageSender.USER, "password not taking since morning account locked", None),
            (
                MessageSender.ASSISTANT,
                "This looks like an account lockout. I will escalate with the details already collected.",
                {"kb_titles": ["Password reset and account unlock", "MFA prompt missing or authenticator unavailable"]},
            ),
        ],
    )
    ensure_demo_ticket(
        db,
        user=user,
        technician=None,
        title="Printer offline near finance area",
        category="PRINTER",
        description="Shared printer shows offline for one floor. Needs technician triage if multiple users are affected.",
        status=TicketStatus.ESCALATED,
        priority=TicketPriority.LOW,
        routing_group="endpoint",
        urgency_level="low",
        failure_count=2,
        messages=[
            (MessageSender.USER, "printer says offline", None),
            (
                MessageSender.ASSISTANT,
                "Check paper, toner, queue status, and whether other users can print to the same printer.",
                {"kb_titles": ["Printer offline or print queue stuck"]},
            ),
        ],
    )
    ensure_demo_ticket(
        db,
        user=user,
        technician=technician,
        title="Payroll portal access denied",
        category="ACCESS",
        description="User can sign in to SSO but payroll portal shows access denied. Business impact is payroll cutoff.",
        status=TicketStatus.ESCALATED,
        priority=TicketPriority.CRITICAL,
        routing_group="access",
        urgency_level="critical",
        failure_count=1,
        sla_breached=True,
        internal_notes="Confirm manager approval and group membership immediately.",
        messages=[
            (MessageSender.USER, "payroll access blocked and I cannot work", None),
            (
                MessageSender.ASSISTANT,
                "This is high impact, so I am escalating with your SSO and application context.",
                {"kb_titles": ["Access denied to company application"]},
            ),
        ],
    )


def main() -> None:
    db = SessionLocal()
    try:
        seed_knowledge_base(db)
        admin, technician, user = ensure_demo_users(db)
        seed_demo_tickets(db, admin=admin, technician=technician, user=user)
    finally:
        db.close()
    print("Demo seed completed: users, knowledge base, tickets, notifications, and analytics data are ready.")


if __name__ == "__main__":
    main()
