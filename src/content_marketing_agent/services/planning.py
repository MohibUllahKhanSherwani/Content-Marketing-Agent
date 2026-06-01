from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import datetime, timezone

from content_marketing_agent.domain.enums import ContentFormat, ContentStatus, Platform
from content_marketing_agent.domain.models import ContentItem


@dataclass(frozen=True)
class MonthlyPlan:
    items: list[ContentItem]
    summary: dict[str, int]


def build_monthly_plan(*, month: str, blog_posts: int) -> MonthlyPlan:
    year, month_value = _parse_month(month)
    days_in_month = calendar.monthrange(year, month_value)[1]
    weeks_in_month = _count_mondays(year, month_value)

    items: list[ContentItem] = []
    items.extend(_blog_items(year, month_value, blog_posts, days_in_month))
    items.extend(_email_items(year, month_value, weeks_in_month))
    items.extend(_social_items(year, month_value, days_in_month))
    items.extend(_ad_items(year, month_value))
    items.extend(_landing_items(year, month_value))
    items.extend(_case_study_items(year, month_value))

    summary = {
        "blog_posts": blog_posts,
        "email_campaigns": weeks_in_month,
        "social_posts": days_in_month,
        "ad_variants": 4,
        "landing_pages": 2,
        "case_studies": 1,
        "total_items": len(items),
    }
    return MonthlyPlan(items=items, summary=summary)


def _parse_month(month: str) -> tuple[int, int]:
    parsed = datetime.strptime(month, "%Y-%m")
    return parsed.year, parsed.month


def _count_mondays(year: int, month: int) -> int:
    weeks = calendar.monthcalendar(year, month)
    return sum(1 for week in weeks if week[calendar.MONDAY] != 0)


def _scheduled_at(year: int, month: int, day: int, hour: int = 10) -> datetime:
    return datetime(year, month, day, hour, 0, 0, tzinfo=timezone.utc)


def _blog_items(year: int, month: int, count: int, days_in_month: int) -> list[ContentItem]:
    days = _spread_days(count, days_in_month)
    return [
        ContentItem(
            title=f"Blog Post {index}: Monthly Growth Strategy",
            format=ContentFormat.BLOG_POST,
            target_platform=Platform.WORDPRESS,
            status=ContentStatus.BRIEFED,
            scheduled_at=_scheduled_at(year, month, day, 9),
            metadata={"plan_type": "monthly_plan"},
        )
        for index, day in enumerate(days, start=1)
    ]


def _email_items(year: int, month: int, weeks_in_month: int) -> list[ContentItem]:
    monday_days = [week[calendar.MONDAY] for week in calendar.monthcalendar(year, month) if week[calendar.MONDAY]]
    return [
        ContentItem(
            title=f"Weekly Email Campaign {index}",
            format=ContentFormat.EMAIL_CAMPAIGN,
            target_platform=Platform.HUBSPOT,
            status=ContentStatus.BRIEFED,
            scheduled_at=_scheduled_at(year, month, day, 8),
            metadata={"plan_type": "monthly_plan"},
        )
        for index, day in enumerate(monday_days[:weeks_in_month], start=1)
    ]


def _social_items(year: int, month: int, days_in_month: int) -> list[ContentItem]:
    return [
        ContentItem(
            title=f"Daily Social Post Day {day}",
            format=ContentFormat.SOCIAL_POST,
            target_platform=Platform.LINKEDIN,
            status=ContentStatus.BRIEFED,
            scheduled_at=_scheduled_at(year, month, day, 12),
            metadata={"plan_type": "monthly_plan"},
        )
        for day in range(1, days_in_month + 1)
    ]


def _ad_items(year: int, month: int) -> list[ContentItem]:
    return [
        ContentItem(
            title=f"Ad Variant {index}",
            format=ContentFormat.AD_VARIANT,
            target_platform=Platform.META,
            status=ContentStatus.BRIEFED,
            scheduled_at=_scheduled_at(year, month, min(7 * index, 28), 14),
            metadata={"plan_type": "monthly_plan"},
        )
        for index in range(1, 5)
    ]


def _landing_items(year: int, month: int) -> list[ContentItem]:
    return [
        ContentItem(
            title=f"Landing Page Draft {index}",
            format=ContentFormat.LANDING_PAGE,
            target_platform=Platform.WORDPRESS,
            status=ContentStatus.BRIEFED,
            scheduled_at=_scheduled_at(year, month, 10 * index, 11),
            metadata={"plan_type": "monthly_plan"},
        )
        for index in range(1, 3)
    ]


def _case_study_items(year: int, month: int) -> list[ContentItem]:
    return [
        ContentItem(
            title="Monthly Case Study",
            format=ContentFormat.CASE_STUDY,
            target_platform=Platform.WORDPRESS,
            status=ContentStatus.BRIEFED,
            scheduled_at=_scheduled_at(year, month, 25, 15),
            metadata={"plan_type": "monthly_plan"},
        )
    ]


def _spread_days(count: int, days_in_month: int) -> list[int]:
    if count <= 1:
        return [1]
    step = (days_in_month - 1) / (count - 1)
    days = [int(round(1 + (index * step))) for index in range(count)]
    return sorted(set(min(max(day, 1), days_in_month) for day in days))
