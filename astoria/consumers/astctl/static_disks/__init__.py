"""Commands for managing static disks."""
import click

from .add import add
from .remove import remove
from .remove_all import remove_all


@click.group("static-disk")
def static_disk() -> None:
    """Interact with metadata."""


static_disk.add_command(add)
static_disk.add_command(remove)
static_disk.add_command(remove_all)
