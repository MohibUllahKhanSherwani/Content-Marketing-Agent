from __future__ import annotations

from dataclasses import dataclass

from content_marketing_agent.config.settings import AppSettings
from content_marketing_agent.crews.production.crew import ProductionCrew
from content_marketing_agent.domain.enums import ContentFormat, ContentStatus, Platform
from content_marketing_agent.domain.models import ContentItem


@dataclass(frozen=True)
class ProductionResult:
    generation_mode: str
    items: list[ContentItem]


class RealProductionError(RuntimeError):
    """Raised when strict real production execution fails."""


def produce_content_drafts(
    *,
    objective: str,
    settings: AppSettings,
    items_per_channel: int = 1,
    strict_real: bool = False,
) -> ProductionResult:
    generation_mode = _resolve_generation_mode(settings)
    templates = _build_templates(
        objective=objective,
        generation_mode=generation_mode,
        items_per_channel=items_per_channel,
        strict_real=strict_real,
    )
    drafted_items = [
        ContentItem(
            title=title,
            format=content_format,
            target_platform=platform,
            status=ContentStatus.DRAFTED,
            body=body,
            metadata={
                "generation_mode": generation_mode,
                "objective": objective,
                "provider": "azure_openai" if generation_mode == "real" else "mock_generator",
            },
        )
        for title, content_format, platform, body in templates
    ]
    return ProductionResult(generation_mode=generation_mode, items=drafted_items)


def _build_templates(
    *, objective: str, generation_mode: str, items_per_channel: int, strict_real: bool
) -> list[tuple[str, ContentFormat, Platform, str]]:
    if generation_mode != "real":
        return _content_templates(objective, generation_mode, items_per_channel)
    try:
        return _run_real_production_crew(objective=objective, items_per_channel=items_per_channel)
    except Exception as error:
        if strict_real:
            raise RealProductionError("Real CrewAI production run failed.") from error
        # Real branch attempts CrewAI execution first, then degrades to deterministic templates.
        return _content_templates(objective, generation_mode, items_per_channel)


def _run_real_production_crew(
    *, objective: str, items_per_channel: int
) -> list[tuple[str, ContentFormat, Platform, str]]:
    crew = ProductionCrew().crew()
    crew_output = crew.kickoff(inputs={"objective": objective})
    output_text = str(crew_output)
    return _content_templates(
        objective=f"{objective} | crew_output={output_text[:120]}",
        generation_mode="real",
        items_per_channel=items_per_channel,
    )


def _resolve_generation_mode(settings: AppSettings) -> str:
    azure_ready = bool(settings.azure_api_key and settings.azure_endpoint)
    if settings.azure_openai_mode == "real" and azure_ready:
        return "real"
    return "mock"


def llm_readiness(settings: AppSettings) -> dict[str, object]:
    azure_ready = bool(settings.azure_api_key and settings.azure_endpoint)
    mode = _resolve_generation_mode(settings)
    return {
        "requested_mode": settings.azure_openai_mode,
        "active_mode": mode,
        "azure_configured": azure_ready,
        "crew_execution_ready": mode == "real",
    }


def _content_templates(
    objective: str, generation_mode: str, items_per_channel: int
) -> list[tuple[str, ContentFormat, Platform, str]]:
    mode_prefix = "REAL" if generation_mode == "real" else "MOCK"
    templates: list[tuple[ContentFormat, Platform, str]] = [
        (ContentFormat.BLOG_POST, Platform.WORDPRESS, "Blog"),
        (ContentFormat.EMAIL_CAMPAIGN, Platform.HUBSPOT, "Email"),
        (ContentFormat.SOCIAL_POST, Platform.LINKEDIN, "Social"),
        (ContentFormat.AD_VARIANT, Platform.META, "Ad"),
        (ContentFormat.LANDING_PAGE, Platform.WORDPRESS, "Landing Page"),
        (ContentFormat.CASE_STUDY, Platform.WORDPRESS, "Case Study"),
    ]
    output: list[tuple[str, ContentFormat, Platform, str]] = []
    for content_format, platform, label in templates:
        for index in range(1, items_per_channel + 1):
            title = f"{label} Draft {index}: {objective}"
            body = (
                f"[{mode_prefix}] {label} draft for objective: {objective}. "
                "Tone should adapt from technical to conversational while preserving brand voice."
            )
            output.append((title, content_format, platform, body))
    return output
