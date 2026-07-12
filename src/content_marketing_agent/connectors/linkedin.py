"""LinkedIn connector — supports personal profile (urn:li:person:XXX) and org page
(urn:li:organization:XXX) posting via the same LinkedIn Posts REST API endpoint.

Set LINKEDIN_ORG_URN to a person URN if you do not have a company page:
    LINKEDIN_ORG_URN=urn:li:person:<your_member_id>

To find your member ID, call:
    GET https://api.linkedin.com/v2/userinfo
with your access token and read the ``sub`` field.
"""

from __future__ import annotations

import httpx

from content_marketing_agent.config.settings import AppSettings
from content_marketing_agent.connectors.hybrid import HybridPlaceholderConnector
from content_marketing_agent.domain.enums import ConnectorMode, Platform, PublicationOperation
from content_marketing_agent.domain.models import ConnectorResult, ContentItem

# LinkedIn REST API base (versioned header required)
_LINKEDIN_API_BASE = "https://api.linkedin.com"
_LINKEDIN_API_VERSION = "202504"  # bump quarterly per LinkedIn versioning policy
_TIMEOUT = 15.0


class LinkedInConnector(HybridPlaceholderConnector):
    """LinkedIn platform connector.

    ``LINKEDIN_ORG_URN`` accepts either:
    - ``urn:li:person:<member_id>``  — post as your personal profile
    - ``urn:li:organization:<org_id>`` — post as a company page
    """

    real_implementation_ready = True  # real HTTP implementation is wired

    def __init__(self, settings: AppSettings) -> None:
        super().__init__(
            platform=Platform.LINKEDIN,
            mode=ConnectorMode(settings.linkedin_mode),
            required_values={
                "LINKEDIN_ACCESS_TOKEN": settings.linkedin_access_token,
                "LINKEDIN_ORG_URN": settings.linkedin_org_urn,
            },
        )
        self._token: str | None = settings.linkedin_access_token
        self._author_urn: str | None = settings.linkedin_org_urn

    # ------------------------------------------------------------------
    # Public operations — both call the same LinkedIn Posts endpoint.
    # LinkedIn has no server-side draft state; our DB tracks draft/publish.
    # ------------------------------------------------------------------

    def create_draft(self, content_item: ContentItem) -> ConnectorResult:
        """Create a LinkedIn post (recorded locally as a draft)."""
        capabilities = self.check_capabilities()
        if capabilities.active_mode == ConnectorMode.MOCK:
            return self.mock.create_draft(content_item)
        return self._post_to_linkedin(content_item, PublicationOperation.CREATE_DRAFT)

    def publish(self, content_item: ContentItem) -> ConnectorResult:
        """Publish a LinkedIn post immediately."""
        capabilities = self.check_capabilities()
        if capabilities.active_mode == ConnectorMode.MOCK:
            return self.mock.publish(content_item)
        return self._post_to_linkedin(content_item, PublicationOperation.PUBLISH)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _post_to_linkedin(self, content_item: ContentItem, operation: PublicationOperation) -> ConnectorResult:
        """Call POST /rest/posts and return a structured ConnectorResult."""
        text = (
            content_item.body
            or content_item.title
            or f"New post: {content_item.content_format.value}"
        )
        payload = {
            "author": self._author_urn,
            "commentary": text[:3000],  # LinkedIn hard limit
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        }
        headers = {
            "Authorization": f"Bearer {self._token}",
            "LinkedIn-Version": _LINKEDIN_API_VERSION,
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json",
        }
        try:
            with httpx.Client(timeout=_TIMEOUT) as client:
                response = client.post(
                    f"{_LINKEDIN_API_BASE}/rest/posts",
                    headers=headers,
                    json=payload,
                )
            if response.status_code == 201:
                # LinkedIn returns the post URN in the X-RestLi-Id header
                post_urn = response.headers.get("x-restli-id", "")
                post_url = (
                    f"https://www.linkedin.com/feed/update/{post_urn}"
                    if post_urn
                    else "https://www.linkedin.com/feed/"
                )
                return ConnectorResult(
                    platform=self.platform,
                    mode=ConnectorMode.REAL,
                    operation=operation.value,
                    success=True,
                    platform_id=post_urn or "linkedin_post_created",
                    platform_url=post_url,
                    human_message="LinkedIn post created successfully.",
                    raw_response={"status": response.status_code, "post_urn": post_urn},
                )
            # Map LinkedIn error codes to structured error
            error_body: dict = {}
            try:
                error_body = response.json()
            except Exception:
                pass
            error_code = error_body.get("errorDetails", {}).get("inputErrors", [{}])[0].get(
                "code", "linkedin_http_error"
            ) if error_body else "linkedin_http_error"
            return ConnectorResult(
                platform=self.platform,
                mode=ConnectorMode.REAL,
                operation=operation.value,
                success=False,
                error_code=error_code,
                human_message=(
                    f"LinkedIn API returned {response.status_code}: "
                    f"{error_body.get('message', response.text[:200])}"
                ),
                raw_response={"status": response.status_code, "body": error_body},
            )
        except httpx.TimeoutException:
            return ConnectorResult(
                platform=self.platform,
                mode=ConnectorMode.REAL,
                operation=operation.value,
                success=False,
                error_code="linkedin_timeout",
                human_message="LinkedIn API request timed out.",
            )
        except httpx.RequestError as exc:
            return ConnectorResult(
                platform=self.platform,
                mode=ConnectorMode.REAL,
                operation=operation.value,
                success=False,
                error_code="linkedin_network_error",
                human_message=f"LinkedIn network error: {exc}",
            )

