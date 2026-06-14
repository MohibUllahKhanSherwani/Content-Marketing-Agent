# Content Marketing Agent Team

This project will become a production-grade CrewAI agent system for Roman Khaliq's Content Marketing Agent role from Agent Talent.

The agent team creates and manages multi-channel marketing content: blog posts, email campaigns, social posts, ad copy, landing-page copy, case studies, content calendars, approval workflows, publishing integrations, and monthly performance analysis.

The immediate goal is to support an AgentTalent.ai application/proposal with a credible working demo, then evolve into a production-capable agency content operations system.

## Current Decisions

- **Framework:** CrewAI with Flows as the top-level orchestrator and specialist Crews for strategy, production, QA, distribution, and analytics.
- **LLM provider:** Gemini API.
- **Primary model:** `gemini/gemini-1.5-flash` for high-volume generation and extraction.
- **Review model:** `gemini/gemini-1.5-pro` for final strategic and quality checks.
- **Integrations:** WordPress, HubSpot, LinkedIn, Meta, GA4, and optional web search.
- **Demo mode:** Hybrid. Use real services where credentials and access exist; otherwise use realistic mocks.
- **Approval:** Human approval is mandatory before any real publishing.

## Quickstart

```bash
uv sync --extra dev
cp .env.example .env
uv run cma hello
uv run cma connectors
uv run uvicorn content_marketing_agent.api:app --reload
```

The default connector behavior is safe for demos: Gemini API is real when configured, and external platforms use `auto` mode with mock fallback.

## Fullstack Getting Started (Backend + Frontend)

### 1) Install backend dependencies

```bash
uv sync --extra dev
```

### 2) Configure environment

```bash
cp .env.example .env
```

For local safe demo mode, keep external connectors in `auto` and do not enable `ALLOW_REAL_PUBLISH`.

### 3) Start backend API

```bash
uv run uvicorn content_marketing_agent.api:app --reload
```

Backend base URL:
- `http://127.0.0.1:8000`
- OpenAPI docs: `http://127.0.0.1:8000/docs`

### 4) Install frontend dependencies

```bash
cd frontend
npm install
```

### 5) Start frontend dashboard

```bash
cd frontend
npm run dev
```

Frontend base URL:
- `http://127.0.0.1:5173`

If needed, set API base explicitly:

```bash
# PowerShell
$env:VITE_API_BASE_URL="http://127.0.0.1:8000"
npm run dev
```

### 6) Frontend test/lint/build

```bash
cd frontend
npm test
npm run lint
npm run build
```

### 7) Frontend routes

- `/review-queue`
- `/publication-audit`
- `/campaign-workspace`
- `/calendar`
- `/connectors`
- `/telemetry`
  - run budget visibility and campaign telemetry drilldown

## Playwright E2E

E2E spec and config are included under `frontend/e2e/` and `frontend/playwright.config.ts`.

Install browser binaries (first run only):

```bash
cd frontend
npx playwright install chromium
```

Run E2E:

```bash
cd frontend
npm run test:e2e
```

Note: browser download can take time depending on network. The Playwright config uses an increased `webServer.timeout` to reduce startup flakiness.

## Implemented Demo Endpoints

The current FastAPI app already supports a local review-and-distribution loop:

- `GET /health`
- `GET /health/llm`
- `GET /connectors`
- `GET /connectors/diagnostics`
- `GET /calendar/demo`
- `POST /demo/seed`
- `POST /client-profiles`
- `GET /client-profiles/{id}`
- `POST /campaigns`
- `GET /campaigns/{id}`
- `GET /campaigns/{id}/content-items`
- `GET /campaigns/{id}/telemetry-summary`
- `GET /content-items`
- `GET /content-items/{id}`
- `POST /content-items/{id}/approve`
- `POST /content-items/{id}/request-changes`
- `POST /content-items/{id}/publish-draft`
- `POST /content-items/{id}/publish`
- `GET /content-items/{id}/publications`
- `GET /content-items/{id}/approval-decisions`
- `POST /runs/monthly-plan`
- `POST /runs/produce-content`
- `POST /runs/monthly-analytics`
- `POST /runs/monthly-flow`
- `POST /runs/integration-smoke`
- `GET /runs/telemetry`
- `GET /runs/telemetry/summary`
- `GET /analytics/monthly-summary`

