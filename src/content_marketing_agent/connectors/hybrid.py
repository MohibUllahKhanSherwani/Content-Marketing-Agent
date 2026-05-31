from collections.abc import Sequence

from content_marketing_agent.connectors.base import BaseConnector
from content_marketing_agent.connectors.mock import MockConnector
from content_marketing_agent.domain.enums import ConnectorMode, Platform, PublicationOperation
from content_marketing_agent.domain.models import (
    ConnectorCapabilities,
    ConnectorResult,
    ContentItem,
    PerformanceSnapshot,
)


class HybridPlaceholderConnector(BaseConnector):
    """Connector boundary for real APIs before the HTTP implementation is added.

    In `auto` mode, this class falls back to a realistic mock until the real API
    implementation is marked ready. In `real` mode, it fails loudly so operators
    do not mistake a placeholder for a live integration.
    """

    real_implementation_ready = False

    def __init__(
        self,
        platform: Platform,
        mode: ConnectorMode,
        required_values: dict[str, str | None],
        mock: MockConnector | None = None,
    ) -> None:
        super().__init__(mode)
        self.platform = platform
        self.required_values = required_values
        self.mock = mock or MockConnector(platform)

    def check_capabilities(self) -> ConnectorCapabilities:
        missing = [name for name, value in self.required_values.items() if not value]
        if self.mode == ConnectorMode.MOCK:
            return self.mock.check_capabilities()
        if missing:
            if self.mode == ConnectorMode.AUTO:
                capabilities = self.mock.check_capabilities()
                capabilities.requested_mode = self.mode
                capabilities.reason = f"Missing credentials: {', '.join(missing)}."
                return capabilities
            return self._real_unavailable(f"Missing credentials: {', '.join(missing)}.")
        if not self.real_implementation_ready:
            if self.mode == ConnectorMode.AUTO:
                capabilities = self.mock.check_capabilities()
                capabilities.requested_mode = self.mode
                capabilities.reason = "Real connector scaffold exists; API implementation pending."
                return capabilities
            return self._real_unavailable("Real connector scaffold exists; API implementation pending.")
        return ConnectorCapabilities(
            platform=self.platform,
            requested_mode=self.mode,
            active_mode=ConnectorMode.REAL,
            can_create_draft=True,
            can_schedule=True,
            can_publish=True,
            can_fetch_metrics=True,
            reason="Real connector available.",
        )

    def create_draft(self, content_item: ContentItem) -> ConnectorResult:
        return self._delegate_or_fail(content_item, PublicationOperation.CREATE_DRAFT)

    def schedule(self, content_item: ContentItem) -> ConnectorResult:
        return self._delegate_or_fail(content_item, PublicationOperation.SCHEDULE)

    def publish(self, content_item: ContentItem) -> ConnectorResult:
        return self._delegate_or_fail(content_item, PublicationOperation.PUBLISH)

    def fetch_metrics(self, content_item_ids: Sequence[str] | None = None) -> list[PerformanceSnapshot]:
        capabilities = self.check_capabilities()
        if capabilities.active_mode == ConnectorMode.MOCK:
            return self.mock.fetch_metrics(content_item_ids)
        return []

    def _delegate_or_fail(
        self, content_item: ContentItem, operation: PublicationOperation
    ) -> ConnectorResult:
        capabilities = self.check_capabilities()
        if capabilities.active_mode == ConnectorMode.MOCK:
            if operation == PublicationOperation.CREATE_DRAFT:
                return self.mock.create_draft(content_item)
            if operation == PublicationOperation.SCHEDULE:
                return self.mock.schedule(content_item)
            return self.mock.publish(content_item)
        return ConnectorResult(
            platform=self.platform,
            mode=ConnectorMode.REAL,
            operation=operation.value,
            success=False,
            error_code="real_connector_not_implemented",
            human_message="Real API implementation is not wired yet.",
        )

    def _real_unavailable(self, reason: str) -> ConnectorCapabilities:
        return ConnectorCapabilities(
            platform=self.platform,
            requested_mode=self.mode,
            active_mode=ConnectorMode.REAL,
            reason=reason,
        )
