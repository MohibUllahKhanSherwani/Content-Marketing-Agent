from content_marketing_agent.config.settings import AppSettings
from content_marketing_agent.domain.enums import ContentStatus
from content_marketing_agent.domain.models import ContentItem


class ApprovalError(ValueError):
    """Raised when a content item is not allowed to publish."""


def ensure_publish_allowed(content_item: ContentItem, settings: AppSettings) -> None:
    if content_item.status != ContentStatus.APPROVED:
        raise ApprovalError("Content item must be approved before real publishing.")
    if not settings.allow_real_publish:
        raise ApprovalError("ALLOW_REAL_PUBLISH must be true before real publishing.")

