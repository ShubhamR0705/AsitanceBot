# AssistIQ Project Positioning, Demo, and Interview Guide

This guide is based on the current repository audit, not only the original product brief.

Current verification:

- Backend tests: `118 passed`
- Frontend tests: `8 passed`
- Frontend production build: passed
- Known build note: Vite reports one large JavaScript chunk after adding charts. This is a performance optimization item, not a functional blocker.

## 1. Project Audit Summary

### What Is Definitely Present

AssistIQ is a full-stack AI-assisted IT support platform with a FastAPI backend, React/Vite frontend, PostgreSQL persistence, JWT authentication, role-based access control, chat-based issue intake, KB-grounded troubleshooting, guided question chips, deterministic escalation, technician ticket handling, admin operations, analytics, notifications, audit logs, and deployment support for Render, Vercel, and Supabase.

Implemented backend capabilities include:

- Signup, login, JWT auth, password hashing, and current-user lookup.
- Three roles: `USER`, `TECHNICIAN`, and `ADMIN`.
- User-only chat conversations with message history.
- Chat intent routing for greetings, small talk, support requests, irrelevant input, abusive/frustrated input, and empty input.
- Deterministic classification plus optional Azure OpenAI issue understanding.
- Structured LLM output validation for issue understanding.
- Diagnostic playbooks and guided troubleshooting questions.
- Context-aware selectable answers for common support categories.
- KB retrieval using category, keyword, phrase, title, and content scoring.
- Optional Azure OpenAI response generation grounded in retrieved KB content.
- Deterministic fallback responses when Azure OpenAI is unavailable or invalid.
- Resolved / Not Resolved feedback loop.
- Escalation after two unresolved attempts or immediately for critical cases.
- Technician-ready ticket creation with conversation history and handoff summary.
- Ticket priority, routing group, SLA due time, first response tracking, reopen tracking, notes, and resolution fields.
- Audit logs for important ticket and KB events.
- Role-scoped in-app notifications and mock email logging.
- Admin analytics for tickets, conversations, categories, KB outcomes, feedback, and technician workload.
- Admin KB CRUD with active/inactive article control.
- Demo seed data and enriched KB coverage.
- Docker, Alembic, Render, Vercel, and Supabase deployment support.

Implemented frontend capabilities include:

- Role-protected routes.
- User dashboard, support chat, ticket history, ticket detail, and profile pages.
- Technician dashboard, ticket queue, and ticket detail/update workflow.
- Admin dashboard, visual analytics, user management, ticket overview/detail, and KB management.
- Notification dropdown in the shared app shell.
- Responsive sidebar/topbar layout.
- Tailwind styling, Framer Motion transitions, status badges, priority badges, loading skeletons, empty states, and Recharts analytics.
- Guided question chips with frontend validation so invalid generic Yes/No options are ignored for non-binary questions.

### Partially Implemented Or Bounded Features

- Azure OpenAI is optional. The system works without it through deterministic fallback logic.
- Email notification is currently mock/log based, not a real SMTP or transactional email integration.
- SLA breach alerts are evaluated during ticket operations, not through a continuous background scheduler.
- Retrieval is keyword/phrase scored and RAG-ready, but not using embeddings or a vector database.
- Technician workload is visible in analytics, but automatic technician assignment by workload is not fully implemented. Tickets use routing groups and can be manually assigned or self-assigned.
- Notifications are in-app and role-scoped. They are not real-time WebSocket notifications.
- Monitoring is basic application logging, not full observability with Sentry, Datadog, tracing, or alerting.
- The app is staging/pilot-ready, but enterprise production would require hardening around monitoring, rate limiting, backups, real email, security review, and load testing.

### What Should Not Be Claimed

- Do not claim the system has vector search or embeddings.
- Do not claim real SMTP/email delivery is implemented.
- Do not claim ServiceNow, Jira, Slack, Teams, or SSO integrations are implemented.
- Do not claim multi-tenant architecture.
- Do not claim WebSocket real-time messaging.
- Do not claim autonomous IT remediation on user machines.
- Do not claim the LLM controls ticket status, permissions, or business rules.
- Do not claim full enterprise production readiness without additional monitoring and security hardening.

## 2. Project Summary

### One-Line Summary

AssistIQ is an AI-assisted IT support platform that resolves common issues through guided, KB-grounded chat and escalates unresolved cases to technicians with full context.

### Short Product Summary

