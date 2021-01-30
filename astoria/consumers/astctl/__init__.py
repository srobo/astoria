"""
Astoria command line interface.

Split up into one class per command.
"""
import click

from .list_disks import list_disks
from .metadata import metadata
from .usercode import usercode


@click.group("astdiskd")
def main() -> None:
    """Astoria Command Line Utility."""


main.add_command(list_disks)
main.add_command(metadata)
main.add_command(usercode)

if __name__ == "__main__":
    main()
