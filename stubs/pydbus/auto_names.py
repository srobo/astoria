"""Stubs for pydbus.auto_names."""

from typing import Optional


def auto_bus_name(bus_name: str) -> str: ...


def auto_object_path(bus_name: str, object_path: Optional[str] = None) -> str: ...
