import httpx

from content_marketing_agent.config.settings import AppSettings
from content_marketing_agent.connectors.hybrid import HybridPlaceholderConnector
from content_marketing_agent.domain.enums import ConnectorMode, Platform, PublicationOperation
from content_marketing_agent.domain.models import (
    ConnectorCapabilities,
    ConnectorResult,
    ContentItem,
)


class HubSpotConnector(HybridPlaceholderConnector):
    real_implementation_ready = True

    def __init__(self, settings: AppSettings) -> None:
        super().__init__(
            platform=Platform.HUBSPOT,
            mode=ConnectorMode(settings.hubspot_mode),
            required_values={
                "HUBSPOT_PRIVATE_APP_TOKEN": settings.hubspot_private_app_token,
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
            reason="HubSpot real email draft creation is available.",
        )

    def create_draft(self, content_item: ContentItem) -> ConnectorResult:
        capabilities = self.check_capabilities()
        if capabilities.active_mode == ConnectorMode.MOCK:
            return self.mock.create_draft(content_item)

        token = self._settings.hubspot_private_app_token or ""
        payload = {
            "name": content_item.title,
            "subject": content_item.title,
            "content": {"widgets": {}, "postBody": content_item.body},
            "isPublished": False,
        }
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        try:
            with httpx.Client(timeout=20.0, headers=headers) as client:
                response = client.post(
                    "https://api.hubapi.com/marketing/v3/marketing-emails/",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as error:
            return ConnectorResult(
                platform=self.platform,
                mode=ConnectorMode.REAL,
                operation=PublicationOperation.CREATE_DRAFT.value,
                success=False,
                error_code="hubspot_http_error",
                human_message=f"HubSpot draft creation failed with status {error.response.status_code}.",
            )
        except httpx.HTTPError as error:
            return ConnectorResult(
                platform=self.platform,
                mode=ConnectorMode.REAL,
                operation=PublicationOperation.CREATE_DRAFT.value,
                success=False,
                error_code="hubspot_network_error",
                human_message=f"HubSpot draft creation failed: {error.__class__.__name__}.",
            )

        draft_id = str(data.get("id", ""))
        return ConnectorResult(
            platform=self.platform,
            mode=ConnectorMode.REAL,
            operation=PublicationOperation.CREATE_DRAFT.value,
            success=True,
            platform_id=draft_id or None,
            platform_url=f"https://app.hubspot.com/email/{draft_id}" if draft_id else None,
            status="draft",
            human_message="HubSpot email draft created successfully.",
            raw_response={"id": data.get("id"), "name": data.get("name"), "isPublished": data.get("isPublished")},
        )
