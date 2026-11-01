from audio.schemas import AudioChunk, AudioFormat, AudioError


class MockAudioSource:
    """
    Simulates a microphone using predefined audio bytes.

    The same input always produces the same chunks.
    No physical microphone or internet connection is required.
    """

    def __init__(
        self,
        audio_data: bytes,
        audio_format: AudioFormat,
        chunk_size: int = 8,
        start_timestamp: float = 0.0
    ):
        if not isinstance(audio_data, bytes) or not audio_data:
            raise AudioError("Mock audio data must be non-empty bytes.")

        if not isinstance(audio_format, AudioFormat):
            raise AudioError("A valid AudioFormat is required.")

        if not isinstance(chunk_size, int) or isinstance(chunk_size, bool) or chunk_size <= 0:
            raise AudioError("Chunk size must be a positive integer.")

        frame_size = audio_format.channels * audio_format.sample_width

        if len(audio_data) % frame_size != 0:
            raise AudioError("Audio data length must align with the audio frame size.")

        if chunk_size % frame_size != 0:
            raise AudioError("Chunk size must align with the audio frame size.")

        if not isinstance(start_timestamp, (int, float)) or isinstance(start_timestamp, bool):
            raise AudioError("Start timestamp must be a number.")

        if start_timestamp < 0:
            raise AudioError("Start timestamp cannot be negative.")

        self.audio_data = audio_data
        self.audio_format = audio_format
        self.chunk_size = chunk_size
        self.start_timestamp = float(start_timestamp)

    def stream(self):
        """Yield deterministic audio chunks with timestamps and sequence IDs."""

        frame_size = (
            self.audio_format.channels * self.audio_format.sample_width
        )

        bytes_per_second = (
            self.audio_format.sample_rate * frame_size
        )

        for sequence_id, start in enumerate(
            range(0, len(self.audio_data), self.chunk_size)
        ):
            chunk_data = self.audio_data[
                start:start + self.chunk_size
            ]

            timestamp = (
                self.start_timestamp + start / bytes_per_second
            )

            yield AudioChunk(
                data=chunk_data,
                timestamp=timestamp,
                sequence_id=sequence_id,
                audio_format=self.audio_format
            )
