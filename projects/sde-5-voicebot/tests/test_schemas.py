
"""Tests for the W3 context and reasoning schemas."""

import pytest
from pydantic import ValidationError

from context_reasoning.schemas import (
    SourceReference,
    ContextItem,
    ScreenContext,
    ReasoningRequest,
    ReasoningResult,
)


def create_valid_context():
    """Create reusable synthetic context for tests."""

    source = SourceReference(
        source_id="source-001",
        source_type="synthetic_frame",
        trust_level="untrusted",
    )

    item = ContextItem(
        item_id="item-001",
        content="Synthetic button labelled Submit",
        content_type="ui_element",
        source=source,
        confidence=0.95,
    )

    return ScreenContext(
        context_id="context-001",
        frame_id="frame-001",
        items=[item],
    )


def test_source_reference():
    source = SourceReference(
        source_id="source-001",
        source_type="synthetic_frame",
        trust_level="untrusted",
    )

    assert source.source_id == "source-001"


def test_context_item():
    context = create_valid_context()

    assert context.items[0].item_id == "item-001"
    assert context.items[0].confidence == 0.95


def test_screen_context():
    context = create_valid_context()

    assert context.capture_enabled is False
    assert context.frame_width_px == 1280
    assert len(context.items) == 1


def test_reasoning_request():
    request = ReasoningRequest(
        request_id="request-001",
        question="What does the button say?",
        context=create_valid_context(),
        prompt_version="v1",
    )

    assert request.request_id == "request-001"


def test_reasoning_result():
    result = ReasoningResult(
        request_id="request-001",
        answer="The button says Submit.",
        grounded_item_ids=["item-001"],
        confidence=0.95,
        prompt_version="v1",
    )

    assert result.mode == "mock"
    assert result.grounded_item_ids == ["item-001"]


def test_invalid_confidence_rejected():
    with pytest.raises(ValidationError):
        ContextItem(
            item_id="item-002",
            content="Example",
            content_type="text",
            source=SourceReference(
                source_id="source-002",
                source_type="user_text",
                trust_level="untrusted",
            ),
            confidence=1.5,
        )


def test_real_screen_capture_rejected():
    with pytest.raises(ValidationError):
        ScreenContext(
            context_id="context-002",
            frame_id="frame-002",
            capture_enabled=True,
        )


def test_duplicate_context_item_ids_rejected():
    context = create_valid_context()
    duplicate_item = context.items[0].model_copy()

    with pytest.raises(ValidationError):
        ScreenContext(
            context_id="context-003",
            frame_id="frame-003",
            items=[context.items[0], duplicate_item],
        )


def test_duplicate_grounded_ids_rejected():
    with pytest.raises(ValidationError):
        ReasoningResult(
            request_id="request-002",
            answer="Example answer",
            grounded_item_ids=["item-001", "item-001"],
            confidence=0.8,
        )
