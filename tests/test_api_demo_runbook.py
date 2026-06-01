from fastapi.testclient import TestClient

from content_marketing_agent.api import app
from content_marketing_agent.config.settings import AppSettings
from content_marketing_agent.domain.enums import ContentStatus
from content_marketing_agent.services.content_items import ContentItemStore


def test_demo_runbook_seed_produce_approve_publish_draft_audit_telemetry() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore(seed_if_empty=False)
    api_module.get_settings = lambda: AppSettings(azure_openai_mode="mock")
    client = TestClient(app)

    seed_response = client.post("/demo/seed")
    assert seed_response.status_code == 200
    assert seed_response.json()["items_seeded"] > 0

    produce_response = client.post("/runs/produce-content", json={"items_per_channel": 1})
    assert produce_response.status_code == 200
    assert produce_response.json()["items_created"] > 0

    items_response = client.get("/content-items")
    assert items_response.status_code == 200
    items = items_response.json()
    draft_item = next(item for item in items if item["status"] == ContentStatus.DRAFTED.value)

    approve_response = client.post(
        f"/content-items/{draft_item['id']}/approve", json={"approver": "demo_operator"}
    )
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == ContentStatus.APPROVED.value

    publish_draft_response = client.post(f"/content-items/{draft_item['id']}/publish-draft")
    assert publish_draft_response.status_code == 200
    assert publish_draft_response.json()["publication"]["operation"] == "create_draft"

    publications_response = client.get(f"/content-items/{draft_item['id']}/publications")
    assert publications_response.status_code == 200
    publications = publications_response.json()
    assert len(publications) >= 1

    telemetry_response = client.get("/runs/telemetry/summary")
    assert telemetry_response.status_code == 200
    telemetry = telemetry_response.json()
    assert telemetry["total_runs"] >= 1
