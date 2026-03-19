# Reddit Export Guide

## How to Export Your Reddit Subscriptions

There are two ways to get your subreddit list out of Reddit.

### Option A: Reddit Data Request (Official)

1. Go to [Reddit Data Request](https://www.reddit.com/settings/data-request)
2. Click **Request my data**
3. Wait for the email (can take up to 48 hours)
4. Download and extract the ZIP file
5. Look for a file containing your subscribed subreddits (often `subscribed_subreddits.csv`)

Then convert:

```bash
eta reddit subscribed_subreddits.csv -o reddit_feeds.opml
```

### Option B: Manual List (Quick and Easy)

If you don't want to wait for the data request, just make a text file with your subreddits:

```
python
linux
privacy
selfhosted
opensource
```

Any of these formats work:
- Plain names: `python`
- With prefix: `r/python`
- Full URLs: `https://www.reddit.com/r/python`
- Lines starting with `#` are treated as comments

Then convert:

```bash
eta reddit my_subreddits.txt -o reddit_feeds.opml
```

### How Reddit RSS Works

Every subreddit has an RSS feed at:

```
https://www.reddit.com/r/SUBREDDIT/.rss
```

Your RSS reader will show new posts from each subreddit in chronological order, with no algorithmic ranking or recommended content.
