# _*_ coding: utf-8 _*_

"""Console script for aita_updater."""
import sys
import click
from aita_updater.aita_updater import func1


@click.command()
def main(args=None):
    """console script for aita_updater."""
    click.echo("Hello, what would you like to search for?")
    return 0

@click.command()
def get_results():
    """
    get sample data
    """
    pass

if __name__ == "__main__":
    sys.exit(main()) # pragma: no cover
