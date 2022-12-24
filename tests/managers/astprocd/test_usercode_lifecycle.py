"""Test the usercode lifecycle code used by astprocd."""
import asyncio
from contextlib import AbstractContextManager
from pathlib import Path
from re import compile
from typing import IO, Any, List, Optional, Tuple, Type

import pytest

from astoria.astprocd.usercode_lifecycle import UsercodeLifecycle
from astoria.common.code_status import CodeStatus
from astoria.common.config import AstoriaConfig
from astoria.common.disks import DiskInfo, DiskType, DiskUUID
from astoria.common.ipc import UsercodeLogBroadcastEvent
from astoria.common.metadata import Metadata
from astoria.common.mqtt.broadcast_helper import BroadcastHelper, T

EXTRACT_ZIP_DATA = Path("tests/data/extract_zip")
EXECUTE_CODE_DATA = Path("tests/data/execute_code")
TIMESTAMP_REGEX = compile(r"^(\[.*\]) (.*)$")

with Path("tests/data/config/valid.toml").open("rb") as fh:
    CONFIG = AstoriaConfig.load_from_file(fh)


def _strip_timestamp(line: str) -> str:
    """
    Strip the timestamp from a log line.

    Also checks that the line has a timestamp and errors if not.
    """
    match = TIMESTAMP_REGEX.match(line)
    if match:
        ts, line = match.groups()
        return line
    else:
        assert False, f"{line} Line did not have timestamp"


class MockBroadcastHelper(BroadcastHelper[T]):
    """Mock BroadcastHelper class to help with tests."""

    def __init__(self, name: str, schema: Type[T]) -> None:
        self._name = name
        self._schema = schema

        self._event_queue: asyncio.PriorityQueue[T] = asyncio.PriorityQueue()
        self._sent: List[T] = []

    @classmethod
    def get_helper(cls, schema: Type[T]) -> 'MockBroadcastHelper[T]':  # type: ignore
        """Get the broadcast helper for a given event."""
        return cls(schema.name, schema)

    def get_lines(self) -> List[str]:
        """Get lines in the same format as the file."""
        return "".join(a.content for a in self._sent).splitlines()  # type: ignore

    def send(self, **kwargs: Any) -> None:  # type: ignore
        """Send an event."""
        data = self._schema(  # noqa: F841
            event_name=self._schema.name,
            sender_name="mock",
            **kwargs,
        )
        self._sent.append(data)


class ReadAndCleanupFile(AbstractContextManager):  # type: ignore
    """Read a file and clean it up."""

    def __init__(self, file_path: Path) -> None:
        self._file_path = file_path
        self._fh: Optional[IO[str]] = None

    def __enter__(self) -> IO[str]:
        self._fh = self._file_path.open("r")
        return self._fh

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:  # type: ignore
        if self._fh is not None:
            self._fh.close()
        # self._file_path.unlink()


class StatusInformTestHelper:
    """Helper class for mocking the inform callback."""

    def __init__(self) -> None:
        self.times_called = 0
        self.log_helper = MockBroadcastHelper.get_helper(UsercodeLogBroadcastEvent)
        self.called_queue: List[CodeStatus] = []

    def callback(self, status: CodeStatus) -> None:
        """Mock inform callback."""
        self.times_called += 1
        self.called_queue.append(status)

    @classmethod
    def setup(
        cls,
        mount_path: Path = Path(),
        *,
        config: AstoriaConfig = CONFIG,
    ) -> Tuple[UsercodeLifecycle, 'StatusInformTestHelper']:
        """Setup a lifecycle and helper for testing."""
        sith = cls()
        ucl = UsercodeLifecycle(
            uuid=DiskUUID("foo"),
            disk_info=DiskInfo(
                uuid="foo",
                mount_path=mount_path,
                disk_type=DiskType.USERCODE,
            ),
            status_inform_callback=sith.callback,
            log_helper=sith.log_helper,
            config=config,
            metadata=Metadata.init(config),
        )
        return ucl, sith


def test_usercode_lifecycle_init() -> None:
    """Test the constructor."""
    ucl, sith = StatusInformTestHelper.setup()
    assert sith.times_called == 1
    assert sith.called_queue == [CodeStatus.STARTING]
    assert ucl._process is None


