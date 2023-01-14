Usercode Drives
===============

A usercode drive is a USB mass storage device containing a Python file, usually ``robot.py``.

Entrypoint
----------

The entrypoint to the Python code is usually ``robot.py``. However, this can be configured in ``astoria.toml``.

The entrypoint is executed in a subprocess in unbuffered mode, usually ``python3 -u robot.py``.

You can change the entrypoint in the robot settings file.

Robot Settings File
-------------------

A usercode drive can also contain a ``robot-settings.toml`` file, which can be used by the user to configure their robot.

If the settings file does not already exist, it will be automatically created.

.. note:: The settings file will be ignored if the USB does not contain a code bundle.

.. literalinclude:: ../_code/robot-settings.toml
  :language: TOML

Entrypoint Setting
~~~~~~~~~~~~~~~~~~

You can override the entrypoint in the settings file by changing the value of ``usercode_entrypoint``.

WiFi Settings
~~~~~~~~~~~~~

The settings file controls the WiFi network broadcast by the kit.
It contains information such as credentials and region. Region is required for compliance regions and
should be specified in accordance with [ISO-3166-1 Standard and must be in ALPHA-2 format](https://en.wikipedia.org/wiki/ISO_3166-2#Current_codes).

The ``wifi_enabled`` key should be set to ``true`` in the majority of cases, and will be overridden to ``false``
using the standard metadata mechanisms, i.e the competition USB contains a ``wifi_enabled`` key too.
