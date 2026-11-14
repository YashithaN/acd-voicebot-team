
import pytest

from audio.device import (
    MockAudioDevice,
    PermissionState,
    DeviceError,
)


def test_list_devices():
    device = MockAudioDevice()

    assert device.list_devices() == ["Mock Microphone"]


def test_select_device():
    device = MockAudioDevice()

    result = device.select_device("Mock Microphone")

    assert result == "Mock Microphone"
    assert device.selected_device == "Mock Microphone"


def test_unsupported_device():
    device = MockAudioDevice()

    with pytest.raises(DeviceError):
        device.select_device("Unknown Microphone")


def test_no_devices_available():
    device = MockAudioDevice(devices=[])

    with pytest.raises(DeviceError):
        device.select_device("Mock Microphone")


def test_permission_granted():
    device = MockAudioDevice(
        permission_state=PermissionState.GRANTED
    )

    assert device.request_permission() == PermissionState.GRANTED


def test_permission_denied():
    device = MockAudioDevice(
        permission_state=PermissionState.DENIED
    )

    with pytest.raises(DeviceError, match="denied"):
        device.request_permission()


def test_permission_unknown():
    device = MockAudioDevice(
        permission_state=PermissionState.UNKNOWN
    )

    with pytest.raises(DeviceError):
        device.request_permission()
