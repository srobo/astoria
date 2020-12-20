State Managers and Consumers
============================

Astoria has exactly two types of entity within the architecture: State Managers and State Consumers.

Every component and process that interacts with Astoria must take one of these roles.

State Managers
--------------

A state manager is a process that stores and mutates some state.

-  A state manager must publish it’s state to MQTT when the state
   changes.
-  A state manager must publish the status of the state manager.
-  A state manager should be run as a daemon process.
-  A state manager can subscribe to other state managers.
-  A state manager can allow the mutation of it’s state by a state
   consumer.

State Consumers
---------------

A state consumer is a program that does not publish persistent data.

-  A state manager must not hold any state information that is required
   by another entity.

   -  If this is needed for a program to function, it should be upgraded
      to a state manager.

-  A state manager can subscribe to state information from state
   managers
-  A state manager can make a mutation request to a state manager.
