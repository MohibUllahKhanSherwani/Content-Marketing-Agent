from content_marketing_agent.config.settings import AppSettings, get_settings
from content_marketing_agent.connectors.base import BaseConnector
from content_marketing_agent.connectors.ga4 import GA4Connector
from content_marketing_agent.connectors.hubspot import HubSpotConnector
from content_marketing_agent.connectors.linkedin import LinkedInConnector
from content_marketing_agent.connectors.meta import MetaConnector
from content_marketing_agent.connectors.search import SearchConnector
from content_marketing_agent.connectors.wordpress import WordPressConnector
from content_marketing_agent.domain.enums import Platform
from content_marketing_agent.domain.models import ConnectorCapabilities


class ConnectorRegistry:
    def __init__(self, connectors: dict[Platform, BaseConnector]) -> None:
        self._connectors = connectors

    def get(self, platform: Platform) -> BaseConnector:
        return self._connectors[platform]

    def capabilities(self) -> list[ConnectorCapabilities]:
        return [connector.check_capabilities() for connector in self._connectors.values()]

    def as_dict(self) -> dict[str, dict[str, object]]:
        return {
            capability.platform.value: capability.model_dump(mode="json")
            for capability in self.capabilities()
        }


def build_connector_registry(settings: AppSettings | None = None) -> ConnectorRegistry:
    resolved = settings or get_settings()
    connectors: dict[Platform, BaseConnector] = {
        Platform.WORDPRESS: WordPressConnector(resolved),
        Platform.HUBSPOT: HubSpotConnector(resolved),
        Platform.LINKEDIN: LinkedInConnector(resolved),
        Platform.META: MetaConnector(resolved),
        Platform.GA4: GA4Connector(resolved),
        Platform.SEARCH: SearchConnector(resolved),
    }
    return ConnectorRegistry(connectors)

