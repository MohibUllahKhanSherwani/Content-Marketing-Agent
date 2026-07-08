import httpx
import respx

from content_marketing_agent.config.settings import AppSettings
from content_marketing_agent.connectors.wordpress import WordPressConnector
from content_marketing_agent.domain.enums import ConnectorMode, ContentFormat, Platform
from content_marketing_agent.domain.models import ContentItem


def _demo_item() -> ContentItem:
    return ContentItem(
        title="Draft post",
        body="Hello world",
        format=ContentFormat.BLOG_POST,
        target_platform=Platform.WORDPRESS,
    )


def test_wordpress_auto_mode_uses_mock_without_credentials() -> None:
    connector = WordPressConnector(
        AppSettings(
            wordpress_mode="auto",
            wordpress_base_url=None,
            wordpress_username=None,
            wordpress_app_password=None,
        )
    )
    result = connector.create_draft(_demo_item())
    assert result.mode == ConnectorMode.MOCK
    assert result.success is True


@respx.mock
def test_wordpress_real_create_draft_success() -> None:
    route = respx.post("https://wp.example.com/wp-json/wp/v2/posts").mock(
        return_value=httpx.Response(
            201,
            json={"id": 123, "status": "draft", "link": "https://wp.example.com/?p=123"},
        )
    )
    connector = WordPressConnector(
        AppSettings(
            wordpress_mode="real",
            wordpress_base_url="https://wp.example.com",
            wordpress_username="demo",
            wordpress_app_password="app-pass",
        )
    )
    result = connector.create_draft(_demo_item())
    assert route.called
    assert result.mode == ConnectorMode.REAL
    assert result.success is True
    assert result.platform_id == "123"
    assert result.status == "draft"


@respx.mock
def test_wordpress_real_create_draft_http_error_returns_structured_failure() -> None:
    respx.post("https://wp.example.com/wp-json/wp/v2/posts").mock(
        return_value=httpx.Response(403, json={"message": "forbidden"})
    )
    connector = WordPressConnector(
        AppSettings(
            wordpress_mode="real",
            wordpress_base_url="https://wp.example.com",
            wordpress_username="demo",
            wordpress_app_password="app-pass",
        )
    )
    result = connector.create_draft(_demo_item())
    assert result.mode == ConnectorMode.REAL
    assert result.success is False
    assert result.error_code == "wordpress_http_error"


@respx.mock
def test_wordpress_real_create_draft_with_all_optional_fields() -> None:
    import json

    def side_effect(request):
        payload = json.loads(request.content)
        assert payload["status"] == "pending"
        assert payload["excerpt"] == "SEO Description"
        assert payload["categories"] == [1, 2, 3]
        assert payload["tags"] == [4, 5]
        return httpx.Response(
            201,
            json={"id": 123, "status": "pending", "link": "https://wp.example.com/?p=123"},
        )

    route = respx.post("https://wp.example.com/wp-json/wp/v2/posts").mock(side_effect=side_effect)

    connector = WordPressConnector(
        AppSettings(
            wordpress_mode="real",
            wordpress_base_url="https://wp.example.com",
            wordpress_username="demo",
            wordpress_app_password="app-pass",
            wordpress_default_status="pending",
            wordpress_default_categories="1,2,3",
            wordpress_default_tags="4,5",
        )
    )

    item = ContentItem(
        title="Draft post",
        body="Hello world",
        format=ContentFormat.BLOG_POST,
        target_platform=Platform.WORDPRESS,
        meta_description="SEO Description",
    )

    result = connector.create_draft(item)
    assert route.called
    assert result.mode == ConnectorMode.REAL
    assert result.success is True
    assert result.status == "pending"

