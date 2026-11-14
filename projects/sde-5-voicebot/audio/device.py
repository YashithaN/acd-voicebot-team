
from abc import ABC, abstractmethod
from enum import Enum

from audio.schemas import AudioError


class PermissionState(Enum):
    UNKNOWN = "unknown"
    GRANTED = "granted"
    DENIED = "denied"


class DeviceError(AudioError):
    """Raised when an audio device cannot be used."""


class AudioDevice(ABC):
    """Interface that all audio devices must implement."""

    @abstractmethod
    def list_devices(self):
        """Return available audio device names."""
        pass

    @abstractmethod
    def select_device(self, device_name):
        """Select a device by name."""
        pass

    @abstractmethod
    def request_permission(self):
        """Request microphone permission."""
        pass


class MockAudioDevice(AudioDevice):
    """Deterministic mock device for testing without a microphone."""

    def __init__(
        self,
        devices=None,
        permission_state=PermissionState.GRANTED
    ):
        self.devices = devices if devices is not None else ["Mock Microphone"]
        self.permission_state = permission_state
        self.selected_device = None

    def list_devices(self):
        return list(self.devices)

    def select_device(self, device_name):
        if not self.devices:
            raise DeviceError("No supported audio devices available.")

        if device_name not in self.devices:
            raise DeviceError(f"Unsupported audio device: {device_name}")

        self.selected_device = device_name
        return self.selected_device

    def request_permission(self):
        if self.permission_state == PermissionState.DENIED:
            raise DeviceError("Microphone permission denied.")

        if self.permission_state != PermissionState.GRANTED:
            raise DeviceError("Microphone permission is not available.")

        return self.permission_state
