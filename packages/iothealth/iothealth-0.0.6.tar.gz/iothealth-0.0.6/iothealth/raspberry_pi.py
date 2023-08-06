# Copyright © 2020 by IoT Spectator. All rights reserved.

"""Raspberry Pi health information."""

import re
import shutil
import subprocess

from iothealth import linux


class RaspberryPi(linux.Linux):
    """Check Raspberry Pi health and status."""

    # Override
    @classmethod
    def device_platform(cls) -> str:
        """Get the IoT device platform.

        Returns
        -------
        `str`
            An empty string is returned if the platform is unknown.
            Otherwise, return the device platform info, e.g.,
            `Raspberry Pi 3 Model B Plus Rev 1.3`.
        """
        result = subprocess.run(
            ["cat", "/sys/firmware/devicetree/base/model"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.stderr:
            return str()
        return result.stdout.decode("utf-8").strip()

    # Override
    @classmethod
    def temperature(cls) -> dict:
        """Get the device's temperature.

        Returns
        -------
        float
            The device temperature, e.g., 54.8.
            The temperature unit is Celsius.

        Raises
        ------
        `RuntimeError`
            Raised if the temperature info is not available.
        """
        VCGENGCMD = "vcgencmd"
        vcgencmd_path = shutil.which(VCGENGCMD)

        if not vcgencmd_path:
            raise RuntimeError(f"No {VCGENGCMD} command found.")

        result = subprocess.run(
            [vcgencmd_path, "measure_temp"],
            capture_output=True,
            text=True,
        )
        if not result.stderr:
            temp = re.search("\\d+\\.\\d+", result.stdout)
            if temp:
                return {"chip": temp.group(0)}

        return {}

    # Override
    @classmethod
    def cameras(cls) -> dict:
        """Provide the cameras info."""
        return {}
