from content_marketing_agent.config.settings import AppSettings
from content_marketing_agent.connectors.hybrid import HybridPlaceholderConnector
from content_marketing_agent.domain.enums import ConnectorMode, Platform


class LinkedInConnector(HybridPlaceholderConnector):
    def __init__(self, settings: AppSettings) -> None:
        super().__init__(
            platform=Platform.LINKEDIN,
            mode=ConnectorMode(settings.linkedin_mode),
            required_values={
                "LINKEDIN_ACCESS_TOKEN": settings.linkedin_access_token,
                "LINKEDIN_ORG_URN": settings.linkedin_org_urn,
            },
        )

