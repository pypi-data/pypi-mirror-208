"""Unit tests for Device Health module."""

from iothealth import device_health


def test_basic():
    assert device_health.DeviceHealth().summary() is not None
