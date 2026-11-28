
# SDE 5 Voice Bot — Audio Pipeline: Weeks 1, 2 & 3

**Team:** SDE 5  
**Engineer:** Yashitha N  
**Project:** Academia AI Voice Bot  
**Workstream:** W1 – Audio and VAD  
**Duration:** Week 1 to Week 3 (Day 1–Day 21)

**Week 1 Branch:** `feature/yashitha`  
**Week 2 Branch:** `feature/yashitha-w2-audio-lifecycle`  
**Week 3 Branch:** `feature/yashitha-w3-speech-integration`

---

## 1. Project Overview

This module provides the audio processing foundation for the Academia AI Voice Bot.

It implements typed audio schemas, deterministic mock audio input, device selection and permissions, audio lifecycle management, Voice Activity Detection (VAD), bounded audio buffering, speech event generation, device-loss recovery, and a mock transcription handoff.

The implementation builds incrementally across three weeks while reusing existing audio schemas and interfaces.

### Week 1 — Audio and VAD Foundation

- Typed audio schemas using immutable dataclasses.
- Deterministic mock audio source.
- Frame-aligned audio chunks.
- Timestamp and sequence ID generation.
- CLI demonstration.
- Unit tests for valid and invalid audio data.

### Week 2 — Device, Lifecycle, VAD and Buffer

- Mock audio device interface.
- Device discovery and selection.
- Permission handling.
- Audio lifecycle management.
- Configurable mock Voice Activity Detection.
- Bounded audio buffer with overflow handling.
- Sequence-gap and late-chunk tracking.
- Week 2 integration demonstration.

### Week 3 — Speech Events, Recovery and Transcription Integration

- Speech-start and speech-end event generation.
- Normalized typed audio event envelopes.
- Session ID and correlation ID propagation.
- Audio event ordering and sequence validation.
- Device-loss detection and reconnection attempts.
- Cancellation and buffer release.
- Integration with a mock transcription receiver.
- Week 3 end-to-end demonstration.
- Integration and recovery tests.

---

## 2. Project Structure

```text
sde-5-voicebot/
│
├── audio/
│   ├── __init__.py
│   ├── schemas.py
│   ├── mock_source.py
│   ├── device.py
│   ├── lifecycle.py
│   ├── vad.py
│   ├── buffer.py
│   ├── events.py
│   ├── pipeline.py
│   └── recovery.py
│
├── tests/
│   ├── __init__.py
│   ├── test_audio_schemas.py
│   ├── test_mock_source.py
│   ├── test_device.py
│   ├── test_lifecycle.py
│   ├── test_vad.py
│   ├── test_buffer.py
│   ├── test_events.py
│   ├── test_pipeline.py
│   └── test_recovery.py
│
├── cli_demo.py
├── week2_demo.py
├── week3_demo.py
├── README.md
├── PULL_REQUEST.md
└── .gitignore
```

---

## 3. Technologies and Implementation

- Python
- Dataclasses
- Enum-based state management
- Pytest
- Deterministic mock audio input
- Object-oriented programming
- Event-driven audio processing

All demonstrations and tests use mock audio data. A physical microphone is not required.

---

## 4. Quickstart and Commands

Run commands from the `projects/sde-5-voicebot` directory.

### Week 1 CLI Demonstration

```bash
python cli_demo.py
```

### Week 2 Integration Demonstration

```bash
python week2_demo.py
```

The Week 2 demo demonstrates:

1. Mock audio device discovery.
2. Device selection and permission checking.
3. Deterministic mock audio stream generation.
4. Bounded buffer and overflow handling.
5. Voice Activity Detection.
6. Audio pause, resume and stop operations.
7. Buffer clearing after stopping.

### Week 3 Integration Demonstration

```bash
python week3_demo.py
```

The Week 3 demo demonstrates:

1. Creation of a mock audio format.
2. Generation of deterministic audio chunks.
3. Speech activity detection.
4. Speech-start event generation.
5. Audio event generation with session and correlation IDs.
6. Audio chunk handoff to a mock transcription receiver.
7. Speech-end event generation.
8. Integration summary.

### Run the Complete Test Suite

```bash
python -m pytest -v
```

### Run Individual Test Modules

```bash
python -m pytest tests/test_audio_schemas.py -v
python -m pytest tests/test_mock_source.py -v
python -m pytest tests/test_device.py -v
python -m pytest tests/test_lifecycle.py -v
python -m pytest tests/test_vad.py -v
python -m pytest tests/test_buffer.py -v
python -m pytest tests/test_events.py -v
python -m pytest tests/test_pipeline.py -v
python -m pytest tests/test_recovery.py -v
```

---

## 5. Shared Audio Schemas — Week 1

All shared audio schemas are defined in `audio/schemas.py`.

