import { motion } from "framer-motion";
import { Check, Send } from "lucide-react";
import { useMemo, useState } from "react";
import { cn } from "../../lib/cn";
import type { GuidedQuestion, GuidedQuestionOption, StructuredResponse } from "../../types/api";

type GuidedQuestionOptionsProps = {
  questions: GuidedQuestion[];
  disabled?: boolean;
  onAnswer: (content: string, structuredResponse?: StructuredResponse) => void;
};

const fallbackOptionsByField: Record<string, GuidedQuestionOption[]> = {
  affected_app: [
    { label: "Email (Outlook/Gmail)", value: "email" },
    { label: "VPN", value: "vpn" },
    { label: "Company Portal", value: "company_portal" },
    { label: "Internal Tool", value: "internal_tool" },
    { label: "HR System", value: "hr_system" },
    { label: "Other", value: "other", requires_text: true }
  ],
  application: [
    { label: "Email (Outlook/Gmail)", value: "email" },
    { label: "VPN", value: "vpn" },
    { label: "Company Portal", value: "company_portal" },
    { label: "Internal Tool", value: "internal_tool" },
    { label: "HR System", value: "hr_system" },
    { label: "Other", value: "other", requires_text: true }
  ],
  vpn_issue_type: [
    { label: "Cannot connect", value: "cannot_connect" },
    { label: "Connected but no internet", value: "connected_no_internet" },
    { label: "Slow connection", value: "slow_connection" },
    { label: "Disconnecting frequently", value: "disconnecting" },
    { label: "Other", value: "other", requires_text: true }
  ],
  wifi_issue_type: [
    { label: "No networks visible", value: "no_networks_visible" },
    { label: "Connected but no internet", value: "connected_no_internet" },
    { label: "Slow internet", value: "slow_internet" },
    { label: "Frequent disconnect", value: "frequent_disconnect" },
    { label: "Other", value: "other", requires_text: true }
  ],
  password_issue_type: [
    { label: "Forgot password", value: "forgot_password" },
    { label: "Account locked", value: "account_locked" },
    { label: "Incorrect password error", value: "incorrect_password" },
    { label: "MFA issue", value: "mfa_issue" },
    { label: "Other", value: "other", requires_text: true }
  ],
  account_locked: [
    { label: "Yes - account locked", value: "yes" },
    { label: "No - different error", value: "no" },
    { label: "I am not sure", value: "unknown" },
    { label: "Other", value: "other", requires_text: true }
  ],
  mfa_available: [
    { label: "Yes - I can access MFA", value: "yes" },
    { label: "No - MFA unavailable", value: "no" },
    { label: "I am not sure", value: "unknown" },
    { label: "Other", value: "other", requires_text: true }
  ],
  mfa_prompt: [
    { label: "Yes - prompt appears", value: "yes" },
    { label: "No - no prompt", value: "no" },
    { label: "I am not sure", value: "unknown" },
    { label: "Other", value: "other", requires_text: true }
  ],
  internet_working: [
    { label: "Yes - normal websites work", value: "yes" },
    { label: "No - internet is down", value: "no" },
    { label: "I am not sure", value: "unknown" },
    { label: "Other", value: "other", requires_text: true }
  ],
  device_os: [
    { label: "Windows laptop", value: "windows" },
    { label: "macOS", value: "macos" },
    { label: "Ubuntu/Linux", value: "linux" },
    { label: "Mobile device", value: "mobile" },
    { label: "Other", value: "other", requires_text: true }
  ],
  email_client: [
    { label: "Outlook", value: "outlook" },
    { label: "Webmail", value: "webmail" },
    { label: "Apple Mail", value: "apple_mail" },
    { label: "Other", value: "other", requires_text: true }
  ],
  webmail_works: [
    { label: "Yes - webmail works", value: "yes" },
    { label: "No - webmail also fails", value: "no" },
    { label: "I am not sure", value: "unknown" },
    { label: "Other", value: "other", requires_text: true }
  ],
  send_receive_scope: [
    { label: "Sending", value: "sending" },
    { label: "Receiving", value: "receiving" },
    { label: "Sync/calendar", value: "sync" },
    { label: "Attachments", value: "attachments" },
    { label: "Other", value: "other", requires_text: true }
  ]
};

const booleanFields = new Set(["account_locked", "cache_cleared", "internet_working", "mfa_available", "mfa_prompt", "other_devices_working", "other_users_affected", "reset_attempted", "restart_done", "webmail_works"]);
const genericOptionLabels = new Set(["yes", "no", "not sure"]);

