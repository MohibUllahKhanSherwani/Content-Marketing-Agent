from fastapi.testclient import TestClient

from content_marketing_agent.api import app
from content_marketing_agent.config.settings import AppSettings
from content_marketing_agent.domain.enums import ContentFormat, Platform
from content_marketing_agent.services.content_items import ContentItemStore


def test_monthly_flow_runs_plan_production_analytics_and_returns_telemetry() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    api_module.get_settings = lambda: AppSettings(gemini_api_mode='mock')
    client = TestClient(app)

    response = client.post(
        '/runs/monthly-flow',
        json={'month': '2026-08', 'blog_posts': 8, 'items_per_channel': 1},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload['plan']['items_created'] > 0
    assert payload['production']['items_created'] > 0
    assert payload['analytics']['snapshots_collected'] > 0
    assert payload['run_telemetry']['run_type'] == 'monthly_flow'


def test_monthly_flow_strict_real_failure_returns_502(monkeypatch) -> None:
    from content_marketing_agent import api as api_module
    from content_marketing_agent.services import production as production_module

    def fake_run_real_production_crew(
        *, objective: str, items_per_channel: int
    ) -> list[tuple[str, ContentFormat, Platform, str]]:
        raise RuntimeError("boom")

    monkeypatch.setattr(production_module, "_run_real_production_crew", fake_run_real_production_crew)
    api_module.content_item_store = ContentItemStore()
    api_module.get_settings = lambda: AppSettings(
        gemini_api_mode="real",
        gemini_api_key="test-key",
    )
    client = TestClient(app)

    response = client.post(
        "/runs/monthly-flow",
        json={"month": "2026-08", "blog_posts": 8, "strict_real": True},
    )

    assert response.status_code == 502
    detail = response.json()["detail"]
    assert detail["error_code"] == "real_generation_failed"


def test_monthly_flow_strict_real_failure_records_failed_telemetry(monkeypatch) -> None:
    from content_marketing_agent import api as api_module
    from content_marketing_agent.services import production as production_module

    def fake_run_real_production_crew(
        *, objective: str, items_per_channel: int
    ) -> list[tuple[str, ContentFormat, Platform, str]]:
        raise RuntimeError("boom")

    monkeypatch.setattr(production_module, "_run_real_production_crew", fake_run_real_production_crew)
    api_module.content_item_store = ContentItemStore()
    api_module.get_settings = lambda: AppSettings(
        gemini_api_mode="real",
        gemini_api_key="test-key",
    )
    client = TestClient(app)

    response = client.post(
        "/runs/monthly-flow",
        json={"month": "2026-08", "blog_posts": 8, "strict_real": True},
    )
    assert response.status_code == 502

    telemetry_response = client.get("/runs/telemetry", params={"run_type": "monthly_flow", "limit": 5})
    assert telemetry_response.status_code == 200
    runs = telemetry_response.json()["runs"]
    assert len(runs) == 1
    assert runs[0]["success"] is False
    assert runs[0]["error_code"] == "real_generation_failed"
