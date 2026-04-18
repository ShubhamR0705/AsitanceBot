import { useQuery } from "@tanstack/react-query";
import { ticketsApi } from "../../api/client";
import { TicketList } from "../../components/tickets/TicketList";
import { EmptyState } from "../../components/ui/EmptyState";
import { LinkButton } from "../../components/ui/LinkButton";
import { PageTransition } from "../../components/ui/PageTransition";
import { Skeleton } from "../../components/ui/Skeleton";

export function MyTicketsPage() {
  const tickets = useQuery({ queryKey: ["my-tickets"], queryFn: ticketsApi.mine });

  return (
    <PageTransition>
      <div className="space-y-5">
        <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
          <div>
            <h2 className="text-2xl font-semibold text-ink">My tickets</h2>
            <p className="mt-2 text-sm text-muted">Track escalated issues and technician updates.</p>
          </div>
          <LinkButton to="/user/chat">New support chat</LinkButton>
        </div>
        {tickets.isLoading ? (
          <div className="space-y-3">
            <Skeleton className="h-16" />
            <Skeleton className="h-16" />
            <Skeleton className="h-16" />
          </div>
        ) : tickets.data?.length ? (
          <TicketList tickets={tickets.data} detailBasePath="/user/tickets" />
        ) : (
          <EmptyState title="No tickets yet" description="When an issue fails two AI attempts, it will be escalated and listed here." />
        )}
      </div>
    </PageTransition>
  );
}
