import { useMutation, useQueryClient } from "@tanstack/react-query";
import { AnimatePresence } from "framer-motion";
import { useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { chatApi } from "../../api/client";
import { ChatBubble } from "../../components/chat/ChatBubble";
import { ChatComposer } from "../../components/chat/ChatComposer";
import { FeedbackActions } from "../../components/chat/FeedbackActions";
import { getGuidedQuestions, GuidedQuestionOptions } from "../../components/chat/GuidedQuestionOptions";
import { TypingIndicator } from "../../components/chat/TypingIndicator";
import { Badge } from "../../components/ui/Badge";
import { EmptyState } from "../../components/ui/EmptyState";
import { PageTransition } from "../../components/ui/PageTransition";
import type { Conversation, StructuredResponse } from "../../types/api";

type ChatSendPayload = {
  content: string;
  structuredResponse?: StructuredResponse;
};

export function SupportChatPage() {
  const queryClient = useQueryClient();
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [error, setError] = useState("");
  const [messageFeedback, setMessageFeedback] = useState<Record<number, boolean>>({});
  const containerRef = useRef<HTMLDivElement>(null);

  const createConversation = useMutation({ mutationFn: chatApi.createConversation });
  const sendMessage = useMutation({
    mutationFn: async ({ content, structuredResponse }: ChatSendPayload) => {
      const activeConversation = conversation ?? (await createConversation.mutateAsync());
      return chatApi.sendMessage(activeConversation.id, content, structuredResponse);
    },
    onSuccess: (response) => {
      setConversation(response.conversation);
      queryClient.invalidateQueries({ queryKey: ["my-conversations"] });
      setError("");
      requestAnimationFrame(() => containerRef.current?.scrollTo({ top: containerRef.current.scrollHeight, behavior: "smooth" }));
    },
    onError: (err) => setError(err instanceof Error ? err.message : "Unable to send message")
  });
  const feedback = useMutation({
    mutationFn: (resolved: boolean) => {
      if (!conversation) throw new Error("No active conversation");
      return chatApi.submitFeedback(conversation.id, resolved);
    },
    onSuccess: (response) => {
      setConversation(response.conversation);
      queryClient.invalidateQueries({ queryKey: ["my-tickets"] });
      queryClient.invalidateQueries({ queryKey: ["my-conversations"] });
      requestAnimationFrame(() => containerRef.current?.scrollTo({ top: containerRef.current.scrollHeight, behavior: "smooth" }));
    },
    onError: (err) => setError(err instanceof Error ? err.message : "Unable to submit feedback")
  });
  const helpfulness = useMutation({
    mutationFn: ({ messageId, helpful }: { messageId: number; helpful: boolean }) => chatApi.submitMessageHelpfulness(messageId, helpful),
    onSuccess: (response) => {
      setMessageFeedback((current) => ({ ...current, [response.message_id]: response.helpful }));
    },
    onError: (err) => setError(err instanceof Error ? err.message : "Unable to save helpfulness feedback")
  });

  const messages = useMemo(() => conversation?.messages ?? [], [conversation]);
  const lastAssistantMessage = useMemo(() => [...messages].reverse().find((message) => message.sender === "ASSISTANT"), [messages]);
  const isClarifying = lastAssistantMessage?.meta?.triage_action === "ASK_CLARIFYING_QUESTIONS" || conversation?.triage_stage === "CLARIFYING";
  const collectedContext = conversation?.collected_context ?? {};
  const contextEntries = Object.entries(collectedContext).filter(([, value]) => Boolean(value));
  const canFeedback =
    conversation?.status === "ACTIVE" &&
    Array.isArray(lastAssistantMessage?.meta?.kb_entry_ids) &&
    lastAssistantMessage.meta.kb_entry_ids.length > 0 &&
    lastAssistantMessage?.meta?.support_response !== false &&
    !isClarifying &&
    !sendMessage.isPending;

  return (
    <PageTransition>
      <div className="mx-auto flex max-w-5xl flex-col overflow-hidden rounded-lg border border-line bg-surface shadow-soft">
        <div className="flex flex-col gap-3 border-b border-line bg-elevated px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-ink">Support chat</h2>
            <p className="mt-1 text-sm text-muted">Describe the issue. The assistant will collect key details before suggesting approved fixes.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            {conversation?.category ? <Badge tone="brand">{conversation.category.replaceAll("_", " ")}</Badge> : null}
            {conversation?.triage_stage ? <Badge tone={conversation.triage_stage === "CLARIFYING" ? "warning" : "info"}>{conversation.triage_stage.replaceAll("_", " ")}</Badge> : null}
            {conversation?.status ? <Badge tone={conversation.status === "ESCALATED" ? "warning" : conversation.status === "RESOLVED" ? "success" : "info"}>{conversation.status}</Badge> : null}
          </div>
        </div>

        {contextEntries.length ? (
          <div className="border-b border-line bg-brand-50/60 px-5 py-3">
            <p className="text-xs font-semibold uppercase text-brand-700">Collected triage details</p>
            <div className="mt-2 flex flex-wrap gap-2">
              {contextEntries.slice(0, 6).map(([key, value]) => (
                <Badge key={key} tone="neutral">
                  {key.replaceAll("_", " ")}: {String(value)}
                </Badge>
              ))}
            </div>
          </div>
        ) : null}

        <div ref={containerRef} className="min-h-[460px] flex-1 space-y-4 overflow-y-auto bg-base/60 p-4">
          {messages.length ? (
            <AnimatePresence>
              {messages.map((message) => (
                <div key={message.id}>
                  <ChatBubble message={message} />
                  {message.sender === "ASSISTANT" && getGuidedQuestions(message.meta).length ? (
                    <GuidedQuestionOptions
                      questions={getGuidedQuestions(message.meta)}
                      disabled={message.id !== lastAssistantMessage?.id || sendMessage.isPending || feedback.isPending}
                      onAnswer={(content, structuredResponse) => sendMessage.mutate({ content, structuredResponse })}
                    />
                  ) : null}
                  {message.sender === "ASSISTANT" && Array.isArray(message.meta?.kb_entry_ids) ? (
                    <div className="ml-2 mt-2 flex items-center gap-2 text-xs text-muted">
                      <span>Was this helpful?</span>
                      <button
                        className="rounded-md border border-line bg-surface px-2 py-1 hover:bg-brand-50"
                        onClick={() => helpfulness.mutate({ messageId: message.id, helpful: true })}
                      >
                        Yes
                      </button>
                      <button
                        className="rounded-md border border-line bg-surface px-2 py-1 hover:bg-red-50"
                        onClick={() => helpfulness.mutate({ messageId: message.id, helpful: false })}
                      >
                        No
                      </button>
                      {messageFeedback[message.id] !== undefined ? <Badge tone="success">Saved</Badge> : null}
                    </div>
                  ) : null}
                </div>
              ))}
            </AnimatePresence>
          ) : (
            <EmptyState
              title="What can I help with?"
              description="Try: VPN is not connecting, Outlook will not sync, WiFi keeps dropping, or my password is locked."
            />
          )}
          {sendMessage.isPending || feedback.isPending ? <TypingIndicator /> : null}
        </div>

        {error ? <div className="border-t border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div> : null}

        {conversation?.status === "ESCALATED" ? (
          <div className="border-t border-yellow-200 bg-yellow-50 px-4 py-3 text-sm text-yellow-900">
            This issue is escalated.{" "}
            <Link className="font-semibold underline" to="/user/tickets">
              View your ticket status.
            </Link>
          </div>
        ) : null}

        {canFeedback ? (
          <FeedbackActions
            onResolved={() => feedback.mutate(true)}
            onNotResolved={() => feedback.mutate(false)}
            isLoading={feedback.isPending}
            disabled={sendMessage.isPending}
          />
        ) : null}

        <ChatComposer onSend={(message) => sendMessage.mutate({ content: message })} isLoading={sendMessage.isPending || createConversation.isPending} />
      </div>
    </PageTransition>
  );
}
