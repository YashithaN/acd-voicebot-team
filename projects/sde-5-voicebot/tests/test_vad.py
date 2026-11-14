
import pytest

from audio.vad import MockVAD, VADError


def test_speech_detected_after_minimum_duration():
    vad = MockVAD(threshold=0.5, min_speech_duration_ms=300)

    assert vad.process(0.8, 100) is False
    assert vad.process(0.9, 100) is False
    assert vad.process(0.8, 100) is True


def test_silence_does_not_detect_speech():
    vad = MockVAD(threshold=0.5, min_speech_duration_ms=300)

    assert vad.process(0.1, 100) is False
    assert vad.speech_duration_ms == 0


def test_noise_resets_speech_duration():
    vad = MockVAD(threshold=0.5, min_speech_duration_ms=300)

    vad.process(0.8, 200)
    assert vad.speech_duration_ms == 200

    vad.process(0.2, 100)
    assert vad.speech_duration_ms == 0


def test_speech_duration_accumulates():
    vad = MockVAD(threshold=0.5, min_speech_duration_ms=200)

    assert vad.process(0.7, 100) is False
    assert vad.process(0.7, 100) is True


def test_custom_threshold():
    vad = MockVAD(threshold=0.8, min_speech_duration_ms=100)

    assert vad.process(0.6, 100) is False
    assert vad.process(0.9, 100) is True


def test_invalid_threshold():
    with pytest.raises(VADError):
        MockVAD(threshold=1.5)


def test_invalid_minimum_duration():
    with pytest.raises(VADError):
        MockVAD(min_speech_duration_ms=0)


def test_invalid_audio_level():
    vad = MockVAD()

    with pytest.raises(VADError):
        vad.process(1.5, 100)


def test_invalid_audio_duration():
    vad = MockVAD()

    with pytest.raises(VADError):
        vad.process(0.8, 0)
