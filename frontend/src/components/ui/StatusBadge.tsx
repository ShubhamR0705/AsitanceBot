import type { TicketStatus } from "../../types/api";
import { Badge } from "./Badge";

const statusTone: Record<TicketStatus, "neutral" | "success" | "warning" | "error" | "info" | "brand"> = {
  OPEN: "info",
  ESCALATED: "warning",
  IN_PROGRESS: "brand",
  WAITING_FOR_USER: "warning",
  RESOLVED: "success",
  CLOSED: "neutral",
  REOPENED: "error"
};

export function StatusBadge({ status }: { status: TicketStatus }) {
  return <Badge tone={statusTone[status]}>{status.replaceAll("_", " ")}</Badge>;
}
