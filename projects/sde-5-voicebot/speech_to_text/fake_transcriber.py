import hashlib

from speech_to_text.adapter import SpeechToTextAdapter
from speech_to_text.schemas import (
    TranscriptSegment,
    TranscriptEvent
)


class FakeTranscriber(SpeechToTextAdapter):

    def transcribe(self, audio_chunk: dict):

        chunk_id = audio_chunk["chunk_id"]
        sequence = audio_chunk["sequence_number"]

        audio_data = audio_chunk.get("audio_data", b"")

        if not isinstance(audio_data, bytes):
            raise ValueError("audio_data must be bytes")

        if not audio_data:
            raise ValueError("Audio data cannot be empty")

        audio_hash = hashlib.sha256(audio_data).hexdigest()[:12]

        mock_texts = [
            "Hello, welcome to Academia AI",
            "Today we are learning about artificial intelligence",
            "Speech recognition converts audio into text",
            "Thank you for using our voice assistant"
        ]

        text_index = int(audio_hash, 16) % len(mock_texts)
        transcript_text = mock_texts[text_index]

        segment = TranscriptSegment(
            segment_id=f"segment-{chunk_id}",
            chunk_id=chunk_id,
            sequence_number=sequence,
            start_ms=audio_chunk["start_ms"],
            end_ms=audio_chunk["end_ms"],
            text=transcript_text,
            confidence=0.95,
            is_final=True,
            language="en-IN"
        )

        event = TranscriptEvent(
            event_id=f"event-{chunk_id}",
            event_type="transcript",
            timestamp_ms=audio_chunk["end_ms"],
            segment=segment
        )

        return [event]