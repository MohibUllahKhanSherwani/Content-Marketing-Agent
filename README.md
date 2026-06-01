# Content Marketing Agent Team

This project will become a production-grade CrewAI agent system for Roman Khaliq's Content Marketing Agent role from Agent Talent.

The agent team creates and manages multi-channel marketing content: blog posts, email campaigns, social posts, ad copy, landing-page copy, case studies, content calendars, approval workflows, publishing integrations, and monthly performance analysis.

The immediate goal is to support an AgentTalent.ai application/proposal with a credible working demo, then evolve into a production-capable agency content operations system.

## Current Decisions

- **Framework:** CrewAI with Flows as the top-level orchestrator and specialist Crews for strategy, production, QA, distribution, and analytics.
- **LLM provider:** Azure OpenAI.
- **Primary model:** `azure/gpt-4o-mini` for high-volume generation and extraction.
- **Review model:** `azure/gpt-4o` or another stronger Azure deployment for final strategic and quality checks.
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

The default connector behavior is safe for demos: Azure OpenAI is real when configured, and external platforms use `auto` mode with mock fallback.

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
- `POST /runs/integration-smoke`
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

- Azure OpenAI:
  - `AZURE_API_KEY`
  - `AZURE_ENDPOINT`
  - `AZURE_API_VERSION`
  - `CONTENT_AGENT_MODEL`
  - `CONTENT_AGENT_REVIEW_MODEL`
- WordPress (real draft creation):
  - `WORDPRESS_BASE_URL`
  - `WORDPRESS_USERNAME`
  - `WORDPRESS_APP_PASSWORD`
- HubSpot (real email draft creation):
  - `HUBSPOT_PRIVATE_APP_TOKEN`
- GA4 (real read-only analytics):
  - `GA4_PROPERTY_ID`
  - `GOOGLE_APPLICATION_CREDENTIALS` (service account JSON path)

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

The demo should feel real without being blocked by platform approvals. Azure OpenAI runs for real. WordPress, GA4, HubSpot, LinkedIn, and Meta run in `auto` mode: real when credentials and permissions are ready, mock otherwise.
