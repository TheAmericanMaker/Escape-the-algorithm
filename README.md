<p align="center">
  <pre align="center">
  ___  ___  ___ __ _ _ __   ___
 / _ \/ __|/ __/ _` | '_ \ / _ \
|  __/\__ \ (_| (_| | |_) |  __/
 \___||___/\___\__,_| .__/ \___|   the algorithm
                     |_|
  </pre>
</p>

<p align="center">
  <strong>Your feed is not your friend. Take it back.</strong>
</p>

<p align="center">
  <a href="https://github.com/TheAmericanMaker/Escape-the-algorithm/actions"><img src="https://github.com/TheAmericanMaker/Escape-the-algorithm/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://pypi.org/project/escape-the-algorithm/"><img src="https://img.shields.io/pypi/v/escape-the-algorithm" alt="PyPI"></a>
  <a href="https://pypi.org/project/escape-the-algorithm/"><img src="https://img.shields.io/pypi/pyversions/escape-the-algorithm" alt="Python"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/TheAmericanMaker/Escape-the-algorithm" alt="License"></a>
  <img src="https://img.shields.io/badge/dependencies-zero-brightgreen" alt="Zero Dependencies">
</p>

---

## The Problem

Every time you open YouTube, Reddit, TikTok, or Twitter, an algorithm decides what you see. It doesn't optimize for what *you* want — it optimizes for engagement, outrage, and time-on-site. Your subscriptions exist to serve the platform's goals, not yours.

You already chose who to follow. The algorithm overrides that choice.

## The Solution

`eta` (Escape the Algorithm) converts your platform data exports into standard [OPML](https://en.wikipedia.org/wiki/OPML) files that work with any RSS reader. Export your data, run one command, and get a feed that shows you **exactly what you subscribed to** — in chronological order, with no recommendations, no autoplay, no tracking.

```
$ eta youtube subscriptions.csv

  ===================================================
  | ✓ 142 youtube subscriptions converted           |
  |   → youtube_feeds.opml                          |
  |                                                 |
  | Import into your RSS reader.                    |
  | Escape the algorithm.                           |
  ===================================================
```

No data leaves your machine. Zero dependencies. Pure Python.

## Quick Start

```bash
pip install escape-the-algorithm

# Convert any export file — eta auto-detects the format
eta convert subscriptions.csv

# Or specify the platform explicitly
eta youtube subscriptions.csv -o my_feeds.opml

# Spotify: auto-resolve RSS feeds via Podcast Index API
eta spotify Follow.json --resolve-rss -o podcasts.opml

# Preview without writing anything
eta youtube subscriptions.csv --dry-run

# Combine multiple platforms into one feed
eta merge youtube.opml reddit.opml podcasts.opml -o everything.opml
```

Import the `.opml` file into your RSS reader. Done. The algorithm no longer decides what you see.

## Supported Platforms

| Platform | Export Source | What You Get | Status |
|----------|-------------|--------------|--------|
| **YouTube** | Google Takeout CSV | RSS feed for every channel you subscribe to | Ready |
| **Reddit** | GDPR data export or text list | RSS feed for every subreddit | Ready |
| **Twitter/X** | Data archive (following.js) | RSS feeds via Nitter instances | Ready |
| **TikTok** | Data export (user_data.json) | RSS feeds via ProxiTok instances | Ready |
| **Spotify** | Privacy data export JSON | Podcast RSS feeds via Podcast Index | Ready* |

*Spotify doesn't include RSS URLs in their export. `--resolve-rss` auto-resolves them via the free [Podcast Index API](https://podcastindex.org/). See [docs/spotify.md](docs/spotify.md).

## How It Works

```
┌──────────────┐     ┌─────────┐     ┌──────────────┐     ┌────────────┐
│  YouTube CSV │────▶│         │────▶│              │────▶│ Import to  │
│  Reddit CSV  │     │         │     │              │     │ RSS Reader │
│  Twitter JS  │     │   eta   │     │  feeds.opml  │     │            │
│  TikTok JSON │     │         │     │              │     │            │
│  Spotify JSON│────▶│         │────▶│              │────▶│            │
└──────────────┘     └─────────┘     └──────────────┘     └────────────┘
     Your data         1 command       Standard format      Your choice
