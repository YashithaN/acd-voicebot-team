# Speech-to-Text Module

## 1. Overview

This module manages speech-to-text processing. It defines transcript schemas, validates transcript data, handles transcript events and provides a fake transcriber for testing.

## 2. TranscriptSegment Schema

TranscriptSegment represents one part of a converted speech transcript.

| Field | Data Type | Description | Constraints |
|---|---|---|---|
| segment_id | String | Unique transcript segment ID | Cannot be empty |
| chunk_id | String | ID of the audio chunk | Cannot be empty |
| sequence_number | Integer | Order of the audio chunk | Must be non-negative |
| start_ms | Integer | Starting timestamp in milliseconds | Must be non-negative |
| end_ms | Integer | Ending timestamp in milliseconds | Must be greater than or equal to start_ms |
| text | String | Recognized speech text | Must be a string |
| confidence | Float | Recognition confidence score | Must be between 0 and 1 |
| is_final | Boolean | Indicates whether the transcript is final or interim | Must be True or False |
| language | String | Language code of the transcript | Cannot be empty; default is en-IN |

## 3. TranscriptEvent Schema

TranscriptEvent represents an event generated during speech-to-text processing.

| Field | Data Type | Description | Constraints |
|---|---|---|---|
| event_id | String | Unique event ID | Cannot be empty |
| event_type | String | Type of event | Must be transcript or error |
| timestamp_ms | Integer | Event timestamp in milliseconds | Must be non-negative |
| segment | TranscriptSegment or None | Transcript information | Required for transcript events |
| error | String or None | Error message | Required for error events |

### Event Types

- **transcript:** Contains a TranscriptSegment and no error message.
- **error:** Contains an error message and no transcript segment.

## 4. Validation Rules

- Segment and event IDs cannot be empty.
- Sequence numbers cannot be negative.
- Timestamps cannot be negative.
- End timestamps cannot be earlier than start timestamps.
- Confidence scores must be between 0 and 1.
- The is_final field must be a Boolean.
- Language cannot be empty.
- Event types must be transcript or error.
- Transcript and error events must contain the correct fields.

Invalid data raises a ValueError with a descriptive message.

## 5. Language and Error Fields

The language field stores a language identifier such as en or en-IN. The default language is en-IN.

The error field stores an error message when transcription processing fails. It is None for transcript events.

## 6. Testing

The module includes tests for valid transcript schemas, invalid payload validation, transcript event validation, fake transcriber output and deterministic transcription results.

Run all tests using:

```bash
python -m pytest -v
```