# Pull Request: W1 Foundation — Audio Schemas, Deterministic Mock Microphone, and CLI Demo

## Summary
- **Workstream:** W1 – Audio and VAD
- **Team:** SDE 5
- **Author:** Yashitha N
- **Target Branch:** `team/sde-5-voicebot` (or `main`)
- **Source Branch:** `feature/yashitha`

This PR establishes the foundation of the Academia AI Voice Bot audio pipeline, providing typed audio contracts, deterministic audio chunking for hardware-independent development, input validation against corrupt/unaligned frames, a CLI demonstration, and a comprehensive 25-test unit suite.

---

## Deliverables & Acceptance Checklist
- [x] **Audio Schemas Defined Once & Documented**: `AudioFormat`, `AudioChunk`, and `AudioError` in `projects/sde-5-voicebot/audio/schemas.py`.
- [x] **Sample-Rate & Channel Validation**: Strict type and range validation raising `AudioError` with descriptive messages.
- [x] **Corrupt & Unaligned Chunk Prevention**: Enforced frame boundary checks (`len(data) % frame_size == 0`) preventing partial or corrupted audio samples.
- [x] **Deterministic Mock Audio Source**: `MockAudioSource` produces identical chunk streams on repeated runs.
- [x] **Monotonic Sequence IDs & Timestamps**: Every chunk carries a 0-indexed sequence counter and continuous millisecond-accurate timestamps.
- [x] **CLI Demonstration**: Runs with a single documented command: `python projects/sde-5-voicebot/cli_demo.py`.
- [x] **Unit Test Suite**: 25 tests covering happy path, invalid inputs, empty chunks, and corrupt unaligned frames.
- [x] **Privacy & Cleanliness**: No credentials, secrets, PII, or raw external audio files committed.

---

## Test Execution Output

Command:
```bash
python -m unittest discover -s projects/sde-5-voicebot/tests -t projects/sde-5-voicebot -v
```

Output:
```text
test_corrupt_non_finite_timestamp (tests.test_audio_schemas.TestAudioChunk.test_corrupt_non_finite_timestamp) ... ok
test_corrupt_stereo_unaligned_chunk (tests.test_audio_schemas.TestAudioChunk.test_corrupt_stereo_unaligned_chunk) ... ok
test_corrupt_unaligned_audio_chunk (tests.test_audio_schemas.TestAudioChunk.test_corrupt_unaligned_audio_chunk) ... ok
test_empty_audio_chunk (tests.test_audio_schemas.TestAudioChunk.test_empty_audio_chunk) ... ok
test_invalid_audio_data (tests.test_audio_schemas.TestAudioChunk.test_invalid_audio_data) ... ok
test_invalid_audio_format_in_chunk (tests.test_audio_schemas.TestAudioChunk.test_invalid_audio_format_in_chunk) ... ok
test_invalid_sequence_id (tests.test_audio_schemas.TestAudioChunk.test_invalid_sequence_id) ... ok
test_invalid_timestamp (tests.test_audio_schemas.TestAudioChunk.test_invalid_timestamp) ... ok
test_valid_audio_chunk (tests.test_audio_schemas.TestAudioChunk.test_valid_audio_chunk) ... ok
test_invalid_channel_count (tests.test_audio_schemas.TestAudioFormat.test_invalid_channel_count) ... ok
test_invalid_channel_count_type (tests.test_audio_schemas.TestAudioFormat.test_invalid_channel_count_type) ... ok
test_invalid_sample_rate (tests.test_audio_schemas.TestAudioFormat.test_invalid_sample_rate) ... ok
test_invalid_sample_rate_type (tests.test_audio_schemas.TestAudioFormat.test_invalid_sample_rate_type) ... ok
test_invalid_sample_width (tests.test_audio_schemas.TestAudioFormat.test_invalid_sample_width) ... ok
test_valid_audio_format (tests.test_audio_schemas.TestAudioFormat.test_valid_audio_format) ... ok
test_corrupt_unaligned_audio_data (tests.test_mock_source.TestMockAudioSource.test_corrupt_unaligned_audio_data) ... ok
test_corrupt_unaligned_chunk_size (tests.test_mock_source.TestMockAudioSource.test_corrupt_unaligned_chunk_size) ... ok
test_every_chunk_has_timestamp (tests.test_mock_source.TestMockAudioSource.test_every_chunk_has_timestamp) ... ok
test_invalid_audio_format (tests.test_mock_source.TestMockAudioSource.test_invalid_audio_format) ... ok
test_invalid_chunk_size (tests.test_mock_source.TestMockAudioSource.test_invalid_chunk_size) ... ok
test_invalid_empty_audio (tests.test_mock_source.TestMockAudioSource.test_invalid_empty_audio) ... ok
test_invalid_start_timestamp (tests.test_mock_source.TestMockAudioSource.test_invalid_start_timestamp) ... ok
test_mock_source_creates_chunks (tests.test_mock_source.TestMockAudioSource.test_mock_source_creates_chunks) ... ok
test_output_is_deterministic (tests.test_mock_source.TestMockAudioSource.test_output_is_deterministic) ... ok
test_sequence_ids_increase (tests.test_mock_source.TestMockAudioSource.test_sequence_ids_increase) ... ok

----------------------------------------------------------------------
Ran 25 tests in 0.001s

OK
```

