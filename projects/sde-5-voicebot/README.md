# SDE 5 Voice Bot — W1: Audio and VAD Foundation

**Team:** SDE 5  
**Engineer:** Yashitha N  
**Workstream:** W1 – Audio and VAD  
**Duration:** Week 1 (Day 1 – Day 7)  
**Branch:** `feature/yashitha` (synced with `feature/w1-audio-schemas`)

---

## 1. Overview

This module provides the foundation of the Academia AI Voice Bot audio pipeline:
- **Typed Audio Schemas**: Clean, immutable dataclass contracts (`AudioFormat`, `AudioChunk`, and `AudioError`) with strict input validation.
- **Deterministic Mock Audio Source**: A fake microphone source emitting identical, frame-aligned chunks with continuous timestamps and monotonically increasing sequence IDs.
- **CLI Demo**: A terminal stream demo printing chunk metadata.
- **Unit Test Suite**: Thorough validation testing happy paths, empty chunks, invalid parameters, and corrupt/unaligned audio chunks.

---

## 2. Quickstart & Commands

### Run CLI Demonstration (Single Command)
From the repository root:
```bash
python projects/sde-5-voicebot/cli_demo.py
```
Or from within the project directory:
```bash
cd projects/sde-5-voicebot
python cli_demo.py
```

### Run Unit Tests (Single Command)
From the repository root:
```bash
python -m unittest discover -s projects/sde-5-voicebot/tests -t projects/sde-5-voicebot
```
Or with `pytest`:
```bash
cd projects/sde-5-voicebot
python -m pytest
```

---

## 3. Schema Specifications & Contracts

All schemas are defined once in `projects/sde-5-voicebot/audio/schemas.py`.

### `AudioError(ValueError)`
Base exception raised for invalid audio data, invalid parameters, corrupt chunks, or misaligned audio frames.

### `AudioFormat`
Describes PCM audio characteristics.
- `sample_rate` (`int`): Samples per second in Hz. Must be an integer `> 0`.
- `channels` (`int`): Audio channel count (1 = mono, 2 = stereo). Must be an integer `> 0`.
- `sample_width` (`int`, default `2`): Byte depth per sample (e.g. 2 for 16-bit PCM). Must be an integer `> 0`.
- `frame_size` (`int`, property): Computed as `channels * sample_width`.

### `AudioChunk`
Represents an immutable chunk of audio streaming through the pipeline.
- `data` (`bytes`): Raw audio bytes. Must be non-empty and a multiple of `audio_format.frame_size`. Unaligned/partial frames raise `AudioError` (corrupt chunk prevention).
- `timestamp` (`float`): Capture timestamp in seconds. Must be finite and non-negative (`>= 0.0`).
- `sequence_id` (`int`): Monotonically increasing sequence index. Must be an integer `>= 0`.
- `audio_format` (`AudioFormat`): Format metadata associated with the chunk.

---

## 4. Mock Audio Source (`MockAudioSource`)

Defined in `projects/sde-5-voicebot/audio/mock_source.py`.
- Simulates live microphone input without physical hardware.
- Slices audio data into frame-aligned chunks deterministically: identical inputs produce identical chunks across runs.
- Assigns monotonic `sequence_id` (0, 1, 2, ...) and accurate offset-based timestamps.
- Enforces frame alignment for both source data and chunk size.

---

## 5. Test Suite Summary

Tests cover all specified acceptance criteria across 25 unit tests:
- **Valid Happy Path**: Schema instantiation, sequence ordering, timestamp continuity, multi-run determinism.
- **Empty Chunks**: Rejection of empty byte payloads.
- **Invalid Inputs**: Non-integer types, boolean values, negative sequence IDs, negative timestamps, invalid formats.
- **Corrupt / Misaligned Chunks**: Detection and rejection of odd-byte slices and incomplete PCM frames.
