import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError


class SpeechToTextError(Exception):

    def __init__(self, message, error_code, retryable):
        super().__init__(message)
        self.error_code = error_code
        self.retryable = retryable


def normalize_error(error):

    if isinstance(error, TimeoutError):
        return SpeechToTextError(
            "Speech recognition timed out",
            "TIMEOUT",
            True
        )

    if isinstance(error, ValueError):
        return SpeechToTextError(
            str(error),
            "INVALID_INPUT",
            False
        )

    return SpeechToTextError(
        str(error),
        "PROVIDER_ERROR",
        True
    )


def transcribe_with_retry(
    provider,
    audio_chunk,
    timeout_seconds=5,
    max_retries=2
):

    if timeout_seconds <= 0 or max_retries < 0:
        raise ValueError("Invalid timeout or retry configuration")

    for attempt in range(max_retries + 1):

        executor = ThreadPoolExecutor(max_workers=1)

        try:
            future = executor.submit(
                provider.transcribe,
                audio_chunk
            )

            result = future.result(timeout=timeout_seconds)

            executor.shutdown(wait=False)
            return result

        except Exception as error:

            future.cancel()
            executor.shutdown(wait=False, cancel_futures=True)

            normalized = normalize_error(error)

            if not normalized.retryable:
                raise normalized from error

            if attempt == max_retries:
                raise normalized from error

            time.sleep(0.1 * (attempt + 1))