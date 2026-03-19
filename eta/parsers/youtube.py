"""Parse YouTube subscriptions from Google Takeout CSV export."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import List

from eta.parsers import FeedItem

YOUTUBE_RSS_URL = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
YOUTUBE_CHANNEL_URL = "https://www.youtube.com/channel/{channel_id}"


def parse(path: Path) -> List[FeedItem]:
    """Parse a YouTube subscriptions.csv file from Google Takeout.

    The CSV has 3 columns (header names vary by locale, order is fixed):
      Column 0: Channel Id
      Column 1: Channel Url
      Column 2: Channel Title
    """
    items: list[FeedItem] = []

    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None:
            return items

        for row in reader:
            if len(row) < 3:
                continue

            channel_id = row[0].strip()
            channel_url = row[1].strip()
            channel_title = row[2].strip()

            if not channel_id:
                continue

            items.append(
                FeedItem(
                    title=channel_title or channel_id,
                    xml_url=YOUTUBE_RSS_URL.format(channel_id=channel_id),
                    html_url=channel_url or YOUTUBE_CHANNEL_URL.format(channel_id=channel_id),
                    category="YouTube",
                )
            )

    return items
