from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from content_marketing_agent.domain.enums import (
    ConnectorMode,
    ContentFormat,
    ContentStatus,
    Platform,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ClientProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    industry: str | None = None
    audience: list[str] = Field(default_factory=list)
    offers: list[str] = Field(default_factory=list)
    competitors: list[str] = Field(default_factory=list)
    brand_voice: str | None = None
    banned_claims: list[str] = Field(default_factory=list)
    preferred_ctas: list[str] = Field(default_factory=list)


class CampaignBrief(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    client_profile_id: str
    objective: str
    audience: str
    funnel_stage: str
    channels: list[Platform]
    keywords: list[str] = Field(default_factory=list)
    offer: str | None = None
    cta: str | None = None
    success_metrics: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)


class ContentItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    campaign_brief_id: str | None = None
    title: str
    format: ContentFormat
    target_platform: Platform
    status: ContentStatus = ContentStatus.IDEA
    body: str = ""
    seo_title: str | None = None
    meta_description: str | None = None
    cta: str | None = None
    scheduled_at: datetime | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ApprovalDecision(BaseModel):
    content_item_id: str
    approver: str
    approved: bool
    notes: str | None = None
    decided_at: datetime = Field(default_factory=utc_now)


class ConnectorCapabilities(BaseModel):
    platform: Platform
    requested_mode: ConnectorMode
    active_mode: ConnectorMode
    can_create_draft: bool = False
    can_schedule: bool = False
    can_publish: bool = False
    can_fetch_metrics: bool = False
    reason: str | None = None


class ConnectorResult(BaseModel):
    platform: Platform
    mode: ConnectorMode
    operation: str
    success: bool
    platform_id: str | None = None
    platform_url: str | None = None
    status: str | None = None
    error_code: str | None = None
    human_message: str | None = None
    raw_response: dict[str, Any] = Field(default_factory=dict)


class PerformanceSnapshot(BaseModel):
    content_item_id: str | None = None
    campaign_brief_id: str | None = None
    platform: Platform
    source_mode: ConnectorMode
    impressions: int = 0
    clicks: int = 0
    engagements: int = 0
    conversions: int = 0
    spend: float = 0.0
    captured_at: datetime = Field(default_factory=utc_now)

    @property
    def engagement_rate(self) -> float:
        if self.impressions <= 0:
            return 0.0
        return self.engagements / self.impressions

