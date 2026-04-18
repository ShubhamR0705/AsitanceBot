import { motion, useMotionValue, useTransform, animate } from "framer-motion";
import { useEffect } from "react";
import { cn } from "../../lib/cn";

interface StatCardProps {
  label: string;
  value: number;
  detail?: string;
  className?: string;
}

export function StatCard({ label, value, detail, className }: StatCardProps) {
  const count = useMotionValue(0);
  const rounded = useTransform(count, (latest) => Math.round(latest).toLocaleString());

  useEffect(() => {
    const controls = animate(count, value, { duration: 0.7, ease: "easeOut" });
    return controls.stop;
  }, [count, value]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -2 }}
      transition={{ duration: 0.2 }}
      className={cn("premium-panel p-5", className)}
    >
      <p className="text-sm font-medium text-muted">{label}</p>
      <motion.p className="mt-3 text-3xl font-semibold text-ink">{rounded}</motion.p>
      {detail ? <p className="mt-2 text-sm text-muted">{detail}</p> : null}
    </motion.div>
  );
}
