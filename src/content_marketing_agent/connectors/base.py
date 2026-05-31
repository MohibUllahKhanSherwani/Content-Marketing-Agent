from abc import ABC, abstractmethod
from collections.abc import Sequence

from content_marketing_agent.domain.enums import ConnectorMode, Platform, PublicationOperation
from content_marketing_agent.domain.models import (
    ConnectorCapabilities,
    ConnectorResult,
    ContentItem,
    PerformanceSnapshot,
)


class BaseConnector(ABC):
    """Base interface for all real, mock, and hybrid platform connectors."""

    platform: Platform

    def __init__(self, mode: ConnectorMode) -> None:
        self.mode = mode  # requested runtime behavior: real, mock, or auto

    @abstractmethod
    def check_capabilities(self) -> ConnectorCapabilities:
        """Return what this connector can do in its current mode."""

    def create_draft(self, content_item: ContentItem) -> ConnectorResult:
        # Default is safe: connectors must opt into supported operations.
        return self._unsupported(PublicationOperation.CREATE_DRAFT)

    def schedule(self, content_item: ContentItem) -> ConnectorResult:
        # Real scheduling is platform-specific, so base class refuses it.
        return self._unsupported(PublicationOperation.SCHEDULE)

    def publish(self, content_item: ContentItem) -> ConnectorResult:
        # Public publishing should only exist in explicit connector implementations.
        return self._unsupported(PublicationOperation.PUBLISH)

    def fetch_metrics(self, content_item_ids: Sequence[str] | None = None) -> list[PerformanceSnapshot]:
        # Analytics support is optional per platform.
        return []

    def _unsupported(self, operation: PublicationOperation) -> ConnectorResult:
        return ConnectorResult(
            platform=self.platform,
            mode=self.mode,
            operation=operation.value,
            success=False,
            error_code="unsupported_operation",
            human_message=f"{self.platform.value} does not support {operation.value}.",
        )
