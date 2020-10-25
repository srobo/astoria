"""Type stubs for pydbus.publication."""

from typing import Any

from pydbus.bus import Bus


class Publication:

    def __init__(
            self,
            bus: Bus,
            bus_name: str,
            *objects: Any,
            allow_replacement: bool = True,
            replace: bool = False,
    ) -> None: ...

    def unpublish(self) -> None:
        """Actually a method made by ExitableWithAliases."""
        ...