export function GuidedQuestionOptions({ questions, disabled, onAnswer }: GuidedQuestionOptionsProps) {
  return (
    <div className="ml-11 mt-3 space-y-3">
      {questions.map((question) => (
        <GuidedQuestionCard key={`${question.field}-${question.question}`} question={question} disabled={disabled} onAnswer={onAnswer} />
      ))}
    </div>
  );
}

function GuidedQuestionCard({ question, disabled, onAnswer }: { question: GuidedQuestion; disabled?: boolean; onAnswer: GuidedQuestionOptionsProps["onAnswer"] }) {
  const [selectedValues, setSelectedValues] = useState<string[]>([]);
  const [otherMode, setOtherMode] = useState(false);
  const [otherText, setOtherText] = useState("");

  const selectedLabels = useMemo(
    () => question.options.filter((option) => selectedValues.includes(option.value)).map((option) => option.label),
    [question.options, selectedValues]
  );

  const submitSingle = (option: GuidedQuestionOption) => {
    if (option.requires_text || option.value === "other") {
      setOtherMode(true);
      return;
    }
    onAnswer(option.label, {
      field: question.field,
      value: option.value,
      label: option.label,
      input_type: question.input_type,
      question: question.question
    });
  };

  const toggleMulti = (option: GuidedQuestionOption) => {
    if (option.requires_text || option.value === "other") {
      setOtherMode(true);
      return;
    }
    setSelectedValues((current) => (current.includes(option.value) ? current.filter((value) => value !== option.value) : [...current, option.value]));
  };

  const submitMulti = () => {
    if (!selectedValues.length) return;
    onAnswer(selectedLabels.join(", "), {
      field: question.field,
      value: selectedValues,
      label: selectedLabels.join(", "),
      input_type: question.input_type,
      question: question.question
    });
  };

  const submitOther = () => {
    const text = otherText.trim();
    if (!text) return;
    onAnswer(text);
    setOtherText("");
    setOtherMode(false);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.18 }}
      className="rounded-lg border border-brand-100 bg-white px-4 py-3 shadow-sm"
    >
      <p className="text-xs font-semibold uppercase text-brand-700">Quick answer</p>
      <p className="mt-1 text-sm font-medium text-ink">{question.question}</p>
      <div className="mt-3 flex flex-wrap gap-2">
        {question.options.map((option) => {
          const selected = selectedValues.includes(option.value);
          const onClick = question.input_type === "multi_select" ? () => toggleMulti(option) : () => submitSingle(option);
          return (
            <motion.button
              key={option.value}
              type="button"
              whileHover={disabled ? undefined : { y: -1 }}
              whileTap={disabled ? undefined : { scale: 0.98 }}
              disabled={disabled}
              onClick={onClick}
              className={cn(
                "inline-flex min-h-9 items-center gap-2 rounded-lg border px-3 py-2 text-left text-sm transition disabled:cursor-not-allowed disabled:opacity-60",
                selected ? "border-brand-500 bg-brand-50 text-brand-800" : "border-line bg-surface text-ink hover:border-brand-300 hover:bg-brand-50"
              )}
            >
              {selected ? <Check className="h-3.5 w-3.5" /> : null}
              {option.label}
            </motion.button>
          );
        })}
      </div>

      {question.input_type === "multi_select" ? (
        <button
          type="button"
          disabled={disabled || !selectedValues.length}
          onClick={submitMulti}
          className="mt-3 inline-flex min-h-9 items-center rounded-lg bg-brand-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:bg-muted"
        >
          Save selection
        </button>
      ) : null}

      {otherMode ? (
        <div className="mt-3 flex flex-col gap-2 sm:flex-row">
          <input
            value={otherText}
            onChange={(event) => setOtherText(event.target.value)}
            placeholder="Type the details instead"
            className="min-h-10 flex-1 rounded-lg border border-line bg-surface px-3 text-sm transition focus:border-brand-500 focus:focus-ring"
          />
          <button
            type="button"
            disabled={disabled || !otherText.trim()}
            onClick={submitOther}
            className="inline-flex min-h-10 items-center justify-center gap-2 rounded-lg bg-ink px-3 text-sm font-semibold text-white transition hover:bg-ink/90 disabled:cursor-not-allowed disabled:bg-muted"
          >
            <Send className="h-4 w-4" />
            Send
          </button>
        </div>
      ) : null}
    </motion.div>
  );
}

