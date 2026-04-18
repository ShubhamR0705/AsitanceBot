from datetime import datetime, timedelta

from app.models.ticket import Ticket, TicketPriority, TicketStatus


class SupportOperationsService:
    SLA_HOURS = {
        TicketPriority.LOW: 72,
        TicketPriority.MEDIUM: 24,
        TicketPriority.HIGH: 8,
        TicketPriority.CRITICAL: 2,
    }

    ROUTING_GROUPS = {
        "VPN": "network",
        "WIFI": "network",
        "NETWORK": "network",
        "PASSWORD": "access",
        "ACCESS": "access",
        "EMAIL": "communication",
        "DEVICE_PERFORMANCE": "endpoint",
        "SOFTWARE": "endpoint",
        "BROWSER": "endpoint",
        "PRINTER": "endpoint",
    }

    def determine_priority(self, *, category: str, text: str, triage: dict | None = None) -> TicketPriority:
        lower = text.lower()
        urgency_level = (triage or {}).get("urgency_level")
        security_sensitive = bool((triage or {}).get("security_sensitive"))
        signals = " ".join(str(signal).lower() for signal in (triage or {}).get("urgency_signals", []) or [])
        combined = f"{lower} {signals}"

        if security_sensitive or urgency_level == "critical" or any(term in combined for term in ["security", "breach", "stolen", "malware", "ransomware"]):
            return TicketPriority.CRITICAL
        if urgency_level == "high" or any(term in combined for term in ["urgent", "cannot work", "can't work", "blocked", "payroll", "ceo", "production down"]):
            return TicketPriority.HIGH
        if urgency_level == "medium" or category in {"PASSWORD", "VPN"}:
            return TicketPriority.MEDIUM
        return TicketPriority.LOW

    def routing_group_for_category(self, category: str) -> str:
        return self.ROUTING_GROUPS.get(category, "general")

    def sla_due_at(self, priority: TicketPriority, created_at: datetime | None = None) -> datetime:
        started_at = created_at or datetime.utcnow()
        return started_at + timedelta(hours=self.SLA_HOURS[priority])

    def refresh_sla_state(self, ticket: Ticket, now: datetime | None = None) -> bool:
        if ticket.status in {TicketStatus.RESOLVED, TicketStatus.CLOSED}:
            return False
        if not ticket.sla_due_at:
            ticket.sla_due_at = self.sla_due_at(ticket.priority, ticket.created_at)
        ticket.sla_breached = ticket.sla_due_at < (now or datetime.utcnow())
        return ticket.sla_breached
