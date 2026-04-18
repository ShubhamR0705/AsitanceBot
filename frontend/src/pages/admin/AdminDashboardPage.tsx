import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { AlertTriangle, BookOpen, Users } from "lucide-react";
import { adminApi, ticketsApi } from "../../api/client";
import { PageTransition } from "../../components/ui/PageTransition";
import { StatCard } from "../../components/ui/StatCard";
import { StatusBadge } from "../../components/ui/StatusBadge";

export function AdminDashboardPage() {
  const analytics = useQuery({ queryKey: ["admin-analytics"], queryFn: adminApi.analytics });
  const tickets = useQuery({ queryKey: ["all-tickets"], queryFn: ticketsApi.all });

  return (
    <PageTransition>
      <div className="space-y-6">
        <section className="grid gap-4 md:grid-cols-4">
          <StatCard label="Users" value={analytics.data?.total_users ?? 0} detail="All active roles" />
          <StatCard label="Tickets" value={analytics.data?.total_tickets ?? 0} detail="Total created" />
          <StatCard label="Escalated" value={analytics.data?.escalated_tickets ?? 0} detail="Waiting for support" />
          <StatCard label="Resolved" value={analytics.data?.resolved_tickets ?? 0} detail="Marked solved" />
        </section>

        <section className="grid gap-6 lg:grid-cols-[1fr_1fr]">
          <div className="rounded-lg border border-line bg-surface p-6 shadow-soft">
            <div className="mb-5 flex items-center gap-3">
              <AlertTriangle className="h-5 w-5 text-yellow-700" />
              <h2 className="text-lg font-semibold text-ink">Operational attention</h2>
            </div>
            <div className="space-y-3">
              {(tickets.data ?? []).filter((ticket) => ticket.status === "ESCALATED").slice(0, 5).map((ticket) => (
                <Link key={ticket.id} to={`/admin/tickets/${ticket.id}`} className="block rounded-lg border border-line bg-elevated p-4 transition hover:border-brand-500/50">
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <p className="truncate text-sm font-semibold text-ink">#{ticket.id} {ticket.title}</p>
                      <p className="mt-1 text-xs text-muted">{ticket.user?.email}</p>
                    </div>
                    <StatusBadge status={ticket.status} />
                  </div>
                </Link>
              ))}
              {!tickets.data?.some((ticket) => ticket.status === "ESCALATED") ? (
                <p className="rounded-lg border border-dashed border-line bg-elevated p-6 text-center text-sm text-muted">No escalations need attention.</p>
              ) : null}
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <Link to="/admin/users" className="rounded-lg border border-line bg-surface p-6 shadow-soft transition hover:border-brand-500/50">
              <Users className="h-6 w-6 text-brand-700" />
              <h3 className="mt-4 text-base font-semibold text-ink">Manage users</h3>
              <p className="mt-2 text-sm leading-6 text-muted">Promote technicians and admins.</p>
            </Link>
            <Link to="/admin/knowledge-base" className="rounded-lg border border-line bg-surface p-6 shadow-soft transition hover:border-brand-500/50">
              <BookOpen className="h-6 w-6 text-accent-600" />
              <h3 className="mt-4 text-base font-semibold text-ink">Knowledge base</h3>
              <p className="mt-2 text-sm leading-6 text-muted">Maintain approved troubleshooting content.</p>
            </Link>
          </div>
        </section>
      </div>
    </PageTransition>
  );
}