AssistIQ helps employees get IT support faster. Users describe an issue in chat, the system understands the request, asks guided follow-up questions when needed, retrieves approved troubleshooting steps, and creates a technician-ready ticket when AI support is not enough.

### Detailed Summary

AssistIQ is a workflow-driven IT support MVP, not just a chatbot. It combines AI-assisted issue understanding with deterministic ticketing rules, role-based access, knowledge base retrieval, guided troubleshooting, feedback collection, and operational analytics. The user gets a simple support chat experience, the technician receives escalated tickets with conversation history and attempted fixes, and the admin can manage users, tickets, KB articles, and support analytics.

### Business-Oriented Summary

AssistIQ reduces repetitive IT support workload by handling common issues first and escalating only the cases that need human attention. It improves employee experience through fast guided support, improves technician efficiency by preserving context, and gives administrators visibility into issue trends, KB performance, escalation load, and support operations.

### Technical Summary

AssistIQ uses FastAPI, PostgreSQL, SQLAlchemy, Alembic, Pydantic, JWT auth, React, Vite, TypeScript, TailwindCSS, Framer Motion, React Query, and Recharts. AI is used for understanding and response generation through Azure OpenAI when configured, while workflow-critical logic such as RBAC, ticket lifecycle, escalation, priority, SLA, and notification visibility remains deterministic and testable.

## 3. Features

### User-Facing Features

| Feature | What It Does | Why It Matters |
| --- | --- | --- |
| Signup and login | Allows employees to access a protected support workspace. | Keeps support data tied to the right user. |
| Support chat | Lets users describe IT issues in natural language. | Reduces friction compared to filling long forms. |
| Guided troubleshooting | Shows selectable answer chips for common clarifying questions. | Improves accuracy and reduces typing. |
| KB-grounded suggestions | Returns approved troubleshooting steps from the knowledge base. | Keeps advice controlled and support-safe. |
| Resolved / Not Resolved feedback | Users confirm whether a fix worked. | Drives retry or escalation workflow. |
| Auto escalation | Creates a ticket after failed attempts or urgent signals. | Prevents users from getting stuck with AI. |
| My tickets | Shows user-owned ticket history and status. | Gives users visibility into support progress. |
| Ticket detail | Shows ticket state and conversation context. | Builds trust after escalation. |
| Helpfulness feedback | Lets users rate assistant replies. | Helps measure KB and answer quality. |

### Technician Features

| Feature | What It Does | Why It Matters |
| --- | --- | --- |
| Ticket queue | Shows actionable open, escalated, reopened, and in-progress tickets. | Gives support agents a clean work queue. |
| Ticket detail | Shows issue summary, category, priority, SLA, user, and conversation history. | Avoids asking the user to repeat information. |
| Status updates | Allows updates to `IN_PROGRESS`, `WAITING_FOR_USER`, `RESOLVED`, and `CLOSED`. | Supports the real support lifecycle. |
| Notes and resolution | Captures internal notes and user-facing resolution text. | Preserves technician decisions and communication. |
| Self-assignment | Technician updates can assign unassigned tickets to themselves. | Keeps ownership simple for a pilot. |
| Audit timeline | Displays important ticket events. | Improves accountability and handoff quality. |

### Admin Features

| Feature | What It Does | Why It Matters |
| --- | --- | --- |
| Admin dashboard | Shows visual support analytics with cards and charts. | Makes operations easy to understand. |
| User management | Lets admins change roles. | Supports real RBAC administration. |
| Ticket overview | Shows all tickets across users. | Gives full operational visibility. |
| Admin ticket update | Allows status, priority, technician assignment, notes, and resolution updates. | Supports oversight and intervention. |
| Analytics page | Shows ticket status, categories, system metrics, workload, and KB performance. | Helps improve support process over time. |
| Knowledge base management | Create, edit, enable/disable, and delete KB articles. | Lets the support team improve AI grounding. |

### AI And Workflow Features

