"""Opt-in processing for caller-supplied synthetic frame data only.

This module does not capture frames or access the operating system. Frame bytes
are processed in memory and are never written to disk.
"""

from dataclasses import dataclass
import math
from typing import Protocol

from .schemas import ContextItem, ScreenContext, SourceReference


class CaptureError(ValueError):
    """Raised when synthetic frame processing is disabled or invalid."""


@dataclass(frozen=True)
class CaptureConfig:
    """Limits for synthetic frame processing; processing is disabled by default."""

    enabled: bool = False
    sample_interval_seconds: float = 1.0
    max_frame_bytes: int = 1_000_000

    def __post_init__(self) -> None:
        if not isinstance(self.enabled, bool):
            raise CaptureError("Capture enabled must be a boolean.")
        if (
            not isinstance(self.sample_interval_seconds, (int, float))
            or isinstance(self.sample_interval_seconds, bool)
            or not math.isfinite(self.sample_interval_seconds)
            or self.sample_interval_seconds <= 0
        ):
            raise CaptureError("Sampling interval must be a positive finite number.")
        if (
            not isinstance(self.max_frame_bytes, int)
            or isinstance(self.max_frame_bytes, bool)
            or self.max_frame_bytes <= 0
        ):
            raise CaptureError("Maximum frame size must be a positive integer.")


class VisionAdapter(Protocol):
    """Interface for extracting context items from synthetic frame bytes."""

    def process(self, frame_data: bytes, frame_id: str) -> list[ContextItem]:
        """Return context items inferred from an in-memory frame."""


class MockVisionAdapter:
    """Return deterministic synthetic OCR-like output without image processing."""

    def __init__(self, recognized_text: str = "Synthetic frame content") -> None:
        if not recognized_text.strip():
            raise ValueError("Recognized text must not be empty.")
        self.recognized_text = recognized_text

    def process(self, frame_data: bytes, frame_id: str) -> list[ContextItem]:
        """Create one synthetic context item; frame data is never persisted."""
        if not frame_data:
            raise CaptureError("Synthetic frame data cannot be empty.")

        return [
            ContextItem(
                item_id=f"{frame_id}-item-001",
                content=self.recognized_text,
                content_type="text",
                source=SourceReference(
                    source_id=frame_id,
                    source_type="synthetic_frame",
                    trust_level="untrusted",
                ),
                confidence=0.9,
            )
        ]


class OptInCaptureAdapter:
    """Rate-limit and size-check explicitly opted-in synthetic frame input."""

    def __init__(
        self,
        vision_adapter: VisionAdapter,
        config: CaptureConfig | None = None,
    ) -> None:
        self.config = config or CaptureConfig()
        self.vision_adapter = vision_adapter
        self._opted_in = False
        self._last_sample_timestamp: float | None = None

    def opt_in(self) -> None:
        """Record explicit caller consent for synthetic frame processing."""
        self._opted_in = True

    def opt_out(self) -> None:
        """Clear consent and reset the sampling window."""
        self._opted_in = False
        self._last_sample_timestamp = None

    def process_frame(
        self,
        frame_data: bytes,
        frame_id: str,
        timestamp: float,
    ) -> ScreenContext | None:
        """Process a due synthetic frame, or return ``None`` when sampled out."""
        if not self.config.enabled:
            raise CaptureError("Synthetic frame processing is disabled.")
        if not self._opted_in:
            raise CaptureError("Explicit opt-in is required before processing frames.")
        if not isinstance(frame_data, bytes) or not frame_data:
            raise CaptureError("Frame data must be non-empty bytes.")
        if len(frame_data) > self.config.max_frame_bytes:
            raise CaptureError("Frame data exceeds the configured size limit.")
        if not isinstance(frame_id, str) or not frame_id.strip():
            raise CaptureError("Frame ID must not be empty.")
        if (
            not isinstance(timestamp, (int, float))
            or isinstance(timestamp, bool)
            or not math.isfinite(timestamp)
            or timestamp < 0
        ):
            raise CaptureError("Timestamp must be finite and non-negative.")

        if (
            self._last_sample_timestamp is not None
            and timestamp < self._last_sample_timestamp
        ):
            raise CaptureError("Timestamp must not be less than the last sampled timestamp.")

        if (
            self._last_sample_timestamp is not None
            and timestamp - self._last_sample_timestamp
            < self.config.sample_interval_seconds
        ):
            return None

        items = self.vision_adapter.process(frame_data, frame_id)
        self._last_sample_timestamp = float(timestamp)
        return ScreenContext(
            context_id=f"context-{frame_id}",
            frame_id=frame_id,
            items=items,
            capture_enabled=False,
        )