from __future__ import annotations

from dataclasses import dataclass

from content_marketing_agent.config.settings import AppSettings
from content_marketing_agent.domain.enums import ContentFormat, ContentStatus, Platform
from content_marketing_agent.domain.models import ContentItem


@dataclass(frozen=True)
class ProductionResult:
    generation_mode: str
    items: list[ContentItem]


def produce_content_drafts(
    *,
    objective: str,
    settings: AppSettings,
    items_per_channel: int = 1,
) -> ProductionResult:
    generation_mode = _resolve_generation_mode(settings)
    templates = _content_templates(objective, generation_mode, items_per_channel)
    drafted_items = [
        ContentItem(
            title=title,
            format=content_format,
            target_platform=platform,
            status=ContentStatus.DRAFTED,
            body=body,
            metadata={
                "generation_mode": generation_mode,
                "objective": objective,
                "provider": "azure_openai" if generation_mode == "real" else "mock_generator",
            },
        )
        for title, content_format, platform, body in templates
    ]
    return ProductionResult(generation_mode=generation_mode, items=drafted_items)


def _resolve_generation_mode(settings: AppSettings) -> str:
    azure_ready = bool(settings.azure_api_key and settings.azure_endpoint)
    if settings.azure_openai_mode == "real" and azure_ready:
        return "real"
    return "mock"


def _content_templates(
    objective: str, generation_mode: str, items_per_channel: int
) -> list[tuple[str, ContentFormat, Platform, str]]:
    mode_prefix = "REAL" if generation_mode == "real" else "MOCK"
    templates: list[tuple[ContentFormat, Platform, str]] = [
        (ContentFormat.BLOG_POST, Platform.WORDPRESS, "Blog"),
        (ContentFormat.EMAIL_CAMPAIGN, Platform.HUBSPOT, "Email"),
        (ContentFormat.SOCIAL_POST, Platform.LINKEDIN, "Social"),
        (ContentFormat.AD_VARIANT, Platform.META, "Ad"),
        (ContentFormat.LANDING_PAGE, Platform.WORDPRESS, "Landing Page"),
        (ContentFormat.CASE_STUDY, Platform.WORDPRESS, "Case Study"),
    ]
    output: list[tuple[str, ContentFormat, Platform, str]] = []
    for content_format, platform, label in templates:
        for index in range(1, items_per_channel + 1):
            title = f"{label} Draft {index}: {objective}"
            body = (
                f"[{mode_prefix}] {label} draft for objective: {objective}. "
                "Tone should adapt from technical to conversational while preserving brand voice."
            )
            output.append((title, content_format, platform, body))
    return output
