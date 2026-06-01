from fastapi.testclient import TestClient

from content_marketing_agent.api import app
from content_marketing_agent.domain.enums import ContentStatus
from content_marketing_agent.services.content_items import ContentItemStore


def test_monthly_plan_creates_briefed_items_with_schedule() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    client = TestClient(app)

    response = client.post(
        "/runs/monthly-plan",
        json={"month": "2026-02", "blog_posts": 8},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["items_created"] > 0
    assert payload["summary"]["blog_posts"] == 8
    assert payload["summary"]["social_posts"] == 28
    assert payload["summary"]["email_campaigns"] == 4

    items = payload["items"]
    assert all(item["status"] == ContentStatus.BRIEFED.value for item in items)
    assert all(item["scheduled_at"] is not None for item in items)


def test_calendar_endpoint_returns_scheduled_items() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    client = TestClient(app)
    client.post("/runs/monthly-plan", json={"month": "2026-03", "blog_posts": 9})

    calendar_response = client.get("/calendar")
    assert calendar_response.status_code == 200
    calendar_items = calendar_response.json()
    assert len(calendar_items) > 0
    assert all(item["scheduled_at"] is not None for item in calendar_items)
    assert all(item["status"] == ContentStatus.BRIEFED.value for item in calendar_items)
