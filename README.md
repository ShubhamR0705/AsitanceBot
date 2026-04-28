# AssistIQ - AI IT Support Chatbot MVP

AssistIQ is a production-oriented MVP for AI-assisted IT support. Users describe IT issues in chat, the backend classifies the issue, retrieves approved knowledge base content, returns bounded troubleshooting steps, and escalates to a human technician after two failed attempts.

## What Is Included

- FastAPI backend with PostgreSQL, SQLAlchemy, Alembic, Pydantic, JWT auth, password hashing, and role-based access control.
- React + Vite + TypeScript frontend with TailwindCSS, Framer Motion, React Query, protected routes, and responsive role dashboards.
- Exactly three roles: `USER`, `TECHNICIAN`, and `ADMIN`.
- Knowledge base seed data for VPN, password reset, WiFi, email, access, browser, printer, network, software, and device performance issues.
- Optional Azure OpenAI intelligence layer for structured issue understanding, grounded responses, and technician summaries.
- Category-specific diagnostic playbooks that collect missing context before suggesting fixes.
- Technician-ready escalation summaries with collected facts and missing information.
- Smart deterministic escalation for lockouts, urgent/security-sensitive issues, explicit human requests, low-confidence ambiguity, and two unresolved AI attempts.
- Operational support layer with priority, SLA targets, assignment, routing groups, notifications, audit timeline, reopen flow, KB usage, and helpfulness feedback.
- Dockerfiles and `docker-compose.yml` for local deployment.
- Backend pytest coverage for auth, chat escalation, ticket creation, operational workflows, and ticket updates.
- Minimal frontend component tests.

## Architecture

```text
backend/
  app/
    api/routes/          HTTP routes for auth, chat, tickets, admin
    core/                settings and security
    db/                  SQLAlchemy engine, base metadata, seed bootstrap
    knowledge/           seed knowledge base content
    models/              User, Conversation, Message, Ticket, KnowledgeBase
    repositories/        database access layer
    schemas/             Pydantic request/response contracts
    services/            issue understanding, classification, KB retrieval, chat, escalation, tickets
    main.py              FastAPI application
  alembic/               migration environment and initial schema
  tests/                 pytest API tests

frontend/
  src/
    api/                 typed API client
    components/          reusable layout, chat, tickets, and UI components
    contexts/            authentication context
    pages/               role-specific screens
    types/               API types
```

## Database Schema

- `users`: account, hashed password, role, active flag.
- `conversations`: user chat sessions, category, status, triage stage, structured context, unresolved failure count, and escalation summary.
- `messages`: user, assistant, technician, and system messages with metadata for KB articles, confidence, urgency, and handoff context.
- `tickets`: escalated support cases with status, priority, routing group, SLA target, notes, resolution, technician assignment, and reopen tracking.
- `knowledge_base`: approved troubleshooting content, keywords, active flag, and usage count.
- `audit_logs`: ticket and KB operational events with previous/new values.
- `notifications`: in-app notifications plus mock email logging.
- `message_feedback`: helpful/not-helpful feedback linked to assistant messages.

Ticket statuses:

```text
OPEN -> ESCALATED -> IN_PROGRESS -> WAITING_FOR_USER -> RESOLVED -> CLOSED
                         ^                                      |
                         |-------------- REOPENED --------------|
```

## API Overview

Base URL: `http://localhost:8000/api`

Auth:

- `POST /auth/signup`
- `POST /auth/login`
- `GET /auth/me`

User chat:

- `POST /chat/conversations`
- `GET /chat/conversations`
- `GET /chat/conversations/{id}`
- `POST /chat/conversations/{id}/messages`
- `POST /chat/conversations/{id}/feedback`
- `POST /chat/messages/{message_id}/helpfulness`

Tickets:

- `GET /tickets/mine`
- `GET /tickets/queue`
- `GET /tickets/all`
- `GET /tickets/{id}`
- `PATCH /tickets/{id}`
- `POST /tickets/{id}/reopen`

Notifications:

- `GET /notifications`
- `PATCH /notifications/{id}/read`

Admin:

- `GET /admin/analytics`
- `GET /admin/users`
- `PATCH /admin/users/{id}/role`
- `GET /admin/knowledge-base`
- `POST /admin/knowledge-base`
- `PATCH /admin/knowledge-base/{id}`
- `DELETE /admin/knowledge-base/{id}`

Health:

- `GET /health`

## Run With Docker

```bash
docker compose up --build
```

Services:

- Frontend: `http://localhost:8088`
- Backend API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- PostgreSQL: `localhost:55432`

The backend container runs `alembic upgrade head` on startup, then starts FastAPI.

If you are upgrading an existing local database that was created before migrations were stamped, run:

