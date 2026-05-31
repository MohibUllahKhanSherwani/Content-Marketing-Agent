# Start Here For New Codex Chats

Use this file when starting a fresh Codex conversation for this repo.

## Copy/Paste Prompt

```text
We are working in D:\Projects\content_marketing_agent.

First read AGENTS.md, README.md, docs/CURRENT_STATE.md, docs/PROJECT_PLAN.md, docs/INTEGRATIONS.md, and docs/UBIQUITOUS_LANGUAGE.md. Then inspect the repo state before making changes.

This project is a CrewAI Content Marketing Agent Team for Roman Khaliq's Agent Talent role. Azure OpenAI is the real LLM provider. External services use hybrid connectors: real where credentials and permissions exist, otherwise realistic mocks. Human approval is mandatory before real publishing.

After reading, summarize the current repo state, then continue with my task.

My task is: <paste task here>
```

## What Future Codex Should Do First

1. Read `AGENTS.md` for operating rules.
2. Read `docs/CURRENT_STATE.md` for what exists right now.
3. Read `docs/PROJECT_PLAN.md` for the intended architecture.
4. Read `docs/INTEGRATIONS.md` for API and connector behavior.
5. Read `docs/UBIQUITOUS_LANGUAGE.md` to keep terminology consistent.
6. Read `graphify-out/GRAPH_REPORT.md` when source-level architecture context is needed.
7. Inspect the filesystem before editing.
8. If a git repository exists, run `git status --short` before edits.

## What Graphify Is For Later

Graphify will be useful once the repo has actual source code. It can help map modules, imports, dependencies, and implementation state.

The repo now has an initial Graphify structural graph in `graphify-out/`. Keep `docs/CURRENT_STATE.md` updated after major changes and rerun graph/code analysis to verify it.
