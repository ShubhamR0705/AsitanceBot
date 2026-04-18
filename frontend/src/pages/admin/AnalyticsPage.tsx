import { useQuery } from "@tanstack/react-query";
import { adminApi } from "../../api/client";
import { PageTransition } from "../../components/ui/PageTransition";
import { Skeleton } from "../../components/ui/Skeleton";
import { StatCard } from "../../components/ui/StatCard";

export function AnalyticsPage() {
  const analytics = useQuery({ queryKey: ["admin-analytics"], queryFn: adminApi.analytics });

  if (analytics.isLoading) {
    return (
      <PageTransition>
        <Skeleton className="h-96" />
      </PageTransition>
    );
  }

  const data = analytics.data;

  return (
    <PageTransition>
      <div className="space-y-6">
        <section className="grid gap-4 md:grid-cols-3">
          <StatCard label="Total users" value={data?.total_users ?? 0} />
          <StatCard label="Total tickets" value={data?.total_tickets ?? 0} />
          <StatCard label="Active chats" value={data?.active_conversations ?? 0} />
          <StatCard label="Low confidence" value={data?.low_confidence_conversations ?? 0} />
          <StatCard label="Clarifications" value={data?.clarification_requested ?? 0} />
          <StatCard label="Escalated" value={data?.escalated_tickets ?? 0} />
          <StatCard label="Avg resolution hrs" value={data?.avg_resolution_hours ?? 0} />
          <StatCard label="KB failure rate" value={Math.round((data?.kb_failure_rate ?? 0) * 100)} detail="Percent escalated after KB" />
          <StatCard label="Helpful replies" value={data?.message_feedback?.helpful ?? 0} />
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          <Breakdown title="Ticket status" values={data?.status_breakdown ?? {}} />
          <Breakdown title="Issue categories" values={data?.category_breakdown ?? {}} />
          <Breakdown title="Conversation stage" values={data?.stage_breakdown ?? {}} />
          <Breakdown title="Urgency signals" values={data?.urgency_breakdown ?? {}} />
          <Breakdown title="Escalation reasons" values={data?.escalation_reason_breakdown ?? {}} />
          <Breakdown title="Technician workload" values={data?.technician_workload ?? {}} />
          <TechnicianWorkload values={data?.technician_workload_detail ?? {}} />
          <Breakdown title="Message feedback" values={data?.message_feedback ?? {}} />
          <Breakdown title="KB article usage" values={data?.kb_article_usage ?? {}} />
          <KbOutcomeTable values={data?.kb_article_outcomes ?? {}} />
        </section>
      </div>
    </PageTransition>
  );
}

function TechnicianWorkload({ values }: { values: Record<string, { open: number; resolved: number; total: number }> }) {
  const rows = Object.entries(values);
  return (
    <div className="rounded-lg border border-line bg-surface p-6 shadow-soft">
      <h2 className="text-lg font-semibold text-ink">Workload detail</h2>
      <div className="mt-5 space-y-3">
        {rows.length ? (
          rows.map(([name, item]) => (
            <div key={name} className="rounded-lg border border-line bg-elevated p-4">
              <div className="flex items-center justify-between gap-3">
                <span className="text-sm font-semibold text-ink">{name}</span>
                <span className="text-xs text-muted">{item.total} total</span>
              </div>
              <p className="mt-2 text-sm text-muted">{item.open} open · {item.resolved} resolved</p>
            </div>
          ))
        ) : (
          <p className="rounded-lg border border-dashed border-line bg-elevated p-6 text-center text-sm text-muted">No workload yet.</p>
        )}
      </div>
    </div>
  );
}

function Breakdown({ title, values }: { title: string; values: Record<string, number> }) {
  const max = Math.max(1, ...Object.values(values));
  return (
    <div className="rounded-lg border border-line bg-surface p-6 shadow-soft">
      <h2 className="text-lg font-semibold text-ink">{title}</h2>
      <div className="mt-5 space-y-4">
        {Object.entries(values).length ? (
          Object.entries(values).map(([label, value]) => (
            <div key={label}>
              <div className="mb-2 flex items-center justify-between text-sm">
                <span className="font-medium text-ink">{label.replaceAll("_", " ")}</span>
                <span className="text-muted">{value}</span>
              </div>
              <div className="h-2 overflow-hidden rounded-lg bg-line">
                <div className="h-full rounded-lg bg-brand-600 transition-all" style={{ width: `${(value / max) * 100}%` }} />
              </div>
            </div>
          ))
        ) : (
          <p className="rounded-lg border border-dashed border-line bg-elevated p-6 text-center text-sm text-muted">No data yet.</p>
        )}
      </div>
    </div>
  );
}

function KbOutcomeTable({
  values,
}: {
  values: Record<string, { shown: number; resolved: number; escalated: number; unresolved_feedback: number }>;
}) {
  const rows = Object.entries(values);
  return (
    <div className="rounded-lg border border-line bg-surface p-6 shadow-soft">
      <h2 className="text-lg font-semibold text-ink">KB outcomes</h2>
      <div className="mt-5 overflow-x-auto">
        {rows.length ? (
          <table className="w-full min-w-[520px] text-left text-sm">
            <thead className="text-xs uppercase tracking-wide text-muted">
              <tr>
                <th className="py-3 pr-4 font-semibold">Article</th>
                <th className="py-3 pr-4 font-semibold">Shown</th>
                <th className="py-3 pr-4 font-semibold">Resolved</th>
                <th className="py-3 pr-4 font-semibold">Escalated</th>
                <th className="py-3 font-semibold">Unresolved</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {rows.map(([title, outcome]) => (
                <tr key={title}>
                  <td className="max-w-[260px] py-3 pr-4 font-medium text-ink">{title}</td>
                  <td className="py-3 pr-4 text-muted">{outcome.shown}</td>
                  <td className="py-3 pr-4 text-emerald-700">{outcome.resolved}</td>
                  <td className="py-3 pr-4 text-yellow-700">{outcome.escalated}</td>
                  <td className="py-3 text-muted">{outcome.unresolved_feedback}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="rounded-lg border border-dashed border-line bg-elevated p-6 text-center text-sm text-muted">No KB outcomes yet.</p>
        )}
      </div>
    </div>
  );
}
