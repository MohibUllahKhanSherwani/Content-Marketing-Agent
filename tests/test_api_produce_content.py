from fastapi.testclient import TestClient

from content_marketing_agent.api import app
from content_marketing_agent.config.settings import AppSettings
from content_marketing_agent.domain.enums import ContentStatus
from content_marketing_agent.services.content_items import ContentItemStore


def test_produce_content_uses_mock_mode_when_azure_not_configured() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    api_module.get_settings = lambda: AppSettings(azure_openai_mode="real")
    client = TestClient(app)

    response = client.post("/runs/produce-content", json={"objective": "Increase demo pipeline"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["generation_mode"] == "mock"
    assert payload["items_created"] == 6
    assert all(item["status"] == ContentStatus.DRAFTED.value for item in payload["items"])


def test_produce_content_uses_real_mode_when_azure_is_configured() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    api_module.get_settings = lambda: AppSettings(
        azure_openai_mode="real",
        azure_api_key="test-key",
        azure_endpoint="https://example.openai.azure.com",
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