## Operator CLI

```bash
uv run cma monthly-plan --month 2026-07 --blog-posts 8
uv run cma produce --objective "Increase inbound demos" --items-per-channel 1
uv run cma monthly-analytics
uv run cma connector-diagnostics
uv run cma integration-smoke
uv run cma wp-draft-smoke
```

## Credentials Needed For Full Real Mode

- Gemini API:
  - `GEMINI_API_KEY` — your Google AI Studio or Vertex AI API key
  - `CONTENT_AGENT_MODEL` — model for drafting/extraction (e.g. `gemini/gemini-1.5-flash`)
  - `CONTENT_AGENT_REVIEW_MODEL` — model for review/strategy (e.g. `gemini/gemini-1.5-pro`)
  - Models follow the `provider/model-name` format. See `.env.example` for the full list of options.
- WordPress (real draft creation):
  - `WORDPRESS_BASE_URL`
  - `WORDPRESS_USERNAME`
  - `WORDPRESS_APP_PASSWORD`
- HubSpot (real email draft creation):
  - `HUBSPOT_PRIVATE_APP_TOKEN`
- GA4 (real read-only analytics):
  - `GA4_PROPERTY_ID`
  - `GOOGLE_APPLICATION_CREDENTIALS` (service account JSON path)

## When Real Credentials Are Required

No real credentials are required for:

- backend feature development
- frontend feature development
- backend unit tests
- frontend unit tests
- mock/auto demo flows

Real credentials are required for:

- validating Gemini generation quality in real mode (`GEMINI_API_KEY`)
- validating real WordPress draft creation
- validating real HubSpot draft creation
- validating real GA4 read-only analytics
- any intentional public publishing path (also requires `ALLOW_REAL_PUBLISH=true`)

## Success Criteria

- Produce 8-12 blog posts monthly.
- Produce weekly email campaigns.
- Produce daily social posts.
- Produce ad copy variations, landing-page copy, and case studies.
- Track everything in a content calendar.
- Maintain or improve engagement baseline.
- Provide a monthly analytics dashboard and recommendation report.

## Project Memory

- `START_HERE.md`: copy/paste prompt and orientation flow for new Codex chats.
- `docs/CURRENT_STATE.md`: current repo state, completed decisions, and next likely work.
- `docs/FOLDER_STRUCTURE.md`: folder layout and rationale.
- `docs/PROJECT_PLAN.md`: full architecture and implementation plan.
- `docs/INTEGRATIONS.md`: API and connector strategy.
- `docs/INTEGRATION_SMOKE_PLAYBOOK.md`: credentialed smoke-test playbook and safety checks.
- `docs/UBIQUITOUS_LANGUAGE.md`: domain glossary and shared terminology.
- `.env.example`: expected configuration and runtime modes.
- `AGENTS.md`: concise instructions for future coding agents.

## Repository Structure

```text
src/content_marketing_agent/
  api.py                 FastAPI app
  cli.py                 operator CLI
  main.py                CrewAI flow entrypoint
  config/                settings
  domain/                vocabulary, enums, models
  connectors/            real/mock/auto integration boundaries
  crews/                 YAML-configured specialist crews
  flows/                 CrewAI Flow orchestration
  services/              approval and calendar services
  storage/               database boundary
  telemetry/             logging and future cost tracking
```

## Demo Philosophy

The demo should feel real without being blocked by platform approvals. Gemini API runs for real. WordPress, GA4, HubSpot, LinkedIn, and Meta run in `auto` mode: real when credentials and permissions are ready, mock otherwise.
