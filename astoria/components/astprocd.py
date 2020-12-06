"""astprocd - Astoria Process Manager."""

import asyncio
import logging
from json import loads
from pathlib import Path
from signal import SIGTERM, SIGKILL
from typing import IO, Dict, Match

import click

from astoria.common.manager import StateManager
from astoria.common.messages.astdiskd import DiskInfoMessage, DiskType, DiskUUID
from astoria.common.messages.astprocd import CodeStatus
from astoria.common.mqtt import Registry

LOGGER = logging.getLogger(__name__)

loop = asyncio.get_event_loop()

registry = Registry()


@click.command("astprocd")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.File('r'), default=Path("astoria.toml"))
def main(*, verbose: bool, config_file: IO[str]) -> None:
    """Process Manager."""
    procd = ProcessManager(verbose, config_file, registry)
    loop.run_until_complete(procd.run())


class ProcessManager(StateManager):
    """Astoria Process Manager."""

    name = "astprocd"
    dependencies = ["astdiskd"]

    def _init(self) -> None:
        self._lifecycle: Optional[UsercodeLifecycle] = None
        self._cur_disks: Dict[DiskUUID, DiskInfoMessage] = {}

    @registry.handler('astoria/astdiskd/disks/+')
    async def handle_astdiskd_disk_info_message(
        self,
        match: Match[str],
        payload: str,
    ) -> None:
        """Handle disk info messages."""
        uuid = DiskUUID(match.group(1))
        if payload:
            if uuid not in self._cur_disks:
                info = DiskInfoMessage(**loads(payload))
                self._cur_disks[uuid] = info
                asyncio.ensure_future(self.handle_disk_insertion(uuid, info))
            else:
                LOGGER.warning(f"Received duplicate disk insertion for {uuid}")
        else:
            info = self._cur_disks.pop(uuid)
            asyncio.ensure_future(self.handle_disk_removal(uuid, info))

    async def main(self) -> None:
        """Main routine for astprocd."""
        # Wait whilst the program is running.
        await self.wait_loop()

        for uuid, info in self._cur_disks.items():
            asyncio.ensure_future(self.handle_disk_removal(uuid, info))

    async def handle_disk_insertion(self, uuid: DiskUUID, disk_info: DiskInfoMessage) -> None:
        LOGGER.debug(f"Disk inserted: {uuid} ({disk_info.disk_type})")
        if disk_info.disk_type is DiskType.USERCODE:
            LOGGER.info(f"Usercode disk {uuid} is mounted at {disk_info.mount_path}")
            if self._lifecycle is None:
                LOGGER.debug(f"Starting usercode lifecycle for {uuid}")
                self._lifecycle = UsercodeLifecycle(uuid, disk_info)
                asyncio.ensure_future(self._lifecycle.run_process())
            else:
                LOGGER.warn("Cannot run usercode, there is already a lifecycle present.")
                with disk_info.mount_path.joinpath("log.txt").open("w") as fh:
                    fh.write(b"Unable to start code.\n")
                    fh.write(b"It is not safe to run multiple code drives at once.\n")

    async def handle_disk_removal(self, uuid: DiskUUID, disk_info: DiskInfoMessage) -> None:
        LOGGER.debug(f"Disk removed: {uuid} ({disk_info.disk_type})")

        if disk_info.disk_type is DiskType.USERCODE:
            LOGGER.info(f"Usercode disk {uuid} removed ({disk_info.mount_path})")

            if self._lifecycle.uuid == uuid:
                if self._lifecycle is not None:
                    await self._lifecycle.kill_process()
                    self._lifecycle = None
                else:
                    # TODO: something here
                    pass


class UsercodeLifecycle:
    """
    Manages the lifecycle of usercode.

    Handles process management and logging.
    """

    def __init__(self, uuid: DiskUUID, disk_info: DiskInfoMessage) -> None:
        self._uuid = uuid
        self._disk_info = disk_info

        self._process = None

        self._status = CodeStatus.STARTING

    @property
    def uuid(self) -> DiskUUID:
        """The UUID of the managed Disk."""
        return self._uuid

    @property
    def status(self) -> CodeStatus:
        """Get the status of the executing code."""
        return self._status

    @status.setter
    def status(self, status: CodeStatus) -> None:
        """Set the status of the executing code."""
        self._status = status
        # TODO: Inform MQTT here

    async def run_process(self) -> None:
        """
        Start the execution of the usercode.

        This function will not return until the code has exited.
        """

        if self._process is None:
            # TODO Unpack into Tmp file

            self._process = await asyncio.create_subprocess_exec(
                "python",
                "-u",
                "test.py",
                stdin=asyncio.subprocess.DEVNULL,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                # TODO CWD to tmp file
                start_new_session=True,
            )
            asyncio.ensure_future(self.logger(self._process.stdout))
            self.status = CodeStatus.RUNNING
            LOGGER.info(f"Usercode process started with pid {self._process.pid}")

            # Wait for the subprocess to exit.
            # This may include if it is killed.
            rc = await self._process.wait()

            LOGGER.info(f"Usercode process exited with code {rc}")
            if rc == 0:
                self.status = CodeStatus.FINISHED
            elif rc < 0:
                self.status = CodeStatus.KILLED
            elif rc > 0:
                self.status = CodeStatus.CRASHED

            self._process = None
        else:
            LOGGER.warn("Tried to start process, but one is already running.")

    async def kill_process(self) -> None:
        if self._process is not None:
            try:
                LOGGER.info(f"Attempting to kill process.")
                LOGGER.info(f"Sent SIGTERM to pid {self._process.pid}")
                self._process.send_signal(SIGTERM)
                try:
                    await asyncio.wait_for(self._process.communicate(), timeout=5.0)
                except asyncio.TimeoutError:
                    LOGGER.info(f"Sent SIGKILL to pid {self._process.pid}")
                    self._process.send_signal(SIGKILL)
            except AttributeError:
                # Under some circumstances, there is a race condition such that
                # _process becomes None whilst the communicate timeout is running.
                # We want to catch and discard this error.
                pass
        else:
            LOGGER.debug("Tried to kill process, but no process is running.")

    async def logger(self, proc_output: asyncio.StreamReader) -> None:
        log_path = self._disk_info.mount_path / "log.txt"
        with log_path.open("w") as fh:
            fh.write("=== LOG STARTED === \n")
            fh.flush()
            data = await proc_output.readline()
            while data != b"":
                fh.write(data.decode('utf-8'))
                fh.flush()
                data = await proc_output.readline()
            fh.write("=== LOG FINISHED === \n")
            fh.flush()