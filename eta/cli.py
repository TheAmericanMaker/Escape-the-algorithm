"""Command-line interface for Escape the Algorithm."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from eta import __version__


# ANSI color codes — no dependencies needed
class _Colors:
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    RED = "\033[31m"
    RESET = "\033[0m"

    @classmethod
    def disable(cls) -> None:
        for attr in ("BOLD", "DIM", "GREEN", "YELLOW", "CYAN", "RED", "RESET"):
            setattr(cls, attr, "")


# Disable colors if not a terminal
if not sys.stderr.isatty():
    _Colors.disable()

C = _Colors

BANNER = rf"""{C.CYAN}{C.BOLD}
  ___  ___  ___ __ _ _ __   ___
 / _ \/ __|/ __/ _` | '_ \ / _ \
|  __/\__ \ (_| (_| | |_) |  __/
 \___||___/\___\__,_| .__/ \___|  {C.GREEN}the algorithm{C.RESET}
{C.DIM}v{__version__}{C.RESET}              {C.CYAN}|_|{C.RESET}
"""


def _box(lines: list[str], color: str = C.GREEN) -> str:
    """Draw a box around lines of text."""
    width = max(len(line) for line in lines) + 2
    top = f"{color}{'=' * (width + 2)}{C.RESET}"
    bottom = top
    boxed = [top]
    for line in lines:
        padded = line.ljust(width)
        boxed.append(f"{color}|{C.RESET} {padded}{color}|{C.RESET}")
    boxed.append(bottom)
    return "\n".join(boxed)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="eta",
        description="Escape the Algorithm — Convert platform exports to RSS/OPML.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"{C.DIM}Docs: https://github.com/TheAmericanMaker/Escape-the-algorithm{C.RESET}",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command")

    # Convert (auto-detect)
    cv = subparsers.add_parser(
        "convert", help="Auto-detect format and convert to OPML"
    )
    cv.add_argument("input", type=Path, help="Export file from any supported platform")
    cv.add_argument("-o", "--output", type=Path, help="Output OPML file")
    cv.add_argument("--dry-run", action="store_true", help="Preview without writing")
    cv.add_argument("--verbose", action="store_true", help="Show each feed as it's found")

    # YouTube
    yt = subparsers.add_parser(
        "youtube", help="Convert YouTube subscriptions CSV to OPML"
    )
    yt.add_argument("input", type=Path, help="Path to subscriptions.csv from Google Takeout")
    yt.add_argument("-o", "--output", type=Path, help="Output OPML file (default: youtube_feeds.opml)")
    yt.add_argument("--dry-run", action="store_true", help="Preview without writing")
    yt.add_argument("--verbose", action="store_true", help="Show each feed as it's found")

    # Reddit
    rd = subparsers.add_parser(
        "reddit", help="Convert Reddit subscriptions to OPML"
    )
    rd.add_argument("input", type=Path, help="Path to subscribed_subreddits.csv or text file")
    rd.add_argument("-o", "--output", type=Path, help="Output OPML file (default: reddit_feeds.opml)")
    rd.add_argument("--dry-run", action="store_true", help="Preview without writing")
    rd.add_argument("--verbose", action="store_true", help="Show each feed as it's found")

    # Spotify
    sp = subparsers.add_parser(
        "spotify", help="Convert Spotify podcast data to OPML"
    )
    sp.add_argument("input", type=Path, help="Path to Spotify export JSON file")
    sp.add_argument("-o", "--output", type=Path, help="Output OPML file (default: spotify_feeds.opml)")
    sp.add_argument("--dry-run", action="store_true", help="Preview without writing")
    sp.add_argument("--verbose", action="store_true", help="Show each feed as it's found")

    # Merge
    mg = subparsers.add_parser(
        "merge", help="Merge multiple OPML files into one"
    )
    mg.add_argument("inputs", nargs="+", type=Path, help="OPML files to merge")
    mg.add_argument("-o", "--output", type=Path, help="Output OPML file (default: merged.opml)")

    args = parser.parse_args(argv)

    if not args.command:
        print(BANNER, file=sys.stderr)
        parser.print_help()
        return 1

    try:
        if args.command == "merge":
            return _cmd_merge(args)
        if args.command == "convert":
            return _cmd_auto_convert(args)
        return _cmd_convert(args)
    except FileNotFoundError as e:
        _error(str(e))
        return 1
    except Exception as e:
        _error(str(e))
        return 1


def _cmd_auto_convert(args: argparse.Namespace) -> int:
    """Handle the auto-detect 'convert' subcommand."""
    input_path: Path = args.input
    if not input_path.exists():
        _error(f"File not found: {input_path}")
        return 1

    from eta.parsers.detect import detect_platform
    platform = detect_platform(input_path)
    if not platform:
        _error(
            f"Could not detect platform format for: {input_path}\n"
            f"  Try specifying the platform directly: eta youtube|reddit|spotify {input_path}"
        )
        return 1

    _info(f"Detected format: {C.BOLD}{platform}{C.RESET}")

    # Reuse the convert logic with the detected platform
    args.command = platform
    if not args.output:
        args.output = Path(f"{platform}_feeds.opml")
    return _cmd_convert(args)


def _cmd_convert(args: argparse.Namespace) -> int:
    """Handle youtube/reddit/spotify subcommands."""
    input_path: Path = args.input
    if not input_path.exists():
        _error(f"File not found: {input_path}")
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

    if getattr(args, "verbose", False):
        for item in items:
            rss_indicator = f"{C.GREEN}rss{C.RESET}" if item.xml_url else f"{C.YELLOW}no rss{C.RESET}"
            print(f"  [{rss_indicator}] {item.title}", file=sys.stderr)

    if not items:
        _warn(f"No subscriptions found in {input_path}")
        return 0

    output_path = args.output or Path(f"{args.command}_feeds.opml")

    feeds_with_rss = sum(1 for item in items if item.xml_url)
    feeds_without_rss = len(items) - feeds_with_rss

    if getattr(args, "dry_run", False):
        _print_dry_run(args.command, items, output_path, feeds_with_rss, feeds_without_rss)
        return 0

    from eta.exporters.opml import write_opml
    write_opml(items, output_path, title=f"Escape the Algorithm - {args.command.title()}")

    _print_success(args.command, items, output_path, feeds_with_rss, feeds_without_rss)
    return 0


def _cmd_merge(args: argparse.Namespace) -> int:
    """Handle the merge subcommand."""
    for path in args.inputs:
        if not path.exists():
            _error(f"File not found: {path}")
            return 1

    from eta.exporters.opml import merge_opml
    output_path = args.output or Path("merged.opml")
    result = merge_opml(args.inputs)
    output_path.write_text(result, encoding="utf-8")

    summary = _box([
        f"{C.GREEN}\u2713{C.RESET} Merged {C.BOLD}{len(args.inputs)}{C.RESET} OPML files",
        f"  \u2192 {C.CYAN}{output_path}{C.RESET}",
    ])
    print(summary, file=sys.stderr)
    return 0


def _print_success(
    platform: str,
    items: list,
    output_path: Path,
    feeds_with_rss: int,
    feeds_without_rss: int,
) -> None:
    """Print a nice summary box after successful conversion."""
    lines = [
        f"{C.GREEN}\u2713{C.RESET} {C.BOLD}{len(items)}{C.RESET} {platform} subscriptions converted",
        f"  \u2192 {C.CYAN}{output_path}{C.RESET}",
    ]
    if feeds_without_rss:
        lines.append("")
        lines.append(
            f"  {C.YELLOW}\u26a0{C.RESET} {feeds_without_rss} items without RSS URLs"
        )
        lines.append(f"  {C.DIM}See docs/spotify.md to find podcast RSS feeds{C.RESET}")
    lines.append("")
    lines.append(f"{C.DIM}Import into your RSS reader. Escape the algorithm.{C.RESET}")

    print(_box(lines), file=sys.stderr)


def _print_dry_run(
    platform: str,
    items: list,
    output_path: Path,
    feeds_with_rss: int,
    feeds_without_rss: int,
) -> None:
    """Print a preview of what would be converted."""
    _info(f"{C.BOLD}DRY RUN{C.RESET} — no files will be written\n")

    print(f"  Platform:  {C.BOLD}{platform}{C.RESET}", file=sys.stderr)
    print(f"  Output:    {C.CYAN}{output_path}{C.RESET}", file=sys.stderr)
    print(f"  Feeds:     {C.GREEN}{feeds_with_rss}{C.RESET} with RSS", file=sys.stderr)
    if feeds_without_rss:
        print(f"             {C.YELLOW}{feeds_without_rss}{C.RESET} without RSS", file=sys.stderr)
    print(file=sys.stderr)

    for item in items[:20]:
        rss = f"{C.GREEN}\u2713{C.RESET}" if item.xml_url else f"{C.YELLOW}\u2717{C.RESET}"
        print(f"  {rss} {item.title}", file=sys.stderr)

    if len(items) > 20:
        print(f"  {C.DIM}... and {len(items) - 20} more{C.RESET}", file=sys.stderr)


def _error(msg: str) -> None:
    print(f"{C.RED}error:{C.RESET} {msg}", file=sys.stderr)


def _warn(msg: str) -> None:
    print(f"{C.YELLOW}warning:{C.RESET} {msg}", file=sys.stderr)


def _info(msg: str) -> None:
    print(f"{C.CYAN}>{C.RESET} {msg}", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
