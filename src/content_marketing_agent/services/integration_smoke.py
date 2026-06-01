from __future__ import annotations

from dataclasses import dataclass

from content_marketing_agent.config.settings import AppSettings
from content_marketing_agent.connectors.registry import build_connector_registry
from content_marketing_agent.domain.enums import ContentFormat, ContentStatus, Platform
from content_marketing_agent.domain.models import ContentItem


@dataclass(frozen=True)
class IntegrationSmokeResult:
    platform: str
    operation: str
    requested_mode: str
    active_mode: str
    success: bool
    details: str


def run_integration_smoke(settings: AppSettings) -> list[IntegrationSmokeResult]:
    registry = build_connector_registry(settings)
    results: list[IntegrationSmokeResult] = []

    for capability in registry.capabilities():
        connector = registry.get(capability.platform)
        if capability.can_fetch_metrics:
            snapshots = connector.fetch_metrics(["smoke-check-item"])
            results.append(
                IntegrationSmokeResult(
                    platform=capability.platform.value,
                    operation="fetch_metrics",
                    requested_mode=capability.requested_mode.value,
                    active_mode=capability.active_mode.value,
                    success=True,
                    details=f"Fetched {len(snapshots)} snapshots.",
                )
            )
            continue

        if capability.can_create_draft:
            smoke_item = _smoke_content_item(capability.platform)
            publication = connector.create_draft(smoke_item)
            results.append(
                IntegrationSmokeResult(
                    platform=capability.platform.value,
                    operation="create_draft",
                    requested_mode=capability.requested_mode.value,
                    active_mode=capability.active_mode.value,
                    success=publication.success,
                    details=publication.human_message or publication.error_code or "Draft operation completed.",
                )
            )
            continue

        results.append(
            IntegrationSmokeResult(
                platform=capability.platform.value,
                operation="none",
                requested_mode=capability.requested_mode.value,
                active_mode=capability.active_mode.value,
                success=False,
                details=capability.reason or "No safe smoke operation available.",
            )
        )

    return results


def _smoke_content_item(platform: Platform) -> ContentItem:
    format_map = {
        Platform.WORDPRESS: ContentFormat.BLOG_POST,
        Platform.HUBSPOT: ContentFormat.EMAIL_CAMPAIGN,
        Platform.LINKEDIN: ContentFormat.SOCIAL_POST,
        Platform.META: ContentFormat.SOCIAL_POST,
        Platform.SEARCH: ContentFormat.BLOG_POST,
        Platform.GA4: ContentFormat.BLOG_POST,
    }
    return ContentItem(
        title=f"Smoke test draft for {platform.value}",
        body="Integration smoke test payload.",
        format=format_map.get(platform, ContentFormat.BLOG_POST),
        target_platform=platform,
        status=ContentStatus.APPROVED,
    )
