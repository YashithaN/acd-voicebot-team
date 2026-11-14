
from abc import ABC, abstractmethod
import math

from audio.schemas import AudioError


class VADError(AudioError):
    """Raised when invalid VAD configuration or input is provided."""


class VoiceActivityDetector(ABC):
    """Interface for voice activity detection implementations."""

    @abstractmethod
    def process(self, audio_level, duration_ms):
        """Analyze an audio level and return whether speech is detected."""
        pass


class MockVAD(VoiceActivityDetector):
    """
    Deterministic mock VAD.

    Detects speech using a configurable audio-level threshold
    and minimum continuous speech duration.
    """

    def __init__(self, threshold=0.5, min_speech_duration_ms=300):
        if (
            isinstance(threshold, bool)
            or not isinstance(threshold, (int, float))
            or not math.isfinite(threshold)
            or not 0 <= threshold <= 1
        ):
            raise VADError("Threshold must be between 0 and 1.")

        if (
            isinstance(min_speech_duration_ms, bool)
            or not isinstance(min_speech_duration_ms, (int, float))
            or not math.isfinite(min_speech_duration_ms)
            or min_speech_duration_ms <= 0
        ):
            raise VADError("Minimum speech duration must be positive.")

        self.threshold = float(threshold)
        self.min_speech_duration_ms = min_speech_duration_ms
        self.speech_duration_ms = 0

    def process(self, audio_level, duration_ms):
        """Return True when sufficient continuous speech is detected."""

        if (
            isinstance(audio_level, bool)
            or not isinstance(audio_level, (int, float))
            or not math.isfinite(audio_level)
            or not 0 <= audio_level <= 1
        ):
            raise VADError("Audio level must be between 0 and 1.")

        if (
            isinstance(duration_ms, bool)
            or not isinstance(duration_ms, (int, float))
            or not math.isfinite(duration_ms)
            or duration_ms <= 0
        ):
            raise VADError("Audio duration must be positive.")

        if audio_level >= self.threshold:
            self.speech_duration_ms += duration_ms
        else:
            # Silence or low-level noise resets continuous speech duration.
            self.speech_duration_ms = 0

        return self.speech_duration_ms >= self.min_speech_duration_ms
