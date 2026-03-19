"""Shared data model for all parsers."""

from dataclasses import dataclass


@dataclass
class FeedItem:
    """A single feed subscription."""

    title: str
    xml_url: str
    html_url: str = ""
    category: str = ""