```bash
docker compose run --rm backend alembic stamp 0001_initial
docker compose run --rm backend alembic upgrade head
```

Seeded demo accounts:

| Role | Email | Password |
| --- | --- | --- |
| User | `user@company.com` | `UserPass123!` |
| Technician | `tech@company.com` | `TechPass123!` |
| Admin | `admin@company.com` | `AdminPass123!` |

## Local Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

The backend can auto-create tables and seed demo data when `AUTO_CREATE_TABLES=true`.

Alembic is included for managed schema changes:

```bash
cd backend
alembic upgrade head
```

## Local Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Frontend dev URL: `http://localhost:5173`

## Environment Variables

Backend:

- `APP_NAME`
- `ENVIRONMENT`
- `DATABASE_URL`
- `DATABASE_SSL_MODE`
- `SECRET_KEY`
- `CORS_ORIGINS`
- `CORS_ORIGIN_REGEX`
- `AUTO_CREATE_TABLES`
- `SEED_DEMO_DATA`
- `DEMO_ADMIN_EMAIL`
- `DEMO_ADMIN_PASSWORD`
- `DEMO_TECHNICIAN_EMAIL`
- `DEMO_TECHNICIAN_PASSWORD`
- `DEMO_USER_EMAIL`
- `DEMO_USER_PASSWORD`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_DEPLOYMENT`
- `AZURE_OPENAI_API_VERSION`
- `AZURE_OPENAI_TIMEOUT_SECONDS`
- `AZURE_OPENAI_MAX_COMPLETION_TOKENS`
- `AZURE_OPENAI_TEMPERATURE`

Frontend:

- `VITE_API_URL`

## Public Deployment: Render + Supabase + Vercel

This repo is prepared for free-tier friendly staging with:

- Backend: Render Python web service from `backend/`
- Database: Supabase Postgres
- Frontend: Vercel static Vite build from `frontend/`

Docker is still useful locally, but the hosted deployment should use native Render and Vercel builds because they are simpler for this project.

### Deployment Readiness Report

- Frontend root path: `frontend`
- Backend root path: `backend`
- Backend entrypoint: `app.main:app`
- Backend start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Backend health endpoint: `/health`
- Frontend build command: `npm run build`
- Frontend output directory: `dist`
- Database migrations: `alembic upgrade head`
- Demo seed command: `python scripts/seed_demo.py`
- Frontend API env: `VITE_API_URL=https://your-render-service.onrender.com/api`
- Backend CORS env: set `CORS_ORIGINS` to your Vercel URL. `CORS_ORIGIN_REGEX=https://.*\.vercel\.app` is included for Vercel preview URLs.

Deployment fixes included:

- `render.yaml` for Render Blueprint deployment.
- `frontend/vercel.json` for Vercel SPA routing and Vite build settings.
- Supabase-compatible database URL normalization. The backend accepts Supabase `postgresql://` or `postgres://` URLs and uses SQLAlchemy with the installed `psycopg` driver.
- Optional `DATABASE_SSL_MODE=require` for hosted Postgres.
- Production config validation for missing `SECRET_KEY`, localhost `DATABASE_URL`, and missing frontend CORS.
- Idempotent demo seed script for users, KB, tickets, notifications, audits, and analytics data.
- Deployment check script for env, DB connectivity, seed data, and optional public health validation.

### Supabase Setup

1. Create a Supabase project.
2. Open Project Settings -> Database -> Connect.
3. Copy a Postgres connection string.
4. For Render free-tier compatibility, prefer the Supabase session pooler connection if direct IPv6 connectivity is unavailable.
5. Replace `[YOUR-PASSWORD]` with the database password.
6. Use that value as Render `DATABASE_URL`.
7. Set `DATABASE_SSL_MODE=require`.

Example accepted formats:

```text
postgresql://postgres.project-ref:password@aws-0-region.pooler.supabase.com:5432/postgres
postgres://postgres.project-ref:password@aws-0-region.pooler.supabase.com:5432/postgres
postgresql+psycopg://postgres.project-ref:password@aws-0-region.pooler.supabase.com:5432/postgres
```

### Render Backend Setup

Preferred path: create a Render Blueprint from this repository. Render will read `render.yaml`.

Manual settings if you do not use Blueprint:

```text
Service type: Web Service
Runtime: Python
Root Directory: backend
Build Command: pip install -r requirements.txt
Pre-Deploy Command: alembic upgrade head && python scripts/seed_demo.py
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
Health Check Path: /health
```

Required Render environment variables:

