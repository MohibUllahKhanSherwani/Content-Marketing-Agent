from enum import Enum


class StrEnum(str, Enum):
    """Python 3.10-compatible string enum base."""


class ConnectorMode(StrEnum):
    REAL = "real"
    MOCK = "mock"
    AUTO = "auto"


class Platform(StrEnum):
    GEMINI = "gemini"
    WORDPRESS = "wordpress"
    HUBSPOT = "hubspot"
    LINKEDIN = "linkedin"
    META = "meta"
    GA4 = "ga4"
    SEARCH = "search"


class ContentStatus(StrEnum):
    IDEA = "idea"
    BRIEFED = "briefed"
    DRAFTED = "drafted"
    QA_FAILED = "qa_failed"
    READY_FOR_REVIEW = "ready_for_review"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    PUBLISH_FAILED = "publish_failed"
    ARCHIVED = "archived"


class ContentFormat(StrEnum):
    BLOG_POST = "blog_post"
    EMAIL_CAMPAIGN = "email_campaign"
    SOCIAL_POST = "social_post"
    AD_VARIANT = "ad_variant"
    LANDING_PAGE = "landing_page"
    CASE_STUDY = "case_study"


class PublicationOperation(StrEnum):
    CREATE_DRAFT = "create_draft"
    SCHEDULE = "schedule"
    PUBLISH = "publish"
    FETCH_METRICS = "fetch_metrics"
