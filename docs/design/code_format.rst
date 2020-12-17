Code Bundle Format
==================

``robot.zip`` format spec

zip file containing:

- ``main.py`` - code entrypoint
- ``bundle.toml``
    - ``bundle version``- SemVer of bundle specification
    - ``target kit name`` - String identifying the kit image name
    - ``target kit version`` - SemVer with Epoch identifying the kit image version.
        - Compared against version in ``astoria.toml``
        - If epoch or major different, refuse to run.
        - If minor different, warn that the robot needs updating, and is out of support.
        - If patch different, warn that the robot needs updating. Always run code.
    - ``wifi_ssid`` - SSID of WiFi network
    - ``wifi_password`` - Password to WiFi network

- Check if info.yaml or wifi.yaml are present. If so, reject.

Example:

.. code-block:: toml

    [bundle]
    version = "2.0.0"

    [kit]
    target = "Student Robotics"
    version = "2022.1.0.0"

    [wifi]
    ssid = "robot-ABC"
    password = "beeeeees"