Existing schemas are reused throughout the implementation. Duplicate audio schema definitions are avoided.

### AudioError

Base exception for invalid audio data and audio-related validation errors.

### AudioFormat

Describes PCM audio characteristics.

- `sample_rate`: Samples per second in Hz.
- `channels`: Number of audio channels.
- `sample_width`: Bytes per sample.
- `frame_size`: Computed from channel count and sample width.

### AudioChunk

Represents an immutable audio chunk.

- `data`: Raw audio bytes.
- `timestamp`: Capture timestamp.
- `sequence_id`: Audio chunk sequence identifier.
- `audio_format`: Associated audio format.

The schemas validate audio formats, timestamps, sequence IDs, and frame alignment.

---

## 6. Mock Audio Source — Week 1

Defined in `audio/mock_source.py`.

Features:

- Simulates microphone input without physical hardware.
- Generates deterministic audio chunks.
- Splits data into frame-aligned chunks.
- Assigns monotonically increasing sequence IDs.
- Generates timestamps based on audio offsets.
- Rejects invalid and misaligned source data.

---

## 7. Device Adapter and Permissions — Week 2

Defined in `audio/device.py`.

### AudioDevice

Abstract interface supporting:

- Listing available audio devices.
- Selecting an audio device.
- Requesting microphone permission.

### MockAudioDevice

Provides deterministic device behavior for testing.

### PermissionState

Supported states:

- `UNKNOWN`
- `GRANTED`
- `DENIED`

Unsupported devices and unavailable permissions raise `DeviceError`.

---

## 8. Audio Lifecycle Controller — Week 2

Defined in `audio/lifecycle.py`.

The `AudioLifecycle` controller manages audio capture states.

### Supported States

- `IDLE`
- `RUNNING`
- `PAUSED`
- `STOPPED`

### Supported Operations

| Operation | Description |
|---|---|
| Start | Selects the configured device and checks permissions |
| Pause | Pauses running audio capture |
| Resume | Resumes paused audio capture |
| Stop | Stops capture and clears buffered audio |

Invalid lifecycle transitions raise `LifecycleError`.

The controller supports injected device adapters and buffers for integration testing.

---

## 9. Voice Activity Detection — Week 2

Defined in `audio/vad.py`.

### MockVAD

Provides deterministic voice activity detection using configurable parameters.

- `threshold`: Minimum audio level required to count as speech.
- `min_speech_duration_ms`: Minimum accumulated speech duration required for detection.

### Behavior

- Audio levels above the threshold accumulate speech duration.
- Audio levels below the threshold reset accumulated speech duration.
- Speech is detected after the minimum duration is reached.
- Invalid threshold, audio level, or duration values are rejected.

The current implementation is a deterministic mock VAD, not a production speech-recognition model.

---

## 10. Bounded Audio Buffer — Week 2

Defined in `audio/buffer.py`.

The `BoundedAudioBuffer` manages incoming audio chunks within a fixed capacity.

### Features

- Configurable buffer capacity.
- FIFO retrieval of accepted chunks.
- Drop-newest overflow policy.
- Dropped-chunk counter.
- Sequence-gap tracking.
- Late and duplicate chunk detection.
- Buffer clearing support.

When the buffer reaches capacity, incoming chunks are rejected and the dropped-chunk counter is incremented.

Stopping the lifecycle controller clears the connected buffer.

---

## 11. Speech Events — Week 3

Defined in `audio/events.py`.

The event module provides structured event representations for the audio pipeline.

### SpeechEventType

Supported event types:

- `SPEECH_STARTED`
- `SPEECH_ENDED`
- `AUDIO_CHUNK`

### SpeechEvent

Each event contains:

- `event_type`: Type of event.
- `session_id`: Identifies the active voice session.
- `correlation_id`: Connects related events.
- `timestamp_ms`: Event timestamp in milliseconds.
- `sequence_id`: Audio sequence identifier when applicable.
- `audio_chunk`: Associated audio chunk for audio events.

### Validation

- Session ID cannot be empty.
- Correlation ID cannot be empty.
- Timestamp must be non-negative.
- Audio events require a valid audio chunk.
- Event sequence ID must match the associated audio chunk.
- Speech boundary events cannot contain audio chunk data.

---

## 12. Audio Event Pipeline — Week 3

Defined in `audio/pipeline.py`.

The `AudioEventPipeline` converts audio chunks and VAD decisions into structured speech events.

### Main Responsibilities

1. Accepts an audio chunk.
2. Processes the supplied audio level and duration through VAD.
3. Detects the beginning of speech.
4. Emits a speech-start event.
5. Emits audio chunk events while speech is active.
6. Detects silence and emits a speech-end event.
7. Maintains session and correlation identifiers.
8. Rejects out-of-order audio chunks.

