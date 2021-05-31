Astmetad
========

Astmetad is responsible for:

- Waiting for :ref:`metadata drive <metadata usbs>` information from :ref:`astdiskd`
- :ref:`Resolving <Metadata Resolution>` metadata from :ref:`metadata sources <metadata source>`

See :ref:`metadata` for more information on this state manager.

Metadata Disk Lifecycle
-----------------------

When a :ref:`metadata drive <metadata usbs>` is inserted, it follows a lifecycle.

There can only be one metadata drive at any given time. Additional drives are ignored.

Once the drive has had its data loaded and validated, it will be added as a high priority :ref:`metadata source`.

Astmetad Data Structures and Classes
------------------------------------

.. autoclass:: astoria.common.messages.astmetad.MetadataManagerMessage
    :members:

.. autoclass:: astoria.common.messages.astmetad.Metadata
    :members:

.. autoclass:: astoria.common.messages.astmetad.RobotMode
    :members:
