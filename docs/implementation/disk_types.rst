Disk Types
==========

Whilst :ref:`astdiskd` is responsible for detecting what disks are attached to the system, it is the responsibility of each individual :ref:`data component` to determine if a disk is relevant to Astoria.

Disks are sorted into one of a few relevant types:

- Usercode
- Metadata
- Update
- No Action

Disk Identification
-------------------

A disk can only have one type, the value of which must be a member of :class:`astoria.common.disks.DiskType`.

Given the mount path for a disk, the type of the disk can be found using :class:`astoria.common.disks.DiskTypeCalculator`.

The path is compared against a :class:`astoria.common.disks.constraints.Constraint` for each type. The type that is returned will be the first type for which the constraint matches.

As a disk must always have a type, the last constraint in the list is `DiskType.NOACTION`, which is matched using a :class:`astoria.common.disks.constraints.TrueConstraint`.

Constraints
~~~~~~~~~~~

A constraint is a class that implements :class:`astoria.common.disks.constraints.Constraint`. Given a path, a constaint will determine if the path matches the constraint or not.

Some constraints, such as :class:`astoria.common.disks.constraints.AndConstraint` take other constraints as parameters in the constructor. This allows us to combine constraints programmatically.

A full list of available constraints, along with their uses is listed in :ref:`Constraint Definitions`.

Disk Type Classes
-----------------

.. autoclass:: astoria.common.disks.DiskType
    :members:

.. autoclass:: astoria.common.disks.DiskTypeCalculator
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