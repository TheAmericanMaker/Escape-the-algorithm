"""Tests for the Podcast Index RSS resolver."""

import json
import unittest
from unittest.mock import patch, MagicMock
from io import BytesIO

from eta.parsers import FeedItem
from eta.resolvers.podcastindex import (
    _auth_headers,
    search_by_title,
    resolve_feeds,
)


class TestAuthHeaders(unittest.TestCase):
    @patch("eta.resolvers.podcastindex.time")
    def test_headers_include_required_fields(self, mock_time):
        mock_time.time.return_value = 1700000000
        headers = _auth_headers("mykey", "mysecret")
        self.assertEqual(headers["X-Auth-Key"], "mykey")
        self.assertEqual(headers["X-Auth-Date"], "1700000000")
        self.assertIn("Authorization", headers)
        self.assertIn("User-Agent", headers)

    @patch("eta.resolvers.podcastindex.time")
    def test_auth_hash_is_sha1(self, mock_time):
        mock_time.time.return_value = 1700000000
        import hashlib
        expected = hashlib.sha1(b"mykeymysecret1700000000").hexdigest()
        headers = _auth_headers("mykey", "mysecret")
        self.assertEqual(headers["Authorization"], expected)


class TestSearchByTitle(unittest.TestCase):
    def _mock_response(self, data: dict):
        resp = MagicMock()
        resp.read.return_value = json.dumps(data).encode()
        resp.__enter__ = lambda s: s
        resp.__exit__ = MagicMock(return_value=False)
        return resp

    @patch("eta.resolvers.podcastindex.urlopen")
    def test_returns_exact_match_feed_url(self, mock_urlopen):
        mock_urlopen.return_value = self._mock_response({
            "feeds": [
                {"title": "Other Podcast", "feedUrl": "https://example.com/other.xml"},
                {"title": "Darknet Diaries", "feedUrl": "https://feeds.megaphone.fm/darknetdiaries"},
            ]
        })
        result = search_by_title("Darknet Diaries", "key", "secret")
        self.assertEqual(result, "https://feeds.megaphone.fm/darknetdiaries")

    @patch("eta.resolvers.podcastindex.urlopen")
    def test_falls_back_to_first_result(self, mock_urlopen):
        mock_urlopen.return_value = self._mock_response({
            "feeds": [
                {"title": "Almost Match", "feedUrl": "https://example.com/almost.xml"},
            ]
        })
        result = search_by_title("Something Else", "key", "secret")
        self.assertEqual(result, "https://example.com/almost.xml")

    @patch("eta.resolvers.podcastindex.urlopen")
    def test_returns_empty_on_no_results(self, mock_urlopen):
        mock_urlopen.return_value = self._mock_response({"feeds": []})
        result = search_by_title("Nonexistent Podcast", "key", "secret")
        self.assertEqual(result, "")

    @patch("eta.resolvers.podcastindex.urlopen")
    def test_handles_network_error(self, mock_urlopen):
        from urllib.error import URLError
        mock_urlopen.side_effect = URLError("Connection refused")
        result = search_by_title("Test", "key", "secret")
        self.assertEqual(result, "")


class TestResolveFeeds(unittest.TestCase):
    @patch("eta.resolvers.podcastindex.search_by_title")
    def test_resolves_missing_rss_urls(self, mock_search):
        mock_search.return_value = "https://feeds.example.com/podcast.xml"

        items = [
            FeedItem(title="My Podcast", xml_url="", html_url="https://spotify.com/show/123", category="Podcasts"),
            FeedItem(title="Has RSS", xml_url="https://existing.com/rss", html_url="", category="Podcasts"),
        ]

        result = resolve_feeds(items, key="k", secret="s")

        # First item should be resolved
        self.assertEqual(result[0].xml_url, "https://feeds.example.com/podcast.xml")
        self.assertEqual(result[0].title, "My Podcast")
        self.assertEqual(result[0].html_url, "https://spotify.com/show/123")

        # Second item should be unchanged (already had RSS)
        self.assertEqual(result[1].xml_url, "https://existing.com/rss")

        # Only searched for the one missing RSS
        mock_search.assert_called_once_with("My Podcast", "k", "s")

    @patch("eta.resolvers.podcastindex.search_by_title")
    def test_calls_progress_callback(self, mock_search):
        mock_search.return_value = "https://feed.xml"
        items = [FeedItem(title="Pod", xml_url="", html_url="", category="Podcasts")]

        progress_calls = []
        def on_progress(current, total, title, feed_url):
            progress_calls.append((current, total, title, feed_url))

        resolve_feeds(items, key="k", secret="s", on_progress=on_progress)
        self.assertEqual(len(progress_calls), 1)
        self.assertEqual(progress_calls[0], (1, 1, "Pod", "https://feed.xml"))

    @patch("eta.resolvers.podcastindex.search_by_title")
    def test_preserves_items_when_not_found(self, mock_search):
        mock_search.return_value = ""
        items = [FeedItem(title="Exclusive Pod", xml_url="", html_url="https://spotify.com/x", category="Podcasts")]

        result = resolve_feeds(items, key="k", secret="s")
        self.assertEqual(result[0].xml_url, "")
        self.assertEqual(result[0].title, "Exclusive Pod")

    def test_raises_without_credentials(self):
        items = [FeedItem(title="Pod", xml_url="", html_url="", category="Podcasts")]
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(ValueError) as ctx:
                resolve_feeds(items)
            self.assertIn("PODCAST_INDEX_KEY", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
