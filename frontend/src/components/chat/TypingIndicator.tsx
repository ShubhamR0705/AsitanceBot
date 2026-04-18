import { motion } from "framer-motion";

export function TypingIndicator() {
  return (
    <div className="flex items-center gap-3">
      <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-50 text-brand-700">AI</div>
      <div className="rounded-lg border border-line bg-white px-4 py-3 shadow-sm">
        <div className="flex gap-1">
          {[0, 1, 2].map((dot) => (
            <motion.span
              key={dot}
              className="h-2 w-2 rounded-full bg-brand-600"
              animate={{ opacity: [0.35, 1, 0.35], y: [0, -2, 0] }}
              transition={{ duration: 0.8, repeat: Infinity, delay: dot * 0.12 }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

