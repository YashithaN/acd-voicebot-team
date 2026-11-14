# SDE 5 Voice Bot — Audio Pipeline: W1 & W2

**Team:** SDE 5
**Engineer:** Yashitha N
**Workstream:** W1 – Audio and VAD
**Duration:** Week 1 and Week 2 (Day 1 – Day 14)
**Week 1 Branch:** `feature/yashitha`
**Week 2 Branch:** `feature/yashitha-w2-audio-lifecycle`

---

## 1. Overview

This module provides the foundation of the Academia AI Voice Bot audio pipeline.

It implements typed audio schemas, deterministic mock audio input, device selection and permissions, audio lifecycle management, Voice Activity Detection (VAD), and bounded audio buffering.

### Week 1 — Audio and VAD Foundation

- **Typed Audio Schemas:** Immutable dataclass contracts (`AudioFormat`, `AudioChunk`, and `AudioError`) with strict input validation.
- **Deterministic Mock Audio Source:** A fake microphone source emitting frame-aligned chunks with continuous timestamps and monotonically increasing sequence IDs.
- **CLI Demo:** A terminal stream demo printing chunk metadata.
- **Unit Test Suite:** Validation of valid inputs, invalid parameters, empty chunks, and corrupt or unaligned audio chunks.

### Week 2 — Device, Lifecycle, VAD and Buffer

- **Device Adapter:** Mock audio device interface supporting device listing, device selection, and permission states.
- **Permission Handling:** Handles granted, denied, and unknown microphone permission states.
- **Audio Lifecycle Controller:** Supports start, pause, resume, and stop operations while rejecting invalid transitions.
- **Voice Activity Detection:** Configurable mock VAD with speech threshold and minimum speech duration.
- **Bounded Audio Buffer:** Capacity-limited buffer with overflow handling, dropped-chunk counters, sequence-gap tracking, and late-chunk detection.
- **Integration Demo:** Demonstrates the audio pipeline using mock data without requiring a physical microphone.

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
│   └── buffer.py
│
├── tests/
│   ├── __init__.py
│   ├── test_audio_schemas.py
│   ├── test_mock_source.py
│   ├── test_device.py
│   ├── test_lifecycle.py
│   ├── test_vad.py
│   └── test_buffer.py
│
├── cli_demo.py
├── week2_demo.py
├── README.md
├── PULL_REQUEST.md
└── .gitignore
```

---

## 3. Quickstart & Commands

Run all commands from the `projects/sde-5-voicebot` directory unless otherwise specified.

### Run Week 1 CLI Demonstration

```bash
python cli_demo.py
```

### Run Week 2 Integration Demonstration

```bash
python week2_demo.py
```

The Week 2 demo demonstrates:

1. Mock audio device discovery.
2. Device selection and permission checking.
3. Deterministic mock audio stream generation.
4. Bounded buffer and overflow handling.
5. Voice Activity Detection.
6. Audio pause, resume, and stop operations.
7. Buffer clearing after stopping.

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
```

---

## 4. Schema Specifications & Contracts

All shared audio schemas are defined once in `audio/schemas.py`.

### AudioError(ValueError)

Base exception raised for invalid audio data, parameters, corrupt chunks, or misaligned audio frames.

### AudioFormat

Describes PCM audio characteristics.

- `sample_rate` (`int`): Samples per second in Hz. Must be greater than zero.
- `channels` (`int`): Audio channel count.
- `sample_width` (`int`, default `2`): Byte depth per sample.
- `frame_size` (`int`, property): Computed as `channels * sample_width`.

### AudioChunk

Represents an immutable chunk of audio streaming through the pipeline.

- `data` (`bytes`): Non-empty raw audio bytes aligned to the audio frame size.
- `timestamp` (`float`): Finite, non-negative capture timestamp.
- `sequence_id` (`int`): Non-negative sequence identifier.
- `audio_format` (`AudioFormat`): Format metadata associated with the chunk.

---

## 5. Mock Audio Source

Defined in `audio/mock_source.py`.

- Simulates live microphone input without physical hardware.
- Splits audio data into frame-aligned chunks deterministically.
- Assigns monotonically increasing sequence IDs.
- Calculates timestamps based on audio offsets.
- Rejects invalid or misaligned source data.

---

## 6. Device Adapter and Permissions — Week 2

Defined in `audio/device.py`.

### AudioDevice

