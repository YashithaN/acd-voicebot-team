"""Tests for the synthetic-only opt-in capture adapter."""

import pytest

from context_reasoning.capture_adapter import (
    CaptureConfig,
    CaptureError,
    MockVisionAdapter,
    OptInCaptureAdapter,
)


def make_adapter(**config_values):
    return OptInCaptureAdapter(
        MockVisionAdapter("Synthetic Submit button"),
        CaptureConfig(**config_values),
    )


def test_capture_processing_is_disabled_by_default():
    adapter = OptInCaptureAdapter(MockVisionAdapter())

    with pytest.raises(CaptureError, match="disabled"):
        adapter.process_frame(b"synthetic", "frame-001", 0.0)


def test_enabled_processing_still_requires_explicit_opt_in():
    adapter = make_adapter(enabled=True)

    with pytest.raises(CaptureError, match="opt-in"):
        adapter.process_frame(b"synthetic", "frame-001", 0.0)


def test_sampling_interval_limits_processed_frames():
    adapter = make_adapter(enabled=True, sample_interval_seconds=2.0)
    adapter.opt_in()

    first = adapter.process_frame(b"synthetic", "frame-001", 0.0)
    skipped = adapter.process_frame(b"synthetic", "frame-002", 1.5)
    second = adapter.process_frame(b"synthetic", "frame-003", 2.0)

    assert first is not None
    assert skipped is None
    assert second is not None
    assert first.capture_enabled is False
    assert second.frame_id == "frame-003"


def test_decreasing_timestamp_is_rejected_without_changing_sample_boundary():
    adapter = make_adapter(enabled=True, sample_interval_seconds=2.0)
    adapter.opt_in()

    first = adapter.process_frame(b"synthetic", "frame-001", 2.0)

    with pytest.raises(CaptureError, match="less than the last sampled timestamp"):
        adapter.process_frame(b"synthetic", "frame-002", 1.0)

    skipped = adapter.process_frame(b"synthetic", "frame-003", 3.5)
    second = adapter.process_frame(b"synthetic", "frame-004", 4.0)

    assert first is not None
    assert skipped is None
    assert second is not None


def test_frame_size_limit_is_enforced():
    adapter = make_adapter(enabled=True, max_frame_bytes=4)
    adapter.opt_in()

    with pytest.raises(CaptureError, match="size limit"):
        adapter.process_frame(b"12345", "frame-001", 0.0)


def test_mock_vision_returns_synthetic_context_without_real_capture():
    adapter = make_adapter(enabled=True)
    adapter.opt_in()

    context = adapter.process_frame(b"synthetic frame bytes", "frame-001", 0.0)

    assert context is not None
    assert context.capture_enabled is False
    assert context.items[0].content == "Synthetic Submit button"
    assert context.items[0].source.source_type == "synthetic_frame"
    assert context.items[0].source.trust_level == "untrusted"


def test_opt_out_requires_new_opt_in():
    adapter = make_adapter(enabled=True)
    adapter.opt_in()
    adapter.opt_out()

    with pytest.raises(CaptureError, match="opt-in"):
        adapter.process_frame(b"synthetic", "frame-001", 0.0)