import pytest

from speech_to_text.error_handler import (
    SpeechToTextError,
    normalize_error,
    transcribe_with_retry
)


class SuccessfulProvider:

    def __init__(self):
        self.calls = 0

    def transcribe(self, audio_chunk):
        self.calls += 1
        return ["Transcript generated"]


class FailingProvider:

    def transcribe(self, audio_chunk):
        raise RuntimeError("Provider unavailable")


class InvalidProvider:

    def transcribe(self, audio_chunk):
        raise ValueError("Invalid audio data")


def test_successful_transcription():

    provider = SuccessfulProvider()

    result = transcribe_with_retry(
        provider,
        {"audio_data": b"test"}
    )

    assert result == ["Transcript generated"]


def test_bounded_retries():

    provider = FailingProvider()

    with pytest.raises(SpeechToTextError) as error:

        transcribe_with_retry(
            provider,
            {"audio_data": b"test"},
            max_retries=2
        )

    assert error.value.error_code == "PROVIDER_ERROR"


def test_invalid_input_is_not_retried():

    provider = InvalidProvider()

    with pytest.raises(SpeechToTextError) as error:

        transcribe_with_retry(
            provider,
            {"audio_data": b""},
            max_retries=2
        )

    assert error.value.error_code == "INVALID_INPUT"
    assert error.value.retryable is False


def test_error_normalization():

    error = normalize_error(RuntimeError("Something failed"))

    assert error.error_code == "PROVIDER_ERROR"
    assert error.retryable is True