```

1. **Export** your data from the platform ([YouTube](docs/youtube.md) | [Reddit](docs/reddit.md) | [Twitter/X](docs/twitter.md) | [TikTok](docs/tiktok.md) | [Spotify](docs/spotify.md))
2. **Convert** with `eta` — one command, auto-detects the format
3. **Import** the OPML file into any RSS reader

That's it. No accounts, no cloud, no tracking. Your subscriptions become a file you own.

## What is RSS?

RSS is a 25-year-old open standard that lets you subscribe to websites and get updates in chronological order. No algorithm, no ads injected into your feed, no tracking. You choose a reader app, you add feeds, and you see exactly what was published — nothing more, nothing less.

It's what the internet was like before the algorithm. And it still works.

## Recommended RSS Readers

| Reader | Platform | Notes |
|--------|----------|-------|
| [**Miniflux**](https://miniflux.app/) | Web (self-hosted) | Minimalist, fast, the privacy-conscious choice |
| [**FreshRSS**](https://freshrss.org/) | Web (self-hosted) | Feature-rich, great mobile support |
| [**NetNewsWire**](https://netnewswire.com/) | macOS / iOS | Free, native, beautiful UX |
| [**Newsboat**](https://newsboat.org/) | Terminal | For the command-line faithful |
| [**Feeder**](https://github.com/spacecowboy/Feeder) | Android | Free, open source, no account needed |
| [**Thunderbird**](https://www.thunderbird.net/) | Desktop | Email client with built-in RSS |

## Installation

**Python 3.9+ required.** Zero external dependencies.

```bash
# From PyPI
pip install escape-the-algorithm

# With pipx (isolated install, recommended)
pipx install escape-the-algorithm

# From source
git clone https://github.com/TheAmericanMaker/Escape-the-algorithm.git
cd Escape-the-algorithm
pip install -e .

# Docker
docker run --rm -v $(pwd):/data ghcr.io/theamericanmaker/escape-the-algorithm youtube /data/subscriptions.csv
```

## CLI Reference

```
eta convert <file>              Auto-detect format and convert to OPML
eta youtube <file> [-o out]     Convert YouTube subscriptions CSV
eta reddit <file> [-o out]      Convert Reddit subscriptions CSV/text
eta twitter <file> [-o out]     Convert Twitter/X following list
eta tiktok <file> [-o out]      Convert TikTok following list
eta spotify <file> [-o out]     Convert Spotify podcast export
eta merge <f1> <f2> ... [-o out] Merge multiple OPML files

Flags:
  --dry-run       Preview conversion without writing files
  --verbose       Show each feed as it's found
  --resolve-rss   (spotify only) Look up RSS feeds via Podcast Index API
  --version       Show version
```

## Documentation

- [Getting Started](docs/getting-started.md) — Full walkthrough from export to RSS reader
- [YouTube Guide](docs/youtube.md) — How to export from Google Takeout
- [Reddit Guide](docs/reddit.md) — How to export your subreddit subscriptions
- [Twitter/X Guide](docs/twitter.md) — How to export your following list
- [TikTok Guide](docs/tiktok.md) — How to export your following list
- [Spotify Guide](docs/spotify.md) — How to export podcasts (and find their RSS feeds)

## Why Zero Dependencies?

This tool exists because platforms hoard your attention. It would be ironic to ask you to trust a dependency tree to escape that. Every line of `eta` uses Python's standard library — `csv`, `json`, `xml`, `argparse`. You can read the entire codebase in an afternoon. No supply chain risk. No surprises.

## Contributing

Contributions welcome. The codebase is intentionally simple.

```bash
git clone https://github.com/TheAmericanMaker/Escape-the-algorithm.git
cd Escape-the-algorithm
pip install -e .
python -m unittest discover tests/
```

Ideas for contributions:
- New platform parsers (Mastodon, Bluesky, Tumblr, Twitch)
- Translations of documentation
- Packaging for Homebrew, Nix, AUR

## Spread the Word

If `eta` helped you escape the algorithm, tell someone. Share it in your RSS reader's community, on Mastodon, on Hacker News, on the subreddits you just converted to RSS.

The algorithm thrives on silence. Break it.

## License

[MIT](LICENSE)
