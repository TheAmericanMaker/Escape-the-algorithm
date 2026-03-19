"""Tests for YouTube parser."""

import tempfile
import unittest
from pathlib import Path

from eta.parsers.youtube import parse

FIXTURES = Path(__file__).parent / "fixtures"


class TestYouTubeParser(unittest.TestCase):
    def test_parse_subscriptions_csv(self):
        items = parse(FIXTURES / "subscriptions.csv")
        self.assertEqual(len(items), 3)

        self.assertEqual(items[0].title, "Raycevick")
        self.assertEqual(
            items[0].xml_url,
            "https://www.youtube.com/feeds/videos.xml?channel_id=UC1JTQBa5QxZCpXrFSkMxmPw",
        )
        self.assertEqual(
            items[0].html_url,
            "http://www.youtube.com/channel/UC1JTQBa5QxZCpXrFSkMxmPw",
        )
        self.assertEqual(items[0].category, "YouTube")

    def test_parse_empty_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("")
            f.flush()
            items = parse(Path(f.name))
        self.assertEqual(items, [])

    def test_parse_header_only(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("Channel Id,Channel Url,Channel Title\n")
            f.flush()
            items = parse(Path(f.name))
        self.assertEqual(items, [])

    def test_skips_short_rows(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("Channel Id,Channel Url,Channel Title\n")
            f.write("UC123\n")  # Too few columns
            f.write("UC456,http://example.com,Good Channel\n")
            f.flush()
            items = parse(Path(f.name))
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].title, "Good Channel")

    def test_fallback_title_to_channel_id(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("Channel Id,Channel Url,Channel Title\n")
            f.write("UC789,http://example.com,\n")
            f.flush()
            items = parse(Path(f.name))
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].title, "UC789")


if __name__ == "__main__":
    unittest.main()
