from __future__ import annotations

from dataclasses import dataclass

from content_marketing_agent.config.settings import AppSettings
from content_marketing_agent.connectors.registry import build_connector_registry
from content_marketing_agent.domain.enums import Platform
from content_marketing_agent.domain.models import ContentItem, PerformanceSnapshot


@dataclass(frozen=True)
class AnalyticsSummary:
    snapshots_count: int
    totals: dict[str, int | float]
    by_platform: dict[str, dict[str, int | float]]


def collect_monthly_snapshots(
    *, settings: AppSettings, content_items: list[ContentItem]
) -> list[PerformanceSnapshot]:
    registry = build_connector_registry(settings)
    item_ids_by_platform: dict[Platform, list[str]] = {}
    for item in content_items:
        item_ids_by_platform.setdefault(item.target_platform, []).append(item.id)

    snapshots: list[PerformanceSnapshot] = []
    for platform, item_ids in item_ids_by_platform.items():
        connector = registry.get(platform)
        snapshots.extend(connector.fetch_metrics(item_ids))
    return snapshots


def summarize_snapshots(snapshots: list[PerformanceSnapshot]) -> AnalyticsSummary:
    totals: dict[str, int | float] = {
        "impressions": 0,
        "clicks": 0,
        "engagements": 0,
        "conversions": 0,
        "spend": 0.0,
    }
    by_platform: dict[str, dict[str, int | float]] = {}
    for snapshot in snapshots:
        platform_key = snapshot.platform.value
        platform_totals = by_platform.setdefault(
            platform_key,
            {"impressions": 0, "clicks": 0, "engagements": 0, "conversions": 0, "spend": 0.0},
        )
        platform_totals["impressions"] += snapshot.impressions
        platform_totals["clicks"] += snapshot.clicks
        platform_totals["engagements"] += snapshot.engagements
        platform_totals["conversions"] += snapshot.conversions
        platform_totals["spend"] += snapshot.spend

        totals["impressions"] += snapshot.impressions
        totals["clicks"] += snapshot.clicks
        totals["engagements"] += snapshot.engagements
        totals["conversions"] += snapshot.conversions
        totals["spend"] += snapshot.spend

    return AnalyticsSummary(
        snapshots_count=len(snapshots),
        totals=totals,
        by_platform=by_platform,
    )
