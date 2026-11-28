
import pytest

from audio.events import SpeechEventType
from audio.pipeline import AudioEventPipeline, PipelineError
from audio.schemas import AudioChunk, AudioFormat
from audio.vad import MockVAD


def make_chunk(sequence_id):
    return AudioChunk(
        data=b"\x00\x00" * 160,
        timestamp=sequence_id * 0.01,
        sequence_id=sequence_id,
        audio_format=AudioFormat(sample_rate=16000, channels=1),
    )


def make_pipeline(min_duration=100):
    vad = MockVAD(
        threshold=0.5,
        min_speech_duration_ms=min_duration,
    )
    return AudioEventPipeline(
        vad=vad,
        session_id="session-1",
        correlation_id="correlation-1",
    )


def test_speech_start_event():
    pipeline = make_pipeline()

    pipeline.process_chunk(make_chunk(0), 0.8, 100)

    assert pipeline.speech_active is True
    assert pipeline.events[0].event_type == SpeechEventType.SPEECH_STARTED


def test_audio_chunk_event_contains_ids():
    pipeline = make_pipeline()

    events = pipeline.process_chunk(make_chunk(0), 0.8, 100)

    audio_event = next(
        event for event in events
        if event.event_type == SpeechEventType.AUDIO_CHUNK
    )

    assert audio_event.session_id == "session-1"
    assert audio_event.correlation_id == "correlation-1"
    assert audio_event.sequence_id == 0


def test_speech_start_precedes_audio_event():
    pipeline = make_pipeline()

    events = pipeline.process_chunk(make_chunk(0), 0.8, 100)

    assert [event.event_type for event in events] == [
        SpeechEventType.SPEECH_STARTED,
        SpeechEventType.AUDIO_CHUNK,
    ]


def test_silence_ends_speech():
    pipeline = make_pipeline()

    pipeline.process_chunk(make_chunk(0), 0.8, 100)
    events = pipeline.process_chunk(make_chunk(1), 0.1, 100)

    assert events[-1].event_type == SpeechEventType.SPEECH_ENDED
    assert pipeline.speech_active is False


def test_silence_without_speech_emits_no_events():
    pipeline = make_pipeline()

    events = pipeline.process_chunk(make_chunk(0), 0.1, 100)

    assert events == []


def test_short_noise_does_not_trigger_speech():
    pipeline = make_pipeline(min_duration=300)

    events = pipeline.process_chunk(make_chunk(0), 0.8, 100)

    assert events == []
    assert pipeline.speech_active is False


def test_speech_can_start_again_after_silence():
    pipeline = make_pipeline()

    pipeline.process_chunk(make_chunk(0), 0.8, 100)
    pipeline.process_chunk(make_chunk(1), 0.1, 100)
    events = pipeline.process_chunk(make_chunk(2), 0.8, 100)

    assert events[0].event_type == SpeechEventType.SPEECH_STARTED


def test_finish_ends_active_speech():
    pipeline = make_pipeline()

    pipeline.process_chunk(make_chunk(0), 0.8, 100)
    events = pipeline.finish()

    assert events[0].event_type == SpeechEventType.SPEECH_ENDED
    assert pipeline.speech_active is False


def test_out_of_order_chunk_is_rejected():
    pipeline = make_pipeline()

    pipeline.process_chunk(make_chunk(2), 0.8, 100)

    with pytest.raises(PipelineError):
        pipeline.process_chunk(make_chunk(1), 0.8, 100)


def test_sequence_gap_is_accepted():
    pipeline = make_pipeline()

    pipeline.process_chunk(make_chunk(0), 0.8, 100)
    events = pipeline.process_chunk(make_chunk(3), 0.8, 100)

    assert events[-1].sequence_id == 3


def test_events_keep_same_session_and_correlation_ids():
    pipeline = make_pipeline()

    pipeline.process_chunk(make_chunk(0), 0.8, 100)
    pipeline.process_chunk(make_chunk(1), 0.1, 100)

    for event in pipeline.events:
        assert event.session_id == "session-1"
        assert event.correlation_id == "correlation-1"
