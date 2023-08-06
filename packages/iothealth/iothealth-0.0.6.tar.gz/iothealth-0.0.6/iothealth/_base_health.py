# Copyright © 2020 by IoT Spectator. All rights reserved.

"""Interface definition."""

import abc


class BaseHealth(abc.ABC):
    """Definition for common health information."""

    @classmethod
    def summary(cls) -> dict:
        """Provide the device health summary."""
        return {
            "platform": cls.device_platform(),
            "cpu_arch": cls.processor_architecture(),
            "os": cls.operating_system(),
            "processors": cls.processors(),
            "memory": cls.memory(),
            "capacity": cls.capacity(),
            "temperature": cls.temperature(),
            "cameras": cls.cameras(),
        }

    @classmethod
    @abc.abstractmethod
    def device_platform(cls) -> str:
        """Provide the device platform info."""
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def processor_architecture(cls) -> str:
        """Provide the device CPU info."""
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def operating_system(cls) -> str:
        """Provide the device OS info."""
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def processors(cls) -> dict:
        """Provice the device processors info."""
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def memory(cls) -> dict:
        """Provide the device memory info."""
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def capacity(cls) -> dict:
        """Provide the device disk usage info."""
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def temperature(cls) -> dict:
        """Provide the device temperature."""
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def cameras(cls) -> dict:
        """Provide the cameras info."""
        raise NotImplementedError()
