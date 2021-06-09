"""Metadata State Manager."""

import asyncio
import logging
from typing import Dict, List, Optional, Set, Tuple, Type

from astoria.common.manager import StateManager
from astoria.common.manager_requests import (
    MetadataSetManagerRequest,
    RequestResponse,
)
from astoria.common.messages.astdiskd import DiskInfo, DiskType, DiskUUID
from astoria.common.messages.astmetad import Metadata, MetadataManagerMessage
from astoria.managers.mixins.disk_handler import DiskHandlerMixin

from .metadata_cache import MetadataCache
from .metadata_disk_lifecycle import (
    AbstractMetadataDiskLifecycle,
    BundleDiskLifecycle,
    MetadataDiskLifecycle,
)

LOGGER = logging.getLogger(__name__)


class MetadataManager(DiskHandlerMixin, StateManager[MetadataManagerMessage]):
    """Astoria Metadata State Manager."""

    name = "astmetad"
    dependencies = ["astdiskd"]

    DISK_TYPE_LIFECYCLE_MAP: Dict[DiskType, Type[AbstractMetadataDiskLifecycle]] = {
        DiskType.USERCODE: BundleDiskLifecycle,
        DiskType.METADATA: MetadataDiskLifecycle,
    }

    DISK_TYPE_OVERRIDE_MAP: Dict[DiskType, Set[str]] = {
        DiskType.USERCODE: {"wifi_ssid", "wifi_psk", "wifi_region", "wifi_enabled"},
        DiskType.METADATA: {"arena", "zone", "mode", "game_timeout", "wifi_enabled"},
    }

    MUTABLE_ATTRS_BY_REQUEST: Set[str] = {"arena", "zone", "mode"}
    CACHED_ATTRS: Set[str] = {"wifi_ssid", "wifi_psk", "wifi_region"}

    def _init(self) -> None:
        self._lifecycles: Dict[DiskType, Optional[AbstractMetadataDiskLifecycle]] = {
            disk_type: None
            for disk_type in self.DISK_TYPE_LIFECYCLE_MAP
        }
        self._cache = MetadataCache(
            self.CACHED_ATTRS,
            cache_path=self.config.system.cache_dir / "astmetad-metadata.json",
        )

        self._cur_disks: Dict[DiskUUID, DiskInfo] = {}
        self._mqtt.subscribe("astdiskd", self.handle_astdiskd_disk_info_message)

        self._requested_data: Dict[str, str] = {}
        self._register_request(
            "mutate",
            MetadataSetManagerRequest,
            self.handle_mutation_request,
        )

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
        for disk_type, lifecycle_class in self.DISK_TYPE_LIFECYCLE_MAP.items():
            if disk_info.disk_type is disk_type:
                LOGGER.info(
                    f"{disk_type.name} disk {uuid} is mounted"
                    f" at {disk_info.mount_path}",
                )
                if self._lifecycles[disk_type] is None:
                    LOGGER.debug(f"Starting lifecycle for {uuid}")
                    self._lifecycles[disk_type] = lifecycle_class(uuid, disk_info)
                    self.update_status()
                else:
                    LOGGER.warn(
                        "Cannot use metadata, there is already a lifecycle present.",
                    )

    async def handle_disk_removal(self, uuid: DiskUUID, disk_info: DiskInfo) -> None:
        """Handle a disk removal."""
        LOGGER.debug(f"Disk removed: {uuid} ({disk_info.disk_type})")
        for disk_type, lifecycle_class in self.DISK_TYPE_LIFECYCLE_MAP.items():
            if disk_info.disk_type is disk_type:
                LOGGER.info(f"Metadata disk {uuid} removed ({disk_info.mount_path})")
                lifecycle = self._lifecycles[disk_type]
                if lifecycle is not None and lifecycle._uuid == disk_info.uuid:
                    self._lifecycles[disk_type] = None
                    self.update_status()

    async def handle_mutation_request(
        self,
        request: MetadataSetManagerRequest,
    ) -> RequestResponse:
        """Handle a request to mutate metadata."""
        if request.attr not in self.MUTABLE_ATTRS_BY_REQUEST:
            return RequestResponse(
                uuid=request.uuid,
                success=False,
                reason=f"{request.attr} is not a mutable attribute",
            )

        if len(request.value) == 0:
            # Stop mutating the attr if it is empty.
            try:
                del self._requested_data[request.attr]
                LOGGER.info(f"{request.attr} override has been removed by request")
                self.update_status()
            except KeyError:
                pass
        else:
            self._requested_data[request.attr] = request.value
            LOGGER.info(
                f"{request.attr} has been overridden to {request.value} by request",
            )
            self.update_status()
        return RequestResponse(
            uuid=request.uuid,
            success=True,
        )

    def get_current_metadata(self) -> Metadata:
        """
        Calculate the current metadata.

        Takes the default, static metadata based on the config and system
        information. It then overlays data from other sources in a priority order,
        whereby each source has a set of permitted attributes in the metadata that
        can be overridden.
        """
        # Metadata sources in priority order.
        metadata_sources: List[Tuple[Set[str], Dict[str, str]]] = [
            (self.CACHED_ATTRS, self._cache.data),
            (self.MUTABLE_ATTRS_BY_REQUEST, self._requested_data),
        ]

        for disk_type, val in self._lifecycles.items():
            if val is not None:
                # Add disk-based metadata source if it is present.
                metadata_sources.append(
                    (
                        self.DISK_TYPE_OVERRIDE_MAP[disk_type],
                        val.diff_data,
                    ),
                )

        metadata = Metadata.init(self.config)

        for permitted_attrs, diff_data in metadata_sources:
            for k, v in diff_data.items():
                if k in permitted_attrs:
                    metadata.__setattr__(k, v)
                else:
                    LOGGER.warning(
                        f"There was an attempt to mutate {k}, but it was not permitted.",
                    )

        # Update the cache with the new values.
        for key in self.CACHED_ATTRS:
            self._cache.update_cached_attr(key, metadata.__getattribute__(key))

        return metadata

    def update_status(self) -> None:
        """Update the status of the manager."""
        self.status = MetadataManagerMessage(
            status=MetadataManagerMessage.Status.RUNNING,
            metadata=self.get_current_metadata(),
        )
