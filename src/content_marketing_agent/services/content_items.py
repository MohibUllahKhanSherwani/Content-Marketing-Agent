from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON
from sqlalchemy.pool import StaticPool
from sqlmodel import Column, Field, Session, SQLModel, col, create_engine, delete, select

from content_marketing_agent.config.settings import AppSettings
from content_marketing_agent.domain.enums import (
    ConnectorMode,
    ContentFormat,
    ContentStatus,
    Platform,
)
from content_marketing_agent.domain.models import (
    CampaignBrief,
    ClientProfile,
    ConnectorResult,
    ContentItem,
    PerformanceSnapshot,
    utc_now,
)
from content_marketing_agent.services.calendar import demo_calendar_items
from content_marketing_agent.storage.database import create_db_engine


class ContentItemNotFoundError(LookupError):
    """Raised when a content item cannot be found."""


class ClientProfileNotFoundError(LookupError):
    """Raised when a client profile cannot be found."""


class CampaignNotFoundError(LookupError):
    """Raised when a campaign cannot be found."""


class ContentItemRecord(SQLModel, table=True):
    id: str = Field(primary_key=True)
    campaign_brief_id: str | None = None
    title: str
    format: str
    target_platform: str
    status: str
    body: str = ""
    seo_title: str | None = None
    meta_description: str | None = None
    cta: str | None = None
    scheduled_at: datetime | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    metadata_json: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))


class PublicationRecord(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    content_item_id: str = Field(index=True)
    platform: str
    mode: str
    operation: str
    success: bool
    platform_id: str | None = None
    platform_url: str | None = None
    status: str | None = None
    error_code: str | None = None
    human_message: str | None = None
    raw_response_json: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=utc_now)


