import type { TicketPriority } from "../../types/api";
import { Badge } from "./Badge";

const priorityTone: Record<TicketPriority, "neutral" | "success" | "warning" | "error" | "info" | "brand"> = {
  LOW: "neutral",
  MEDIUM: "info",
  HIGH: "warning",
  CRITICAL: "error"
};

export function PriorityBadge({ priority }: { priority: TicketPriority }) {
  return <Badge tone={priorityTone[priority]}>{priority}</Badge>;
}
