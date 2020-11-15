from enum import Enum, IntFlag


class BusType(Enum):
    """An enum that indicates a type of bus. On most systems, there are
    normally two different kinds of buses running.
    """
    SESSION = 1  #: A bus for the current graphical user session.
    SYSTEM = 2  #: A persistent bus for the whole machine.
