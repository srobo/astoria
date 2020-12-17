Requirements
============

The following requirements were set out for the development of Astoria.

Minimum
-------

-  Run student code when a USB drive is inserted
-  Handle ‘Arena USBs’, herein referred to as metadata drives.
-  Make it possible for software updates to be delivered over USB
-  Provide an programmatic interface for a Web UI to receive data and
   control the robot.

Additional
----------

These requirements are above the MVP requirements, but are aimed to be
implemented too:

-  Ability to implement workaround for the PLOD bug
-  Ability to implement remote arena start mechanisms in the future
-  Live streaming of data for arena usage
-  Ability to control status LEDs (SB Power Hat style)
-  Command line interface in addition to the Web UI
-  Enable and disable the wireless interface depending on if we are in
   competition mode or not.

Technical
---------

These requirements are technical aims that have been incorporated into
the design of the solution:

-  Where possible, no ‘polling loops’, using asynchronous or
   callback-based means where possible
-  Use of off-the-shelf components where possible
-  Standards-based protocols where possible, with schemas where required
   (e.g using Pydantic)
-  Modular
-  Avoid complex protocols where we can
-  Allow integrations to be written in other languages than Python (i.e
   Web UI in JS / TS)
