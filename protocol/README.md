# Astoria Protocol

*Version 1.0.0*

This document defines the protocol used for Astoria and it's various
services. This document should be used when implementing clients for
Astoria.

This document uses semantic versioning and should have changes to it
reviewed and approved appropriately to ensure that any breaking changes
are dealt with appropriately.

Where appropriate, schemas are provided alongside this document and must
be kept up to date as the protocol develops over time.

## Protocol Overview

The Astoria is an IPC mechanism between multiple independent programs
that hold individual state on a robot.

There are two categories of program that interact using the Astoria
Protocol:

-   Astoria Services  
    -   A service is a program that holds and manages its own state.
    -   The state usually reflects a *domain* that the service is
        controlling, e.g running usercode.
    -   Each service must be defined in the protocol specification.
    -   Additionally, each service has a *slug*, usually the name of the
        service.

-   Astoria Clients  
    -   A client is a program that interacts with Astoria but does not
        expose state to other programs using Astoria
    -   The client is able to read the state of services but may not
        necessarily be able to manipulate the state.
    -   A client is usually associated with a user, such as a web
        interface or command line client.

Services and clients communicate using defined message types over a
transport, defined later in this specification.

## Transport

The protocol sends and receives messages using MQTT v5. Other versions
of MQTT are not supported. Message data is encoded using JSON within the
MQTT messages.

Each message is published to a defined MQTT topic and has a QoS value of
`1`.

Each message is encoded using UTF-8. The Payload Format Indicator must
be set to `1` to indicate a UTF-8 encoded payload. The `contentType`
must be set to `application/vnd.astoria+json`.

Astoria services must set their MQTT client identifier to be the same
value as the service *slug*.

MQTT may be over TCP or a Websocket, although it is expected that
services connect to the broker using MQTT over TCP.

## Protocol Message Types

There are three IPC mechanisms defined in the Astoria Protocol:

-   State Updates
-   Request-Response
-   Streams

### State Updates

Services must publish their current state as soon as possible upon
starting and then whenever the state is changed.

The exact state that a service publishes varies per service and is
defined in the protocol specification.

Services must publish their state to the topic: `astoria/<slug>` where
`<slug>` is the defined *slug* for that service.

When a service is unavailable, it must publish an empty message to the
state topic. An empty message on the state topic must also be set as the
Last Will and Testament for the service's MQTT client.

MQTT messages for state updates should be sent with the retained flag.

The schema of a state update should be as follows:

``` json
{
    "version": "1.2.3",
    "protocol_version": "1.0.0",
    "service": "example",
    "type": "state_update",
    "state": {}
}
```

-   `protocol_version` - protocol version for the service
-   `type` - always `state_update` for state updates.
-   `service` - *slug* for the service
-   `version` - software version for the service
-   `state`- current state of the service, schema varies per service.

### Request-Response

Services may allow other services or clients to make a request against
the service.

Services must listen on the *request topic* `astoria/<slug>/request/+`
where `<slug>` is the *slug* for the service. The wildcard at the end of
the topic is for the *request slug*, a unique identifier for the
request, e.g `kill_usercode`.

A request can be made to a service by publishing a message to the
appropriate *request topic*. The message may have the MQTT *response
topic* set.

The message content for a request must be a valid JSON object. The
schema for the JSON object can vary depending on the request, and may be
an empty object if no parameters are required.

If the *response topic* is set on a request message, the service must
respond by publishing a *response message* to the *response topic*. If
no *response topic* is set, the service does not need to response, but
should still attempt to perform the requested action.

A *response topic* must be either of the format
`astoria/<slug>/response/+` or be outside of the `astoria` topic
namespace to avoid collisions.

A *response message* must be a JSON object of the following format:

``` json
{
    "protocol_version": "1.0.0",
    "type": "response",
    "service": "example",
    "version": "1.2.3",
    "success": true,
    "message": "An optional user-facing message"
}
```

-   `protocol_version` - protocol version for the service
-   `type` - always `response` for response messages.
-   `service` - *slug* for the service
-   `version` - software version for the service
-   `success`- boolean value, `true` if the request was successful,
    `false` if not.
-   `message` - optionally, a message for the user. This attribute may
    be excluded from the message.

### Streams

A stream is a series of stream messages published to a given topic. A
stream message can be published by clients or services.

A stream message must only be acted on by clients. A service should be
actioned using a request instead.

A stream message is published to `astoria/stream/<stream_slug>`. It can
be published by any component and multiple components can publish to the
same stream simultaneously.

Every stream must have a unique `stream_slug` that identifies the stream
and its purpose, e.g `usercode_log`.

A stream message must be a JSON object of the format:

``` json
{
    "protocol_version": "1.0.0",
    "type": "stream",
    "stream": "example",
    "sender": "example_sender",
    "data": {"some_data": 1}
}
```

