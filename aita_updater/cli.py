# _*_ coding: utf-8 _*_

"""Console script for aita_updater."""
import sys
import click
from aita_updater.session import Session
from aita_updater.processors import RedditProcessor
from logging.config import fileConfig

fileConfig('logging.ini')


@click.group()
def main(args=None):
    """console script for aita_updater."""
    return 0


@main.command()
def get_results():
    """
    get sample data
    """
    reddit_session = Session('AmItheAsshole')
    session_data = reddit_session.get_posts(5)
    exit()
    processor = RedditProcessor(session_data)
    processor.run()
    return


if __name__ == "__main__":
    sys.exit(main()) # pragma: no cover
