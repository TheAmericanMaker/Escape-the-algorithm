"""Parse Reddit subscriptions from GDPR data export or text list."""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import List

from eta.parsers import FeedItem

REDDIT_RSS_URL = "https://www.reddit.com/r/{subreddit}/.rss"
REDDIT_HTML_URL = "https://www.reddit.com/r/{subreddit}"


def parse(path: Path) -> List[FeedItem]:
    """Parse Reddit subscriptions from a CSV export or plain text file.

    Supports:
    - Reddit GDPR CSV export (subscribed_subreddits.csv)
    - Plain text file with one subreddit name per line (e.g. "python")
    - Plain text with r/ prefix (e.g. "r/python")
    - Plain text with full URLs (e.g. "https://www.reddit.com/r/python")
    """
    text = path.read_text(encoding="utf-8-sig").strip()
    if not text:
        return []

    # Try CSV first
    if "," in text.split("\n")[0]:
        return _parse_csv(path)

    # Fall back to text list
    return _parse_text(text)


def _parse_csv(path: Path) -> List[FeedItem]:
    """Parse Reddit GDPR CSV export."""
    items: list[FeedItem] = []

    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None:
            return items

        for row in reader:
            if not row:
                continue
            # Try each column for a subreddit name
            for cell in row:
                subreddit = _extract_subreddit(cell)
                if subreddit:
                    items.append(_make_feed_item(subreddit))
                    break

    return items


def _parse_text(text: str) -> List[FeedItem]:
    """Parse a plain text list of subreddits."""
    items: list[FeedItem] = []

    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        subreddit = _extract_subreddit(line)
        if subreddit:
            items.append(_make_feed_item(subreddit))

    return items


def _extract_subreddit(value: str) -> str:
    """Extract a subreddit name from various formats."""
    value = value.strip()

    # Full URL: https://www.reddit.com/r/python or reddit.com/r/python
    match = re.search(r"reddit\.com/r/([A-Za-z0-9_]+)", value)
    if match:
        return match.group(1)

    # r/subreddit format
    match = re.match(r"r/([A-Za-z0-9_]+)", value)
    if match:
        return match.group(1)

    # Plain subreddit name (alphanumeric + underscores only)
    if re.match(r"^[A-Za-z0-9_]+$", value):
        return value

    return ""


def _make_feed_item(subreddit: str) -> FeedItem:
    return FeedItem(
        title=f"r/{subreddit}",
        xml_url=REDDIT_RSS_URL.format(subreddit=subreddit),
        html_url=REDDIT_HTML_URL.format(subreddit=subreddit),
        category="Reddit",
    )
