from content_marketing_agent.config.settings import AppSettings
from content_marketing_agent.flows.monthly import MonthlyContentFlow
from content_marketing_agent.services.content_items import ContentItemStore


def test_monthly_content_flow_orchestrates_plan_production_and_analytics() -> None:
    settings = AppSettings(gemini_api_mode="mock")
    store = ContentItemStore(seed_if_empty=False)
    flow = MonthlyContentFlow(settings=settings, content_item_store=store)

    result = flow.kickoff(
        inputs={
            "month": "2026-09",
            "blog_posts": 8,
            "objective": "Drive qualified inbound demos with educational content.",
            "items_per_channel": 1,
        }
    )

    assert result is not None
    assert flow.state.completed is True
    assert int(flow.state.plan["items_created"]) > 0
    assert int(flow.state.production["items_created"]) > 0
    assert int(flow.state.analytics["snapshots_collected"]) > 0
