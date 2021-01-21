"""
Astoria command line interface.

Split up into one class per command.
"""
import click

from .event import event
from .list_disks import list_disks
from .metadata import show_metadata


@click.group("astdiskd")
def main() -> None:
    """Astoria Command Line Utility."""


main.add_command(event)
main.add_command(list_disks)
main.add_command(show_metadata)

if __name__ == "__main__":
    main()
