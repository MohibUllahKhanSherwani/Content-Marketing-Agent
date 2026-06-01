from content_marketing_agent.config.settings import AppSettings
from content_marketing_agent.connectors.ga4 import GA4Connector
from content_marketing_agent.domain.enums import ConnectorMode


def test_ga4_auto_mode_uses_mock_without_credentials() -> None:
    connector = GA4Connector(AppSettings(ga4_mode="auto"))
    snapshots = connector.fetch_metrics(["item-1"])
    assert len(snapshots) == 1
    assert snapshots[0].source_mode == ConnectorMode.MOCK


def test_ga4_real_fetch_metrics_returns_real_snapshot(monkeypatch) -> None:
    connector = GA4Connector(
        AppSettings(
            ga4_mode="real",
            ga4_property_id="123456789",
            google_application_credentials="C:/tmp/service-account.json",
        )
    )

    monkeypatch.setattr(
        connector,
        "_run_report_totals",
        lambda *_args, **_kwargs: {
            "impressions": 1200,
            "clicks": 90,
            "engagements": 160,
            "conversions": 14,
        },
    )

    snapshots = connector.fetch_metrics(["item-1", "item-2"])
    assert len(snapshots) == 1
    assert snapshots[0].source_mode == ConnectorMode.REAL
    assert snapshots[0].platform.value == "ga4"
    assert snapshots[0].impressions == 1200
    assert snapshots[0].clicks == 90
