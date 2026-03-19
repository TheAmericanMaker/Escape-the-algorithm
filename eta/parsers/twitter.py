"""Parse Twitter/X following list from data archive export."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List

from eta.parsers import FeedItem

# Default Nitter instance for RSS feeds — user can override
NITTER_INSTANCE = "nitter.net"
TWITTER_RSS_URL = "https://{instance}/{username}/rss"
TWITTER_HTML_URL = "https://x.com/{username}"


def parse(path: Path, nitter_instance: str = NITTER_INSTANCE) -> List[FeedItem]:
    """Parse Twitter/X following list from data archive.

    Twitter data archives contain a file `data/following.js` with format:
        window.YTD.following.part0 = [ { "following": { "accountId": "...", "userLink": "..." } } ]

    Also supports:
    - Plain JSON array of objects with screenName/username fields
    - Simple text file with one @username per line
    """
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []

    # Try Twitter archive JS format first
    items = _parse_twitter_js(text, nitter_instance)
    if items is not None:
        return items

    # Try plain JSON
    items = _parse_json(text, nitter_instance)
    if items is not None:
        return items

    # Fall back to text list of usernames
    return _parse_text(text, nitter_instance)


def _parse_twitter_js(text: str, instance: str) -> List[FeedItem] | None:
    """Parse Twitter archive JS format (window.YTD.following.part0 = [...])."""
    match = re.match(r"^window\.YTD\.\w+\.part\d+\s*=\s*", text)
    if not match:
        return None

    json_str = text[match.end():]
    # Strip trailing semicolons
    json_str = json_str.rstrip().rstrip(";")

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        return None

    if not isinstance(data, list):
        return None

    items: list[FeedItem] = []
    for entry in data:
        if isinstance(entry, dict) and "following" in entry:
            following = entry["following"]
            username = _extract_username_from_entry(following)
            if username:
                items.append(_make_feed_item(username, instance))
        elif isinstance(entry, dict):
            username = _extract_username_from_entry(entry)
            if username:
                items.append(_make_feed_item(username, instance))

    return items


def _parse_json(text: str, instance: str) -> List[FeedItem] | None:
    """Parse a plain JSON array of user objects."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None

    if not isinstance(data, list):
        return None

    items: list[FeedItem] = []
    for entry in data:
        if isinstance(entry, dict):
            username = _extract_username_from_entry(entry)
            if username:
                items.append(_make_feed_item(username, instance))
        elif isinstance(entry, str):
            username = _clean_username(entry)
            if username:
                items.append(_make_feed_item(username, instance))

    return items if items else None


def _parse_text(text: str, instance: str) -> List[FeedItem]:
    """Parse a plain text list of usernames, one per line."""
    items: list[FeedItem] = []

    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        username = _clean_username(line)
        if username:
            items.append(_make_feed_item(username, instance))

    return items


def _extract_username_from_entry(entry: dict) -> str:
    """Extract a Twitter username from various field names."""
    # Try userLink field (Twitter archive format): "https://x.com/username"
    user_link = entry.get("userLink", "")
    if user_link:
        match = re.search(r"(?:twitter\.com|x\.com)/(\w+)", user_link)
        if match:
            return match.group(1)

    # Try common field names
    for key in ("screenName", "screen_name", "username", "name", "handle"):
        value = entry.get(key, "")
        if value and isinstance(value, str):
            return _clean_username(value)

    return ""


def _clean_username(value: str) -> str:
    """Clean a username string — strip @, validate."""
    value = value.strip().lstrip("@")

    # Extract from URLs
    match = re.search(r"(?:twitter\.com|x\.com)/(\w+)", value)
    if match:
        return match.group(1)

    # Validate: Twitter usernames are alphanumeric + underscores, max 15 chars
    if re.match(r"^\w{1,15}$", value):
        return value

    return ""


def _make_feed_item(username: str, instance: str) -> FeedItem:
    return FeedItem(
        title=f"@{username}",
        xml_url=TWITTER_RSS_URL.format(instance=instance, username=username),
        html_url=TWITTER_HTML_URL.format(username=username),
        category="Twitter",
    )
