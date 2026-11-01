from dataclasses import dataclass
import math


class AudioError(ValueError):
    """Raised when audio data or audio format is invalid."""


@dataclass(frozen=True)
class AudioFormat:
    """
    Describes the format of audio data.

    sample_rate: Number of samples per second in Hz (Constraint: positive integer).
    channels: Number of audio channels, 1 = mono, 2 = stereo (Constraint: positive integer).
    sample_width: Bytes used for each audio sample (Constraint: positive integer, default: 2).
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

    @property
    def frame_size(self) -> int:
        """Size of one audio frame in bytes (channels * sample_width)."""
        return self.channels * self.sample_width


@dataclass(frozen=True)
class AudioChunk:
    """
    Represents one chunk of audio.

    data: Raw audio bytes (Constraint: non-empty bytes, length multiple of frame size).
    timestamp: Time when the chunk was captured in seconds (Constraint: finite, non-negative number).
    sequence_id: Monotonically increasing identifier for chunk (Constraint: non-negative integer).
    audio_format: Format specifications of the audio data (Constraint: valid AudioFormat).
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

        frame_size = self.audio_format.channels * self.audio_format.sample_width
        if len(self.data) % frame_size != 0:
            raise AudioError(
                f"Audio chunk data length ({len(self.data)} bytes) must be a multiple of frame size ({frame_size} bytes)."
            )
