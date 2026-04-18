import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { LifeBuoy, Timer, Wrench } from "lucide-react";
import { ticketsApi } from "../../api/client";
import { PageTransition } from "../../components/ui/PageTransition";
import { StatCard } from "../../components/ui/StatCard";
import { StatusBadge } from "../../components/ui/StatusBadge";

export function TechnicianDashboardPage() {
  const queue = useQuery({ queryKey: ["ticket-queue"], queryFn: ticketsApi.queue });
  const tickets = queue.data ?? [];
  const escalated = tickets.filter((ticket) => ticket.status === "ESCALATED").length;
  const inProgress = tickets.filter((ticket) => ticket.status === "IN_PROGRESS").length;

  return (
    <PageTransition>
      <div className="space-y-6">
        <section className="grid gap-4 md:grid-cols-3">
          <StatCard label="Queue" value={tickets.length} detail="Open support workload" />
          <StatCard label="Escalated" value={escalated} detail="AI handoffs ready for review" />
          <StatCard label="In progress" value={inProgress} detail="Tickets currently being handled" />
        </section>

        <section className="grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
          <div className="rounded-lg border border-line bg-surface p-6 shadow-soft">
            <Wrench className="h-7 w-7 text-brand-700" />
            <h2 className="mt-4 text-lg font-semibold text-ink">Support workflow</h2>
            <p className="mt-2 text-sm leading-6 text-muted">
              Review the AI attempts before taking over. Update status clearly so users and admins can track progress.
            </p>
            <div className="mt-5 space-y-3 text-sm text-muted">
              <p className="rounded-lg border border-line bg-elevated p-3">1. Open escalated ticket</p>
              <p className="rounded-lg border border-line bg-elevated p-3">2. Read conversation history</p>
              <p className="rounded-lg border border-line bg-elevated p-3">3. Add notes and resolution</p>
            </div>
          </div>

          <div className="rounded-lg border border-line bg-surface p-6 shadow-soft">
            <div className="mb-5 flex items-center gap-3">
              <LifeBuoy className="h-5 w-5 text-brand-700" />
              <h2 className="text-lg font-semibold text-ink">Newest escalations</h2>
            </div>
            <div className="space-y-3">
              {tickets.slice(0, 5).map((ticket) => (
                <Link key={ticket.id} to={`/technician/tickets/${ticket.id}`} className="block rounded-lg border border-line bg-elevated p-4 transition hover:border-brand-500/50">
                  <div className="flex items-start justify-between gap-4">
                    <div className="min-w-0">
                      <p className="truncate text-sm font-semibold text-ink">#{ticket.id} {ticket.title}</p>
                      <p className="mt-1 flex items-center gap-2 text-xs text-muted">
                        <Timer className="h-3.5 w-3.5" />
                        {new Date(ticket.created_at).toLocaleString()}
                      </p>
                    </div>
                    <StatusBadge status={ticket.status} />
                  </div>
                </Link>
              ))}
              {!tickets.length ? <p className="rounded-lg border border-dashed border-line bg-elevated p-6 text-center text-sm text-muted">The queue is clear.</p> : null}
            </div>
          </div>
        </section>
      </div>
    </PageTransition>
  );
}

