import time
import inspect
import threading

from concurrent.futures import (
    ThreadPoolExecutor,
    TimeoutError as FuturesTimeoutError
)


class SpeechToTextError(Exception):

    def __init__(self, message, error_code, retryable):
        super().__init__(message)
        self.error_code = error_code
        self.retryable = retryable


class TranscriptionCancelled(Exception):
    """Raised when transcription is cancelled."""


class QuotaExceededError(Exception):
    """Raised when provider quota is exhausted."""


class NetworkUnavailableError(Exception):
    """Raised when the provider network is unavailable."""


def normalize_error(error):

    if isinstance(error, SpeechToTextError):
        return error

    if isinstance(error, TranscriptionCancelled):
        return SpeechToTextError(
            "Transcription was cancelled",
            "CANCELLED",
            False
        )

    if isinstance(error, QuotaExceededError):
        return SpeechToTextError(
            "Speech recognition quota exceeded",
            "QUOTA_EXCEEDED",
            True
        )

    if isinstance(error, NetworkUnavailableError):
        return SpeechToTextError(
            "Speech recognition network unavailable",
            "NETWORK_ERROR",
            True
        )

    if isinstance(error, FuturesTimeoutError):
        return SpeechToTextError(
            "Speech recognition timed out",
            "TIMEOUT",
            True
        )

    if isinstance(error, ValueError):
        return SpeechToTextError(
            "Invalid audio input",
            "INVALID_INPUT",
            False
        )

    return SpeechToTextError(
        "Speech recognition provider failed",
        "PROVIDER_ERROR",
        True
    )


def _call_provider(provider, audio_chunk, cancellation_event):

    method = provider.transcribe
    parameters = inspect.signature(method).parameters

    if "cancellation_event" in parameters:
        return method(
            audio_chunk,
            cancellation_event=cancellation_event
        )

    if "cancel_event" in parameters:
        return method(
            audio_chunk,
            cancel_event=cancellation_event
        )

    return method(audio_chunk)


def transcribe_with_retry(
    provider,
    audio_chunk,
    timeout_seconds=5,
    max_retries=2,
    cancellation_event=None
):

    if timeout_seconds <= 0 or max_retries < 0:
        raise ValueError("Invalid timeout or retry configuration")

    if cancellation_event is None:
        cancellation_event = threading.Event()

    for attempt in range(max_retries + 1):

        if cancellation_event.is_set():
            raise normalize_error(TranscriptionCancelled())

        # Separate event for each attempt.
        attempt_cancellation = threading.Event()

        executor = ThreadPoolExecutor(max_workers=1)

        future = executor.submit(
            _call_provider,
            provider,
            audio_chunk,
            attempt_cancellation
        )

        deadline = time.monotonic() + timeout_seconds
        normalized = None

        try:

            while True:

                if cancellation_event.is_set():
                    attempt_cancellation.set()
                    future.cancel()

                    raise normalize_error(
                        TranscriptionCancelled()
                    )

                remaining = deadline - time.monotonic()

                if remaining <= 0:
                    attempt_cancellation.set()
                    future.cancel()

                    normalized = normalize_error(
                        FuturesTimeoutError()
                    )
                    break

                try:
                    result = future.result(
                        timeout=min(0.05, remaining)
                    )

                    if cancellation_event.is_set():
                        attempt_cancellation.set()

                        raise normalize_error(
                            TranscriptionCancelled()
                        )

                    executor.shutdown(wait=False)
                    return result

                except FuturesTimeoutError:
                    # Check cancellation and deadline again.
                    continue

        except SpeechToTextError:
            executor.shutdown(
                wait=False,
                cancel_futures=True
            )
            raise

        except Exception as error:

            attempt_cancellation.set()

            normalized = normalize_error(error)

        finally:

            # Never block the caller waiting for a
            # provider that may still be running.
            executor.shutdown(
                wait=False,
                cancel_futures=True
            )

        if cancellation_event.is_set():
            raise normalize_error(TranscriptionCancelled())

        if not normalized.retryable:
            raise normalized

        if attempt == max_retries:
            raise normalized

        # Wait between retries, while allowing cancellation.
        if cancellation_event.wait(0.1 * (attempt + 1)):
            raise normalize_error(TranscriptionCancelled())