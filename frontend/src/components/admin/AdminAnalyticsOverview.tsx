import { motion } from "framer-motion";
import type { ComponentType, ReactNode } from "react";
import { AlertTriangle, MessageSquareMore, Ticket, Users } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import type { Analytics } from "../../types/api";

type AdminAnalyticsOverviewProps = {
  data?: Analytics;
};

const chartColors = ["#0f766e", "#2563eb", "#e11d48", "#ca8a04", "#16a34a", "#e64980"];
const statusColors: Record<string, string> = {
  Waiting: "#ca8a04",
  "In progress": "#2563eb",
  Escalated: "#e11d48"
};

export function AdminAnalyticsOverview({ data }: AdminAnalyticsOverviewProps) {
  const statusData = ticketStatusData(data);
  const categoryData = issueCategoryData(data);
  const systemData = systemMetricData(data);
  const workloadData = technicianWorkloadRows(data);
  const kbRows = kbPerformanceRows(data);
  const visibleStatusData = statusData.filter((item) => item.value > 0);

  return (
    <div className="space-y-6">
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard icon={Users} label="Total users" value={data?.total_users ?? 0} detail="People with platform access" tone="brand" />
        <MetricCard icon={Ticket} label="Total tickets" value={data?.total_tickets ?? 0} detail="All support cases" tone="info" />
        <MetricCard icon={MessageSquareMore} label="Active chats" value={data?.active_conversations ?? 0} detail="Conversations still open" tone="success" />
        <MetricCard icon={AlertTriangle} label="Escalations" value={data?.escalated_tickets ?? 0} detail={`${data?.pending_approvals ?? 0} approvals pending`} tone="warning" />
      </section>

      <section className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <ChartPanel title="Ticket status" description="Open work by current state">
          <div className="grid gap-4 lg:grid-cols-[1fr_0.9fr]">
            <div className="h-64">
              {visibleStatusData.length ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={visibleStatusData} dataKey="value" nameKey="name" innerRadius={58} outerRadius={88} paddingAngle={3}>
                      {visibleStatusData.map((entry) => (
                        <Cell key={entry.name} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip content={<ChartTooltip />} />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <EmptyChartState text="Ticket status appears after tickets are created." />
              )}
            </div>
            <LegendList rows={statusData} />
          </div>
        </ChartPanel>

        <ChartPanel title="Issue categories" description="Most common request types">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryData} margin={{ left: -18, right: 8, top: 8, bottom: 8 }}>
                <CartesianGrid stroke="#e5e7eb" vertical={false} />
                <XAxis dataKey="name" tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: "#64748b" }} />
                <YAxis allowDecimals={false} tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: "#64748b" }} />
                <Tooltip content={<ChartTooltip />} />
                <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                  {categoryData.map((entry, index) => (
                    <Cell key={entry.name} fill={chartColors[index % chartColors.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartPanel>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1fr_1fr]">
        <ChartPanel title="System metrics" description="Signals that show chatbot quality">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={systemData} layout="vertical" margin={{ left: 20, right: 24, top: 8, bottom: 8 }}>
                <CartesianGrid stroke="#e5e7eb" horizontal={false} />
                <XAxis type="number" allowDecimals={false} tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: "#64748b" }} />
                <YAxis dataKey="name" type="category" width={116} tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: "#475569" }} />
                <Tooltip content={<ChartTooltip />} />
                <Bar dataKey="value" radius={[0, 8, 8, 0]}>
                  {systemData.map((entry, index) => (
                    <Cell key={entry.name} fill={chartColors[(index + 2) % chartColors.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartPanel>

        <ChartPanel title="Technician workload" description="Open load by owner">
          <div className="space-y-4">
            {workloadData.length ? (
              workloadData.map((row) => <WorkloadBar key={row.name} row={row} max={Math.max(...workloadData.map((item) => item.total), 1)} />)
            ) : (
              <EmptyChartState text="Workload appears after tickets are assigned." />
            )}
          </div>
        </ChartPanel>
      </section>

      <ChartPanel title="Knowledge base performance" description="Which answers help, and which ones still escalate">
        {kbRows.length ? (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[680px] text-left text-sm">
              <thead className="text-xs uppercase text-muted">
                <tr>
                  <th className="py-3 pr-4 font-semibold">Article</th>
                  <th className="py-3 pr-4 font-semibold">Shown</th>
                  <th className="py-3 pr-4 font-semibold">Resolved</th>
                  <th className="py-3 pr-4 font-semibold">Escalated</th>
                  <th className="py-3 pr-4 font-semibold">Success</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {kbRows.map((row) => (
                  <tr key={row.title}>
                    <td className="max-w-[320px] py-4 pr-4 font-semibold text-ink">{row.title}</td>
                    <td className="py-4 pr-4 text-muted">{row.shown}</td>
                    <td className="py-4 pr-4 text-emerald-700">{row.resolved}</td>
                    <td className="py-4 pr-4 text-yellow-700">{row.escalated}</td>
                    <td className="py-4 pr-4">
                      <span className={successTone(row.successRate)}>{row.successRate}%</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyChartState text="KB outcomes appear after users rate or escalate suggested answers." />
        )}
      </ChartPanel>
    </div>
  );
}

function MetricCard({
  icon: Icon,
  label,
  value,
  detail,
  tone
}: {
  icon: ComponentType<{ className?: string }>;
  label: string;
  value: number;
  detail: string;
  tone: "brand" | "info" | "success" | "warning";
}) {
  const toneClass = {
    brand: "bg-brand-50 text-brand-700",
    info: "bg-blue-50 text-blue-700",
    success: "bg-emerald-50 text-emerald-700",
    warning: "bg-yellow-50 text-yellow-700"
  }[tone];

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} whileHover={{ y: -2 }} className="premium-panel p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-muted">{label}</p>
          <p className="mt-3 text-3xl font-semibold text-ink">{value.toLocaleString()}</p>
        </div>
        <div className={`rounded-lg p-3 ${toneClass}`}>
          <Icon className="h-5 w-5" />
        </div>
      </div>
      <p className="mt-3 text-sm text-muted">{detail}</p>
    </motion.div>
  );
}

function ChartPanel({ title, description, children }: { title: string; description: string; children: ReactNode }) {
  return (
    <motion.section initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.22 }} className="premium-panel p-5">
      <div className="mb-5 flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-ink">{title}</h2>
          <p className="mt-1 text-sm text-muted">{description}</p>
        </div>
      </div>
      {children}
    </motion.section>
  );
}

function LegendList({ rows }: { rows: Array<{ name: string; value: number; color?: string }> }) {
  return (
    <div className="space-y-3 self-center">
      {rows.map((row, index) => (
        <div key={row.name} className="flex items-center justify-between gap-3 rounded-lg border border-line bg-elevated px-3 py-2">
          <div className="flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: row.color ?? chartColors[index % chartColors.length] }} />
            <span className="text-sm font-medium text-ink">{row.name}</span>
          </div>
          <span className="text-sm text-muted">{row.value}</span>
        </div>
      ))}
    </div>
  );
}

function WorkloadBar({ row, max }: { row: { name: string; open: number; resolved: number; total: number }; max: number }) {
  return (
    <div className="rounded-lg border border-line bg-elevated p-4">
      <div className="flex items-center justify-between gap-3">
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold text-ink">{row.name}</p>
          <p className="mt-1 text-xs text-muted">{row.open} open, {row.resolved} resolved</p>
        </div>
        <span className="text-sm font-semibold text-ink">{row.total}</span>
      </div>
      <div className="mt-3 h-2 overflow-hidden rounded-lg bg-line">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${Math.max(6, (row.total / max) * 100)}%` }}
          transition={{ duration: 0.45 }}
          className="h-full rounded-lg bg-brand-600"
        />
      </div>
    </div>
  );
}

function ChartTooltip({ active, payload, label }: { active?: boolean; payload?: Array<{ value?: number; name?: string; payload?: { name?: string } }>; label?: string }) {
  if (!active || !payload?.length) return null;
  const item = payload[0];
  return (
    <div className="rounded-lg border border-line bg-surface px-3 py-2 shadow-soft">
      <p className="text-xs font-semibold text-ink">{item.payload?.name ?? item.name ?? label}</p>
      <p className="mt-1 text-xs text-muted">{Number(item.value ?? 0).toLocaleString()}</p>
    </div>
  );
}

function EmptyChartState({ text }: { text: string }) {
  return (
    <div className="flex min-h-48 items-center justify-center rounded-lg border border-dashed border-line bg-elevated p-6 text-center text-sm text-muted">
      {text}
    </div>
  );
}

function ticketStatusData(data?: Analytics) {
  const breakdown = data?.status_breakdown ?? {};
  return [
    { name: "Waiting", value: breakdown.WAITING_FOR_USER ?? 0, color: statusColors.Waiting },
    { name: "In progress", value: breakdown.IN_PROGRESS ?? 0, color: statusColors["In progress"] },
    { name: "Escalated", value: breakdown.ESCALATED ?? 0, color: statusColors.Escalated }
  ];
}

function issueCategoryData(data?: Analytics) {
  const breakdown = data?.category_breakdown ?? {};
  return ["VPN", "WIFI", "PASSWORD", "ACCESS"]
    .map((name) => ({ name, value: breakdown[name] ?? 0 }))
    .filter((item) => item.value > 0 || ["VPN", "WIFI", "PASSWORD", "ACCESS"].includes(item.name));
}

function systemMetricData(data?: Analytics) {
  return [
    { name: "Clarifications", value: data?.clarification_requested ?? 0 },
    { name: "Helpful replies", value: data?.message_feedback?.helpful ?? 0 },
    { name: "KB failure %", value: Math.round((data?.kb_failure_rate ?? 0) * 100) },
    { name: "Pending approvals", value: data?.pending_approvals ?? 0 }
  ];
}

function technicianWorkloadRows(data?: Analytics) {
  return Object.entries(data?.technician_workload_detail ?? {})
    .map(([name, item]) => ({ name, ...item }))
    .sort((a, b) => b.open - a.open || b.total - a.total)
    .slice(0, 8);
}

function kbPerformanceRows(data?: Analytics) {
  return Object.entries(data?.kb_article_outcomes ?? {})
    .map(([title, item]) => ({
      title,
      ...item,
      successRate: item.shown ? Math.round((item.resolved / item.shown) * 100) : 0
    }))
    .sort((a, b) => b.shown - a.shown || b.successRate - a.successRate)
    .slice(0, 8);
}

function successTone(value: number) {
  if (value >= 70) return "rounded-lg bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700";
  if (value >= 35) return "rounded-lg bg-yellow-50 px-2.5 py-1 text-xs font-semibold text-yellow-700";
  return "rounded-lg bg-red-50 px-2.5 py-1 text-xs font-semibold text-red-700";
}
