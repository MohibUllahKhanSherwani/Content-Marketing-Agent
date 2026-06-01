from fastapi.testclient import TestClient

from content_marketing_agent.api import app
from content_marketing_agent.config.settings import AppSettings
from content_marketing_agent.services.content_items import ContentItemStore


def test_produce_content_returns_run_telemetry_and_persists_it() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    api_module.get_settings = lambda: AppSettings(azure_openai_mode="mock")
    client = TestClient(app)

    response = client.post(
        "/runs/produce-content",
        json={"objective": "Telemetry smoke", "items_per_channel": 1},
    )

    assert response.status_code == 200
    payload = response.json()
    telemetry = payload["run_telemetry"]
    assert telemetry["run_type"] == "produce_content"
    assert telemetry["success"] is True
    assert telemetry["items_created"] == payload["items_created"]
    assert telemetry["estimated_cost_usd"] >= 0
    assert telemetry["duration_ms"] >= 0

    list_response = client.get("/runs/telemetry")
    assert list_response.status_code == 200
    entries = list_response.json()["runs"]
    assert len(entries) >= 1
    assert entries[0]["run_id"] == telemetry["run_id"]


def test_produce_content_budget_guard_blocks_run_when_exceeded() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    api_module.get_settings = lambda: AppSettings(azure_openai_mode="mock")
    client = TestClient(app)

    response = client.post(
        "/runs/produce-content",
        json={
            "objective": "Budget guard check",
            "items_per_channel": 3,
            "max_budget_usd": 0.0001,
        },
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["error_code"] == "run_budget_exceeded"
