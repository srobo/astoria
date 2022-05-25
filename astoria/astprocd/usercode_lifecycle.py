"""Manage running, killing and observing usercode."""

import asyncio
import logging
from datetime import datetime
from os import environ
from signal import SIGKILL, SIGTERM
from typing import Callable, Dict, Optional

from astoria.common.code_status import CodeStatus
from astoria.common.config import AstoriaConfig
from astoria.common.disks import DiskInfo, DiskUUID
from astoria.common.ipc import LogEventSource, UsercodeLogBroadcastEvent
from astoria.common.metadata import Metadata
from astoria.common.mqtt import BroadcastHelper

LOGGER = logging.getLogger(__name__)

loop = asyncio.get_event_loop()


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
            metadata: Metadata,
            config: AstoriaConfig,
    ) -> None:
        self._uuid = uuid
        self._disk_info = disk_info
        self._status_inform_callback = status_inform_callback
        self._log_helper = log_helper
        self._metadata = metadata
        self._config = config

        self._process: Optional[asyncio.subprocess.Process] = None
        self._process_lock = asyncio.Lock()

        self._entrypoint = self._metadata.usercode_entrypoint

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

    async def run_process(self) -> None:
        """
        Start the execution of the usercode.

        This function will not return until the code has exited.
        """
        if self._process is None:
            async with self._process_lock:
                LOGGER.info(
                    "Starting usercode execution with "
                    f"entrypoint {self._entrypoint}",
                )
                self._process = await asyncio.create_subprocess_exec(
                    "python3",
                    "-u",
                    self._metadata.usercode_entrypoint,
                    stdin=asyncio.subprocess.DEVNULL,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=self.disk_info.mount_path,
                    start_new_session=True,
                    env={**environ.copy(), **self._config.env},
                )
                if self._process is not None:
                    if self._process.stdout is not None and \
                            self._process.stderr is not None:
                        asyncio.ensure_future(
                            self.logger(
                                {LogEventSource.STDOUT: self._process.stdout,
                                    LogEventSource.STDERR: self._process.stderr},
                            ),
                        )
                    else:
                        LOGGER.warning("Unable to start logger task.")
                    self.status = CodeStatus.RUNNING
                    LOGGER.info(
                        f"Usercode pid {self._process.pid} "
                        f"started in {self._disk_info.mount_path}",
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
                else:
                    LOGGER.warning("Tried to start process, but failed.")
                    self.status = CodeStatus.CRASHED  # Close enough to indicate error
        else:
            LOGGER.warning("Tried to start process, but one is already running.")

    async def kill_process(self) -> None:
        """Kill the process, if one is running."""
        if self._process is not None and self._process_lock.locked():
            LOGGER.info("Attempting to kill process.")

            # Work-around for bpo-43884
            self._process._transport.close()  # type: ignore

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
    ) -> None:
        """
        Logger task.

        Logs the output of the process to a log file and MQTT

        :param proc_outputs: streams of data from the usercode process
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
                    data_str = data.decode('utf-8', errors='ignore')
                    time_passed = datetime.now() - start_time
                    log(f"[{time_passed}] {data_str}", log_line_idx, source)
                    data = await output.readline()
                    log_line_idx += 1

            time_passed = datetime.now() - start_time

            # Print initial lines to the log, if any.
            # This is useful to show a message to the user in every log file.
            if self._config.system.initial_log_lines:
                log(f"[{time_passed}] ---\n", log_line)

                for line in self._config.system.initial_log_lines:
                    log(f"[{time_passed}] {line}\n", log_line)
                log(f"[{time_passed}] ---\n", log_line)

            log(f"[{time_passed}] === LOG STARTED ===\n", log_line)
            log_line += 1

            await asyncio.gather(
                read_from_stream(proc_outputs, LogEventSource.STDOUT, log_line),
                read_from_stream(proc_outputs, LogEventSource.STDERR, log_line),
            )
            time_passed = datetime.now() - start_time
            log(f"[{time_passed}] === LOG FINISHED ===\n", log_line)