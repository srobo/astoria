"""Tests for astmetad message definitions."""
from astoria.common.ipc import MetadataManagerMessage
from astoria.common.metadata import Metadata


def test_metadata_manager_message_fields() -> None:
    """Test that the metadata manager message has the expected fields."""
    metadata = Metadata(
        astoria_version="0.0.0",
        kernel_version="5.0.0",
        arch="x64",
        python_version="3",
        libc_ver="2.0",
        os_name="Student Robotics OS",
        os_pretty_name="Student Robotics OS 2023.0.0",
        os_version="2023.0.0",
        usercode_entrypoint="robot.py",
    )

    mmm = MetadataManagerMessage(
        metadata=metadata,
        status=MetadataManagerMessage.Status.RUNNING,
    )

    assert mmm.metadata == metadata
