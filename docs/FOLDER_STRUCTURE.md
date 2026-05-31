# Folder Structure

This repo is organized as a modular monolith. CrewAI owns orchestration, the domain layer owns business language, connectors own platform integrations, and the API/dashboard layer exposes the workflow for demos and production use.

```text
content_marketing_agent/
  .github/                         GitHub CI and collaboration templates
  docs/                            durable project memory and architecture docs
  src/content_marketing_agent/
    api.py                         FastAPI app entrypoint
    cli.py                         local operator commands
    main.py                        CrewAI flow entrypoint
    config/                        settings and environment handling
    domain/                        statuses, enums, and Pydantic domain models
    connectors/                    real/mock/auto platform connectors
    crews/                         YAML-configured CrewAI specialist crews
    flows/                         CrewAI Flow orchestration
    services/                      approval, calendar, publishing, analytics services
    storage/                       database session and migrations boundary
    telemetry/                     logging, run IDs, cost/token tracking
  tests/                           unit and integration-style tests
```

## Why This Shape

- CrewAI YAML stays close to each crew so agent/task prompts are easy to review.
- Connectors are isolated from crews so the same content workflow can use real or mock platforms.
- Domain models sit below everything so API, crews, connectors, and tests use the same vocabulary.
- The dashboard/API can evolve without coupling external platform SDKs to route handlers.
- GitHub workflows can run tests without requiring real platform credentials.

