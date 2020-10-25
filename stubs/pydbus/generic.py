"""Stubs for pydbus.generic."""

from typing import Any, Dict, List


class signal:
    ...

    def __call__(
            self,
            object: str,
            properties: Dict[str, Any],
            objects: List[Any],
    ) -> None: ...
