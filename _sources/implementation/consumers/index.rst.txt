State Consumers
===============

A state consumer is a program that does not publish persistent data.

-  A state consumer must not hold any state information that is required
   by another entity.

   -  If this is needed for a program to function, it should be upgraded to a :ref:`state manager<state managers>`.

-  A state manager can subscribe to state information from state managers.
-  A state manager can make a mutation request to a state manager.

.. toctree::
   :maxdepth: 1
   :caption: List of State Consumers:

   astctl
   astwifid
