from speech_to_text.adapter import SpeechToTextAdapter
from speech_to_text.fake_transcriber import FakeTranscriber
from speech_to_text.schemas import TranscriptEvent, TranscriptSegment


def test_fake_transcriber_implements_adapter():
    provider = FakeTranscriber()
    assert isinstance(provider, SpeechToTextAdapter)


def test_provider_returns_list_of_events():
    provider = FakeTranscriber()

    audio_chunk = {
        "chunk_id": "contract-001",
        "sequence_number": 0,
        "start_ms": 0,
        "end_ms": 2000,
        "audio_data": b"synthetic contract audio"
    }

    events = provider.transcribe(audio_chunk)

    assert isinstance(events, list)
    assert len(events) > 0


def test_provider_returns_valid_transcript_event():
    provider = FakeTranscriber()

    audio_chunk = {
        "chunk_id": "contract-002",
        "sequence_number": 1,
        "start_ms": 2000,
        "end_ms": 4000,
        "audio_data": b"another synthetic audio"
    }

    events = provider.transcribe(audio_chunk)

    for event in events:
        assert isinstance(event, TranscriptEvent)
        assert event.event_type == "transcript"
        assert isinstance(event.segment, TranscriptSegment)
        assert event.segment.chunk_id == "contract-002"
        assert isinstance(event.segment.text, str)
        assert 0 <= event.segment.confidence <= 1
        assert isinstance(event.segment.is_final, bool)