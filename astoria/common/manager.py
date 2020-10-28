"""Common code for manager daemons."""
import atexit
import logging
from abc import ABCMeta, abstractmethod
from signal import SIGHUP, SIGINT, SIGTERM, Signals, signal
from types import FrameType

from systemd.daemon import notify

from astoria import __version__

LOGGER = logging.getLogger(__name__)


class ManagerDaemon(metaclass=ABCMeta):
    """A manager daemon."""

    def __init__(self, verbose: bool) -> None:
        if verbose:
            logging.basicConfig(
                level=logging.DEBUG,
                format=f"%(asctime)s {self.name} %(name)s %(levelname)s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        else:
            logging.basicConfig(
                level=logging.INFO,
                format=f"%(asctime)s {self.name} %(levelname)s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        LOGGER.info(f"{self.name} v{__version__} - {self.__doc__}")

        self._running = True
        self.init()

        atexit.register(lambda: self.halt() if self._running else None)
        signal(SIGHUP, self._signal_halt)
        signal(SIGINT, self._signal_halt)
        signal(SIGTERM, self._signal_halt)

    def init(self) -> None:
        """Initialisation of the manager."""
        LOGGER.debug("Initialising manager")
        self._init()

    @abstractmethod
    def _init(self) -> None:
        """Initialisation of the manager."""
        raise NotImplementedError

    def run(self) -> None:
        """
        Run the daemon.

        Should be a blocking call, as the daemon loops.
        """
        notify("READY=1")
        LOGGER.info("Ready")
        self._run()

    @abstractmethod
    def _run(self) -> None:
        """
        Run the daemon.

        Should be a blocking call, as the daemon loops.
        """
        raise NotImplementedError

    def halt(self) -> None:
        """
        Halt the daemon.

        Should stop the daemon safely.
        """
        self._running = False
        notify("STOPPING=1")
        LOGGER.debug("Halting")
        self._halt()
        LOGGER.info("Halted")

    @abstractmethod
    def _halt(self) -> None:
        """
        Halt the daemon.

        Should stop the daemon safely.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the daemon."""
        raise NotImplementedError

    def _signal_halt(self, signal: Signals, __: FrameType) -> None:
        LOGGER.debug(f"Received {Signals(signal).name}, triggering halt")
        self.halt()
