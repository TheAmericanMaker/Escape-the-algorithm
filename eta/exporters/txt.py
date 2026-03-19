"""Plain text feed list exporter."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import List

from eta.parsers import FeedItem


def generate_txt(
    items: List[FeedItem],
    title: str = "Escape the Algorithm - Subscriptions",
) -> str:
    """Generate a plain text feed list from FeedItems."""
    lines = [
        f"# {title}",
        "# Exported by Escape the Algorithm (eta)",
        "",
    ]

    groups: dict[str, list[FeedItem]] = defaultdict(list)
    for item in items:
        groups[item.category or "Uncategorized"].append(item)

    for category in sorted(groups):
        lines.append(f"## {category}")
        lines.append("")
        for item in sorted(groups[category], key=lambda x: x.title.lower()):
            lines.append(item.title)
            if item.xml_url:
                lines.append(f"  RSS: {item.xml_url}")
            if item.html_url:
                lines.append(f"  Web: {item.html_url}")
            lines.append("")

    return "\n".join(lines)


def write_txt(
    items: List[FeedItem],
    output_path: Path,
    title: str = "Escape the Algorithm - Subscriptions",
) -> None:
    """Write FeedItems to a plain text file."""
    output_path.write_text(generate_txt(items, title), encoding="utf-8")