def test_usercode_lifecycle_properties() -> None:
    """Test that the properties on the lifecycle work."""
    ucl, _ = StatusInformTestHelper.setup()

    assert ucl.uuid == "foo"
    assert ucl.disk_info.uuid == "foo"
    assert ucl.status is CodeStatus.STARTING


def test_usercode_lifecycle_inform_callback_called_on_status_change() -> None:
    """Test that the inform callback is called in the correct order."""
    ucl, sith = StatusInformTestHelper.setup()

    ucl.status = CodeStatus.RUNNING
    ucl.status = CodeStatus.CRASHED
    ucl.status = CodeStatus.RUNNING
    ucl.status = CodeStatus.FINISHED

    assert sith.called_queue == [
        CodeStatus.STARTING,
        CodeStatus.RUNNING,
        CodeStatus.CRASHED,
        CodeStatus.RUNNING,
        CodeStatus.FINISHED,
    ]


@pytest.mark.asyncio
async def test_existing_process_on_run() -> None:
    """
    Test that only one process can exist.

    Checks that:
    - The code doesn't run twice
    """
    ucl, sith = StatusInformTestHelper.setup()
    ucl._process = "HACK. Easier than creating a process object."  # type: ignore
    await ucl.run_process()
    assert sith.called_queue == [CodeStatus.STARTING]  # Code should not have started.


@pytest.mark.asyncio
async def test_run_with_not_python() -> None:
    """
    Test that non-python code is handled.

    Checks that:
    - Entrypoint is executed
    - Output is written to the log file
    - The correct status is passed to the state manager
    - Development indicator is printed
    """
    ucl, sith = StatusInformTestHelper.setup(EXECUTE_CODE_DATA / "not_python")
    await ucl.run_process()
    await asyncio.sleep(0.05)  # Wait for logger to flush
    assert sith.called_queue == [
        CodeStatus.STARTING,
        CodeStatus.RUNNING,
        CodeStatus.CRASHED,
    ]
    # Check that the log file contains the right text
    log_file = EXECUTE_CODE_DATA / "not_python" / "log.txt"
    with ReadAndCleanupFile(log_file) as fh:
        lines = fh.read().splitlines()
    assert _strip_timestamp(lines[0]) == "=== LOG STARTED ==="
    assert "This is not a python program" in _strip_timestamp(lines[2])
    assert _strip_timestamp(lines[-1]) == "=== LOG FINISHED ==="

    assert lines == sith.log_helper.get_lines()


@pytest.mark.asyncio
async def test_run_with_syntax_error() -> None:
    """
    Test that bad python code is handled.

    Checks that:
    - Entrypoint is executed
    - Output is written to the log file
    - The correct status is passed to the state manager
    - Development indicator is printed
    """
    ucl, sith = StatusInformTestHelper.setup(EXECUTE_CODE_DATA / "syntax_error")
    await ucl.run_process()
    await asyncio.sleep(0.05)  # Wait for logger to flush
    assert sith.called_queue == [
        CodeStatus.STARTING,
        CodeStatus.RUNNING,
        CodeStatus.CRASHED,
    ]
    # Check that the log file contains the right text
    log_file = EXECUTE_CODE_DATA / "syntax_error" / "log.txt"
    with ReadAndCleanupFile(log_file) as fh:
        lines = fh.read().splitlines()
    assert _strip_timestamp(lines[0]) == "=== LOG STARTED ==="
    assert "SyntaxError" in _strip_timestamp(lines[4])
    assert _strip_timestamp(lines[-1]) == "=== LOG FINISHED ==="

    assert lines == sith.log_helper.get_lines()


@pytest.mark.asyncio
async def test_run_with_valid_python_wait_finish() -> None:
    """
    Test that valid python code is successfully executed.

    Checks that:
    - Entrypoint is executed
    - Output is written to the log file
    - The correct status is passed to the state manager
    """
    ucl, sith = StatusInformTestHelper.setup(EXECUTE_CODE_DATA / "valid_python_short")
    await ucl.run_process()
    await asyncio.sleep(0.05)  # Wait for logger to flush
    assert sith.called_queue == [
        CodeStatus.STARTING,
        CodeStatus.RUNNING,
        CodeStatus.FINISHED,
    ]
    # Check that the log file contains the right text
    log_file = EXECUTE_CODE_DATA / "valid_python_short" / "log.txt"
    with ReadAndCleanupFile(log_file) as fh:
        lines = fh.read().splitlines()
    assert _strip_timestamp(lines[0]) == "=== LOG STARTED ==="
    assert _strip_timestamp(lines[1]) == "Hello World"
    assert _strip_timestamp(lines[-1]) == "=== LOG FINISHED ==="

    assert lines == sith.log_helper.get_lines()


