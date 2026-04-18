import { Send } from "lucide-react";
import { FormEvent, useState } from "react";
import { Button } from "../ui/Button";

export function ChatComposer({ onSend, isLoading }: { onSend: (message: string) => void; isLoading?: boolean }) {
  const [message, setMessage] = useState("");

  const submit = (event: FormEvent) => {
    event.preventDefault();
    const next = message.trim();
    if (!next) return;
    onSend(next);
    setMessage("");
  };

  return (
    <form onSubmit={submit} className="flex flex-col gap-3 border-t border-line bg-surface p-4 sm:flex-row">
      <textarea
        value={message}
        onChange={(event) => setMessage(event.target.value)}
        placeholder="Describe the IT issue, including any exact error message..."
        className="min-h-12 flex-1 resize-none rounded-lg border border-line bg-white px-3 py-3 text-sm shadow-sm transition placeholder:text-muted/70 focus:border-brand-500 focus:focus-ring"
      />
      <Button type="submit" isLoading={isLoading} disabled={!message.trim()} className="sm:self-end">
        <Send className="h-4 w-4" />
        Send
      </Button>
    </form>
  );
}

