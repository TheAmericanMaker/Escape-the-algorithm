"""Parse TikTok following list from data export."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from eta.parsers import FeedItem

# Default ProxiTok instance for RSS feeds
PROXITOK_INSTANCE = "proxitok.pabloferreiro.es"
TIKTOK_RSS_URL = "https://{instance}/@{username}/rss"
TIKTOK_HTML_URL = "https://www.tiktok.com/@{username}"


def parse(path: Path, proxitok_instance: str = PROXITOK_INSTANCE) -> List[FeedItem]:
    """Parse TikTok following list from data export.

    TikTok data exports contain a JSON file (user_data.json) with structure:
        { "Activity": { "Following List": { "Following": [ ... ] } } }

    Also supports:
    - Plain JSON array of objects with UserName/username fields
    - Simple text file with one @username per line
    """
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []

    # Try JSON first
    try:
        data = json.loads(text)
        return _parse_json(data, proxitok_instance)
    except json.JSONDecodeError:
        pass

    # Fall back to text list
    return _parse_text(text, proxitok_instance)


def _parse_json(data: object, instance: str) -> List[FeedItem]:
    """Parse TikTok JSON export in various formats."""
    items: list[FeedItem] = []

    if isinstance(data, dict):
        # Official TikTok export: Activity > Following List > Following
        following = data.get("Activity", {}).get("Following List", {}).get("Following", [])
        if following:
            for entry in following:
                username = _extract_username(entry)
                if username:
                    items.append(_make_feed_item(username, instance))
            return items

        # Alternative paths in TikTok exports
        for key in ("Following", "following", "followingList"):
            if key in data and isinstance(data[key], list):
                for entry in data[key]:
                    username = _extract_username(entry)
                    if username:
                        items.append(_make_feed_item(username, instance))
                return items

    elif isinstance(data, list):
        for entry in data:
            if isinstance(entry, dict):
                username = _extract_username(entry)
                if username:
                    items.append(_make_feed_item(username, instance))
            elif isinstance(entry, str):
                username = _clean_username(entry)
                if username:
                    items.append(_make_feed_item(username, instance))

    return items


def _parse_text(text: str, instance: str) -> List[FeedItem]:
    """Parse a plain text list of TikTok usernames."""
    items: list[FeedItem] = []

    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        username = _clean_username(line)
        if username:
            items.append(_make_feed_item(username, instance))

    return items


def _extract_username(entry: dict) -> str:
    """Extract a TikTok username from various field names."""
    for key in ("UserName", "username", "user_name", "Username", "name"):
        value = entry.get(key, "")
        if value and isinstance(value, str):
            return _clean_username(value)

    # Try URL fields
    url = entry.get("url", entry.get("profileUrl", ""))
    if "tiktok.com/@" in url:
        parts = url.split("@", 1)
        if len(parts) == 2:
            username = parts[1].split("/")[0].split("?")[0]
            if username:
                return username

    return ""


def _clean_username(value: str) -> str:
    """Clean a TikTok username — strip @, validate."""
    value = value.strip().lstrip("@")

    # Extract from TikTok URLs
    if "tiktok.com/@" in value:
        parts = value.split("@", 1)
        if len(parts) == 2:
            value = parts[1].split("/")[0].split("?")[0]

    # TikTok usernames: letters, numbers, underscores, periods
    if value and all(c.isalnum() or c in "_." for c in value):
        return value

    return ""


def _make_feed_item(username: str, instance: str) -> FeedItem:
    return FeedItem(
        title=f"@{username}",
        xml_url=TIKTOK_RSS_URL.format(instance=instance, username=username),
        html_url=TIKTOK_HTML_URL.format(username=username),
        category="TikTok",
    )
