from pathlib import Path

from audio.mock_source import MockAudioSource
from audio.schemas import AudioFormat

from speech_to_text.fake_transcriber import FakeTranscriber
from speech_to_text.orchestrator import SpeechToTextOrchestrator
from speech_to_text.preprocessing import preprocess_audio


def main():
    print("\n=== AcademiaAI Integrated Speech-to-Text Demo ===")

    # Step 1: Load sample audio
    audio_path = Path("fixtures/synthetic_audio/sample_audio.pcm")

    if not audio_path.exists():
        print("Error: Sample audio file not found!")
        return

    audio_data = audio_path.read_bytes()
    print("Audio loaded:", len(audio_data), "bytes")

    # Step 2: Define audio format
    audio_format = AudioFormat(
        sample_rate=16000,
        channels=1,
        sample_width=2
    )

    # Step 3: Create Week 1 MockAudioSource
    audio_source = MockAudioSource(
        audio_data=audio_data,
        audio_format=audio_format,
        chunk_size=6400
    )

    # Step 4: Create Week 2 speech-to-text components
    provider = FakeTranscriber()
    orchestrator = SpeechToTextOrchestrator(provider)

    print("\nAudio stream started...")

    # Step 5: Process each audio chunk
    for chunk in audio_source.stream():

        start_ms = round(chunk.timestamp * 1000)

        duration_ms = (
            len(chunk.data)
            / (
                chunk.audio_format.sample_rate
                * chunk.audio_format.channels
                * chunk.audio_format.sample_width
            )
        ) * 1000

        end_ms = start_ms + round(duration_ms)

        print(
            f"\nProcessing Chunk {chunk.sequence_id}"
            f" | Timestamp: {chunk.timestamp:.3f}s"
            f" | Size: {len(chunk.data)} bytes"
        )

        processed_audio = preprocess_audio(
            audio_data=chunk.data,
            source_sample_rate=chunk.audio_format.sample_rate,
            target_sample_rate=16000
        )

        # Convert Week 1 AudioChunk into Week 2 input format
        audio_chunk = {
            "chunk_id": f"chunk-{chunk.sequence_id + 1:03d}",
            "sequence_number": chunk.sequence_id,
            "start_ms": start_ms,
            "end_ms": end_ms,
            "audio_data": processed_audio
        }

        # Send audio to Week 2 orchestrator
        events = orchestrator.process_audio_chunk(audio_chunk)

        for event in events:
            if event.segment:
                print("Transcript:", event.segment.text)

    # Step 6: Display final transcript
    print("\n=== Final Transcript ===")
    print(orchestrator.get_transcript())

    print("\nIntegrated demo completed successfully!")


if __name__ == "__main__":
    main()