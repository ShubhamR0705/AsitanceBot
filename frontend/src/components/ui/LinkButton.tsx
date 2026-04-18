import { motion } from "framer-motion";
import { Link, type LinkProps } from "react-router-dom";
import { cn } from "../../lib/cn";

type LinkButtonVariant = "primary" | "secondary" | "ghost";

const variants: Record<LinkButtonVariant, string> = {
  primary: "bg-brand-600 text-white shadow-lift hover:bg-brand-700",
  secondary: "border border-line bg-surface text-ink shadow-soft hover:border-brand-500/50 hover:bg-brand-50",
  ghost: "text-muted hover:bg-elevated hover:text-ink"
};

interface LinkButtonProps extends LinkProps {
  variant?: LinkButtonVariant;
}

export function LinkButton({ className, variant = "primary", ...props }: LinkButtonProps) {
  return (
    <motion.div whileHover={{ y: -1 }} whileTap={{ scale: 0.98 }} transition={{ duration: 0.15 }}>
      <Link
        className={cn(
          "inline-flex min-h-10 items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold transition focus-visible:focus-ring",
          variants[variant],
          className
        )}
        {...props}
      />
    </motion.div>
  );
}
