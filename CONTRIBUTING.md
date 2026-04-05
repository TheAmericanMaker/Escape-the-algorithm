# Contributing to Escape the Algorithm

Thanks for wanting to help. This project exists to give people back control over their feeds, and every contribution — bug reports, docs, new platform parsers, translations — moves that goal forward.

## Table of contents

- [Before you start](#before-you-start)
- [Development setup](#development-setup)
- [How the code is structured](#how-the-code-is-structured)
- [Adding a new platform parser](#adding-a-new-platform-parser)
- [Running the tests](#running-the-tests)
- [Submitting a pull request](#submitting-a-pull-request)
- [Reporting a bug](#reporting-a-bug)
- [Other ways to contribute](#other-ways-to-contribute)

---

## Before you start

- Check [open issues](https://github.com/TheAmericanMaker/Escape-the-algorithm/issues) to see if someone is already working on what you have in mind.
- For large changes, open an issue first to discuss the approach before writing code.
- All contributions are subject to the [MIT License](LICENSE).

---

## Development setup

You need Python 3.9 or newer. No other tools are required — the project has zero runtime dependencies.

```bash
# 1. Fork and clone the repo
git clone https://github.com/YOUR-USERNAME/Escape-the-algorithm.git
cd Escape-the-algorithm

# 2. Install in editable mode (changes to source take effect immediately)
pip install -e .

# 3. Install the linter (optional but useful)
pip install ruff

# 4. Verify everything works
python -m unittest discover tests/ -v
```

That's it. Run `eta --version` to confirm the install worked.

---

## How the code is structured

```
eta/
├── cli.py              # Entry point — argument parsing and output formatting
├── parsers/
│   ├── detect.py       # Auto-detects which platform a file came from
│   ├── youtube.py      # Parses Google Takeout CSV → list of FeedItems
│   ├── reddit.py       # Parses Reddit GDPR CSV or subreddit text list
│   ├── twitter.py      # Parses Twitter archive JS/JSON
│   ├── tiktok.py       # Parses TikTok JSON export
│   └── spotify.py      # Parses Spotify JSON export
├── exporters/
│   ├── opml.py         # Writes and merges OPML 2.0 files
│   └── txt.py          # Writes a plain-text feed list
└── resolvers/
    └── podcastindex.py # Resolves Spotify podcast names → RSS URLs via Podcast Index
```

The data flow is simple:

```
export file  →  parser (platform-specific)  →  list[FeedItem]  →  exporter (OPML/txt)
```

`FeedItem` is a small dataclass defined in `eta/parsers/__init__.py`:

```python
@dataclass
class FeedItem:
    title: str
    xml_url: str | None   # RSS feed URL (None if not known)
    html_url: str | None  # Link to the channel/profile page
```

Every parser takes a `Path` and returns a `list[FeedItem]`. That's the whole interface. If you can write a function with that signature, you can add a new platform.

---

## Adding a new platform parser

This is the most valuable contribution you can make. Here's exactly how to do it.

### 1. Create the parser file

Add `eta/parsers/yourplatform.py`:

```python
"""Parser for YourPlatform export files."""

from __future__ import annotations

from pathlib import Path

from eta.parsers import FeedItem


def parse(path: Path) -> list[FeedItem]:
    """Parse a YourPlatform export file and return a list of FeedItems.

    Args:
        path: Path to the export file.

    Returns:
        List of FeedItem objects, one per subscription.

    Raises:
        ValueError: If the file cannot be parsed.
    """
    items: list[FeedItem] = []

    # ... your parsing logic here ...

    return items
```

**RSS URL construction:** If the platform has predictable RSS URLs (like YouTube's `https://www.youtube.com/feeds/videos.xml?channel_id=XXX`), construct them directly. If not, leave `xml_url=None` and the user can resolve them later.

### 2. Register the parser in cli.py

In `eta/cli.py`, add a subparser alongside the existing ones:

```python
# YourPlatform
yp = subparsers.add_parser("yourplatform", help="Convert YourPlatform following list to OPML")
yp.add_argument("input", type=Path, help="Path to export file from YourPlatform")
yp.add_argument("-o", "--output", type=Path, help="Output OPML file (default: yourplatform_feeds.opml)")
yp.add_argument("--dry-run", action="store_true", help="Preview without writing")
yp.add_argument("--verbose", action="store_true", help="Show each feed as it's found")
```

Then add the import inside `_cmd_convert`:

```python
elif args.command == "yourplatform":
    from eta.parsers.yourplatform import parse
```

### 3. Add auto-detection (optional but nice)

In `eta/parsers/detect.py`, add logic to `detect_platform()` so `eta convert` can identify your file format automatically.

### 4. Write tests

Add `tests/test_yourplatform.py` with at least:

- A test with a valid export file
- A test that verifies the RSS URL format is correct
- A test with an empty or malformed file

Add a sample fixture file to `tests/fixtures/` (with any personal data removed or replaced with fake data).

### 5. Write a guide

Add `docs/yourplatform.md` explaining:

1. How to request/download the data export from the platform
2. Which file to use (name, format)
3. The `eta` command to run
4. Any known limitations

Look at `docs/youtube.md` or `docs/reddit.md` for the expected format.

---

## Running the tests

```bash
# Run all tests
python -m unittest discover tests/ -v

# Run tests for a single platform
python -m unittest tests.test_youtube -v

# Check formatting and lint
ruff format --check eta/ tests/
ruff check eta/ tests/

# Auto-fix formatting
ruff format eta/ tests/
```

CI runs the full test matrix (Python 3.9–3.13) on every pull request. Your PR must pass all checks before it can be merged.

---

## Submitting a pull request

1. Fork the repo and create a branch: `git checkout -b add-mastodon-parser`
2. Make your changes. Keep commits focused — one logical change per commit.
3. Run the tests and linter locally before pushing.
4. Open a pull request against `main`. Fill in the PR description — what does this change, and why?
5. A maintainer will review it. We may suggest changes; that's normal.

**Keep diffs small.** A PR that adds one platform parser is much easier to review than one that adds a parser, refactors the CLI, and updates the README all at once.

---

## Reporting a bug

Use the [bug report template](https://github.com/TheAmericanMaker/Escape-the-algorithm/issues/new?template=bug_report.md). Please include:

- The `eta` command you ran (with the filename, but you can anonymize it)
- What you expected to happen
- What actually happened (paste any error output)
- Your OS and Python version (`python --version`)

---

## Other ways to contribute

You don't have to write code to contribute meaningfully:

- **Translations** — translate the docs or CLI output strings into another language
- **Platform guides** — improve or expand the step-by-step export instructions in `docs/`
- **Screenshots** — add the annotated screenshots referenced in the README (see `docs/screenshots/README.md`)
- **Bug reports** — a clear, reproducible bug report is genuinely helpful
- **Packaging** — help publish to Homebrew, AUR, Nix, or Chocolatey
- **Spread the word** — share the project with people who would benefit from it
