Usage
=====

This page is a work in progress and details the usage of Astoria.

Metadata USBs
-------------

Metadata USBs contain overrides for the metadata.

The override data should be stored in a file called ``astoria.json`` in JSON format.

There should ideally not be any other files on the Metadata USB. If a ``robot.zip`` is placed on the USB, it will cause interference.

Example override file:

.. literalinclude:: _code/astoria.json
  :language: JSON
