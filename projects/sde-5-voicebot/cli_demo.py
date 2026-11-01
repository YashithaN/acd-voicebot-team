
from audio.schemas import AudioFormat
from audio.mock_source import MockAudioSource


def main():
    # Create a simulated audio format
    audio_format = AudioFormat(
        sample_rate=16000,
        channels=1,
        sample_width=2
    )

    # Simulated microphone audio data
    sample_audio = bytes(range(64))

    # Create mock microphone
    microphone = MockAudioSource(
        audio_data=sample_audio,
        audio_format=audio_format,
        chunk_size=8
    )

    print("\n========== MOCK MICROPHONE DEMO ==========")
    print("Audio stream started...\n")

    for chunk in microphone.stream():
        print(f"Sequence ID : {chunk.sequence_id}")
        print(f"Timestamp   : {chunk.timestamp:.6f} seconds")
        print(f"Sample Rate : {chunk.audio_format.sample_rate} Hz")
        print(f"Channels    : {chunk.audio_format.channels}")
        print(f"Chunk Size  : {len(chunk.data)} bytes")
        print("------------------------------------------")

    print("\nAudio stream completed successfully!")


if __name__ == "__main__":
    main()
