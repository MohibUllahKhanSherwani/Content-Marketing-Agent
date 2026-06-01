from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from content_marketing_agent.config.settings import get_settings
from content_marketing_agent.connectors.registry import build_connector_registry
from content_marketing_agent.domain.enums import ContentStatus, Platform
from content_marketing_agent.domain.models import CampaignBrief, ClientProfile
from content_marketing_agent.services.analytics import (
    collect_monthly_snapshots,
    summarize_snapshots,
)
from content_marketing_agent.services.calendar import demo_calendar_items
from content_marketing_agent.services.connector_diagnostics import build_connector_diagnostics
from content_marketing_agent.services.content_items import (
    CampaignNotFoundError,
    ClientProfileNotFoundError,
    ContentItemNotFoundError,
    ContentItemStore,
)
from content_marketing_agent.services.integration_smoke import run_integration_smoke
from content_marketing_agent.services.planning import build_monthly_plan
from content_marketing_agent.services.production import (
    RealProductionError,
    llm_readiness,
    produce_content_drafts,
)

app = FastAPI(
    title="Content Marketing Agent Team",
    version="0.1.0",
    description="CrewAI content marketing workflow with Azure OpenAI and hybrid connectors.",
)
content_item_store = ContentItemStore.from_settings(get_settings())


class ProduceContentRequest(BaseModel):
    objective: str = "Generate monthly multi-channel content for campaign goals."
    items_per_channel: int = Field(default=1, ge=1, le=3)
    strict_real: bool = False


class MonthlyPlanRequest(BaseModel):
    month: str
    blog_posts: int = Field(default=8, ge=8, le=12)


class ApprovalRequest(BaseModel):
    approver: str = "human_reviewer"
    notes: str | None = None


class RequestChangesRequest(BaseModel):
    approver: str = "human_reviewer"
    notes: str = Field(min_length=3)


class ClientProfileRequest(BaseModel):
    name: str
    industry: str | None = None
    audience: list[str] = Field(default_factory=list)
    offers: list[str] = Field(default_factory=list)
    competitors: list[str] = Field(default_factory=list)
    brand_voice: str | None = None
    banned_claims: list[str] = Field(default_factory=list)
    preferred_ctas: list[str] = Field(default_factory=list)


class CampaignRequest(BaseModel):
    client_profile_id: str
    objective: str
    audience: str
    funnel_stage: str
    channels: list[str]
    keywords: list[str] = Field(default_factory=list)
    offer: str | None = None
    cta: str | None = None
    success_metrics: list[str] = Field(default_factory=list)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/llm")
def health_llm() -> dict[str, object]:
    return llm_readiness(get_settings())

# dumps the connector registry state as a dict
@app.get("/connectors")
def connectors() -> dict[str, dict[str, object]]:
    registry = build_connector_registry(get_settings())
    return registry.as_dict()


@app.get("/connectors/diagnostics")
def connector_diagnostics() -> dict[str, object]:
    diagnostics = build_connector_diagnostics(get_settings())
    return {"connectors": [item.__dict__ for item in diagnostics]}


@app.get("/calendar/demo")
def calendar_demo() -> list[dict[str, object]]:
    return [item.model_dump(mode="json") for item in demo_calendar_items()]


@app.get("/calendar")
def calendar_items() -> list[dict[str, object]]:
    return [item.model_dump(mode="json") for item in content_item_store.list_scheduled_items()]


@app.post("/demo/seed")
def seed_demo() -> dict[str, int]:
    items_seeded = content_item_store.seed_demo_items()
    return {"items_seeded": items_seeded}


@app.post("/client-profiles")
def create_client_profile(request: ClientProfileRequest) -> dict[str, object]:
    profile = ClientProfile(
        name=request.name,
        industry=request.industry,
        audience=request.audience,
        offers=request.offers,
        competitors=request.competitors,
        brand_voice=request.brand_voice,
        banned_claims=request.banned_claims,
        preferred_ctas=request.preferred_ctas,
    )
    created = content_item_store.create_client_profile(profile)
    return created.model_dump(mode="json")


