Getting Started
===============

System Requirements
-------------------

- Python 3.8 or later
- Python Library Requirements
- DBus
- UDisks 2
- UDiskie (should be run as the same user as Astoria)
    - It is possible to use other automounting programs, as long as they are compatible with UDisks
- MQTT Broker supporting MQTT 3 or later. Mosquitto is recommended

Astoria is targeted for Linux operating systems, although it is also possible to run most functionality on MacOS. Windows is not supported and we recommend using Docker for development on Windows.

Configuration
-------------

Astoria is configured using the ``astoria.toml`` config file. All components will look for this config file and the location can be specified using the ``-c`` command line option.

.. literalinclude:: ../astoria.toml
  :language: TOML


Running
-------

State Managers should be installed in the path once the package is installed.

For the recommended setup, you will need to run at least ``astdiskd``, ``astmetad`` and ``astprocd``.

The state managers should be managed using systemd in a proper deployment, although that is outside of the scope of this documentation. ``tmux`` is good for testing.

Command Line Usage
------------------

.. click:: astoria.astctl:main
   :prog: astctl
   :nested: short
