from speech_to_text.adapter import SpeechToTextAdapter
from speech_to_text.accumulator import TranscriptAccumulator
from speech_to_text.error_handler import transcribe_with_retry
from speech_to_text.schemas import TranscriptEvent, current_timestamp_ms


class SpeechToTextOrchestrator:

    def __init__(self, provider: SpeechToTextAdapter):
        self.provider = provider
        self.accumulator = TranscriptAccumulator()

    def process_audio_chunk(self, audio_chunk: dict):
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

        except Exception as error:
            error_event = TranscriptEvent(
                event_id=f"error-{audio_chunk['chunk_id']}",
                event_type="error",
                timestamp_ms=current_timestamp_ms(),
                error=str(error)
            )

            self.accumulator.add_event(error_event)
            return [error_event]

    def get_transcript(self):
        return self.accumulator.get_transcript()

    def get_segments(self):
        return self.accumulator.get_segments()