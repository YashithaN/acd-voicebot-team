
from enum import Enum

from audio.buffer import BoundedAudioBuffer
from audio.device import AudioDevice, DeviceError
from audio.lifecycle import AudioLifecycle, AudioState


class RecoveryError(RuntimeError):
    """Raised when audio device recovery fails."""


class RecoveryState(Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    RECOVERING = "recovering"
    CANCELLED = "cancelled"
    FAILED = "failed"


class AudioDeviceRecovery:
    """
    Handles mock audio-device loss, reconnection and cancellation.
    Cancellation also stops an attached audio lifecycle.
    """

    def __init__(
        self,
        device: AudioDevice,
        device_name: str,
        buffer: BoundedAudioBuffer,
        max_retries: int = 3,
        lifecycle: AudioLifecycle = None,
    ):
        if not isinstance(device, AudioDevice):
            raise RecoveryError("A valid audio device is required.")

        if not device_name:
            raise RecoveryError("Device name cannot be empty.")

        if not isinstance(buffer, BoundedAudioBuffer):
            raise RecoveryError("A valid audio buffer is required.")

        if (
            isinstance(max_retries, bool)
            or not isinstance(max_retries, int)
            or max_retries < 1
        ):
            raise RecoveryError("Maximum retries must be a positive integer.")

        if lifecycle is not None and not isinstance(
            lifecycle, AudioLifecycle
        ):
            raise RecoveryError("A valid audio lifecycle is required.")

        self.device = device
        self.device_name = device_name
        self.buffer = buffer
        self.max_retries = max_retries
        self.lifecycle = lifecycle

        self.state = RecoveryState.CONNECTED
        self.recovery_attempts = 0

    def detect_device_loss(self):
        """Mark the device as disconnected."""

        if self.state == RecoveryState.CANCELLED:
            raise RecoveryError("Capture has been cancelled.")

        if self.state != RecoveryState.CONNECTED:
            raise RecoveryError("Device is not currently connected.")

        self.state = RecoveryState.DISCONNECTED
        return self.state

    def recover(self):
        """Attempt to reconnect to the selected mock device."""

        if self.state == RecoveryState.CANCELLED:
            raise RecoveryError("Cannot recover after cancellation.")

        if self.state != RecoveryState.DISCONNECTED:
            raise RecoveryError(
                "Device must be disconnected before recovery."
            )

        self.state = RecoveryState.RECOVERING

        while self.recovery_attempts < self.max_retries:
            self.recovery_attempts += 1

            try:
                available_devices = self.device.list_devices()

                if self.device_name not in available_devices:
                    raise DeviceError("Selected device is unavailable.")

                self.device.select_device(self.device_name)
                self.device.request_permission()

                self.state = RecoveryState.CONNECTED
                return True

            except DeviceError:
                continue

        self.state = RecoveryState.FAILED
        return False

    def cancel(self):
        """Stop active capture and release buffered audio."""

        if self.state == RecoveryState.CANCELLED:
            return self.state

        if self.lifecycle is not None:
            if self.lifecycle.state in (
                AudioState.RUNNING,
                AudioState.PAUSED,
            ):
                self.lifecycle.stop()

        self.buffer.clear()
        self.state = RecoveryState.CANCELLED

        return self.state
