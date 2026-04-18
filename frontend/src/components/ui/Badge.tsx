import type { HTMLAttributes } from "react";
import { cn } from "../../lib/cn";

type BadgeTone = "neutral" | "success" | "warning" | "error" | "info" | "brand";

const tones: Record<BadgeTone, string> = {
  neutral: "border-line bg-elevated text-muted",
  success: "border-emerald-200 bg-emerald-50 text-emerald-700",
  warning: "border-yellow-200 bg-yellow-50 text-yellow-800",
  error: "border-red-200 bg-red-50 text-red-700",
  info: "border-blue-200 bg-blue-50 text-blue-700",
  brand: "border-brand-100 bg-brand-50 text-brand-700"
};

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: BadgeTone;
}

export function Badge({ tone = "neutral", className, ...props }: BadgeProps) {
  return <span className={cn("inline-flex items-center rounded-md border px-2 py-1 text-xs font-semibold", tones[tone], className)} {...props} />;
}

