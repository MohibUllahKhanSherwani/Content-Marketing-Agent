"""Tests for LinkedInConnector.

Covers:
- auto mode falls back to mock when credentials are missing
- real mode fails loudly when credentials are missing
- real mode succeeds with person URN (personal profile posting)
- real mode succeeds with org URN (company page posting)
- real mode surfaces LinkedIn API errors cleanly
- real mode handles network timeouts
"""

from __future__ import annotations

import pytest
import respx
import httpx

from content_marketing_agent.config.settings import AppSettings
from content_marketing_agent.connectors.linkedin import LinkedInConnector
from content_marketing_agent.domain.enums import ConnectorMode, Platform
from content_marketing_agent.domain.models import ContentItem, ContentFormat

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_PERSON_URN = "urn:li:person:abc123"
_ORG_URN = "urn:li:organization:9876543"
_FAKE_TOKEN = "AQX_fake_access_token"
_POST_URN = "urn:li:share:7654321"


def _make_settings(
    mode: str = "auto",
    token: str | None = _FAKE_TOKEN,
    author_urn: str | None = _PERSON_URN,
) -> AppSettings:
    return AppSettings(
        linkedin_mode=mode,
        linkedin_access_token=token,
        linkedin_org_urn=author_urn,
    )


def _make_content_item(body: str = "Test LinkedIn post body.") -> ContentItem:
    return ContentItem(
        title="Test LinkedIn Post",
        body=body,
        format=ContentFormat.SOCIAL_POST,
        target_platform=Platform.LINKEDIN,
    )


# ---------------------------------------------------------------------------
# Capability / mode tests (no HTTP calls)
# ---------------------------------------------------------------------------


def test_auto_falls_back_to_mock_when_token_missing() -> None:
    settings = _make_settings(mode="auto", token=None, author_urn=None)
    connector = LinkedInConnector(settings)

    caps = connector.check_capabilities()

    assert caps.requested_mode == ConnectorMode.AUTO
    assert caps.active_mode == ConnectorMode.MOCK
    assert "Missing credentials" in (caps.reason or "")


def test_auto_falls_back_to_mock_when_only_token_missing() -> None:
    settings = _make_settings(mode="auto", token=None, author_urn=_PERSON_URN)
    connector = LinkedInConnector(settings)

    caps = connector.check_capabilities()

    assert caps.active_mode == ConnectorMode.MOCK
    assert "LINKEDIN_ACCESS_TOKEN" in (caps.reason or "")


def test_real_mode_fails_loudly_when_credentials_missing() -> None:
    settings = _make_settings(mode="real", token=None, author_urn=None)
    connector = LinkedInConnector(settings)

    caps = connector.check_capabilities()

    assert caps.requested_mode == ConnectorMode.REAL
    assert caps.active_mode == ConnectorMode.REAL
    assert caps.can_create_draft is False
    assert "Missing credentials" in (caps.reason or "")


def test_auto_with_both_credentials_resolves_to_real() -> None:
    settings = _make_settings(mode="auto", token=_FAKE_TOKEN, author_urn=_PERSON_URN)
    connector = LinkedInConnector(settings)

    caps = connector.check_capabilities()

    assert caps.active_mode == ConnectorMode.REAL
    assert caps.can_create_draft is True


# ---------------------------------------------------------------------------
# Real HTTP posting — personal profile URN
# ---------------------------------------------------------------------------


@respx.mock
def test_create_draft_with_person_urn_succeeds() -> None:
    """create_draft posts to /rest/posts and returns the post URN."""
    respx.post("https://api.linkedin.com/rest/posts").mock(
        return_value=httpx.Response(
            201,
            headers={"x-restli-id": _POST_URN},
            text="",
        )
    )
    settings = _make_settings(mode="real", token=_FAKE_TOKEN, author_urn=_PERSON_URN)
    connector = LinkedInConnector(settings)
    item = _make_content_item()

    result = connector.create_draft(item)

    assert result.success is True
    assert result.mode == ConnectorMode.REAL
    assert result.platform_id == _POST_URN
    assert "linkedin.com/feed/update" in (result.platform_url or "")


@respx.mock
def test_publish_with_person_urn_succeeds() -> None:
    respx.post("https://api.linkedin.com/rest/posts").mock(
        return_value=httpx.Response(
            201,
            headers={"x-restli-id": _POST_URN},
            text="",
        )
    )
    settings = _make_settings(mode="real", token=_FAKE_TOKEN, author_urn=_PERSON_URN)
    connector = LinkedInConnector(settings)
    item = _make_content_item()

    result = connector.publish(item)

    assert result.success is True
    assert result.platform_id == _POST_URN


# ---------------------------------------------------------------------------
# Real HTTP posting — org URN (same endpoint, different author field)
# ---------------------------------------------------------------------------


@respx.mock
def test_create_draft_with_org_urn_succeeds() -> None:
    route = respx.post("https://api.linkedin.com/rest/posts").mock(
        return_value=httpx.Response(
            201,
            headers={"x-restli-id": _POST_URN},
            text="",
        )
    )
    settings = _make_settings(mode="real", token=_FAKE_TOKEN, author_urn=_ORG_URN)
    connector = LinkedInConnector(settings)
    item = _make_content_item()

    result = connector.create_draft(item)

    assert result.success is True
    # Verify the author field sent was the org URN
    import json
    sent_body = json.loads(route.calls[0].request.content)
    assert sent_body["author"] == _ORG_URN


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


@respx.mock
def test_create_draft_surfaces_linkedin_api_error() -> None:
    respx.post("https://api.linkedin.com/rest/posts").mock(
        return_value=httpx.Response(
            401,
            json={"message": "Unauthorized", "status": 401},
        )
    )
    settings = _make_settings(mode="real", token="bad_token", author_urn=_PERSON_URN)
    connector = LinkedInConnector(settings)
    item = _make_content_item()

    result = connector.create_draft(item)

    assert result.success is False
    assert result.error_code == "linkedin_http_error"
    assert "401" in result.human_message


@respx.mock
def test_create_draft_handles_timeout() -> None:
    respx.post("https://api.linkedin.com/rest/posts").mock(
        side_effect=httpx.TimeoutException("timed out")
    )
    settings = _make_settings(mode="real", token=_FAKE_TOKEN, author_urn=_PERSON_URN)
    connector = LinkedInConnector(settings)
    item = _make_content_item()

    result = connector.create_draft(item)

    assert result.success is False
    assert result.error_code == "linkedin_timeout"


@respx.mock
def test_create_draft_handles_network_error() -> None:
    respx.post("https://api.linkedin.com/rest/posts").mock(
        side_effect=httpx.ConnectError("connection refused")
    )
    settings = _make_settings(mode="real", token=_FAKE_TOKEN, author_urn=_PERSON_URN)
    connector = LinkedInConnector(settings)
    item = _make_content_item()

    result = connector.create_draft(item)

    assert result.success is False
    assert result.error_code == "linkedin_network_error"


# ---------------------------------------------------------------------------
# Mock mode — verify mock connector is still usable
# ---------------------------------------------------------------------------


def test_forced_mock_mode_never_hits_network() -> None:
    settings = _make_settings(mode="mock", token=_FAKE_TOKEN, author_urn=_PERSON_URN)
    connector = LinkedInConnector(settings)
    item = _make_content_item()

    # Should not raise even with no network access
    result = connector.create_draft(item)

    assert result.success is True
    assert result.mode == ConnectorMode.MOCK
    assert "mock" in (result.platform_id or "").lower()