-   `protocol_version` - protocol version
-   `type` - always `stream` for stream messages.
-   `stream` - *slug* for the stream
-   `sender`- MQTT client name of the program that published the message
-   `data` - The data for the event, varies by stream.

## Defined Services

Every service that operates as part of Astoria should be defined in this
specification.

### Disk Service

Slug: `disks`

-   Detects newly mounted disk drives
-   Detects the removal of drives
-   Communicating a list of currently mounted drives to other
    components.

#### Disk Service State

The following state is included in state update messages:

``` json
{
    "disks": {
        "<uuid>": {
            "path": "<mount_path>"
        }
    }
}
```

-   `uuid` - The UUID of the mounted disk
-   `mount_path` - The mount path of the mounted disk

Multiple disks can be included in the messages.

#### Disk Service Requests

There are three possible requests to the disks service, all of which are
primarily exist for debugging.

-   `static_disk_add`  
    -   Payload: `{"path": "/path/to/static-disk"}`
    -   Add a new static disk.

-   `static_disk_remove`  
    -   Payload: `{"path": "/path/to/static-disk"}`
    -   Remove an existing static disk.

-   `static_disk_remove_all`  
    -   Payload: `{}`
    -   Remove all existing static disks.

### Metadata Service

-   Publishes metadata information.
-   Uses state from other services to determine dynamic metadata.

#### Metadata Service State

The following state is included in state update messages:

``` json
{
    "game": {
        "arena": "A",
        "zone": 0,
        "mode": "DEV",
        "marker_offset": 0,
        "timeout": 120,
    },
    "system": {
        "kernel": "5.15",
        "arch": "aarch64",
        "python_ver": "3.9.3",
        "os_name": "MacOS",
        "os_pretty_name": "MacOS 13.0",
        "os_version": "13.0"
    },
    "wifi": {
        "region": "GB",
        "mode": "ap",
        "ap": {
            "ssid": "network",
            "psk": "password"
        }
    }
}
```

Further information on the exact values and constraints of this data can
be found in the JSON Schema included with this specification.

#### Metadata Service Requests

The following requests are available:

-   `mutate`  
    -   Payload: `{"attr": "arena", "value": "A"}`
    -   Mutate a metadata attribute to a new value.
    -   The following attributes are mutable: `arena`, `zone`, `mode`

### Usercode Service

-   Waiting for usercode drive information from the disk service
-   Starting and managing the usercode lifecycle
-   Writing logs to the usercode drive
-   Making logs available to other components in real time

#### Usercode Service State

The following state is included in state update messages:

``` json
{
    "lifecycle": {
        "status": "running",
        "pid": 1234,
        "disk": {
            "uuid": "<uuid>",
            "path": "/path/to/disk"
        }
    }
}
```

The `lifecycle` is optional and only present when there is an active
lifecycle.

-   `lifecycle.status` - The status of the lifecycle, one of:  
    -   `starting`
    -   `running`
    -   `killed`
    -   `finished`
    -   `crashed`

-   `lifecycle.pid` - The process ID of the running usercode, if
    available.

-   `lifecycle.disk.uuid` - The UUID of the usercode disk

-   `lifecycle.disk.path` - The mount path of the usercode disk

#### Usercode Service Requests

The following requests are available:

-   `kill`  
    -   Payload: `{}`
    -   Kill the usercode lifecycle, if there is one.

-   `restart`<span class="title-ref"> - Payload: </span><span class="title-ref">{}</span>\`  
    -   Restart the usercode lifecycle. If code is currently running,
        kill it first.

#### Usercode Service Streams

The usercode service publishes a stream of logs as the `usercode_log`
stream.

The data for the log stream is published in the following format:

``` json
{
    "pid": 123,
    "lineno": 0,
    "source": "stdout",
    "content": "A log line from the program"

}
```

-   `pid` - The process ID of the usercode process
-   `lineno` - The line number of the log, starting from 0.
-   `source` - The source of the log, one of `astoria`, `stdout` and
    `stderr`
-   `content` - Content of the log line.

### WiFi Service

-   Hosting a WiFi Access Point (AP) while the kit is running in
    development mode.
-   Configuring the WiFi network based on metadata.

#### WiFi Service State

The following state is included in state update messages:

``` json
{
    "ap": {
        "status": "ready"
    }
}
```

The `ap` is optional and only present when an access point is
configured.

-   `ap.status` - The status of the access point, one of:  
    -   `starting`
    -   `ready`
    -   `failed`

#### WiFi Service Requests

There are currently no service requests defined.

## Other Streams

Other than those streams defined above, the following streams are also
available:

### Usercode Trigger Stream

This event triggers the usercode and is equivalent to the start button
on a robot.

The content of this event is: `{}`.

The usercode process client waits for this event whilst it waits for the
start button.