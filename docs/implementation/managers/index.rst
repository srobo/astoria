State Managers
==============

.. toctree::
   :maxdepth: 1
   :caption: List of State Managers:

   astdiskd
   astmetad
   astprocd
   astwifid

A state manager is a process that stores and mutates some state.

-  A state manager must publish its state to MQTT when the state
   changes.
-  A state manager must publish the status of the state manager.
-  A state manager should be run as a daemon process.
-  A state manager can subscribe to other state managers.
-  A state manager can allow the mutation of it’s state by a :ref:`state consumer <state consumers>`.

Manager Dependencies
--------------------

Some managers are dependant on data from other managers, so will wait for their dependencies to become available.

Minimal State Manager
---------------------

.. literalinclude:: ../../_code/asttestd.py
  :language: Python
