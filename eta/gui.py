"""Local web GUI for Escape the Algorithm.

Starts a private HTTP server on localhost, opens a browser tab, and lets
users drag-and-drop their export file and download the resulting OPML —
no terminal commands required beyond the initial launch.

Usage:
    eta gui              # auto-select port, open browser
    eta gui --port 8080  # specific port
    eta gui --no-browser # skip auto-open (print URL only)
"""

from __future__ import annotations

import base64
import importlib
import json
import os
import socket
import sys
import tempfile
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


# ── Embedded HTML/CSS/JS ──────────────────────────────────────────────────────

_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>eta — Escape the Algorithm</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0d1117;--surface:#161b22;--border:#21262d;
  --text:#c9d1d9;--muted:#8b949e;
  --cyan:#58efec;--green:#56d364;--red:#f85149;--yellow:#e3b341;
}
body{
  background:var(--bg);color:var(--text);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
  font-size:14px;line-height:1.5;min-height:100vh;
  display:flex;flex-direction:column;align-items:center;
  padding:40px 16px 80px;
}
pre.logo{
  font-family:"Courier New",monospace;color:var(--cyan);
  font-size:11px;line-height:1.35;margin-bottom:4px;
  white-space:pre;user-select:none;
}
.tagline{color:var(--muted);font-size:13px;margin-bottom:10px;text-align:center}
.badges{display:flex;gap:8px;margin-bottom:32px;flex-wrap:wrap;justify-content:center}
.badge{
  background:var(--surface);border:1px solid var(--border);
  border-radius:20px;padding:3px 10px;font-size:11px;color:var(--muted);
}
.card{
  width:100%;max-width:560px;background:var(--surface);
  border:1px solid var(--border);border-radius:10px;
  padding:22px 24px;margin-bottom:10px;
}
.step-label{
  font-size:11px;font-weight:600;color:var(--muted);
  text-transform:uppercase;letter-spacing:.08em;margin-bottom:14px;
}
/* ── Drop zone ── */
.drop-zone{
  border:2px dashed var(--border);border-radius:8px;
  padding:32px 20px;text-align:center;cursor:pointer;
  transition:border-color .15s,background .15s;position:relative;
}
.drop-zone:hover,.drop-zone.over{
  border-color:var(--cyan);background:rgba(88,239,236,.04);
}
.drop-zone input[type=file]{
  position:absolute;inset:0;opacity:0;cursor:pointer;width:100%;height:100%;
}
.drop-icon{font-size:30px;margin-bottom:8px;line-height:1}
.drop-primary{font-size:15px;font-weight:500;margin-bottom:4px}
.drop-hint{font-size:12px;color:var(--muted)}
/* ── File pill ── */
.file-pill{
  display:none;align-items:center;gap:10px;
  background:rgba(88,239,236,.06);border:1px solid rgba(88,239,236,.2);
  border-radius:6px;padding:9px 12px;margin-top:12px;
}
.file-pill.show{display:flex}
.file-pill-icon{font-size:18px;flex-shrink:0}
.file-pill-info{flex:1;min-width:0}
.file-pill-name{font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:13px}
.file-pill-meta{font-size:11px;color:var(--muted)}
.file-pill-remove{
  background:none;border:none;color:var(--muted);cursor:pointer;
  font-size:14px;padding:4px;line-height:1;border-radius:4px;flex-shrink:0;
}
.file-pill-remove:hover{color:var(--red)}
/* ── Platform selector ── */
.platforms{display:flex;gap:6px;flex-wrap:wrap}
.plat-btn{
  background:var(--bg);border:1px solid var(--border);color:var(--muted);
  border-radius:20px;padding:5px 13px;font-size:13px;cursor:pointer;
  transition:border-color .15s,color .15s,background .15s;
}
.plat-btn:hover{border-color:var(--cyan);color:var(--text)}
.plat-btn.active{
  border-color:var(--cyan);color:var(--cyan);
  background:rgba(88,239,236,.08);
}
/* ── Spotify extras ── */
.spotify-extras{
  display:none;margin-top:14px;padding-top:14px;
  border-top:1px solid var(--border);
}
.spotify-extras.show{display:block}
.check-row{display:flex;align-items:center;gap:8px;cursor:pointer;user-select:none;margin-bottom:6px}
.check-row input{cursor:pointer;accent-color:var(--cyan)}
.check-row span{font-size:13px}
.api-note{font-size:11px;color:var(--muted);line-height:1.5}
.api-note a{color:var(--cyan);text-decoration:none}
.api-note a:hover{text-decoration:underline}
/* ── Convert button ── */
.btn-convert{
  width:100%;max-width:560px;background:var(--cyan);color:#0d1117;
  border:none;border-radius:8px;padding:12px;
  font-size:15px;font-weight:700;cursor:pointer;
  transition:opacity .15s,transform .1s;margin-bottom:10px;
}
.btn-convert:hover:not(:disabled){opacity:.88}
.btn-convert:active:not(:disabled){transform:scale(.99)}
.btn-convert:disabled{opacity:.3;cursor:not-allowed}
/* ── Result ── */
.result{display:none;width:100%;max-width:560px}
.result.show{display:block}
.result-success{
  background:rgba(86,211,100,.07);border:1px solid rgba(86,211,100,.25);
  border-radius:10px;padding:22px 24px;
}
.result-error{
  background:rgba(248,81,73,.07);border:1px solid rgba(248,81,73,.25);
  border-radius:10px;padding:22px 24px;
}
.result-icon{font-size:22px;margin-bottom:6px}
.result-title{font-size:16px;font-weight:600;margin-bottom:4px}
.result-detail{font-size:13px;color:var(--muted);margin-bottom:16px}
.result-actions{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.btn-download{
  background:var(--green);color:#0d1117;border:none;
  border-radius:6px;padding:9px 18px;font-size:13px;font-weight:700;cursor:pointer;
}
.btn-download:hover{opacity:.88}
.btn-reset{
  background:none;border:1px solid var(--border);color:var(--muted);
  border-radius:6px;padding:8px 14px;font-size:13px;cursor:pointer;
}
.btn-reset:hover{border-color:var(--muted);color:var(--text)}
.what-next{
  margin-top:14px;padding-top:14px;border-top:1px solid rgba(86,211,100,.15);
  font-size:12px;color:var(--muted);
}
.what-next strong{color:var(--text)}
.what-next a{color:var(--cyan);text-decoration:none}
.what-next a:hover{text-decoration:underline}
.error-msg{
  font-family:"Courier New",monospace;font-size:12px;
  color:var(--red);white-space:pre-wrap;word-break:break-word;
  margin-bottom:14px;
}
/* ── Spinner ── */
.spinner{
  display:inline-block;width:13px;height:13px;
  border:2px solid rgba(13,17,23,.25);border-top-color:#0d1117;
  border-radius:50%;animation:spin .6s linear infinite;
  vertical-align:middle;margin-right:6px;
}
@keyframes spin{to{transform:rotate(360deg)}}
/* ── Footer ── */
.footer{
  margin-top:36px;text-align:center;
  font-size:12px;color:var(--muted);line-height:2;
}
.footer a{color:var(--muted);text-decoration:none}
.footer a:hover{color:var(--cyan)}
code{
  background:rgba(255,255,255,.06);border-radius:3px;
  padding:1px 5px;font-family:"Courier New",monospace;font-size:11px;
}
</style>
</head>
<body>

<pre class="logo">  ___  ___  ___ __ _ _ __   ___
 / _ \/ __|/ __/ _` | '_ \ / _ \
|  __/\__ \ (_| (_| | |_) |  __/
 \___||___/\___\__,_| .__/ \___|   the algorithm
                     |_|</pre>

<p class="tagline">Your feed is not your friend. Take it back.</p>

<div class="badges">
  <span class="badge">&#x1F512; 100% local</span>
  <span class="badge">no data leaves your machine</span>
  <span class="badge">zero dependencies</span>
</div>

<!-- Step 1: File -->
<div class="card">
  <div class="step-label">1 &mdash; Drop your export file</div>
  <div class="drop-zone" id="dropZone">
    <input type="file" id="fileInput" accept=".csv,.js,.json,.txt">
    <div class="drop-icon">&#x1F4C2;</div>
    <div class="drop-primary">Drag &amp; drop your export file here</div>
    <div class="drop-hint">or click to browse &nbsp;&middot;&nbsp; .csv &nbsp;.js &nbsp;.json &nbsp;.txt</div>
  </div>
  <div class="file-pill" id="filePill">
    <span class="file-pill-icon">&#x1F4C4;</span>
    <div class="file-pill-info">
      <div class="file-pill-name" id="fileName"></div>
      <div class="file-pill-meta" id="fileMeta"></div>
    </div>
    <button class="file-pill-remove" id="fileRemove" title="Remove">&#x2715;</button>
  </div>
</div>

<!-- Step 2: Platform -->
<div class="card">
  <div class="step-label">2 &mdash; Platform</div>
  <div class="platforms">
    <button class="plat-btn active" data-p="auto">&#x2726; Auto-detect</button>
    <button class="plat-btn" data-p="youtube">YouTube</button>
    <button class="plat-btn" data-p="reddit">Reddit</button>
    <button class="plat-btn" data-p="twitter">Twitter&nbsp;/&nbsp;X</button>
    <button class="plat-btn" data-p="tiktok">TikTok</button>
    <button class="plat-btn" data-p="spotify">Spotify</button>
  </div>
  <div class="spotify-extras" id="spotifyExtras">
    <label class="check-row">
      <input type="checkbox" id="resolveRss">
      <span>Resolve RSS feeds via Podcast Index API</span>
    </label>
    <div class="api-note">
      Requires <code>PODCAST_INDEX_KEY</code> and <code>PODCAST_INDEX_SECRET</code>
      environment variables set before starting the GUI.
      Get free credentials at <a href="https://podcastindex.org/" target="_blank">podcastindex.org</a>.
    </div>
  </div>
</div>

<!-- Convert -->
<button class="btn-convert" id="btnConvert" disabled>Convert to OPML</button>

<!-- Result -->
<div class="result" id="result"></div>

<div class="footer">
  <a href="https://github.com/TheAmericanMaker/Escape-the-algorithm" target="_blank">GitHub</a>
  &nbsp;&middot;&nbsp;
  <a href="https://github.com/TheAmericanMaker/Escape-the-algorithm/tree/main/docs" target="_blank">Docs</a>
  &nbsp;&middot;&nbsp;
  <a href="https://github.com/TheAmericanMaker/Escape-the-algorithm/blob/main/docs/troubleshooting.md" target="_blank">Troubleshooting</a>
  <br>
  For advanced options, use <code>eta --help</code> in your terminal.
</div>

<script>
(function(){
  var file = null, platform = 'auto', blob = null, blobName = 'feeds.opml';

  var dropZone   = document.getElementById('dropZone');
  var fileInput  = document.getElementById('fileInput');
  var filePill   = document.getElementById('filePill');
  var fileNameEl = document.getElementById('fileName');
  var fileMetaEl = document.getElementById('fileMeta');
  var fileRemove = document.getElementById('fileRemove');
  var btnConvert = document.getElementById('btnConvert');
  var resultEl   = document.getElementById('result');
  var spotifyEx  = document.getElementById('spotifyExtras');
  var resolveRss = document.getElementById('resolveRss');

  // ── Drag & drop ──
  dropZone.addEventListener('dragover', function(e){
    e.preventDefault(); dropZone.classList.add('over');
  });
  dropZone.addEventListener('dragleave', function(){
    dropZone.classList.remove('over');
  });
  dropZone.addEventListener('drop', function(e){
    e.preventDefault(); dropZone.classList.remove('over');
    var f = e.dataTransfer.files[0];
    if(f) setFile(f);
  });
  fileInput.addEventListener('change', function(){
    if(fileInput.files[0]) setFile(fileInput.files[0]);
  });
  fileRemove.addEventListener('click', clearFile);

  function setFile(f){
    file = f;
    fileNameEl.textContent = f.name;
    fileMetaEl.textContent = fmtSize(f.size);
    filePill.classList.add('show');
    btnConvert.disabled = false;
    clearResult();
    hintPlatform(f.name);
  }

  function clearFile(){
    file = null; fileInput.value = '';
    filePill.classList.remove('show');
    btnConvert.disabled = true;
    clearResult();
  }

  function clearResult(){
    resultEl.classList.remove('show');
    resultEl.innerHTML = '';
  }

  function fmtSize(b){
    if(b < 1024) return b + ' B';
    if(b < 1048576) return (b/1024).toFixed(1) + ' KB';
    return (b/1048576).toFixed(1) + ' MB';
  }

  function hintPlatform(name){
    var n = name.toLowerCase();
    var hint = null;
    if(n.indexOf('subscriptions') !== -1 && n.slice(-4) === '.csv') hint = 'youtube';
    else if(n.indexOf('subreddit') !== -1 || n.indexOf('reddit') !== -1) hint = 'reddit';
    else if(n.indexOf('following') !== -1 && n.slice(-3) === '.js') hint = 'twitter';
    else if(n.indexOf('user_data') !== -1) hint = 'tiktok';
    else if(n.slice(-5) === '.json' && (n.indexOf('follow') !== -1 || n.indexOf('spotify') !== -1)) hint = 'spotify';
    if(hint) setPlatform(hint);
  }

  // ── Platform selector ──
  document.querySelectorAll('.plat-btn').forEach(function(btn){
    btn.addEventListener('click', function(){ setPlatform(btn.dataset.p); });
  });

  function setPlatform(p){
    platform = p;
    document.querySelectorAll('.plat-btn').forEach(function(b){
      b.classList.toggle('active', b.dataset.p === p);
    });
    spotifyEx.classList.toggle('show', p === 'spotify');
  }

  // ── Convert ──
  btnConvert.addEventListener('click', function(){
    if(!file) return;
    btnConvert.disabled = true;
    btnConvert.innerHTML = '<span class="spinner"></span>Converting\u2026';
    clearResult();

    var reader = new FileReader();
    reader.onload = function(){
      var b64 = reader.result.split(',')[1];
      fetch('/convert', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({
          filename: file.name,
          data: b64,
          platform: platform,
          resolve_rss: (platform === 'spotify' && resolveRss.checked)
        })
      })
      .then(function(r){ return r.json(); })
      .then(function(data){
        if(data.ok) showSuccess(data);
        else showError(data.error);
      })
      .catch(function(err){
        showError(err.message || 'An unexpected error occurred.');
      })
      .finally(function(){
        btnConvert.disabled = !file;
        btnConvert.textContent = 'Convert to OPML';
      });
    };
    reader.readAsDataURL(file);
  });

  function showSuccess(data){
    blob = new Blob([data.opml], {type:'application/xml'});
    blobName = data.filename;
    var pct = data.count ? Math.round(data.feeds_with_rss/data.count*100) : 0;
    var warn = (data.feeds_with_rss < data.count)
      ? '<br><span style="color:var(--yellow)">&#x26A0;</span> ' + (data.count - data.feeds_with_rss) + ' items have no RSS URL and will be skipped by your reader.'
      : '';
    resultEl.innerHTML =
      '<div class="result-success">' +
        '<div class="result-icon">&#x2713;</div>' +
        '<div class="result-title">' + esc(data.count) + ' ' + esc(data.platform) + ' subscriptions converted</div>' +
        '<div class="result-detail">' + esc(data.feeds_with_rss) + ' of ' + esc(data.count) + ' have RSS feeds (' + pct + '%)' + warn + '</div>' +
        '<div class="result-actions">' +
          '<button class="btn-download" id="btnDl">&#x2B07; Download ' + esc(data.filename) + '</button>' +
          '<button class="btn-reset" id="btnAgain">Convert another</button>' +
        '</div>' +
        '<div class="what-next">' +
          '<strong>Next:</strong> open your RSS reader &rarr; Settings &rarr; Import OPML &rarr; select the downloaded file.<br>' +
          'New to RSS readers? See the <a href="https://github.com/TheAmericanMaker/Escape-the-algorithm#recommended-rss-readers" target="_blank">recommended readers list</a>.' +
        '</div>' +
      '</div>';
    resultEl.classList.add('show');

    document.getElementById('btnDl').addEventListener('click', function(){
      var url = URL.createObjectURL(blob);
      var a = document.createElement('a');
      a.href = url; a.download = blobName; a.click();
      URL.revokeObjectURL(url);
    });
    document.getElementById('btnAgain').addEventListener('click', function(){
      clearFile(); setPlatform('auto');
    });
  }

  function showError(msg){
    resultEl.innerHTML =
      '<div class="result-error">' +
        '<div class="result-icon">&#x2715;</div>' +
        '<div class="result-title">Conversion failed</div>' +
        '<div class="error-msg">' + esc(msg) + '</div>' +
        '<div class="result-actions">' +
          '<button class="btn-reset" id="btnRetry">Dismiss</button>' +
        '</div>' +
      '</div>';
    resultEl.classList.add('show');
    document.getElementById('btnRetry').addEventListener('click', clearResult);
  }

  function esc(s){
    return String(s)
      .replace(/&/g,'&amp;').replace(/</g,'&lt;')
      .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }
})();
</script>
</body>
</html>"""


# ── Request handler ───────────────────────────────────────────────────────────

class _Handler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):  # noqa: A002
        pass  # keep stdout clean

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            body = _HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path != "/convert":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        response = _handle_convert(raw)
        body = json.dumps(response).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


# ── Conversion logic ──────────────────────────────────────────────────────────

def _handle_convert(raw: bytes) -> dict:
    """Parse the JSON request, run the appropriate eta parser, return OPML."""
    # --- decode request ---
    try:
        payload = json.loads(raw)
        filename: str = payload["filename"]
        file_data: bytes = base64.b64decode(payload["data"])
        platform: str = payload.get("platform", "auto")
        resolve_rss: bool = bool(payload.get("resolve_rss", False))
    except (KeyError, ValueError) as exc:
        return {"ok": False, "error": f"Invalid request: {exc}"}

    suffix = Path(filename).suffix or ".tmp"
    tmp_path: Path | None = None

    try:
        # write upload to a temp file so parsers can use Path API
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as fh:
            fh.write(file_data)
            tmp_path = Path(fh.name)

        # --- platform detection ---
        if platform == "auto":
            from eta.parsers.detect import detect_platform

            detected = detect_platform(tmp_path)
            if not detected:
                return {
                    "ok": False,
                    "error": (
                        f"Could not detect which platform '{filename}' came from.\n"
                        "Try selecting the platform manually using the buttons above."
                    ),
                }
            platform = detected

        # --- parse ---
        _PARSERS = {
            "youtube": "eta.parsers.youtube",
            "reddit":  "eta.parsers.reddit",
            "twitter": "eta.parsers.twitter",
            "tiktok":  "eta.parsers.tiktok",
            "spotify": "eta.parsers.spotify",
        }
        if platform not in _PARSERS:
            return {"ok": False, "error": f"Unknown platform: '{platform}'"}

        parse_fn = importlib.import_module(_PARSERS[platform]).parse
        items = parse_fn(tmp_path)

        if not items:
            return {
                "ok": False,
                "error": (
                    "No subscriptions found in this file.\n"
                    "Make sure you're using the correct export file for this platform.\n"
                    "See the platform guides at: "
                    "https://github.com/TheAmericanMaker/Escape-the-algorithm/tree/main/docs"
                ),
            }

        # --- optional Spotify RSS resolution ---
        if resolve_rss and platform == "spotify":
            if not os.environ.get("PODCAST_INDEX_KEY"):
                return {
                    "ok": False,
                    "error": (
                        "Podcast Index API credentials not found.\n"
                        "Set PODCAST_INDEX_KEY and PODCAST_INDEX_SECRET environment variables\n"
                        "before starting the GUI, then try again.\n"
                        "Get free credentials at: https://podcastindex.org/"
                    ),
                }
            from eta.resolvers.podcastindex import resolve_feeds

            items = resolve_feeds(items)

        # --- export to OPML string ---
        from eta.exporters.opml import generate_opml

        opml = generate_opml(items, title=f"Escape the Algorithm - {platform.title()}")
        feeds_with_rss = sum(1 for item in items if item.xml_url)

        return {
            "ok": True,
            "platform": platform,
            "count": len(items),
            "feeds_with_rss": feeds_with_rss,
            "filename": f"{platform}_feeds.opml",
            "opml": opml,
        }

    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}

    finally:
        if tmp_path and tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass


# ── Server launcher ───────────────────────────────────────────────────────────

def _free_port() -> int:
    """Find an available localhost port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def start(port: int = 0, open_browser: bool = True) -> None:
    """Start the local GUI server and (optionally) open a browser tab.

    Args:
        port: TCP port to listen on. 0 = pick a free port automatically.
        open_browser: Whether to open the default browser automatically.
    """
    port = port or _free_port()
    url = f"http://127.0.0.1:{port}"
    server = HTTPServer(("127.0.0.1", port), _Handler)

    print(f"\n  eta GUI  \u2192  {url}", file=sys.stderr)
    print("  Press Ctrl+C to stop.\n", file=sys.stderr)

    if open_browser:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  GUI stopped.", file=sys.stderr)
        server.shutdown()
