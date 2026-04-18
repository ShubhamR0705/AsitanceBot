import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useParams } from "react-router-dom";
import { ticketsApi } from "../../api/client";
import { ChatBubble } from "../../components/chat/ChatBubble";
import { TicketChatPanel } from "../../components/tickets/TicketChatPanel";
import { AuditTimeline, TicketOperationalPanel } from "../../components/tickets/TicketOperationalPanel";
import { Button } from "../../components/ui/Button";
import { LinkButton } from "../../components/ui/LinkButton";
import { PageTransition } from "../../components/ui/PageTransition";
import { Skeleton } from "../../components/ui/Skeleton";
import { StatusBadge } from "../../components/ui/StatusBadge";
import { Textarea } from "../../components/ui/Input";

export function TicketDetailPage() {
  const { ticketId } = useParams();
  const id = Number(ticketId);
  const queryClient = useQueryClient();
  const [reopenNote, setReopenNote] = useState("");
  const ticket = useQuery({ queryKey: ["ticket", id], queryFn: () => ticketsApi.detail(id), enabled: Number.isFinite(id) });
  const reopen = useMutation({
    mutationFn: () => ticketsApi.reopen(id, reopenNote || undefined),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ticket", id] });
      queryClient.invalidateQueries({ queryKey: ["my-tickets"] });
      setReopenNote("");
    }
  });

  if (ticket.isLoading) {
    return (
      <PageTransition>
        <div className="space-y-3">
          <Skeleton className="h-24" />
          <Skeleton className="h-72" />
        </div>
      </PageTransition>
    );
  }

  if (!ticket.data) {
    return <PageTransition>Ticket not found.</PageTransition>;
  }

  return (
    <PageTransition>
      <div className="space-y-5">
        <LinkButton to="/user/tickets" variant="ghost">Back to tickets</LinkButton>
        <section className="rounded-lg border border-line bg-surface p-6 shadow-soft">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <p className="text-sm font-semibold text-brand-700">Ticket #{ticket.data.id}</p>
              <h2 className="mt-2 text-2xl font-semibold text-ink">{ticket.data.title}</h2>
              <p className="mt-2 text-sm text-muted">{ticket.data.category.replaceAll("_", " ")}</p>
            </div>
            <StatusBadge status={ticket.data.status} />
          </div>
          <div className="mt-5">
            <TicketOperationalPanel ticket={ticket.data} />
          </div>
          {ticket.data.resolution_notes ? (
            <div className="mt-5 rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-sm leading-6 text-emerald-800">
              {ticket.data.resolution_notes}
            </div>
          ) : null}
          {ticket.data.request_type === "SOFTWARE_INSTALL" ? (
            <div className="mt-5 rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm leading-6 text-amber-900">
              Approval status: <strong>{ticket.data.approval_status.replaceAll("_", " ")}</strong>
              {ticket.data.approval_notes ? ` · ${ticket.data.approval_notes}` : ""}
            </div>
          ) : null}
          {ticket.data.status === "RESOLVED" || ticket.data.status === "CLOSED" ? (
            <div className="mt-5 rounded-lg border border-line bg-elevated p-4">
              <p className="text-sm font-semibold text-ink">Still need help?</p>
              <Textarea className="mt-3" value={reopenNote} onChange={(event) => setReopenNote(event.target.value)} placeholder="Add a short follow-up note" />
              <Button className="mt-3" variant="secondary" isLoading={reopen.isPending} onClick={() => reopen.mutate()}>
                Reopen ticket
              </Button>
            </div>
          ) : null}
        </section>

        <TicketChatPanel ticket={ticket.data} />

        <section className="rounded-lg border border-line bg-surface shadow-soft">
          <div className="border-b border-line px-5 py-4">
            <h3 className="text-lg font-semibold text-ink">Conversation history</h3>
          </div>
          <div className="space-y-4 bg-base/60 p-4">
            {ticket.data.conversation?.messages?.map((message) => <ChatBubble key={message.id} message={message} />)}
          </div>
        </section>
        <AuditTimeline ticket={ticket.data} />
      </div>
    </PageTransition>
  );
}
