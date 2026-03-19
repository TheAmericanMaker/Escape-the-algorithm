"""Tests for OPML exporter."""

import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from eta.exporters.opml import generate_opml, merge_opml, parse_opml, write_opml
from eta.parsers import FeedItem


class TestOPMLExporter(unittest.TestCase):
    def setUp(self):
        self.items = [
            FeedItem(
                title="Raycevick",
                xml_url="https://www.youtube.com/feeds/videos.xml?channel_id=UC1",
                html_url="http://www.youtube.com/channel/UC1",
                category="YouTube",
            ),
            FeedItem(
                title="r/python",
                xml_url="https://www.reddit.com/r/python/.rss",
                html_url="https://www.reddit.com/r/python",
                category="Reddit",
            ),
        ]

    def test_generate_valid_xml(self):
        xml_str = generate_opml(self.items)
        # Should parse without error
        root = ET.fromstring(xml_str)
        self.assertEqual(root.tag, "opml")
        self.assertEqual(root.get("version"), "2.0")

    def test_has_head_and_body(self):
        root = ET.fromstring(generate_opml(self.items))
        self.assertIsNotNone(root.find("head"))
        self.assertIsNotNone(root.find("body"))
        self.assertIsNotNone(root.find("head/title"))
        self.assertIsNotNone(root.find("head/dateCreated"))

    def test_groups_by_category(self):
        root = ET.fromstring(generate_opml(self.items))
        body = root.find("body")
        categories = [outline.get("text") for outline in body.findall("outline")]
        self.assertIn("YouTube", categories)
        self.assertIn("Reddit", categories)

    def test_feed_attributes(self):
        root = ET.fromstring(generate_opml(self.items))
        feeds = list(root.iter("outline"))
        rss_feeds = [f for f in feeds if f.get("type") == "rss"]
        self.assertEqual(len(rss_feeds), 2)

        yt_feed = next(f for f in rss_feeds if f.get("text") == "Raycevick")
        self.assertEqual(yt_feed.get("type"), "rss")
        self.assertEqual(
            yt_feed.get("xmlUrl"),
            "https://www.youtube.com/feeds/videos.xml?channel_id=UC1",
        )

    def test_xml_declaration(self):
        xml_str = generate_opml(self.items)
        self.assertTrue(xml_str.startswith('<?xml version="1.0" encoding="UTF-8"?>'))

    def test_write_and_parse_roundtrip(self):
        with tempfile.NamedTemporaryFile(suffix=".opml", delete=False) as f:
            path = Path(f.name)

        write_opml(self.items, path)
        parsed = parse_opml(path)

        self.assertEqual(len(parsed), 2)
        titles = {item.title for item in parsed}
        self.assertIn("Raycevick", titles)
        self.assertIn("r/python", titles)

    def test_empty_items(self):
        xml_str = generate_opml([])
        root = ET.fromstring(xml_str)
        body = root.find("body")
        self.assertEqual(len(list(body)), 0)


class TestOPMLMerge(unittest.TestCase):
    def test_merge_deduplicates(self):
        item_a = FeedItem(
            title="Raycevick",
            xml_url="https://www.youtube.com/feeds/videos.xml?channel_id=UC1",
            category="YouTube",
        )
        item_b = FeedItem(
            title="r/python",
            xml_url="https://www.reddit.com/r/python/.rss",
            category="Reddit",
        )

        with tempfile.NamedTemporaryFile(suffix=".opml", delete=False) as f1, \
             tempfile.NamedTemporaryFile(suffix=".opml", delete=False) as f2:
            path1 = Path(f1.name)
            path2 = Path(f2.name)

        # Both files contain Raycevick, file2 also has r/python
        write_opml([item_a], path1)
        write_opml([item_a, item_b], path2)

        result = merge_opml([path1, path2])
        root = ET.fromstring(result)
        rss_feeds = [f for f in root.iter("outline") if f.get("type") == "rss"]
        self.assertEqual(len(rss_feeds), 2)  # Raycevick + r/python, no duplicates


if __name__ == "__main__":
    unittest.main()
