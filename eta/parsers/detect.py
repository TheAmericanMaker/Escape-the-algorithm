"""Auto-detect platform format from export files."""

from __future__ import annotations

import json
from pathlib import Path


def detect_platform(path: Path) -> str | None:
    """Detect which platform an export file came from.

    Returns "youtube", "reddit", "spotify", or None if unrecognized.
    """
    suffix = path.suffix.lower()

    # JSON files — likely Spotify
    if suffix == ".json":
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                spotify_keys = {"shows", "podcasts", "podcastInteractionData", "followerCount"}
                if spotify_keys & set(data.keys()):
                    return "spotify"
            if isinstance(data, list) and data:
                first = data[0]
                if isinstance(first, dict) and (
                    "showName" in first or "show_name" in first
                    or "spotifyUri" in first or "uri" in first
                ):
                    return "spotify"
            # If it's a JSON list with name/title entries, still likely Spotify
            if isinstance(data, list) and data and isinstance(data[0], dict):
                if "name" in data[0] or "title" in data[0]:
                    return "spotify"
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
        return None

    # CSV or text files
    if suffix in (".csv", ".txt", ""):
        try:
            text = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            return None

        first_line = text.split("\n", 1)[0].strip().lower()

        # YouTube: CSV with Channel Id header or YouTube URLs
        if "channel id" in first_line or "channel_id" in first_line:
            return "youtube"
        if "youtube.com/channel/" in text[:2000]:
            return "youtube"

        # Reddit: contains subreddit-like patterns
        # Check if lines look like subreddit names (alphanumeric, short, no spaces)
        lines = [l.strip() for l in text.splitlines() if l.strip() and not l.startswith("#")]
        if lines:
            # If lines contain r/ prefix or reddit.com URLs
            reddit_indicators = sum(
                1 for l in lines[:20]
                if l.startswith("r/") or "reddit.com/r/" in l
            )
            if reddit_indicators > 0:
                return "reddit"

            # If it's a CSV with a single column of short alphanumeric names
            if "," not in first_line:
                # Check if most lines look like subreddit names
                subreddit_like = sum(
                    1 for l in lines[:20]
                    if l.replace("_", "").isalnum() and len(l) < 50
                )
                if subreddit_like > len(lines[:20]) * 0.7:
                    return "reddit"

    return None