```env
APP_NAME=AssistIQ
ENVIRONMENT=production
DATABASE_URL=<supabase-postgres-url>
DATABASE_SSL_MODE=require
SECRET_KEY=<stable-random-64-character-secret>
CORS_ORIGINS=https://your-vercel-app.vercel.app
CORS_ORIGIN_REGEX=https://.*\.vercel\.app
AUTO_CREATE_TABLES=false
SEED_DEMO_DATA=false
AZURE_OPENAI_API_KEY=<your-azure-openai-key>
AZURE_OPENAI_ENDPOINT=https://aaif-codebridge-llm.cognitiveservices.azure.com/
AZURE_OPENAI_DEPLOYMENT=codeBridge-gtp5-chat
AZURE_OPENAI_API_VERSION=2025-01-01-preview
AZURE_OPENAI_TIMEOUT_SECONDS=15
AZURE_OPENAI_MAX_COMPLETION_TOKENS=700
AZURE_OPENAI_TEMPERATURE=
DEMO_ADMIN_EMAIL=admin@company.com
DEMO_ADMIN_PASSWORD=AdminPass123!
DEMO_TECHNICIAN_EMAIL=tech@company.com
DEMO_TECHNICIAN_PASSWORD=TechPass123!
DEMO_USER_EMAIL=user@company.com
DEMO_USER_PASSWORD=UserPass123!
```

After backend deploy, verify:

```bash
curl https://your-render-service.onrender.com/health
```

Expected response:

```json
{"status":"ok"}
```

### Vercel Frontend Setup

Import the same GitHub repository into Vercel and use:

```text
Framework Preset: Vite
Root Directory: frontend
Install Command: npm ci
Build Command: npm run build
Output Directory: dist
```

Required Vercel environment variable:

```env
VITE_API_URL=https://your-render-service.onrender.com/api
```

After Vercel gives you the frontend URL, update Render `CORS_ORIGINS` with that exact URL and redeploy the backend if needed.

### Migrations, Seeds, and Checks

Render runs this automatically through `render.yaml`:

```bash
cd backend
alembic upgrade head
python scripts/seed_demo.py
```

You can also run the deployment check from the backend service shell:

```bash
cd backend
BACKEND_HEALTH_URL=https://your-render-service.onrender.com/health python scripts/check_deploy.py
```

The demo seed is idempotent. It creates or verifies:

- `user@company.com` / `UserPass123!`
- `tech@company.com` / `TechPass123!`
- `admin@company.com` / `AdminPass123!`
- Rich knowledge base entries.
- Sample escalated, in-progress, waiting, resolved, and SLA-breached tickets.
- Audit logs, in-app notifications, message feedback, and analytics data.

### Client Demo Flow

1. Share the Vercel frontend URL.
2. Log in as `user@company.com` to test chat, guided troubleshooting, ticket history, and reopen flow.
3. Log in as `tech@company.com` to test assigned tickets, queue, audit timeline, notes, and status updates.
4. Log in as `admin@company.com` to test all tickets, analytics, user roles, and KB management.

### Final Step-by-Step Deployment Guide

1. Push the repository to GitHub.
2. Create a Supabase project and copy the Postgres connection string.
3. Create a Render Blueprint or Python web service for `backend`.
4. Set Render env vars, especially `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`, and `AZURE_OPENAI_API_KEY`.
5. Let Render run `alembic upgrade head && python scripts/seed_demo.py`.
6. Confirm `https://your-render-service.onrender.com/health` returns `{"status":"ok"}`.
7. Create a Vercel project for `frontend`.
8. Set `VITE_API_URL=https://your-render-service.onrender.com/api`.
9. Deploy Vercel.
10. Update Render `CORS_ORIGINS` with the final Vercel URL.
11. Open the Vercel URL and test the three demo accounts.

## Tests

Backend:

```bash
cd backend
pytest
```

Frontend:

```bash
cd frontend
npm test
```

## Core User Flow

1. User logs in and opens Support Chat.
2. User submits an issue, such as "VPN is not connecting".
3. Backend classifies the issue and starts category-specific triage.
4. If key details are missing, the assistant asks targeted clarifying questions first.
5. Backend retrieves relevant KB entries and generates a grounded troubleshooting response.
6. User marks `Resolved` or `Not Resolved`.
7. First unresolved response triggers one more guided attempt.
8. Second unresolved response creates an escalated ticket with a technician-ready summary.
9. Technician opens the queue, reads the full conversation and collected facts, updates status, and adds notes or resolution.
10. Admin monitors users, tickets, analytics, and the knowledge base.

## Operational Layer

Tickets now behave more like a real IT support queue:

