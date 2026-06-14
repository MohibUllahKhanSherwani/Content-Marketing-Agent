# Agent Instructions

## Canon
- Read `START_HERE.md`, `README.md`, `docs/CURRENT_STATE.md`, `docs/PROJECT_PLAN.md`, `docs/INTEGRATIONS.md`, and `docs/UBIQUITOUS_LANGUAGE.md` before implementation.
- Build a CrewAI-based Content Marketing Agent Team for multi-channel content creation, approval, publishing, calendar tracking, and analytics.
- Default to Gemini API as the real LLM provider and hybrid `auto` connectors for external platforms.

## Package Manager
- Use **uv** for Python dependency and command management.
- Target Python `>=3.10,<3.14`, matching CrewAI support.
- Expected commands after scaffold:

| Task | Command |
| --- | --- |
| Install | `uv sync` |
| Run app | `uv run crewai run` |
| API dev server | `uv run uvicorn content_marketing_agent.api:app --reload` |
| Tests | `uv run pytest` |
| Lint | `uv run ruff check .` |
| Typecheck | `uv run mypy src` |

## Runtime Modes
- `GEMINI_API_MODE=real` for generation.
- External connectors use `auto`, `real`, or `mock`.
- `auto` means real only when credentials and permissions validate; otherwise use realistic mocks.
- Never publish externally unless the content item is `APPROVED` and the target connector is explicitly allowed to publish.

## Key Conventions
- Use CrewAI Flows for orchestration and Crews for specialist work.
- Keep agents and tasks in YAML where practical; keep connector logic in Python.
- Preserve a human approval gate between QA and external publishing.
- Store secrets only in `.env` or the deployment secret store; never commit credentials.
- Prefer read-only real integrations for demos unless publishing is intentionally enabled.
- Use mocks that return realistic platform IDs, links, metrics, and errors.

## Connector Safety
- WordPress may create drafts when real credentials exist; publishing is gated.
- HubSpot may create drafts only if account/API capabilities allow it; otherwise mock.
- LinkedIn and Meta default to mock unless token, app permissions, and target asset access are confirmed.
- GA4 is read-only; fall back to mock analytics when credentials are missing.

## Commit Attribution
AI commits MUST include:

```text
Co-Authored-By: (the agent model's name and attribution byline)
```
