from content_marketing_agent.config.settings import AppSettings
from content_marketing_agent.connectors.hybrid import HybridPlaceholderConnector
from content_marketing_agent.domain.enums import ConnectorMode, Platform


class SearchConnector(HybridPlaceholderConnector):
    def __init__(self, settings: AppSettings) -> None:
        super().__init__(
            platform=Platform.SEARCH,
            mode=ConnectorMode(settings.search_mode),
            required_values={
                "SERPER_API_KEY": settings.serper_api_key,
            },
        )

