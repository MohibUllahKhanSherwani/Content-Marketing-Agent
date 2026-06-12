from fastapi.testclient import TestClient

from content_marketing_agent.api import app
from content_marketing_agent.config.settings import AppSettings
from content_marketing_agent.domain.enums import ContentFormat, ContentStatus, Platform
from content_marketing_agent.services.content_items import ContentItemStore


def test_produce_content_uses_mock_mode_when_gemini_not_configured() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    api_module.get_settings = lambda: AppSettings(gemini_api_mode="real")
    client = TestClient(app)

    response = client.post("/runs/produce-content", json={"objective": "Increase demo pipeline"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["generation_mode"] == "mock"
    assert payload["items_created"] == 6
    assert all(item["status"] == ContentStatus.DRAFTED.value for item in payload["items"])


def test_produce_content_uses_real_mode_when_gemini_is_configured() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    api_module.get_settings = lambda: AppSettings(
        gemini_api_mode="real",
        gemini_api_key="test-key",
    )
    client = TestClient(app)

    response = client.post(
        "/runs/produce-content",
        json={"objective": "Increase proposal conversion", "items_per_channel": 2},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["generation_mode"] == "real"
    assert payload["items_created"] == 12

    items_response = client.get("/content-items")
    assert items_response.status_code == 200
    assert len(items_response.json()) >= 12


def test_produce_content_real_mode_attempts_crew_execution(monkeypatch) -> None:
    from content_marketing_agent import api as api_module
    from content_marketing_agent.services import production as production_module

    called = {"value": False}

    def fake_run_real_production_crew(
        *, objective: str, items_per_channel: int
    ) -> list[tuple[str, ContentFormat, Platform, str]]:
        called["value"] = True
        return production_module._content_templates(objective, "real", items_per_channel)

    monkeypatch.setattr(production_module, "_run_real_production_crew", fake_run_real_production_crew)

    api_module.content_item_store = ContentItemStore()
    api_module.get_settings = lambda: AppSettings(
        gemini_api_mode="real",
        gemini_api_key="test-key",
    )
    client = TestClient(app)
    response = client.post("/runs/produce-content", json={"objective": "Crew integration smoke"})

    assert response.status_code == 200
    assert response.json()["generation_mode"] == "real"
    assert called["value"] is True


def test_produce_content_strict_real_fails_loudly_when_crew_fails(monkeypatch) -> None:
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
        "/runs/produce-content",
        json={"objective": "Strict failure check", "strict_real": True},
    )
    assert response.status_code == 502
    detail = response.json()["detail"]
    assert detail["error_code"] == "real_generation_failed"


def test_produce_content_uses_campaign_objective_and_links_items_when_campaign_id_provided() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    api_module.get_settings = lambda: AppSettings(gemini_api_mode="mock")
    client = TestClient(app)
    profile = client.post(
        "/client-profiles",
        json={"name": "Acme", "audience": ["CTOs"], "offers": ["Platform"]},
    ).json()
    campaign = client.post(
        "/campaigns",
        json={
            "client_profile_id": profile["id"],
            "objective": "Increase qualified demos",
            "audience": "Startup engineering leaders",
            "funnel_stage": "TOFU",
            "channels": ["linkedin", "wordpress"],
        },
    ).json()

    response = client.post(
        "/runs/produce-content",
        json={"campaign_id": campaign["id"], "items_per_channel": 1},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["items_created"] == 4
    assert all(item["campaign_brief_id"] == campaign["id"] for item in payload["items"])
    assert all(
        "Increase qualified demos" in item["metadata"]["objective"] for item in payload["items"]
    )
