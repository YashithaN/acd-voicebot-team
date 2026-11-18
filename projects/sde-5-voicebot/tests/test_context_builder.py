"""Tests for bounded context selection."""

from datetime import datetime, timedelta, timezone
import math

from context_reasoning.context_builder import ContextBuildConfig, ContextBuilder
from context_reasoning.schemas import ContextItem, ScreenContext, SourceReference


NOW = datetime(2026, 11, 13, 12, 0, tzinfo=timezone.utc)


def make_item(item_id, content, created_at, source_id=None):
    return ContextItem(
        item_id=item_id,
        content=content,
        content_type="text",
        source=SourceReference(
            source_id=source_id or item_id,
            source_type="user_text",
            trust_level="untrusted",
        ),
        confidence=0.9,
        created_at=created_at,
    )


def make_context(items):
    return ScreenContext(
        context_id="context-001",
        frame_id="synthetic-frame-001",
        items=items,
    )


def test_context_respects_approximate_token_budget():
    items = [
        make_item("one", "abcdefgh", NOW),
        make_item("two", "ijklmnop", NOW - timedelta(seconds=1)),
    ]
    builder = ContextBuilder(ContextBuildConfig(max_tokens=2))

    result = builder.build(make_context(items), now=NOW)

    assert [item.item_id for item in result.items] == ["one"]
    assert math.ceil(len(result.items[0].content) / 4) <= 2
    assert result.capture_enabled is False


def test_relevant_items_are_preferred_over_newer_unrelated_items():
    relevant = make_item("relevant", "The screen shows a Submit button", NOW - timedelta(minutes=5))
    recent = make_item("recent", "A blue panel is open", NOW)
    builder = ContextBuilder(ContextBuildConfig(max_tokens=100))

    result = builder.build(
        make_context([recent, relevant]),
        question="Where is the Submit button?",
        now=NOW,
    )

    assert [item.item_id for item in result.items] == ["relevant", "recent"]


def test_stale_items_are_dropped():
    fresh = make_item("fresh", "Current status", NOW - timedelta(minutes=2))
    stale = make_item("stale", "Old status", NOW - timedelta(hours=2))
    builder = ContextBuilder(ContextBuildConfig(max_age_seconds=600))

    result = builder.build(make_context([fresh, stale]), now=NOW)

    assert [item.item_id for item in result.items] == ["fresh"]


def test_duplicate_content_is_removed_and_newest_copy_is_kept():
    older = make_item("older", "Project status: active", NOW - timedelta(minutes=2))
    newer = make_item("newer", " project   status: ACTIVE ", NOW)
    builder = ContextBuilder()

    result = builder.build(make_context([older, newer]), now=NOW)

    assert [item.item_id for item in result.items] == ["newer"]