import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Search } from "lucide-react";
import { ticketsApi } from "../../api/client";
import { TicketList } from "../../components/tickets/TicketList";
import { EmptyState } from "../../components/ui/EmptyState";
import { Input } from "../../components/ui/Input";
import { PageTransition } from "../../components/ui/PageTransition";
import { Skeleton } from "../../components/ui/Skeleton";
import type { TicketStatus } from "../../types/api";

const statuses: Array<"ALL" | TicketStatus> = ["ALL", "OPEN", "ESCALATED", "IN_PROGRESS", "WAITING_FOR_USER", "RESOLVED", "CLOSED"];

export function TicketOverviewPage() {
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<"ALL" | TicketStatus>("ALL");
  const tickets = useQuery({ queryKey: ["all-tickets"], queryFn: ticketsApi.all });

  const filtered = useMemo(() => {
    const term = query.toLowerCase();
    return (tickets.data ?? []).filter((ticket) => {
      const matchesStatus = status === "ALL" || ticket.status === status;
      const matchesQuery = [ticket.title, ticket.category, ticket.user?.email ?? "", ticket.technician?.email ?? ""].join(" ").toLowerCase().includes(term);
      return matchesStatus && matchesQuery;
    });
  }, [query, status, tickets.data]);

  return (
    <PageTransition>
      <div className="space-y-5">
        <div>
          <h2 className="text-2xl font-semibold text-ink">All tickets</h2>
          <p className="mt-2 text-sm text-muted">Platform-wide support visibility.</p>
        </div>
        <div className="flex flex-col gap-3 rounded-lg border border-line bg-surface p-4 shadow-soft md:flex-row">
          <label className="relative flex-1">
            <Search className="pointer-events-none absolute left-3 top-3.5 h-4 w-4 text-muted" />
            <Input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search title, user, technician, category" className="pl-9" />
          </label>
          <select
            value={status}
            onChange={(event) => setStatus(event.target.value as "ALL" | TicketStatus)}
            className="h-11 rounded-lg border border-line bg-white px-3 text-sm text-ink shadow-sm focus:focus-ring"
          >
            {statuses.map((item) => (
              <option key={item} value={item}>
                {item.replaceAll("_", " ")}
              </option>
            ))}
          </select>
        </div>
        {tickets.isLoading ? (
          <Skeleton className="h-96" />
        ) : filtered.length ? (
          <TicketList tickets={filtered} detailBasePath="/admin/tickets" />
        ) : (
          <EmptyState title="No tickets" description="Ticket activity appears here after escalations." />
        )}
      </div>
    </PageTransition>
  );
}

