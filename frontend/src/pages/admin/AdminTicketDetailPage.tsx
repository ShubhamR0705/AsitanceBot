import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FormEvent, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { adminApi, ticketsApi } from "../../api/client";
import { ChatBubble } from "../../components/chat/ChatBubble";
import { AuditTimeline, TicketOperationalPanel } from "../../components/tickets/TicketOperationalPanel";
import { Button } from "../../components/ui/Button";
import { LinkButton } from "../../components/ui/LinkButton";
import { PageTransition } from "../../components/ui/PageTransition";
import { Skeleton } from "../../components/ui/Skeleton";
import { StatusBadge } from "../../components/ui/StatusBadge";
import { Textarea } from "../../components/ui/Input";
import type { TicketPriority, TicketStatus } from "../../types/api";

const statuses: TicketStatus[] = ["OPEN", "ESCALATED", "REOPENED", "IN_PROGRESS", "WAITING_FOR_USER", "RESOLVED", "CLOSED"];
const priorities: TicketPriority[] = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];

export function AdminTicketDetailPage() {
  const { ticketId } = useParams();
  const id = Number(ticketId);
  const queryClient = useQueryClient();
  const ticket = useQuery({ queryKey: ["ticket", id], queryFn: () => ticketsApi.detail(id), enabled: Number.isFinite(id) });
  const users = useQuery({ queryKey: ["admin-users"], queryFn: adminApi.users });
  const [status, setStatus] = useState<TicketStatus>("ESCALATED");
  const [priority, setPriority] = useState<TicketPriority>("MEDIUM");
  const [technicianId, setTechnicianId] = useState("");
  const [internalNotes, setInternalNotes] = useState("");
  const [resolutionNotes, setResolutionNotes] = useState("");

  const update = useMutation({
    mutationFn: () =>
      ticketsApi.update(id, {
        status,
        priority,
        technician_id: technicianId ? Number(technicianId) : undefined,
        internal_notes: internalNotes || undefined,
        resolution_notes: resolutionNotes || undefined
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ticket", id] });
      queryClient.invalidateQueries({ queryKey: ["all-tickets"] });
      queryClient.invalidateQueries({ queryKey: ["admin-analytics"] });
    }
  });

  const submit = (event: FormEvent) => {
    event.preventDefault();
    update.mutate();
  };

  useEffect(() => {
    if (ticket.data) {
      setStatus(ticket.data.status);
      setPriority(ticket.data.priority);
      setTechnicianId(ticket.data.technician_id ? String(ticket.data.technician_id) : "");
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
          <LinkButton to="/admin/tickets" variant="ghost">Back to all tickets</LinkButton>
          <div className="rounded-lg border border-line bg-surface p-6 shadow-soft">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <p className="text-sm font-semibold text-brand-700">Ticket #{ticket.data.id}</p>
                <h2 className="mt-2 text-2xl font-semibold text-ink">{ticket.data.title}</h2>
                <p className="mt-2 text-sm text-muted">
                  {ticket.data.user?.email} · {ticket.data.technician?.email ?? "Unassigned"} · {ticket.data.category.replaceAll("_", " ")}
                </p>
              </div>
              <StatusBadge status={ticket.data.status} />
            </div>
            <div className="mt-5">
              <TicketOperationalPanel ticket={ticket.data} />
            </div>
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
          <h3 className="text-lg font-semibold text-ink">Admin update</h3>
          <label className="mt-5 block">
            <span className="mb-2 block text-sm font-medium text-ink">Status</span>
            <select value={status} onChange={(event) => setStatus(event.target.value as TicketStatus)} className="h-11 w-full rounded-lg border border-line bg-white px-3 text-sm shadow-sm focus:focus-ring">
              {statuses.map((item) => (
                <option key={item} value={item}>
                  {item.replaceAll("_", " ")}
                </option>
              ))}
            </select>
          </label>
          <label className="mt-4 block">
            <span className="mb-2 block text-sm font-medium text-ink">Priority</span>
            <select value={priority} onChange={(event) => setPriority(event.target.value as TicketPriority)} className="h-11 w-full rounded-lg border border-line bg-white px-3 text-sm shadow-sm focus:focus-ring">
              {priorities.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>
          <label className="mt-4 block">
            <span className="mb-2 block text-sm font-medium text-ink">Technician</span>
            <select value={technicianId} onChange={(event) => setTechnicianId(event.target.value)} className="h-11 w-full rounded-lg border border-line bg-white px-3 text-sm shadow-sm focus:focus-ring">
              <option value="">Unassigned</option>
              {users.data?.filter((item) => item.role === "TECHNICIAN").map((item) => (
                <option key={item.id} value={item.id}>
                  {item.full_name} · {item.email}
                </option>
              ))}
            </select>
          </label>
          <label className="mt-4 block">
            <span className="mb-2 block text-sm font-medium text-ink">Internal notes</span>
            <Textarea value={internalNotes} onChange={(event) => setInternalNotes(event.target.value)} />
          </label>
          <label className="mt-4 block">
            <span className="mb-2 block text-sm font-medium text-ink">Resolution</span>
            <Textarea value={resolutionNotes} onChange={(event) => setResolutionNotes(event.target.value)} />
          </label>
          <Button type="submit" className="mt-5 w-full" isLoading={update.isPending}>
            Save
          </Button>
        </form>
      </div>
    </PageTransition>
  );
}
