Astoria
=======

Robot Management System for Student Robotics 2022 kit.

.. toctree::
   :maxdepth: 1
   :caption: Documentation:

   design/index
   development

System Requirements
-------------------

- Python 3.6 + python library Requirements
- DBus
- UDisks 2
- Udiskie (should be run as the same user as Astoria)
- MQTT Broker supporting MQTT 3 or later

Astoria is targeted for Linux-based OSes, although it may be possible to run on other POSIX-compatible operating systems.

Configuration
-------------

Astoria is configured using the ``astoria.toml`` config file. All components will look for this config file and the location can be specified using the ``-c`` command line option.

.. literalinclude:: ../astoria.toml
  :language: TOML

Manager Dependencies
--------------------

Some managers are dependent on data from other managers, so will wait for their dependencies to become available.
