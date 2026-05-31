from collections.abc import Sequence
from hashlib import sha1

from content_marketing_agent.connectors.base import BaseConnector
from content_marketing_agent.domain.enums import ConnectorMode, Platform, PublicationOperation
from content_marketing_agent.domain.models import (
    ConnectorCapabilities,
    ConnectorResult,
    ContentItem,
    PerformanceSnapshot,
)


class MockConnector(BaseConnector):
    """Realistic no-network connector used for demos and unavailable integrations."""

    def __init__(
        self,
        platform: Platform,
        can_create_draft: bool = True,
        can_schedule: bool = True,
        can_publish: bool = True,
        can_fetch_metrics: bool = True,
        reason: str | None = None,
    ) -> None:
        super().__init__(ConnectorMode.MOCK)
        self.platform = platform
        self._capabilities = ConnectorCapabilities(
            platform=platform,
            requested_mode=ConnectorMode.MOCK,
            active_mode=ConnectorMode.MOCK,
            can_create_draft=can_create_draft,
            can_schedule=can_schedule,
            can_publish=can_publish,
            can_fetch_metrics=can_fetch_metrics,
            reason=reason or "Mock connector active.",
        )

    def check_capabilities(self) -> ConnectorCapabilities:
        # Mocks advertise deterministic capabilities for demos and tests.
        return self._capabilities

    def create_draft(self, content_item: ContentItem) -> ConnectorResult:
        return self._result(content_item, PublicationOperation.CREATE_DRAFT, "draft")

    def schedule(self, content_item: ContentItem) -> ConnectorResult:
        return self._result(content_item, PublicationOperation.SCHEDULE, "scheduled")

    def publish(self, content_item: ContentItem) -> ConnectorResult:
        return self._result(content_item, PublicationOperation.PUBLISH, "published")

    def fetch_metrics(self, content_item_ids: Sequence[str] | None = None) -> list[PerformanceSnapshot]:
        ids = list(content_item_ids or ["mock_content_item"])  # default one fake row if none given
        snapshots: list[PerformanceSnapshot] = []
        for index, content_item_id in enumerate(ids, start=1):
            # Deterministic fake metrics: stable enough for tests, realistic enough for demos.
            impressions = 1000 + (index * 137)
            clicks = 40 + (index * 7)
            engagements = 120 + (index * 11)
            conversions = 3 + index
            snapshots.append(
                PerformanceSnapshot(
                    content_item_id=content_item_id,
                    platform=self.platform,
                    source_mode=ConnectorMode.MOCK,
                    impressions=impressions,
                    clicks=clicks,
                    engagements=engagements,
                    conversions=conversions,
                )
            )
        return snapshots

    def _result(
        self, content_item: ContentItem, operation: PublicationOperation, status: str
    ) -> ConnectorResult:
        # Stable fake external ID based on platform + content + operation.
        digest = sha1(f"{self.platform.value}:{content_item.id}:{operation.value}".encode()).hexdigest()[
            :10
        ]
        platform_id = f"{self.platform.value}_mock_{digest}"
        return ConnectorResult(
            platform=self.platform,
            mode=ConnectorMode.MOCK,
            operation=operation.value,
            success=True,
            platform_id=platform_id,
            platform_url=f"https://mock.{self.platform.value}.local/{platform_id}",
            status=status,
            human_message=f"Mock {self.platform.value} {operation.value} completed.",
        )
