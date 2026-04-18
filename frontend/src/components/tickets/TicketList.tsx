import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { cn } from "../../lib/cn";
import type { Ticket } from "../../types/api";
import { PriorityBadge } from "../ui/PriorityBadge";
import { StatusBadge } from "../ui/StatusBadge";

interface TicketListProps {
  tickets: Ticket[];
  detailBasePath: string;
}

export function TicketList({ tickets, detailBasePath }: TicketListProps) {
  return (
    <div className="overflow-hidden rounded-lg border border-line bg-surface shadow-soft">
      <div className="grid grid-cols-12 border-b border-line bg-elevated px-4 py-3 text-xs font-semibold uppercase text-muted">
        <span className="col-span-6 md:col-span-5">Ticket</span>
        <span className="hidden md:col-span-2 md:block">Routing</span>
        <span className="col-span-3 md:col-span-2">Status</span>
        <span className="col-span-3 text-right md:col-span-3">Updated</span>
      </div>
      {tickets.map((ticket, index) => (
        <motion.div
          key={ticket.id}
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.18, delay: index * 0.03 }}
        >
          <Link
            to={`${detailBasePath}/${ticket.id}`}
            className={cn(
              "grid grid-cols-12 items-center gap-2 border-b border-line px-4 py-4 transition last:border-b-0 hover:bg-brand-50/60",
              ticket.status === "ESCALATED" && "bg-yellow-50/40",
              ticket.sla_breached && "bg-red-50/50"
            )}
          >
            <div className="col-span-6 min-w-0 md:col-span-5">
              <p className="truncate text-sm font-semibold text-ink">#{ticket.id} {ticket.title}</p>
              <p className="mt-1 truncate text-xs text-muted">
                {ticket.user?.email ?? "Your request"} · {ticket.sla_due_at ? `SLA ${new Date(ticket.sla_due_at).toLocaleString()}` : "No SLA"}
              </p>
            </div>
            <div className="hidden text-sm text-muted md:col-span-2 md:block">
              <div>{ticket.routing_group.replaceAll("_", " ")}</div>
              <div className="mt-1"><PriorityBadge priority={ticket.priority} /></div>
            </div>
            <div className="col-span-3 md:col-span-2">
              <StatusBadge status={ticket.status} />
            </div>
            <div className="col-span-3 text-right text-xs text-muted md:col-span-3">{new Date(ticket.updated_at).toLocaleString()}</div>
          </Link>
        </motion.div>
      ))}
    </div>
  );
}
