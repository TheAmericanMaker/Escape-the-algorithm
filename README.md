# Escape the Algorithm

**Your feed is not your friend. Take it back.**

Escape the Algorithm converts your platform data exports into [OPML](https://en.wikipedia.org/wiki/OPML) files you can import into any RSS reader. No cloud, no account, no tracking — runs on your machine with your data.

Stop letting YouTube, Reddit, and Spotify decide what you see. Export your subscriptions, convert them to RSS, and own your feed.

## Quick Start

```bash
pip install escape-the-algorithm

# YouTube: Export from Google Takeout, then:
eta youtube subscriptions.csv -o my_youtube.opml

# Reddit: Export your data or paste subreddits into a text file:
eta reddit subreddits.txt -o my_reddit.opml

# Spotify: Export your data, then:
eta spotify Follow.json -o my_podcasts.opml

# Combine everything into one feed file:
eta merge my_youtube.opml my_reddit.opml my_podcasts.opml -o everything.opml
```

Import the `.opml` file into your RSS reader of choice. Done.

## Supported Platforms

| Platform | Export Source | What You Get |
|----------|-------------|--------------|
| YouTube | Google Takeout `subscriptions.csv` | RSS feed for every channel |
| Reddit | Data export or text list | RSS feed for every subreddit |
| Spotify | Privacy data export JSON | Podcast names + Spotify URLs* |

*Spotify doesn't include RSS URLs in their export. See [docs/spotify.md](docs/spotify.md) for how to find podcast RSS feeds.

## How It Works

1. **Export** your data from the platform (Google Takeout, Reddit data request, Spotify privacy export)
2. **Convert** with `eta` — it reads the export file and generates an OPML file with RSS feed URLs
3. **Import** the OPML into any RSS reader

No data leaves your machine. The entire tool is pure Python with zero dependencies.

## Recommended RSS Readers

| Reader | Platform | Self-hosted? | Notes |
|--------|----------|-------------|-------|
| [Miniflux](https://miniflux.app/) | Web | Yes | Minimalist, fast, supports OPML import |
| [FreshRSS](https://freshrss.org/) | Web | Yes | Feature-rich, good mobile support |
| [NetNewsWire](https://netnewswire.com/) | macOS/iOS | No | Free, native, excellent UX |
| [Thunderbird](https://www.thunderbird.net/) | Desktop | No | Email client with built-in RSS |
| [Feeder](https://github.com/spacecowboy/Feeder) | Android | No | Free, open source, no account needed |

## Installation

Requires Python 3.9+.

```bash
# From PyPI
pip install escape-the-algorithm

# From source
git clone https://github.com/TheAmericanMaker/Escape-the-algorithm.git
cd Escape-the-algorithm
pip install -e .
```

## Documentation

- [Getting Started](docs/getting-started.md) — Full walkthrough from export to RSS reader
- [YouTube Guide](docs/youtube.md) — How to export from Google Takeout
- [Reddit Guide](docs/reddit.md) — How to export your subreddit subscriptions
- [Spotify Guide](docs/spotify.md) — How to export podcasts (and find their RSS feeds)

## Contributing

Contributions welcome. The codebase is intentionally simple — pure Python, stdlib only, easy to audit.

```bash
git clone https://github.com/TheAmericanMaker/Escape-the-algorithm.git
cd Escape-the-algorithm
pip install -e .
python -m unittest discover tests/
```

## License

[MIT](LICENSE)
