"""Auto-detect platform format from export files."""

from __future__ import annotations

import json
from pathlib import Path


def detect_platform(path: Path) -> str | None:
    """Detect which platform an export file came from.

    Returns "youtube", "reddit", "twitter", "tiktok", "spotify", or None.
    """
    suffix = path.suffix.lower()

    # JS files — Twitter archive format
    if suffix == ".js":
        try:
            text = path.read_text(encoding="utf-8")
            if text.strip().startswith("window.YTD.following"):
                return "twitter"
        except UnicodeDecodeError:
            pass
        return None

    # JSON files — could be Spotify or Twitter
    if suffix == ".json":
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                # TikTok: has Activity > Following List structure
                if "Activity" in data and isinstance(data.get("Activity"), dict):
                    activity = data["Activity"]
                    if "Following List" in activity:
                        return "tiktok"
                # TikTok: direct Following key
                if "Following" in data and isinstance(data["Following"], list):
                    return "tiktok"
                spotify_keys = {"shows", "podcasts", "podcastInteractionData", "followerCount"}
                if spotify_keys & set(data.keys()):
                    return "spotify"
            if isinstance(data, list) and data:
                first = data[0]
                # Twitter JSON: objects with screenName/following keys
                if isinstance(first, dict) and (
                    "following" in first or "screenName" in first or "screen_name" in first
                ):
                    return "twitter"
                if isinstance(first, dict) and (
                    "showName" in first
                    or "show_name" in first
                    or "spotifyUri" in first
                    or "uri" in first
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

        # Twitter: text with @ prefixed usernames or x.com/twitter.com URLs
        twitter_indicators = sum(
            1
            for l in (text.splitlines()[:20])
            if l.strip().startswith("@") or "twitter.com/" in l or "x.com/" in l
        )
        if twitter_indicators > 0:
            return "twitter"

        # Reddit: contains subreddit-like patterns
        # Check if lines look like subreddit names (alphanumeric, short, no spaces)
        lines = [l.strip() for l in text.splitlines() if l.strip() and not l.startswith("#")]
        if lines:
            # If lines contain r/ prefix or reddit.com URLs
            reddit_indicators = sum(
                1 for l in lines[:20] if l.startswith("r/") or "reddit.com/r/" in l
            )
            if reddit_indicators > 0:
                return "reddit"

            # If it's a CSV with a single column of short alphanumeric names
            if "," not in first_line:
                # Check if most lines look like subreddit names
                subreddit_like = sum(
                    1 for l in lines[:20] if l.replace("_", "").isalnum() and len(l) < 50
                )
                if subreddit_like > len(lines[:20]) * 0.7:
                    return "reddit"

    return None
