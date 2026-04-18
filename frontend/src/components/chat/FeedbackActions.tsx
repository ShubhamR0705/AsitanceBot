import { CheckCircle2, XCircle } from "lucide-react";
import { Button } from "../ui/Button";

interface FeedbackActionsProps {
  onResolved: () => void;
  onNotResolved: () => void;
  isLoading?: boolean;
  disabled?: boolean;
}

export function FeedbackActions({ onResolved, onNotResolved, isLoading, disabled }: FeedbackActionsProps) {
  return (
    <div className="flex flex-col gap-2 border-t border-line bg-elevated px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
      <p className="text-sm text-muted">Did this resolve the issue?</p>
      <div className="flex gap-2">
        <Button variant="secondary" onClick={onResolved} isLoading={isLoading} disabled={disabled}>
          <CheckCircle2 className="h-4 w-4" />
          Resolved
        </Button>
        <Button variant="ghost" onClick={onNotResolved} isLoading={isLoading} disabled={disabled}>
          <XCircle className="h-4 w-4" />
          Not Resolved
        </Button>
      </div>
    </div>
  );
}

