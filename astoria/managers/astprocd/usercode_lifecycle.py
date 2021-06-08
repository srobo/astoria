"""Manage running, killing and observing usercode."""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from signal import SIGKILL, SIGTERM
from tempfile import TemporaryDirectory
from typing import Callable, Dict, List, Optional, Set
from zipfile import BadZipFile, ZipFile

import toml
from pydantic import ValidationError

from astoria.common.broadcast_event import (
    LogEventSource,
    UsercodeLogBroadcastEvent,
)
from astoria.common.bundle import CodeBundle, IncompatibleKitVersionException
from astoria.common.config import AstoriaConfig
from astoria.common.messages.astdiskd import DiskInfo, DiskUUID
from astoria.common.messages.astprocd import CodeStatus
from astoria.common.mqtt import BroadcastHelper

LOGGER = logging.getLogger(__name__)

loop = asyncio.get_event_loop()


class InvalidCodeBundleException(Exception):
    """The code bundle was not valid."""


class UsercodeLifecycle:
    """
    Manages the lifecycle of usercode.

    Handles process management and logging.
    """

    def __init__(
            self,
            uuid: DiskUUID,
            disk_info: DiskInfo,
            status_inform_callback: Callable[[CodeStatus], None],
            log_helper: BroadcastHelper[UsercodeLogBroadcastEvent],
            config: AstoriaConfig,
    ) -> None:
        self._uuid = uuid
        self._disk_info = disk_info
        self._status_inform_callback = status_inform_callback
        self._log_helper = log_helper
        self._config = config

        self._process: Optional[asyncio.subprocess.Process] = None
        self._process_lock = asyncio.Lock()
        self._setup_temp_dir()

        self.status = CodeStatus.STARTING

    @property
    def uuid(self) -> DiskUUID:
        """The UUID of the managed Disk."""
        return self._uuid

    @property
    def disk_info(self) -> DiskInfo:
        """Disk Info for the managed disk."""
        return self._disk_info

    @property
    def status(self) -> CodeStatus:
        """Get the status of the executing code."""
        return self._status

    @status.setter
    def status(self, status: CodeStatus) -> None:
        """Set the status of the executing code."""
        self._status = status
        self._status_inform_callback(status)

    def _setup_temp_dir(self) -> None:
        """Setup a temporary directory."""
        self._dir = TemporaryDirectory(prefix="astprocd-")
        self._dir_path = Path(self._dir.name)

    def _extract_and_validate_zip_file(self) -> List[str]:
        """
        Extract and validate a robot.zip file.

        This function will extract and validate the contents of the
        robot.zip file. It will overwrite the current temporary dir
        of the usercode lifecycle, and should not be called multiple
        times.

        :returns: messages to put in the log file
        """
        zip_path = self._disk_info.mount_path / "robot.zip"

        if not (zip_path.exists() and zip_path.is_file()):
            raise InvalidCodeBundleException("Unable to find robot.zip file")

        try:
            with ZipFile(zip_path, "r") as zf:
                zf.extractall(self._dir_path)
        except BadZipFile:
            raise InvalidCodeBundleException(
                "The provided robot.zip is not a valid ZIP archive",
            )

        # Check that robot.py is present
        exe_path = self._dir_path / "robot.py"
        if not exe_path.exists():
            raise InvalidCodeBundleException(
                "The provided robot.zip did not contain a robot.py",
            )

        LEGACY_FILES: Set[str] = {"info.yaml", "info.yml", "wifi.yaml", "wifi.yml"}

        for legacy_file in LEGACY_FILES:
            legacy_info_path = self._dir_path / legacy_file
            if legacy_info_path.exists():
                raise InvalidCodeBundleException(
                    "This is an old robot code package and \
                    will not work with this version of the kit.",
                )

        # Check for code bundle info
        bundle_meta_path = self._dir_path / "bundle.toml"
        if not bundle_meta_path.exists():
            raise InvalidCodeBundleException(
                "The provided robot.zip did not contain a bundle.toml",
            )
        else:
            # Validate code bundle info
            try:
                bundle_contents = toml.loads(bundle_meta_path.read_text())
            except toml.TomlDecodeError as e:
                raise InvalidCodeBundleException(f"The code bundle was invalid.\n{e}")

            try:
                bundle = CodeBundle(**bundle_contents)
            except ValidationError as e:
                raise InvalidCodeBundleException(f"The code bundle was invalid.\n{e}")

            try:
                return bundle.check_kit_version_is_compatible(self._config.kit)
            except IncompatibleKitVersionException as e:
                raise InvalidCodeBundleException(f"Invalid code bundle: {e}")

    async def run_process(self) -> None:
        """
        Start the execution of the usercode.

        This function will not return until the code has exited.
        """
        if self._process is None:
            try:
                log_message = self._extract_and_validate_zip_file()
                async with self._process_lock:
                    self._process = await asyncio.create_subprocess_exec(
                        "python3",
                        "-u",
                        "robot.py",
                        stdin=asyncio.subprocess.DEVNULL,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd=self._dir_path,
                        start_new_session=True,
                    )
                    if self._process is not None:
                        if self._process.stdout is not None and \
                                self._process.stderr is not None:
                            asyncio.ensure_future(
                                self.logger(
                                    {LogEventSource.STDOUT: self._process.stdout,
                                     LogEventSource.STDERR: self._process.stderr},
                                    initial_messages=log_message,
                                ),
                            )
                        else:
                            LOGGER.warning("Unable to start logger task.")
                        self.status = CodeStatus.RUNNING
                        LOGGER.info(
                            f"Usercode pid {self._process.pid} "
                            f"started in {self._dir_path}",
                        )

                        # Wait for the subprocess to exit.
                        # This may include if it is killed.
                        rc = await self._process.wait()

                        if rc == 0:
                            self.status = CodeStatus.FINISHED
                        elif rc < 0:
                            self.status = CodeStatus.KILLED
                        elif rc > 0:
                            self.status = CodeStatus.CRASHED
                        LOGGER.info(
                            f"Usercode process exited with code {rc} "
                            f"({self.status.name})",
                        )

                        self._process = None

                        self._dir.cleanup()  # Reset directory
                        self._setup_temp_dir()
                    else:
                        LOGGER.warning("Tried to start process, but failed.")
                        self.status = CodeStatus.CRASHED  # Close enough to indicate error
            except InvalidCodeBundleException as e:
                LOGGER.warning("robot.zip was invalid. Unable to start code.")
                # Write error message to the log file.
                with self._disk_info.mount_path.joinpath("log.txt").open("w") as fh:
                    LOGGER.warning(str(e))
                    fh.write("Unable to start code.\n")
                    fh.write(f"{e}.\n")

                self.status = CodeStatus.CRASHED  # Close enough to indicate error
        else:
            LOGGER.warning("Tried to start process, but one is already running.")

    async def kill_process(self) -> None:
        """Kill the process, if one is running."""
        if self._process is not None and self._process_lock.locked():
            LOGGER.info("Attempting to kill process.")
            LOGGER.info(f"Sent SIGTERM to pid {self._process.pid}")
            self._process.send_signal(SIGTERM)
            try:
                await asyncio.wait_for(self._process.communicate(), timeout=5.0)
            except asyncio.TimeoutError:
                if self._process is not None:
                    LOGGER.info(f"Sent SIGKILL to pid {self._process.pid}")
                    self._process.send_signal(SIGKILL)
            except AttributeError:
                # Under some circumstances, there is a race condition such that
                # _process becomes None whilst the communicate timeout is running.
                # We want to catch and discard this error.
                pass
        else:
            LOGGER.debug("Tried to kill process, but no process is running.")

    async def logger(
        self,
        proc_outputs: Dict[LogEventSource, asyncio.StreamReader],
        *,
        initial_messages: List[str] = [],
    ) -> None:
        """
        Logger task.

        Logs the output of the process to a log file and MQTT

        :param proc_outputs: streams of data from the usercode process
        :param initial_messages: optional messages to add at the start of the log
        """
        log_path = self._disk_info.mount_path / "log.txt"

        if self._process is not None:
            pid = self._process.pid
        else:
            pid = -1  # Use -1 if unknown

        def log(
            data: str,
            log_line_idx: int,
            source: LogEventSource = LogEventSource.ASTORIA,
        ) -> None:
            fh.write(data)
            fh.flush()
            self._log_helper.send(
                pid=pid,
                priority=log_line_idx,
                content=data,
                source=source,
            )

        with log_path.open("w") as fh:
            log_line = 0

            start_time = datetime.now()

            async def read_from_stream(
                    outputs: Dict[LogEventSource, asyncio.StreamReader],
                    source: LogEventSource,
                    log_line_idx: int,
            ) -> None:
                output = outputs[source]

                data = await output.readline()
                while data != b"":
                    data_str = data.decode('utf-8')
                    time_passed = datetime.now() - start_time
                    log(f"[{time_passed}] {data_str}", log_line_idx, source)
                    data = await output.readline()
                    log_line_idx += 1

            # Print any initial messages
            for message in initial_messages:
                time_passed = datetime.now() - start_time
                log(f"[{time_passed}] {message}\n", log_line)
                log_line += 1

            time_passed = datetime.now() - start_time
            log(f"[{time_passed}] === LOG STARTED ===\n", log_line)
            log_line += 1

            await asyncio.gather(
                read_from_stream(proc_outputs, LogEventSource.STDOUT, log_line),
                read_from_stream(proc_outputs, LogEventSource.STDERR, log_line),
            )
            time_passed = datetime.now() - start_time
            log(f"[{time_passed}] === LOG FINISHED ===\n", log_line)
