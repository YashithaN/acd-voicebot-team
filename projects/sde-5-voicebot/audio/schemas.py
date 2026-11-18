
from dataclasses import dataclass
import math


class AudioError(ValueError):
    """Raised when audio data or audio format is invalid."""


@dataclass(frozen=True)
class AudioFormat:
    """
    Describes the format of audio data.

    sample_rate: Number of samples per second (Hz).
    channels: Number of audio channels (1 = mono, 2 = stereo).
    sample_width: Bytes used for each audio sample.
    """

    sample_rate: int
    channels: int
    sample_width: int = 2

    def __post_init__(self):
        if not isinstance(self.sample_rate, int) or isinstance(self.sample_rate, bool):
            raise AudioError("Sample rate must be an integer.")

        if self.sample_rate <= 0:
            raise AudioError("Sample rate must be greater than zero.")

        if not isinstance(self.channels, int) or isinstance(self.channels, bool):
            raise AudioError("Channel count must be an integer.")

        if self.channels <= 0:
            raise AudioError("Channel count must be greater than zero.")

        if not isinstance(self.sample_width, int) or isinstance(self.sample_width, bool):
            raise AudioError("Sample width must be an integer.")

        if self.sample_width <= 0:
            raise AudioError("Sample width must be greater than zero.")


@dataclass(frozen=True)
class AudioChunk:
    """
    Represents one chunk of audio.

    data: Raw audio bytes.
    timestamp: Time when the chunk was captured (seconds).
    sequence_id: Increasing identifier for each chunk.
    audio_format: Format of the audio data.
    """

    data: bytes
    timestamp: float
    sequence_id: int
    audio_format: AudioFormat

    def __post_init__(self):
        if not isinstance(self.data, bytes):
            raise AudioError("Audio data must be bytes.")

        if not self.data:
            raise AudioError("Audio chunk cannot be empty.")

        if not isinstance(self.timestamp, (int, float)) or isinstance(self.timestamp, bool):
            raise AudioError("Timestamp must be a number.")

        if not math.isfinite(self.timestamp) or self.timestamp < 0:
            raise AudioError("Timestamp must be finite and non-negative.")

        if not isinstance(self.sequence_id, int) or isinstance(self.sequence_id, bool):
            raise AudioError("Sequence ID must be an integer.")

        if self.sequence_id < 0:
            raise AudioError("Sequence ID cannot be negative.")

        if not isinstance(self.audio_format, AudioFormat):
            raise AudioError("A valid AudioFormat is required.")