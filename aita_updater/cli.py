# _*_ coding: utf-8 _*_

"""Console script for aita_updater."""
import sys
import click
from aita_updater.session import Session


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
    posts = reddit_session.get_posts(100)
    parsed_results = reddit_session.update_results(posts)
    results_df = reddit_session.convert_results()
    return


if __name__ == "__main__":
    sys.exit(main()) # pragma: no cover
