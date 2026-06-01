from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from content_marketing_agent.domain.models import RunTelemetry


@dataclass(frozen=True)
class TelemetryEstimate:
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost_usd: float


def estimate_produce_content_run(
    *, objective: str, items_created: int, generation_mode: str
) -> TelemetryEstimate:
    objective_tokens = max(32, len(objective) // 4)
    per_item_input = 220 if generation_mode == "real" else 120
    per_item_output = 520 if generation_mode == "real" else 280
    input_tokens = objective_tokens + (items_created * per_item_input)
    output_tokens = items_created * per_item_output
    total_tokens = input_tokens + output_tokens
    # Simple deterministic estimate to support budget guardrails and reporting.
    estimated_cost_usd = round((total_tokens / 1_000_000) * 0.75, 6)
    return TelemetryEstimate(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        estimated_cost_usd=estimated_cost_usd,
    )


def build_run_telemetry(
    *,
    run_type: str,
    started_at: datetime,
    completed_at: datetime,
    items_created: int,
    generation_mode: str | None,
    estimate: TelemetryEstimate,
    budget_limit_usd: float | None = None,
    success: bool = True,
    error_code: str | None = None,
    metadata: dict[str, object] | None = None,
) -> RunTelemetry:
    duration_ms = max(0, int((completed_at - started_at).total_seconds() * 1000))
    budget_exceeded = (
        budget_limit_usd is not None and estimate.estimated_cost_usd > budget_limit_usd
    )
    return RunTelemetry(
        run_type=run_type,
        started_at=started_at,
        completed_at=completed_at,
        duration_ms=duration_ms,
        success=success,
        error_code=error_code,
        generation_mode=generation_mode,
        items_created=items_created,
        estimated_input_tokens=estimate.input_tokens,
        estimated_output_tokens=estimate.output_tokens,
        estimated_total_tokens=estimate.total_tokens,
        estimated_cost_usd=estimate.estimated_cost_usd,
        budget_limit_usd=budget_limit_usd,
        budget_exceeded=budget_exceeded,
        metadata=dict(metadata or {}),
    )
