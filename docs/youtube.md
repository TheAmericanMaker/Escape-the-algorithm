# YouTube Export Guide

## How to Export Your YouTube Subscriptions

YouTube subscriptions can be exported via Google Takeout.

### Step 1: Request Your Data

1. Go to [Google Takeout](https://takeout.google.com/)
2. Click **Deselect all** (you don't need everything)
3. Scroll down and check **YouTube and YouTube Music**
4. Click **All YouTube data included**, then select only **subscriptions**
5. Click **OK**, then **Next step**
6. Choose your export format (ZIP is fine) and click **Create export**
7. Wait for the email — this can take minutes to hours

### Step 2: Find the CSV File

1. Download and extract the ZIP file
2. Navigate to `Takeout/YouTube and YouTube Music/subscriptions/`
3. The file you need is `subscriptions.csv`

The CSV file looks like this:

```
Channel Id,Channel Url,Channel Title
UC1JTQBa5QxZCpXrFSkMxmPw,http://www.youtube.com/channel/UC1JTQBa5QxZCpXrFSkMxmPw,Raycevick
UCFl7yKfcRcFmIUbKeCA-SJQ,http://www.youtube.com/channel/UCFl7yKfcRcFmIUbKeCA-SJQ,Joji
```

Note: Header names may differ by locale, but the column order is always the same.

### Step 3: Convert

```bash
eta youtube subscriptions.csv -o youtube_feeds.opml
```

This creates an OPML file with an RSS feed for every YouTube channel you're subscribed to.

### How YouTube RSS Works

Every YouTube channel has a hidden RSS feed at:

```
https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID
```

The `eta youtube` command builds these URLs automatically from your subscription list. When you subscribe to these feeds in an RSS reader, you'll see every new video in chronological order — no algorithm.
