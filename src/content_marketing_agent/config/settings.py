from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ConnectorMode = Literal["real", "mock", "auto"]


class AppSettings(BaseSettings):
    """Environment-backed runtime settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    environment: str = "development"
    database_url: str = "sqlite:///./content_marketing_agent.db"
    connector_default_mode: ConnectorMode = "auto"
    allow_real_publish: bool = False
    monthly_token_budget_usd: int = 50
    crew_max_iterations: int = 8
    crew_task_timeout_seconds: int = 180

    azure_openai_mode: ConnectorMode = "real"
    azure_api_key: str | None = None
    azure_endpoint: str | None = None
    azure_api_version: str = "2024-06-01"
    content_agent_model: str = "azure/gpt-4o-mini"
    content_agent_review_model: str = "azure/gpt-4o"

    search_mode: ConnectorMode = "mock"
    serper_api_key: str | None = None

    wordpress_mode: ConnectorMode = "auto"
    wordpress_base_url: str | None = None
    wordpress_username: str | None = None
    wordpress_app_password: str | None = None
    wordpress_default_author_id: int | None = None

    hubspot_mode: ConnectorMode = "auto"
    hubspot_private_app_token: str | None = None
    hubspot_business_unit_id: str | None = None
    hubspot_email_template_path: str | None = None

    linkedin_mode: ConnectorMode = "auto"
    linkedin_access_token: str | None = None
    linkedin_org_urn: str | None = None

    meta_mode: ConnectorMode = "auto"
    meta_access_token: str | None = None
    meta_page_id: str | None = None
    meta_ig_user_id: str | None = None
    meta_ad_account_id: str | None = None

    ga4_mode: ConnectorMode = "auto"
    ga4_property_id: str | None = None
    google_application_credentials: str | None = Field(default=None)


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()
