import { useMutation, useQueryClient } from "@tanstack/react-query";
import { FormEvent, useState } from "react";
import { Send } from "lucide-react";
import { ticketsApi } from "../../api/client";
import { useAuth } from "../../contexts/AuthContext";
import type { Ticket } from "../../types/api";
import { Button } from "../ui/Button";
import { Textarea } from "../ui/Input";

export function TicketChatPanel({ ticket }: { ticket: Ticket }) {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [content, setContent] = useState("");
  const [error, setError] = useState("");
  const isClosed = ticket.status === "RESOLVED" || ticket.status === "CLOSED";
  const canSend = Boolean(
    user &&
      !isClosed &&
      (user.role === "ADMIN" || (user.role === "USER" && ticket.user_id === user.id) || (user.role === "TECHNICIAN" && ticket.technician_id === user.id))
  );

  const send = useMutation({
    mutationFn: () => ticketsApi.sendMessage(ticket.id, content),
    onSuccess: () => {
      setContent("");
      setError("");
      queryClient.invalidateQueries({ queryKey: ["ticket", ticket.id] });
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
    onError: (err) => setError(err instanceof Error ? err.message : "Unable to send message")
  });

  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (!content.trim()) return;
    send.mutate();
  };

  return (
    <section className="rounded-lg border border-line bg-surface shadow-soft">
      <div className="border-b border-line px-5 py-4">
        <h3 className="text-lg font-semibold text-ink">Ticket chat</h3>
        <p className="mt-1 text-sm text-muted">User and assigned support can continue here until the ticket is resolved.</p>
      </div>
      <div className="space-y-3 bg-base/60 p-4">
        {ticket.ticket_messages?.length ? (
          ticket.ticket_messages.map((message) => {
            const own = message.sender_id === user?.id;
            return (
              <div key={message.id} className={`flex ${own ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-[82%] rounded-lg border px-4 py-3 shadow-sm ${own ? "border-brand-200 bg-brand-50" : "border-line bg-white"}`}>
                  <div className="mb-1 flex items-center gap-2 text-xs font-semibold uppercase text-muted">
                    <span>{message.sender?.full_name ?? message.sender_role}</span>
                    <span>{new Date(message.created_at).toLocaleString()}</span>
                  </div>
                  <p className="whitespace-pre-line text-sm leading-6 text-ink">{message.content}</p>
                </div>
              </div>
            );
          })
        ) : (
          <p className="rounded-lg border border-dashed border-line bg-elevated p-6 text-center text-sm text-muted">
            No support messages yet. The AI conversation remains below for context.
          </p>
        )}
      </div>
      <form onSubmit={submit} className="border-t border-line p-4">
        {canSend ? (
          <>
            <Textarea value={content} onChange={(event) => setContent(event.target.value)} placeholder="Write a ticket update..." />
            {error ? <p className="mt-3 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}
            <Button type="submit" className="mt-3" isLoading={send.isPending}>
              <Send className="h-4 w-4" />
              Send message
            </Button>
          </>
        ) : (
          <p className="rounded-lg border border-line bg-elevated p-4 text-sm text-muted">
            {isClosed ? "This ticket is resolved or closed, so chat is read-only." : "Messages are available after the ticket is assigned to you."}
          </p>
        )}
      </form>
    </section>
  );
}
