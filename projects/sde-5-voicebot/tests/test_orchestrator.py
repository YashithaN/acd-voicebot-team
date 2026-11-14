from speech_to_text.orchestrator import SpeechToTextOrchestrator
from speech_to_text.fake_transcriber import FakeTranscriber


def test_audio_chunk_to_transcript():

    provider = FakeTranscriber()

    orchestrator = SpeechToTextOrchestrator(provider)

    audio_chunk = {
        "chunk_id": "chunk-001",
        "sequence_number": 0,
        "start_ms": 0,
        "end_ms": 2000,
        "audio_data": b"synthetic audio data"
    }

    events = orchestrator.process_audio_chunk(audio_chunk)

    assert len(events) == 1
    assert events[0].event_type == "transcript"

    transcript = orchestrator.get_transcript()

    assert isinstance(transcript, str)
    assert len(transcript) > 0


def test_orchestrator_stores_segments():

    provider = FakeTranscriber()
    orchestrator = SpeechToTextOrchestrator(provider)

    audio_chunk = {
        "chunk_id": "chunk-002",
        "sequence_number": 0,
        "start_ms": 0,
        "end_ms": 2000,
        "audio_data": b"another synthetic audio chunk"
    }

    orchestrator.process_audio_chunk(audio_chunk)

    segments = orchestrator.get_segments()

    assert len(segments) == 1
    assert segments[0].chunk_id == "chunk-002"