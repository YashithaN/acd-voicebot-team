from speech_to_text.accumulator import TranscriptAccumulator
from speech_to_text.schemas import TranscriptSegment, TranscriptEvent


def create_event(event_id, chunk_id, sequence, text, is_final):

    segment = TranscriptSegment(
        segment_id=f"segment-{chunk_id}",
        chunk_id=chunk_id,
        sequence_number=sequence,
        start_ms=sequence * 1000,
        end_ms=(sequence + 1) * 1000,
        text=text,
        confidence=0.95,
        is_final=is_final,
        language="en-IN"
    )

    return TranscriptEvent(
        event_id=event_id,
        event_type="transcript",
        timestamp_ms=segment.end_ms,
        segment=segment
    )


def test_segments_are_ordered():
    accumulator = TranscriptAccumulator()

    accumulator.add_event(
        create_event("e2", "chunk-2", 2, "Second", True)
    )
    accumulator.add_event(
        create_event("e1", "chunk-1", 1, "First", True)
    )

    segments = accumulator.get_segments()

    assert segments[0].text == "First"
    assert segments[1].text == "Second"


def test_duplicate_events_are_ignored():
    accumulator = TranscriptAccumulator()

    event = create_event("e1", "chunk-1", 1, "Hello", True)

    accumulator.add_event(event)
    result = accumulator.add_event(event)

    assert result is False
    assert len(accumulator.get_segments()) == 1


def test_final_replaces_interim():
    accumulator = TranscriptAccumulator()

    interim = create_event("e1", "chunk-1", 1, "Hello", False)
    final = create_event("e2", "chunk-1", 1, "Hello Academia AI", True)

    accumulator.add_event(interim)
    accumulator.add_event(final)

    assert accumulator.get_segments()[0].text == "Hello Academia AI"


def test_interim_does_not_replace_final():
    accumulator = TranscriptAccumulator()

    final = create_event("e1", "chunk-1", 1, "Final transcript", True)
    interim = create_event("e2", "chunk-1", 1, "Interim transcript", False)

    accumulator.add_event(final)
    accumulator.add_event(interim)

    assert accumulator.get_segments()[0].text == "Final transcript"