@app.get("/client-profiles/{client_profile_id}")
def get_client_profile(client_profile_id: str) -> dict[str, object]:
    try:
        profile = content_item_store.get_client_profile(client_profile_id)
    except ClientProfileNotFoundError as error:
        raise HTTPException(status_code=404, detail="Client profile not found.") from error
    return profile.model_dump(mode="json")


@app.post("/campaigns")
def create_campaign(request: CampaignRequest) -> dict[str, object]:
    channels = [Platform(channel) for channel in request.channels]
    campaign = CampaignBrief(
        client_profile_id=request.client_profile_id,
        objective=request.objective,
        audience=request.audience,
        funnel_stage=request.funnel_stage,
        channels=channels,
        keywords=request.keywords,
        offer=request.offer,
        cta=request.cta,
        success_metrics=request.success_metrics,
    )
    try:
        created = content_item_store.create_campaign(campaign)
    except ClientProfileNotFoundError as error:
        raise HTTPException(status_code=404, detail="Client profile not found.") from error
    return created.model_dump(mode="json")


@app.get("/campaigns/{campaign_id}")
def get_campaign(campaign_id: str) -> dict[str, object]:
    try:
        campaign = content_item_store.get_campaign(campaign_id)
    except CampaignNotFoundError as error:
        raise HTTPException(status_code=404, detail="Campaign not found.") from error
    return campaign.model_dump(mode="json")


@app.get("/content-items")
def content_items() -> list[dict[str, object]]:
    return [item.model_dump(mode="json") for item in content_item_store.list_items()]


@app.get("/content-items/{content_item_id}")
def content_item_detail(content_item_id: str) -> dict[str, object]:
    try:
        item = content_item_store.get_item(content_item_id)
    except ContentItemNotFoundError as error:
        raise HTTPException(status_code=404, detail="Content item not found.") from error
    return item.model_dump(mode="json")


@app.post("/content-items/{content_item_id}/approve")
def approve_content_item(content_item_id: str, request: ApprovalRequest) -> dict[str, object]:
    try:
        item = content_item_store.approve_item(
            content_item_id, approver=request.approver, notes=request.notes
        )
    except ContentItemNotFoundError as error:
        raise HTTPException(status_code=404, detail="Content item not found.") from error
    return item.model_dump(mode="json")


@app.post("/content-items/{content_item_id}/request-changes")
def request_changes(content_item_id: str, request: RequestChangesRequest) -> dict[str, object]:
    try:
        item = content_item_store.request_changes_item(
            content_item_id, approver=request.approver, notes=request.notes
        )
    except ContentItemNotFoundError as error:
        raise HTTPException(status_code=404, detail="Content item not found.") from error
    return item.model_dump(mode="json")


@app.post("/content-items/{content_item_id}/publish-draft")
def publish_content_item_draft(content_item_id: str) -> dict[str, dict[str, object]]:
    try:
        item = content_item_store.get_item(content_item_id)
    except ContentItemNotFoundError as error:
        raise HTTPException(status_code=404, detail="Content item not found.") from error

    if item.status != ContentStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Content item must be approved before draft publish.")

    connector = build_connector_registry(get_settings()).get(item.target_platform)
    publication = connector.create_draft(item)
    content_item_store.record_publication(content_item_id, publication)
    return {
        "content_item": item.model_dump(mode="json"),
        "publication": publication.model_dump(mode="json"),
    }


