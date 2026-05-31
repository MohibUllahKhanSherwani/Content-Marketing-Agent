from fastapi import FastAPI

from content_marketing_agent.config.settings import get_settings
from content_marketing_agent.connectors.registry import build_connector_registry
from content_marketing_agent.services.calendar import demo_calendar_items

app = FastAPI(
    title="Content Marketing Agent Team",
    version="0.1.0",
    description="CrewAI content marketing workflow with Azure OpenAI and hybrid connectors.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/connectors")
def connectors() -> dict[str, dict[str, object]]:
    registry = build_connector_registry(get_settings())
    return registry.as_dict()


@app.get("/calendar/demo")
def calendar_demo() -> list[dict[str, object]]:
    return [item.model_dump(mode="json") for item in demo_calendar_items()]

