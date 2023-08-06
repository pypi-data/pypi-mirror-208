# Copyright © 2020 by IoT Spectator. All rights reserved.

"""IoT Health."""

from typing import Optional

from iothealth import _base_health
from iothealth import linux
from iothealth import raspberry_pi


class DeviceHealth(_base_health.BaseHealth):
    """Generic class for a device health info."""

    _current_device_cache: Optional[_base_health.BaseHealth] = None

    # Override
    @classmethod
    def summary(cls) -> dict:
        """Provide the health information for the current device.

        Returns
        -------
        `dict`
            All the available health information as a key-value dictionary.
        """
        return DeviceHealth._current_device().summary()

    # Override
    @classmethod
    def device_platform(cls) -> str:
        """Provide the device platform info."""
        return DeviceHealth._current_device().device_platform()

    # Override
    @classmethod
    def processor_architecture(cls) -> str:
        """Provide the device CPU info."""
        return DeviceHealth._current_device().processor_architecture()

    # Override
    @classmethod
    def operating_system(cls) -> str:
        """Provide the device OS info."""
        return DeviceHealth._current_device().operating_system()

    # Override
    @classmethod
    def processors(cls) -> dict:
        """Provice the device processors info."""
        return DeviceHealth._current_device().processors()

    # Override
    @classmethod
    def memory(cls) -> dict:
        """Provide the device memory info."""
        return DeviceHealth._current_device().memory()

    # Override
    @classmethod
    def capacity(cls) -> dict:
        """Provide the device disk usage info."""
        return DeviceHealth._current_device().capacity()

    # Override
    @classmethod
    def temperature(cls) -> dict:
        """Provide the device temperature."""
        return DeviceHealth._current_device().temperature()

    # Override
    @classmethod
    def cameras(cls) -> dict:
        """Provide the cameras info."""
        return DeviceHealth._current_device().cameras()

    @classmethod
    def _current_device(cls) -> _base_health.BaseHealth:
        if cls._current_device_cache is None:
            if "Raspberry Pi" in raspberry_pi.RaspberryPi().device_platform():
                cls._current_device_cache = raspberry_pi.RaspberryPi()
            else:
                cls._current_device_cache = (
                    linux.Linux()
                )  # Jetson Nano is also included
        return cls._current_device_cache
