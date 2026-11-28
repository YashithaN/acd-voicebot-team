import hashlib

from speech_to_text.adapter import SpeechToTextAdapter
from speech_to_text.schemas import (
    TranscriptSegment,
    TranscriptEvent
)


class FakeTranscriber(SpeechToTextAdapter):
    """
    Deterministic mock speech-to-text provider.

    Supports:
    - Normal transcription
    - Interim transcript generation
    - Transcript revisions
    - Finalization events
    - Session-aware events

    No external API or API key is required.
    """

    MOCK_TEXTS = [
        "Hello, welcome to Academia AI",
        "Today we are learning about artificial intelligence",
        "Speech recognition converts audio into text",
        "Thank you for using our voice assistant"
    ]

    def _generate_text(self, audio_data):
        """
        Generate deterministic text from audio bytes.
        """

        audio_hash = hashlib.sha256(
            audio_data
        ).hexdigest()[:12]

        text_index = int(
            audio_hash, 16
        ) % len(self.MOCK_TEXTS)

        return self.MOCK_TEXTS[text_index]

    def _validate_audio(self, audio_chunk):
        """
        Validate incoming audio data.
        """

        audio_data = audio_chunk.get("audio_data", b"")

        if not isinstance(audio_data, bytes):
            raise ValueError("audio_data must be bytes")

        if not audio_data:
            raise ValueError("Audio data cannot be empty")

        return audio_data

    def transcribe(self, audio_chunk: dict):
        """
        Backward-compatible normal transcription.

        Returns one finalized transcript event.
        """

        audio_data = self._validate_audio(audio_chunk)

        chunk_id = audio_chunk["chunk_id"]
        sequence = audio_chunk["sequence_number"]

        session_id = audio_chunk.get(
            "session_id", "default"
        )

        transcript_text = self._generate_text(
            audio_data
        )

        segment = TranscriptSegment(
            segment_id=f"segment-{chunk_id}",
            chunk_id=chunk_id,
            sequence_number=sequence,
            start_ms=audio_chunk["start_ms"],
            end_ms=audio_chunk["end_ms"],
            text=transcript_text,
            confidence=0.95,
            is_final=True,
            language="en-IN",
            session_id=session_id
        )

        event = TranscriptEvent(
            event_id=f"event-{chunk_id}",
            event_type="transcript",
            timestamp_ms=audio_chunk["end_ms"],
            segment=segment,
            session_id=session_id
        )

        return [event]

    def transcribe_lifecycle(self, audio_chunk: dict):
        """
        Generate interim, revision and finalized events.

        This method demonstrates the Week 3
        transcription lifecycle.
        """

        audio_data = self._validate_audio(
            audio_chunk
        )

        chunk_id = audio_chunk["chunk_id"]
        sequence = audio_chunk["sequence_number"]

        session_id = audio_chunk.get(
            "session_id", "default"
        )

        start_ms = audio_chunk["start_ms"]
        end_ms = audio_chunk["end_ms"]

        final_text = self._generate_text(
            audio_data
        )

        # Simulated initial prediction.
        interim_text = final_text.split(" ")[0]

        # Simulated improved prediction.
        revision_text = final_text

        events = []

        # Stage 1: Interim transcript.
        interim_segment = TranscriptSegment(
            segment_id=f"segment-{chunk_id}-interim",
            chunk_id=chunk_id,
            sequence_number=sequence,
            start_ms=start_ms,
            end_ms=end_ms,
            text=interim_text,
            confidence=0.65,
            is_final=False,
            language="en-IN",
            session_id=session_id
        )

        interim_event = TranscriptEvent(
            event_id=f"event-{chunk_id}-interim",
            event_type="transcript",
            timestamp_ms=end_ms,
            segment=interim_segment,
            session_id=session_id
        )

        events.append(interim_event)

        # Stage 2: Revised transcript.
        revision_segment = TranscriptSegment(
            segment_id=f"segment-{chunk_id}-revision",
            chunk_id=chunk_id,
            sequence_number=sequence,
            start_ms=start_ms,
            end_ms=end_ms,
            text=revision_text,
            confidence=0.85,
            is_final=False,
            language="en-IN",
            session_id=session_id
        )

        revision_event = TranscriptEvent(
            event_id=f"event-{chunk_id}-revision",
            event_type="revision",
            timestamp_ms=end_ms + 1,
            segment=revision_segment,
            session_id=session_id
        )

        events.append(revision_event)

        # Stage 3: Finalized transcript.
        final_segment = TranscriptSegment(
            segment_id=f"segment-{chunk_id}-final",
            chunk_id=chunk_id,
            sequence_number=sequence,
            start_ms=start_ms,
            end_ms=end_ms,
            text=final_text,
            confidence=0.98,
            is_final=True,
            language="en-IN",
            session_id=session_id
        )

        final_event = TranscriptEvent(
            event_id=f"event-{chunk_id}-final",
            event_type="finalized",
            timestamp_ms=end_ms + 2,
            segment=final_segment,
            session_id=session_id
        )

        events.append(final_event)

        return events