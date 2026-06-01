from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from content_marketing_agent.config.settings import get_settings
from content_marketing_agent.connectors.registry import build_connector_registry
from content_marketing_agent.domain.enums import ContentStatus
from content_marketing_agent.services.calendar import demo_calendar_items
from content_marketing_agent.services.content_items import (
    ContentItemNotFoundError,
    ContentItemStore,
)
from content_marketing_agent.services.production import produce_content_drafts

app = FastAPI(
    title="Content Marketing Agent Team",
    version="0.1.0",
    description="CrewAI content marketing workflow with Azure OpenAI and hybrid connectors.",
)
content_item_store = ContentItemStore.from_settings(get_settings())


class ProduceContentRequest(BaseModel):
    objective: str = "Generate monthly multi-channel content for campaign goals."
    items_per_channel: int = Field(default=1, ge=1, le=3)


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


@app.post("/demo/seed")
def seed_demo() -> dict[str, int]:
    items_seeded = content_item_store.seed_demo_items()
    return {"items_seeded": items_seeded}


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


@app.post("/content-items/{content_item_id}/publish-draft")
def publish_content_item_draft(content_item_id: str) -> dict[str, dict[str, object]]:
    try:
        item = content_item_store.get_item(content_item_id)
    except ContentItemNotFoundError as error:
        raise HTTPException(status_code=404, detail="Content item not found.") from error

    if item.status != ContentStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Content item must be approved before draft publish.")

    connector = build_connector_registry(get_settings()).get(item.target_platform)
    publication = connector.create_draft(item)
    content_item_store.record_publication(content_item_id, publication)
    return {
        "content_item": item.model_dump(mode="json"),
        "publication": publication.model_dump(mode="json"),
    }


@app.get("/content-items/{content_item_id}/publications")
def content_item_publications(content_item_id: str) -> list[dict[str, object]]:
    try:
        publications = content_item_store.list_publications(content_item_id)
    except ContentItemNotFoundError as error:
        raise HTTPException(status_code=404, detail="Content item not found.") from error
    return [record.model_dump(mode="json") for record in publications]


@app.post("/runs/produce-content")
def run_produce_content(request: ProduceContentRequest) -> dict[str, object]:
    settings = get_settings()
    result = produce_content_drafts(
        objective=request.objective,
        settings=settings,
        items_per_channel=request.items_per_channel,
    )
    saved_items = content_item_store.add_items(result.items)
    return {
        "generation_mode": result.generation_mode,
        "items_created": len(saved_items),
        "items": [item.model_dump(mode="json") for item in saved_items],
    }
