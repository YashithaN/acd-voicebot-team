
from dataclasses import dataclass
from enum import Enum
import time
from typing import Optional

from audio.schemas import AudioChunk


class SpeechEventError(ValueError):
    """Raised when a speech event is invalid."""


class SpeechEventType(Enum):
    SPEECH_STARTED = "speech_started"
    SPEECH_ENDED = "speech_ended"
    AUDIO_CHUNK = "audio_chunk"


@dataclass(frozen=True)
class SpeechEvent:
    """Represents a normalized speech or audio event."""

    event_type: SpeechEventType
    session_id: str
    correlation_id: str
    timestamp_ms: int
    sequence_id: Optional[int] = None
    audio_chunk: Optional[AudioChunk] = None

    def __post_init__(self):
        if not isinstance(self.event_type, SpeechEventType):
            raise SpeechEventError("Invalid speech event type.")

        if not self.session_id:
            raise SpeechEventError("Session ID cannot be empty.")

        if not self.correlation_id:
            raise SpeechEventError("Correlation ID cannot be empty.")

        if (
            isinstance(self.timestamp_ms, bool)
            or not isinstance(self.timestamp_ms, int)
            or self.timestamp_ms < 0
        ):
            raise SpeechEventError("Timestamp must be a non-negative integer.")

        if self.event_type == SpeechEventType.AUDIO_CHUNK:
            if not isinstance(self.audio_chunk, AudioChunk):
                raise SpeechEventError(
                    "Audio chunk event requires a valid AudioChunk."
                )

            if self.sequence_id != self.audio_chunk.sequence_id:
                raise SpeechEventError(
                    "Event sequence ID must match the audio chunk."
                )

        elif self.audio_chunk is not None or self.sequence_id is not None:
            raise SpeechEventError(
                "Speech boundary events cannot contain audio chunk data."
            )


def current_timestamp_ms():
    """Return the current timestamp in milliseconds."""
    return int(time.time() * 1000)