Background
==========

Astoria is not the first "Robot Management System" and takes heavy inspiration from it's predecessors.

Herdsman
--------

Herdsman is the original equivalent to Astoria for the SRv4 kit. It uses WAMP and HTTP for communication.

runusb
------

Developed by SourceBots, runusb is a simple python script that executes Python on an inserted USB drive.

It also had partial support for installing system updates.

Code execution was isolated in a systemd-nspawn container originally, but this only worked with robotd.

Shepherd
--------

Developed for HR Robocon. Not open source.

pepper2
-------

Prototype. Uses DBus for all comms. A port to HTTP was started but then superceded by Astoria.

Less modular.