@pytest.mark.asyncio
async def test_run_with_valid_python_other_entrypoint() -> None:
    """
    Test that a non-default entrypoint is successfully executed.

    Checks that:
    - The correct entrypoint is executed
    - Output is written to the log file
    - The correct status is passed to the state manager
    """
    code_dir = EXECUTE_CODE_DATA / "valid_python_different_entrypoint"
    ucl, sith = StatusInformTestHelper.setup(code_dir)
    await ucl.run_process()
    await asyncio.sleep(0.05)  # Wait for logger to flush
    assert sith.called_queue == [
        CodeStatus.STARTING,
        CodeStatus.RUNNING,
        CodeStatus.FINISHED,
    ]
    # Check that the log file contains the right text
    log_file = code_dir / "log.txt"
    with ReadAndCleanupFile(log_file) as fh:
        lines = fh.read().splitlines()
    assert _strip_timestamp(lines[0]) == "=== LOG STARTED ==="
    assert _strip_timestamp(lines[1]) == "World Hello"
    assert _strip_timestamp(lines[-1]) == "=== LOG FINISHED ==="

    assert lines == sith.log_helper.get_lines()


@pytest.mark.asyncio
async def test_run_with_valid_python_additional_log_lines() -> None:
    """
    Test that valid python code is successfully executed.

    Checks that:
    - Entrypoint is executed
    - Output is written to the log file
    - The correct status is passed to the state manager
    """
    config = CONFIG.dict()
    config["system"]["initial_log_lines"] = ["Hello", "World"]
    ucl, sith = StatusInformTestHelper.setup(
        EXECUTE_CODE_DATA / "valid_python_short",
        config=AstoriaConfig(**config),
    )
    await ucl.run_process()
    await asyncio.sleep(0.05)  # Wait for logger to flush
    assert sith.called_queue == [
        CodeStatus.STARTING,
        CodeStatus.RUNNING,
        CodeStatus.FINISHED,
    ]
    # Check that the log file contains the right text
    log_file = EXECUTE_CODE_DATA / "valid_python_short" / "log.txt"
    with ReadAndCleanupFile(log_file) as fh:
        lines = fh.read().splitlines()
    assert _strip_timestamp(lines[0]) == "---"
    assert _strip_timestamp(lines[1]) == "Hello"
    assert _strip_timestamp(lines[2]) == "World"
    assert _strip_timestamp(lines[3]) == "---"
    assert _strip_timestamp(lines[4]) == "=== LOG STARTED ==="
    assert _strip_timestamp(lines[5]) == "Hello World"
    assert _strip_timestamp(lines[-1]) == "=== LOG FINISHED ==="

    assert lines == sith.log_helper.get_lines()


@pytest.mark.asyncio
async def test_run_additional_log_lines_templated() -> None:
    """
    Test that we print additional log lines with correct templating.

    Checks that:
    - Output is written to the log file
    - The output has the template variables correctly substituted.
    """
    config = CONFIG.dict()
    config["system"]["initial_log_lines"] = [
        "Hello",
        "World",
        "Zone: $zone",
        "Arena: $arena",
        "Bad Variable: $beees",
    ]
    ucl, _ = StatusInformTestHelper.setup(
        EXECUTE_CODE_DATA / "valid_python_short",
        config=AstoriaConfig(**config),
    )
    await ucl.run_process()
    await asyncio.sleep(0.05)  # Wait for logger to flush

    # Check that the log file contains the right text
    log_file = EXECUTE_CODE_DATA / "valid_python_short" / "log.txt"
    with ReadAndCleanupFile(log_file) as fh:
        lines = fh.read().splitlines()
    assert _strip_timestamp(lines[0]) == "---"
    assert _strip_timestamp(lines[1]) == "Hello"
    assert _strip_timestamp(lines[2]) == "World"
    assert _strip_timestamp(lines[3]) == "Zone: 0"
    assert _strip_timestamp(lines[4]) == "Arena: A"

    # Check that an unknown variable is not substituted
    assert _strip_timestamp(lines[5]) == "Bad Variable: $beees"
    assert _strip_timestamp(lines[6]) == "---"


