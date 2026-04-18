import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FormEvent, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { ticketsApi } from "../../api/client";
import { ChatBubble } from "../../components/chat/ChatBubble";
import { AuditTimeline, TicketOperationalPanel } from "../../components/tickets/TicketOperationalPanel";
import { Button } from "../../components/ui/Button";
import { LinkButton } from "../../components/ui/LinkButton";
import { PageTransition } from "../../components/ui/PageTransition";
import { Skeleton } from "../../components/ui/Skeleton";
import { StatusBadge } from "../../components/ui/StatusBadge";
import { Textarea } from "../../components/ui/Input";
import { useAuth } from "../../contexts/AuthContext";
import type { TicketPriority, TicketStatus } from "../../types/api";

const technicianStatuses: TicketStatus[] = ["IN_PROGRESS", "WAITING_FOR_USER", "RESOLVED", "CLOSED"];
const priorities: TicketPriority[] = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];

export function TechnicianTicketDetailPage() {
  const { ticketId } = useParams();
  const id = Number(ticketId);
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const ticket = useQuery({ queryKey: ["ticket", id], queryFn: () => ticketsApi.detail(id), enabled: Number.isFinite(id) });
  const [status, setStatus] = useState<TicketStatus>("IN_PROGRESS");
  const [priority, setPriority] = useState<TicketPriority>("MEDIUM");
  const [internalNotes, setInternalNotes] = useState("");
  const [resolutionNotes, setResolutionNotes] = useState("");
  const [error, setError] = useState("");

  const update = useMutation({
    mutationFn: () => ticketsApi.update(id, { status, priority, technician_id: user?.id, internal_notes: internalNotes || undefined, resolution_notes: resolutionNotes || undefined }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ticket", id] });
      queryClient.invalidateQueries({ queryKey: ["ticket-queue"] });
      setError("");
    },
    onError: (err) => setError(err instanceof Error ? err.message : "Unable to update ticket")
  });

  const submit = (event: FormEvent) => {
    event.preventDefault();
    update.mutate();
  };

  useEffect(() => {
    if (ticket.data) {
      setStatus(ticket.data.status === "ESCALATED" || ticket.data.status === "OPEN" || ticket.data.status === "REOPENED" ? "IN_PROGRESS" : ticket.data.status);
      setPriority(ticket.data.priority);
    }
  }, [ticket.data]);

  if (ticket.isLoading) {
    return (
      <PageTransition>
        <Skeleton className="h-96" />
      </PageTransition>
    );
  }

  if (!ticket.data) return <PageTransition>Ticket not found.</PageTransition>;

  return (
    <PageTransition>
      <div className="grid gap-5 xl:grid-cols-[1fr_380px]">
        <section className="space-y-5">
          <LinkButton to="/technician/tickets" variant="ghost">Back to queue</LinkButton>
          <div className="rounded-lg border border-line bg-surface p-6 shadow-soft">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <p className="text-sm font-semibold text-brand-700">Ticket #{ticket.data.id}</p>
                <h2 className="mt-2 text-2xl font-semibold text-ink">{ticket.data.title}</h2>
                <p className="mt-2 text-sm text-muted">{ticket.data.user?.email} · {ticket.data.category.replaceAll("_", " ")}</p>
              </div>
              <StatusBadge status={ticket.data.status} />
            </div>
            <div className="mt-5">
              <TicketOperationalPanel ticket={ticket.data} />
            </div>
            <p className="mt-5 whitespace-pre-line rounded-lg border border-line bg-elevated p-4 text-sm leading-6 text-muted">{ticket.data.description}</p>
          </div>

          <div className="rounded-lg border border-line bg-surface shadow-soft">
            <div className="border-b border-line px-5 py-4">
              <h3 className="text-lg font-semibold text-ink">Conversation history</h3>
            </div>
            <div className="space-y-4 bg-base/60 p-4">
              {ticket.data.conversation?.messages?.map((message) => <ChatBubble key={message.id} message={message} />)}
            </div>
          </div>

          <AuditTimeline ticket={ticket.data} />
        </section>

        <form onSubmit={submit} className="h-fit rounded-lg border border-line bg-surface p-5 shadow-soft">
          <h3 className="text-lg font-semibold text-ink">Update ticket</h3>
          <label className="mt-5 block">
            <span className="mb-2 block text-sm font-medium text-ink">Status</span>
            <select
              value={status}
              onChange={(event) => setStatus(event.target.value as TicketStatus)}
              className="h-11 w-full rounded-lg border border-line bg-white px-3 text-sm shadow-sm focus:focus-ring"
            >
              {technicianStatuses.map((item) => (
                <option key={item} value={item}>
                  {item.replaceAll("_", " ")}
                </option>
              ))}
            </select>
          </label>
          <label className="mt-4 block">
            <span className="mb-2 block text-sm font-medium text-ink">Priority</span>
            <select
              value={priority}
              onChange={(event) => setPriority(event.target.value as TicketPriority)}
              className="h-11 w-full rounded-lg border border-line bg-white px-3 text-sm shadow-sm focus:focus-ring"
            >
              {priorities.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>
          <label className="mt-4 block">
            <span className="mb-2 block text-sm font-medium text-ink">Internal notes</span>
            <Textarea value={internalNotes} onChange={(event) => setInternalNotes(event.target.value)} placeholder="Private troubleshooting notes" />
          </label>
          <label className="mt-4 block">
            <span className="mb-2 block text-sm font-medium text-ink">Resolution for user</span>
            <Textarea value={resolutionNotes} onChange={(event) => setResolutionNotes(event.target.value)} placeholder="Visible resolution or next step" />
          </label>
          {error ? <p className="mt-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}
          <Button type="submit" className="mt-5 w-full" isLoading={update.isPending}>
            Save update
          </Button>
        </form>
      </div>
    </PageTransition>
  );
}
