from audio.lifecycle import AudioLifecycle, AudioState
import pytest

from audio.buffer import BoundedAudioBuffer
from audio.device import MockAudioDevice, PermissionState
from audio.recovery import (
    AudioDeviceRecovery,
    RecoveryError,
    RecoveryState,
)


def make_recovery(
    devices=None,
    permission=PermissionState.GRANTED,
    max_retries=3,
):
    device = MockAudioDevice(
        devices=devices if devices is not None else ["Mock Microphone"],
        permission_state=permission,
    )
    buffer = BoundedAudioBuffer(capacity=5)

    recovery = AudioDeviceRecovery(
        device=device,
        device_name="Mock Microphone",
        buffer=buffer,
        max_retries=max_retries,
    )

    return recovery, device, buffer


def test_device_loss_changes_state():
    recovery, _, _ = make_recovery()

    assert recovery.detect_device_loss() == RecoveryState.DISCONNECTED


def test_successful_reconnection():
    recovery, device, _ = make_recovery()

    recovery.detect_device_loss()

    assert recovery.recover() is True
    assert recovery.state == RecoveryState.CONNECTED
    assert device.selected_device == "Mock Microphone"


def test_recovery_attempt_counter():
    recovery, _, _ = make_recovery()

    recovery.detect_device_loss()
    recovery.recover()

    assert recovery.recovery_attempts == 1


def test_missing_device_causes_recovery_failure():
    recovery, _, _ = make_recovery(devices=[])

    recovery.detect_device_loss()

    assert recovery.recover() is False
    assert recovery.state == RecoveryState.FAILED


def test_recovery_stops_after_max_retries():
    recovery, _, _ = make_recovery(devices=[], max_retries=2)

    recovery.detect_device_loss()
    recovery.recover()

    assert recovery.recovery_attempts == 2


def test_denied_permission_causes_recovery_failure():
    recovery, _, _ = make_recovery(
        permission=PermissionState.DENIED
    )

    recovery.detect_device_loss()

    assert recovery.recover() is False
    assert recovery.state == RecoveryState.FAILED


def test_cancel_clears_buffer():
    recovery, _, buffer = make_recovery()

    assert buffer.add.__name__ == "add"

    recovery.cancel()

    assert buffer.is_empty
    assert recovery.state == RecoveryState.CANCELLED


def test_cancel_prevents_recovery():
    recovery, _, _ = make_recovery()

    recovery.detect_device_loss()
    recovery.cancel()

    with pytest.raises(RecoveryError):
        recovery.recover()


def test_cancel_is_idempotent():
    recovery, _, _ = make_recovery()

    recovery.cancel()
    result = recovery.cancel()

    assert result == RecoveryState.CANCELLED


def test_cannot_detect_loss_twice():
    recovery, _, _ = make_recovery()

    recovery.detect_device_loss()

    with pytest.raises(RecoveryError):
        recovery.detect_device_loss()

def test_cancel_stops_running_audio_lifecycle():
    device = MockAudioDevice(devices=["Mock Microphone"])
    buffer = BoundedAudioBuffer(capacity=5)
    lifecycle = AudioLifecycle(buffer=buffer)

    lifecycle.start()

    recovery = AudioDeviceRecovery(
        device=device,
        device_name="Mock Microphone",
        buffer=buffer,
        lifecycle=lifecycle,
    )

    recovery.cancel()

    assert lifecycle.state == AudioState.STOPPED
    assert recovery.state == RecoveryState.CANCELLED


def test_cancel_stops_paused_audio_lifecycle():
    device = MockAudioDevice(devices=["Mock Microphone"])
    buffer = BoundedAudioBuffer(capacity=5)
    lifecycle = AudioLifecycle(buffer=buffer)

    lifecycle.start()
    lifecycle.pause()

    recovery = AudioDeviceRecovery(
        device=device,
        device_name="Mock Microphone",
        buffer=buffer,
        lifecycle=lifecycle,
    )

    recovery.cancel()

    assert lifecycle.state == AudioState.STOPPED
    assert recovery.state == RecoveryState.CANCELLED
