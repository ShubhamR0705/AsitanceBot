import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { Bot, CheckCircle2, Clock3, Ticket } from "lucide-react";
import { chatApi, ticketsApi } from "../../api/client";
import { EmptyState } from "../../components/ui/EmptyState";
import { LinkButton } from "../../components/ui/LinkButton";
import { PageTransition } from "../../components/ui/PageTransition";
import { StatCard } from "../../components/ui/StatCard";
import { StatusBadge } from "../../components/ui/StatusBadge";

export function UserDashboardPage() {
  const tickets = useQuery({ queryKey: ["my-tickets"], queryFn: ticketsApi.mine });
  const conversations = useQuery({ queryKey: ["my-conversations"], queryFn: chatApi.listConversations });

  const ticketData = tickets.data ?? [];
  const activeTickets = ticketData.filter((ticket) => !["RESOLVED", "CLOSED"].includes(ticket.status)).length;
  const resolvedTickets = ticketData.filter((ticket) => ticket.status === "RESOLVED").length;

  return (
    <PageTransition>
      <div className="space-y-6">
        <section className="grid gap-4 md:grid-cols-3">
          <StatCard label="Active tickets" value={activeTickets} detail="Open, escalated, or in progress" />
          <StatCard label="Resolved tickets" value={resolvedTickets} detail="Closed through AI or technician help" />
          <StatCard label="Chat sessions" value={conversations.data?.length ?? 0} detail="Your saved support history" />
        </section>

        <section className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="rounded-lg border border-line bg-surface p-6 shadow-soft">
            <div className="mb-5 flex items-center justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-ink">Start with AI support</h2>
                <p className="mt-1 text-sm text-muted">
                  Describe what is not working. AssistIQ will guide you through the next step and bring in support when needed.
                </p>
              </div>
              <Bot className="h-8 w-8 text-brand-600" />
            </div>
            <div className="grid gap-3 sm:grid-cols-3">
              {[
                { icon: Bot, title: "Tell us the issue", text: "Use everyday language and include the app, device, or error if you have it." },
                { icon: CheckCircle2, title: "Try guided steps", text: "Follow approved fixes one step at a time." },
                { icon: Ticket, title: "Get support handoff", text: "If it is still not solved, a technician gets the details already collected." }
              ].map((item) => (
                <div key={item.title} className="rounded-lg border border-line bg-elevated p-4">
                  <item.icon className="h-5 w-5 text-brand-700" />
                  <p className="mt-3 text-sm font-semibold text-ink">{item.title}</p>
                  <p className="mt-1 text-xs leading-5 text-muted">{item.text}</p>
                </div>
              ))}
            </div>
            <LinkButton to="/user/chat" className="mt-6">Open support chat</LinkButton>
          </div>

          <div className="rounded-lg border border-line bg-surface p-6 shadow-soft">
            <div className="mb-5 flex items-center gap-3">
              <Clock3 className="h-5 w-5 text-brand-700" />
              <h2 className="text-lg font-semibold text-ink">Recent tickets</h2>
            </div>
            {ticketData.length ? (
              <div className="space-y-3">
                {ticketData.slice(0, 4).map((ticket) => (
                  <Link key={ticket.id} to={`/user/tickets/${ticket.id}`} className="block rounded-lg border border-line bg-elevated p-3 transition hover:border-brand-500/50">
                    <div className="flex items-center justify-between gap-3">
                      <p className="truncate text-sm font-semibold text-ink">#{ticket.id} {ticket.title}</p>
                      <StatusBadge status={ticket.status} />
                    </div>
                    <p className="mt-2 text-xs text-muted">{new Date(ticket.updated_at).toLocaleString()}</p>
                  </Link>
                ))}
              </div>
            ) : (
              <EmptyState title="No tickets yet" description="Tickets appear here after the AI escalates an unresolved issue." />
            )}
          </div>
        </section>
      </div>
    </PageTransition>
  );
}
