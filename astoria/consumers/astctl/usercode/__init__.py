"""Commands to interact with usercode."""
import click

from .kill import kill
from .restart import restart


@click.group("usercode")
def usercode() -> None:
    """Interact with Usercode."""


usercode.add_command(kill)
usercode.add_command(restart)