### Event Ordering

The expected event sequence is:

```text
SPEECH_STARTED
       |
       v
  AUDIO_CHUNK
       |
       v
  AUDIO_CHUNK
       |
       v
  AUDIO_CHUNK
       |
       v
  SPEECH_ENDED
```

Sequence gaps are accepted by the pipeline, while out-of-order chunks are rejected.

The `finish()` operation closes an active speech segment.

---

## 13. Device-Loss Recovery — Week 3

Defined in `audio/recovery.py`.

The `AudioDeviceRecovery` component handles mock audio-device disconnection, reconnection and cancellation.

### RecoveryState

Supported states:

- `CONNECTED`
- `DISCONNECTED`
- `RECOVERING`
- `CANCELLED`
- `FAILED`

### Recovery Operations

| Operation | Description |
|---|---|
| Detect device loss | Marks the device as disconnected |
| Recover | Attempts to reconnect to the configured device |
| Retry | Repeats reconnection attempts up to the configured maximum |
| Cancel | Stops an attached active or paused lifecycle and clears the buffer |

### Cancellation Behavior

Cancellation:

- Stops an active audio lifecycle.
- Stops a paused audio lifecycle.
- Clears buffered audio.
- Changes the recovery state to `CANCELLED`.
- Prevents subsequent recovery attempts.

The recovery implementation uses the existing audio device and lifecycle interfaces.

---

## 14. Transcription Handoff — Week 3

The Week 3 demonstration includes a `MockTranscriptionReceiver` in `week3_demo.py`.

It receives audio events generated by the audio event pipeline.

### Handoff Process

```text
Mock Audio Source
       |
       v
 Audio Chunks
       |
       v
  Mock VAD
       |
       v
 Audio Event Pipeline
       |
       v
 Structured Speech Events
       |
       v
 Mock Transcription Receiver
```

The receiver collects audio chunks from `AUDIO_CHUNK` events.

This validates the event handoff in mock mode. It is not a live integration with the team's production transcription adapter or a speech-recognition service.

---

## 15. Test Coverage

The project contains tests covering all three implementation weeks.

### Week 1

- Audio format validation.
- Audio chunk validation.
- Invalid timestamps and sequence IDs.
- Frame alignment.
- Deterministic mock source generation.

### Week 2

- Device discovery and selection.
- Permission states.
- Lifecycle transitions.
- VAD threshold and speech duration.
- Buffer capacity and FIFO behavior.
- Overflow and dropped-chunk tracking.
- Sequence gaps and late chunks.

### Week 3

- Speech-start and speech-end events.
- Event validation.
- Session and correlation ID propagation.
- Audio event ordering.
- Silence and false-trigger handling.
- Sequence ordering and gaps.
- Device-loss detection.
- Successful and unsuccessful recovery.
- Recovery retry limits.
- Cancellation and buffer clearing.
- Cancellation of running and paused lifecycles.

---

## 16. Latest Test Results

The complete test suite was executed using:

```bash
python -m pytest -v
```

Latest verified result after Week 3 cancellation integration:

```text
100 passed, 1 warning
```

All 100 tests passed successfully.

The warning is a pytest deprecation warning originating from the installed AnyIO plugin. It does not indicate a test failure.

---

## 17. Demo Evidence

### Week 3 Demo

The Week 3 demonstration was executed successfully using:

```bash
python week3_demo.py
```

Observed results:

- Session ID: `demo-session-001`
- Correlation ID: `demo-correlation-001`
- Speech-start event generated.
- Four audio chunks received by the mock transcription receiver.
- Speech-end event generated.
- Total events generated: 6.
- Demo completed successfully.

The demonstration uses deterministic mock audio data and does not require a physical microphone.

---

## 18. Implementation Notes

- Existing Week 1 audio schemas are reused.
- No duplicate shared audio schema definitions are introduced.
- Mock mode is used for deterministic testing.
- No real microphone recordings are committed.
- No credentials or secrets are required.
- The bounded buffer uses a drop-newest overflow policy.
- The VAD is a deterministic mock implementation.
- The transcription receiver is a local mock handoff, not a production transcription integration.

---

## 19. Current Project Status

**Week 1:** Audio schemas, deterministic mock audio source, CLI demonstration and unit tests completed.

**Week 2:** Device adapter, permission handling, lifecycle controller, mock VAD, bounded audio buffer, integration demonstration and tests completed.

**Week 3:** Speech events, audio event pipeline, device-loss recovery, cancellation, mock transcription handoff, integration demonstration and tests implemented.

**Latest verification:** 100 tests passed, 1 non-blocking warning.

**Engineer:** Yashitha N  
**Team:** SDE 5  
**Project:** Academia AI Voice Bot