export function getGuidedQuestions(meta: Record<string, unknown> | null | undefined): GuidedQuestion[] {
  if (isGuidedQuestion(meta)) {
    return [meta];
  }
  if (meta?.type === "question") {
    logInvalidGuidedQuestion(meta);
  }

  const rawQuestions = meta?.structured_questions;
  if (Array.isArray(rawQuestions)) {
    const structuredQuestions = rawQuestions.filter(isGuidedQuestion);
    if (structuredQuestions.length) {
      return structuredQuestions;
    }
    rawQuestions.forEach(logInvalidGuidedQuestion);
  }

  return getLegacyGuidedQuestions(meta);
}

function isGuidedQuestion(value: unknown): value is GuidedQuestion {
  if (!value || typeof value !== "object") {
    return false;
  }
  const candidate = value as Partial<GuidedQuestion>;
  const isShapeValid =
    candidate.type === "question" &&
    typeof candidate.question === "string" &&
    typeof candidate.field === "string" &&
    (candidate.input_type === "single_select" || candidate.input_type === "multi_select") &&
    Array.isArray(candidate.options);
  return isShapeValid && isQuestionOptionAligned(candidate as GuidedQuestion);
}

function getLegacyGuidedQuestions(meta: Record<string, unknown> | null | undefined): GuidedQuestion[] {
  const rawQuestions = meta?.questions;
  if (!Array.isArray(rawQuestions)) {
    return [];
  }
  const missingFields = Array.isArray(meta?.missing_fields) ? meta.missing_fields.filter((field): field is string => typeof field === "string") : [];
  const usedFields = new Set<string>();

  return rawQuestions
    .filter((question): question is string => typeof question === "string")
    .map((question) => {
      const field = fieldForLegacyQuestion(question, missingFields, usedFields);
      if (!field) return null;
      usedFields.add(field);
      return {
        type: "question",
        question,
        field,
        input_type: field === "business_impact" ? "multi_select" : "single_select",
        options: fallbackOptionsByField[field] ?? []
      } satisfies GuidedQuestion;
    })
    .filter((question): question is GuidedQuestion => question !== null)
    .filter(isQuestionOptionAligned);
}

function fieldForLegacyQuestion(question: string, missingFields: string[], usedFields: Set<string>) {
  const lower = question.toLowerCase();
  const candidates: Array<[string, boolean]> = [
    ["device_os", lower.includes("device") && (lower.includes("os") || lower.includes("windows") || lower.includes("mac"))],
    ["internet_working", lower.includes("browse") || lower.includes("normal websites") || lower.includes("internet")],
    ["mfa_prompt", lower.includes("mfa prompt") || lower.includes("receive an mfa")],
    ["mfa_available", lower.includes("mfa method") || lower.includes("authenticator")],
    ["account_locked", lower.includes("account is locked") || lower.includes("locked")],
    ["affected_app", lower.includes("application") || lower.includes("company service") || lower.includes("trying to access")],
    ["email_client", lower.includes("outlook") || lower.includes("gmail") || lower.includes("webmail")],
    ["webmail_works", lower.includes("webmail work")],
    ["send_receive_scope", lower.includes("sending") || lower.includes("receiving") || lower.includes("sync") || lower.includes("attachment")],
    ["business_impact", lower.includes("blocking") || lower.includes("multiple people")]
  ];
  const detected = candidates.find(([field, matches]) => matches && missingFields.includes(field) && !usedFields.has(field));
  if (detected) {
    return detected[0];
  }
  return missingFields.find((field) => !usedFields.has(field) && fallbackOptionsByField[field]);
}

function isQuestionOptionAligned(question: GuidedQuestion) {
  const nonOtherOptions = question.options.filter((option) => option.value !== "other" && option.label.trim() && option.value.trim());
  if (nonOtherOptions.length < 3) {
    return false;
  }

  const labels = new Set(nonOtherOptions.map((option) => option.label.trim().toLowerCase()));
  const values = new Set(nonOtherOptions.map((option) => option.value.trim().toLowerCase()));
  const isBoolean = booleanFields.has(question.field) || /^(are|can|did|do|does|have|has|is|was|were)\b/i.test(question.question.trim());

  if ([...labels].some((label) => genericOptionLabels.has(label)) && !isBoolean) {
    return false;
  }
  if (values.has("yes") && values.has("no") && !isBoolean) {
    return false;
  }
  if (["affected_app", "application", "affected_site"].includes(question.field) && (values.has("yes") || values.has("no") || values.has("unknown"))) {
    return false;
  }
  if (question.field.endsWith("_issue_type") && (values.has("yes") || values.has("no") || values.has("unknown"))) {
    return false;
  }
  return true;
}

function logInvalidGuidedQuestion(value: unknown) {
  if (typeof console === "undefined" || typeof console.warn !== "function") {
    return;
  }
  console.warn("AssistIQ ignored invalid guided question metadata", value);
}
