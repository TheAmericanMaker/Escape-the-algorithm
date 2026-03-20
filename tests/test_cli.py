"""Tests for the CLI."""

import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from eta.cli import main

FIXTURES = Path(__file__).parent / "fixtures"


class TestCLI(unittest.TestCase):
    def test_no_command_returns_1(self):
        result = main([])
        self.assertEqual(result, 1)

    def test_version(self):
        with self.assertRaises(SystemExit) as ctx:
            main(["--version"])
        self.assertEqual(ctx.exception.code, 0)

    def test_youtube_command(self):
        with tempfile.NamedTemporaryFile(suffix=".opml", delete=False) as f:
            output = Path(f.name)

        result = main(["youtube", str(FIXTURES / "subscriptions.csv"), "-o", str(output)])
        self.assertEqual(result, 0)
        self.assertTrue(output.exists())

        root = ET.parse(output).getroot()
        rss_feeds = [f for f in root.iter("outline") if f.get("type") == "rss"]
        self.assertEqual(len(rss_feeds), 3)

    def test_reddit_command(self):
        with tempfile.NamedTemporaryFile(suffix=".opml", delete=False) as f:
            output = Path(f.name)

        result = main(["reddit", str(FIXTURES / "subreddits.txt"), "-o", str(output)])
        self.assertEqual(result, 0)
        self.assertTrue(output.exists())

    def test_spotify_command(self):
        with tempfile.NamedTemporaryFile(suffix=".opml", delete=False) as f:
            output = Path(f.name)

        result = main(["spotify", str(FIXTURES / "spotify_podcasts.json"), "-o", str(output)])
        self.assertEqual(result, 0)
        self.assertTrue(output.exists())

    def test_twitter_command(self):
        with tempfile.NamedTemporaryFile(suffix=".opml", delete=False) as f:
            output = Path(f.name)

        result = main(["twitter", str(FIXTURES / "following.js"), "-o", str(output)])
        self.assertEqual(result, 0)
        self.assertTrue(output.exists())

    def test_tiktok_command(self):
        with tempfile.NamedTemporaryFile(suffix=".opml", delete=False) as f:
            output = Path(f.name)

        result = main(["tiktok", str(FIXTURES / "tiktok_following.json"), "-o", str(output)])
        self.assertEqual(result, 0)
        self.assertTrue(output.exists())

        root = ET.parse(output).getroot()
        rss_feeds = [f for f in root.iter("outline") if f.get("type") == "rss"]
        self.assertEqual(len(rss_feeds), 3)

    def test_merge_command(self):
        with (
            tempfile.NamedTemporaryFile(suffix=".opml", delete=False) as f1,
            tempfile.NamedTemporaryFile(suffix=".opml", delete=False) as f2,
            tempfile.NamedTemporaryFile(suffix=".opml", delete=False) as out,
        ):
            yt_out = Path(f1.name)
            rd_out = Path(f2.name)
            merged_out = Path(out.name)

        main(["youtube", str(FIXTURES / "subscriptions.csv"), "-o", str(yt_out)])
        main(["reddit", str(FIXTURES / "subreddits.txt"), "-o", str(rd_out)])

        result = main(["merge", str(yt_out), str(rd_out), "-o", str(merged_out)])
        self.assertEqual(result, 0)

        root = ET.parse(merged_out).getroot()
        rss_feeds = [f for f in root.iter("outline") if f.get("type") == "rss"]
        self.assertEqual(len(rss_feeds), 7)  # 3 YouTube + 4 Reddit

    def test_missing_file_returns_1(self):
        result = main(["youtube", "/nonexistent/file.csv"])
        self.assertEqual(result, 1)

    def test_dry_run_does_not_write(self):
        output = Path(tempfile.mktemp(suffix=".opml"))
        result = main(
            [
                "youtube",
                str(FIXTURES / "subscriptions.csv"),
                "-o",
                str(output),
                "--dry-run",
            ]
        )
        self.assertEqual(result, 0)
        self.assertFalse(output.exists())

    def test_verbose_flag(self):
        with tempfile.NamedTemporaryFile(suffix=".opml", delete=False) as f:
            output = Path(f.name)

        result = main(
            [
                "youtube",
                str(FIXTURES / "subscriptions.csv"),
                "-o",
                str(output),
                "--verbose",
            ]
        )
        self.assertEqual(result, 0)

    def test_convert_auto_detect_youtube(self):
        with tempfile.NamedTemporaryFile(suffix=".opml", delete=False) as f:
            output = Path(f.name)

        result = main(["convert", str(FIXTURES / "subscriptions.csv"), "-o", str(output)])
        self.assertEqual(result, 0)
        self.assertTrue(output.exists())

        root = ET.parse(output).getroot()
        rss_feeds = [f for f in root.iter("outline") if f.get("type") == "rss"]
        self.assertEqual(len(rss_feeds), 3)

    def test_convert_auto_detect_spotify(self):
        with tempfile.NamedTemporaryFile(suffix=".opml", delete=False) as f:
            output = Path(f.name)

        result = main(["convert", str(FIXTURES / "spotify_podcasts.json"), "-o", str(output)])
        self.assertEqual(result, 0)

    def test_convert_unknown_format(self):
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False, mode="w") as f:
            f.write("random nonsense data !@#$%^")
            unknown = Path(f.name)

        result = main(["convert", str(unknown)])
        self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
