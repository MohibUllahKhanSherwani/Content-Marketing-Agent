from fastapi.testclient import TestClient

from content_marketing_agent.api import app
from content_marketing_agent.services.content_items import ContentItemStore


def test_integration_smoke_returns_platform_results() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    client = TestClient(app)

    response = client.post("/runs/integration-smoke")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total_connectors_checked"] >= 6
    assert isinstance(payload["results"], list)

    platforms = {item["platform"] for item in payload["results"]}
    assert "wordpress" in platforms
    assert "hubspot" in platforms
    assert "ga4" in platforms
