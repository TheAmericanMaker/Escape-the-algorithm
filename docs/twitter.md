# Twitter/X Export Guide

## How to Export Your Following List

### Option A: Official Twitter Data Archive

1. Go to **Settings** > **Your Account** > **Download an archive of your data**
2. Click **Request archive**
3. Wait for Twitter to prepare your archive (can take 24-48 hours)
4. Download and extract the ZIP file
5. Find the file at `data/following.js`

This file contains every account you follow.

### Option B: Manual Text List

Create a text file with one username per line:

```
@username1
@username2
@username3
```

You can also use full URLs:

```
https://x.com/username1
https://twitter.com/username2
```

## Converting to OPML

```bash
# From Twitter data archive
eta twitter data/following.js -o twitter_feeds.opml

# From a text file of usernames
eta twitter my_follows.txt -o twitter_feeds.opml

# Preview first
eta twitter data/following.js --dry-run
```

## How Twitter RSS Works

Twitter/X does not offer native RSS feeds. `eta` generates feed URLs using [Nitter](https://github.com/zedeus/nitter), an open-source alternative Twitter frontend that provides RSS feeds for any public account.

The default RSS URL pattern is:
```
https://nitter.net/{username}/rss
```

### Finding a Working Nitter Instance

Nitter instances can go up and down. If the default instance (`nitter.net`) isn't working, you can find active instances at:

- [Nitter instance list](https://github.com/zedeus/nitter/wiki/Instances)
- [status.d420.de/nitter](https://status.d420.de/nitter/)

After generating your OPML, you can find-and-replace the Nitter domain in the file if needed.

## Limitations

- **Private accounts** won't have accessible RSS feeds regardless of instance
- **Nitter availability** depends on community-maintained instances
- **Rate limiting** by Twitter/X may affect Nitter instances periodically
- RSS feeds show tweets in chronological order (which is the point)
