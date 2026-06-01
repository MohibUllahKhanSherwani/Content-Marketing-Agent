from content_marketing_agent.domain.enums import ContentStatus
from content_marketing_agent.domain.models import ContentItem
from content_marketing_agent.services.calendar import demo_calendar_items


class ContentItemNotFoundError(LookupError):
    """Raised when a content item cannot be found."""


class ContentItemStore:
    """Small in-memory content item store for local demo APIs."""

    def __init__(self, seed_items: list[ContentItem] | None = None) -> None:
        items = seed_items if seed_items is not None else demo_calendar_items()
        self._items_by_id: dict[str, ContentItem] = {item.id: item for item in items}

    def list_items(self) -> list[ContentItem]:
        return list(self._items_by_id.values())

    def get_item(self, content_item_id: str) -> ContentItem:
        item = self._items_by_id.get(content_item_id)
        if item is None:
            raise ContentItemNotFoundError(content_item_id)
        return item

    def approve_item(self, content_item_id: str) -> ContentItem:
        current_item = self.get_item(content_item_id)
        approved_item = current_item.model_copy(update={"status": ContentStatus.APPROVED})
        self._items_by_id = {**self._items_by_id, content_item_id: approved_item}
        return approved_item
