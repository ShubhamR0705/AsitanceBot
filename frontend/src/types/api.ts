export type UserRole = "USER" | "TECHNICIAN" | "ADMIN";
export type ConversationStatus = "ACTIVE" | "RESOLVED" | "ESCALATED";
export type ConversationStage = "INTAKE" | "CLARIFYING" | "SUGGESTING_FIX" | "WAITING_FOR_FEEDBACK" | "RESOLVED" | "ESCALATED";
export type MessageSender = "USER" | "ASSISTANT" | "TECHNICIAN" | "SYSTEM";
export type TicketStatus = "OPEN" | "ESCALATED" | "IN_PROGRESS" | "WAITING_FOR_USER" | "RESOLVED" | "CLOSED" | "REOPENED";
export type TicketPriority = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type TicketRequestType = "SUPPORT" | "SOFTWARE_INSTALL";
export type TicketApprovalStatus = "NOT_REQUIRED" | "REQUESTED" | "PENDING_APPROVAL" | "APPROVED" | "REJECTED" | "IN_PROGRESS" | "COMPLETED";
export type GuidedQuestionInputType = "single_select" | "multi_select";
export type ChatActionType = "link" | "internal_route" | "trigger";

export interface ChatAction {
  label: string;
  type: ChatActionType;
  url?: string;
  route?: string;
  trigger?: string;
}

export interface GuidedQuestionOption {
  label: string;
  value: string;
  requires_text?: boolean;
}

export interface GuidedQuestion {
  type: "question";
  question: string;
  field: string;
  input_type: GuidedQuestionInputType;
  options: GuidedQuestionOption[];
  source?: "rule_based" | "llm_generated";
}

export interface StructuredResponse {
  field: string;
  value: string | string[];
  label?: string;
  input_type: GuidedQuestionInputType;
  question?: string;
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface Message {
  id: number;
  conversation_id: number;
  sender: MessageSender;
  content: string;
  meta?: Record<string, unknown> | null;
  actions?: ChatAction[];
  created_at: string;
}

export interface Conversation {
  id: number;
  user_id: number;
  category: string | null;
  status: ConversationStatus;
  failure_count: number;
  triage_stage: ConversationStage;
  collected_context?: Record<string, unknown> | null;
  last_triage?: Record<string, unknown> | null;
  escalation_summary?: string | null;
  created_at: string;
  updated_at: string;
  messages: Message[];
}

export interface Ticket {
  id: number;
  conversation_id: number | null;
  user_id: number;
  technician_id: number | null;
  category: string;
  title: string;
  description: string;
  routing_group: string;
  status: TicketStatus;
  priority: TicketPriority;
  request_type: TicketRequestType;
  assignment_source: string | null;
  assigned_at: string | null;
  requested_software: string | null;
  request_reason: string | null;
  request_device: string | null;
  approval_required: boolean;
  approval_status: TicketApprovalStatus;
  approved_by_id: number | null;
  approved_at: string | null;
  approval_notes: string | null;
  internal_notes: string | null;
  resolution_notes: string | null;
  first_response_at: string | null;
  sla_due_at: string | null;
  sla_breached: boolean;
  reopened_from_ticket_id: number | null;
  reopen_count: number;
  last_reopened_at: string | null;
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
  user?: User | null;
  technician?: User | null;
  approved_by?: User | null;
  conversation?: Conversation | null;
  audit_logs?: AuditLog[];
  ticket_messages?: TicketMessage[];
}

export interface TicketMessage {
  id: number;
  ticket_id: number;
  sender_id: number | null;
  sender_role: UserRole;
  content: string;
  created_at: string;
  sender?: User | null;
}

export interface AuditLog {
  id: number;
  ticket_id: number | null;
  actor_user_id: number | null;
  action_type: string;
  previous_value: Record<string, unknown> | null;
  new_value: Record<string, unknown> | null;
  summary: string;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface ChatResponse {
  conversation: Conversation;
  assistant_message: Message;
  category: string;
  kb_titles: string[];
  escalated: boolean;
  ticket_id: number | null;
}

export interface FeedbackResponse {
  conversation: Conversation;
  assistant_message?: Message | null;
  escalated: boolean;
  ticket_id: number | null;
}

export interface Analytics {
  total_users: number;
  total_tickets: number;
  open_tickets: number;
  escalated_tickets: number;
  resolved_tickets: number;
  assigned_tickets: number;
  unassigned_tickets: number;
  pending_approvals: number;
  active_conversations: number;
  avg_resolution_hours: number | null;
  kb_failure_rate: number;
  low_confidence_conversations: number;
  clarification_requested: number;
  status_breakdown: Record<string, number>;
  category_breakdown: Record<string, number>;
  approval_breakdown: Record<string, number>;
  stage_breakdown: Record<string, number>;
  urgency_breakdown: Record<string, number>;
  escalation_reason_breakdown: Record<string, number>;
  kb_article_usage: Record<string, number>;
  kb_article_outcomes: Record<string, { shown: number; resolved: number; escalated: number; unresolved_feedback: number }>;
  technician_workload: Record<string, number>;
  technician_workload_detail: Record<string, { open: number; resolved: number; total: number }>;
  message_feedback: Record<string, number>;
}

export interface KnowledgeBaseEntry {
  id: number;
  category: string;
  title: string;
  content: string;
  keywords: string;
  is_active: boolean;
  usage_count: number;
  created_at: string;
  updated_at: string;
}

export interface NotificationItem {
  id: number;
  recipient_user_id: number;
  actor_user_id: number | null;
  ticket_id: number | null;
  channel: "IN_APP" | "EMAIL_MOCK";
  title: string;
  body: string;
  is_read: boolean;
  created_at: string;
}

export interface NotificationListResponse {
  unread_count: number;
  notifications: NotificationItem[];
}

export interface MessageFeedback {
  id: number;
  message_id: number;
  conversation_id: number;
  user_id: number;
  helpful: boolean;
  note: string | null;
  created_at: string;
}
