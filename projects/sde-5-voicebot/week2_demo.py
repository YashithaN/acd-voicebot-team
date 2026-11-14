
from audio.device import MockAudioDevice, PermissionState
from audio.lifecycle import AudioLifecycle
from audio.buffer import BoundedAudioBuffer
from audio.schemas import AudioFormat
from audio.mock_source import MockAudioSource
from audio.vad import MockVAD


def main():
    print("=" * 50)
    print("       SDE-5 VOICEBOT - WEEK 2 DEMO")
    print("=" * 50)

    # 1. Device selection and permission
    print("\n[1] AUDIO DEVICE")

    device = MockAudioDevice(
        permission_state=PermissionState.GRANTED
    )

    print("Available devices:", device.list_devices())

    # 2. Initialize bounded buffer and lifecycle
    buffer = BoundedAudioBuffer(capacity=3)

    lifecycle = AudioLifecycle(
        device=device,
        device_name="Mock Microphone",
        buffer=buffer
    )

    lifecycle.start()
    print("Device selected:", device.selected_device)
    print("Permission:", device.permission_state.value)
    print("Audio state:", lifecycle.state.value)

    # 3. Generate deterministic mock audio
    print("\n[2] MOCK AUDIO STREAM")

    audio_format = AudioFormat(
        sample_rate=16000,
        channels=1,
        sample_width=2
    )

    audio_data = b"\x01\x00" * 40

    source = MockAudioSource(
        audio_data=audio_data,
        audio_format=audio_format,
        chunk_size=8
    )

    chunks = list(source.stream())
    print("Generated chunks:", len(chunks))

    # 4. Bounded buffer and backpressure
    print("\n[3] BOUNDED BUFFER")

    for chunk in chunks:
        accepted = buffer.add(chunk)
        print(
            f"Chunk {chunk.sequence_id}:",
            "Accepted" if accepted else "Dropped (buffer full)"
        )

    print("Buffer size:", len(buffer))
    print("Dropped chunks:", buffer.dropped_chunks)

    # 5. Voice Activity Detection
    print("\n[4] VOICE ACTIVITY DETECTION")

    vad = MockVAD(
        threshold=0.5,
        min_speech_duration_ms=300
    )

    speech_detected = vad.process(
        audio_level=0.8,
        duration_ms=300
    )

    print("Speech detected:", speech_detected)

    # 6. Lifecycle controls
    print("\n[5] LIFECYCLE CONTROLS")

    lifecycle.pause()
    print("Paused:", lifecycle.state.value)

    lifecycle.resume()
    print("Resumed:", lifecycle.state.value)

    lifecycle.stop()
    print("Stopped:", lifecycle.state.value)
    print("Buffer after stop:", len(buffer))

    print("\n" + "=" * 50)
    print("          WEEK 2 DEMO COMPLETED")
    print("=" * 50)


if __name__ == "__main__":
    main()
