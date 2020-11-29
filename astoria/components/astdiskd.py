"""Disk Manager Application."""

import asyncio
import logging
from pathlib import Path
from typing import IO, Callable, Coroutine, Dict, List, Set

import click
from dbus_next.aio import MessageBus
from dbus_next.aio.proxy_object import ProxyInterface
from dbus_next.constants import BusType
from dbus_next.errors import InterfaceNotFoundError
from dbus_next.signature import Variant

from astoria.common.manager import StateManager
from astoria.common.messages.astdiskd import (
    DiskInfoMessage,
    DiskType,
    DiskUUID,
)
from astoria.common.messages.base import ManagerStatusMessage
from astoria.common.mqtt import Registry

LOGGER = logging.getLogger(__name__)

loop = asyncio.get_event_loop()

registry = Registry()


@click.command("astdiskd")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.File('r'), default=Path("astoria.toml"))
def main(*, verbose: bool, config_file: IO[str]) -> None:
    """Disk Manager Application Entrypoint."""
    diskd = DiskManager(verbose, config_file, registry)
    loop.run_until_complete(diskd.run())


class DiskManager(StateManager):
    """Astoria Disk Manager."""

    name = "astdiskd"

    def _init(self) -> None:
        self._state_lock = asyncio.Lock()
        self._state_disks: Set[DiskUUID] = set()

        self._udisks = UdisksConnection(notify_coro=self.update_state)

    async def main(self) -> None:
        """Main routine for astdiskd."""
        asyncio.ensure_future(self._udisks.main())

        # Wait whilst the program is running.
        await self.wait_loop()

        async with self._state_lock:
            for uuid in self._state_disks:
                await self.mqtt_publish(f"disks/{uuid}", "")

    async def update_state(self) -> None:
        """Update the daemon state on MQTT."""
        async with self._state_lock:
            disk_set = set(self._udisks.drives.keys())
            added_disks = disk_set - self._state_disks
            removed_disks = self._state_disks - disk_set
            self._state_disks = disk_set

        for disk_uuid in added_disks:
            mount_path = self._udisks.drives[disk_uuid]
            await self.mqtt_publish(
                f"disks/{disk_uuid}",
                DiskInfoMessage(
                    uuid=disk_uuid,
                    mount_path=mount_path,
                    disk_type=DiskType.determine_disk_type(mount_path),
                ),
            )

        for disk_uuid in removed_disks:
            asyncio.ensure_future(self.mqtt_publish(
                f"disks/{disk_uuid}",
                "",
            ))


