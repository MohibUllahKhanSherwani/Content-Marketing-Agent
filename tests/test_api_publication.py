from fastapi.testclient import TestClient

from content_marketing_agent.api import app
from content_marketing_agent.config.settings import AppSettings
from content_marketing_agent.connectors.base import BaseConnector
from content_marketing_agent.domain.enums import ConnectorMode, ContentStatus, Platform
from content_marketing_agent.domain.models import (
    ConnectorCapabilities,
    ConnectorResult,
    ContentItem,
)
from content_marketing_agent.services.content_items import ContentItemStore


def test_demo_seed_resets_in_memory_state() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    client = TestClient(app)

    content_item_id = client.get("/content-items").json()[0]["id"]
    approve_response = client.post(f"/content-items/{content_item_id}/approve", json={})
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == ContentStatus.APPROVED.value

    seed_response = client.post("/demo/seed")
    assert seed_response.status_code == 200
    assert seed_response.json()["items_seeded"] == 3

    detail_response = client.get(f"/content-items/{content_item_id}")
    assert detail_response.status_code == 404


def test_publish_draft_requires_approved_content_item() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    client = TestClient(app)

    content_item_id = client.get("/content-items").json()[0]["id"]
    publish_response = client.post(f"/content-items/{content_item_id}/publish-draft")

    assert publish_response.status_code == 400
    assert "approved" in publish_response.json()["detail"].lower()


def test_publish_draft_records_publication_audit() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    client = TestClient(app)

    content_item_id = client.get("/content-items").json()[0]["id"]
    client.post(f"/content-items/{content_item_id}/approve", json={})

    publish_response = client.post(f"/content-items/{content_item_id}/publish-draft")
    assert publish_response.status_code == 200
    payload = publish_response.json()
    assert payload["publication"]["success"] is True
    assert payload["publication"]["operation"] == "create_draft"

    publications_response = client.get(f"/content-items/{content_item_id}/publications")
    assert publications_response.status_code == 200
    publications = publications_response.json()
    assert len(publications) == 1
    assert publications[0]["operation"] == "create_draft"


class FakeRealPublishConnector(BaseConnector):
    platform = Platform.WORDPRESS

    def __init__(self) -> None:
        super().__init__(ConnectorMode.REAL)

    def check_capabilities(self) -> ConnectorCapabilities:
        return ConnectorCapabilities(
            platform=self.platform,
            requested_mode=ConnectorMode.REAL,
            active_mode=ConnectorMode.REAL,
            can_publish=True,
            can_create_draft=True,
        )

    def publish(self, content_item: ContentItem) -> ConnectorResult:
        return ConnectorResult(
            platform=self.platform,
            mode=ConnectorMode.REAL,
            operation="publish",
            success=True,
            platform_id=f"real_{content_item.id}",
            platform_url="https://example.com/real-post",
            status="published",
        )


def test_publish_requires_approved_content_item() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    client = TestClient(app)
    content_item_id = client.get("/content-items").json()[0]["id"]

    publish_response = client.post(f"/content-items/{content_item_id}/publish")
    assert publish_response.status_code == 400
    assert "approved" in publish_response.json()["detail"].lower()


def test_publish_blocks_real_mode_when_runtime_flag_disabled(monkeypatch) -> None:
    from content_marketing_agent import api as api_module

    class FakeRegistry:
        def get(self, platform: Platform) -> BaseConnector:
            return FakeRealPublishConnector()

    api_module.content_item_store = ContentItemStore()
    monkeypatch.setattr(api_module, "build_connector_registry", lambda _settings: FakeRegistry())
    monkeypatch.setattr(api_module, "get_settings", lambda: AppSettings(allow_real_publish=False))

    client = TestClient(app)
    content_item_id = client.get("/content-items").json()[0]["id"]
    client.post(f"/content-items/{content_item_id}/approve", json={})

    publish_response = client.post(f"/content-items/{content_item_id}/publish")
    assert publish_response.status_code == 400
    assert "allow_real_publish" in publish_response.json()["detail"].lower()


def test_publish_marks_item_published_and_records_audit(monkeypatch) -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    monkeypatch.setattr(api_module, "get_settings", lambda: AppSettings(allow_real_publish=False))
    client = TestClient(app)
    content_item_id = client.get("/content-items").json()[0]["id"]
    client.post(f"/content-items/{content_item_id}/approve", json={})

    publish_response = client.post(f"/content-items/{content_item_id}/publish")
    assert publish_response.status_code == 200
    payload = publish_response.json()
    assert payload["content_item"]["status"] == ContentStatus.PUBLISHED.value
    assert payload["publication"]["operation"] == "publish"
    assert payload["publication"]["success"] is True

    publications_response = client.get(f"/content-items/{content_item_id}/publications")
    assert publications_response.status_code == 200
    publications = publications_response.json()
    assert publications[-1]["operation"] == "publish"
