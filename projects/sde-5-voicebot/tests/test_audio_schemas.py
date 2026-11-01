import math
import unittest

from audio.schemas import AudioChunk, AudioFormat, AudioError


class TestAudioFormat(unittest.TestCase):

    def test_valid_audio_format(self):
        audio_format = AudioFormat(sample_rate=16000, channels=1, sample_width=2)

        self.assertEqual(audio_format.sample_rate, 16000)
        self.assertEqual(audio_format.channels, 1)
        self.assertEqual(audio_format.sample_width, 2)
        self.assertEqual(audio_format.frame_size, 2)

    def test_invalid_sample_rate(self):
        with self.assertRaises(AudioError):
            AudioFormat(sample_rate=0, channels=1)

    def test_invalid_sample_rate_type(self):
        with self.assertRaises(AudioError):
            AudioFormat(sample_rate=True, channels=1)
        with self.assertRaises(AudioError):
            AudioFormat(sample_rate="16000", channels=1)

    def test_invalid_channel_count(self):
        with self.assertRaises(AudioError):
            AudioFormat(sample_rate=16000, channels=0)

    def test_invalid_channel_count_type(self):
        with self.assertRaises(AudioError):
            AudioFormat(sample_rate=16000, channels=False)
        with self.assertRaises(AudioError):
            AudioFormat(sample_rate=16000, channels="mono")

    def test_invalid_sample_width(self):
        with self.assertRaises(AudioError):
            AudioFormat(sample_rate=16000, channels=1, sample_width=0)
        with self.assertRaises(AudioError):
            AudioFormat(sample_rate=16000, channels=1, sample_width="2")


class TestAudioChunk(unittest.TestCase):

    def setUp(self):
        self.audio_format = AudioFormat(
            sample_rate=16000,
            channels=1,
            sample_width=2
        )

    def test_valid_audio_chunk(self):
        chunk = AudioChunk(
            data=b"\x01\x02\x03\x04",
            timestamp=1.5,
            sequence_id=1,
            audio_format=self.audio_format
        )

        self.assertEqual(chunk.sequence_id, 1)
        self.assertEqual(chunk.timestamp, 1.5)
        self.assertEqual(chunk.data, b"\x01\x02\x03\x04")
        self.assertEqual(chunk.audio_format, self.audio_format)

    def test_empty_audio_chunk(self):
        with self.assertRaises(AudioError):
            AudioChunk(
                data=b"",
                timestamp=1.5,
                sequence_id=1,
                audio_format=self.audio_format
            )

    def test_invalid_audio_data(self):
        with self.assertRaises(AudioError):
            AudioChunk(
                data="not bytes",
                timestamp=1.5,
                sequence_id=1,
                audio_format=self.audio_format
            )

    def test_corrupt_unaligned_audio_chunk(self):
        # Frame size is 2 bytes (1 channel * 2 bytes sample_width).
        # An odd length (3 bytes) is unaligned/corrupt.
        with self.assertRaises(AudioError) as ctx:
            AudioChunk(
                data=b"\x01\x02\x03",
                timestamp=1.5,
                sequence_id=1,
                audio_format=self.audio_format
            )
        self.assertIn("multiple of frame size", str(ctx.exception))

    def test_corrupt_stereo_unaligned_chunk(self):
        # Stereo format: 2 channels * 2 bytes = 4 bytes per frame.
        stereo_format = AudioFormat(sample_rate=44100, channels=2, sample_width=2)
        # 6 bytes is not a multiple of 4 bytes -> corrupt frame.
        with self.assertRaises(AudioError):
            AudioChunk(
                data=b"\x01\x02\x03\x04\x05\x06",
                timestamp=0.0,
                sequence_id=0,
                audio_format=stereo_format
            )

    def test_invalid_timestamp(self):
        with self.assertRaises(AudioError):
            AudioChunk(
                data=b"\x01\x02",
                timestamp=-1,
                sequence_id=1,
                audio_format=self.audio_format
            )

    def test_corrupt_non_finite_timestamp(self):
        with self.assertRaises(AudioError):
            AudioChunk(
                data=b"\x01\x02",
                timestamp=float("nan"),
                sequence_id=1,
                audio_format=self.audio_format
            )
        with self.assertRaises(AudioError):
            AudioChunk(
                data=b"\x01\x02",
                timestamp=float("inf"),
                sequence_id=1,
                audio_format=self.audio_format
            )

    def test_invalid_sequence_id(self):
        with self.assertRaises(AudioError):
            AudioChunk(
                data=b"\x01\x02",
                timestamp=1.5,
                sequence_id=-1,
                audio_format=self.audio_format
            )
        with self.assertRaises(AudioError):
            AudioChunk(
                data=b"\x01\x02",
                timestamp=1.5,
                sequence_id=True,
                audio_format=self.audio_format
            )

    def test_invalid_audio_format_in_chunk(self):
        with self.assertRaises(AudioError):
            AudioChunk(
                data=b"\x01\x02",
                timestamp=1.5,
                sequence_id=1,
                audio_format=None
            )


if __name__ == "__main__":
    unittest.main()
