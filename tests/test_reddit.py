"""Tests for Reddit parser."""

import tempfile
import unittest
from pathlib import Path

from eta.parsers.reddit import parse

FIXTURES = Path(__file__).parent / "fixtures"


class TestRedditParser(unittest.TestCase):
    def test_parse_text_file(self):
        items = parse(FIXTURES / "subreddits.txt")
        self.assertEqual(len(items), 4)

        names = [item.title for item in items]
        self.assertIn("r/python", names)
        self.assertIn("r/linux", names)
        self.assertIn("r/privacy", names)
        self.assertIn("r/selfhosted", names)

        for item in items:
            self.assertEqual(item.category, "Reddit")
            self.assertIn("reddit.com/r/", item.xml_url)
            self.assertTrue(item.xml_url.endswith(".rss"))

    def test_parse_csv_file(self):
        items = parse(FIXTURES / "subreddits.csv")
        self.assertEqual(len(items), 4)

    def test_parse_empty_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("")
            f.flush()
            items = parse(Path(f.name))
        self.assertEqual(items, [])

    def test_skips_comments(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("# comment\npython\n# another comment\nlinux\n")
            f.flush()
            items = parse(Path(f.name))
        self.assertEqual(len(items), 2)

    def test_handles_r_prefix(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("r/python\n")
            f.flush()
            items = parse(Path(f.name))
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].title, "r/python")

    def test_handles_full_url(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("https://www.reddit.com/r/privacy\n")
            f.flush()
            items = parse(Path(f.name))
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].title, "r/privacy")


if __name__ == "__main__":
    unittest.main()
