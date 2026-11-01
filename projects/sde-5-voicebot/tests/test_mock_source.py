import unittest

from audio.schemas import AudioFormat, AudioError
from audio.mock_source import MockAudioSource


class TestMockAudioSource(unittest.TestCase):

    def setUp(self):
        self.audio_format = AudioFormat(
            sample_rate=16000,
            channels=1,
            sample_width=2
        )

        self.audio_data = bytes(range(32))

    def test_mock_source_creates_chunks(self):
        source = MockAudioSource(
            self.audio_data,
            self.audio_format,
            chunk_size=8
        )

        chunks = list(source.stream())

        self.assertEqual(len(chunks), 4)

    def test_sequence_ids_increase(self):
        source = MockAudioSource(
            self.audio_data,
            self.audio_format,
            chunk_size=8
        )

        chunks = list(source.stream())

        self.assertEqual(
            [chunk.sequence_id for chunk in chunks],
            [0, 1, 2, 3]
        )

    def test_every_chunk_has_timestamp(self):
        source = MockAudioSource(
            self.audio_data,
            self.audio_format,
            chunk_size=8
        )

        chunks = list(source.stream())

        self.assertTrue(all(chunk.timestamp >= 0 for chunk in chunks))

    def test_output_is_deterministic(self):
        source1 = MockAudioSource(
            self.audio_data, self.audio_format, chunk_size=8
        )

        source2 = MockAudioSource(
            self.audio_data, self.audio_format, chunk_size=8
        )

        chunks1 = list(source1.stream())
        chunks2 = list(source2.stream())

        self.assertEqual(chunks1, chunks2)

    def test_invalid_empty_audio(self):
        with self.assertRaises(AudioError):
            MockAudioSource(
                b"",
                self.audio_format
            )

    def test_corrupt_unaligned_audio_data(self):
        # 31 bytes is not divisible by 2-byte frame size -> unaligned/corrupt
        corrupt_data = bytes(range(31))
        with self.assertRaises(AudioError):
            MockAudioSource(
                corrupt_data,
                self.audio_format,
                chunk_size=8
            )

    def test_invalid_chunk_size(self):
        with self.assertRaises(AudioError):
            MockAudioSource(
                self.audio_data,
                self.audio_format,
                chunk_size=0
            )

    def test_corrupt_unaligned_chunk_size(self):
        # Chunk size 3 is not aligned with 2-byte frame size
        with self.assertRaises(AudioError):
            MockAudioSource(
                self.audio_data,
                self.audio_format,
                chunk_size=3
            )

    def test_invalid_start_timestamp(self):
        with self.assertRaises(AudioError):
            MockAudioSource(
                self.audio_data,
                self.audio_format,
                chunk_size=8,
                start_timestamp=-0.5
            )
        with self.assertRaises(AudioError):
            MockAudioSource(
                self.audio_data,
                self.audio_format,
                chunk_size=8,
                start_timestamp="invalid"
            )

    def test_invalid_audio_format(self):
        with self.assertRaises(AudioError):
            MockAudioSource(
                self.audio_data,
                audio_format=None,
                chunk_size=8
            )


if __name__ == "__main__":
    unittest.main()
