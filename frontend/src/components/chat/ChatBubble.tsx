import { motion } from "framer-motion";
import { Bot, UserRound, Wrench } from "lucide-react";
import { cn } from "../../lib/cn";
import type { Message } from "../../types/api";

const iconBySender = {
  USER: UserRound,
  ASSISTANT: Bot,
  TECHNICIAN: Wrench,
  SYSTEM: Bot
};

export function ChatBubble({ message }: { message: Message }) {
  const isUser = message.sender === "USER";
  const Icon = iconBySender[message.sender];

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={cn("flex gap-3", isUser ? "justify-end" : "justify-start")}
    >
      {!isUser ? (
        <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-brand-50 text-brand-700">
          <Icon className="h-4 w-4" />
        </div>
      ) : null}
      <div
        className={cn(
          "max-w-[82%] whitespace-pre-line rounded-lg px-4 py-3 text-sm leading-6 shadow-sm",
          isUser ? "bg-brand-600 text-white" : "border border-line bg-white text-ink"
        )}
      >
        {message.content}
      </div>
      {isUser ? (
        <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-ink text-white">
          <Icon className="h-4 w-4" />
        </div>
      ) : null}
    </motion.div>
  );
}

