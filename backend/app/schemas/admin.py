from pydantic import BaseModel


class AnalyticsResponse(BaseModel):
    total_users: int
    total_tickets: int
    open_tickets: int
    escalated_tickets: int
    resolved_tickets: int
    assigned_tickets: int
    unassigned_tickets: int
    pending_approvals: int
    active_conversations: int
    avg_resolution_hours: float | None
    kb_failure_rate: float
    low_confidence_conversations: int
    clarification_requested: int
    status_breakdown: dict[str, int]
    category_breakdown: dict[str, int]
    approval_breakdown: dict[str, int]
    stage_breakdown: dict[str, int]
    urgency_breakdown: dict[str, int]
    escalation_reason_breakdown: dict[str, int]
    kb_article_usage: dict[str, int]
    kb_article_outcomes: dict[str, dict[str, int]]
    technician_workload: dict[str, int]
    technician_workload_detail: dict[str, dict[str, int]]
    message_feedback: dict[str, int]
