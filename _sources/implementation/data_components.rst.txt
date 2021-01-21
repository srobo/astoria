Data Components
===============

A data component represents the common functionality between
State Managers and Consumers. It handles connecting to the broker
and managing the event loop.

Every standalone application in Astoria must be a Data Component.

The entrypoint of any data component is the ``run`` function.

Callbacks
---------

The data component superclass will call various methods at different stages that can be overriden to customise behaviour.

- ``_pre_connect`` - Called before MQTT connection
- ``_post_connect`` - Called after MQTT connection
- ``_pre_disconnect`` - Called before MQTT disconnection
- ``_post_disconnect`` - Called after MQTT disconnection
