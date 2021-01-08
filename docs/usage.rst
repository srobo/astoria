Usage
=====

Astoria is designed to be deployed on robots that do not have a traditional keyboard or mouse interface. This page describes
the requirements for it to be deployed on such a system. Reference to packages available in Debian Buster will be made,
although it is possible for Astoria to be deployed on any Linux system.

System Requirements
-------------------

- Python 3.6 + library Requirements
- DBus
- UDisks 2
- UDiskie (should be run as the same user as Astoria)
    - It is possible to use other automounting programs, as long as they are compatible with UDisks
- MQTT Broker supporting MQTT 3 or later. Mosquitto is recommended

Astoria is targeted for Linux-based OSes, although it may be possible to run on other POSIX-compatible operating systems.

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

You can run ``astctl event`` to see what data is currently published.

Metadata USBs
-------------

Metadata USBs contain a high priority :ref:`Metadata Source`.

The source data should be stored in a file called ``astoria.json`` in JSON format.

There should ideally not be any other files on the Metadata USB. 

.. Caution:: If a ``robot.zip`` is placed on the Metadata USB, the robot will not recognise the Metadata USB.

Example override file:

.. literalinclude:: _code/astoria.json
  :language: JSON
