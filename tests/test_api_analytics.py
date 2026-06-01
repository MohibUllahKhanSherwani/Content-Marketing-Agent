from fastapi.testclient import TestClient

from content_marketing_agent.api import app
from content_marketing_agent.services.content_items import ContentItemStore


def test_monthly_analytics_run_persists_snapshots_and_returns_summary() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    client = TestClient(app)

    run_response = client.post("/runs/monthly-analytics")
    assert run_response.status_code == 200
    payload = run_response.json()
    assert payload["snapshots_collected"] >= 3
    assert payload["snapshots_persisted"] == payload["snapshots_collected"]
    assert payload["summary"]["snapshots_count"] == payload["snapshots_collected"]
    assert payload["summary"]["totals"]["impressions"] > 0


def test_monthly_summary_reads_persisted_snapshots() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    client = TestClient(app)
    client.post("/runs/monthly-analytics")

    summary_response = client.get("/analytics/monthly-summary")
    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["snapshots_count"] >= 3
    assert summary["totals"]["clicks"] > 0
    assert len(summary["by_platform"]) >= 1


def test_monthly_analytics_includes_ga4_rollup_platform() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    client = TestClient(app)

    run_response = client.post("/runs/monthly-analytics")
    assert run_response.status_code == 200
    payload = run_response.json()
    assert "ga4" in payload["summary"]["by_platform"]
