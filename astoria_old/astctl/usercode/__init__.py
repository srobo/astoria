"""Commands to interact with usercode."""
import click

from .kill import kill
from .log import log
from .restart import restart
from .show import show
from .trigger import trigger


@click.group("usercode")
def usercode() -> None:
    """Interact with Usercode."""


usercode.add_command(kill)
usercode.add_command(log)
usercode.add_command(restart)
usercode.add_command(show)
usercode.add_command(trigger)
