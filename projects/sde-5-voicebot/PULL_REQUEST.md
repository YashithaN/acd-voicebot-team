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