@app.post("/content-items/{content_item_id}/publish")
def publish_content_item(content_item_id: str) -> dict[str, dict[str, object]]:
    settings = get_settings()
    try:
        item = content_item_store.get_item(content_item_id)
    except ContentItemNotFoundError as error:
        raise HTTPException(status_code=404, detail="Content item not found.") from error

    if item.status != ContentStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Content item must be approved before publish.")

    connector = build_connector_registry(settings).get(item.target_platform)
    capabilities = connector.check_capabilities()
    if capabilities.active_mode.value == "real" and not settings.allow_real_publish:
        raise HTTPException(
            status_code=400,
            detail="ALLOW_REAL_PUBLISH must be true before real publishing.",
        )

    publication = connector.publish(item)
    content_item_store.record_publication(content_item_id, publication)
    next_status = ContentStatus.PUBLISHED if publication.success else ContentStatus.PUBLISH_FAILED
    updated_item = content_item_store.update_status(content_item_id, next_status)
    return {
        "content_item": updated_item.model_dump(mode="json"),
        "publication": publication.model_dump(mode="json"),
    }


@app.get("/content-items/{content_item_id}/publications")
def content_item_publications(content_item_id: str) -> list[dict[str, object]]:
    try:
        publications = content_item_store.list_publications(content_item_id)
    except ContentItemNotFoundError as error:
        raise HTTPException(status_code=404, detail="Content item not found.") from error
    return [record.model_dump(mode="json") for record in publications]


@app.get("/content-items/{content_item_id}/approval-decisions")
def content_item_approval_decisions(content_item_id: str) -> list[dict[str, object]]:
    try:
        decisions = content_item_store.list_approval_decisions(content_item_id)
    except ContentItemNotFoundError as error:
        raise HTTPException(status_code=404, detail="Content item not found.") from error
    return [decision.model_dump(mode="json") for decision in decisions]


@app.post("/runs/produce-content")
def run_produce_content(request: ProduceContentRequest) -> dict[str, object]:
    settings = get_settings()
    try:
        result = produce_content_drafts(
            objective=request.objective,
            settings=settings,
            items_per_channel=request.items_per_channel,
            strict_real=request.strict_real,
        )
    except RealProductionError as error:
        raise HTTPException(
            status_code=502,
            detail={
                "error_code": "real_generation_failed",
                "message": str(error),
            },
        ) from error
    saved_items = content_item_store.add_items(result.items)
    return {
        "generation_mode": result.generation_mode,
        "items_created": len(saved_items),
        "items": [item.model_dump(mode="json") for item in saved_items],
    }


@app.post("/runs/monthly-plan")
def run_monthly_plan(request: MonthlyPlanRequest) -> dict[str, object]:
    plan = build_monthly_plan(month=request.month, blog_posts=request.blog_posts)
    saved_items = content_item_store.add_items(plan.items)
    return {
        "items_created": len(saved_items),
        "summary": plan.summary,
        "items": [item.model_dump(mode="json") for item in saved_items],
    }


@app.post("/runs/monthly-analytics")
def run_monthly_analytics() -> dict[str, object]:
    settings = get_settings()
    content_items = content_item_store.list_items()
    snapshots = collect_monthly_snapshots(settings=settings, content_items=content_items)
    persisted_count = content_item_store.record_performance_snapshots(snapshots)
    summary = summarize_snapshots(snapshots)
    return {
        "snapshots_collected": len(snapshots),
        "snapshots_persisted": persisted_count,
        "summary": {
            "snapshots_count": summary.snapshots_count,
            "totals": summary.totals,
            "by_platform": summary.by_platform,
        },
    }


@app.post("/runs/integration-smoke")
def run_connector_integration_smoke() -> dict[str, object]:
    settings = get_settings()
    results = run_integration_smoke(settings)
    successes = sum(1 for item in results if item.success)
    return {
        "total_connectors_checked": len(results),
        "successes": successes,
        "failures": len(results) - successes,
        "results": [item.__dict__ for item in results],
    }


@app.get("/analytics/monthly-summary")
def monthly_summary() -> dict[str, object]:
    snapshots = content_item_store.list_performance_snapshots()
    summary = summarize_snapshots(snapshots)
    return {
        "snapshots_count": summary.snapshots_count,
        "totals": summary.totals,
        "by_platform": summary.by_platform,
    }
