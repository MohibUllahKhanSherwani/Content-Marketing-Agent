from content_marketing_agent.config.settings import AppSettings
from content_marketing_agent.connectors.registry import build_connector_registry
from content_marketing_agent.domain.enums import ConnectorMode, Platform


def test_auto_connector_falls_back_to_mock_when_credentials_missing() -> None:
    settings = AppSettings(wordpress_mode="auto")
    registry = build_connector_registry(settings)

    capabilities = registry.get(Platform.WORDPRESS).check_capabilities()

    assert capabilities.requested_mode == ConnectorMode.AUTO
    assert capabilities.active_mode == ConnectorMode.MOCK
    assert "Missing credentials" in (capabilities.reason or "")


def test_real_connector_fails_loudly_when_credentials_missing() -> None:
    settings = AppSettings(wordpress_mode="real")
    registry = build_connector_registry(settings)

    capabilities = registry.get(Platform.WORDPRESS).check_capabilities()

    assert capabilities.requested_mode == ConnectorMode.REAL
    assert capabilities.active_mode == ConnectorMode.REAL
    assert capabilities.can_create_draft is False
    assert "Missing credentials" in (capabilities.reason or "")
