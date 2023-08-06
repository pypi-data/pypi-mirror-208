"""Classes and methods needed to publish posts on a Fediverse instance."""
import asyncio
import tempfile
import traceback
from typing import List
from typing import Optional

import aiohttp
import arrow
from feedparser import FeedParserDict
from minimal_activitypub.client_2_server import ActivityPub
from minimal_activitypub.client_2_server import ClientError
from minimal_activitypub.client_2_server import RatelimitError

from .collect import FeedReader
from .collect import get_file
from .control import Configuration
from .control import PostRecorder


class Fediverse:
    """Helper class to publish posts on a fediverse instance from rss feed items."""

    def __init__(self, config: Configuration, post_recorder: PostRecorder) -> None:
        self.config = config
        self.post_recorder = post_recorder

    async def publish(self, items: List[FeedParserDict]) -> None:
        """Publish posts to fediverse instance from content in the items list.

        :param items: Rss feed items to post
        """
        async with aiohttp.ClientSession() as session:
            fediverse = ActivityPub(
                instance=self.config.fedi_instance,
                session=session,
                access_token=self.config.fedi_access_token,
            )
            await fediverse.determine_instance_type()
            await fediverse.verify_credentials()

            for item in items:
                if await self.post_recorder.duplicate_check(identifier=item.link):
                    continue

                status = f"{item.title}\n\n{item.link}"
                media_ids: Optional[List[str]] = None

                try:
                    # Post media if configured to and media_thumbnail is present with a url
                    if self.config.bot_post_media:
                        media_ids = await Fediverse._post_media(
                            fediverse=fediverse,
                            item=item,
                        )

                    posted_status = await fediverse.post_status(
                        status=status,
                        visibility=self.config.bot_post_visibility.value,
                        media_ids=media_ids,
                    )

                    print(
                        f"Posted {item.title} to Fediverse at\n{posted_status['url']}"
                    )

                    await self.post_recorder.log_post(shared_url=item.link)

                except RatelimitError:
                    reset = fediverse.ratelimit_reset
                    seconds = reset.timestamp() - arrow.now().timestamp()
                    print(
                        f'!!! Server "cool down" - waiting for {seconds} seconds (until {reset})'
                    )
                    await asyncio.sleep(delay=seconds)

                except ClientError as error:
                    print(f"!!! Encountered error: {error}")
                    traceback.print_tb(error.__traceback__)
                    print("\nLog article to avoid repeat of error")
                    await self.post_recorder.log_post(shared_url=item.link)

    @staticmethod
    async def _post_media(
        fediverse: ActivityPub,
        item: FeedParserDict,
    ) -> Optional[List[str]]:
        """Post media to fediverse instance and return media ID.

        :param fediverse: ActivityPub api instance
        :param item: Feed item to load media from
        :returns:
            None or List containing one string of the media id after upload
        """
        if media_url := FeedReader.determine_image_url(item):
            with tempfile.TemporaryFile() as temp_image_file:
                mime_type = await get_file(img_url=media_url, file=temp_image_file)
                if mime_type:
                    temp_image_file.seek(0)
                    media = await fediverse.post_media(
                        file=temp_image_file,
                        mime_type=mime_type,
                    )
                    return [media["id"]]

        return None
