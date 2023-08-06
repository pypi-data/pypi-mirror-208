Health and Status Library for IoT Devices
=========================================

.. image:: https://github.com/iot-spectator/iot-health/workflows/Test/badge.svg 
    :target: https://github.com/iot-spectator/iot-health/actions?query=workflow%3ATest

.. image:: https://github.com/iot-spectator/iot-health/workflows/Linting/badge.svg
    :target: https://github.com/iot-spectator/iot-health/actions?query=workflow%3ALinting

.. image:: https://codecov.io/gh/iot-spectator/iot-health/branch/master/graph/badge.svg?token=NODdpjzGeS
    :target: https://codecov.io/gh/iot-spectator/iot-health

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

IoT Health is a library which provides the health information for supported IoT devices.


Requirements
------------
``Python 3.9`` or newer is required.


Installation
------------
There are a few ways to install ``IoT Health``. 

- Install the latest release from PyPI

.. code-block:: bash

    pip install iothealth

- Install from source

.. code-block:: bash

    git clone https://github.com/iot-spectator/iot-health.git
    cd iot-health
    pip install .


Supported Devices
-----------------
``IoT Health`` supports and tested on the following devices and platforms.

+-------------------------------------+----------------------------+
| Device                              | Operating System           |
+=====================================+============================+
| x86_64                              | Ubuntu 16, 18, 20          |
+-------------------------------------+----------------------------+
| Raspberry Pi 3 Model B Plus Rev 1.3 | Raspbian (Debian 9, 10)    |
+-------------------------------------+----------------------------+
| NVIDIA Jetson Nano                  | Jetpack 4.5 (Ubuntu 18.04) |
+-------------------------------------+----------------------------+


Usages
------
``IoT Health`` provides a convenient command line tool. After install ``IoT Health``, run ``iot-health-cli`` to launch the CLI tool.

.. code-block:: bash

    $ iot-health-cli
    Usage: iot-health-cli [OPTIONS] COMMAND [ARGS]...

    Options:
    --help  Show this message and exit.

    Commands:
    cameras
    capacity
    memory
    os-info
    platform
    processor-arch
    processors
    summary
    temperature
