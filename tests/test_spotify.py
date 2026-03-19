"""Tests for Spotify parser."""

import json
import tempfile
import unittest
from pathlib import Path

from eta.parsers.spotify import parse

FIXTURES = Path(__file__).parent / "fixtures"


class TestSpotifyParser(unittest.TestCase):
    def test_parse_podcast_list(self):
        items = parse(FIXTURES / "spotify_podcasts.json")
        self.assertEqual(len(items), 3)

        names = [item.title for item in items]
        self.assertIn("Darknet Diaries", names)
        self.assertIn("The Changelog", names)
        self.assertIn("Acquired", names)

        for item in items:
            self.assertEqual(item.category, "Podcasts")
            self.assertEqual(item.xml_url, "")  # Spotify doesn't provide RSS

    def test_spotify_uri_to_url(self):
        items = parse(FIXTURES / "spotify_podcasts.json")
        darknet = next(i for i in items if i.title == "Darknet Diaries")
        self.assertEqual(
            darknet.html_url,
            "https://open.spotify.com/show/4XPl3uEEL9HkA2FahKZfDB",
        )

    def test_direct_url_preserved(self):
        items = parse(FIXTURES / "spotify_podcasts.json")
        changelog = next(i for i in items if i.title == "The Changelog")
        self.assertEqual(
            changelog.html_url,
            "https://open.spotify.com/show/5bBki72YeKSLUqyRefELlJ",
        )

    def test_empty_list(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump([], f)
            f.flush()
            items = parse(Path(f.name))
        self.assertEqual(items, [])

    def test_dict_with_shows_key(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"shows": [{"name": "Test Show", "uri": "spotify:show:abc123"}]}, f)
            f.flush()
            items = parse(Path(f.name))
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].title, "Test Show")

    def test_skips_entries_without_name(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump([{"uri": "spotify:show:abc123"}, {"name": "Good Show"}], f)
            f.flush()
            items = parse(Path(f.name))
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].title, "Good Show")


if __name__ == "__main__":
    unittest.main()
