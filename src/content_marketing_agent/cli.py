import json

import typer
from rich.console import Console
from rich.table import Table

from content_marketing_agent.config.settings import get_settings
from content_marketing_agent.connectors.registry import build_connector_registry

app = typer.Typer(help="Content Marketing Agent Team operator commands.")
console = Console()


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


@app.command()
def hello() -> None:
    """Smoke command for local setup checks."""

    console.print("Content Marketing Agent Team scaffold is ready.")

