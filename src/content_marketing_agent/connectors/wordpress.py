from content_marketing_agent.config.settings import AppSettings
from content_marketing_agent.connectors.hybrid import HybridPlaceholderConnector
from content_marketing_agent.domain.enums import ConnectorMode, Platform


class WordPressConnector(HybridPlaceholderConnector):
    def __init__(self, settings: AppSettings) -> None:
        super().__init__(
            platform=Platform.WORDPRESS,
            mode=ConnectorMode(settings.wordpress_mode),
            required_values={
                "WORDPRESS_BASE_URL": settings.wordpress_base_url,
                "WORDPRESS_USERNAME": settings.wordpress_username,
                "WORDPRESS_APP_PASSWORD": settings.wordpress_app_password,
            },
        )

