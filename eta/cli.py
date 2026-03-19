"""Command-line interface for Escape the Algorithm."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from eta import __version__
from eta.exporters.opml import generate_opml, merge_opml, write_opml
from eta.parsers import FeedItem


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="eta",
        description="Escape the Algorithm — Convert platform exports to RSS/OPML.",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command")

    # YouTube
    yt = subparsers.add_parser(
        "youtube", help="Convert YouTube subscriptions CSV to OPML"
    )
    yt.add_argument("input", type=Path, help="Path to subscriptions.csv from Google Takeout")
    yt.add_argument("-o", "--output", type=Path, help="Output OPML file (default: youtube_feeds.opml)")

    # Reddit
    rd = subparsers.add_parser(
        "reddit", help="Convert Reddit subscriptions to OPML"
    )
    rd.add_argument("input", type=Path, help="Path to subscribed_subreddits.csv or text file")
    rd.add_argument("-o", "--output", type=Path, help="Output OPML file (default: reddit_feeds.opml)")

    # Spotify
    sp = subparsers.add_parser(
        "spotify", help="Convert Spotify podcast data to OPML"
    )
    sp.add_argument("input", type=Path, help="Path to Spotify export JSON file")
    sp.add_argument("-o", "--output", type=Path, help="Output OPML file (default: spotify_feeds.opml)")

    # Merge
    mg = subparsers.add_parser(
        "merge", help="Merge multiple OPML files into one"
    )
    mg.add_argument("inputs", nargs="+", type=Path, help="OPML files to merge")
    mg.add_argument("-o", "--output", type=Path, help="Output OPML file (default: merged.opml)")

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == "merge":
            return _cmd_merge(args)
        return _cmd_convert(args)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _cmd_convert(args: argparse.Namespace) -> int:
    """Handle youtube/reddit/spotify subcommands."""
    input_path: Path = args.input
    if not input_path.exists():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        return 1

    # Import the right parser
    if args.command == "youtube":
        from eta.parsers.youtube import parse
    elif args.command == "reddit":
        from eta.parsers.reddit import parse
    elif args.command == "spotify":
        from eta.parsers.spotify import parse
    else:
        return 1

    items = parse(input_path)
    if not items:
        print(f"Warning: No subscriptions found in {input_path}", file=sys.stderr)
        return 0

    output_path = args.output or Path(f"{args.command}_feeds.opml")
    write_opml(items, output_path, title=f"Escape the Algorithm - {args.command.title()}")

    # Report to user
    feeds_with_rss = sum(1 for item in items if item.xml_url)
    feeds_without_rss = len(items) - feeds_with_rss

    print(
        f"Converted {len(items)} {args.command} subscriptions -> {output_path}",
        file=sys.stderr,
    )
    if feeds_without_rss:
        print(
            f"  ({feeds_without_rss} items without RSS URLs — see docs for how to find them)",
            file=sys.stderr,
        )

    return 0


def _cmd_merge(args: argparse.Namespace) -> int:
    """Handle the merge subcommand."""
    for path in args.inputs:
        if not path.exists():
            print(f"Error: File not found: {path}", file=sys.stderr)
            return 1

    output_path = args.output or Path("merged.opml")
    result = merge_opml(args.inputs)
    output_path.write_text(result, encoding="utf-8")

    print(f"Merged {len(args.inputs)} files -> {output_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