| Feature | What It Does | Why It Matters |
| --- | --- | --- |
| Intent router | Separates greetings, small talk, support requests, irrelevant input, abusive input, and empty input. | Prevents every message from being treated as an IT issue. |
| Classification | Maps issues to categories such as VPN, PASSWORD, ACCESS, WIFI, EMAIL, SOFTWARE, BROWSER, PRINTER, and more. | Enables targeted retrieval and workflow. |
| LLM-assisted understanding | Uses Azure OpenAI for structured interpretation when configured. | Handles vague, messy, and typo-heavy input better. |
| Guardrails | Validates structured LLM output and falls back deterministically if needed. | Reduces hallucination and brittle AI behavior. |
| Diagnostic playbooks | Defines required fields per category. | Creates predictable troubleshooting flow. |
| Guided questions | Uses category and field templates for relevant answer chips. | Improves UX and structured context capture. |
| KB retrieval | Finds relevant active KB articles using scoring. | Grounds support responses in approved content. |
| Grounded response generation | Generates concise steps from KB context only when LLM is configured. | Produces better language without letting AI invent policy. |
| Smart retry | Uses different KB entries on retry when available. | Avoids repeating the same failed advice. |
| Deterministic escalation | Escalates on two failures, urgent/security signals, lockouts, low-confidence ambiguity, and explicit human requests. | Keeps business rules explainable and safe. |

### Security And Access Features

| Feature | What It Does | Why It Matters |
| --- | --- | --- |
| JWT auth | Protects API calls with bearer tokens. | Standard secure API access pattern. |
| Password hashing | Stores hashed passwords, not plaintext. | Basic credential security. |
| Backend RBAC | Enforces role access in API dependencies. | Prevents frontend-only security. |
| User data isolation | Users can view only their own conversations and tickets. | Protects support privacy. |
| Role-scoped notifications | Notifications are tied to recipient IDs and visibility rules. | Prevents cross-role notification leakage. |
| Production config validation | Checks critical env vars in staging/production. | Reduces deployment mistakes. |

## 4. Extra / Standout Features

Core features:

- User support chat.
- KB-grounded troubleshooting.
- Ticket creation and escalation.
- Technician handling.
- Admin management.
- Role-based access.

Extra features:

- Guided answer chips.
- Intent routing for non-support messages.
- Structured issue understanding.
- Role-scoped notifications.
- Ticket audit timeline.
- Reopen flow.
- SLA fields and breach flag.
- Priority and routing group logic.
- Helpfulness feedback.
- KB usage and outcome analytics.
- Admin charts and workload visualization.

Standout features:

- The chatbot knows when to stop and hand off.
- The LLM is assistive, not authoritative.
- Technicians get conversation history and AI attempts.
- Admins can see where AI support works and where KB content needs improvement.
- The system remains understandable and maintainable for a startup MVP.

## 5. How This Is Different

### Different From A Basic Chatbot

A basic chatbot answers messages. AssistIQ runs an operational support workflow. It classifies the issue, collects missing context, retrieves approved KB content, tracks failures, asks for feedback, escalates when appropriate, creates tickets, notifies the right people, and preserves the full history.

### Different From A Normal Ticketing System

A normal ticketing system usually starts with a form and waits for a human. AssistIQ tries to resolve common issues before ticket creation. When it escalates, the ticket already includes category, priority, collected context, conversation history, attempted fixes, and escalation reason.

### Different From A Student Or Demo Project

This project includes production-oriented layers that demo projects often skip: Alembic migrations, RBAC enforced in the backend, role-specific dashboards, audit logs, notifications, knowledge base management, deployment configuration, seeded demo data, test coverage, and fallback behavior when AI is unavailable.

### What Makes It Feel Like A Real Product

- Clear role-specific workflows.
- A modern SaaS-style UI.
- Support operations concepts like priority, SLA, routing, assignment, reopen, and audit timeline.
- Admin analytics that visualize business signals.
- A controlled AI layer with deterministic business rules.
- Demo-ready seed data and deployment-ready configuration.

### Strongest Differentiators

- AI support that hands off intelligently.
- KB-grounded answers instead of open-ended hallucination.
- Structured guided troubleshooting that improves data quality.
- Technician-ready escalation context.
- Admin visibility into support and KB performance.

## 6. Full Documentation Draft

### Project Overview

AssistIQ is an AI-assisted IT support platform for employees, technicians, and admins. It helps users resolve common IT issues through guided chat and escalates unresolved or high-risk cases to human support.

### Problem Statement

Internal IT teams spend significant time on repetitive issues such as VPN failures, password problems, WiFi issues, email sync, access errors, browser problems, and device performance complaints. Users often provide incomplete information, and technicians waste time asking for basic context that could have been collected upfront.

### Solution Overview

AssistIQ provides a structured support workflow:

