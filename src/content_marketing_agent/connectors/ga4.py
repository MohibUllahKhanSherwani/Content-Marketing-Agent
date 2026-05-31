from content_marketing_agent.config.settings import AppSettings
from content_marketing_agent.connectors.hybrid import HybridPlaceholderConnector
from content_marketing_agent.domain.enums import ConnectorMode, Platform


class GA4Connector(HybridPlaceholderConnector):
    def __init__(self, settings: AppSettings) -> None:
        super().__init__(
            platform=Platform.GA4,
            mode=ConnectorMode(settings.ga4_mode),
            required_values={
                "GA4_PROPERTY_ID": settings.ga4_property_id,
                "GOOGLE_APPLICATION_CREDENTIALS": settings.google_application_credentials,
            },
        )

