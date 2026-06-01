from fastapi import FastAPI, HTTPException

from content_marketing_agent.config.settings import get_settings
from content_marketing_agent.connectors.registry import build_connector_registry
from content_marketing_agent.services.calendar import demo_calendar_items
from content_marketing_agent.services.content_items import (
    ContentItemNotFoundError,
    ContentItemStore,
)

app = FastAPI(
    title="Content Marketing Agent Team",
    version="0.1.0",
    description="CrewAI content marketing workflow with Azure OpenAI and hybrid connectors.",
)
content_item_store = ContentItemStore()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

# dumps the connector registry state as a dict
@app.get("/connectors")
def connectors() -> dict[str, dict[str, object]]:
    registry = build_connector_registry(get_settings())
    return registry.as_dict()


@app.get("/calendar/demo")
def calendar_demo() -> list[dict[str, object]]:
    return [item.model_dump(mode="json") for item in demo_calendar_items()]


@app.get("/content-items")
def content_items() -> list[dict[str, object]]:
    return [item.model_dump(mode="json") for item in content_item_store.list_items()]


@app.get("/content-items/{content_item_id}")
def content_item_detail(content_item_id: str) -> dict[str, object]:
    try:
        item = content_item_store.get_item(content_item_id)
    except ContentItemNotFoundError as error:
        raise HTTPException(status_code=404, detail="Content item not found.") from error
    return item.model_dump(mode="json")


@app.post("/content-items/{content_item_id}/approve")
def approve_content_item(content_item_id: str) -> dict[str, object]:
    try:
        item = content_item_store.approve_item(content_item_id)
    except ContentItemNotFoundError as error:
        raise HTTPException(status_code=404, detail="Content item not found.") from error
    return item.model_dump(mode="json")
