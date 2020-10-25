"""Disk Manager Application."""

import logging
from pathlib import Path
from time import sleep
from typing import Dict, List

import click
from gi.repository import GLib
from pydbus import SystemBus

from astoria.common.manager import ManagerDaemon
from astoria.common.messages.disk import DiskUUID

LOGGER = logging.getLogger(__name__)


@click.command("astdiskd")
@click.option("-v", "--verbose", is_flag=True)
def main(*, verbose: bool) -> None:
    """Disk Manager Application Entrypoint."""
    diskd = DiskManager(verbose)

    diskd.run()


class DiskManager(ManagerDaemon):
    """Astoria Disk Manager."""

    name = "astdiskd"

    def _init(self) -> None:
        self._loop = GLib.MainLoop()
        self._udisks = UdisksConnection()

    def _run(self) -> None:
        self._loop.run()

    def _halt(self) -> None:
        self._udisks.disconnect()
        self._loop.quit()


class UdisksConnection:
    """Connect and communicate with UDisks2."""

    DBUS_PATH: str = ".UDisks2"

    def __init__(self) -> None:
        self._bus = SystemBus()

        try:
            self._bus.get(self.DBUS_PATH).Ping()
        except GLib.Error:
            raise Exception("Unable to connect to UDisks2 over DBus")

        self._drives: Dict[DiskUUID, Path] = {}

        self._disk_signal_handler = self._bus.get(self.DBUS_PATH).InterfacesAdded.connect(
            self._disk_signal,
        )

        self._detect_initial_drives()

    def disconnect(self) -> None:
        """Disconnect."""
        LOGGER.debug("Disconnecting DBus signal handler")
        self._disk_signal_handler.disconnect()

    def _bytes_to_path(self, data: List[int]) -> Path:
        """Convert a null terminated int array to a path."""
        # Data is null terminated.
        mount_point = data[:len(data) - 1]

        chars = [chr(x) for x in mount_point]
        mount_point_str = "".join(chars)

        return Path(mount_point_str)

    def _disk_signal(self, path: str, data: Dict[str, Dict[str, str]]) -> None:
        """Handle a disk signal event from UDisks2."""
        LOGGER.debug(f"Received event from {path}")

        if path.startswith("/org/freedesktop/UDisks2/jobs/"):
            for job in data.keys():
                event_data = data[job]
                if "Operation" in event_data.keys():
                    if event_data["Operation"] == "filesystem-mount":
                        LOGGER.debug(f"Mount Event detected at {path}")
                        sleep(0.3)
                        self._handle_mount_event(event_data)

                    if event_data["Operation"] == "cleanup":
                        LOGGER.debug(f"Removal Event detected at {path}")
                        sleep(0.3)
                        self._handle_cleanup_event(event_data)

    def _handle_mount_event(self, event_data: Dict[str, str]) -> None:
        """Handle a mount event."""
        if 'Objects' in event_data.keys() and len(event_data["Objects"]) > 0:
            disk_bus_path = event_data["Objects"][0]
            block_device = self._bus.get(self.DBUS_PATH, disk_bus_path)
            mount_points = block_device.MountPoints
            if len(mount_points) > 0:
                # We are only interested in the first mountpoint.
                mount_point = mount_points[0]
                mount_path = self._bytes_to_path(mount_point)

                if mount_path.exists() and mount_path.is_dir():
                    uuid = DiskUUID(block_device.IdUUID)
                    if uuid not in self._drives.keys():
                        LOGGER.info(f"Drive {uuid} mounted ({mount_path})")
                        self._drives[uuid] = mount_path
                    else:
                        LOGGER.error(f"Drive UUID collision! uuid={uuid}")
                else:
                    LOGGER.warning(f"Invalid mount path: {mount_path}")
            else:
                LOGGER.warning(
                    f"No mountpoints available for {disk_bus_path}",
                )
        else:
            LOGGER.warning("No information on drive available. Aborting.")

    def _handle_cleanup_event(self, _: Dict[str, str]) -> None:
        """Handle a cleanup event."""
        # We have no information to tell which drive left.
        # Thus we need to check.
        removed_drives: List[DiskUUID] = []
        for uuid, path in self._drives.items():
            if not path.exists():
                LOGGER.info(f"Drive {uuid} removed ({path})")
                removed_drives.append(uuid)
        for uuid in removed_drives:
            self._drives.pop(uuid)

    def _detect_initial_drives(self) -> None:
        """Detect and register drives as startup."""
        LOGGER.info("Checking for initial drives at startup.")
        udisks = self._bus.get(self.DBUS_PATH)
        managed_objects = udisks.GetManagedObjects()
        block_devices = {
            x: managed_objects[x]
            for x in managed_objects.keys()
            if x.startswith("/org/freedesktop/UDisks2/block_devices/")
        }
        for path, data in block_devices.items():
            LOGGER.debug(f"Checking drive at {path}")
            if 'org.freedesktop.UDisks2.Filesystem' in data.keys():
                filesystem = data['org.freedesktop.UDisks2.Filesystem']
                if 'MountPoints' in filesystem.keys():
                    mountpoints = filesystem['MountPoints']
                    if len(mountpoints) > 0:
                        mount_path = self._bytes_to_path(mountpoints[0])
                        if 'org.freedesktop.UDisks2.Block' in data.keys():
                            block = data['org.freedesktop.UDisks2.Block']
                            if 'IdUUID' in block.keys():
                                uuid = DiskUUID(block["IdUUID"])
                                LOGGER.info(f"Drive {uuid} mounted ({mount_path})")
                                self._drives[uuid] = mount_path


if __name__ == "__main__":
    main()
