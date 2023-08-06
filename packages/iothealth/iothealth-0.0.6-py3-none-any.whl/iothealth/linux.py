# Copyright © 2020 by IoT Spectator. All rights reserved.

"""General Linux health info on x86 platform."""

import platform
import shutil
import subprocess

import psutil

from iothealth import _base_health


class Linux(_base_health.BaseHealth):
    """Health information for general Linux devices."""

    # Override
    @classmethod
    def device_platform(cls) -> str:
        """Get the system information.

        Returns
        -------
        `str`
            An empty string is returned if the platform is unknown.
            Otherwise, return the device platform info.
        """
        result = subprocess.run(
            ["cat", "/proc/version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if result.stderr:
            return str()
        return result.stdout.decode("utf-8").strip()

    # Override
    @classmethod
    def processor_architecture(cls) -> str:
        """Get the processor architecture.

        Returns
        -------
        `str`
            An empty string is returned if the processor architecture is
            unknown. Otherwise, return the processor type, e.g., `x86_64`.
        """
        return platform.processor()

    # Override
    @classmethod
    def operating_system(cls) -> str:
        """Get the OS info.

        Returns
        -------
        `str`
            An empty string is returned if the OS is unknown.
            Otherwise, return the processor type, e.g., `Linux`.
        """
        return platform.system()

    # Override
    @classmethod
    def processors(cls) -> dict:
        """Get the detail processor information as JSON format.

        Returns
        -------
        `dict`
            The detail information is as the following format:
        .. code-block:: JSON
            {
                "physical_cores": 4,
                "total_cores": 4,
                "max_frequency": 1400.00,
                "min_frequency": 600.00,
                "current_frequency": 1400.00,
                "usage_per_core": [
                    {
                        "core": 0,
                        "usage": 0.2
                    },
                    {
                        "core": 1,
                        "usage": 0.0
                    },
                    {
                        "core": 2,
                        "usage": 0.0
                    },
                    {
                        "core": 3,
                        "usage": 0.0
                    }
                ],
                "total_usage": 0.1
            }
        """
        frequency = psutil.cpu_freq()
        usages = list()
        for index, usage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
            each_cpu = {"core": index, "usage": usage}
            usages.append(each_cpu)

        result = {
            "physical_cores": psutil.cpu_count(logical=False),
            "total_cores": psutil.cpu_count(logical=True),
            "max_frequency": frequency.max,
            "min_frequency": frequency.min,
            "current_frequency": frequency.current,
            "usage_per_core": usages,
            "total_usage": psutil.cpu_percent(),
        }
        return result

    # Override
    @classmethod
    def memory(cls) -> dict:
        """Get virtual memory usage in bytes.

        Returns
        -------
        `dict`
            Usages returned as a `dictionary` with keys `total`, `available`,
            and `used`.
        """
        result = psutil.virtual_memory()
        return {
            "total": result.total,
            "available": result.available,
            "used": result.used,
        }

    # Override
    @classmethod
    def capacity(cls) -> dict:
        """Get the current disk capacity usage in bytes.

        Returns
        -------
        `dict`
            Usages returned as a `dictionary` with keys `total`, `available`,
            and `used`.
        """
        result = shutil.disk_usage("/")
        return {"total": result.total, "available": result.free, "used": result.used}

    # Override
    @classmethod
    def temperature(cls) -> dict:
        """Provide the device temperature."""
        thermal_zone_path = "/sys/devices/virtual/thermal/thermal_zone"
        zone_temps = {}
        for zone_number in range(0, 6):
            zone_dir = thermal_zone_path + str(zone_number)
            zname = subprocess.run(
                ["cat", zone_dir + "/type"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if zname.stderr:
                continue
            ztemp = subprocess.run(
                ["cat", zone_dir + "/temp"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if ztemp.stderr:
                continue
            zone_temps[zname.stdout.decode("utf-8").strip()] = ztemp.stdout.decode(
                "utf-8"
            ).strip()
        return zone_temps

    # Override
    @classmethod
    def cameras(cls) -> dict:
        """Provide cameras information."""
        return {}
