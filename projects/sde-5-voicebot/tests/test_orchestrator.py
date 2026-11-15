import pytest

from speech_to_text.orchestrator import SpeechToTextOrchestrator
from speech_to_text.fake_transcriber import FakeTranscriber
from speech_to_text.schemas import TranscriptEvent, TranscriptSegment


def create_audio_chunk(chunk_id, sequence_number):

    return {
        "chunk_id": chunk_id,
        "sequence_number": sequence_number,
        "start_ms": sequence_number * 2000,
        "end_ms": (sequence_number + 1) * 2000,
        "audio_data": f"audio-{chunk_id}".encode()
    }


def test_audio_chunk_to_transcript():

    provider = FakeTranscriber()
    orchestrator = SpeechToTextOrchestrator(provider)

    audio_chunk = create_audio_chunk("chunk-001", 0)

    events = orchestrator.process_audio_chunk(audio_chunk)

    assert len(events) == 1
    assert events[0].event_type == "transcript"

    transcript = orchestrator.get_transcript()

    assert isinstance(transcript, str)
    assert len(transcript) > 0


def test_orchestrator_stores_segments():

    provider = FakeTranscriber()
    orchestrator = SpeechToTextOrchestrator(provider)

    audio_chunk = create_audio_chunk("chunk-002", 0)

    orchestrator.process_audio_chunk(audio_chunk)

    segments = orchestrator.get_segments()

    assert len(segments) == 1
    assert segments[0].chunk_id == "chunk-002"


def test_out_of_order_chunks_produce_ordered_transcript():

    provider = FakeTranscriber()
    orchestrator = SpeechToTextOrchestrator(provider)

    chunk_2 = create_audio_chunk("chunk-2", 2)
    chunk_0 = create_audio_chunk("chunk-0", 0)
    chunk_1 = create_audio_chunk("chunk-1", 1)

    orchestrator.process_audio_chunk(chunk_2)
    orchestrator.process_audio_chunk(chunk_0)
    orchestrator.process_audio_chunk(chunk_1)

    segments = orchestrator.get_segments()

    assert [s.sequence_number for s in segments] == [0, 1, 2]

    expected_transcript = " ".join(s.text for s in segments)

    assert orchestrator.get_transcript() == expected_transcript


def test_duplicate_chunk_is_ignored():

    provider = FakeTranscriber()
    orchestrator = SpeechToTextOrchestrator(provider)

    audio_chunk = create_audio_chunk("duplicate-001", 0)

    first_result = orchestrator.process_audio_chunk(audio_chunk)
    second_result = orchestrator.process_audio_chunk(audio_chunk)

    assert len(first_result) == 1
    assert second_result == []
    assert len(orchestrator.get_segments()) == 1


class FailingProvider:

    def transcribe(self, audio_chunk):
        raise RuntimeError("Sensitive internal error details")


def test_orchestrator_returns_safe_error_event():

    orchestrator = SpeechToTextOrchestrator(FailingProvider())

    audio_chunk = create_audio_chunk("error-001", 0)

    events = orchestrator.process_audio_chunk(audio_chunk)

    assert len(events) == 1

    error_event = events[0]

    assert error_event.event_type == "error"
    assert error_event.error_code == "PROVIDER_ERROR"
    assert error_event.message == "Speech recognition provider failed"
    assert error_event.retryable is True

    assert "Sensitive internal error details" not in error_event.message


def test_interim_event_is_replaced_by_final_event():

    provider = FakeTranscriber()
    orchestrator = SpeechToTextOrchestrator(provider)

    interim_segment = TranscriptSegment(
        segment_id="segment-interim",
        chunk_id="chunk-interim",
        sequence_number=0,
        start_ms=0,
        end_ms=1000,
        text="Hello",
        confidence=0.80,
        is_final=False
    )

    final_segment = TranscriptSegment(
        segment_id="segment-final",
        chunk_id="chunk-interim",
        sequence_number=0,
        start_ms=0,
        end_ms=1000,
        text="Hello everyone",
        confidence=0.98,
        is_final=True
    )

    interim_event = TranscriptEvent(
        event_id="event-interim",
        event_type="transcript",
        timestamp_ms=1000,
        segment=interim_segment
    )

    final_event = TranscriptEvent(
        event_id="event-final",
        event_type="transcript",
        timestamp_ms=1200,
        segment=final_segment
    )

    orchestrator.accumulator.add_event(interim_event)
    orchestrator.accumulator.add_event(final_event)

    segments = orchestrator.get_segments()

    assert len(segments) == 1
    assert segments[0].is_final is True
    assert segments[0].text == "Hello everyone"