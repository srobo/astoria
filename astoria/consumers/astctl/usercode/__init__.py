"""Commands to interact with usercode."""
import click

from .kill import kill
from .restart import restart
from .show import show


@click.group("usercode")
def usercode() -> None:
    """Interact with Usercode."""


usercode.add_command(kill)
usercode.add_command(restart)
usercode.add_command(show)
