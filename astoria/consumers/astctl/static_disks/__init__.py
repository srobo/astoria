"""Commands for managing static disks."""
import click

from .add import add


@click.group("static-disk")
def static_disk() -> None:
    """Interact with metadata."""


static_disk.add_command(add)
