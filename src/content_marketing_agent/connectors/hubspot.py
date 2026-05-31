from content_marketing_agent.config.settings import AppSettings
from content_marketing_agent.connectors.hybrid import HybridPlaceholderConnector
from content_marketing_agent.domain.enums import ConnectorMode, Platform


class HubSpotConnector(HybridPlaceholderConnector):
    def __init__(self, settings: AppSettings) -> None:
        super().__init__(
            platform=Platform.HUBSPOT,
            mode=ConnectorMode(settings.hubspot_mode),
            required_values={
                "HUBSPOT_PRIVATE_APP_TOKEN": settings.hubspot_private_app_token,
            },
        )

