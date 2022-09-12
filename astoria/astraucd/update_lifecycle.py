"""Manage the lifecycle of a system update."""
from pathlib import Path
from typing import Callable

from astoria.common.update_state import UpdateState


class UpdateLifecycle:

    def __init__(
        self,
        update_file: Path,
        status_inform_callback: Callable[[UpdateState], None]
    ) -> None:
        self._update_file = update_file
        self._status_inform_callback = status_inform_callback

    async def run_process(self) -> None:
        """
        Start the execution of the update.

        This function will not return until the update has finished.
        """
        state = UpdateState(
            bundle_filename=self._update_file.name,
            progress_percentage=0,
        )
        self._status_inform_callback(state)
