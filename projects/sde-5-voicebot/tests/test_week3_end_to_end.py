
from audio.events import SpeechEventType
from audio.pipeline import AudioEventPipeline
from audio.mock_source import MockAudioSource
from audio.schemas import AudioFormat
from audio.vad import MockVAD

from speech_to_text.audio_bridge import AudioToSpeechBridge
from speech_to_text.orchestrator import SpeechToTextOrchestrator
from speech_to_text.fake_transcriber import FakeTranscriber


def test_audio_pipeline_reaches_mock_transcriber_end_to_end():

    session_id = "e2e-session-001"
    correlation_id = "e2e-correlation-001"

    audio_format = AudioFormat(
        sample_rate=16000,
        channels=1,
        sample_width=2
    )

    source = MockAudioSource(
        audio_data=bytes(range(256)),
        audio_format=audio_format,
        chunk_size=320
    )

    pipeline = AudioEventPipeline(
        vad=MockVAD(
            threshold=0.5,
            min_speech_duration_ms=100
        ),
        session_id=session_id,
        correlation_id=correlation_id
    )

    orchestrator = SpeechToTextOrchestrator(
        provider=FakeTranscriber()
    )

    bridge = AudioToSpeechBridge(
        orchestrator=orchestrator,
        session_id=session_id
    )

    transcript_events = []

    for chunk in source.stream():

        speech_events = pipeline.process_chunk(
            chunk=chunk,
            audio_level=0.8,
            duration_ms=100
        )

        for speech_event in speech_events:

            result = bridge.process_speech_event(speech_event)
            transcript_events.extend(result)

    # Finish any active speech segment.
    final_events = pipeline.finish()

    for speech_event in final_events:
        result = bridge.process_speech_event(speech_event)
        transcript_events.extend(result)

    # At least one transcript must be generated.
    assert transcript_events

    transcript = orchestrator.get_transcript(session_id)

    assert isinstance(transcript, str)
    assert transcript.strip()

    # Verify session and correlation IDs.
    for event in transcript_events:

        assert event.session_id == session_id
        assert event.correlation_id == correlation_id

        if event.segment is not None:
            assert event.segment.session_id == session_id
            assert event.segment.correlation_id == correlation_id

    assert any(
        event.event_type == "transcript"
        for event in transcript_events
    )

    # Verify that the bridge received the audio chunks.
    assert bridge.get_received_sequence_ids(session_id) == [0]
