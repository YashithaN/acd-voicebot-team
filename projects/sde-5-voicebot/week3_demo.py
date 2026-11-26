
"""
Week 3 demo: speech events, audio pipeline and mock transcription handoff.

Uses only mock audio data. No real microphone or external API is required.
"""

import time

from audio.events import SpeechEventType
from audio.pipeline import AudioEventPipeline
from audio.schemas import AudioChunk, AudioFormat
from audio.vad import MockVAD


class MockTranscriptionReceiver:
    """Receives audio events as a stand-in for the team's transcription module."""

    def __init__(self):
        self.received_chunks = []

    def receive(self, event):
        if event.event_type == SpeechEventType.AUDIO_CHUNK:
            self.received_chunks.append(event.audio_chunk)
            print(
                f"[TRANSCRIPTION] Received audio chunk "
                f"#{event.sequence_id}"
            )


def main():
    print("=" * 55)
    print("WEEK 3 - SPEECH EVENT & TRANSCRIPTION INTEGRATION DEMO")
    print("=" * 55)

    audio_format = AudioFormat(
        sample_rate=16000,
        channels=1,
        sample_width=2,
    )

    vad = MockVAD(
        threshold=0.5,
        min_speech_duration_ms=300,
    )

    pipeline = AudioEventPipeline(
        vad=vad,
        session_id="demo-session-001",
        correlation_id="demo-correlation-001",
    )

    transcription = MockTranscriptionReceiver()

    # Deterministic mock audio levels: speech, then silence.
    mock_audio = [
        (1, 0.8, 300),
        (2, 0.9, 300),
        (3, 0.85, 300),
        (4, 0.1, 300),
    ]

    for sequence_id, audio_level, duration_ms in mock_audio:
        chunk = AudioChunk(
            data=b"\x00\x01" * 160,
            timestamp=time.time(),
            sequence_id=sequence_id,
            audio_format=audio_format,
        )

        print(f"\n[CAPTURE] Processing chunk #{sequence_id}")

        events = pipeline.process_chunk(
            chunk=chunk,
            audio_level=audio_level,
            duration_ms=duration_ms,
        )

        for event in events:
            print(
                f"[EVENT] {event.event_type.value} | "
                f"Session: {event.session_id} | "
                f"Correlation: {event.correlation_id}"
            )

            transcription.receive(event)

    # Close any speech segment still active.
    for event in pipeline.finish():
        print(f"[EVENT] {event.event_type.value}")

    print("\n" + "=" * 55)
    print("DEMO SUMMARY")
    print("=" * 55)
    print(f"Total audio chunks sent to transcription: "
          f"{len(transcription.received_chunks)}")
    print(f"Total events generated: {len(pipeline.events)}")
    print("Demo completed successfully.")


if __name__ == "__main__":
    main()
