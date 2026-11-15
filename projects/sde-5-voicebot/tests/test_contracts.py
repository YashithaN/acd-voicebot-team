import pytest

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


def create_valid_segment(**overrides):
    data = {
        "segment_id": "segment-001",
        "chunk_id": "chunk-001",
        "sequence_number": 0,
        "start_ms": 100,
        "end_ms": 500,
        "text": "Hello world",
        "confidence": 0.95,
        "is_final": True,
        "language": "en-IN"
    }

    data.update(overrides)
    return data


@pytest.mark.parametrize(
    "field",
    ["segment_id", "chunk_id"]
)
def test_empty_segment_ids_are_rejected(field):
    data = create_valid_segment(**{field: ""})

    with pytest.raises(ValueError, match="cannot be empty"):
        TranscriptSegment(**data)


def test_empty_event_id_is_rejected():
    with pytest.raises(ValueError, match="Event ID cannot be empty"):
        TranscriptEvent(
            event_id="",
            event_type="error",
            timestamp_ms=100,
            error_code="TEST_ERROR",
            message="Test error",
            retryable=False
        )


@pytest.mark.parametrize(
    "field",
    ["start_ms", "end_ms"]
)
def test_negative_segment_timestamps_are_rejected(field):
    data = create_valid_segment(**{field: -1})

    with pytest.raises(ValueError):
        TranscriptSegment(**data)


def test_end_timestamp_before_start_is_rejected():
    data = create_valid_segment(
        start_ms=500,
        end_ms=200
    )

    with pytest.raises(
        ValueError,
        match="End timestamp cannot be before start"
    ):
        TranscriptSegment(**data)


def test_negative_event_timestamp_is_rejected():
    with pytest.raises(
        ValueError,
        match="Invalid event timestamp"
    ):
        TranscriptEvent(
            event_id="event-001",
            event_type="error",
            timestamp_ms=-1,
            error_code="TEST_ERROR",
            message="Test error",
            retryable=False
        )


@pytest.mark.parametrize(
    "confidence",
    [-0.1, 1.1]
)
def test_invalid_confidence_is_rejected(confidence):
    data = create_valid_segment(confidence=confidence)

    with pytest.raises(
        ValueError,
        match="Confidence must be between 0 and 1"
    ):
        TranscriptSegment(**data)


@pytest.mark.parametrize(
    "is_final",
    ["True", 1, None]
)
def test_non_boolean_is_final_is_rejected(is_final):
    data = create_valid_segment(is_final=is_final)

    with pytest.raises(
        ValueError,
        match="is_final must be True or False"
    ):
        TranscriptSegment(**data)


def test_fake_transcriber_is_deterministic():
    provider = FakeTranscriber()

    audio_chunk = {
        "chunk_id": "deterministic-001",
        "sequence_number": 1,
        "start_ms": 0,
        "end_ms": 2000,
        "audio_data": b"same synthetic audio input"
    }

    first_result = provider.transcribe(audio_chunk)
    second_result = provider.transcribe(audio_chunk)

    assert first_result == second_result


def test_error_event_requires_normalized_fields():
    with pytest.raises(ValueError):
        TranscriptEvent(
            event_id="error-001",
            event_type="error",
            timestamp_ms=100
        )


def test_error_event_contains_normalized_fields():
    event = TranscriptEvent(
        event_id="error-002",
        event_type="error",
        timestamp_ms=100,
        error_code="TIMEOUT",
        message="Speech recognition timed out",
        retryable=True
    )

    assert event.error_code == "TIMEOUT"
    assert event.message == "Speech recognition timed out"
    assert event.retryable is True


def test_transcript_event_requires_segment_only():
    with pytest.raises(ValueError):
        TranscriptEvent(
            event_id="event-002",
            event_type="transcript",
            timestamp_ms=100
        )