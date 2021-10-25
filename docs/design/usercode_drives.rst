Usercode Drives
===============

A usercode drive is a USB mass storage device containing a "code bundle", also called a ``robot.zip``.

Code Bundle Format
------------------

A Code Bundle is simply a zip file containing Python code.

The entrypoint to the Python code is ``robot.py`` and Astoria will refuse to run the code bundle if it does not exist.

Robot Settings File
-------------------

A usercode drive can also contain a ``robot-settings.toml`` file, which can be used by the user to configure their robot.

If the settings file does not already exist, it will be automatically created.

.. note:: The settings file will be ignored if the USB does not contain a code bundle.

.. literalinclude:: ../_code/robot-settings.toml
  :language: TOML

The settings file controls the WiFi network broadcast by the kit.
It contains information such as credentials and region. Region is required for compliance regions and
should be specified in accordance with ISO-3166-1 Standard and must be in ALPHA-2 format.

The ``wifi_enabled`` key should be set to ``true`` in the majority of cases, and will be overridden to ``false``
using the standard metadata mechanisms, i.e the competition USB contains a ``wifi_enabled`` key too.
