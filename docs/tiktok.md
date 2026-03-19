# TikTok Export Guide

## How to Export Your Following List

### Option A: Official TikTok Data Export

1. Open TikTok and go to **Settings and Privacy**
2. Tap **Account** > **Download Your Data**
3. Select **JSON** format (not TXT)
4. Select **Request Data**
5. Wait for TikTok to prepare your export (can take a few days)
6. Download and extract the ZIP file
7. Find the file `user_data.json`

### Option B: Manual Text List

Create a text file with one username per line:

```
@charlidamelio
@khaby.lame
@bellapoarch
```

## Converting to OPML

```bash
# From TikTok data export
eta tiktok user_data.json -o tiktok_feeds.opml

# From a text list
eta tiktok my_creators.txt -o tiktok_feeds.opml

# Preview first
eta tiktok user_data.json --dry-run
```

## How TikTok RSS Works

TikTok does not offer native RSS feeds. `eta` generates feed URLs using [ProxiTok](https://github.com/pablouser1/ProxiTok), an open-source alternative TikTok frontend that provides RSS feeds.

The default RSS URL pattern is:
```
https://proxitok.pabloferreiro.es/@{username}/rss
```

### Finding a Working ProxiTok Instance

ProxiTok instances are community-maintained. If the default instance isn't working, check:

- [ProxiTok GitHub](https://github.com/pablouser1/ProxiTok) for the list of public instances

After generating your OPML, you can find-and-replace the ProxiTok domain to point to a working instance.

## Limitations

- **ProxiTok availability** depends on community-maintained instances
- **Private accounts** won't have accessible RSS feeds
- TikTok RSS feeds via ProxiTok show videos in chronological order
- Self-hosting ProxiTok is the most reliable option