@pytest.mark.asyncio
async def test_run_with_valid_python_wait_kill() -> None:
    """
    Test that valid python code is successfully executed and killed.

    Checks that:
    - Entrypoint is executed
    - The code is killed after 2 secs of execution
    - Output is written to the log file
    - The correct status is passed to the state manager
    """
    ucl, sith = StatusInformTestHelper.setup(EXECUTE_CODE_DATA / "valid_python_long")
    asyncio.ensure_future(ucl.run_process())
    await asyncio.sleep(2)
    await ucl.kill_process()
    assert sith.called_queue == [
        CodeStatus.STARTING,
        CodeStatus.RUNNING,
        CodeStatus.KILLED,
    ]
    # Check that the log file contains the right text
    log_file = EXECUTE_CODE_DATA / "valid_python_long" / "log.txt"
    with ReadAndCleanupFile(log_file) as fh:
        lines = fh.read().splitlines()
    assert _strip_timestamp(lines[0]) == "=== LOG STARTED ==="
    assert _strip_timestamp(lines[1]) == "Starting"
    assert _strip_timestamp(lines[2]) == "0"
    assert _strip_timestamp(lines[-1]) == "=== LOG FINISHED ==="
    assert len(lines) == 5  # Check the code didn't run for the entire length

    assert lines == sith.log_helper.get_lines()


@pytest.mark.asyncio
async def test_run_with_valid_python_wait_kill_ignore_sigint() -> None:
    """
    Test that valid python code that ignores SIGINT can be killed.

    Checks that:
    - Entrypoint is executed
    - The code is killed after 2 secs of execution
    - Output is written to the log file
    - The correct status is passed to the state manager
    - Test that the exported PID is updated when the process starts and exits
    """
    ucl, sith = StatusInformTestHelper.setup(
        EXECUTE_CODE_DATA / "valid_python_long_ignore_signals",
    )
    assert ucl.pid is None
    asyncio.ensure_future(ucl.run_process())
    await asyncio.sleep(2)
    assert ucl.pid is not None
    await ucl.kill_process()
    assert ucl.pid is None
    assert sith.called_queue == [
        CodeStatus.STARTING,
        CodeStatus.RUNNING,
        CodeStatus.KILLED,
    ]
    # Check that the log file contains the right text
    log_file = EXECUTE_CODE_DATA / "valid_python_long_ignore_signals" / "log.txt"
    with ReadAndCleanupFile(log_file) as fh:
        lines = fh.read().splitlines()
    assert _strip_timestamp(lines[0]) == "=== LOG STARTED ==="
    assert _strip_timestamp(lines[1]) == "Starting"
    assert _strip_timestamp(lines[2]) == "0"
    assert _strip_timestamp(lines[-1]) == "=== LOG FINISHED ==="
    assert len(lines) == 5  # Check the code didn't run for the entire length

    assert lines == sith.log_helper.get_lines()


@pytest.mark.asyncio
async def test_run_with_valid_python_env_vars() -> None:
    """
    Tests that environment variables are passed down to executed Python code.

    Checks that:
    - Entrypoint is executed
    - The code finishes running after 1 second of execution
    - Log file output contains the contents of an environment variable set in astoria.toml
    """
    ucl, sith = StatusInformTestHelper.setup(
        EXECUTE_CODE_DATA / "valid_python_with_env",
    )
    asyncio.ensure_future(ucl.run_process())
    await asyncio.sleep(1)
    assert sith.called_queue == [
        CodeStatus.STARTING,
        CodeStatus.RUNNING,
        CodeStatus.FINISHED,
    ]
    # Check that the log file contains the right text
    log_file = EXECUTE_CODE_DATA / "valid_python_with_env" / "log.txt"
    with ReadAndCleanupFile(log_file) as fh:
        lines = fh.read().splitlines()
    assert _strip_timestamp(lines[0]) == "=== LOG STARTED ==="
    assert _strip_timestamp(lines[1]) == "123"
    assert _strip_timestamp(lines[-1]) == "=== LOG FINISHED ==="
