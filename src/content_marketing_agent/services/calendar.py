from content_marketing_agent.domain.enums import ContentFormat, Platform
from content_marketing_agent.domain.models import ContentItem


def demo_calendar_items() -> list[ContentItem]:
    """Small deterministic calendar seed for local demos."""

    return [
        ContentItem(
            title="How AI Agents Change Content Operations",
            format=ContentFormat.BLOG_POST,
            target_platform=Platform.WORDPRESS,
        ),
        ContentItem(
            title="Weekly Email: Turn Content Chaos Into Calendar Clarity",
            format=ContentFormat.EMAIL_CAMPAIGN,
            target_platform=Platform.HUBSPOT,
        ),
        ContentItem(
            title="Daily LinkedIn Thought Leadership Post",
            format=ContentFormat.SOCIAL_POST,
            target_platform=Platform.LINKEDIN,
        ),
    ]

