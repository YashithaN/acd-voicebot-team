
from uuid import uuid4

from audio.events import (
    SpeechEvent,
    SpeechEventType,
    current_timestamp_ms,
)
from audio.schemas import AudioChunk
from audio.vad import VoiceActivityDetector


class PipelineError(ValueError):
    """Raised when an invalid audio pipeline operation occurs."""


class AudioEventPipeline:
    """
    Converts audio chunks and VAD decisions into ordered speech events.

    Audio levels are supplied separately because AudioChunk contains
    raw audio bytes, not a calculated audio-level measurement.
    """

    def __init__(
        self,
        vad: VoiceActivityDetector,
        session_id: str,
        correlation_id: str = None,
    ):
        if not isinstance(vad, VoiceActivityDetector):
            raise PipelineError("A valid VAD implementation is required.")

        if not session_id:
            raise PipelineError("Session ID cannot be empty.")

        self.vad = vad
        self.session_id = session_id
        self.correlation_id = correlation_id or str(uuid4())
        self.speech_active = False
        self.last_sequence_id = None
        self.events = []

    def process_chunk(
        self,
        chunk: AudioChunk,
        audio_level: float,
        duration_ms: float,
    ):
        """Process one chunk and return the events generated."""

        if not isinstance(chunk, AudioChunk):
            raise PipelineError("A valid AudioChunk is required.")

        if (
            self.last_sequence_id is not None
            and chunk.sequence_id <= self.last_sequence_id
        ):
            raise PipelineError("Audio chunks must arrive in sequence order.")

        detected = self.vad.process(audio_level, duration_ms)
        generated = []

        if detected and not self.speech_active:
            generated.append(
                SpeechEvent(
                    event_type=SpeechEventType.SPEECH_STARTED,
                    session_id=self.session_id,
                    correlation_id=self.correlation_id,
                    timestamp_ms=current_timestamp_ms(),
                )
            )
            self.speech_active = True

        if self.speech_active:
            generated.append(
                SpeechEvent(
                    event_type=SpeechEventType.AUDIO_CHUNK,
                    session_id=self.session_id,
                    correlation_id=self.correlation_id,
                    timestamp_ms=current_timestamp_ms(),
                    sequence_id=chunk.sequence_id,
                    audio_chunk=chunk,
                )
            )

        if not detected and self.speech_active:
            generated.append(
                SpeechEvent(
                    event_type=SpeechEventType.SPEECH_ENDED,
                    session_id=self.session_id,
                    correlation_id=self.correlation_id,
                    timestamp_ms=current_timestamp_ms(),
                )
            )
            self.speech_active = False

        self.last_sequence_id = chunk.sequence_id
        self.events.extend(generated)

        return generated

    def finish(self):
        """Close an active speech segment when the session finishes."""

        generated = []

        if self.speech_active:
            generated.append(
                SpeechEvent(
                    event_type=SpeechEventType.SPEECH_ENDED,
                    session_id=self.session_id,
                    correlation_id=self.correlation_id,
                    timestamp_ms=current_timestamp_ms(),
                )
            )
            self.speech_active = False

        self.events.extend(generated)
        return generated