---

## CLI Demonstration Output

Command:
```bash
python projects/sde-5-voicebot/cli_demo.py
```

Output:
```text
========== MOCK MICROPHONE DEMO ==========
Audio stream started...

Sequence ID : 0
Timestamp   : 0.000000 seconds
Sample Rate : 16000 Hz
Channels    : 1
Chunk Size  : 8 bytes
------------------------------------------
Sequence ID : 1
Timestamp   : 0.000250 seconds
Sample Rate : 16000 Hz
Channels    : 1
Chunk Size  : 8 bytes
------------------------------------------
Sequence ID : 2
Timestamp   : 0.000500 seconds
Sample Rate : 16000 Hz
Channels    : 1
Chunk Size  : 8 bytes
------------------------------------------
Sequence ID : 3
Timestamp   : 0.000750 seconds
Sample Rate : 16000 Hz
Channels    : 1
Chunk Size  : 8 bytes
------------------------------------------
Sequence ID : 4
Timestamp   : 0.001000 seconds
Sample Rate : 16000 Hz
Channels    : 1
Chunk Size  : 8 bytes
------------------------------------------
Sequence ID : 5
Timestamp   : 0.001250 seconds
Sample Rate : 16000 Hz
Channels    : 1
Chunk Size  : 8 bytes
------------------------------------------
Sequence ID : 6
Timestamp   : 0.001500 seconds
Sample Rate : 16000 Hz
Channels    : 1
Chunk Size  : 8 bytes
------------------------------------------
Sequence ID : 7
Timestamp   : 0.001750 seconds
Sample Rate : 16000 Hz
Channels    : 1
Chunk Size  : 8 bytes
------------------------------------------

Audio stream completed successfully!
```

---

## Peer Review Checklist (For Reviewer)
- [ ] Code follows Python conventions and type annotations.
- [ ] No duplicate schemas or cross-boundary mutations.
- [ ] All 25 unit tests execute and pass locally.
- [ ] Deterministic mock stream verified via CLI demo.

---

# Week 2 — Device Permissions, Lifecycle Controls, VAD & Bounded Buffer

**Team:** SDE 5
**Engineer:** Yashitha N
**Workstream:** W1 – Audio and VAD
**Duration:** Week 2 (Day 8 – Day 14)
**Branch:** `feature/yashitha-w2-audio-lifecycle`

## 1. Objective

Extend the Week 1 audio foundation with device selection, permission handling, audio lifecycle controls, configurable mock VAD, and bounded audio buffering.

## 2. Implementation

- Added an audio device interface and deterministic mock device adapter.
- Implemented microphone permission states: UNKNOWN, GRANTED, and DENIED.
- Added device selection and permission validation.
- Implemented audio lifecycle operations: start, pause, resume, and stop.
- Added configurable MockVAD with threshold and minimum speech duration.
- Implemented BoundedAudioBuffer with configurable capacity.
- Added overflow handling and dropped-chunk, sequence-gap, and late-chunk counters.
- Connected the lifecycle controller to the device adapter and bounded buffer.
- Added a Week 2 integration demo using mock audio data.

## 3. Files Added or Updated

**New modules:**
- `audio/device.py`
- `audio/lifecycle.py`
- `audio/vad.py`
- `audio/buffer.py`
- `week2_demo.py`

**Tests:**
- `tests/test_device.py`
- `tests/test_lifecycle.py`
- `tests/test_vad.py`
- `tests/test_buffer.py`

**Documentation:**
- Updated `README.md`
- Updated `PULL_REQUEST.md`

## 4. Test Results

Complete test suite:

`68 passed, 1 warning`

Lifecycle integration tests:

`15 passed`

All tests run using deterministic mock data without requiring a physical microphone.

## 5. Demo Verification

The Week 2 demo successfully demonstrated:

- Mock microphone discovery and selection.
- Permission granted.
- Generation of 10 mock audio chunks.
- Bounded buffer capacity of 3 chunks.
- 7 incoming chunks dropped when the buffer was full.
- Successful speech detection.
- Pause, resume, and stop operations.
- Buffer cleared after stopping.

## 6. Acceptance Criteria

- Device selection and permission handling implemented.
- Unsupported devices and denied permissions handled safely.
- Invalid lifecycle transitions rejected.
- Configurable VAD threshold and minimum speech duration implemented.
- Bounded buffer with overflow handling and dropped-chunk counters implemented.
- Tests cover sequence gaps, late chunks, noise, and lifecycle integration.
- Existing Week 1 schemas reused without duplicate definitions.
- Mock-mode demo runs without real microphone access.

## 7. Submission Status

Week 2 implementation and local verification completed.

**Engineer:** Yashitha N
**Team:** SDE 5
