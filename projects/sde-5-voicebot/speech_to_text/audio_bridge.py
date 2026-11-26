from audio.schemas import AudioChunk
from speech_to_text.orchestrator import SpeechToTextOrchestrator


class AudioToSpeechBridge:
    """
    Connects W1 AudioChunk objects to the W2/W3
    Speech-to-Text orchestrator.

    Supports:
    - Audio format conversion
    - Session association
    - Out-of-order chunks
    - Missing chunk detection
    """

    def __init__(
        self,
        orchestrator: SpeechToTextOrchestrator,
        session_id="default"
    ):

        if not isinstance(session_id, str) or not session_id.strip():
            raise ValueError("Session ID cannot be empty")

        self.orchestrator = orchestrator
        self.session_id = session_id

        # Track received sequence IDs separately for each session.
        self.received_sequences = {}

    def convert_chunk(self, audio_chunk, session_id=None):
        """
        Convert W1 AudioChunk into the dictionary
        expected by the Speech-to-Text provider.
        """

        if not isinstance(audio_chunk, AudioChunk):
            raise TypeError("Expected an AudioChunk object")

        active_session = session_id or self.session_id

        if not isinstance(active_session, str) or not active_session.strip():
            raise ValueError("Session ID cannot be empty")

        audio_format = audio_chunk.audio_format

        bytes_per_second = (
            audio_format.sample_rate
            * audio_format.channels
            * audio_format.sample_width
        )

        start_ms = round(audio_chunk.timestamp * 1000)

        duration_ms = max(
            1,
            round(len(audio_chunk.data) / bytes_per_second * 1000)
        )

        end_ms = start_ms + duration_ms

        return {
            "chunk_id": (
                f"audio-{active_session}-{audio_chunk.sequence_id}"
            ),
            "sequence_number": audio_chunk.sequence_id,
            "start_ms": start_ms,
            "end_ms": end_ms,
            "audio_data": audio_chunk.data,
            "session_id": active_session
        }

    def process_chunk(self, audio_chunk, session_id=None):
        """
        Convert and send one W1 audio chunk
        to the Speech-to-Text orchestrator.
        """

        payload = self.convert_chunk(audio_chunk, session_id)

        active_session = payload["session_id"]

        if active_session not in self.received_sequences:
            self.received_sequences[active_session] = set()

        self.received_sequences[active_session].add(
            audio_chunk.sequence_id
        )

        return self.orchestrator.process_audio_chunk(payload)

    def process_stream(self, audio_chunks, session_id=None):
        """
        Process an iterable of W1 audio chunks.

        Chunks can arrive out of order. The transcript
        accumulator maintains transcript sequence order.
        """

        events = []

        for chunk in audio_chunks:
            chunk_events = self.process_chunk(chunk, session_id)
            events.extend(chunk_events)

        return events

    def get_received_sequence_ids(self, session_id=None):
        """
        Return received chunk sequence IDs in sorted order.
        """

        active_session = session_id or self.session_id

        return sorted(
            self.received_sequences.get(active_session, set())
        )

    def get_missing_sequence_ids(self, session_id=None):
        """
        Detect missing sequence IDs between zero
        and the highest received sequence ID.

        A missing ID may indicate a dropped audio chunk.
        """

        received = set(
            self.get_received_sequence_ids(session_id)
        )

        if not received:
            return []

        expected = set(range(max(received) + 1))

        return sorted(expected - received)