1. A user opens support chat and describes an issue.
2. The system routes the message by intent.
3. For support issues, it classifies the category and extracts context.
4. If details are missing, it asks guided questions.
5. It retrieves approved KB content.
6. It generates or returns bounded troubleshooting steps.
7. The user marks the issue resolved or not resolved.
8. Failed or high-risk issues become technician tickets.
9. Technicians resolve escalated tickets.
10. Admins monitor operations and improve the KB.

### User Roles

User:

- Uses chat support.
- Answers guided questions.
- Receives troubleshooting steps.
- Marks responses as resolved or not resolved.
- Views only their own tickets and conversations.

Technician:

- Views the support queue.
- Opens escalated ticket details.
- Reads conversation history.
- Updates status, priority, notes, and resolution.
- Works from AI-collected context.

Admin:

- Views all users, tickets, and analytics.
- Manages user roles.
- Manages KB articles.
- Updates tickets and assigns technicians.
- Monitors support trends and KB performance.

### Core Workflow

```text
User issue -> intent routing -> classification -> context collection -> KB retrieval
-> grounded troubleshooting -> user feedback -> retry or escalation -> technician ticket
-> resolution -> analytics and KB improvement
```

### Feature Modules

- Auth module: signup, login, JWT token generation, current-user access.
- Chat module: conversations, messages, feedback, guided answers.
- Intelligence module: intent routing, classification, LLM issue understanding, triage.
- Knowledge module: KB seeds, retrieval, usage tracking, admin KB CRUD.
- Escalation module: ticket creation and handoff summary.
- Ticket module: queues, status updates, priority, SLA, reopen, notes.
- Notification module: role-scoped in-app notifications and mock email logs.
- Admin module: analytics, users, tickets, KB management.
- Frontend module: role dashboards, chat UI, ticket UI, charts, responsive layout.

### Tech Stack

Backend:

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic
- JWT authentication
- Azure OpenAI chat completion integration
- Pytest

Frontend:

- React
- Vite
- TypeScript
- TailwindCSS
- Framer Motion
- React Query
- Recharts
- Vitest

Deployment:

- Docker and docker-compose for local
- Render backend support
- Vercel frontend support
- Supabase Postgres support

### Architecture Overview

The backend owns security, workflow state, AI orchestration, ticket rules, notifications, and persistence. The frontend renders role-specific workflows and calls typed API client functions. PostgreSQL stores users, conversations, messages, tickets, KB articles, notifications, audit logs, and feedback.

The AI architecture is intentionally bounded:

- LLM for understanding and wording.
- KB for factual troubleshooting content.
- Deterministic services for business rules.
- Database for workflow state.
- Tests for critical behavior.

### Folder And Module Overview

Backend:

- `app/api/routes`: API endpoints.
- `app/core`: config and security.
- `app/db`: SQLAlchemy session, metadata, init.
- `app/models`: database models.
- `app/schemas`: Pydantic contracts.
- `app/repositories`: database access.
- `app/services`: business logic and AI workflow.
- `app/knowledge`: seed KB content.
- `alembic`: migrations.
- `tests`: backend test suite.

Frontend:

- `src/api`: API client.
- `src/components`: reusable UI, chat, ticket, layout, analytics components.
- `src/contexts`: auth context.
- `src/pages`: role-specific screens.
- `src/types`: API types.

### Database Entities

- `User`: account identity and role.
- `Conversation`: chat session, category, status, triage stage, context, failures.
- `Message`: conversation messages with metadata.
- `Ticket`: escalated support case with status, priority, SLA, notes, assignment.
- `KnowledgeBase`: approved troubleshooting article.
- `AuditLog`: ticket and KB event timeline.
- `Notification`: in-app notification and mock email record.
- `MessageFeedback`: helpfulness feedback for assistant messages.

### Key APIs

Auth:

- `POST /api/auth/signup`
- `POST /api/auth/login`
- `GET /api/auth/me`

Chat:

- `POST /api/chat/conversations`
- `GET /api/chat/conversations`
- `GET /api/chat/conversations/{id}`
- `POST /api/chat/conversations/{id}/messages`
- `POST /api/chat/conversations/{id}/feedback`
- `POST /api/chat/messages/{message_id}/helpfulness`

Tickets:

- `GET /api/tickets/mine`
- `GET /api/tickets/queue`
- `GET /api/tickets/all`
- `GET /api/tickets/{id}`
- `PATCH /api/tickets/{id}`
- `POST /api/tickets/{id}/reopen`

