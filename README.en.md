[中文](README.md) | **English**

# wxarchive

> Give it a WeChat Official Account link and it saves the whole thing locally: Markdown + offline HTML + original images, sorted into date folders. **No login, no browser.**

[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

```bash
wxarchive "<article-or-album-url>" -o ./archive
```

```
archive/
├─ _index.csv
└─ 2025/2025-06/2025-06-07_article-title/
   ├─ original.html    full DOM, scripts stripped, images still remote
   ├─ index.html       images localised, open offline
   ├─ article.md       body as Markdown, editable
   ├─ meta.json        title / author / date / original / summary / album
   └─ images/001.jpg
```

---

## Features

- **One link does it** — detects single articles vs. albums/columns; albums are paginated to fetch everything.
- **Fidelity** — keeps both the original DOM and converted Markdown, downloads images in order, drops placeholders and duplicates.
- **Offline reading** — the generated `index.html` has inline styles and no network dependency; works on phones.
- **Resumable** — Ctrl+C or a dropped connection is fine; re-running skips what's done and retries what failed.
- **Polite** — random 1.2–2.8 s delay per article, single-threaded, to avoid tripping rate limits.
- **Agent-friendly** — ships [SKILL.md](skills/wxarchive/SKILL.md) for opencode / Claude Code / Cursor.

## Install

> Not on PyPI yet; install from source.

```bash
git clone https://github.com/logic77lhl/wxarchive.git
cd wxarchive
pip install .
```

Development mode (with test dependencies):

```bash
pip install -e ".[dev]"
```

## Usage

```bash
# 1) dry run: three articles
wxarchive "<url>" -o ./out --limit 3

# 2) everything
wxarchive "<url>" -o ./out

# 3) just see what's there
wxarchive "<url>" --list

# 4) follow the album links and grab the account's other columns
wxarchive "<url>" -o ./out --follow-albums --max-albums 20
```

### Options

| Flag | Default | Meaning |
|---|---|---|
| `url` | — | article or album URL; multiple allowed |
| `--url-file` | — | read URLs from a file, one per line |
| `--out, -o` | `./wxarchive_out` | output root |
| `--limit N` | 0 (no limit) | stop after N articles |
| `--delay a,b` | `1.2,2.8` | delay range in seconds |
| `--cooldown N` | 900 | pause in seconds after repeated captcha blocks |
| `--no-images` | off | skip image downloads |
| `--no-original` | off | skip `original.html` |
| `--follow-albums` | off | also fetch other albums by the same account |
| `--split-albums` | off | one subfolder per album; duplicates stored twice |
| `--max-albums N` | 10 | limit for album expansion |
| `--list` | off | list titles only |
| `--retry-failed` | off | retry previously failed items |

## As an agent skill

Copy `skills/wxarchive/` into your agent's skills directory:

| Tool | Location |
|---|---|
| opencode | `~/.config/opencode/skills/wxarchive/` |
| Claude Code | `~/.claude/skills/wxarchive/` |
| Cursor / others | `.agents/skills/wxarchive/` in the project |

Then just tell the agent "download this link" and it will call `wxarchive`. You can skip the skill entirely and run the command yourself.

## How it works (and the traps)

| Problem | Fix |
|---|---|
| Article pages often return "unknown error / invalid verification page" | append `&scene=27` to the URL and use a mobile WeChat User-Agent |
| Album pagination | `mp/appmsgalbum?action=getalbum&album_id=...&f=json`, 20 per page, continue with `begin_msgid` + `begin_itemidx` |
| Lazy-loaded body | take `#js_content` and rewrite `img[data-src]` back to `src` |
| Image hotlink protection | send `Referer: https://mp.weixin.qq.com/` when downloading |
| 1×1 placeholders / duplicate QR codes | drop anything under 1 KB, dedupe by md5 within an article |
| 3.7 MB pages | strip `script/style/link` from the saved original — down to ~100 KB |
| Empty `###` and `2. 1.` after HTML→Markdown | targeted cleanup pass |
| Redirected to `appmsgcaptcha` when too fast | detect it, fail with a wait message instead of hammering |

## Known limits

- **Album/column articles only.** WeChat exposes no public "all historical posts" endpoint; articles outside any album require a logged-in session (`uin` / `key` / `pass_ticket`) to enumerate.
- **No read/like/"wow" counts** — those come from JS endpoints, not the static page.
- Paid articles, deleted articles, and collapsed "share" content can't be captured.
- WeChat's rate limiting changes without notice; if failures spike, slow down or try later.

## Compliance

This project is for **personal study, backup, and offline reading**. Copyright belongs to the original authors and accounts; republishing, commercial use, or bulk redistribution requires permission. Follow WeChat's terms and local law. You are responsible for how you use it.

## Moving an archive to another machine

Package it first (this also generates a searchable offline index page):

```bash
# full package (images included, roughly the original size)
wxarchive-pack ./archive --zip archive.zip

# text only — usually a few MB, fine for chat apps or email
wxarchive-pack ./archive --zip archive_text.zip --text-only
```

Then pick a transfer method:

**LAN (fastest, nothing to install)**

```bash
python -m http.server 8000
# on the other machine: http://<your-ip>:8000/
```

Find your IP with `ipconfig` (the "IPv4 address" line).

| Method | Good for | Notes |
|---|---|---|
| LAN HTTP / shared folder | same Wi-Fi, hundreds of MB | 1–2 minutes on gigabit |
| WeChat file transfer | text-only package | ~100 MB per file |
| Cloud drive | different locations | slower upload, no hassle |
| USB drive | large files | most reliable |

> Whoever receives the zip unzips it and double-clicks `index.html` — a searchable offline index, no Python needed.

## Development

```bash
pip install -e ".[dev]"
ruff check .
pytest -q
```

## License

[MIT](LICENSE)
