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

### Nitter Availability

Since early 2024, X/Twitter has blocked guest account access, which broke most public Nitter instances. Some community-maintained instances still work, but availability varies. Check:

- [status.d420.de/nitter](https://status.d420.de/) — live instance health tracker
- [Nitter instance list](https://github.com/zedeus/nitter/wiki/Instances)

After generating your OPML, you can find-and-replace the Nitter domain in the file to point to a working instance. Self-hosting Nitter with your own Twitter API credentials is the most reliable option.

### Archives With Only User IDs

Some Twitter data archives only contain numeric user IDs (via intent URLs like `twitter.com/intent/user?user_id=12345`) without usernames. In this case, `eta` preserves the user IDs but cannot generate RSS feed URLs. You'll see these as "Twitter User 12345" entries with empty RSS URLs.

To get usernames, you can:
1. Visit each intent URL in your browser to see the profile
2. Use a third-party tool to batch-resolve IDs to usernames

## Limitations

- **Nitter availability** is unreliable since X blocked guest access in 2024. Self-hosting is recommended.
- **Private accounts** won't have accessible RSS feeds regardless of instance
- **ID-only archives** from official Twitter exports may lack usernames — RSS feeds can't be generated from IDs alone
- RSS feeds show tweets in chronological order (which is the point)
