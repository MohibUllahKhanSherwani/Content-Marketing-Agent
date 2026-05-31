from content_marketing_agent.config.settings import AppSettings
from content_marketing_agent.connectors.hybrid import HybridPlaceholderConnector
from content_marketing_agent.domain.enums import ConnectorMode, Platform


class MetaConnector(HybridPlaceholderConnector):
    def __init__(self, settings: AppSettings) -> None:
        super().__init__(
            platform=Platform.META,
            mode=ConnectorMode(settings.meta_mode),
            required_values={
                "META_ACCESS_TOKEN": settings.meta_access_token,
                "META_PAGE_ID": settings.meta_page_id,
            },
        )

