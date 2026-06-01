from fastapi.testclient import TestClient

from content_marketing_agent.api import app
from content_marketing_agent.config.settings import AppSettings
from content_marketing_agent.services.content_items import ContentItemStore


def _seed_runs(client: TestClient) -> None:
    client.post("/runs/monthly-plan", json={"month": "2026-06", "blog_posts": 8})
    client.post(
        "/runs/produce-content",
        json={"objective": "Seed telemetry", "items_per_channel": 1},
    )
    client.post("/runs/integration-smoke")


def test_runs_telemetry_supports_run_type_filter() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    api_module.get_settings = lambda: AppSettings(azure_openai_mode="mock")
    client = TestClient(app)

    _seed_runs(client)

    response = client.get("/runs/telemetry", params={"run_type": "produce_content", "limit": 10})
    assert response.status_code == 200
    runs = response.json()["runs"]
    assert len(runs) >= 1
    assert all(run["run_type"] == "produce_content" for run in runs)


def test_runs_telemetry_summary_returns_totals_and_breakdown() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    api_module.get_settings = lambda: AppSettings(azure_openai_mode="mock")
    client = TestClient(app)

    _seed_runs(client)

    response = client.get("/runs/telemetry/summary")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total_runs"] >= 3
    assert payload["successful_runs"] >= 3
    assert payload["total_estimated_cost_usd"] >= 0
    assert "produce_content" in payload["by_run_type"]
    assert "budget_limited_runs" in payload
    assert "budget_exceeded_runs" in payload


def test_campaign_telemetry_summary_filters_to_campaign_runs() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    api_module.get_settings = lambda: AppSettings(azure_openai_mode="mock")
    client = TestClient(app)

    profile = client.post(
        "/client-profiles",
        json={"name": "Acme", "audience": ["CTOs"], "offers": ["Platform"]},
    ).json()
    campaign_a = client.post(
        "/campaigns",
        json={
            "client_profile_id": profile["id"],
            "objective": "Campaign A objective",
            "audience": "Startup CTOs",
            "funnel_stage": "TOFU",
            "channels": ["linkedin", "wordpress"],
        },
    ).json()
    campaign_b = client.post(
        "/campaigns",
        json={
            "client_profile_id": profile["id"],
            "objective": "Campaign B objective",
            "audience": "Ops Leaders",
            "funnel_stage": "MOFU",
            "channels": ["linkedin", "wordpress"],
        },
    ).json()

    client.post("/runs/monthly-plan", json={"month": "2026-06", "blog_posts": 8, "campaign_id": campaign_a["id"]})
    client.post("/runs/monthly-plan", json={"month": "2026-07", "blog_posts": 8, "campaign_id": campaign_b["id"]})

    response = client.get(f"/campaigns/{campaign_a['id']}/telemetry-summary")
    assert response.status_code == 200
    payload = response.json()
    assert payload["campaign_id"] == campaign_a["id"]
    assert payload["total_runs"] >= 1
    assert payload["total_runs"] < 3


def test_runs_telemetry_rejects_invalid_date_range() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    client = TestClient(app)

    response = client.get(
        "/runs/telemetry",
        params={"date_from": "2026-07-01T00:00:00Z", "date_to": "2026-06-01T00:00:00Z"},
    )
    assert response.status_code == 400
