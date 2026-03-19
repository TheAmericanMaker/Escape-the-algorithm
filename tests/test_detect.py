"""Tests for auto-detection of platform formats."""

import json
import tempfile
import unittest
from pathlib import Path

from eta.parsers.detect import detect_platform


class TestDetectPlatform(unittest.TestCase):
    def _write_temp(self, content: str, suffix: str = ".csv") -> Path:
        f = tempfile.NamedTemporaryFile(suffix=suffix, delete=False, mode="w")
        f.write(content)
        f.close()
        return Path(f.name)

    def test_detect_youtube_csv(self):
        path = self._write_temp("Channel Id,Channel Url,Channel Title\nUC123,http://x,Test\n")
        self.assertEqual(detect_platform(path), "youtube")

    def test_detect_youtube_by_url(self):
        path = self._write_temp("id,url,title\nUC123,http://www.youtube.com/channel/UC123,Test\n")
        self.assertEqual(detect_platform(path), "youtube")

    def test_detect_reddit_text(self):
        path = self._write_temp("r/python\nr/rust\nr/linux\n", suffix=".txt")
        self.assertEqual(detect_platform(path), "reddit")

    def test_detect_reddit_plain_names(self):
        path = self._write_temp("python\nrust\nlinux\nprogramming\n", suffix=".txt")
        self.assertEqual(detect_platform(path), "reddit")

    def test_detect_spotify_json(self):
        data = {"shows": [{"name": "Test Podcast"}]}
        path = self._write_temp(json.dumps(data), suffix=".json")
        self.assertEqual(detect_platform(path), "spotify")

    def test_detect_spotify_list(self):
        data = [{"name": "Podcast A", "uri": "spotify:show:123"}]
        path = self._write_temp(json.dumps(data), suffix=".json")
        self.assertEqual(detect_platform(path), "spotify")

    def test_unknown_format(self):
        path = self._write_temp("just random data !@#$", suffix=".xyz")
        self.assertIsNone(detect_platform(path))

    def test_empty_file(self):
        path = self._write_temp("", suffix=".csv")
        self.assertIsNone(detect_platform(path))


if __name__ == "__main__":
    unittest.main()
