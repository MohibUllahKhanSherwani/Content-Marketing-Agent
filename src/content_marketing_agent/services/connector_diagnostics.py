from __future__ import annotations

from dataclasses import dataclass

from content_marketing_agent.config.settings import AppSettings
from content_marketing_agent.connectors.registry import build_connector_registry
from content_marketing_agent.domain.models import ConnectorCapabilities


@dataclass(frozen=True)
class ConnectorDiagnostic:
    platform: str
    requested_mode: str
    active_mode: str
    healthy: bool
    missing_credentials: list[str]
    reason: str
    action_items: list[str]


def build_connector_diagnostics(settings: AppSettings) -> list[ConnectorDiagnostic]:
    registry = build_connector_registry(settings)
    diagnostics: list[ConnectorDiagnostic] = []
    for capability in registry.capabilities():
        missing_credentials = _extract_missing_credentials(capability)
        reason = capability.reason or "No issues detected."
        healthy = _is_healthy(capability, missing_credentials)
        diagnostics.append(
            ConnectorDiagnostic(
                platform=capability.platform.value,
                requested_mode=capability.requested_mode.value,
                active_mode=capability.active_mode.value,
                healthy=healthy,
                missing_credentials=missing_credentials,
                reason=reason,
                action_items=_build_action_items(capability, missing_credentials),
            )
        )
    return diagnostics


def _extract_missing_credentials(capability: ConnectorCapabilities) -> list[str]:
    reason = capability.reason or ""
    prefix = "Missing credentials:"
    if not reason.startswith(prefix):
        return []
    values = reason.removeprefix(prefix).strip()
    if not values:
        return []
    return [name.strip() for name in values.split(",") if name.strip()]


def _is_healthy(capability: ConnectorCapabilities, missing_credentials: list[str]) -> bool:
    if missing_credentials:
        return False
    if capability.requested_mode.value == "real" and capability.active_mode.value != "real":
        return False
    return True


def _build_action_items(
    capability: ConnectorCapabilities, missing_credentials: list[str]
) -> list[str]:
    if missing_credentials:
        return [
            f"Set {name} in environment or .env for {capability.platform.value}."
            for name in missing_credentials
        ]
    if capability.requested_mode.value == "auto" and capability.active_mode.value == "mock":
        return [
            f"Provide credentials and permissions to enable real mode for {capability.platform.value}.",
        ]
    if capability.requested_mode.value == "real" and capability.active_mode.value == "real":
        return [f"Run a real integration smoke test for {capability.platform.value}."]
    return ["No action required."]
