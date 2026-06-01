import httpx

from content_marketing_agent.config.settings import AppSettings
from content_marketing_agent.connectors.hybrid import HybridPlaceholderConnector
from content_marketing_agent.domain.enums import (
    ConnectorMode,
    Platform,
    PublicationOperation,
)
from content_marketing_agent.domain.models import (
    ConnectorCapabilities,
    ConnectorResult,
    ContentItem,
)


class WordPressConnector(HybridPlaceholderConnector):
    real_implementation_ready = True

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
        self._settings = settings

    def check_capabilities(self) -> ConnectorCapabilities:
        missing = [name for name, value in self.required_values.items() if not value]
        if self.mode == ConnectorMode.MOCK:
            return self.mock.check_capabilities()
        if missing:
            if self.mode == ConnectorMode.AUTO:
                capabilities = self.mock.check_capabilities()
                capabilities.requested_mode = self.mode
                capabilities.reason = f"Missing credentials: {', '.join(missing)}."
                return capabilities
            return ConnectorCapabilities(
                platform=self.platform,
                requested_mode=self.mode,
                active_mode=ConnectorMode.REAL,
                reason=f"Missing credentials: {', '.join(missing)}.",
            )
        return ConnectorCapabilities(
            platform=self.platform,
            requested_mode=self.mode,
            active_mode=ConnectorMode.REAL,
            can_create_draft=True,
            can_schedule=False,
            can_publish=False,
            can_fetch_metrics=False,
            reason="WordPress real draft creation is available.",
        )

    def create_draft(self, content_item: ContentItem) -> ConnectorResult:
        capabilities = self.check_capabilities()
        if capabilities.active_mode == ConnectorMode.MOCK:
            return self.mock.create_draft(content_item)

        base_url = (self._settings.wordpress_base_url or "").rstrip("/")
        username = self._settings.wordpress_username or ""
        app_password = self._settings.wordpress_app_password or ""
        payload: dict[str, object] = {
            "title": content_item.title,
            "content": content_item.body,
            "status": "draft",
        }
        if self._settings.wordpress_default_author_id is not None:
            payload["author"] = self._settings.wordpress_default_author_id

        try:
            with httpx.Client(timeout=20.0, auth=(username, app_password)) as client:
                response = client.post(f"{base_url}/wp-json/wp/v2/posts", json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as error:
            return ConnectorResult(
                platform=self.platform,
                mode=ConnectorMode.REAL,
                operation=PublicationOperation.CREATE_DRAFT.value,
                success=False,
                error_code="wordpress_http_error",
                human_message=f"WordPress draft creation failed with status {error.response.status_code}.",
            )
        except httpx.HTTPError as error:
            return ConnectorResult(
                platform=self.platform,
                mode=ConnectorMode.REAL,
                operation=PublicationOperation.CREATE_DRAFT.value,
                success=False,
                error_code="wordpress_network_error",
                human_message=f"WordPress draft creation failed: {error.__class__.__name__}.",
            )

        return ConnectorResult(
            platform=self.platform,
            mode=ConnectorMode.REAL,
            operation=PublicationOperation.CREATE_DRAFT.value,
            success=True,
            platform_id=str(data.get("id")),
            platform_url=str(data.get("link") or data.get("guid", {}).get("rendered", "")),
            status=str(data.get("status", "draft")),
            human_message="WordPress draft created successfully.",
            raw_response={"id": data.get("id"), "status": data.get("status"), "link": data.get("link")},
        )
