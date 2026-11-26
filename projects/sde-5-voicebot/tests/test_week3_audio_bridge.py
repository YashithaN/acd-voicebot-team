import pytest

from audio.schemas import AudioFormat
from audio.mock_source import MockAudioSource

from speech_to_text.audio_bridge import AudioToSpeechBridge
from speech_to_text.orchestrator import SpeechToTextOrchestrator
from speech_to_text.fake_transcriber import FakeTranscriber


def create_bridge(session_id="bridge-session"):

    orchestrator = SpeechToTextOrchestrator(
        provider=FakeTranscriber()
    )

    return AudioToSpeechBridge(
        orchestrator=orchestrator,
        session_id=session_id
    )


def create_audio_source():

    audio_format = AudioFormat(
        sample_rate=16000,
        channels=1,
        sample_width=2
    )

    audio_data = bytes(range(48))

    return MockAudioSource(
        audio_data=audio_data,
        audio_format=audio_format,
        chunk_size=8
    )


def test_w1_audio_chunk_converts_to_stt_payload():

    bridge = create_bridge()

    source = create_audio_source()

    chunk = next(source.stream())

    payload = bridge.convert_chunk(chunk)

    assert payload["chunk_id"] == "audio-bridge-session-0"
    assert payload["sequence_number"] == 0
    assert payload["audio_data"] == chunk.data
    assert payload["session_id"] == "bridge-session"
    assert payload["start_ms"] == 0
    assert payload["end_ms"] >= payload["start_ms"]


def test_out_of_order_chunks_produce_ordered_transcript():

    bridge = create_bridge()

    source = create_audio_source()

    chunks = list(source.stream())

    # Simulate chunks arriving out of order.
    out_of_order_chunks = [
        chunks[2],
        chunks[0],
        chunks[1]
    ]

    bridge.process_stream(out_of_order_chunks)

    segments = bridge.orchestrator.get_segments(
        "bridge-session"
    )

    sequence_ids = [
        segment.sequence_number
        for segment in segments
    ]

    assert sequence_ids == [0, 1, 2]

    assert len(segments) == 3

    assert all(
        segment.session_id == "bridge-session"
        for segment in segments
    )


def test_missing_audio_chunk_is_detected():

    bridge = create_bridge()

    source = create_audio_source()

    chunks = list(source.stream())

    # Chunk 1 is intentionally missing.
    bridge.process_chunk(chunks[0])
    bridge.process_chunk(chunks[2])

    missing = bridge.get_missing_sequence_ids()

    assert missing == [1]


def test_all_audio_chunks_received_no_missing_chunks():

    bridge = create_bridge()

    source = create_audio_source()

    bridge.process_stream(source.stream())

    assert bridge.get_missing_sequence_ids() == []

    assert bridge.get_received_sequence_ids() == [0, 1, 2, 3, 4, 5]


def test_audio_chunks_keep_session_association():

    bridge = create_bridge("session-123")

    source = create_audio_source()

    chunk = next(source.stream())

    events = bridge.process_chunk(chunk)

    assert len(events) == 1

    assert events[0].session_id == "session-123"

    assert events[0].segment.session_id == "session-123"
def test_missing_chunks_are_isolated_between_sessions():

    bridge = create_bridge()

    source = create_audio_source()
    chunks = list(source.stream())

    # Session A receives chunks 0 and 2.
    bridge.process_chunk(chunks[0], session_id="session-A")
    bridge.process_chunk(chunks[2], session_id="session-A")

    # Session B receives chunks 0 and 1.
    bridge.process_chunk(chunks[0], session_id="session-B")
    bridge.process_chunk(chunks[1], session_id="session-B")

    assert bridge.get_missing_sequence_ids("session-A") == [1]
    assert bridge.get_missing_sequence_ids("session-B") == []
