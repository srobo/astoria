"""Test the usercode lifecycle code used by astprocd."""
import asyncio
from contextlib import AbstractContextManager
from pathlib import Path
from typing import IO, Any, List, Optional, Tuple, Type

import pytest

from astoria.common.broadcast_event import UsercodeLogBroadcastEvent
from astoria.common.messages.astdiskd import DiskInfo, DiskType, DiskUUID
from astoria.common.messages.astprocd import CodeStatus
from astoria.common.mqtt.broadcast_helper import BroadcastHelper, T
from astoria.managers.astprocd import UsercodeLifecycle

EXTRACT_ZIP_DATA = Path("tests/data/extract_zip")
EXECUTE_CODE_DATA = Path("tests/data/execute_code")


class MockBroadcastHelper(BroadcastHelper[T]):
    """Mock BroadcastHelper class to help with tests."""

    def __init__(self, name: str, schema: Type[T]) -> None:
        self._event_queue: asyncio.PriorityQueue[T] = asyncio.PriorityQueue()

    @classmethod
    def get_helper(cls, schema: Type[T]) -> 'MockBroadcastHelper[T]':
        """Get the broadcast helper for a given event."""
        return cls[T](schema.name, schema)

    def send(self, **kwargs: Any) -> None:  # type: ignore
        """Send an event."""
        data = self._schema(  # noqa: F841
            event_name=self._schema.name,
            sender_name=self._mqtt._client_name,
            **kwargs,
        )
        pass


class ReadAndCleanupFile(AbstractContextManager):
    """Read a file and clean it up."""

    def __init__(self, file_path: Path) -> None:
        self._file_path = file_path
        self._fh: Optional[IO[str]] = None

    def __enter__(self) -> IO[str]:
        self._fh = self._file_path.open("r")
        return self._fh

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        if self._fh is not None:
            self._fh.close()
        self._file_path.unlink()


class StatusInformTestHelper:
    """Helper class for mocking the inform callback."""

    def __init__(self) -> None:
        self.times_called = 0
        self.called_queue: List[CodeStatus] = []

    def callback(self, status: CodeStatus) -> None:
        """Mock inform callback."""
        self.times_called += 1
        self.called_queue.append(status)

    @classmethod
    def setup(
        cls,
        mount_path: Path = Path(),
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
            log_helper=MockBroadcastHelper.get_helper(UsercodeLogBroadcastEvent),
        )
        return ucl, sith


def test_usercode_lifecycle_init() -> None:
    """Test the constructor."""
    ucl, sith = StatusInformTestHelper.setup()
    assert sith.times_called == 1
    assert sith.called_queue == [CodeStatus.STARTING]

    assert ucl._dir_path.exists()
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


def test_extract_and_validate_no_zip() -> None:
    """Test that a disk with no zip is handled."""
    ucl, sith = StatusInformTestHelper.setup(EXTRACT_ZIP_DATA / "no_zip")
    assert not ucl._extract_and_validate_zip_file()

    # Check that the log file contains the right text
    log_file = EXTRACT_ZIP_DATA / "no_zip" / "log.txt"
    with ReadAndCleanupFile(log_file) as fh:
        assert fh.read() == "Unable to start code.\nUnable to find robot.zip file.\n"


def test_bad_zip() -> None:
    """Test that an invalid zip is handled."""
    ucl, sith = StatusInformTestHelper.setup(EXTRACT_ZIP_DATA / "bad_zip")
    assert not ucl._extract_and_validate_zip_file()

    # Check that the log file contains the right text
    log_file = EXTRACT_ZIP_DATA / "bad_zip" / "log.txt"
    with ReadAndCleanupFile(log_file) as fh:
        assert fh.read() == "Unable to start code.\nThe provided robot.zip is not a valid ZIP archive.\n"  # noqa: E501


def test_no_main_zip() -> None:
    """Test that a zip with no main is handled."""
    ucl, sith = StatusInformTestHelper.setup(EXTRACT_ZIP_DATA / "no_main_zip")
    assert not ucl._extract_and_validate_zip_file()

    # Check that the log file contains the right text
    log_file = EXTRACT_ZIP_DATA / "no_main_zip" / "log.txt"
    with ReadAndCleanupFile(log_file) as fh:
        assert fh.read() == "Unable to start code.\nThe provided robot.zip did not contain a main.py.\n"  # noqa: E501


def test_good_zip() -> None:
    """Test that a valid zip is successfully extracted."""
    ucl, sith = StatusInformTestHelper.setup(EXTRACT_ZIP_DATA / "good_zip")
    assert ucl._extract_and_validate_zip_file()

    # Check that the log file does not yet exist
    log_file = EXTRACT_ZIP_DATA / "good_zip" / "log.txt"
    assert not log_file.exists()


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
async def test_run_with_bad_zip() -> None:
    """
    Test that a bad zip is handled.

    Checks that:
    - Status message is written to the log file
    - The correct status is passed to the state manager
    """
    ucl, sith = StatusInformTestHelper.setup(EXTRACT_ZIP_DATA / "bad_zip")
    await ucl.run_process()
    assert sith.called_queue == [
        CodeStatus.STARTING,
        CodeStatus.CRASHED,
    ]


@pytest.mark.asyncio
async def test_run_with_not_python() -> None:
    """
    Test that non-python code is handled.

    Checks that:
    - Zip file is extracted and main.py is run
    - Output is written to the log file
    - The correct status is passed to the state manager
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
    assert lines[0] == "=== LOG STARTED ==="
    assert "This is not a python program" in lines[2]
    assert lines[-1] == "=== LOG FINISHED ==="


@pytest.mark.asyncio
async def test_run_with_syntax_error() -> None:
    """
    Test that bad python code is handled.

    Checks that:
    - Zip file is extracted and main.py is run
    - Output is written to the log file
    - The correct status is passed to the state manager
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
    assert lines[0] == "=== LOG STARTED ==="
    assert "SyntaxError" in lines[4]
    assert lines[-1] == "=== LOG FINISHED ==="


@pytest.mark.asyncio
async def test_run_with_valid_python_wait_finish() -> None:
    """
    Test that valid python code is successfully executed.

    Checks that:
    - Zip file is extracted and main.py is run
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
    assert lines[0] == "=== LOG STARTED ==="
    assert lines[1] == "Hello World"
    assert lines[-1] == "=== LOG FINISHED ==="
