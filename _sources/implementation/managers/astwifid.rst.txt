Astwifid
========

Astwifid is responsible for:

- Hosting a WiFi Access Point (AP) while the kit is running in development mode.
- Configuring the WiFi network based on code bundle information.
- Caching of WiFi configuration to allow the network to come up after a restart without the presence of a Usercode USB.

It is not responsible for handling any networking components such as DHCP. These are to be handled by the operating system.

Hostapd is used to create the WiFi hotspot and uses a configuration that is dynamically generate and stored in ``/tmp``.
Hostapd is then launched as a child process of the astwifid process. This is managed via the ``asyncio.subprocess`` module.

 - Metadata is received from ref:`astmetad`
 - If ``wifi_enabled`` is True and other data is provided (``ssid``, ``psk``, ``region``), then the hotspot is started.
 - If the metadata changes, the hotspot will automatically restarted with updated credentials if required.
 - If ``wifi_enabled`` changes to False, then the hotspot will be killed.

Astwifid Data Structures and Classes
------------------------------------

.. autoclass:: astoria.common.ipc.WiFiManagerMessage
   :members:

.. autoclass:: astoria.astwifid.WiFiHotspotLifeCycle
   :members:
