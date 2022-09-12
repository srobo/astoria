"""State of an in-progress system update."""

import enum

from pydantic import BaseModel


class UpdateMechanism(str, enum.Enum):
    """The update mechanism for the update."""

    RAUC = "rauc"


class UpdateState(BaseModel):
    """The state of an in-progress system update."""

    mechanism: UpdateMechanism = UpdateMechanism.RAUC
    bundle_filename: str
    progress_percentage: float
