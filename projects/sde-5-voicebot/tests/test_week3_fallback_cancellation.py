import threading
import pytest

from concurrent.futures import ThreadPoolExecutor

from speech_to_text.orchestrator import SpeechToTextOrchestrator

from speech_to_text.error_handler import (
    QuotaExceededError,
    NetworkUnavailableError,
    TranscriptionCancelled
)


class QuotaFailureProvider:

    def transcribe(self, audio_chunk):
        raise QuotaExceededError("Private quota details")


class NetworkFailureProvider:

    def transcribe(self, audio_chunk):
        raise NetworkUnavailableError("Private network details")


class CancellableProvider:

    def __init__(self):
        self.started = threading.Event()

    def transcribe(self, audio_chunk, cancellation_event=None):

        self.started.set()

        while not cancellation_event.wait(0.01):
            pass

        raise TranscriptionCancelled()


def create_audio_chunk(chunk_id):

    return {
        "chunk_id": chunk_id,
        "sequence_number": 0,
        "start_ms": 0,
        "end_ms": 2000,
        "audio_data": b"synthetic audio data",
        "session_id": "week3-session"
    }


@pytest.mark.parametrize(
    "provider_class",
    [
        QuotaFailureProvider,
        NetworkFailureProvider
    ]
)
def test_provider_failure_uses_mock_fallback(provider_class):

    provider = provider_class()

    orchestrator = SpeechToTextOrchestrator(provider)

    events = orchestrator.process_audio_chunk(
        create_audio_chunk("fallback-test")
    )

    assert orchestrator.fallback_used is True
    assert orchestrator.last_provider_used == "mock"

    assert len(events) == 1
    assert events[0].event_type == "transcript"

    assert events[0].session_id == "week3-session"

    assert orchestrator.get_transcript(
        "week3-session"
    ) != ""


def test_cancellation_stops_cooperative_provider():

    provider = CancellableProvider()

    orchestrator = SpeechToTextOrchestrator(provider)

    chunk = create_audio_chunk("cancel-test")

    with ThreadPoolExecutor(max_workers=1) as executor:

        future = executor.submit(
            orchestrator.process_audio_chunk,
            chunk
        )

        assert provider.started.wait(timeout=2)

        cancelled = orchestrator.cancel_transcription(
            "cancel-test",
            "week3-session"
        )

        assert cancelled is True

        events = future.result(timeout=3)

    assert len(events) == 1

    assert events[0].event_type == "error"

    assert events[0].error_code == "CANCELLED"

    assert orchestrator.fallback_used is False

    assert orchestrator.get_transcript(
        "week3-session"
    ) == ""


def test_cancellation_of_unknown_chunk_returns_false():

    orchestrator = SpeechToTextOrchestrator(
        QuotaFailureProvider()
    )

    result = orchestrator.cancel_transcription(
        "unknown-chunk",
        "week3-session"
    )

    assert result is False