Admin:

- `GET /api/admin/analytics`
- `GET /api/admin/users`
- `PATCH /api/admin/users/{id}/role`
- `GET /api/admin/knowledge-base`
- `POST /api/admin/knowledge-base`
- `PATCH /api/admin/knowledge-base/{id}`
- `DELETE /api/admin/knowledge-base/{id}`

Notifications:

- `GET /api/notifications`
- `PATCH /api/notifications/{id}/read`

### Chatbot And AI Logic

AssistIQ routes messages before support processing. Greetings and irrelevant questions get short redirects. Support requests go through classification, optional LLM issue understanding, triage, KB retrieval, and response generation.

The LLM is used for:

- Understanding messy input.
- Extracting structured issue fields.
- Summarizing technician handoff context.
- Generating user-friendly KB-grounded responses.

The LLM does not control:

- Permissions.
- Ticket lifecycle.
- Role access.
- Escalation rules.
- Admin actions.

### KB And Retrieval Overview

The KB contains realistic enterprise IT support articles across access, password, VPN, WiFi, network, email, device performance, browser, software, printer, and general enterprise scenarios. Retrieval scores active KB articles using category match, secondary category, keywords, phrase hits, title hits, and content hits.

### Escalation Flow

Escalation happens when:

- The user marks two attempts as not resolved.
- No alternate KB path is available.
- The user asks for a human.
- Account lockout or critical business impact is detected.
- Security-sensitive wording is detected.
- The issue remains too ambiguous after clarification.

The ticket includes:

- Title and category.
- Priority and routing group.
- SLA due time.
- Conversation history.
- Technician summary.
- Attempt/failure context.
- Audit events.

### Notification Flow

Notifications are tied to a recipient user ID and filtered by backend visibility rules. Users see their own ticket updates. Technicians see support queue or assigned ticket notifications. Admins see operational notifications such as critical tickets and SLA breaches. Email is currently mock/log based.

### Analytics Overview

Admin analytics include:

- Total users.
- Total tickets.
- Active conversations.
- Escalations.
- Status breakdown.
- Issue categories.
- Clarifications.
- Helpful replies.
- KB failure rate.
- Technician workload.
- KB article outcomes.

### Security Overview

Security is enforced through JWT auth, hashed passwords, backend role dependencies, protected frontend routes, user-owned data checks, role-scoped notifications, and production config validation.

### Setup And Run Summary

Local Docker:

```bash
docker compose up --build
```

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

### Demo-Ready Notes

Use seeded users:

- User: `user@company.com` / `UserPass123!`
- Technician: `tech@company.com` / `TechPass123!`
- Admin: `admin@company.com` / `AdminPass123!`

Best demo categories:

- Login/access issue.
- VPN issue.
- WiFi issue.
- Email sync issue.
- Urgent human escalation.
- Admin analytics.

### Future Improvements

- Real email provider.
- Background queue for notifications and SLA checks.
- WebSockets for live updates.
- Vector search or embeddings.
- SSO integration.
- External ITSM integration.
- Observability and alerting.
- Rate limiting.
- Multi-tenant support.

## 7. Client Presentation Content

### Project Introduction

AssistIQ is an AI-assisted IT support platform designed to reduce repetitive support workload while keeping human technicians in control when issues need escalation.

### Business Pain Point

IT support teams often receive incomplete tickets like "VPN not working" or "cannot login." Technicians spend time collecting basic details, while employees wait for help on issues that could often be resolved with approved steps.

### Why This Solution Matters

AssistIQ improves the first support interaction. It collects context, suggests safe fixes, tracks failed attempts, and escalates with a complete handoff when needed.

### Key Capabilities

- Guided AI support chat.
- Approved KB troubleshooting.
- Automatic escalation after failed attempts.
- Urgent and security-sensitive issue escalation.
- Technician-ready ticket context.
- Admin analytics and KB management.
- Role-based workflows for users, technicians, and admins.

### Business Benefits

- Reduces repetitive technician work.
- Improves employee response time.
- Makes escalations more useful.
- Shows where the KB needs improvement.
- Gives admins visibility into support operations.
- Keeps AI bounded and controlled.

### What The Client Can Expect

In a pilot, clients can test employee issue reporting, guided troubleshooting, escalation, technician ticket handling, admin analytics, and KB maintenance.

### How It Reduces Support Effort

