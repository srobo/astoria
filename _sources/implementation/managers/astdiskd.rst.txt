Astdiskd
========

Astdiskd is responsible for:

- Detecting newly mounted disk drives
- Detecting the removal of drives
- Determining if and how the drive is relevant to Astoria
- Communicating a list of currently mounted drives to other components.

Drive Detection
---------------

Astdiskd communicates with `UDisks 2 <https://www.freedesktop.org/wiki/Software/udisks/>`_  over `DBus <https://www.freedesktop.org/wiki/Software/dbus/>`_
to receive information about the mounted volumes on the system.

On startup, it reads disk information from the UDisks managed objects at ``/org/freedesktop/UDisks2/block_devices/``.

It listens for job signals in the path ``/org/freedesktop/UDisks2/jobs/``, dispatching a task if the job is ``filesystem-mount`` or ``cleanup``.

This relies on another program automatically mounting drives that are inserted, and ensuring that DBus notices them. `UDiskie 2 <https://github.com/coldfix/udiskie>`_ is recommended.

`DFeet <https://wiki.gnome.org/Apps/DFeet>`_ is useful for observing and debugging the DBus interactions. `Python-dbus-next <https://github.com/altdesktop/python-dbus-next>`_ is the pure-python library that is used to communicate with DBus.

Disk Identification
-------------------

After a disk has been detected, the type of disk also needs to be identified. A disk can only have one type, the value of which must be a member of :class:`astoria.common.disks.DiskType`.

Given the mount path for a disk, the type of the disk can be found using the :meth:`astoria.common.disks.DiskType.determine_disk_type` method.

The path is compared against a :class:`astoria.common.disks.constraints.Constraint` for each type. The type that is returned will be the first type for which the constraint matches.

As a disk must always have a type, the last constraint in the list is `DiskType.NOACTION`, which is matched using a :class:`astoria.common.disks.constraints.TrueConstraint`.

Constraints
~~~~~~~~~~~

A constraint is a class that implements :class:`astoria.common.disks.constraints.Constraint`. Given a path, a constaint will determine if the path matches the constraint or not.

Some constraints, such as :class:`astoria.common.disks.constraints.AndConstraint` take other constraints as parameters in the constructor. This allows us to combine constraints programmatically.

A full list of available constraints, along with their uses is listed in :ref:`Constraint Definitions`.

Astdiskd Data Structures and Classes
------------------------------------

.. autoclass:: astoria.astdiskd.DiskManager
    :members:

.. autoclass:: astoria.common.disks.DiskUUID
    :members:

.. autoclass:: astoria.common.disks.DiskInfo
    :members:

.. autoclass:: astoria.common.disks.DiskType
    :members:

.. autoclass:: astoria.common.ipc.DiskManagerMessage
    :members:

Constraint Definitions
----------------------

.. autoclass:: astoria.common.disks.constraints.Constraint
    :members:

.. autoclass:: astoria.common.disks.constraints.FilePresentConstraint
    :members:

.. autoclass:: astoria.common.disks.constraints.NumberOfFilesConstraint
    :members:

.. autoclass:: astoria.common.disks.constraints.OrConstraint
    :members:

.. autoclass:: astoria.common.disks.constraints.AndConstraint
    :members:

.. autoclass:: astoria.common.disks.constraints.NotConstraint
    :members:

.. autoclass:: astoria.common.disks.constraints.TrueConstraint
    :members:

.. autoclass:: astoria.common.disks.constraints.FalseConstraint
    :members: