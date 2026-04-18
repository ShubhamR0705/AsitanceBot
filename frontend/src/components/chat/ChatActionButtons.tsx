import { motion } from "framer-motion";
import { ExternalLink, Route, Zap } from "lucide-react";
import { Link } from "react-router-dom";
import type { ChatAction, Message } from "../../types/api";

const allowedHosts = new Set(["company.com", "mail.company.com"]);
const allowedTriggers = new Set(["request_human_support"]);

export function ChatActionButtons({ message }: { message: Message }) {
  const actions = getChatActions(message);
  if (!actions.length) return null;

  return (
    <div className="ml-11 mt-3 flex flex-wrap gap-2">
      {actions.map((action) => (
        <ActionButton key={`${action.type}-${action.label}-${action.url ?? action.route ?? action.trigger ?? ""}`} action={action} />
      ))}
    </div>
  );
}

export function getChatActions(message: Message): ChatAction[] {
  const directActions = Array.isArray(message.actions) ? message.actions : [];
  const metaActions = Array.isArray(message.meta?.actions) ? message.meta.actions : [];
  return [...directActions, ...metaActions].filter(isChatAction).filter(uniqueAction);
}

function ActionButton({ action }: { action: ChatAction }) {
  const className =
    "inline-flex min-h-10 items-center gap-2 rounded-lg border border-brand-200 bg-brand-50 px-3 py-2 text-sm font-semibold text-brand-800 transition hover:border-brand-400 hover:bg-brand-100";

  if (action.type === "link" && action.url) {
    return (
      <motion.a href={action.url} target="_blank" rel="noreferrer" whileHover={{ y: -1 }} whileTap={{ scale: 0.98 }} className={className}>
        <ExternalLink className="h-4 w-4" />
        {action.label}
      </motion.a>
    );
  }

  if (action.type === "internal_route" && action.route) {
    return (
      <motion.div whileHover={{ y: -1 }} whileTap={{ scale: 0.98 }}>
        <Link to={action.route} className={className}>
          <Route className="h-4 w-4" />
          {action.label}
        </Link>
      </motion.div>
    );
  }

  return (
    <button type="button" disabled className={`${className} cursor-not-allowed opacity-60`}>
      <Zap className="h-4 w-4" />
      {action.label}
    </button>
  );
}

function isChatAction(value: unknown): value is ChatAction {
  if (!value || typeof value !== "object") return false;
  const action = value as Partial<ChatAction>;
  if (!action.label || typeof action.label !== "string" || action.label.length > 80) return false;
  if (action.type === "link") {
    return typeof action.url === "string" && isAllowedUrl(action.url);
  }
  if (action.type === "internal_route") {
    return typeof action.route === "string" && isAllowedRoute(action.route);
  }
  if (action.type === "trigger") {
    return typeof action.trigger === "string" && allowedTriggers.has(action.trigger);
  }
  return false;
}

function isAllowedUrl(url: string) {
  try {
    const parsed = new URL(url);
    return parsed.protocol === "https:" && allowedHosts.has(parsed.hostname);
  } catch {
    return false;
  }
}

function isAllowedRoute(route: string) {
  return route.startsWith("/user/tickets") && !route.includes("//") && !route.includes("..");
}

function uniqueAction(action: ChatAction, index: number, actions: ChatAction[]) {
  const identity = `${action.type}-${action.label}-${action.url ?? action.route ?? action.trigger ?? ""}`;
  return actions.findIndex((item) => `${item.type}-${item.label}-${item.url ?? item.route ?? item.trigger ?? ""}` === identity) === index;
}