AssistIQ resolves common issues through approved steps and only creates tickets when the user needs human help. When tickets are created, technicians receive the conversation history and attempted steps, reducing back-and-forth.

### How It Improves User Experience

Employees get an immediate response, guided questions instead of long forms, clear next steps, and visibility into ticket progress after escalation.

## 8. Perfect Demo Script

### Short Demo Script: 3 To 5 Minutes

1. Open the app and introduce AssistIQ.
   - Say: "This is an AI-assisted IT support platform. It is designed to solve common issues quickly and escalate the rest with context."

2. Login as the user.
   - Show the user dashboard and support chat.
   - Say: "The user experience is intentionally simple. Employees do not need to know the category. They just describe what is wrong."

3. Type: `having problem logging in`
   - Show guided options.
   - Say: "The system asks structured follow-up questions, so it can collect useful context without forcing users to write long explanations."

4. Type or select a clear support path, such as VPN or Company Portal.
   - Show the AI response or clarification.
   - Say: "The answer is grounded in the knowledge base, not an open-ended chatbot response."

5. Mark Not Resolved twice or use: `connect me to a human now`
   - Show escalation and ticket creation.
   - Say: "The important part is that the assistant knows when to stop. Failed attempts become technician-ready tickets."

6. Login as technician.
   - Open the ticket.
   - Show conversation history, priority, SLA, routing, notes, and resolution update.
   - Say: "The technician can continue from the context already collected."

7. Login as admin.
   - Show analytics and KB management.
   - Say: "Admins can monitor common categories, escalations, workload, and KB performance."

8. Close.
   - Say: "AssistIQ is not replacing the support team. It is reducing repetitive work and improving handoff quality."

### Full Demo Script: 8 To 12 Minutes

1. Opening
   - "Most IT support tickets start with vague messages. AssistIQ turns those messages into a guided support workflow."

2. User dashboard
   - Show active tickets, resolved tickets, and chat sessions.
   - Explain that this is the employee-facing view.

3. Guided chat
   - Type: `vpn not working`
   - Show category badge and guided options.
   - Select a VPN option.
   - Explain structured triage context.

4. KB-grounded response
   - Show the assistant response and KB-driven steps.
   - Explain that the LLM, when configured, uses KB context and does not own business rules.

5. Feedback loop
   - Click Not Resolved.
   - Show second attempt or escalation logic.
   - Explain failed attempt tracking.

6. Immediate escalation scenario
   - Start a new conversation or use a fast scenario: `security issue, suspicious login detected`
   - Show immediate escalation.
   - Explain rule-based escalation for high-risk issues.

7. User ticket history
   - Go to My Tickets.
   - Show status, priority, and ticket details.

8. Technician workflow
   - Login as technician.
   - Show ticket queue.
   - Open ticket.
   - Show full conversation history and operational panel.
   - Update status to `IN_PROGRESS`.
   - Add internal notes and resolution.
   - Save update.
   - Explain audit and notification behavior.

9. Admin workflow
   - Login as admin.
   - Show visual analytics dashboard.
   - Show ticket overview.
   - Show user management.
   - Show KB management.
   - Explain how admins use analytics to improve support quality.

10. Closing
   - "The value is the combination of AI intake, approved knowledge, deterministic escalation, and operational visibility."

### Presenter Notes

- Emphasize "AI-assisted workflow," not "general chatbot."
- Keep the demo focused on business value.
- Use one ordinary issue and one urgent issue.
- Show that humans remain in control.
- Avoid promising integrations that are not implemented.
- If the AI response varies, explain that workflow rules remain stable.

## 9. Best Test Scenarios

### Top 10 Showcase Scenarios

| Scenario | User Input | Expected Behavior | Why It Is Impressive |
| --- | --- | --- | --- |
| Greeting | `hi` | Polite redirect to IT support. | Shows intent routing. |
| Vague login | `having problem logging in` | Access/login classification and contextual options. | Shows guided troubleshooting. |
| VPN issue | `vpn not working` | VPN category and VPN-specific options. | Shows category-aware flow. |
| WiFi issue | `wifi not working` | WiFi category and network troubleshooting. | Common real-world issue. |
| Email sync | `outlook not syncing` | Email category and KB-backed help. | Shows non-technical phrasing support. |
| Password reset | `forgot password` | Password category and guided questions or KB help. | Common support deflection case. |
| Account locked | `my account is locked` | Immediate escalation. | Shows safety handoff. |
| Human request | `connect me to a human now` | Escalates if context exists, otherwise redirects calmly. | Shows frustration handling. |
| Security issue | `security issue, suspicious login detected` | Critical escalation and ticket. | Shows high-risk handling. |
| Technician resolution | Update ticket to `RESOLVED` with notes. | User gets status update and audit logs. | Shows end-to-end workflow. |

