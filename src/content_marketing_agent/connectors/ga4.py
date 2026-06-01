from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from content_marketing_agent.config.settings import AppSettings
from content_marketing_agent.connectors.hybrid import HybridPlaceholderConnector
from content_marketing_agent.domain.enums import ConnectorMode, Platform
from content_marketing_agent.domain.models import ConnectorCapabilities, PerformanceSnapshot


class GA4Connector(HybridPlaceholderConnector):
    real_implementation_ready = True

    def __init__(self, settings: AppSettings) -> None:
        super().__init__(
            platform=Platform.GA4,
            mode=ConnectorMode(settings.ga4_mode),
            required_values={
                "GA4_PROPERTY_ID": settings.ga4_property_id,
                "GOOGLE_APPLICATION_CREDENTIALS": settings.google_application_credentials,
            },
        )
        self._settings = settings

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
            return ConnectorCapabilities(
                platform=self.platform,
                requested_mode=self.mode,
                active_mode=ConnectorMode.REAL,
                reason=f"Missing credentials: {', '.join(missing)}.",
            )
        return ConnectorCapabilities(
            platform=self.platform,
            requested_mode=self.mode,
            active_mode=ConnectorMode.REAL,
            can_create_draft=False,
            can_schedule=False,
            can_publish=False,
            can_fetch_metrics=True,
            reason="GA4 read-only metrics collection is available.",
        )

    def fetch_metrics(self, content_item_ids: Sequence[str] | None = None) -> list[PerformanceSnapshot]:
        capabilities = self.check_capabilities()
        if capabilities.active_mode == ConnectorMode.MOCK:
            return self.mock.fetch_metrics(content_item_ids)

        totals = self._run_report_totals()
        return [
            PerformanceSnapshot(
                content_item_id=None,
                platform=Platform.GA4,
                source_mode=ConnectorMode.REAL,
                impressions=int(totals["impressions"]),
                clicks=int(totals["clicks"]),
                engagements=int(totals["engagements"]),
                conversions=int(totals["conversions"]),
            )
        ]

    def _run_report_totals(self) -> dict[str, int]:
        try:
            from google.analytics.data_v1beta import BetaAnalyticsDataClient
            from google.analytics.data_v1beta.types import DateRange, Metric, RunReportRequest
            from google.oauth2 import service_account
        except ImportError as error:
            raise RuntimeError(
                "GA4 real mode requires optional dependency google-analytics-data."
            ) from error

        property_id = self._settings.ga4_property_id or ""
        credentials_path = self._settings.google_application_credentials or ""
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        client = BetaAnalyticsDataClient(credentials=credentials)

        response = client.run_report(
            RunReportRequest(
                property=f"properties/{property_id}",
                date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
                metrics=[
                    Metric(name="screenPageViews"),
                    Metric(name="sessions"),
                    Metric(name="engagedSessions"),
                    Metric(name="conversions"),
                ],
            )
        )
        return self._sum_metric_rows(response.rows)

    @staticmethod
    def _sum_metric_rows(rows: list[Any]) -> dict[str, int]:
        totals = {"impressions": 0, "clicks": 0, "engagements": 0, "conversions": 0}
        for row in rows:
            values = [int(metric_value.value) for metric_value in row.metric_values]
            if len(values) >= 4:
                totals["impressions"] += values[0]
                totals["clicks"] += values[1]
                totals["engagements"] += values[2]
                totals["conversions"] += values[3]
        return totals
