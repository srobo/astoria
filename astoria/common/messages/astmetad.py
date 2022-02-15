"""Types for astmetad."""
from astoria.common.ipc import ManagerMessage
from astoria.common.metadata import Metadata


class MetadataManagerMessage(ManagerMessage):
    """
    Status message for Metadata Manager.

    Published to /astoria/astmetad
    """

    metadata: Metadata
