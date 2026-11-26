
import pytest

from audio.events import (
    SpeechEvent,
    SpeechEventError,
    SpeechEventType,
)
from audio.schemas import AudioChunk, AudioFormat


def make_chunk(sequence_id=1):
    return AudioChunk(
        data=b"\x00\x00" * 160,
        timestamp=1.0,
        sequence_id=sequence_id,
        audio_format=AudioFormat(sample_rate=16000, channels=1),
    )


def test_speech_started_event():
    event = SpeechEvent(
        event_type=SpeechEventType.SPEECH_STARTED,
        session_id="session-1",
        correlation_id="corr-1",
        timestamp_ms=1000,
    )

    assert event.event_type == SpeechEventType.SPEECH_STARTED
    assert event.session_id == "session-1"


def test_speech_ended_event():
    event = SpeechEvent(
        event_type=SpeechEventType.SPEECH_ENDED,
        session_id="session-1",
        correlation_id="corr-1",
        timestamp_ms=2000,
    )

    assert event.event_type == SpeechEventType.SPEECH_ENDED


def test_audio_chunk_event():
    chunk = make_chunk()

    event = SpeechEvent(
        event_type=SpeechEventType.AUDIO_CHUNK,
        session_id="session-1",
        correlation_id="corr-1",
        timestamp_ms=1000,
        sequence_id=chunk.sequence_id,
        audio_chunk=chunk,
    )

    assert event.audio_chunk == chunk
    assert event.sequence_id == 1


def test_empty_session_id_rejected():
    with pytest.raises(SpeechEventError):
        SpeechEvent(
            event_type=SpeechEventType.SPEECH_STARTED,
            session_id="",
            correlation_id="corr-1",
            timestamp_ms=1000,
        )


def test_empty_correlation_id_rejected():
    with pytest.raises(SpeechEventError):
        SpeechEvent(
            event_type=SpeechEventType.SPEECH_STARTED,
            session_id="session-1",
            correlation_id="",
            timestamp_ms=1000,
        )


def test_negative_timestamp_rejected():
    with pytest.raises(SpeechEventError):
        SpeechEvent(
            event_type=SpeechEventType.SPEECH_STARTED,
            session_id="session-1",
            correlation_id="corr-1",
            timestamp_ms=-1,
        )


def test_audio_event_requires_chunk():
    with pytest.raises(SpeechEventError):
        SpeechEvent(
            event_type=SpeechEventType.AUDIO_CHUNK,
            session_id="session-1",
            correlation_id="corr-1",
            timestamp_ms=1000,
        )


def test_audio_sequence_must_match_chunk():
    chunk = make_chunk(sequence_id=2)

    with pytest.raises(SpeechEventError):
        SpeechEvent(
            event_type=SpeechEventType.AUDIO_CHUNK,
            session_id="session-1",
            correlation_id="corr-1",
            timestamp_ms=1000,
            sequence_id=3,
            audio_chunk=chunk,
        )


def test_speech_boundary_cannot_contain_audio():
    chunk = make_chunk()

    with pytest.raises(SpeechEventError):
        SpeechEvent(
            event_type=SpeechEventType.SPEECH_STARTED,
            session_id="session-1",
            correlation_id="corr-1",
            timestamp_ms=1000,
            sequence_id=1,
            audio_chunk=chunk,
        )