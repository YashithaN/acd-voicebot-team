"""Build bounded screen contexts from existing context item schemas.

The token estimate is intentionally simple and provider-independent: each
item's text costs ``ceil(character_count / 4)`` approximate tokens. Metadata,
prompt instructions, and tokenizer-specific differences are not included.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import math
import re

from .schemas import ContextItem, ScreenContext


class ContextBuildError(ValueError):
    """Raised when context-building limits are invalid."""


@dataclass(frozen=True)
class ContextBuildConfig:
    """Limits for context age and approximate text-token budget."""

    max_tokens: int = 1000
    max_age_seconds: float = 3600.0

    def __post_init__(self) -> None:
        if (
            not isinstance(self.max_tokens, int)
            or isinstance(self.max_tokens, bool)
            or self.max_tokens <= 0
        ):
            raise ContextBuildError("Maximum token budget must be a positive integer.")
        if (
            not isinstance(self.max_age_seconds, (int, float))
            or isinstance(self.max_age_seconds, bool)
            or not math.isfinite(self.max_age_seconds)
            or self.max_age_seconds < 0
        ):
            raise ContextBuildError("Maximum age must be a finite non-negative number.")


class ContextBuilder:
    """Filter, rank, deduplicate, and bound items in a ScreenContext."""

    def __init__(self, config: ContextBuildConfig | None = None) -> None:
        self.config = config or ContextBuildConfig()

    def build(
        self,
        context: ScreenContext,
        question: str = "",
        now: datetime | None = None,
    ) -> ScreenContext:
        """Return a new context containing only fresh, unique, budgeted items."""
        current_time = now or datetime.now(timezone.utc)
        if current_time.tzinfo is None:
            raise ContextBuildError("Current time must include a timezone.")
        current_time = current_time.astimezone(timezone.utc)

        query_terms = set(re.findall(r"\w+", question.casefold()))
        fresh_items = [
            item
            for item in context.items
            if self._age_seconds(item, current_time) <= self.config.max_age_seconds
        ]
        ranked_items = sorted(
            fresh_items,
            key=lambda item: (
                self._relevance(item, query_terms),
                self._created_at_utc(item),
                item.confidence,
            ),
            reverse=True,
        )

        selected: list[ContextItem] = []
        seen_ids: set[str] = set()
        seen_content: set[str] = set()
        tokens_used = 0

        for item in ranked_items:
            normalized_content = " ".join(item.content.casefold().split())
            if item.item_id in seen_ids or normalized_content in seen_content:
                continue

            item_tokens = math.ceil(len(item.content) / 4)
            if tokens_used + item_tokens > self.config.max_tokens:
                continue

            selected.append(item)
            seen_ids.add(item.item_id)
            seen_content.add(normalized_content)
            tokens_used += item_tokens

        return ScreenContext(
            context_id=context.context_id,
            frame_id=context.frame_id,
            items=selected,
            capture_enabled=False,
            frame_width_px=context.frame_width_px,
            frame_height_px=context.frame_height_px,
            created_at=current_time,
        )

    @staticmethod
    def _created_at_utc(item: ContextItem) -> datetime:
        created_at = item.created_at
        if created_at.tzinfo is None:
            return created_at.replace(tzinfo=timezone.utc)
        return created_at.astimezone(timezone.utc)

    @classmethod
    def _age_seconds(cls, item: ContextItem, now: datetime) -> float:
        return (now - cls._created_at_utc(item)).total_seconds()

    @staticmethod
    def _relevance(item: ContextItem, query_terms: set[str]) -> int:
        if not query_terms:
            return 0
        item_terms = set(re.findall(r"\w+", item.content.casefold()))
        return len(query_terms & item_terms)