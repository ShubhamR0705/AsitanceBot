import type { ReactNode } from "react";
import { Badge } from "../ui/Badge";
import { PriorityBadge } from "../ui/PriorityBadge";
import type { Ticket } from "../../types/api";

export function TicketOperationalPanel({ ticket }: { ticket: Ticket }) {
  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      <Metric label="Priority" value={<PriorityBadge priority={ticket.priority} />} />
      <Metric label="Routing" value={ticket.routing_group.replaceAll("_", " ")} />
      <Metric label="Assignee" value={ticket.technician?.email ?? "Unassigned"} />
      <Metric label="SLA" value={ticket.sla_breached ? <Badge tone="error">Breached</Badge> : ticket.sla_due_at ? new Date(ticket.sla_due_at).toLocaleString() : "Not set"} />
    </div>
  );
}

function Metric({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="rounded-lg border border-line bg-elevated p-4">
      <p className="text-xs font-semibold uppercase text-muted">{label}</p>
      <div className="mt-2 text-sm font-semibold text-ink">{value}</div>
    </div>
  );
}

export function AuditTimeline({ ticket }: { ticket: Ticket }) {
  return (
    <div className="rounded-lg border border-line bg-surface shadow-soft">
      <div className="border-b border-line px-5 py-4">
        <h3 className="text-lg font-semibold text-ink">Audit timeline</h3>
      </div>
      <div className="space-y-3 p-5">
        {ticket.audit_logs?.length ? (
          ticket.audit_logs.map((entry) => (
            <div key={entry.id} className="rounded-lg border border-line bg-elevated p-4">
              <div className="flex items-center justify-between gap-3">
                <Badge tone="neutral">{entry.action_type.replaceAll("_", " ")}</Badge>
                <span className="text-xs text-muted">{new Date(entry.created_at).toLocaleString()}</span>
              </div>
              <p className="mt-2 text-sm text-ink">{entry.summary}</p>
            </div>
          ))
        ) : (
          <p className="rounded-lg border border-dashed border-line bg-elevated p-6 text-center text-sm text-muted">No audit events yet.</p>
        )}
      </div>
    </div>
  );
}
