# Spotify Export Guide

## How to Export Your Spotify Podcasts

### Step 1: Request Your Data

1. Go to [Spotify Privacy Settings](https://www.spotify.com/account/privacy/)
2. Scroll down to **Download your data**
3. Request your data (select at least "Account data")
4. Wait for the email (can take up to 30 days, but usually a few days)
5. Download and extract the ZIP file

### Step 2: Find the Podcast Data

Look for a JSON file containing your followed podcasts or shows. The filename varies by export version — common names include:
- `Follow.json`
- `YourLibrary.json`
- Files in a `Podcast` or `Shows` directory

### Step 3: Convert

```bash
eta spotify Follow.json -o spotify_feeds.opml
```

## Automatic RSS Feed Resolution

Spotify does not include RSS feed URLs in their data export. But `eta` can automatically look them up using the free [Podcast Index](https://podcastindex.org/) API.

### Setup (one time)

1. Get a free API key pair at [api.podcastindex.org](https://api.podcastindex.org/)
2. Set environment variables:

```bash
export PODCAST_INDEX_KEY="your-api-key"
export PODCAST_INDEX_SECRET="your-api-secret"
```

### Usage

```bash
# Auto-resolve RSS feeds for all podcasts
eta spotify Follow.json --resolve-rss -o spotify_feeds.opml

# Preview what would be resolved
eta spotify Follow.json --resolve-rss --verbose --dry-run
```

The `--resolve-rss` flag searches Podcast Index for each podcast by title and fills in the RSS feed URL. Podcasts that are Spotify-exclusive (no RSS feed exists) will be included without an RSS URL.

### Without the API

If you don't want to set up API keys, `eta spotify` still works — it exports podcast names and Spotify URLs. You can manually find RSS feeds at:

- [podcastindex.org](https://podcastindex.org/) — search by name
- [listennotes.com](https://www.listennotes.com/) — search and view RSS feeds
- [Apple Podcasts](https://podcasts.apple.com/) — RSS feeds can be extracted from listings

## Why This Limitation Exists

Spotify hosts many podcasts exclusively and doesn't expose RSS feed URLs in their data export. For Spotify-exclusive podcasts, there is no RSS feed. For podcasts that exist outside Spotify, the RSS feed is how they were distributed before Spotify — it still works.
