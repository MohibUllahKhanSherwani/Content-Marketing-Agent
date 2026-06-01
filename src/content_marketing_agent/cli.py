import json

import typer
from rich.console import Console
from rich.table import Table

from content_marketing_agent.config.settings import get_settings
from content_marketing_agent.connectors.registry import build_connector_registry
from content_marketing_agent.domain.enums import ContentFormat, ContentStatus, Platform
from content_marketing_agent.domain.models import ContentItem
from content_marketing_agent.services.analytics import (
    collect_monthly_snapshots,
    summarize_snapshots,
)
from content_marketing_agent.services.connector_diagnostics import build_connector_diagnostics
from content_marketing_agent.services.content_items import ContentItemStore
from content_marketing_agent.services.integration_smoke import run_integration_smoke
from content_marketing_agent.services.planning import build_monthly_plan
from content_marketing_agent.services.production import produce_content_drafts

app = typer.Typer(help="Content Marketing Agent Team operator commands.")
console = Console()
content_item_store = ContentItemStore.from_settings(get_settings())

@app.command()
def connectors(json_output: bool = typer.Option(False, "--json", help="Print JSON.")) -> None:
    """Show connector modes and capabilities."""

    registry = build_connector_registry(get_settings())
    capabilities = registry.capabilities()
    if json_output:
        console.print(json.dumps([cap.model_dump(mode="json") for cap in capabilities], indent=2))
        return

    table = Table(title="Connector Capabilities")
    table.add_column("Platform")
    table.add_column("Requested")
    table.add_column("Active")
    table.add_column("Draft")
    table.add_column("Schedule")
    table.add_column("Publish")
    table.add_column("Metrics")
    table.add_column("Reason")

    for capability in capabilities:
        table.add_row(
            capability.platform.value,
            capability.requested_mode.value,
            capability.active_mode.value,
            str(capability.can_create_draft),
            str(capability.can_schedule),
            str(capability.can_publish),
            str(capability.can_fetch_metrics),
            capability.reason or "",
        )
    console.print(table)


@app.command("connector-diagnostics")
def connector_diagnostics(json_output: bool = typer.Option(False, "--json", help="Print JSON.")) -> None:
    """Show actionable connector readiness diagnostics."""

    diagnostics = build_connector_diagnostics(get_settings())
    if json_output:
        console.print(json.dumps([item.__dict__ for item in diagnostics], indent=2))
        return

    table = Table(title="Connector Diagnostics")
    table.add_column("Platform")
    table.add_column("Requested")
    table.add_column("Active")
    table.add_column("Healthy")
    table.add_column("Missing Credentials")
    table.add_column("Action")

    for item in diagnostics:
        table.add_row(
            item.platform,
            item.requested_mode,
            item.active_mode,
            str(item.healthy),
            ", ".join(item.missing_credentials),
            "; ".join(item.action_items),
        )
    console.print(table)


@app.command()
def hello() -> None:
    """Smoke command for local setup checks."""

    console.print("Content Marketing Agent Team scaffold is ready.")


@app.command()
def monthly_plan(
    month: str = typer.Option(..., help="Month in YYYY-MM format."),
    blog_posts: int = typer.Option(8, min=8, max=12, help="Target number of blog posts."),
) -> None:
    """Generate and persist a monthly content calendar plan."""

    plan = build_monthly_plan(month=month, blog_posts=blog_posts)
    saved = content_item_store.add_items(plan.items)
    console.print(
        f"Monthly plan saved: {len(saved)} items (blogs={plan.summary['blog_posts']}, "
        f"emails={plan.summary['email_campaigns']}, social={plan.summary['social_posts']})."
    )


@app.command()
def produce(
    objective: str = typer.Option(..., help="Campaign objective."),
    items_per_channel: int = typer.Option(1, min=1, max=3, help="Draft count per channel."),
) -> None:
    """Generate and persist multi-channel drafts."""

    settings = get_settings()
    result = produce_content_drafts(
        objective=objective, settings=settings, items_per_channel=items_per_channel
    )
    saved = content_item_store.add_items(result.items)
    console.print(f"Produced {len(saved)} draft items using mode={result.generation_mode}.")


