import array
import sys


def preprocess_audio(
    audio_data: bytes,
    source_sample_rate: int,
    target_sample_rate: int = 16000,
    target_peak: float = 0.9
):
    """
    Resample and normalize mono PCM16 audio.

    Audio format: 16-bit signed PCM, little-endian.
    """

    if not isinstance(audio_data, bytes):
        raise ValueError("Audio data must be bytes")

    if not audio_data:
        raise ValueError("Audio data cannot be empty")

    if len(audio_data) % 2 != 0:
        raise ValueError("Invalid PCM16 audio data")

    if source_sample_rate <= 0 or target_sample_rate <= 0:
        raise ValueError("Sample rates must be positive")

    if not 0 < target_peak <= 1:
        raise ValueError("Target peak must be between 0 and 1")

    # Convert bytes into signed 16-bit samples
    samples = array.array("h")
    samples.frombytes(audio_data)

    if sys.byteorder == "big":
        samples.byteswap()

    # Resampling
    if source_sample_rate != target_sample_rate:

        new_length = max(
            1,
            round(len(samples) * target_sample_rate / source_sample_rate)
        )

        resampled = []

        for i in range(new_length):

            position = i * source_sample_rate / target_sample_rate

            left = int(position)
            right = min(left + 1, len(samples) - 1)

            fraction = position - left

            value = (
                samples[left] * (1 - fraction)
                + samples[right] * fraction
            )

            resampled.append(round(value))

        samples = array.array("h", resampled)

    # Audio normalization
    peak = max(abs(sample) for sample in samples)

    if peak > 0:

        desired_peak = int(32767 * target_peak)
        scale = desired_peak / peak

        normalized = [
            max(-32768, min(32767, round(sample * scale)))
            for sample in samples
        ]

        samples = array.array("h", normalized)

    if sys.byteorder == "big":
        samples.byteswap()

    return samples.tobytes()