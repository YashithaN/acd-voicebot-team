from speech_to_text.adapter import SpeechToTextAdapter
from speech_to_text.accumulator import TranscriptAccumulator
from speech_to_text.error_handler import (
    transcribe_with_retry,
    SpeechToTextError
)
from speech_to_text.schemas import (
    TranscriptEvent,
    current_timestamp_ms
)


class SpeechToTextOrchestrator:

    def __init__(self, provider: SpeechToTextAdapter):
        self.provider = provider
        self.accumulator = TranscriptAccumulator()
        self.processed_chunks = set()

    def process_audio_chunk(self, audio_chunk: dict):

        chunk_id = audio_chunk.get("chunk_id", "unknown")

        # Ignore duplicate chunks
        if chunk_id in self.processed_chunks:
            return []

        self.processed_chunks.add(chunk_id)

        try:
            events = transcribe_with_retry(
                self.provider,
                audio_chunk,
                timeout_seconds=5,
                max_retries=2
            )

            for event in events:
                self.accumulator.add_event(event)

            return events

        except SpeechToTextError as error:

            error_event = TranscriptEvent(
                event_id=f"error-{chunk_id}",
                event_type="error",
                timestamp_ms=current_timestamp_ms(),
                error_code=error.error_code,
                message=str(error),
                retryable=error.retryable
            )

            self.accumulator.add_event(error_event)

            return [error_event]

        except Exception:

            # Never expose raw exception details
            error_event = TranscriptEvent(
                event_id=f"error-{chunk_id}",
                event_type="error",
                timestamp_ms=current_timestamp_ms(),
                error_code="INTERNAL_ERROR",
                message="An unexpected transcription error occurred",
                retryable=False
            )

            self.accumulator.add_event(error_event)

            return [error_event]

    def get_transcript(self):
        return self.accumulator.get_transcript()

    def get_segments(self):
        return self.accumulator.get_segments()