@app.command()
def monthly_analytics() -> None:
    """Collect and summarize monthly analytics snapshots."""

    settings = get_settings()
    items = content_item_store.list_items()
    snapshots = collect_monthly_snapshots(settings=settings, content_items=items)
    persisted = content_item_store.record_performance_snapshots(snapshots)
    summary = summarize_snapshots(snapshots)
    console.print(
        f"Analytics collected: snapshots={persisted}, impressions={summary.totals['impressions']}, "
        f"clicks={summary.totals['clicks']}."
    )


@app.command("integration-smoke")
def integration_smoke(json_output: bool = typer.Option(False, "--json", help="Print JSON.")) -> None:
    """Run safe connector smoke checks across all configured integrations."""

    results = run_integration_smoke(get_settings())
    if json_output:
        console.print(json.dumps([item.__dict__ for item in results], indent=2))
        return

    table = Table(title="Integration Smoke Results")
    table.add_column("Platform")
    table.add_column("Requested")
    table.add_column("Active")
    table.add_column("Operation")
    table.add_column("Success")
    table.add_column("Details")
    for item in results:
        table.add_row(
            item.platform,
            item.requested_mode,
            item.active_mode,
            item.operation,
            str(item.success),
            item.details,
        )
    console.print(table)


@app.command("wp-draft-smoke")
def wp_draft_smoke() -> None:
    """Create a WordPress draft from an approved item for integration smoke checks."""

    settings = get_settings()
    registry = build_connector_registry(settings)
    connector = registry.get(Platform.WORDPRESS)

    wordpress_items = [
        item for item in content_item_store.list_items() if item.target_platform == Platform.WORDPRESS
    ]
    approved_wordpress_item = next(
        (item for item in wordpress_items if item.status == ContentStatus.APPROVED),
        None,
    )

    if approved_wordpress_item is None:
        existing_wordpress_item = wordpress_items[0] if wordpress_items else None
        if existing_wordpress_item is None:
            created = content_item_store.add_items(
                [
                    ContentItem(
                        title="WordPress Smoke Draft",
                        body="Smoke-test draft payload from CLI command.",
                        format=ContentFormat.BLOG_POST,
                        target_platform=Platform.WORDPRESS,
                        status=ContentStatus.DRAFTED,
                    )
                ]
            )
            existing_wordpress_item = created[0]
        approved_wordpress_item = content_item_store.approve_item(
            existing_wordpress_item.id,
            approver="cli_wp_smoke",
            notes="Auto-approved for WordPress draft smoke test.",
        )

    result = connector.create_draft(approved_wordpress_item)
    content_item_store.record_publication(approved_wordpress_item.id, result)

    if result.success:
        console.print(
            f"WordPress draft created (mode={result.mode.value}) "
            f"id={result.platform_id} url={result.platform_url}"
        )
        return
    console.print(
        f"WordPress draft failed (mode={result.mode.value}) "
        f"error={result.error_code} message={result.human_message}"
    )


@app.command("run-telemetry")
def run_telemetry(
    limit: int = typer.Option(20, min=1, max=100, help="Number of recent run records."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON."),
) -> None:
    """Show recent run-level telemetry records."""

    runs = content_item_store.list_run_telemetry(limit=limit)
    if json_output:
        console.print(json.dumps([run.model_dump(mode="json") for run in runs], indent=2))
        return

    table = Table(title="Run Telemetry")
    table.add_column("Run ID")
    table.add_column("Type")
    table.add_column("Success")
    table.add_column("Mode")
    table.add_column("Items")
    table.add_column("Tokens")
    table.add_column("Cost USD")
    table.add_column("Duration ms")

    for run in runs:
        table.add_row(
            run.run_id[:8],
            run.run_type,
            str(run.success),
            run.generation_mode or "",
            str(run.items_created),
            str(run.estimated_total_tokens),
            f"{run.estimated_cost_usd:.6f}",
            str(run.duration_ms),
        )
    console.print(table)
