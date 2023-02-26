Metadata
========

Astoria introduces the concept of 'metadata', used here as a specific technical term.

Metadata is a specific set of mutable and immutable data that defines the environment that the robot is running in.

Examples of metadata include: robot starting zone, development mode indicator

Metadata is managed by the :ref:`astmetad` state manager. Metadata must conform to the schema, which is defined in :class:`astoria.common.metadata.Metadata`.

Metadata Resolution
-------------------

Metadata is 'resolved' during runtime by overlaying a number of :ref:`metadata sources <metadata source>`.

All metadata attributes must be present, even if the value of an attribute is ``None``.

Sources are overlaid in priority order. The highest priority source is overlaid last such that it can override data from lower-priority sources.

For example:

- Initial metadata is generated.
    - Metadata is ``{"foo": 1, "bar": 2, "bees": "hive"}``
- First Overlay: ``{"foo": 2, "bar": 3}``
    - Metadata is ``{"foo": 2, "bar": 3, "bees": "hive"}``
- Second Overlay: ``{"bar": 0, "bees": "wasp"}``
    - Metadata is ``{"foo": 2, "bar": 0, "bees": "wasp"}``

Metadata Source
---------------

Metadata sources are of the type ``Dict[str, str]``, where the key is the name of the attr to be overridden and the value is the overriding value.

A metadata source must be defined in the code for :ref:`astmetad` and cannot be dynamically registered.

A metadata source must have a set of attributes that it is able to override. No metadata source should be able to arbitrarily override.

Any spurious attributes in the metadata source will have no effect. ``astmetad`` will give a warning though.

Currently implemented sources:

- Initial metadata generation
- :ref:`Metadata USBs`


Metadata USBs
-------------

Metadata USBs contain a high priority :ref:`Metadata Source`.

The source data should be stored in a file called ``astoria.json`` in JSON format.

There should ideally not be any other files on the Metadata USB. 

.. Caution:: If a ``robot.zip`` is placed on the Metadata USB, the robot will not recognise the Metadata USB as Astdiskd will
   recognise it as a usercode disk. See :ref:`Disk Identification` for an explanation of this process.

Example override file:

.. literalinclude:: _code/astoria.json
  :language: JSON
