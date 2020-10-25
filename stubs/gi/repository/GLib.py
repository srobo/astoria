"""Type stubs for gi.repository.GLib."""


class Error(Exception):
    """Horrific GLib Error God Object."""

    @property
    def message(self) -> str: ...


class MainLoop:

    def run(self) -> None: ...

    def quit(self) -> None: ...