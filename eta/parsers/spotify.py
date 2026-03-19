"""Parse Spotify followed podcasts from privacy data export."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from eta.parsers import FeedItem

SPOTIFY_SHOW_URL = "https://open.spotify.com/show/{show_id}"


def parse(path: Path) -> List[FeedItem]:
    """Parse Spotify followed podcasts/shows from data export JSON.

    Spotify's data export includes a file (typically Follow.json or
    YourLibrary.json) containing followed podcasts. The exact format
    varies but we handle common structures.

    Note: Spotify does not include RSS feed URLs in their export.
    The xml_url field will be empty. Users should look up RSS feeds
    via podcastindex.org or their preferred podcast directory.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    items: list[FeedItem] = []

    # Handle various Spotify export formats
    if isinstance(data, list):
        # Direct list of shows/podcasts
        for entry in data:
            item = _parse_entry(entry)
            if item:
                items.append(item)
    elif isinstance(data, dict):
        # Look for podcast/show data in known keys
        for key in ("followerCount", "podcastInteractionData", "shows", "podcasts"):
            if key in data and isinstance(data[key], list):
                for entry in data[key]:
                    item = _parse_entry(entry)
                    if item:
                        items.append(item)
                break
        else:
            # Try the whole dict as a single entry
            item = _parse_entry(data)
            if item:
                items.append(item)

    return items


def _parse_entry(entry: dict) -> FeedItem | None:
    """Parse a single podcast/show entry."""
    if not isinstance(entry, dict):
        return None

    # Try various field names for the show title
    name = (
        entry.get("name")
        or entry.get("showName")
        or entry.get("show_name")
        or entry.get("title")
        or ""
    )
    if not name:
        return None

    # Try to extract a Spotify URL or URI
    uri = entry.get("uri", entry.get("spotifyUri", ""))
    url = entry.get("url", entry.get("showUrl", ""))

    html_url = url
    if not html_url and uri:
        # Convert spotify:show:XXXXX to URL
        parts = uri.split(":")
        if len(parts) == 3 and parts[1] == "show":
            html_url = SPOTIFY_SHOW_URL.format(show_id=parts[2])

    return FeedItem(
        title=name.strip(),
        xml_url="",  # Spotify doesn't provide RSS URLs
        html_url=html_url,
        category="Podcasts",
    )
