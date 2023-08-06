"""Main processing and main entry point methods for Feed2Fedi."""
import asyncio
import sys
import traceback
from pathlib import Path

import click
from minimal_activitypub.client_2_server import ActivityPubError

from . import DISPLAY_NAME
from . import __version__
from .collect import FeedReader
from .control import Configuration
from .control import PostRecorder
from .publish import Fediverse


async def main(config_file: Path):
    """Read configuration and feeds, then make posts while avoiding duplicates.

    :param config_file: Path and file name of file to use for reading and storing configuration from
    """
    error_encountered = False

    print(f"Welcome to {DISPLAY_NAME} {__version__}")

    config = await Configuration.load_config(config_file_path=Path(config_file))

    post_recorder = PostRecorder(history_db_path=config.cache_db_path)
    await post_recorder.db_init()
    await post_recorder.prune(max_age_in_days=config.cache_max_age)

    items = FeedReader(feeds=config.feeds).items

    fediverse = Fediverse(config=config, post_recorder=post_recorder)
    try:
        await fediverse.publish(items=items)
    except ActivityPubError as publishing_error:
        error_encountered = True
        print(
            f"Encountered the following error during publishing feed items:\n{publishing_error}"
        )
        traceback.print_tb(publishing_error.__traceback__)

    await post_recorder.close_db()

    if error_encountered:
        sys.exit(1)


async def import_urls(config_file: Path, url_file: Path) -> None:
    """Start import of URLS into cache db.

    :param config_file: Path and file name of file to use for reading and storing configuration from
    :param url_file: Path and file name to file to be imported
    """
    print(f"Welcome to {DISPLAY_NAME} {__version__}")
    print("\nImporting URLS into cache db from ...")

    config = await Configuration.load_config(config_file_path=Path(config_file))

    post_recorder = PostRecorder(history_db_path=config.cache_db_path)
    await post_recorder.db_init()

    await post_recorder.import_urls(url_file=Path(url_file))

    await post_recorder.close_db()


@click.command()
@click.option(
    "-c",
    "--config-file",
    help="Path and file name to the config file",
    default="config.ini",
    type=click.Path(
        file_okay=True,
        dir_okay=False,
        writable=True,
    ),
)
def start_main(config_file: Path) -> None:
    """Start processing, i.e. main entry point."""
    asyncio.run(main(config_file=config_file))


@click.command()
@click.option(
    "-c",
    "--config-file",
    help="Path and file name to the config file",
    default="config.ini",
    type=click.Path(
        file_okay=True,
        dir_okay=False,
        writable=True,
    ),
)
@click.option(
    "-f",
    "--url-file",
    help="Path and file name to file to be imported. It should contain one URL per line",
    required=True,
    type=click.Path(
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
)
def start_import(config_file: Path, url_file: Path) -> None:
    """Start import of URLS into cache db.

    :param config_file: Path and file name of file to use for reading and storing configuration from
    :param url_file: Path and file name to file to be imported
    """
    asyncio.run(import_urls(config_file=config_file, url_file=url_file))
