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

# Prefer clicking over typing? Launch the local web GUI
eta gui

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

| Platform      | Export Source                 | What You Get                                | Status |
| ------------- | ----------------------------- | ------------------------------------------- | ------ |
| **YouTube**   | Google Takeout CSV            | RSS feed for every channel you subscribe to | Ready  |
| **Reddit**    | GDPR data export or text list | RSS feed for every subreddit                | Ready  |
| **Twitter/X** | Data archive (following.js)   | RSS feeds via Nitter instances              | Ready  |
| **TikTok**    | Data export (user_data.json)  | RSS feeds via ProxiTok instances            | Ready  |
| **Spotify**   | Privacy data export JSON      | Podcast RSS feeds via Podcast Index         | Ready* |

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

| Reader                                              | Platform          | Notes                                          |
| --------------------------------------------------- | ----------------- | ---------------------------------------------- |
| [**Miniflux**](https://miniflux.app/)               | Web (self-hosted) | Minimalist, fast, the privacy-conscious choice |
| [**FreshRSS**](https://freshrss.org/)               | Web (self-hosted) | Feature-rich, great mobile support             |
| [**NetNewsWire**](https://netnewswire.com/)         | macOS / iOS       | Free, native, beautiful UX                     |
| [**Newsboat**](https://newsboat.org/)               | Terminal          | For the command-line faithful                  |
| [**Feeder**](https://github.com/spacecowboy/Feeder) | Android           | Free, open source, no account needed           |
| [**Thunderbird**](https://www.thunderbird.net/)     | Desktop           | Email client with built-in RSS                 |

## Never used a terminal?

That's totally fine — this guide will walk you through everything step by step. A terminal is just a text window where you type commands. It sounds scarier than it is.

### Step 1 — Open a terminal

<details>
<summary><strong>🪟 Windows</strong></summary>

1. Press the **Windows key** and type **terminal**
2. Click **Terminal** (or **Command Prompt**) when it appears in the results

   ![Searching for Terminal in the Windows Start menu](docs/screenshots/windows-search-terminal.png)

3. A dark window will open. That's your terminal.

   ![A Windows Terminal window](docs/screenshots/windows-open-terminal.png)

</details>

<details>
<summary><strong>🍎 macOS</strong></summary>

1. Press **⌘ Space** to open Spotlight, then type **terminal**
2. Press **Enter** when **Terminal** is highlighted

   ![Searching for Terminal in macOS Spotlight](docs/screenshots/mac-spotlight-terminal.png)

3. A white or black window will open. That's your terminal.

   ![A macOS Terminal window](docs/screenshots/mac-terminal-open.png)

</details>

<details>
<summary><strong>🐧 Linux</strong></summary>

Press **Ctrl + Alt + T** — this opens a terminal on most Linux desktops. If that doesn't work, search for "Terminal" in your application menu.

![A Linux terminal window](docs/screenshots/linux-terminal-open.png)

</details>

---

### Step 2 — Install eta

Copy and paste this line into your terminal, then press **Enter**:

```
pip install escape-the-algorithm
```

You'll see some text scroll by. When it finishes and you see a `$` or `>` prompt again, the install is done.

> **Tip:** If you see `command not found: pip`, try `pip3 install escape-the-algorithm` instead.

---

### Step 3 — Navigate to your export file

Your export file is most likely in your **Downloads** folder. Here's how to get there:

<details>
<summary><strong>🪟 Windows</strong></summary>

```
cd Downloads
```

To confirm your file is there, type `dir` and press Enter. You should see your file listed.

![Navigating to Downloads on Windows](docs/screenshots/windows-navigate-downloads.png)

</details>

<details>
<summary><strong>🍎 macOS or 🐧 Linux</strong></summary>

```
cd ~/Downloads
```

To confirm your file is there, type `ls` and press Enter. You should see your file listed.

![Navigating to Downloads on macOS](docs/screenshots/mac-navigate-downloads.png)

</details>

---

### Step 4 — Run eta

Once you're in the right folder, run:

```
eta convert your-file-name-here.csv
```

Replace `your-file-name-here.csv` with the actual name of your export file. Not sure of the exact filename? Use `dir` (Windows) or `ls` (Mac/Linux) to list the files and copy it exactly.

When it works, you'll see something like this:

![eta running successfully in a terminal](docs/screenshots/eta-running.png)

That creates a `.opml` file in the same folder. That's your feed file — ready to import into an RSS reader.

---

### Step 5 — Import into an RSS reader

Open your RSS reader of choice, find its **Import** or **Add feeds** option, and select your `.opml` file. Most readers have an OPML import under Settings or File.

![Importing an OPML file into an RSS reader](docs/screenshots/rss-reader-import.png)

Not sure which RSS reader to use? See the [Recommended RSS Readers](#recommended-rss-readers) table below.

---

**That's it.** You're now getting your subscriptions in chronological order, with no algorithm deciding what you see. If you run into any trouble, check the [platform-specific guides](#documentation) or [open an issue](https://github.com/TheAmericanMaker/Escape-the-algorithm/issues).

---

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
eta gui                         Launch the local web GUI (drag, drop, download)
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

GUI flags:
  --port PORT     Port for the local GUI server (default: auto)
  --no-browser    Print URL without opening a browser tab
```

## Documentation

- [Getting Started](docs/getting-started.md) — Full walkthrough from export to RSS reader
- [Troubleshooting & FAQ](docs/troubleshooting.md) — Common problems and fixes
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
git clone https://github.com/TheAmericanMaker/Es