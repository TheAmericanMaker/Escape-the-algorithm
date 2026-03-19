"""Tests for the Twitter/X parser."""

import json
import tempfile
import unittest
from pathlib import Path

from eta.parsers.twitter import parse

FIXTURES = Path(__file__).parent / "fixtures"


class TestTwitterParser(unittest.TestCase):
    def _write_temp(self, content: str, suffix: str = ".js") -> Path:
        f = tempfile.NamedTemporaryFile(suffix=suffix, delete=False, mode="w")
        f.write(content)
        f.close()
        return Path(f.name)

    def test_parse_twitter_archive_js(self):
        items = parse(FIXTURES / "following.js")
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0].title, "@elonmusk")
        self.assertIn("nitter.net/elonmusk/rss", items[0].xml_url)
        self.assertEqual(items[0].html_url, "https://x.com/elonmusk")
        self.assertEqual(items[0].category, "Twitter")

    def test_parse_json_array(self):
        data = [
            {"screenName": "torvalds"},
            {"screenName": "gabordemooij"},
        ]
        path = self._write_temp(json.dumps(data), suffix=".json")
        items = parse(path)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].title, "@torvalds")

    def test_parse_text_list(self):
        path = self._write_temp("@user1\n@user2\nuser3\n# comment\n", suffix=".txt")
        items = parse(path)
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0].title, "@user1")
        self.assertEqual(items[1].title, "@user2")
        self.assertEqual(items[2].title, "@user3")

    def test_skips_comments_and_blanks(self):
        path = self._write_temp("# my follows\n\n@user1\n\n", suffix=".txt")
        items = parse(path)
        self.assertEqual(len(items), 1)

    def test_empty_file(self):
        path = self._write_temp("", suffix=".txt")
        items = parse(path)
        self.assertEqual(len(items), 0)

    def test_handles_twitter_urls_in_text(self):
        path = self._write_temp(
            "https://twitter.com/torvalds\nhttps://x.com/gabordemooij\n",
            suffix=".txt",
        )
        items = parse(path)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].title, "@torvalds")
        self.assertEqual(items[1].title, "@gabordemooij")

    def test_rss_url_uses_nitter(self):
        path = self._write_temp("@testuser\n", suffix=".txt")
        items = parse(path)
        self.assertEqual(items[0].xml_url, "https://nitter.net/testuser/rss")

    def test_custom_nitter_instance(self):
        path = self._write_temp("@testuser\n", suffix=".txt")
        items = parse(path, nitter_instance="nitter.privacydev.net")
        self.assertEqual(items[0].xml_url, "https://nitter.privacydev.net/testuser/rss")


if __name__ == "__main__":
    unittest.main()
