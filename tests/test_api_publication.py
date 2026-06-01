from fastapi.testclient import TestClient

from content_marketing_agent.api import app
from content_marketing_agent.domain.enums import ContentStatus
from content_marketing_agent.services.content_items import ContentItemStore


def test_demo_seed_resets_in_memory_state() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    client = TestClient(app)

    content_item_id = client.get("/content-items").json()[0]["id"]
    approve_response = client.post(f"/content-items/{content_item_id}/approve")
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == ContentStatus.APPROVED.value

    seed_response = client.post("/demo/seed")
    assert seed_response.status_code == 200
    assert seed_response.json()["items_seeded"] == 3

    detail_response = client.get(f"/content-items/{content_item_id}")
    assert detail_response.status_code == 404


def test_publish_draft_requires_approved_content_item() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    client = TestClient(app)

    content_item_id = client.get("/content-items").json()[0]["id"]
    publish_response = client.post(f"/content-items/{content_item_id}/publish-draft")

    assert publish_response.status_code == 400
    assert "approved" in publish_response.json()["detail"].lower()


def test_publish_draft_records_publication_audit() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    client = TestClient(app)

    content_item_id = client.get("/content-items").json()[0]["id"]
    client.post(f"/content-items/{content_item_id}/approve")

    publish_response = client.post(f"/content-items/{content_item_id}/publish-draft")
    assert publish_response.status_code == 200
    payload = publish_response.json()
    assert payload["publication"]["success"] is True
    assert payload["publication"]["operation"] == "create_draft"

    publications_response = client.get(f"/content-items/{content_item_id}/publications")
    assert publications_response.status_code == 200
    publications = publications_response.json()
    assert len(publications) == 1
    assert publications[0]["operation"] == "create_draft"
