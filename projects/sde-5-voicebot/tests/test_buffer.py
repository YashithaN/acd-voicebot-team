
import pytest

from audio.buffer import BoundedAudioBuffer, BufferError
from audio.schemas import AudioChunk, AudioFormat


@pytest.fixture
def audio_format():
    return AudioFormat(sample_rate=16000, channels=1, sample_width=2)


def make_chunk(sequence_id, audio_format, timestamp=None):
    if timestamp is None:
        timestamp = sequence_id * 0.01

    return AudioChunk(
        data=b"\x00\x00" * 4,
        timestamp=timestamp,
        sequence_id=sequence_id,
        audio_format=audio_format,
    )


def test_buffer_initially_empty():
    buffer = BoundedAudioBuffer(capacity=3)

    assert len(buffer) == 0
    assert buffer.is_empty is True
    assert buffer.is_full is False


def test_add_audio_chunk(audio_format):
    buffer = BoundedAudioBuffer(capacity=3)
    chunk = make_chunk(0, audio_format)

    result = buffer.add(chunk)

    assert result is True
    assert len(buffer) == 1


def test_get_oldest_chunk(audio_format):
    buffer = BoundedAudioBuffer(capacity=3)
    first = make_chunk(0, audio_format)
    second = make_chunk(1, audio_format)

    buffer.add(first)
    buffer.add(second)

    assert buffer.get() == first
    assert len(buffer) == 1


def test_buffer_overflow_drops_incoming_chunk(audio_format):
    buffer = BoundedAudioBuffer(capacity=2)

    assert buffer.add(make_chunk(0, audio_format)) is True
    assert buffer.add(make_chunk(1, audio_format)) is True
    assert buffer.add(make_chunk(2, audio_format)) is False

    assert buffer.is_full is True
    assert buffer.dropped_chunks == 1
    assert len(buffer) == 2


def test_buffer_clear(audio_format):
    buffer = BoundedAudioBuffer(capacity=3)

    buffer.add(make_chunk(0, audio_format))
    buffer.add(make_chunk(1, audio_format))
    buffer.clear()

    assert buffer.is_empty is True
    assert len(buffer) == 0


def test_get_from_empty_buffer():
    buffer = BoundedAudioBuffer()

    assert buffer.get() is None


def test_invalid_capacity():
    with pytest.raises(BufferError):
        BoundedAudioBuffer(capacity=0)


def test_invalid_chunk():
    buffer = BoundedAudioBuffer()

    with pytest.raises(BufferError):
        buffer.add(b"not an audio chunk")


def test_sequence_gap_counter(audio_format):
    buffer = BoundedAudioBuffer()

    buffer.add(make_chunk(0, audio_format))
    buffer.add(make_chunk(3, audio_format))

    assert buffer.sequence_gaps == 2


def test_late_chunk_counter(audio_format):
    buffer = BoundedAudioBuffer()

    buffer.add(make_chunk(2, audio_format))
    result = buffer.add(make_chunk(1, audio_format))

    assert result is False
    assert buffer.late_chunks == 1
    assert buffer.dropped_chunks == 1


def test_duplicate_chunk_counter(audio_format):
    buffer = BoundedAudioBuffer()

    buffer.add(make_chunk(0, audio_format))
    result = buffer.add(make_chunk(0, audio_format))

    assert result is False
    assert buffer.late_chunks == 1


def test_sequence_gap_does_not_accept_late_chunk(audio_format):
    buffer = BoundedAudioBuffer()

    buffer.add(make_chunk(0, audio_format))
    buffer.add(make_chunk(3, audio_format))

    result = buffer.add(make_chunk(2, audio_format))

    assert result is False
    assert buffer.late_chunks == 1
    assert buffer.sequence_gaps == 2