class ApprovalDecisionRecord(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    content_item_id: str = Field(index=True)
    approver: str
    approved: bool
    notes: str | None = None
    decided_at: datetime = Field(default_factory=utc_now)


class PerformanceSnapshotRecord(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    content_item_id: str | None = Field(default=None, index=True)
    campaign_brief_id: str | None = None
    platform: str
    source_mode: str
    impressions: int = 0
    clicks: int = 0
    engagements: int = 0
    conversions: int = 0
    spend: float = 0.0
    captured_at: datetime = Field(default_factory=utc_now)


class ClientProfileRecord(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str
    industry: str | None = None
    audience_json: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    offers_json: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    competitors_json: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    brand_voice: str | None = None
    banned_claims_json: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    preferred_ctas_json: list[str] = Field(default_factory=list, sa_column=Column(JSON))


class CampaignBriefRecord(SQLModel, table=True):
    id: str = Field(primary_key=True)
    client_profile_id: str = Field(index=True)
    objective: str
    audience: str
    funnel_stage: str
    channels_json: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    keywords_json: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    offer: str | None = None
    cta: str | None = None
    success_metrics_json: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=utc_now)


class ContentItemStore:
    """SQLModel-backed store for content items and publication audit records."""

    def __init__(self, *, settings: AppSettings | None = None, seed_if_empty: bool = True) -> None:
        if settings is None:
            self._engine = create_engine(
                "sqlite://",
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
        else:
            self._engine = create_db_engine(settings)
        SQLModel.metadata.create_all(self._engine)
        if seed_if_empty and self._is_empty():
            self.seed_demo_items()

    @classmethod
    def from_settings(cls, settings: AppSettings) -> ContentItemStore:
        return cls(settings=settings, seed_if_empty=True)

    def list_items(self) -> list[ContentItem]:
        with Session(self._engine) as session:
            records = session.exec(select(ContentItemRecord)).all()
        return [self._record_to_model(record) for record in records]

    def list_items_by_campaign(self, campaign_id: str) -> list[ContentItem]:
        with Session(self._engine) as session:
            records = session.exec(
                select(ContentItemRecord).where(ContentItemRecord.campaign_brief_id == campaign_id)
            ).all()
        return [self._record_to_model(record) for record in records]

    def list_scheduled_items(self) -> list[ContentItem]:
        with Session(self._engine) as session:
            records = session.exec(
                select(ContentItemRecord).where(col(ContentItemRecord.scheduled_at).is_not(None))
            ).all()
        return [self._record_to_model(record) for record in records]

    def get_item(self, content_item_id: str) -> ContentItem:
        with Session(self._engine) as session:
            record = session.get(ContentItemRecord, content_item_id)
        if record is None:
            raise ContentItemNotFoundError(content_item_id)
        return self._record_to_model(record)

    def approve_item(
        self,
        content_item_id: str,
        *,
        approver: str = "human_reviewer",
        notes: str | None = None,
    ) -> ContentItem:
        with Session(self._engine) as session:
            record = session.get(ContentItemRecord, content_item_id)
            if record is None:
                raise ContentItemNotFoundError(content_item_id)
            record.status = ContentStatus.APPROVED.value
            record.updated_at = utc_now()
            session.add(
                ApprovalDecisionRecord(
                    content_item_id=content_item_id,
                    approver=approver,
                    approved=True,
                    notes=notes,
                )
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return self._record_to_model(record)

    def request_changes_item(
        self,
        content_item_id: str,
        *,
        approver: str = "human_reviewer",
        notes: str,
    ) -> ContentItem:
        with Session(self._engine) as session:
            record = session.get(ContentItemRecord, content_item_id)
            if record is None:
                raise ContentItemNotFoundError(content_item_id)
            record.status = ContentStatus.QA_FAILED.value
            record.updated_at = utc_now()
            session.add(
                ApprovalDecisionRecord(
                    content_item_id=content_item_id,
                    approver=approver,
                    approved=False,
                    notes=notes,
                )
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return self._record_to_model(record)

    def add_items(self, items: list[ContentItem]) -> list[ContentItem]:
        with Session(self._engine) as session:
            records = [self._model_to_record(item) for item in items]
            for record in records:
                session.add(record)
            session.commit()
        return items

    def update_status(self, content_item_id: str, status: ContentStatus) -> ContentItem:
        with Session(self._engine) as session:
            record = session.get(ContentItemRecord, content_item_id)
            if record is None:
                raise ContentItemNotFoundError(content_item_id)
            record.status = status.value
            record.updated_at = utc_now()
            session.add(record)
            session.commit()
            session.refresh(record)
            return self._record_to_model(record)

    def seed_demo_items(self) -> int:
        seeded_items = demo_calendar_items()
        with Session(self._engine) as session:
            session.exec(delete(PerformanceSnapshotRecord))
            session.exec(delete(ApprovalDecisionRecord))
            session.exec(delete(PublicationRecord))
            session.exec(delete(ContentItemRecord))
            for item in seeded_items:
                session.add(self._model_to_record(item))
            session.commit()
        return len(seeded_items)

    def record_publication(self, content_item_id: str, result: ConnectorResult) -> None:
        _ = self.get_item(content_item_id)
        with Session(self._engine) as session:
            session.add(
                PublicationRecord(
                    content_item_id=content_item_id,
                    platform=result.platform.value,
                    mode=result.mode.value,
                    operation=result.operation,
                    success=result.success,
                    platform_id=result.platform_id,
                    platform_url=result.platform_url,
                    status=result.status,
                    error_code=result.error_code,
                    human_message=result.human_message,
                    raw_response_json=result.raw_response,
                )
            )
            session.commit()

    def list_publications(self, content_item_id: str) -> list[ConnectorResult]:
        _ = self.get_item(content_item_id)
        with Session(self._engine) as session:
            records = session.exec(
                select(PublicationRecord).where(PublicationRecord.content_item_id == content_item_id)
            ).all()
        return [self._publication_record_to_model(record) for record in records]

    def list_approval_decisions(self, content_item_id: str) -> list[ApprovalDecisionRecord]:
        _ = self.get_item(content_item_id)
        with Session(self._engine) as session:
            records = session.exec(
                select(ApprovalDecisionRecord).where(
                    ApprovalDecisionRecord.content_item_id == content_item_id
                )
            ).all()
        return list(records)

    def record_performance_snapshots(self, snapshots: list[PerformanceSnapshot]) -> int:
        with Session(self._engine) as session:
            for snapshot in snapshots:
                session.add(
                    PerformanceSnapshotRecord(
                        content_item_id=snapshot.content_item_id,
                        campaign_brief_id=snapshot.campaign_brief_id,
                        platform=snapshot.platform.value,
                        source_mode=snapshot.source_mode.value,
                        impressions=snapshot.impressions,
                        clicks=snapshot.clicks,
                        engagements=snapshot.engagements,
                        conversions=snapshot.conversions,
                        spend=snapshot.spend,
                        captured_at=snapshot.captured_at,
                    )
                )
            session.commit()
        return len(snapshots)

    def list_performance_snapshots(self) -> list[PerformanceSnapshot]:
        with Session(self._engine) as session:
            records = session.exec(select(PerformanceSnapshotRecord)).all()
        return [self._performance_record_to_model(record) for record in records]

    def create_client_profile(self, profile: ClientProfile) -> ClientProfile:
        with Session(self._engine) as session:
            session.add(self._client_profile_to_record(profile))
            session.commit()
        return profile

    def get_client_profile(self, client_profile_id: str) -> ClientProfile:
        with Session(self._engine) as session:
            record = session.get(ClientProfileRecord, client_profile_id)
        if record is None:
            raise ClientProfileNotFoundError(client_profile_id)
        return self._client_profile_record_to_model(record)

    def create_campaign(self, campaign: CampaignBrief) -> CampaignBrief:
        _ = self.get_client_profile(campaign.client_profile_id)
        with Session(self._engine) as session:
            session.add(self._campaign_to_record(campaign))
            session.commit()
        return campaign

    def get_campaign(self, campaign_id: str) -> CampaignBrief:
        with Session(self._engine) as session:
            record = session.get(CampaignBriefRecord, campaign_id)
        if record is None:
            raise CampaignNotFoundError(campaign_id)
        return self._campaign_record_to_model(record)

    def _is_empty(self) -> bool:
        with Session(self._engine) as session:
            first = session.exec(select(ContentItemRecord.id)).first()
        return first is None

    @staticmethod
    def _model_to_record(item: ContentItem) -> ContentItemRecord:
        return ContentItemRecord(
            id=item.id,
            campaign_brief_id=item.campaign_brief_id,
            title=item.title,
            format=item.format.value,
            target_platform=item.target_platform.value,
            status=item.status.value,
            body=item.body,
            seo_title=item.seo_title,
            meta_description=item.meta_description,
            cta=item.cta,
            scheduled_at=item.scheduled_at,
            created_at=item.created_at,
            updated_at=item.updated_at,
            metadata_json=item.metadata,
        )

    @staticmethod
    def _record_to_model(record: ContentItemRecord) -> ContentItem:
        return ContentItem(
            id=record.id,
            campaign_brief_id=record.campaign_brief_id,
            title=record.title,
            format=ContentFormat(record.format),
            target_platform=Platform(record.target_platform),
            status=ContentStatus(record.status),
            body=record.body,
            seo_title=record.seo_title,
            meta_description=record.meta_description,
            cta=record.cta,
            scheduled_at=record.scheduled_at,
            created_at=record.created_at,
            updated_at=record.updated_at,
            metadata=record.metadata_json,
        )

    @staticmethod
    def _publication_record_to_model(record: PublicationRecord) -> ConnectorResult:
        return ConnectorResult(
            platform=Platform(record.platform),
            mode=ConnectorMode(record.mode),
            operation=record.operation,
            success=record.success,
            platform_id=record.platform_id,
            platform_url=record.platform_url,
            status=record.status,
            error_code=record.error_code,
            human_message=record.human_message,
            raw_response=record.raw_response_json,
        )

    @staticmethod
    def _performance_record_to_model(record: PerformanceSnapshotRecord) -> PerformanceSnapshot:
        return PerformanceSnapshot(
            content_item_id=record.content_item_id,
            campaign_brief_id=record.campaign_brief_id,
            platform=Platform(record.platform),
            source_mode=ConnectorMode(record.source_mode),
            impressions=record.impressions,
            clicks=record.clicks,
            engagements=record.engagements,
            conversions=record.conversions,
            spend=record.spend,
            captured_at=record.captured_at,
        )

    @staticmethod
    def _client_profile_to_record(profile: ClientProfile) -> ClientProfileRecord:
        return ClientProfileRecord(
            id=profile.id,
            name=profile.name,
            industry=profile.industry,
            audience_json=profile.audience,
            offers_json=profile.offers,
            competitors_json=profile.competitors,
            brand_voice=profile.brand_voice,
            banned_claims_json=profile.banned_claims,
            preferred_ctas_json=profile.preferred_ctas,
        )

    @staticmethod
    def _client_profile_record_to_model(record: ClientProfileRecord) -> ClientProfile:
        return ClientProfile(
            id=record.id,
            name=record.name,
            industry=record.industry,
            audience=record.audience_json,
            offers=record.offers_json,
            competitors=record.competitors_json,
            brand_voice=record.brand_voice,
            banned_claims=record.banned_claims_json,
            preferred_ctas=record.preferred_ctas_json,
        )

    @staticmethod
    def _campaign_to_record(campaign: CampaignBrief) -> CampaignBriefRecord:
        return CampaignBriefRecord(
            id=campaign.id,
            client_profile_id=campaign.client_profile_id,
            objective=campaign.objective,
            audience=campaign.audience,
            funnel_stage=campaign.funnel_stage,
            channels_json=[platform.value for platform in campaign.channels],
            keywords_json=campaign.keywords,
            offer=campaign.offer,
            cta=campaign.cta,
            success_metrics_json=campaign.success_metrics,
            created_at=campaign.created_at,
        )

    @staticmethod
    def _campaign_record_to_model(record: CampaignBriefRecord) -> CampaignBrief:
        return CampaignBrief(
            id=record.id,
            client_profile_id=record.client_profile_id,
            objective=record.objective,
            audience=record.audience,
            funnel_stage=record.funnel_stage,
            channels=[Platform(value) for value in record.channels_json],
            keywords=record.keywords_json,
            offer=record.offer,
            cta=record.cta,
            success_metrics=record.success_metrics_json,
            created_at=record.created_at,
        )
