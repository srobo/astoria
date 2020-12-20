IPC
===

Astoria uses Inter-Process Communications (IPC) to communicate events and data between components.

Communications
--------------

Components exchange information using JSON messages over MQTT, a pub/sub protocol. All messages should conform
to a defined schemas, and should be rejected by the receiving component if it does not conform.

An MQTT broker will need to be run on the robot to faciliate this messaging. It should listen on both TCP and Websockets, so that the Web UI can communicate without an additional proxy in the middle.

The retained message flag should be used such that information is available immediately after subscribing to a topic on 
the broker. This means that subscribers do not need to wait for the next publication to receive any information. 

Message Types
-------------

There are currently two classes of message.

Manager Messages
~~~~~~~~~~~~~~~~

A manager message contains information about the status of a manager and it's current state.

Published on ``astoria/[manager_name]``

Based on the ``ManagerMessage`` class, must contain at least:

- ``astoria_version`` - The version of astoria that is running on the manager.
- ``status``: ``"RUNNING"`` or ``"STOPPED"`` - Used to allow / disallow running of dependent components.

It should be ensured that the last will and testament of the client is used to change the status to "STOPPED" 
so that clients are alerted to the disconnection. The state should also be cleared to a safe state. 

Mutation Requests
~~~~~~~~~~~~~~~~~

Mutation requests have not yet been implemented or formally defined.