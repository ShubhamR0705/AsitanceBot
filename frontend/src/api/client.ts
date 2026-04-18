import type {
  Analytics,
  ChatResponse,
  Conversation,
  FeedbackResponse,
  KnowledgeBaseEntry,
  MessageFeedback,
  NotificationListResponse,
  StructuredResponse,
  Ticket,
  TicketApprovalStatus,
  TicketMessage,
  TicketPriority,
  TicketStatus,
  TokenResponse,
  User,
  UserRole
} from "../types/api";

const API_URL = import.meta.env.VITE_API_URL ?? (import.meta.env.DEV ? "http://localhost:8000/api" : "/api");
const TOKEN_KEY = "assistiq_token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

type RequestOptions = RequestInit & {
  auth?: boolean;
};

async function apiFetch<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const token = getToken();
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  if (options.auth !== false && token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers
  });

  if (!response.ok) {
    let message = "Request failed";
    try {
      const body = await response.json();
      message = body.detail ?? message;
    } catch {
      message = response.statusText || message;
    }
    if (response.status === 401) {
      clearToken();
    }
    throw new Error(message);
  }

  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

export const authApi = {
  signup: (payload: { email: string; full_name: string; password: string }) =>
    apiFetch<TokenResponse>("/auth/signup", { method: "POST", body: JSON.stringify(payload), auth: false }),
  login: (payload: { email: string; password: string }) =>
    apiFetch<TokenResponse>("/auth/login", { method: "POST", body: JSON.stringify(payload), auth: false }),
  me: () => apiFetch<User>("/auth/me")
};

export const chatApi = {
  createConversation: () => apiFetch<Conversation>("/chat/conversations", { method: "POST" }),
  listConversations: () => apiFetch<Conversation[]>("/chat/conversations"),
  getConversation: (id: number) => apiFetch<Conversation>(`/chat/conversations/${id}`),
  sendMessage: (conversationId: number, content: string, structuredResponse?: StructuredResponse) =>
    apiFetch<ChatResponse>(`/chat/conversations/${conversationId}/messages`, {
      method: "POST",
      body: JSON.stringify({ content, structured_response: structuredResponse })
    }),
  submitFeedback: (conversationId: number, resolved: boolean) =>
    apiFetch<FeedbackResponse>(`/chat/conversations/${conversationId}/feedback`, {
      method: "POST",
      body: JSON.stringify({ resolved })
    }),
  submitMessageHelpfulness: (messageId: number, helpful: boolean, note?: string) =>
    apiFetch<MessageFeedback>(`/chat/messages/${messageId}/helpfulness`, {
      method: "POST",
      body: JSON.stringify({ helpful, note })
    })
};

export const ticketsApi = {
  mine: () => apiFetch<Ticket[]>("/tickets/mine"),
  queue: () => apiFetch<Ticket[]>("/tickets/queue"),
  all: () => apiFetch<Ticket[]>("/tickets/all"),
  detail: (id: number) => apiFetch<Ticket>(`/tickets/${id}`),
  update: (
    id: number,
    payload: {
      status?: TicketStatus;
      priority?: TicketPriority;
      technician_id?: number;
      routing_group?: string;
      internal_notes?: string;
      resolution_notes?: string;
    }
  ) => apiFetch<Ticket>(`/tickets/${id}`, { method: "PATCH", body: JSON.stringify(payload) }),
  reopen: (id: number, note?: string) => apiFetch<Ticket>(`/tickets/${id}/reopen`, { method: "POST", body: JSON.stringify({ note }) }),
  messages: (id: number) => apiFetch<TicketMessage[]>(`/tickets/${id}/messages`),
  sendMessage: (id: number, content: string) =>
    apiFetch<TicketMessage>(`/tickets/${id}/messages`, { method: "POST", body: JSON.stringify({ content }) }),
  updateApproval: (id: number, approval_status: TicketApprovalStatus, approval_notes?: string) =>
    apiFetch<Ticket>(`/tickets/${id}/approval`, { method: "PATCH", body: JSON.stringify({ approval_status, approval_notes }) })
};

export const adminApi = {
  analytics: () => apiFetch<Analytics>("/admin/analytics"),
  users: (params?: { role?: UserRole | "ALL"; is_active?: boolean | "ALL" }) => {
    const search = new URLSearchParams();
    if (params?.role && params.role !== "ALL") search.set("role", params.role);
    if (params?.is_active !== undefined && params.is_active !== "ALL") search.set("is_active", String(params.is_active));
    return apiFetch<User[]>(`/admin/users${search.toString() ? `?${search}` : ""}`);
  },
  createUser: (payload: { email: string; full_name: string; password: string; role: UserRole; is_active?: boolean }) =>
    apiFetch<User>("/admin/users", { method: "POST", body: JSON.stringify(payload) }),
  updateUser: (userId: number, payload: { email?: string; full_name?: string; role?: UserRole; is_active?: boolean }) =>
    apiFetch<User>(`/admin/users/${userId}`, { method: "PATCH", body: JSON.stringify(payload) }),
  deactivateUser: (userId: number) => apiFetch<User>(`/admin/users/${userId}`, { method: "DELETE" }),
  updateRole: (userId: number, role: UserRole) =>
    apiFetch<User>(`/admin/users/${userId}/role`, { method: "PATCH", body: JSON.stringify({ role }) }),
  knowledgeBase: () => apiFetch<KnowledgeBaseEntry[]>("/admin/knowledge-base"),
  createKnowledgeBaseEntry: (payload: Omit<KnowledgeBaseEntry, "id" | "created_at" | "updated_at" | "usage_count">) =>
    apiFetch<KnowledgeBaseEntry>("/admin/knowledge-base", { method: "POST", body: JSON.stringify(payload) }),
  updateKnowledgeBaseEntry: (id: number, payload: Partial<KnowledgeBaseEntry>) =>
    apiFetch<KnowledgeBaseEntry>(`/admin/knowledge-base/${id}`, { method: "PATCH", body: JSON.stringify(payload) }),
  deleteKnowledgeBaseEntry: (id: number) => apiFetch<void>(`/admin/knowledge-base/${id}`, { method: "DELETE" })
};

export const notificationsApi = {
  list: () => apiFetch<NotificationListResponse>("/notifications"),
  markRead: (id: number) => apiFetch(`/notifications/${id}/read`, { method: "PATCH" })
};
