
from collections import deque

from audio.schemas import AudioError, AudioChunk


class BufferError(AudioError):
    """Raised when an invalid buffer operation is attempted."""


class BoundedAudioBuffer:
    """
    A fixed-capacity audio buffer.

    When full, incoming chunks are rejected and the dropped-chunk
    counter is incremented.
    """

    def __init__(self, capacity=10):
        if (
            isinstance(capacity, bool)
            or not isinstance(capacity, int)
            or capacity <= 0
        ):
            raise BufferError("Buffer capacity must be a positive integer.")

        self.capacity = capacity
        self._buffer = deque()
        self.dropped_chunks = 0
        self.last_sequence_id = None
        self.sequence_gaps = 0
        self.late_chunks = 0

    def add(self, chunk):
        """Add a valid audio chunk if buffer capacity is available."""

        if not isinstance(chunk, AudioChunk):
            raise BufferError("Only AudioChunk objects can be added.")

        if (
            self.last_sequence_id is not None
            and chunk.sequence_id <= self.last_sequence_id
        ):
            self.late_chunks += 1
            self.dropped_chunks += 1
            return False

        if self.last_sequence_id is not None:
            expected_id = self.last_sequence_id + 1

            if chunk.sequence_id > expected_id:
                self.sequence_gaps += chunk.sequence_id - expected_id

        self.last_sequence_id = chunk.sequence_id

        if len(self._buffer) >= self.capacity:
            self.dropped_chunks += 1
            return False

        self._buffer.append(chunk)
        return True

    def get(self):
        """Remove and return the oldest chunk, or None if empty."""

        if not self._buffer:
            return None

        return self._buffer.popleft()

    def clear(self):
        """Remove all buffered chunks."""

        self._buffer.clear()

    def __len__(self):
        return len(self._buffer)

    @property
    def is_full(self):
        return len(self._buffer) >= self.capacity

    @property
    def is_empty(self):
        return len(self._buffer) == 0
