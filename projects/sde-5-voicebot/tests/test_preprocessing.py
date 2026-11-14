import array
import pytest

from speech_to_text.preprocessing import preprocess_audio


def create_audio(samples):

    audio = array.array("h", samples)

    return audio.tobytes()


def test_audio_resampling():

    audio = create_audio([1000] * 8000)

    result = preprocess_audio(
        audio,
        source_sample_rate=8000,
        target_sample_rate=16000
    )

    output = array.array("h")
    output.frombytes(result)

    assert len(output) == 16000


def test_audio_normalization():

    audio = create_audio([1000, 2000, 3000, 4000])

    result = preprocess_audio(
        audio,
        source_sample_rate=16000
    )

    output = array.array("h")
    output.frombytes(result)

    assert max(abs(x) for x in output) >= 29490


def test_empty_audio_rejected():

    with pytest.raises(ValueError):

        preprocess_audio(
            b"",
            source_sample_rate=16000
        )


def test_invalid_sample_rate_rejected():

    audio = create_audio([1000, 2000])

    with pytest.raises(ValueError):

        preprocess_audio(
            audio,
            source_sample_rate=0
        )


def test_invalid_audio_format_rejected():

    with pytest.raises(ValueError):

        preprocess_audio(
            b"123",
            source_sample_rate=16000
        )