### Top 20 QA And Demo Scenarios

| # | Input Or Action | Expected System Behavior |
| --- | --- | --- |
| 1 | `hello, what can you do?` | Small-talk answer plus IT support redirect. |
| 2 | `tell me a joke` | Polite refusal and support redirect. |
| 3 | Empty message or random text | Ask for clearer IT issue details. |
| 4 | `vpn conection not wrking` | VPN classification despite typo. |
| 5 | `vpn connected but internal sites not opening` | VPN/internal resource troubleshooting. |
| 6 | `vpn disconnecting every few minutes` | VPN disconnect scenario retrieval. |
| 7 | `connected but no internet` | Network/WiFi troubleshooting path. |
| 8 | `ubuntu wifi networks not showing` | WiFi category and no-network visibility KB. |
| 9 | `not receiving emails since morning` | Email retrieval and support steps. |
| 10 | `cannot send mail` | Email send scope troubleshooting. |
| 11 | `laptop very slow` | Device performance category and KB help. |
| 12 | `system hangs again and again` | Device performance classification. |
| 13 | `app crashing on startup` | Software issue classification. |
| 14 | `internal website not opening` | Browser/network/VPN handling. |
| 15 | `hr portal not loading` | Access/browser support path. |
| 16 | `company app install failed` | Software install KB support. |
| 17 | `i cannot work, please help urgently` | Critical or high-priority escalation. |
| 18 | `my account is locked and i need payroll access` | Immediate escalation with access/payroll context. |
| 19 | Mark Not Resolved twice | Ticket created automatically. |
| 20 | Admin edits KB article | KB update persists and audit entry is recorded. |

## 10. Interview Architecture Explanation

### Simple Explanation

AssistIQ is a full-stack IT support platform. The frontend gives each role a dedicated workflow. The backend handles authentication, chat, AI-assisted triage, KB retrieval, escalation, tickets, notifications, and analytics. PostgreSQL stores all workflow state. The LLM helps understand and word responses, but deterministic services control ticketing and permissions.

### Strong Interview Answer

I designed AssistIQ as a bounded AI workflow rather than a free-form chatbot. The key design decision was separating AI reasoning from business authority. The LLM can interpret vague user input and generate KB-grounded language, but it cannot decide permissions, status transitions, or escalation rules. Those are deterministic and covered by tests.

The flow starts with intent routing, then classification and optional Azure OpenAI issue understanding. Triage uses diagnostic playbooks to collect missing context through guided options. Retrieval selects approved KB articles using category and keyword/phrase scoring. The response generator uses the KB context when Azure OpenAI is configured, otherwise deterministic fallback text is used. If the user fails twice, asks for a human, reports a lockout, or uses urgent/security-sensitive wording, the escalation service creates a ticket with priority, routing group, SLA, audit logs, notifications, and full conversation history.

The frontend is role-driven: users get chat and ticket tracking, technicians get queue/detail/update screens, and admins get management plus analytics. The backend enforces RBAC, so access is not dependent on frontend routing alone.

### Concise Elevator Explanation

AssistIQ is a production-oriented AI IT support MVP. It uses AI for issue understanding and KB-grounded responses, deterministic rules for escalation and ticketing, and role-based dashboards for users, technicians, and admins. The result is not just chat, but a complete support workflow from intake to resolution.

### Why This Architecture Was Chosen

- FastAPI keeps API development simple and typed.
- PostgreSQL and SQLAlchemy provide durable relational workflow state.
- Alembic supports real schema migrations.
- React/Vite/TypeScript gives a fast frontend with typed API contracts.
- React Query simplifies async server state.
- Tailwind and Framer Motion support polished UI without heavy custom CSS.
- Recharts makes admin analytics understandable.
- Azure OpenAI is optional, so the app can still operate without AI availability.

### How AI Is Used Safely

- LLM output for issue understanding is schema-validated.
- Invalid LLM output falls back to deterministic logic.
- Support responses are generated from retrieved KB context.
- The LLM does not update tickets or control roles.
- Escalation is deterministic.
- Security-sensitive issues trigger human review.

