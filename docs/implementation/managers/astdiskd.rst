Astdiskd
========

Astdiskd is responsible for:

- Detecting newly mounted disk drives
- Detecting the removal of drives
- Communicating a list of currently mounted drives to other components.

Drive Detection
---------------

Astdiskd communicates with `UDisks 2 <https://www.freedesktop.org/wiki/Software/udisks/>`_  over `DBus <https://www.freedesktop.org/wiki/Software/dbus/>`_
to receive information about the mounted volumes on the system.

On startup, it reads disk information from the UDisks managed objects at ``/org/freedesktop/UDisks2/block_devices/``.

It listens for job signals in the path ``/org/freedesktop/UDisks2/jobs/``, dispatching a task if the job is ``filesystem-mount`` or ``cleanup``.

This relies on another program automatically mounting drives that are inserted, and ensuring that DBus notices them. `UDiskie 2 <https://github.com/coldfix/udiskie>`_ is recommended.

`DFeet <https://wiki.gnome.org/Apps/DFeet>`_ is useful for observing and debugging the DBus interactions. `Python-dbus-next <https://github.com/altdesktop/python-dbus-next>`_ is the pure-python library that is used to communicate with DBus.

Astdiskd Data Structures and Classes
------------------------------------

.. autoclass:: astoria.astdiskd.DiskManager
    :members:

.. autoclass:: astoria.common.disks.DiskUUID
    :members:

.. autoclass:: astoria.common.disks.DiskInfo
    :members:

.. autoclass:: astoria.common.ipc.DiskManagerMessage
    :members:
