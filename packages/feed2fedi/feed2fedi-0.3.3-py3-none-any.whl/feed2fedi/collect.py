"""Classes and methods to collect information needed by Feed2Fedi to make posts on Fediverse instance."""
import asyncio
import os
import re
from pathlib import Path
from typing import Any
from typing import Final
from typing import List
from typing import Optional
from urllib.parse import urlsplit

import aiohttp
import feedparser


class FeedReader:
    """Instances hold feed items for RSS/Atom feeds passed during instanciation."""

    def __init__(self, feeds: List[str]) -> None:
        self.items: List[feedparser.FeedParserDict] = []
        for feed in feeds:
            feed_info = feedparser.parse(feed)
            self.items.extend(feed_info.entries)

    @staticmethod
    def determine_image_url(item: feedparser.FeedParserDict) -> Optional[str]:
        """Determine URL for article image.

        :param item: Item to determine an image URL for
        :returns:
            None or string with URL to article image
        """
        MEDIA_KEYS: Final[List[str]] = ["media_thumbnail", "media_content"]
        SUMMARY_REGEXS: Final[List[str]] = [
            "<img .*?src=.*? *?/>",
            'src=.*?".*?"',
            '".*?"',
        ]

        for media_key in MEDIA_KEYS:
            if item.get(media_key) and item.get(media_key)[0].get("url"):
                return str(item.get(media_key)[0].get("url"))

        if (url := item.get("summary")) and "<img" in url:
            for regex in SUMMARY_REGEXS:
                match = re.search(
                    pattern=regex,
                    string=url,
                    flags=re.IGNORECASE,
                )
                if not match or not (url := match.group()):
                    return None
            return str(url)[1:-1]

        if links := item.get("links"):
            for link in links:
                if (link_type := link.get("type")) and "image" in link_type:
                    return str(link.get("href"))

        return None


async def get_file(
    img_url: str,
    file: Any,
) -> Optional[str]:
    """Save a file located at img_url to a file located at filepath.

    :param img_url: url of imgur image to download
    :param file: File to write image to

    :returns:
        mime_type (string): mimetype as returned from URL
    """
    mime_type = await determine_mime_type(img_url=img_url)

    chunk_size = 64 * 1024
    try:
        if not mime_type:
            return None

        async with aiohttp.ClientSession(raise_for_status=True) as client:
            response = await client.get(url=img_url)
            async for data_chunk in response.content.iter_chunked(chunk_size):
                file.write(data_chunk)
            await asyncio.sleep(0)  # allow client session to close before continuing

        return mime_type

    except aiohttp.ClientError as save_image_error:
        print(
            "collect.py - get_file(...) -> None - download failed with: %s"
            % save_image_error,
        )

    return None


async def determine_mime_type(img_url: str) -> Optional[str]:
    """Determine suitable filename for an image based on URL.

    :param img_url: URL to image to determine a file name for.
    :returns:
        mime-type in a String or None
    """
    # First check if URL starts with http:// or https://
    regex = r"^https?://"
    match = re.search(regex, img_url, flags=0)
    if not match:
        print("Post link is not a full link: %s" % img_url)
        return None

    # Acceptable image formats
    image_formats = (
        "image/png",
        "image/jpeg",
        "image/gif",
        "image/webp",
        "video/mp4",
    )

    file_name = Path(os.path.basename(urlsplit(img_url).path))

    # Determine mime type of linked media
    try:
        async with aiohttp.ClientSession(
            raise_for_status=True,
            read_timeout=30,
        ) as client:
            response = await client.head(url=img_url)
            headers = response.headers
            content_type = headers.get("content-type", None)

    except (aiohttp.ClientError, asyncio.exceptions.TimeoutError) as error:
        print("Error while opening URL: %s " % error)
        return None

    if content_type in image_formats:
        return str(content_type)

    if content_type == "application/octet-stream" and file_name.suffix == ".webp":
        return "image/webp"

    print("URL does not point to a valid image file: %s" % img_url)
    return None
