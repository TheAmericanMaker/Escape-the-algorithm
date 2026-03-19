"""Tests for the TikTok parser."""

import json
import tempfile
import unittest
from pathlib import Path

from eta.parsers.tiktok import parse

FIXTURES = Path(__file__).parent / "fixtures"


class TestTikTokParser(unittest.TestCase):
    def _write_temp(self, content: str, suffix: str = ".json") -> Path:
        f = tempfile.NamedTemporaryFile(suffix=suffix, delete=False, mode="w")
        f.write(content)
        f.close()
        return Path(f.name)

    def test_parse_official_export(self):
        items = parse(FIXTURES / "tiktok_following.json")
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0].title, "@charlidamelio")
        self.assertIn("proxitok", items[0].xml_url)
        self.assertIn("@charlidamelio", items[0].xml_url)
        self.assertEqual(items[0].html_url, "https://www.tiktok.com/@charlidamelio")
        self.assertEqual(items[0].category, "TikTok")

    def test_parse_json_list(self):
        data = [{"UserName": "user1"}, {"UserName": "user2"}]
        path = self._write_temp(json.dumps(data))
        items = parse(path)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].title, "@user1")

    def test_parse_text_list(self):
        path = self._write_temp("@user1\n@user2\nuser3\n# comment\n", suffix=".txt")
        items = parse(path)
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0].title, "@user1")
        self.assertEqual(items[2].title, "@user3")

    def test_empty_file(self):
        path = self._write_temp("")
        items = parse(path)
        self.assertEqual(len(items), 0)

    def test_empty_following_list(self):
        data = {"Activity": {"Following List": {"Following": []}}}
        path = self._write_temp(json.dumps(data))
        items = parse(path)
        self.assertEqual(len(items), 0)

    def test_skips_entries_without_username(self):
        data = [{"UserName": "valid"}, {"other": "field"}, {"UserName": "also_valid"}]
        path = self._write_temp(json.dumps(data))
        items = parse(path)
        self.assertEqual(len(items), 2)

    def test_handles_tiktok_url(self):
        data = [{"url": "https://www.tiktok.com/@cooluser/video/123"}]
        path = self._write_temp(json.dumps(data))
        items = parse(path)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].title, "@cooluser")

    def test_custom_proxitok_instance(self):
        path = self._write_temp("@testuser\n", suffix=".txt")
        items = parse(path, proxitok_instance="proxitok.example.com")
        self.assertEqual(items[0].xml_url, "https://proxitok.example.com/@testuser/rss")


if __name__ == "__main__":
    unittest.main()
