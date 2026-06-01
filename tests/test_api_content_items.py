from fastapi.testclient import TestClient

from content_marketing_agent.api import app
from content_marketing_agent.domain.enums import ContentStatus
from content_marketing_agent.services.content_items import ContentItemStore


def test_content_items_list_and_fetch() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    client = TestClient(app)

    list_response = client.get("/content-items")
    assert list_response.status_code == 200
    items = list_response.json()
    assert len(items) == 3

    first_id = items[0]["id"]
    detail_response = client.get(f"/content-items/{first_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == first_id


def test_approve_content_item_updates_status() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    client = TestClient(app)
    content_item_id = client.get("/content-items").json()[0]["id"]

    approve_response = client.post(f"/content-items/{content_item_id}/approve", json={})
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == ContentStatus.APPROVED.value

    detail_response = client.get(f"/content-items/{content_item_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["status"] == ContentStatus.APPROVED.value


def test_content_item_routes_return_404_for_missing_ids() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    client = TestClient(app)
    missing_id = "missing-item-id"

    detail_response = client.get(f"/content-items/{missing_id}")
    assert detail_response.status_code == 404

    approve_response = client.post(f"/content-items/{missing_id}/approve", json={})
    assert approve_response.status_code == 404


def test_request_changes_updates_status_and_stores_decision() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    client = TestClient(app)
    content_item_id = client.get("/content-items").json()[0]["id"]

    request_changes_response = client.post(
        f"/content-items/{content_item_id}/request-changes",
        json={"approver": "editor_1", "notes": "Revise CTA and tighten intro."},
    )
    assert request_changes_response.status_code == 200
    assert request_changes_response.json()["status"] == ContentStatus.QA_FAILED.value

    decisions_response = client.get(f"/content-items/{content_item_id}/approval-decisions")
    assert decisions_response.status_code == 200
    decisions = decisions_response.json()
    assert len(decisions) == 1
    assert decisions[0]["approved"] is False
    assert decisions[0]["approver"] == "editor_1"
