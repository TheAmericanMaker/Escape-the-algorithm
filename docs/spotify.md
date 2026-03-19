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

## Important: Finding RSS Feeds

Spotify deliberately does not include podcast RSS feed URLs in their data export. The `eta spotify` command extracts your podcast names and Spotify URLs, but the OPML file won't have direct RSS feed links.

To find the actual RSS feeds for your podcasts:

### Using Podcast Index

1. Go to [podcastindex.org](https://podcastindex.org/)
2. Search for the podcast name
3. The RSS feed URL is listed on the podcast's page

### Using Apple Podcasts

1. Search for the podcast on [Apple Podcasts](https://podcasts.apple.com/)
2. The RSS feed can be extracted from the Apple Podcasts listing

### Using Listen Notes

1. Go to [listennotes.com](https://www.listennotes.com/)
2. Search for the podcast
3. Click on the podcast and look for the RSS feed link

### Why This Limitation Exists

Spotify hosts many podcasts exclusively and doesn't expose RSS feed URLs for them. For Spotify-exclusive podcasts, there may not be an RSS feed available. For podcasts that exist outside Spotify, the RSS feed is how they were distributed before Spotify — it still works.

This is a known limitation. A future version may add automatic RSS feed lookup.
