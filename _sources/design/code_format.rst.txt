Code Bundle Format
==================

``robot.zip`` format spec

zip file containing:

- ``main.py`` - code entrypoint
- ``bundle.toml`` - code bundle information file

**Check if info.yaml or wifi.yaml are present. If so, reject.**

Example:

.. code-block:: toml

    [bundle]
    version = "2.0.0"

    [kit]
    name = "Student Robotics"
    version = "2022.1.0.0"

    [wifi]
    ssid = "robot-ABC"
    psk = "beeeeees"
    enabled = true
    region = "GB"

Kit version
-----------

The kit version should be matched using the following regular expression:

``^(\d+)\.(\d+)\.(\d+)\.(\d+)(dev)?(?::([0-9a-f]{5,40})(?:@(\w+))?)?$``

The capture groups in the regex are named as follows:

- ``epoch`` - SR competition year
- ``major`` - Increment on breaking changes
- ``minor`` - Increment on non-breaking changes
- ``patch`` - Increment on bug fixes
- ``dev``   - Development Indicator.
- ``hash``  - Git hash of the commit that the kit image was built from. Long or short hash format can be used.
- ``branch``- Git branch of the commit that the kit image was built from

- The version in the code bundle is compared to ``kit.version`` in ``astoria.toml``

    - If epoch is different, refuse to run.
    - If major or minor is different, warn that the robot needs updating, and is out of support. Always run code.
    - If patch is different, warn that the robot needs updating. Always run code.
    - If using a development build, warn the user.

Kit Version Examples
~~~~~~~~~~~~~~~~~~~~

- ``2021.1.0.0`` - Public release

Test Releases: e.g sent to volunteers or students to test something. 

``2021.1.0.2:534912@master``
``2021.1.0.2:534912``

Development Release: Builds that are not sent outside of the kit development team

``2021.1.0.0dev`` - Development release based on version, at unknown branch
``2021.1.0.2dev:53491266d26fcb504eb4b1d9108de04899832c83``
``2021.1.0.2dev:53491266d26fcb504eb4b1d9108de04899832c83@master``
``2021.1.0.2dev:534912@master``

Kit Name
--------

The kit name is an identifier for the kit build series.

If the kit name in ``astoria.toml`` doesn't match the kit name in the code bundle, the code will not run.

WiFi
----

The ``wifi`` section controls the WiFi network broadcast by the kit.
It contains information such as credentials and region. Region is required for compliance regions and
should be specified in accordance with ISO-3166-1 Standard and must be in ALPHA-2 format.

The ``enabled`` key should be set to ``true`` in the majority of cases, and will be overridden to ``false``
using the standard metadata mechanisms, i.e the competition USB contains a ``enabled`` key too.
