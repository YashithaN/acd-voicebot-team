from dataclasses import dataclass
from typing import Optional
import time


@dataclass
class TranscriptSegment:
    """
    Represents one transcript segment.

    start_ms: Start timestamp in milliseconds.
    end_ms: End timestamp in milliseconds.
    confidence: Value between 0 and 1.
    is_final: True if final transcript, False if interim.
    language: Language code such as en or en-IN.
    """

    segment_id: str
    chunk_id: str
    sequence_number: int
    start_ms: int
    end_ms: int
    text: str
    confidence: float
    is_final: bool
    language: str = "en-IN"

    def __post_init__(self):

        if not self.segment_id:
            raise ValueError("Segment ID cannot be empty")

        if not self.chunk_id:
            raise ValueError("Chunk ID cannot be empty")

        if self.sequence_number < 0:
            raise ValueError("Sequence number cannot be negative")

        if self.start_ms < 0:
            raise ValueError("Start timestamp cannot be negative")

        if self.end_ms < self.start_ms:
            raise ValueError("End timestamp cannot be before start")

        if not isinstance(self.text, str):
            raise ValueError("Transcript text must be a string")

        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")

        if not isinstance(self.is_final, bool):
            raise ValueError("is_final must be True or False")

        if not self.language:
            raise ValueError("Language cannot be empty")


@dataclass
class TranscriptEvent:
    """
    Represents a transcript or error event.
    """

    event_id: str
    event_type: str
    timestamp_ms: int
    segment: Optional[TranscriptSegment] = None
    error: Optional[str] = None

    def __post_init__(self):

        if not self.event_id:
            raise ValueError("Event ID cannot be empty")

        if self.event_type not in ("transcript", "error"):
            raise ValueError("Invalid event type")

        if self.timestamp_ms < 0:
            raise ValueError("Invalid event timestamp")

        if self.event_type == "transcript":
            if self.segment is None or self.error is not None:
                raise ValueError(
                    "Transcript event must contain a segment only"
                )

        if self.event_type == "error":
            if not self.error or self.segment is not None:
                raise ValueError(
                    "Error event must contain an error message only"
                )


def current_timestamp_ms():
    return int(time.time() * 1000)