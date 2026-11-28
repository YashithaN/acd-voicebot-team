
import inspect
import threading

from speech_to_text.adapter import SpeechToTextAdapter
from speech_to_text.accumulator import TranscriptAccumulator
from speech_to_text.fake_transcriber import FakeTranscriber

from speech_to_text.error_handler import (
    transcribe_with_retry,
    SpeechToTextError,
)

from speech_to_text.schemas import (
    TranscriptEvent,
    current_timestamp_ms,
)


class _TranscriptionMethodAdapter:

    def __init__(self, provider, use_lifecycle=False):
        self.provider = provider
        self.use_lifecycle = use_lifecycle

    def transcribe(self, audio_chunk, cancellation_event=None):

        method = self.provider.transcribe

        if (
            self.use_lifecycle
            and callable(getattr(self.provider, "transcribe_lifecycle", None))
        ):
            method = self.provider.transcribe_lifecycle

        parameters = inspect.signature(method).parameters

        if "cancellation_event" in parameters:
            return method(
                audio_chunk,
                cancellation_event=cancellation_event
            )

        if "cancel_event" in parameters:
            return method(
                audio_chunk,
                cancel_event=cancellation_event
            )

        return method(audio_chunk)


class SpeechToTextOrchestrator:

    FALLBACK_ERROR_CODES = {
        "QUOTA_EXCEEDED",
        "NETWORK_ERROR"
    }

    def __init__(
        self,
        provider: SpeechToTextAdapter,
        confidence_threshold=0.70,
        emit_revisions=False,
        fallback_provider=None
    ):

        if not isinstance(confidence_threshold, (int, float)):
            raise ValueError("Confidence threshold must be a number")

        if not 0 <= confidence_threshold <= 1:
            raise ValueError("Confidence threshold must be between 0 and 1")

        self.provider = provider

        self.fallback_provider = (
            fallback_provider
            if fallback_provider is not None
            else FakeTranscriber()
        )

        self.accumulator = TranscriptAccumulator()

        self.confidence_threshold = confidence_threshold
        self.emit_revisions = emit_revisions

        self.processed_chunks = set()

        self.primary_adapter = _TranscriptionMethodAdapter(
            self.provider,
            use_lifecycle=emit_revisions
        )

        self.fallback_adapter = _TranscriptionMethodAdapter(
            self.fallback_provider,
            use_lifecycle=emit_revisions
        )

        self.last_provider_used = None
        self.fallback_used = False

        # Active cancellation tracking
        self.active_cancellations = {}
        self.cancellation_lock = threading.Lock()

    # ----------------------------------
    # CANCELLATION
    # ----------------------------------

    def cancel_transcription(self, chunk_id, session_id="default"):

        chunk_key = (session_id, chunk_id)

        with self.cancellation_lock:

            cancellation_event = self.active_cancellations.get(chunk_key)

            if cancellation_event is None:
                return False

            cancellation_event.set()
            return True

    # ----------------------------------
    # TRANSCRIPTION
    # ----------------------------------

    def _transcribe(self, adapter, audio_chunk, cancellation_event):

        return transcribe_with_retry(
            adapter,
            audio_chunk,
            timeout_seconds=5,
            max_retries=2,
            cancellation_event=cancellation_event
        )

    # ----------------------------------
    # EVENT PREPARATION
    # ----------------------------------

    def _prepare_events(self, events, session_id, correlation_id):

        accepted_events = []

        for event in events:

            event.session_id = session_id
            event.correlation_id = correlation_id

            if event.segment is not None:

                event.segment.session_id = session_id
                event.segment.correlation_id = correlation_id

                if event.segment.confidence < self.confidence_threshold:
                    continue

            self.accumulator.add_event(event)
            accepted_events.append(event)

        return accepted_events

    # ----------------------------------
    # ERROR EVENT
    # ----------------------------------

    def _create_error_event(
        self,
        error,
        chunk_id,
        session_id,
        correlation_id
    ):

        return TranscriptEvent(
            event_id=f"error-{session_id}-{chunk_id}",
            event_type="error",
            timestamp_ms=current_timestamp_ms(),
            error_code=error.error_code,
            message=str(error),
            retryable=error.retryable,
            session_id=session_id,
            correlation_id=correlation_id
        )

    # ----------------------------------
    # PROCESS AUDIO CHUNK
    # ----------------------------------

    def process_audio_chunk(self, audio_chunk):

        chunk_id = audio_chunk.get("chunk_id", "unknown")
        session_id = audio_chunk.get("session_id", "default")
        correlation_id = audio_chunk.get("correlation_id", "default")

        chunk_key = (session_id, chunk_id)

        if chunk_key in self.processed_chunks:
            return []

        self.processed_chunks.add(chunk_key)

        cancellation_event = threading.Event()

        with self.cancellation_lock:
            self.active_cancellations[chunk_key] = cancellation_event

        self.fallback_used = False
        self.last_provider_used = None

        try:

            # Check cancellation before starting
            if cancellation_event.is_set():
                raise SpeechToTextError(
                    "Transcription was cancelled",
                    "CANCELLED",
                    False
                )

            # First attempt: primary provider
            try:

                events = self._transcribe(
                    self.primary_adapter,
                    audio_chunk,
                    cancellation_event
                )

                self.last_provider_used = "primary"

            except SpeechToTextError as primary_error:

                # Cancellation must never trigger fallback
                if primary_error.error_code == "CANCELLED":
                    raise

                # Only quota and network failures trigger fallback
                if primary_error.error_code not in self.FALLBACK_ERROR_CODES:
                    raise

                if cancellation_event.is_set():
                    raise SpeechToTextError(
                        "Transcription was cancelled",
                        "CANCELLED",
                        False
                    )

                # Use mock provider as fallback
                self.fallback_used = True

                events = self._transcribe(
                    self.fallback_adapter,
                    audio_chunk,
                    cancellation_event
                )

                self.last_provider_used = "mock"

            if cancellation_event.is_set():
                raise SpeechToTextError(
                    "Transcription was cancelled",
                    "CANCELLED",
                    False
                )

            return self._prepare_events(
                events,
                session_id,
                correlation_id
            )

        except SpeechToTextError as error:

            error_event = self._create_error_event(
                error,
                chunk_id,
                session_id,
                correlation_id
            )

            self.accumulator.add_event(error_event)

            return [error_event]

        except Exception:

            safe_error = SpeechToTextError(
                "An unexpected transcription error occurred",
                "INTERNAL_ERROR",
                False
            )

            error_event = self._create_error_event(
                safe_error,
                chunk_id,
                session_id,
                correlation_id
            )

            self.accumulator.add_event(error_event)

            return [error_event]

        finally:

            # Remove completed transcription from active tracking
            with self.cancellation_lock:
                self.active_cancellations.pop(chunk_key, None)

    # ----------------------------------
    # TRANSCRIPT ACCESS
    # ----------------------------------

    def get_transcript(self, session_id=None):

        return self.accumulator.get_transcript(session_id)

    def get_segments(self, session_id=None):

        return self.accumulator.get_segments(session_id)
