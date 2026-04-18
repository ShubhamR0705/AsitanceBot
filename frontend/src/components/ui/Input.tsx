import type { InputHTMLAttributes, TextareaHTMLAttributes } from "react";
import { cn } from "../../lib/cn";

export function Input({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cn(
        "h-11 w-full rounded-lg border border-line bg-white px-3 text-sm text-ink shadow-sm transition placeholder:text-muted/70 focus:border-brand-500 focus:focus-ring",
        className
      )}
      {...props}
    />
  );
}

export function Textarea({ className, ...props }: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      className={cn(
        "min-h-28 w-full rounded-lg border border-line bg-white px-3 py-3 text-sm text-ink shadow-sm transition placeholder:text-muted/70 focus:border-brand-500 focus:focus-ring",
        className
      )}
      {...props}
    />
  );
}

