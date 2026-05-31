# Contributing

## Local Setup

1. Install `uv`.
2. Copy `.env.example` to `.env` and fill only the credentials you want to use.
3. Run `uv sync --extra dev`.
4. Run `uv run pytest`.

## Development Rules

- Keep Azure OpenAI as the default real LLM provider.
- Keep platform connectors hybrid: `real`, `mock`, and `auto`.
- Keep `ALLOW_REAL_PUBLISH=false` unless explicitly testing a real approved publish path.
- Add tests for connector mode changes, approval gates, and status transitions.
- Update `docs/CURRENT_STATE.md` after major implementation changes.

## Pull Requests

- Include a concise summary.
- Include tests run.
- Note any connector behavior changes.
- Note any new required environment variables.

