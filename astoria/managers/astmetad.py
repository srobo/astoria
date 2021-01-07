"""Metadata Manager Application."""

import asyncio
import logging
from json import loads
from pathlib import Path
from typing import IO, Dict, List, Optional, Set, Tuple

import click

from astoria.common.manager import StateManager
from astoria.common.messages.astdiskd import DiskInfo, DiskType, DiskUUID
from astoria.common.messages.astmetad import Metadata, MetadataManagerMessage

from .mixins.disk_handler import DiskHandlerMixin

LOGGER = logging.getLogger(__name__)

loop = asyncio.get_event_loop()


@click.command("astmetad")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.File('r'), default=Path("astoria.toml"))
def main(*, verbose: bool, config_file: IO[str]) -> None:
    """Metadata Manager Application Entrypoint."""
    metad = MetadataManager(verbose, config_file)
    loop.run_until_complete(metad.run())


class MetadataManager(DiskHandlerMixin, StateManager[MetadataManagerMessage]):
    """Astoria Metadata State Manager."""

    name = "astmetad"
    dependencies = ["astdiskd"]

    def _init(self) -> None:
        self._lifecycle: Optional[MetadataDiskLifecycle] = None
        self._requested_data: Dict[str, str] = {}

        self._cur_disks: Dict[DiskUUID, DiskInfo] = {}
        self._mqtt.subscribe("astdiskd", self.handle_astdiskd_disk_info_message)

    @property
    def offline_status(self) -> MetadataManagerMessage:
        """
        Status to publish when the manager goes offline.

        This status should ensure that any other components relying
        on this data go into a safe state.
        """
        return MetadataManagerMessage(
            status=MetadataManagerMessage.Status.STOPPED,
            metadata=Metadata.init(self.config),
        )

    async def main(self) -> None:
        """Main routine for astmetad."""
        self.update_status()

        # Wait whilst the program is running.
        await self.wait_loop()

        for uuid, info in self._cur_disks.items():
            asyncio.ensure_future(self.handle_disk_removal(uuid, info))

    async def handle_disk_insertion(self, uuid: DiskUUID, disk_info: DiskInfo) -> None:
        """Handle a disk insertion."""
        LOGGER.debug(f"Disk inserted: {uuid} ({disk_info.disk_type})")
        if disk_info.disk_type is DiskType.METADATA:
            LOGGER.info(f"Metadata disk {uuid} is mounted at {disk_info.mount_path}")
            if self._lifecycle is None:
                LOGGER.debug(f"Starting metadata lifecycle for {uuid}")
                self._lifecycle = MetadataDiskLifecycle(uuid, disk_info)
                self.update_status()
            else:
                LOGGER.warn("Cannot use metadata, there is already a lifecycle present.")

    async def handle_disk_removal(self, uuid: DiskUUID, disk_info: DiskInfo) -> None:
        """Handle a disk removal."""
        LOGGER.debug(f"Disk removed: {uuid} ({disk_info.disk_type})")
        if disk_info.disk_type is DiskType.METADATA:
            LOGGER.info(f"Metadata disk {uuid} removed ({disk_info.mount_path})")
            if self._lifecycle is not None and self._lifecycle._uuid == disk_info.uuid:
                self._lifecycle = None
                self.update_status()

    def get_current_metadata(self) -> Metadata:
        """
        Calculate the current metadata.

        Takes the default, static metadata based on the config and system
        information. It then overlays data from other sources in a priority order,
        whereby each source has a set of permitted attributes in the metadata that
        can be overriden.
        """
        # Mutation data sources in priority order.
        MUTATION_SOURCES: List[Tuple[Set[str], Dict[str, str]]] = [
            ({"arena", "zone", "mode"}, self._requested_data),
        ]

        if self._lifecycle is not None:
            # Add mutations from the metadata usb, if it is present.
            MUTATION_SOURCES.append(
                (
                    {"arena", "zone", "mode", "game_timeout", "wifi_enabled"},
                    self._lifecycle.diff_data,
                ),
            )

        metadata = Metadata.init(self.config)

        for permitted_attrs, diff_data in MUTATION_SOURCES:
            for k, v in diff_data.items():
                if k in permitted_attrs:
                    metadata.__setattr__(k, v)
                else:
                    LOGGER.warning(
                        f"There was an attempt to mutate {k}, but it was not permitted.",
                    )
        return metadata

    def update_status(self) -> None:
        """Update the status of the manager."""
        self.status = MetadataManagerMessage(
            status=MetadataManagerMessage.Status.RUNNING,
            metadata=self.get_current_metadata(),
        )


class MetadataDiskLifecycle:
    """Load and validate metadata from a disk."""

    def __init__(self, uuid: DiskUUID, disk_info: DiskInfo) -> None:
        self._uuid = uuid
        self._disk_info = disk_info

        self._metadata_file_path = disk_info.mount_path / "astoria.json"

        with self._metadata_file_path.open("r") as fh:
            self._diff: Dict[str, str] = loads(fh.read())

    @property
    def diff_data(self) -> Dict[str, str]:
        """The data to be used as override."""
        return self._diff


if __name__ == "__main__":
    main()