- Priority levels: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`.
- Priority is auto-detected from urgency, business impact, security wording, and category.
- SLA due dates are generated from priority: `CRITICAL` in 2 hours, `HIGH` in 8 hours, `MEDIUM` in 24 hours, and `LOW` in 72 hours.
- Tickets track `first_response_at`, `sla_due_at`, `sla_breached`, `routing_group`, `reopen_count`, and `last_reopened_at`.
- Routing groups are simple and transparent: VPN/WiFi route to network, password to access, email to communication, device performance to endpoint, and unknown issues to general.
- Technicians can self-assign by updating a ticket. Admins can manually assign technicians.
- Users can reopen resolved or closed tickets while preserving the existing history.

Audit events are stored for ticket creation, escalation, assignment, status changes, priority changes, notes, resolution updates, reopen events, SLA breach events, and KB create/update/delete actions.

Notifications are stored in-app and mock email notifications are logged by the backend. The UI includes a notification panel in the app header.

The feedback loop tracks KB article usage, KB outcomes by resolved/escalated conversation, helpful/not-helpful feedback on assistant messages, and escalation after KB suggestions.

## Chatbot Intelligence Layer

AssistIQ uses a controlled LLM-assisted architecture:

- Azure OpenAI helps interpret vague, typo-heavy, and non-technical IT issues into structured fields.
- Pydantic validates the structured output before business logic uses it.
- Deterministic fallback classification runs when Azure OpenAI is not configured, fails, or returns malformed output.
- KB retrieval uses the user text, issue summary, secondary category, and collected context to rank approved articles.
- Response generation is grounded only in retrieved KB context.
- Escalation, ticket creation, role permissions, and ticket status changes stay deterministic.

Structured understanding fields include:

- `primary_category`
- `secondary_category`
- `confidence_score`
- `missing_slots`
- `urgency_level`
- `urgency_signals`
- `user_intent`
- `short_issue_summary`
- `recommended_next_action`
- `explicit_human_requested`
- `security_sensitive`
- `business_impact`

Immediate deterministic escalation is triggered for:

- explicit human support requests
- critical urgency or business impact
- security-sensitive wording
- account lockout signals
- unresolved low-confidence ambiguity after clarification
- two failed troubleshooting attempts
- no meaningfully different approved KB path for a retry

Admin analytics now include low-confidence conversations, clarification volume, conversation stages, urgency trends, escalation reasons, KB article usage/outcomes, and technician workload.

## Diagnostic Playbooks

The chatbot now tracks structured triage context on each conversation:

- `triage_stage`: `INTAKE`, `CLARIFYING`, `SUGGESTING_FIX`, `WAITING_FOR_FEEDBACK`, `RESOLVED`, or `ESCALATED`.
- `collected_context`: detected details such as OS, error message, MFA status, webmail status, business impact, or affected app.
- `last_triage`: latest triage action, missing fields, questions, confidence, and reason.
- `escalation_summary`: technician handoff summary generated before ticket creation.

Supported playbooks:

- VPN
- Password/account access
- WiFi
- Email
- Device performance
- General IT issue

The assistant does not show `Resolved` / `Not Resolved` actions while it is still asking clarifying questions. This prevents false failure tracking before enough diagnostic context exists.

## Azure OpenAI Intelligence Layer

By default, AssistIQ uses deterministic classification, retrieval, and response text when no Azure OpenAI key is configured. To enable OpenAI-assisted understanding and response generation, add your key to the root `.env` file:

```env
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_DEPLOYMENT=
AZURE_OPENAI_API_VERSION=
```

The backend builds this chat-completions URL internally:

```text
{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_OPENAI_DEPLOYMENT}/chat/completions?api-version={AZURE_OPENAI_API_VERSION}
```

The Azure OpenAI integration is used for:

- structured issue understanding
- concise KB-grounded support responses
- technician handoff summaries

The integration is not allowed to directly control authorization, role behavior, ticket lifecycle, or escalation state. Those remain deterministic backend rules. If the model output is invalid, unavailable, or low confidence, the backend falls back to deterministic behavior.

For Docker, either export the variables before starting Compose:

```bash
export AZURE_OPENAI_API_KEY=your-key-here
export AZURE_OPENAI_ENDPOINT=
export AZURE_OPENAI_DEPLOYMENT=
export AZURE_OPENAI_
docker compose up --build -d
```

Or create a root `.env` file with the same variables. Do not put API keys in frontend env files.

## Design System

The frontend uses a clean SaaS design system:

- Brand accent: teal.
- Secondary accent: rose.
- Neutral layered backgrounds: base, surface, elevated.
- Status colors: green success, yellow warning, red error, blue info.
- Components: buttons, inputs, cards, badges, skeletons, sidebar, chat bubbles, ticket lists, stat cards.
- Motion: subtle page transitions, hover/press states, list entry animations, typing indicator, and dashboard count-up stats.
