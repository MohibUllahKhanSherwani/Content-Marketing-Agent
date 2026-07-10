import httpx
import respx

from content_marketing_agent.config.settings import AppSettings
from content_marketing_agent.connectors.hubspot import HubSpotConnector
from content_marketing_agent.domain.enums import ConnectorMode, ContentFormat, Platform
from content_marketing_agent.domain.models import ContentItem


def _demo_item() -> ContentItem:
    return ContentItem(
        title="Weekly Product Update",
        body="Hello subscriber, here is what shipped this week.",
        format=ContentFormat.EMAIL_CAMPAIGN,
        target_platform=Platform.HUBSPOT,
    )


def test_hubspot_auto_mode_uses_mock_without_credentials() -> None:
    connector = HubSpotConnector(AppSettings(hubspot_mode="auto", hubspot_private_app_token=None))
    result = connector.create_draft(_demo_item())
    assert result.mode == ConnectorMode.MOCK
    assert result.success is True


@respx.mock
def test_hubspot_real_create_draft_success() -> None:
    route = respx.post("https://api.hubapi.com/marketing/v3/emails").mock(
        return_value=httpx.Response(201, json={"id": 987, "name": "Weekly Product Update", "isPublished": False})
    )
    connector = HubSpotConnector(
        AppSettings(
            hubspot_mode="real",
            hubspot_private_app_token="demo-token",
        )
    )

    result = connector.create_draft(_demo_item())

    assert route.called
    assert result.mode == ConnectorMode.REAL
    assert result.success is True
    assert result.platform_id == "987"
    assert result.status == "draft"


@respx.mock
def test_hubspot_real_create_draft_http_error_returns_structured_failure() -> None:
    respx.post("https://api.hubapi.com/marketing/v3/emails").mock(
        return_value=httpx.Response(403, json={"message": "forbidden"})
    )
    connector = HubSpotConnector(
        AppSettings(
            hubspot_mode="real",
            hubspot_private_app_token="demo-token",
        )
    )

    result = connector.create_draft(_demo_item())

    assert result.mode == ConnectorMode.REAL
    assert result.success is False
    assert result.error_code == "hubspot_http_error"
