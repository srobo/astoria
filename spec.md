# Astoria Draft Specification

This specification lays out a draft for a modular robot management daemon, proposed name [Astoria](https://en.wikipedia.org/wiki/Astoria,_Oregon#In_popular_culture_and_entertainment).

## Background

- herdsman
- runusb
- shepherd
- pepper2

## Introduction

- Use JSON over MQTT (or equivalent pub / sub system, preferably with websocket support)
- No central daemon, astoria is more of a protocol with defined modules

## State Managers

A state manager is a daemon that publishes data about it's state.

The state may mutate, and is retained by the broker.

Needs to have MQTT last will to set status as "STOPPED" for safety, which other components should fail-safe upon.

### astdiskd

astdiskd - Astoria Disk Daemon

Publishes data about connected USB drives.

Responsible for detecting drives and determining what to do with them.

Publishes to:

- /astoria/disk/status
- /astoria/disk/disks/DISK-ID 

Subscribes to None

### `astprocd`

astprocd - Astoria Process Daemon

Responsible for executing and logging usercode.

Listens to astdiskd, looking for new usercode disks.

Listens for start / kill code requests.

Publishes to:

- /astoria/proc/status
- /astoria/proc/log
- /astoria/proc/request/result (publishes success / fail of request)

Subscribes to:

- /astoria/disk/status
- /astoria/disk/disks/+
- /astoria/proc/request (execute / kill usercode requests, depends on code state)

### `astmetad`

astmetad - Astoria Metadata Daemon

Responsible for holding state of metadata.

Two types of metadata:

- user mutable, can be mutated over MQTT e.g START_STATE
- user immutable, can only be mutated by astmetad e.g ARENA, USERCODE_DIR

Only pre-defined metadata is allowed.

Publishes to:

- /astoria/meta/status
- /astoria/meta/data
- /astoria/meta/mutate/result (publishes success / fail of mutation)

Subscribes to:
- /astoria/disk/status
- /astoria/disk/disks/+
- /astoria/meta/mutate - allows consumers to change user-mutable metadata.

## State consumers

No state consumers are vital to the functioning of the system at a basic level.

### `astusercode`

The robot usercode accesses metadata for consumption via the API.

This is not an independent process, but is part of `sr-robot3`.

Subscribes to:

- /astoria/meta/data

### `astctl`

Command line utility to debug the system

Subscribes to:

- '#'

Publishes to:

- /astoria/proc/request
- /astoria/meta/mutate

### `astleds`

Controls status LEDs (e.g for [Pi Power Hat](https://docs.sourcebots.co.uk/en/latest/kit/pi.html#power-hat)).

Subscribes to:

- /astoria/proc/status

### Future

- Web Interface
- Remote Start
- Servohack
- Update Manager