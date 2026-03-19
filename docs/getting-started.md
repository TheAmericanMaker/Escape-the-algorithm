# Getting Started

This guide walks you through escaping algorithmic feeds in three steps: export, convert, import.

## Step 1: Install

```bash
pip install escape-the-algorithm
```

Or install from source:

```bash
git clone https://github.com/TheAmericanMaker/Escape-the-algorithm.git
cd Escape-the-algorithm
pip install -e .
```

## Step 2: Export Your Data

Pick the platforms you want to escape from:

- **YouTube** — [YouTube export guide](youtube.md)
- **Reddit** — [Reddit export guide](reddit.md)
- **Twitter/X** — [Twitter export guide](twitter.md)
- **Spotify** — [Spotify export guide](spotify.md)

## Step 3: Convert to OPML

Run the converter for each platform:

```bash
# Specify the platform
eta youtube subscriptions.csv
eta reddit subreddits.txt
eta twitter following.js
eta spotify Follow.json

# Or let eta auto-detect the format
eta convert subscriptions.csv
```

Each command creates an `.opml` file in the current directory.

To combine everything into a single file:

```bash
eta merge youtube_feeds.opml reddit_feeds.opml spotify_feeds.opml -o my_feeds.opml
```

## Step 4: Import Into an RSS Reader

Open your RSS reader and look for "Import OPML" or "Import subscriptions". Select the `.opml` file you generated. All your feeds will appear.

### Recommended Readers

- **Miniflux** (self-hosted, web) — Settings > Import OPML
- **FreshRSS** (self-hosted, web) — Subscription Management > Import/Export > Import OPML
- **NetNewsWire** (macOS/iOS) — File > Import Subscriptions
- **Thunderbird** (desktop) — Account Settings > Manage Feeds > Import
- **Feeder** (Android) — Settings > Import/Export > Import OPML

## What Is RSS?

RSS (Really Simple Syndication) is a way to subscribe to websites and get new content delivered to you — without an algorithm deciding what you see. It's been around since the early 2000s and still works with most websites, YouTube channels, Reddit subreddits, podcasts, and blogs.

When you subscribe to an RSS feed, you see every new post in chronological order. No recommendations, no ads, no tracking.

## What Is OPML?

OPML is a standard file format for lists of RSS subscriptions. Every RSS reader supports importing OPML files. It's the universal way to move your subscriptions between readers.
