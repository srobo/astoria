"""Commands to interact with metadata."""
import click

from .set import set
from .show import show


@click.group("metadata")
def metadata() -> None:
    """Interact with metadata."""


metadata.add_command(set)
metadata.add_command(show)
