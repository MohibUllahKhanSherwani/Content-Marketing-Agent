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


# Helper used as a default_factory so every model gets a proper timezone-aware timestamp
def utc_now() -> datetime:
    return datetime.now(timezone.utc)

# Default factory used to fresh unique ids everytime
class ClientProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))  # auto-generate unique ID
    name: str  # client or brand name
    industry: str | None = None  # optional industry/category label
    audience: list[str] = Field(default_factory=list)  # target audience segments
    offers: list[str] = Field(default_factory=list)  # products/services being marketed
    competitors: list[str] = Field(default_factory=list)  # competitor names to watch
    brand_voice: str | None = None  # tone/style guidance for generated content
    banned_claims: list[str] = Field(default_factory=list)  # claims the agent must not make
    preferred_ctas: list[str] = Field(default_factory=list)  # approved calls to action


class CampaignBrief(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))  # auto-generate campaign ID
    client_profile_id: str  # links the campaign back to its client profile
    objective: str  # campaign goal, e.g. "increase signups"
    audience: str  # campaign-specific targeting note
    funnel_stage: str  # TOFU/MOFU/BOFU or similar journey stage
    channels: list[Platform]  # platforms this campaign targets
    keywords: list[str] = Field(default_factory=list)  # SEO/AEO keywords and themes
    offer: str | None = None  # specific promoted offer, if any
    cta: str | None = None  # primary call to action
    success_metrics: list[str] = Field(default_factory=list)  # how success is measured
    created_at: datetime = Field(default_factory=utc_now)  # campaign creation timestamp


class ContentItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))  # auto-generate content ID
    campaign_brief_id: str | None = None  # optional link to the campaign that produced it
    title: str  # human-readable content title
    format: ContentFormat  # blog, email, social post, ad, landing page, or case study
    target_platform: Platform  # where this content is intended to go
    status: ContentStatus = ContentStatus.IDEA  # lifecycle state from idea to published/archive
    body: str = ""  # actual generated or edited content
    seo_title: str | None = None  # search-specific title when different from title
    meta_description: str | None = None  # web/blog metadata
    cta: str | None = None  # content-specific call to action
    scheduled_at: datetime | None = None  # planned publish time, if scheduled
    created_at: datetime = Field(default_factory=utc_now)  # content creation timestamp
    updated_at: datetime = Field(default_factory=utc_now)  # last update timestamp
    metadata: dict[str, Any] = Field(default_factory=dict)  # platform-specific extras


class ApprovalDecision(BaseModel):
    content_item_id: str  # content item being reviewed
    approver: str  # human reviewer name or ID
    approved: bool  # yes/no decision
    notes: str | None = None  # reviewer feedback or change request
    decided_at: datetime = Field(default_factory=utc_now)  # review timestamp


class ConnectorCapabilities(BaseModel):
    platform: Platform  # platform being checked
    requested_mode: ConnectorMode  # mode requested by config: real, mock, or auto
    active_mode: ConnectorMode  # mode actually used after credential/capability checks
    can_create_draft: bool = False  # whether draft creation is available
    can_schedule: bool = False  # whether scheduling is available
    can_publish: bool = False  # whether public publishing is available
    can_fetch_metrics: bool = False  # whether analytics reads are available
    reason: str | None = None  # why active mode/capabilities differ from requested


class ConnectorResult(BaseModel):
    platform: Platform  # platform that handled the operation
    mode: ConnectorMode  # real or mock mode used for this result
    operation: str  # attempted operation: create_draft, schedule, publish, etc.
    success: bool  # whether the operation succeeded
    platform_id: str | None = None  # external platform ID, real or mock
    platform_url: str | None = None  # external URL, real or mock
    status: str | None = None  # platform-specific result status
    error_code: str | None = None  # machine-readable failure reason
    human_message: str | None = None  # operator-facing success/error message
    raw_response: dict[str, Any] = Field(default_factory=dict)  # safe debug payload


class PerformanceSnapshot(BaseModel):
    content_item_id: str | None = None  # optional metric link to one content item
    campaign_brief_id: str | None = None  # optional metric link to a campaign
    platform: Platform  # platform the metrics came from
    source_mode: ConnectorMode  # real or mock metrics source
    impressions: int = 0  # views/reach count
    clicks: int = 0  # click count
    engagements: int = 0  # likes/comments/shares/reactions/etc.
    conversions: int = 0  # configured conversion count
    spend: float = 0.0  # ad spend, if applicable
    captured_at: datetime = Field(default_factory=utc_now)  # metric capture timestamp

    @property
    def engagement_rate(self) -> float:
        if self.impressions <= 0:
            return 0.0
        return self.engagements / self.impressions
