from fastapi.testclient import TestClient

from content_marketing_agent.api import app
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
    assert payload["run_telemetry"]["run_type"] == "monthly_plan"

    items = payload["items"]
    assert all(item["status"] == "briefed" for item in items)
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
    assert all(item["status"] == "briefed" for item in calendar_items)


def test_monthly_plan_links_items_to_campaign_when_campaign_id_provided() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    client = TestClient(app)
    profile = client.post(
        "/client-profiles",
        json={"name": "Campaign Link Test", "audience": ["CTO"], "offers": ["Advisory"]},
    ).json()
    campaign = client.post(
        "/campaigns",
        json={
            "client_profile_id": profile["id"],
            "objective": "Grow qualified inbound",
            "audience": "Technical founders",
            "funnel_stage": "MOFU",
            "channels": ["wordpress", "linkedin"],
        },
    ).json()

    response = client.post(
        "/runs/monthly-plan",
        json={"month": "2026-05", "blog_posts": 8, "campaign_id": campaign["id"]},
    )

    assert response.status_code == 200
    items = response.json()["items"]
    assert all(item["campaign_brief_id"] == campaign["id"] for item in items)
