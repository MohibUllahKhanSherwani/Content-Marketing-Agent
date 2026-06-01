from __future__ import annotations

from dataclasses import dataclass

from crewai.flow import Flow, listen, start
from pydantic import BaseModel, Field

from content_marketing_agent.config.settings import AppSettings, get_settings
from content_marketing_agent.services.analytics import (
    collect_monthly_snapshots,
    summarize_snapshots,
)
from content_marketing_agent.services.content_items import ContentItemStore
from content_marketing_agent.services.planning import build_monthly_plan
from content_marketing_agent.services.production import produce_content_drafts


@dataclass(frozen=True)
class PlanStageResult:
    month: str
    items_created: int
    summary: dict[str, int]


@dataclass(frozen=True)
class ProductionStageResult:
    generation_mode: str
    items_created: int


@dataclass(frozen=True)
class AnalyticsStageResult:
    snapshots_collected: int
    snapshots_persisted: int
    by_platform: dict[str, dict[str, int | float]]


class MonthlyContentState(BaseModel):
    month: str = "2026-07"
    blog_posts: int = 8
    objective: str = "Generate monthly multi-channel content for campaign goals."
    items_per_channel: int = 1
    strict_real: bool = False
    campaign_id: str | None = None
    plan: dict[str, object] = Field(default_factory=dict)
    production: dict[str, object] = Field(default_factory=dict)
    analytics: dict[str, object] = Field(default_factory=dict)
    completed: bool = False


class MonthlyContentFlow(Flow[MonthlyContentState]):
    """Service-backed monthly orchestration for local run/demo usage."""

    def __init__(
        self,
        *,
        settings: AppSettings | None = None,
        content_item_store: ContentItemStore | None = None,
    ) -> None:
        super().__init__()
        self._settings = settings or get_settings()
        self._content_item_store = content_item_store or ContentItemStore.from_settings(self._settings)

    @start()
    def prepare_campaign(self) -> PlanStageResult:
        plan = build_monthly_plan(
            month=self.state.month,
            blog_posts=self.state.blog_posts,
            campaign_brief_id=self.state.campaign_id,
        )
        persisted = self._content_item_store.add_items(plan.items)
        self.state.plan = {"items_created": len(persisted), "summary": plan.summary}
        return PlanStageResult(
            month=self.state.month,
            items_created=len(persisted),
            summary=plan.summary,
        )

    @listen(prepare_campaign)
    def produce_content(self, _: PlanStageResult) -> ProductionStageResult:
        produced = produce_content_drafts(
            objective=self.state.objective,
            settings=self._settings,
            items_per_channel=self.state.items_per_channel,
            strict_real=self.state.strict_real,
            campaign_brief_id=self.state.campaign_id,
        )
        persisted = self._content_item_store.add_items(produced.items)
        self.state.production = {
            "generation_mode": produced.generation_mode,
            "items_created": len(persisted),
        }
        return ProductionStageResult(
            generation_mode=produced.generation_mode,
            items_created=len(persisted),
        )

    @listen(produce_content)
    def summarize(self, _: ProductionStageResult) -> AnalyticsStageResult:
        snapshots = collect_monthly_snapshots(
            settings=self._settings,
            content_items=self._content_item_store.list_items(),
        )
        persisted_count = self._content_item_store.record_performance_snapshots(snapshots)
        summary = summarize_snapshots(snapshots)
        self.state.analytics = {
            "snapshots_collected": len(snapshots),
            "snapshots_persisted": persisted_count,
            "by_platform": summary.by_platform,
        }
        self.state.completed = True
        return AnalyticsStageResult(
            snapshots_collected=len(snapshots),
            snapshots_persisted=persisted_count,
            by_platform=summary.by_platform,
        )