### How Hallucination Risk Is Reduced

- Retrieval happens before response generation.
- Prompts restrict answers to KB context.
- Deterministic fallback exists.
- KB titles and IDs are stored in message metadata.
- Admins can update and disable KB articles.
- The system escalates when confidence or coverage is weak.

### How Role-Based Flows Work

- Frontend routes are protected by role.
- Backend routes use role dependencies.
- User access is scoped to own conversations and tickets.
- Technician/admin routes use support roles.
- Admin-only endpoints manage users and KB.
- Notifications are filtered by recipient and visibility rules.

### How Workflow State Is Managed

Conversation state stores category, status, triage stage, collected context, last triage metadata, failure count, and escalation summary. Messages store content plus metadata such as KB articles, confidence, and guided question data. Tickets store status, priority, routing, SLA, assignee, notes, resolution, reopen count, and audit logs.

### What Makes It Production-Oriented

- Real database persistence.
- Alembic migrations.
- Backend RBAC.
- Deployment env validation.
- Docker and hosted deployment config.
- Health endpoint.
- Test coverage across auth, chat, escalation, operations, notifications, and scenarios.
- Deterministic fallbacks around AI.
- Audit and analytics for operations.

## 11. Presentation Tips

### How To Impress A Client

- Start with the support pain point, not the technology.
- Show a vague issue first, because that is realistic.
- Show guided chips to make the product feel interactive.
- Show escalation to prove the system does not trap users in AI.
- Show technician context to demonstrate operational value.
- End with admin analytics to show continuous improvement.

### How To Present It As A Product

Say:

- "This is an AI-assisted support workflow."
- "The system uses approved KB content."
- "The assistant escalates when confidence or resolution fails."
- "Technicians receive context, not just a blank ticket."
- "Admins can monitor categories, workload, and KB performance."

Avoid saying:

- "It is just a chatbot."
- "The AI can answer anything."
- "The AI decides everything."
- "It is fully enterprise-ready."
- "It has real email, vector DB, SSO, or ServiceNow integration" unless those are added later.

### Handling Tough Questions

Question: "Can it hallucinate?"

Answer: "The design reduces that risk by grounding responses in approved KB articles and keeping business rules deterministic. If the LLM fails or returns invalid structured output, the system falls back to deterministic behavior."

Question: "Can it replace technicians?"

Answer: "No. It is designed to reduce repetitive work and improve handoffs. Technicians still handle escalations, critical cases, and cases where the KB is not enough."

Question: "Is it production-ready?"

Answer: "It is ready as a strong MVP or pilot system. For enterprise production, I would add real email delivery, observability, rate limiting, security review, backups, and load testing."

Question: "Why not use a vector database?"

Answer: "For this MVP, keyword and phrase retrieval is simpler, explainable, and enough for a controlled KB. The architecture is RAG-ready, so embeddings and vector search can be added when KB scale justifies it."

Question: "What happens if OpenAI is down?"

Answer: "The system has deterministic fallback classification and responses, so core support workflow continues without the LLM."

## 12. Known Limitations / Safe Claims

### Safe Claims

- "AssistIQ is a full-stack AI-assisted IT support MVP."
- "It supports user, technician, and admin workflows."
- "It uses Azure OpenAI when configured for issue understanding and KB-grounded responses."
- "It keeps escalation, permissions, and ticket lifecycle deterministic."
- "It includes guided troubleshooting and contextual answer options."
- "It includes KB management and analytics."
- "It is deployable with Vercel, Render, and Supabase."
- "It is suitable for demo and pilot evaluation."

### Limitations To Disclose Honestly

- Real SMTP/email delivery is not implemented.
- WebSocket real-time updates are not implemented.
- Vector search is not implemented.
- Automatic technician assignment by workload is not fully implemented.
- SLA breach checking is not continuously scheduled in the background.
- There is no external ITSM integration yet.
- There is no enterprise SSO yet.
- There is no full observability stack yet.
- Production security hardening would be required before a real enterprise rollout.

### Final Positioning Verdict

AssistIQ is a strong pilot-ready AI IT support MVP. It is more complete than a demo chatbot because it includes real support operations: RBAC, ticketing, escalation, KB management, guided troubleshooting, role-scoped notifications, audit logs, and admin analytics. It should be presented as a practical startup-grade product foundation, with a clear roadmap for enterprise hardening.
