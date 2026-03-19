"""OPML 2.0 exporter and merger."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from eta.parsers import FeedItem

YOUTUBE_RSS_PREFIX = "https://www.youtube.com/feeds/videos.xml"


def generate_opml(
    items: List[FeedItem],
    title: str = "Escape the Algorithm - Subscriptions",
) -> str:
    """Generate an OPML 2.0 XML string from a list of FeedItems."""
    opml = ET.Element("opml", version="2.0")

    head = ET.SubElement(opml, "head")
    ET.SubElement(head, "title").text = title
    ET.SubElement(head, "dateCreated").text = (
        datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S %z")
    )

    body = ET.SubElement(opml, "body")

    # Group by category
    groups: dict[str, list[FeedItem]] = defaultdict(list)
    for item in items:
        groups[item.category or "Uncategorized"].append(item)

    for category in sorted(groups):
        group_outline = ET.SubElement(
            body, "outline", text=category, title=category
        )
        for item in sorted(groups[category], key=lambda x: x.title.lower()):
            attrs = {
                "type": "rss",
                "text": item.title,
                "title": item.title,
                "xmlUrl": item.xml_url,
            }
            if item.html_url:
                attrs["htmlUrl"] = item.html_url
            ET.SubElement(group_outline, "outline", **attrs)

    ET.indent(opml)
    xml_str = ET.tostring(opml, encoding="unicode", xml_declaration=False)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str + "\n"


def write_opml(
    items: List[FeedItem],
    output_path: Path,
    title: str = "Escape the Algorithm - Subscriptions",
) -> None:
    """Write FeedItems to an OPML file."""
    output_path.write_text(generate_opml(items, title), encoding="utf-8")


def parse_opml(path: Path) -> List[FeedItem]:
    """Parse an OPML file and return a list of FeedItems."""
    tree = ET.parse(path)
    root = tree.getroot()
    items: list[FeedItem] = []

    for outline in root.iter("outline"):
        xml_url = outline.get("xmlUrl")
        if not xml_url:
            continue
        items.append(
            FeedItem(
                title=outline.get("text", outline.get("title", "")),
                xml_url=xml_url,
                html_url=outline.get("htmlUrl", ""),
                category=_get_parent_category(root, outline),
            )
        )

    return items


def _get_parent_category(root: ET.Element, outline: ET.Element) -> str:
    """Find the parent category of an outline element."""
    # Build parent map
    parent_map = {child: parent for parent in root.iter() for child in parent}
    parent = parent_map.get(outline)
    if parent is not None and parent.tag == "outline":
        return parent.get("text", parent.get("title", ""))
    return ""


def merge_opml(paths: List[Path], title: str = "Escape the Algorithm - Merged") -> str:
    """Merge multiple OPML files, deduplicating by xmlUrl."""
    seen_urls: set[str] = set()
    all_items: list[FeedItem] = []

    for path in paths:
        for item in parse_opml(path):
            if item.xml_url not in seen_urls:
                seen_urls.add(item.xml_url)
                all_items.append(item)

    return generate_opml(all_items, title)