Abstract interface defining:

- Listing available audio devices.
- Selecting an audio device.
- Requesting microphone permission.

### MockAudioDevice

Provides deterministic device behavior for testing without a real microphone.

### PermissionState

Supported permission states:

- `UNKNOWN`
- `GRANTED`
- `DENIED`

Unsupported devices and unavailable permissions raise `DeviceError` rather than crashing the application.

---

## 7. Audio Lifecycle Controller — Week 2

Defined in `audio/lifecycle.py`.

The `AudioLifecycle` controller manages the audio capture lifecycle.

### Supported States

- `IDLE`
- `RUNNING`
- `PAUSED`
- `STOPPED`

### Supported Operations

| Operation | Description |
|---|---|
| Start | Selects the configured device, checks permission, and starts capture |
| Pause | Pauses running audio capture |
| Resume | Resumes paused audio capture |
| Stop | Stops capture and clears buffered data |

Invalid lifecycle transitions raise `LifecycleError`.

The controller can use an injected device adapter and bounded buffer for integration testing.

---

## 8. Voice Activity Detection — Week 2

Defined in `audio/vad.py`.

### MockVAD

Provides deterministic voice activity detection using configurable parameters.

- `threshold`: Minimum audio level required to count as speech.
- `min_speech_duration_ms`: Minimum accumulated speech duration required for detection.

### Behavior

- Audio levels above the configured threshold accumulate speech duration.
- Audio levels below the threshold reset accumulated speech duration.
- Speech is detected once the minimum duration is reached.
- Invalid threshold, audio level, or duration values are rejected.

The current implementation is a deterministic mock VAD, not a production speech-recognition model.

---

## 9. Bounded Audio Buffer — Week 2

Defined in `audio/buffer.py`.

The `BoundedAudioBuffer` manages incoming audio chunks within a fixed capacity.

### Features

- Configurable maximum buffer capacity.
- FIFO retrieval of accepted chunks.
- Overflow handling using a drop-newest policy.
- Dropped-chunk counter.
- Sequence-gap counter.
- Late and duplicate chunk detection.
- Buffer clearing support.

When the buffer reaches capacity, incoming chunks are rejected and the dropped-chunk counter is incremented.

Stopping the lifecycle controller clears the connected buffer.

---

## 10. Test Suite Summary

The complete project test suite currently contains **68 passing tests**.

### Test Coverage

- **Audio Schemas:** Valid and invalid formats, timestamps, sequence IDs, and corrupt chunks.
- **Mock Audio Source:** Deterministic chunk generation, frame alignment, timestamps, and sequence ordering.
- **Device Adapter:** Device discovery, selection, unsupported devices, and permission states.
- **Lifecycle Controller:** Start, pause, resume, stop, invalid transitions, permission denial, unsupported devices, and buffer clearing.
- **Voice Activity Detection:** Thresholds, minimum speech duration, silence, noise, and invalid inputs.
- **Bounded Buffer:** Capacity, FIFO retrieval, overflow, dropped chunks, sequence gaps, late chunks, and duplicate chunks.

### Latest Test Result

```text
68 passed, 1 warning
```

The warning is a pytest deprecation warning originating from the installed AnyIO plugin. It does not indicate a test failure.

---

## 11. Week 2 Demo Output

The Week 2 demo uses mock audio data and does not require a physical microphone.

Expected demonstration results:

- Available device: Mock Microphone
- Permission: Granted
- Generated audio chunks: 10
- Buffer capacity: 3
- Accepted chunks: 3
- Dropped chunks: 7
- Speech detection: True
- Lifecycle transitions: Running → Paused → Running → Stopped
- Buffer size after stop: 0

---

## 12. Implementation Notes

- Existing Week 1 schemas are reused; duplicate schema definitions are avoided.
- Mock mode is used for deterministic testing without real microphone hardware.
- No real microphone recordings or credentials are required for the test suite.
- The bounded buffer uses a deterministic drop-newest overflow policy.
- The current VAD implementation is a configurable mock interface.

---

## 13. Current Status

**Week 1:** Foundation implementation and tests completed.

**Week 2:** Device adapter, permission handling, lifecycle controller, mock VAD, bounded buffer, integration tests, and demo completed.

**Latest verification:** 68 tests passed successfully.

**Engineer:** Yashitha N
**Team:** SDE 5
**Project:** Academia AI Voice Bot
