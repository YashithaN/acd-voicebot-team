
from enum import Enum

from audio.schemas import AudioError


class AudioState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"


class LifecycleError(AudioError):
    """Raised when an invalid audio lifecycle operation is attempted."""


class AudioLifecycle:
    """Controls audio device setup and capture lifecycle."""

    def __init__(self, device=None, device_name=None, buffer=None):
        self.state = AudioState.IDLE
        self.device = device
        self.device_name = device_name
        self.buffer = buffer if buffer is not None else []

    def start(self):
        """Select device, check permission, and start capture."""
        if self.state != AudioState.IDLE:
            raise LifecycleError(
                f"Cannot start audio from {self.state.value} state."
            )

        if self.device is not None:
            if not self.device_name:
                raise LifecycleError("No audio device selected.")

            try:
                self.device.select_device(self.device_name)
                self.device.request_permission()
            except AudioError as exc:
                raise LifecycleError(
                    f"Unable to start audio: {exc}"
                ) from exc

        self.state = AudioState.RUNNING
        return self.state

    def pause(self):
        """Pause audio capture."""
        if self.state != AudioState.RUNNING:
            raise LifecycleError(
                f"Cannot pause audio from {self.state.value} state."
            )

        self.state = AudioState.PAUSED
        return self.state

    def resume(self):
        """Resume paused audio capture."""
        if self.state != AudioState.PAUSED:
            raise LifecycleError(
                f"Cannot resume audio from {self.state.value} state."
            )

        self.state = AudioState.RUNNING
        return self.state

    def stop(self):
        """Stop audio capture and release buffered data."""
        if self.state not in (AudioState.RUNNING, AudioState.PAUSED):
            raise LifecycleError(
                f"Cannot stop audio from {self.state.value} state."
            )

        self.buffer.clear()
        self.state = AudioState.STOPPED
        return self.state