class UdisksConnection:
    """Connect and communicate with UDisks2."""

    DBUS_PATH: str = "/org/freedesktop/UDisks2"
    DBUS_NAME: str = "org.freedesktop.UDisks2"

    def __init__(
        self,
        *,
        notify_coro: Callable[[], Coroutine[None, None, None]],
    ) -> None:
        self._drives: Dict[DiskUUID, Path] = {}
        self._notify_coro = notify_coro

    @property
    def drives(self) -> Dict[DiskUUID, Path]:
        """Currently mounted drives."""
        return self._drives

    async def main(self) -> None:
        """Setup the message bus and task dispatcher."""
        mb = MessageBus(bus_type=BusType.SYSTEM)
        self._bus = await mb.connect()

        self._introspection = await self._bus.introspect(self.DBUS_NAME, self.DBUS_PATH)
        udisks_proxy = self._bus.get_proxy_object(
            self.DBUS_NAME,
            self.DBUS_PATH,
            self._introspection,
        )

        udisks_obj_manager = udisks_proxy.get_interface(
            "org.freedesktop.DBus.ObjectManager",
        )
        udisks_obj_manager.on_interfaces_added(self._disk_signal)

        await self._detect_initial_drives(udisks_obj_manager)

    def _bytes_to_path(self, data: List[int]) -> Path:
        """Convert a null terminated int array to a path."""
        # Data is null terminated.
        mount_point = data[:len(data) - 1]

        chars = [chr(x) for x in mount_point]
        mount_point_str = "".join(chars)

        return Path(mount_point_str)

    def _disk_signal(self, path: str, data: Dict[str, Dict[str, Variant]]) -> None:
        """
        Handle a disk signal event from UDisks2.

        Has to be synchronous due to limitations with python-dbus-next.

        Dispatches tasks to handle the events.
        """
        LOGGER.debug(f"disk_signal: Received disk signal from {path}")

        if path.startswith("/org/freedesktop/UDisks2/jobs/"):
            for job in data.keys():
                event_data = data[job]
                try:
                    if event_data["Operation"].value == "filesystem-mount":
                        LOGGER.debug(f"disk_signal: Mount Event detected at {path}")
                        if all((
                            'Objects' in event_data.keys(),
                            len(event_data["Objects"].value) > 0,
                        )):
                            disk_bus_path = event_data["Objects"].value[0]
                            LOGGER.debug(
                                f"disk_signal: Dispatching mount task"
                                f" for {disk_bus_path}",
                            )
                            asyncio.ensure_future(self.mount_task(disk_bus_path))
                        else:
                            LOGGER.warning(
                                f"No information available on drive at {path}, aborting.",
                            )

                    if event_data["Operation"].value == "cleanup":
                        LOGGER.debug(f"disk_signal: Removal Event detected at {path}")
                        asyncio.ensure_future(self.cleanup_task())
                except IndexError:
                    pass

    async def mount_task(self, disk_bus_path: str, *, notify: bool = True) -> None:
        """Handle a mount event."""
        await asyncio.sleep(0.3)  # Allow enough time for the mount to occur.

        introspection = await self._bus.introspect(self.DBUS_NAME, disk_bus_path)
        drive_obj = self._bus.get_proxy_object(
            self.DBUS_NAME,
            disk_bus_path,
            introspection,
        )

        try:
            drive_filesystem = drive_obj.get_interface(
                "org.freedesktop.UDisks2.Filesystem",
            )

            mount_points: List[List[int]] = \
                await drive_filesystem.get_mount_points()

            try:
                # We are only interested in the first mountpoint.
                mount_path = self._bytes_to_path(mount_points[0])
                if mount_path.exists() and mount_path.is_dir():
                    drive_block = drive_obj.get_interface("org.freedesktop.UDisks2.Block")
                    uuid: DiskUUID = DiskUUID(
                        await drive_block.get_id_uuid(),
                    )
                    if uuid not in self._drives.keys():
                        LOGGER.info(f"Drive {uuid} mounted ({mount_path})")
                        self._drives[uuid] = mount_path

                        if notify:
                            asyncio.ensure_future(self._notify_coro())
                    else:
                        LOGGER.error(f"Drive UUID collision! uuid={uuid}")
                else:
                    LOGGER.warning(f"Invalid mount path: {mount_path}")
            except IndexError:
                LOGGER.warning(f"No mount points available for drive at {disk_bus_path}")

        except InterfaceNotFoundError:
            # Object doesn't have a Filesystem interface
            pass

    async def cleanup_task(self, *, notify: bool = True) -> None:
        """Handle a cleanup event."""
        await asyncio.sleep(0.3)  # Allow enough time for the unmount to occur.

        # We have no information to tell which drive left.
        # Thus we need to check all of them.
        removed_drives: List[DiskUUID] = []
        for uuid, path in self._drives.items():
            if not path.exists():
                LOGGER.info(f"Drive {uuid} removed ({path})")
                removed_drives.append(uuid)

        # We have to remove the drives here as we cannot modify
        # a dictionary as we are iterating over it.
        # Equally, we cannot break the previous loop in case a
        # drive had multiple partitions that were mounted.
        for uuid in removed_drives:
            self._drives.pop(uuid)

        if notify:
            asyncio.ensure_future(self._notify_coro())

    async def _detect_initial_drives(self, udisks_obj_manager: ProxyInterface) -> None:
        """Detect and register drives as startup."""
        LOGGER.info("Checking for initial drives at startup.")

        # The block devices are dbus objects managed by Udisks
        # We have to fetch them all unless we already know what they are.
        managed_objects: Dict[str, Dict[str, str]] = \
            await udisks_obj_manager.call_get_managed_objects()

        # Start a mount task for every block device and wait
        # for all of the tasks to be complete.
        tasks = (
            self.mount_task(path, notify=False)
            for path in managed_objects
            if path.startswith("/org/freedesktop/UDisks2/block_devices/")
        )
        await asyncio.gather(*tasks)

        # Send one notify
        asyncio.ensure_future(self._notify_coro())


if __name__ == "__main__":
    main()
