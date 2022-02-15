"""Tests for DiskHandlerMixin."""
import asyncio
from pathlib import Path
from re import match
from typing import Dict, List, Match

import pytest

from astoria.common.disks import DiskInfo, DiskType, DiskUUID
from astoria.common.messages.astdiskd import DiskManagerMessage
from astoria.managers.mixins.disk_handler import DiskHandlerMixin


def get_match() -> Match[str]:
    """Get a Match[str] object."""
    res = match(".*", "bees")
    if res is not None:
        return res
    else:
        raise RuntimeError("Regex did not match")


def get_disk_info_list(names: List[str] = []) -> Dict[DiskUUID, DiskInfo]:
    """
    Construct a list of disk info objects.

    Note that the path and type have to be the same as the comparison relies
    on set logic using the hash of the object.
    """
    return {
        DiskUUID(name): DiskInfo(
            uuid=name,
            mount_path=Path(),
            disk_type=DiskType.NOACTION,
        )
        for name in names
    }


def get_disk_manager_message(names: List[str] = []) -> str:
    """
    Construct a dmm with the named disks.

    Note that the path and type have to be the same as the comparison relies
    on set logic using the hash of the object.
    """
    return DiskManagerMessage(
        disks=get_disk_info_list(names),
        status=DiskManagerMessage.Status.RUNNING,
    ).json()


class StubHelper(DiskHandlerMixin):
    """Stub class for testing."""

    def __init__(self) -> None:
        self._cur_disks = {}
        self.times_disk_inserted = 0
        self.times_disk_removed = 0

    async def dispatch(self, payload: str) -> None:
        """Helper method for testing the dispatch handling."""
        await self.handle_astdiskd_disk_info_message(
            get_match(),
            payload,
        )
        await asyncio.sleep(0.01)  # Wait for the dispatched task to complete.

    async def handle_disk_insertion(self, uuid: DiskUUID, disk_info: DiskInfo) -> None:
        """Handle a disk insertion."""
        self.times_disk_inserted += 1

    async def handle_disk_removal(self, uuid: DiskUUID, disk_info: DiskInfo) -> None:
        """Handle a disk removal."""
        self.times_disk_removed += 1


def test_disk_handler_mixin_subclass_init() -> None:
    """Test that we can subclass from the mixin."""
    StubHelper()


@pytest.mark.asyncio
async def test_disk_handler_mixin_detects_new_disk() -> None:
    """Test that we notice when a disk is added."""
    st = StubHelper()

    assert len(st._cur_disks) == 0

    await st.dispatch(
        get_disk_manager_message(["foo"]),
    )

    assert len(st._cur_disks) == 1
    assert "foo" in st._cur_disks


@pytest.mark.asyncio
async def test_disk_handler_mixin_calls_inserted_method() -> None:
    """Test that we notice when a disk is added."""
    st = StubHelper()

    assert st.times_disk_inserted == 0
    assert st.times_disk_removed == 0

    await st.dispatch(
        get_disk_manager_message(["foo"]),
    )

    assert st.times_disk_inserted == 1
    assert st.times_disk_removed == 0
    assert st._cur_disks == get_disk_info_list(["foo"])


@pytest.mark.asyncio
async def test_disk_handler_mixin_calls_removed_method() -> None:
    """Test that we notice when a disk is removed."""
    st = StubHelper()

    st._cur_disks = get_disk_info_list(["foo"])

    assert st.times_disk_inserted == 0
    assert st.times_disk_removed == 0

    await st.dispatch(
        get_disk_manager_message([]),
    )

    assert st.times_disk_inserted == 0
    assert st.times_disk_removed == 1
    assert st._cur_disks == get_disk_info_list([])


@pytest.mark.asyncio
async def test_disk_handler_mixin_swaps_disks() -> None:
    """Test that we notice when a disk is swapped."""
    st = StubHelper()

    st._cur_disks = get_disk_info_list(["foo"])

    assert st.times_disk_inserted == 0
    assert st.times_disk_removed == 0

    await st.dispatch(
        get_disk_manager_message(["bar"]),
    )

    assert st.times_disk_inserted == 1
    assert st.times_disk_removed == 1
    assert st._cur_disks == get_disk_info_list(["bar"])


@pytest.mark.asyncio
async def test_disk_handler_mixin_empty_message() -> None:
    """Test that we don't crash on an empty message."""
    st = StubHelper()
    await st.dispatch("")


@pytest.mark.asyncio
async def test_disk_handler_mixin_bad_json() -> None:
    """Test that we don't crash on bad JSON."""
    st = StubHelper()
    await st.dispatch("}bees?{")
