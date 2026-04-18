import re
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.audit_log import AuditAction
from app.models.conversation import Conversation
from app.models.ticket import Ticket, TicketApprovalStatus, TicketRequestType, TicketStatus
from app.models.user import User
from app.repositories.ticket_repository import TicketRepository
from app.services.assignment_service import AssignmentService
from app.services.audit_service import AuditService
from app.services.notification_service import NotificationService
from app.services.support_operations_service import SupportOperationsService


@dataclass(frozen=True)
class SoftwareInstallDetails:
    requested_software: str
    request_reason: str
    request_device: str | None


class ApprovalWorkflowService:
    INSTALL_INTENT_PATTERNS = [
        r"\bcan you install\b",
        r"\bneed .{0,40} installed\b",
        r"\bneed to install\b",
        r"\brequest .{0,30} install\b",
        r"\bapproval .{0,40} install\b",
        r"\badmin rights .{0,40} install\b",
        r"\binstall software\b",
    ]
    NON_APPROVAL_PATTERNS = [
        r"\binstall(?:ation)? failed\b",
        r"\bapp install failed\b",
        r"\bsoftware update failed\b",
    ]
    KNOWN_SOFTWARE = [
        "photoshop",
        "vs code",
        "visual studio code",
        "chrome",
        "firefox",
        "zoom",
        "teams",
        "slack",
        "vpn client",
        "intellij",
        "pycharm",
        "postman",
        "docker",
    ]

    def __init__(self, db: Session):
        self.db = db
        self.tickets = TicketRepository(db)
        self.assignment = AssignmentService(db)
        self.audit = AuditService(db)
        self.notifications = NotificationService(db)
        self.operations = SupportOperationsService()

    def is_software_install_request(self, text: str, context: dict | None = None) -> bool:
        lower = text.lower()
        if any(re.search(pattern, lower) for pattern in self.NON_APPROVAL_PATTERNS):
            return False
        if any(re.search(pattern, lower) for pattern in self.INSTALL_INTENT_PATTERNS):
            return True
        if any(term in lower for term in ["approval", "approve", "approved"]) and any(software in lower for software in self.KNOWN_SOFTWARE):
            return True
        if "approval" in lower and any(word in lower for word in ["software", "app", "tool", "license", "install"]):
            return True
        return False

    def create_install_request(
        self,
        *,
        user: User,
        conversation: Conversation,
        text: str,
        context: dict | None = None,
        triage: dict | None = None,
    ) -> Ticket:
        existing = self.tickets.get_by_conversation_id(conversation.id)
        if existing:
            return existing

        details = self.extract_details(text, context or {})
        priority = self.operations.determine_priority(category="SOFTWARE", text=text, triage=triage)
        ticket = self.tickets.create(
            conversation_id=conversation.id,
            user_id=user.id,
            category="SOFTWARE",
            title=f"Software Install: {details.requested_software}"[:180],
            description=self._description(details, text),
            status=TicketStatus.OPEN,
            priority=priority,
            routing_group=self.operations.routing_group_for_category("SOFTWARE"),
            sla_due_at=self.operations.sla_due_at(priority),
            request_type=TicketRequestType.SOFTWARE_INSTALL,
            requested_software=details.requested_software,
            request_reason=details.request_reason,
            request_device=details.request_device,
            approval_required=True,
            approval_status=TicketApprovalStatus.PENDING_APPROVAL,
        )
        ticket = self.assignment.auto_assign(ticket)
        self.audit.record(
            action=AuditAction.TICKET_CREATED,
            ticket_id=ticket.id,
            actor=user,
            new_value={"request_type": ticket.request_type.value, "approval_status": ticket.approval_status.value},
            summary="Software installation request ticket created.",
        )
        self.audit.record(
            action=AuditAction.APPROVAL_REQUESTED,
            ticket_id=ticket.id,
            actor=user,
            new_value={"requested_software": details.requested_software},
            summary="Software installation approval requested.",
        )
        if ticket.technician_id:
            self.audit.record(
                action=AuditAction.TICKET_ASSIGNED,
                ticket_id=ticket.id,
                actor=user,
                previous_value={"technician_id": None},
                new_value={"technician_id": ticket.technician_id, "assignment_source": ticket.assignment_source},
                summary="Software installation request auto-assigned.",
            )
        self._notify_request_created(ticket, user)
        return ticket

    def extract_details(self, text: str, context: dict) -> SoftwareInstallDetails:
        requested_software = self._extract_software(text)
        reason = self._extract_reason(text) or text.strip()
        device = context.get("device_os") or context.get("device_type") or context.get("request_device")
        return SoftwareInstallDetails(
            requested_software=requested_software or "Software not specified",
            request_reason=reason[:1000],
            request_device=str(device)[:160] if device else None,
        )

    def _extract_software(self, text: str) -> str | None:
        lower = text.lower()
        for software in self.KNOWN_SOFTWARE:
            if software in lower:
                return software.title() if software != "vs code" else "VS Code"
        patterns = [
            r"(?:install|installed)\s+([a-zA-Z0-9 .+#-]{2,60})(?:\s+for|\s+on|$)",
            r"need\s+([a-zA-Z0-9 .+#-]{2,60})\s+installed",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                value = re.sub(r"\b(the|a|an|software|app|application)\b", "", match.group(1), flags=re.IGNORECASE).strip(" .-")
                if value:
                    return value[:180]
        return None

    def _extract_reason(self, text: str) -> str | None:
        match = re.search(r"\bfor\s+(.{4,220})", text, flags=re.IGNORECASE)
        return match.group(1).strip() if match else None

    def _description(self, details: SoftwareInstallDetails, original_text: str) -> str:
        return (
            "Software installation approval request.\n\n"
            f"Requested software: {details.requested_software}\n"
            f"Business reason: {details.request_reason or 'Not provided'}\n"
            f"Device/system: {details.request_device or 'Not provided'}\n\n"
            f"Original request: {original_text}"
        )

    def _notify_request_created(self, ticket: Ticket, user: User) -> None:
        self.notifications.notify(
            recipient=user,
            actor=user,
            ticket=ticket,
            title=f"Software request #{ticket.id} created",
            body="Your software installation request is pending admin approval.",
        )
        self.notifications.notify_admins(
            actor=user,
            ticket=ticket,
            title=f"Approval needed for ticket #{ticket.id}",
            body=f"{user.full_name} requested {ticket.requested_software}. Review and approve or reject it.",
        )
        if ticket.technician:
            self.notifications.notify(
                recipient=ticket.technician,
                actor=user,
                ticket=ticket,
                title=f"Ticket #{ticket.id} assigned pending approval",
                body="This software installation request is assigned to you but requires admin approval before work starts.",
                email=False,
            )
