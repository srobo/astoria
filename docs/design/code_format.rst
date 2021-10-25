Code Bundle Format
==================

``robot.zip`` format spec

zip file containing:

- ``robot.py`` - code entrypoint

WiFi
----

The ``wifi`` section controls the WiFi network broadcast by the kit.
It contains information such as credentials and region. Region is required for compliance regions and
should be specified in accordance with ISO-3166-1 Standard and must be in ALPHA-2 format.

The ``enabled`` key should be set to ``true`` in the majority of cases, and will be overridden to ``false``
using the standard metadata mechanisms, i.e the competition USB contains a ``enabled`` key too.
