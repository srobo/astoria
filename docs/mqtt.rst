MQTT
====

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

There are currently three classes of message.

Manager Messages
~~~~~~~~~~~~~~~~

A manager message contains information about the status of a :ref:`state manager <state managers>` and it's current state.

Published on ``astoria/[manager_name]``

Based on the ``ManagerMessage`` class, must contain at least:

- ``astoria_version`` - The version of astoria that is running on the manager.
- ``status``: ``"RUNNING"`` or ``"STOPPED"`` - Used to allow / disallow running of dependent components.

It should be ensured that the last will and testament of the client is used to change the status to "STOPPED" 
so that clients are alerted to the disconnection. The state should also be cleared to a safe state. 

Manager Requests
~~~~~~~~~~~~~~~~~

A *Manager Request* is a message sent to a single, specific :ref:`state manager <state managers>` to request a single specific action.

A :class:`ManagerRequest <astoria.common.ipc.ManagerRequest>` is published to ``astoria/[manager_name]/request/[request]`` by the requesting component.

A request must contain a UUID that is unique to the request.

A request can also contain additional information related to that request.

After a state manager receives a request, it must reply with a :class:`RequestResponse <astoria.common.ipc.RequestResponse>`. The UUID in the response must match the UUID of the request.

Mutation responses are published to ``astoria/[manager_name]/request/[request]/[uuid]``

.. autoclass:: astoria.common.ipc.ManagerRequest
    :members:

.. autoclass:: astoria.common.ipc.RequestResponse
    :members:

Broadcast Events
~~~~~~~~~~~~~~~~

A *Broadcast Event* is a message sent to all components to signify an event occuring.

A BroadcastEvent is published to ``astoria/broadcast_event/[event_name]``. It can be published by any component and multiple components can broadcast the same event simultaneously.

Every *Broadcast Event* must have a unique ``event_name`` that identifies the event and its purpose.

A *Broadcast Event* must also contain a priority and the compenent that originated the event.

Broadcast Events can be sent using the BroadcastHelper class.
