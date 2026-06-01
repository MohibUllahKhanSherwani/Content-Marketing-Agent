from fastapi.testclient import TestClient

from content_marketing_agent.api import app
from content_marketing_agent.config.settings import AppSettings
from content_marketing_agent.services.content_items import ContentItemStore


def test_monthly_flow_runs_plan_production_analytics_and_returns_telemetry() -> None:
    from content_marketing_agent import api as api_module

    api_module.content_item_store = ContentItemStore()
    api_module.get_settings = lambda: AppSettings(azure_openai_mode='mock')
    client = TestClient(app)

    response = client.post(
        '/runs/monthly-flow',
        json={'month': '2026-08', 'blog_posts': 8, 'items_per_channel': 1},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload['plan']['items_created'] > 0
    assert payload['production']['items_created'] > 0
    assert payload['analytics']['snapshots_collected'] > 0
    assert payload['run_telemetry']['run_type'] == 'monthly_flow'
