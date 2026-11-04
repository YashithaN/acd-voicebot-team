
import unittest

from audio.schemas import AudioChunk, AudioFormat, AudioError


class TestAudioFormat(unittest.TestCase):

    def test_valid_audio_format(self):
        audio_format = AudioFormat(sample_rate=16000, channels=1)

        self.assertEqual(audio_format.sample_rate, 16000)
        self.assertEqual(audio_format.channels, 1)

    def test_invalid_sample_rate(self):
        with self.assertRaises(AudioError):
            AudioFormat(sample_rate=0, channels=1)

    def test_invalid_channel_count(self):
        with self.assertRaises(AudioError):
            AudioFormat(sample_rate=16000, channels=0)


class TestAudioChunk(unittest.TestCase):

    def setUp(self):
        self.audio_format = AudioFormat(
            sample_rate=16000,
            channels=1
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

    def test_invalid_timestamp(self):
        with self.assertRaises(AudioError):
            AudioChunk(
                data=b"\x01\x02",
                timestamp=-1,
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


if __name__ == "__main__":
    unittest.main()
