from fastapi.testclient import TestClient

from content_marketing_agent.api import app
from content_marketing_agent.config.settings import AppSettings


def test_health_llm_reports_mock_when_azure_not_configured(monkeypatch) -> None:
    from content_marketing_agent import api as api_module

    monkeypatch.setattr(api_module, "get_settings", lambda: AppSettings(azure_openai_mode="real"))
    client = TestClient(app)
    response = client.get("/health/llm")

    assert response.status_code == 200
    payload = response.json()
    assert payload["requested_mode"] == "real"
    assert payload["active_mode"] == "mock"
    assert payload["azure_configured"] is False
    assert payload["crew_execution_ready"] is False


def test_health_llm_reports_real_when_azure_configured(monkeypatch) -> None:
    from content_marketing_agent import api as api_module

    monkeypatch.setattr(
        api_module,
        "get_settings",
        lambda: AppSettings(
            azure_openai_mode="real",
            azure_api_key="test-key",
            azure_endpoint="https://example.openai.azure.com",
        ),
    )
    client = TestClient(app)
    response = client.get("/health/llm")

    assert response.status_code == 200
    payload = response.json()
    assert payload["active_mode"] == "real"
    assert payload["azure_configured"] is True
    assert payload["crew_execution_ready"] is True
