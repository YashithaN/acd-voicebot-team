
import pytest

from audio.lifecycle import AudioLifecycle, AudioState, LifecycleError
from audio.device import MockAudioDevice, PermissionState
from audio.buffer import BoundedAudioBuffer
from audio.schemas import AudioFormat, AudioChunk


def test_initial_state_is_idle():
    lifecycle = AudioLifecycle()
    assert lifecycle.state == AudioState.IDLE


def test_start_audio():
    lifecycle = AudioLifecycle()
    result = lifecycle.start()

    assert result == AudioState.RUNNING
    assert lifecycle.state == AudioState.RUNNING


def test_pause_audio():
    lifecycle = AudioLifecycle()
    lifecycle.start()

    result = lifecycle.pause()

    assert result == AudioState.PAUSED
    assert lifecycle.state == AudioState.PAUSED


def test_resume_audio():
    lifecycle = AudioLifecycle()
    lifecycle.start()
    lifecycle.pause()

    result = lifecycle.resume()

    assert result == AudioState.RUNNING
    assert lifecycle.state == AudioState.RUNNING


def test_stop_audio():
    lifecycle = AudioLifecycle()
    lifecycle.start()

    result = lifecycle.stop()

    assert result == AudioState.STOPPED
    assert lifecycle.state == AudioState.STOPPED


def test_stop_clears_buffer():
    lifecycle = AudioLifecycle()
    lifecycle.buffer.append(b"audio data")

    lifecycle.start()
    lifecycle.stop()

    assert lifecycle.buffer == []


def test_cannot_start_twice():
    lifecycle = AudioLifecycle()
    lifecycle.start()

    with pytest.raises(LifecycleError):
        lifecycle.start()


def test_cannot_pause_when_idle():
    lifecycle = AudioLifecycle()

    with pytest.raises(LifecycleError):
        lifecycle.pause()


def test_cannot_resume_when_not_paused():
    lifecycle = AudioLifecycle()

    with pytest.raises(LifecycleError):
        lifecycle.resume()


def test_cannot_stop_when_idle():
    lifecycle = AudioLifecycle()

    with pytest.raises(LifecycleError):
        lifecycle.stop()


def test_cannot_stop_twice():
    lifecycle = AudioLifecycle()
    lifecycle.start()
    lifecycle.stop()

    with pytest.raises(LifecycleError):
        lifecycle.stop()


# Week 2 integration tests


def test_start_checks_device_and_permission():
    device = MockAudioDevice(
        permission_state=PermissionState.GRANTED
    )

    lifecycle = AudioLifecycle(
        device=device,
        device_name="Mock Microphone"
    )

    lifecycle.start()

    assert lifecycle.state == AudioState.RUNNING
    assert device.selected_device == "Mock Microphone"


def test_start_fails_when_permission_is_denied():
    device = MockAudioDevice(
        permission_state=PermissionState.DENIED
    )

    lifecycle = AudioLifecycle(
        device=device,
        device_name="Mock Microphone"
    )

    with pytest.raises(LifecycleError):
        lifecycle.start()

    assert lifecycle.state == AudioState.IDLE


def test_start_fails_for_unsupported_device():
    device = MockAudioDevice()

    lifecycle = AudioLifecycle(
        device=device,
        device_name="Unknown Microphone"
    )

    with pytest.raises(LifecycleError):
        lifecycle.start()

    assert lifecycle.state == AudioState.IDLE


def test_stop_clears_actual_bounded_buffer():
    audio_format = AudioFormat(
        sample_rate=16000,
        channels=1,
        sample_width=2
    )

    chunk = AudioChunk(
        data=b"\x00\x00",
        timestamp=0.0,
        sequence_id=0,
        audio_format=audio_format
    )

    buffer = BoundedAudioBuffer(capacity=5)
    buffer.add(chunk)

    lifecycle = AudioLifecycle(buffer=buffer)
    lifecycle.start()
    lifecycle.stop()

    assert buffer.is_empty
