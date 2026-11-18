
"""Synthetic screen context fixtures for W3.

No real screen capture or operating-system access is performed.
"""

from .schemas import ContextItem, ScreenContext, SourceReference


def create_sample_context() -> ScreenContext:
    """Return a deterministic synthetic screen context for demos and tests."""

    source = SourceReference(
        source_id="synthetic-frame-001",
        source_type="synthetic_frame",
        trust_level="untrusted",
    )

    items = [
        ContextItem(
            item_id="item-001",
            content="Academiaai Voicebot project dashboard",
            content_type="ui_element",
            source=source,
            confidence=0.99,
        ),
        ContextItem(
            item_id="item-002",
            content="Current task: implement context and reasoning",
            content_type="text",
            source=source,
            confidence=0.98,
        ),
        ContextItem(
            item_id="item-003",
            content="Project status: in progress",
            content_type="application_state",
            source=source,
            confidence=0.95,
        ),
    ]

    return ScreenContext(
        context_id="sample-context-001",
        frame_id="synthetic-frame-001",
        items=items,
        capture_enabled=False,
        frame_width_px=1280,
        frame_height_px=720,
    )
