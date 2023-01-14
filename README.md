# Astoria

![Tests](https://github.com/srobo/astoria/workflows/Tests/badge.svg)
![Build and Publish docs](https://github.com/srobo/astoria/workflows/Build%20and%20Publish%20docs/badge.svg)
[![PyPI version](https://badge.fury.io/py/astoria.svg)](https://badge.fury.io/py/astoria)
[![MIT license](https://img.shields.io/badge/license-MIT-brightgreen.svg?style=flat)](https://opensource.org/licenses/MIT)
![Bees](https://img.shields.io/badge/bees-110%25-yellow.svg)

Robot Management System for Student Robotics kit.

## What does Astoria do?

Astoria is our _Robot Management System_. It manages the state of the robot and triggers actions as the state of the robot changes.

Some of the things that Astoria does include:

* Detecting USB drives.
* Running Student Code (usercode) when it is inserted on a USB drive.
* Checking the data from an arena comp-mode USB (metadata USB) and changing the behaviour of the robot.
* Turning on and off a WiFi Hotspot.
* Making data available to the [Kit UI](https://github.com/srobo/kit-ui), [kchd](https://github.com/srobo/kchd) and [Robot TUI](https://github.com/srobo/rtui).

## How does Astoria work?

Astoria provides a series of _state manager_ programs that run when the robot is turned on.

Each state manager holds state for a function of the robot and communicates its state with other state managers over [MQTT](https://en.wikipedia.org/wiki/MQTT). MQTT is a real-time pub/sub protocol often used in IoT and event-driven applications.

It is also possible for other programs to fetch the state of state managers from MQTT, make requests for a state manager to change its state and send generic events.

## Where can I find more information?

Astoria is extensively documented in the [Astoria docs](https://srobo.github.io/astoria/).

## How do I get started with development?

Developer documentation is available in the [docs](https://srobo.github.io/astoria/development/).