from fastapi.testclient import TestClient

from content_marketing_agent.api import app


def test_connector_diagnostics_reports_missing_credentials(monkeypatch) -> None:
    from content_marketing_agent import api as api_module
    from content_marketing_agent.config.settings import AppSettings
    from content_marketing_agent.services.content_items import ContentItemStore

    api_module.content_item_store = ContentItemStore()
    monkeypatch.setattr(
        api_module,
        "get_settings",
        lambda: AppSettings(
            wordpress_mode="real",
            wordpress_base_url=None,
            wordpress_username=None,
            wordpress_app_password=None,
        ),
    )
    client = TestClient(app)

    response = client.get("/connectors/diagnostics")
    assert response.status_code == 200
    payload = response.json()
    wordpress = next(item for item in payload["connectors"] if item["platform"] == "wordpress")
    assert wordpress["healthy"] is False
    assert "WORDPRESS_BASE_URL" in wordpress["missing_credentials"]
    assert len(wordpress["action_items"]) >= 1


def test_connector_diagnostics_reports_healthy_real_connector(monkeypatch) -> None:
    from content_marketing_agent import api as api_module
    from content_marketing_agent.config.settings import AppSettings
    from content_marketing_agent.services.content_items import ContentItemStore

    api_module.content_item_store = ContentItemStore()
    monkeypatch.setattr(
        api_module,
        "get_settings",
        lambda: AppSettings(
            hubspot_mode="real",
            hubspot_private_app_token="demo-token",
        ),
    )
    client = TestClient(app)

    response = client.get("/connectors/diagnostics")
    assert response.status_code == 200
    payload = response.json()
    hubspot = next(item for item in payload["connectors"] if item["platform"] == "hubspot")
    assert hubspot["healthy"] is True
    assert hubspot["active_mode"] == "real"
    assert hubspot["missing_credentials"] == []
