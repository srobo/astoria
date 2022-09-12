"""State of an in-progress system update."""

import enum
from pathlib import Path

from pydantic import BaseModel


class UpdateMechanism(str, enum.Enum):
    """The update mechanism for the update."""

    RAUC = "rauc"


class UpdateState(BaseModel):
    """The state of an in-progress system update."""

    mechanism: UpdateMechanism
    update_file: Path
    progress_percentage: float
