"""Resolve podcast RSS feed URLs via the Podcast Index API.

https://podcastindex-org.github.io/docs-api/

Requires a free API key pair from https://api.podcastindex.org
Set via environment variables:
    PODCAST_INDEX_KEY    — your API key
    PODCAST_INDEX_SECRET — your API secret
"""

from __future__ import annotations

import hashlib
import os
import sys
import time
from typing import List
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

import json

from eta.parsers import FeedItem

API_BASE = "https://api.podcastindex.org/api/1.0"
USER_AGENT = "EscapeTheAlgorithm/0.2 (+https://github.com/TheAmericanMaker/Escape-the-algorithm)"


def _get_credentials() -> tuple[str, str]:
    """Get API key and secret from environment."""
    key = os.environ.get("PODCAST_INDEX_KEY", "")
    secret = os.environ.get("PODCAST_INDEX_SECRET", "")
    if not key or not secret:
        raise ValueError(
            "Podcast Index API credentials required.\n"
            "  Get free keys at: https://api.podcastindex.org\n"
            "  Then set: PODCAST_INDEX_KEY and PODCAST_INDEX_SECRET"
        )
    return key, secret


def _auth_headers(key: str, secret: str) -> dict[str, str]:
    """Build the authentication headers for a Podcast Index API request."""
    ts = str(int(time.time()))
    auth_hash = hashlib.sha1((key + secret + ts).encode()).hexdigest()
    return {
        "X-Auth-Key": key,
        "X-Auth-Date": ts,
        "Authorization": auth_hash,
        "User-Agent": USER_AGENT,
    }


def search_by_title(title: str, key: str, secret: str) -> str:
    """Search Podcast Index for a podcast by title, return the best-match feed URL.

    Returns the feedUrl of the first result, or empty string if no match.
    """
    url = f"{API_BASE}/search/bytitle?q={quote_plus(title)}"
    headers = _auth_headers(key, secret)

    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
    except (HTTPError, URLError, TimeoutError):
        return ""

    feeds = data.get("feeds", [])
    if not feeds:
        return ""

    # Try exact title match first (case-insensitive)
    title_lower = title.lower().strip()
    for feed in feeds:
        if feed.get("title", "").lower().strip() == title_lower:
            return feed.get("feedUrl", "")

    # Fall back to first result
    return feeds[0].get("feedUrl", "")


def resolve_feeds(
    items: List[FeedItem],
    key: str | None = None,
    secret: str | None = None,
    on_progress: object = None,
) -> List[FeedItem]:
    """Resolve RSS feed URLs for FeedItems that are missing them.

    Args:
        items: List of FeedItem objects (modified in place and returned)
        key: API key (falls back to env var)
        secret: API secret (falls back to env var)
        on_progress: Optional callable(index, total, title, feed_url) for progress

    Returns the same list with xml_url populated where possible.
    """
    if key is None or secret is None:
        env_key, env_secret = _get_credentials()
        key = key or env_key
        secret = secret or env_secret

    needs_resolve = [(i, item) for i, item in enumerate(items) if not item.xml_url]

    for count, (idx, item) in enumerate(needs_resolve):
        feed_url = search_by_title(item.title, key, secret)
        if feed_url:
            items[idx] = FeedItem(
                title=item.title,
                xml_url=feed_url,
                html_url=item.html_url,
                category=item.category,
            )

        if callable(on_progress):
            on_progress(count + 1, len(needs_resolve), item.title, feed_url)

    return items
