"""
Stubs for pydbus.bus.

The stubs in this file do not necessarily match the structure of pydbus.
"""
from typing import Any, Optional

from .publication import Publication
from .registration import ObjectRegistration


class Bus:
    """Represents a DBus Bus."""

    def get(self, bus_name: str, object: Optional[str] = None) -> Any: ...
    def publish(self, bus_name: str, *objects: Any) -> Publication: ...
    def register_object(self, bus_path: str, object: Any, node_info: Optional[str]) -> ObjectRegistration: ...


def SystemBus() -> Bus:
    """Connect to the system bus."""
    ...


def SessionBus() -> Bus:
    """Connect to the session bus."""
    ...
