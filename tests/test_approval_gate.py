import pytest

from content_marketing_agent.config.settings import AppSettings
from content_marketing_agent.domain.enums import ContentFormat, ContentStatus, Platform
from content_marketing_agent.domain.models import ContentItem
from content_marketing_agent.services.approval import ApprovalError, ensure_publish_allowed


def make_content_item(status: ContentStatus) -> ContentItem:
    return ContentItem(
        title="Demo blog",
        format=ContentFormat.BLOG_POST,
        target_platform=Platform.WORDPRESS,
        status=status,
    )


def test_publish_requires_approved_status() -> None:
    settings = AppSettings(allow_real_publish=True)
    content_item = make_content_item(ContentStatus.READY_FOR_REVIEW)

    with pytest.raises(ApprovalError, match="approved"):
        ensure_publish_allowed(content_item, settings)


def test_publish_requires_runtime_flag() -> None:
    settings = AppSettings(allow_real_publish=False)
    content_item = make_content_item(ContentStatus.APPROVED)

    with pytest.raises(ApprovalError, match="ALLOW_REAL_PUBLISH"):
        ensure_publish_allowed(content_item, settings)


def test_approved_item_can_publish_when_runtime_flag_enabled() -> None:
    settings = AppSettings(allow_real_publish=True)
    content_item = make_content_item(ContentStatus.APPROVED)

    ensure_publish_allowed(content_item, settings)

