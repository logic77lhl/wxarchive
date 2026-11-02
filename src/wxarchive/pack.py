"""把下载好的归档打包：生成可搜索的离线索引页 + 可选 zip。

用法::

    python -m wxarchive.pack E:\\WeChat_articles\\工程塑料
    python -m wxarchive.pack E:\\WeChat_articles\\工程塑料 --zip 工程塑料.zip
    python -m wxarchive.pack E:\\WeChat_articles\\工程塑料 --site index.html --zip out.zip
"""

from __future__ import annotations

import argparse
import html
import json
import os
import shutil
import sys
import time
from typing import Any

INDEX_TEMPLATE = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · 共 {count} 篇</title>
<style>
  :root{{--fg:#1f2328;--muted:#6b7280;--line:#e5e7eb;--accent:#0b6bcb}}
  *{{box-sizing:border-box}}
  body{{margin:0;padding:28px 20px 60px;color:var(--fg);background:#fff;
       font:15px/1.6 -apple-system,"PingFang SC","Microsoft YaHei",sans-serif}}
  header{{max-width:960px;margin:0 auto 18px}}
  h1{{font-size:22px;margin:0 0 6px}}
  .sub{{color:var(--muted);font-size:13px}}
  .tools{{max-width:960px;margin:0 auto 14px;display:flex;gap:10px;flex-wrap:wrap;align-items:center}}
  input{{flex:1;min-width:220px;padding:9px 12px;border:1px solid var(--line);border-radius:8px;font-size:14px}}
  input:focus{{outline:2px solid #cfe3fb;border-color:var(--accent)}}
  .count{{color:var(--muted);font-size:13px;white-space:nowrap}}
  table{{max-width:960px;margin:0 auto;border-collapse:collapse;width:100%;font-size:14px}}
  th,td{{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}}
  th{{position:sticky;top:0;background:#fff;font-size:12px;color:var(--muted);font-weight:600;letter-spacing:.04em}}
  td.date{{white-space:nowrap;color:var(--muted);font-variant-numeric:tabular-nums;width:96px}}
  a{{color:var(--accent);text-decoration:none}}
  a:hover{{text-decoration:underline}}
  tr:hover td{{background:#fafbfc}}
  mark{{background:#fff3a3;padding:0 2px;border-radius:2px}}
  .empty{{max-width:960px;margin:40px auto;color:var(--muted);text-align:center}}
</style>
</head>
<body>
<header>
  <h1>{title}</h1>
  <div class="sub">共 {count} 篇 · 归档于 {built} · 点击标题打开本地文章</div>
</header>
<div class="tools">
  <input id="q" type="search" placeholder="搜索标题、日期…（Ctrl+K）" autofocus>
  <span class="count" id="count"></span>
</div>
<table>
  <thead><tr><th>日期</th><th>标题</th></tr></thead>
  <tbody id="rows"></tbody>
</table>
<div class="empty" id="empty" hidden>没有匹配的文章</div>
<script>
const DATA = {data};
const rows = document.getElementById('rows');
const empty = document.getElementById('empty');
const counter = document.getElementById('count');
const q = document.getElementById('q');

function render(list) {{
  rows.innerHTML = list.map(a =>
    `<tr><td class="date">${{a.d}}</td><td><a href="${{encodeURI(a.p)}}/index.html" target="_blank">${{esc(a.t)}}</a></td></tr>`
  ).join('');
  counter.textContent = list.length + ' / ' + DATA.length;
  empty.hidden = list.length > 0;
}}
function esc(s) {{
  return s.replace(/[&<>"]/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}})[c]);
}}
function filter() {{
  const k = q.value.trim().toLowerCase();
  if (!k) return render(DATA);
  render(DATA.filter(a => (a.t + ' ' + a.d).toLowerCase().includes(k)));
}}
q.addEventListener('input', filter);
document.addEventListener('keydown', e => {{
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {{ e.preventDefault(); q.focus(); }}
}});
render(DATA);
</script>
</body>
</html>
"""


def collect(root: str) -> list[dict[str, Any]]:
    """扫描归档目录，读出每篇文章的元数据。"""
    items: list[dict[str, Any]] = []
    for dirpath, _dirnames, filenames in os.walk(root):
        if "meta.json" not in filenames:
            continue
        try:
            with open(os.path.join(dirpath, "meta.json"), encoding="utf-8") as fh:
                meta = json.load(fh)
        except (OSError, json.JSONDecodeError):
            continue
        rel = os.path.relpath(dirpath, root).replace("\\", "/")
        items.append(
            {
                "t": meta.get("title") or os.path.basename(dirpath),
                "d": (meta.get("date") or "")[:10],
                "p": rel,
            }
        )
    items.sort(key=lambda x: (x["d"], x["t"]), reverse=True)
    return items


def write_site(root: str, items: list[dict], path: str, title: str) -> str:
    data = json.dumps(items, ensure_ascii=False, separators=(",", ":"))
    page = INDEX_TEMPLATE.format(
        title=html.escape(title),
        count=len(items),
        built=time.strftime("%Y-%m-%d %H:%M"),
        data=data,
    )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(page)
    return path


def make_zip(root: str, target: str, text_only: bool = False) -> str:
    if os.path.exists(target):
        os.remove(target)
    if not target.lower().endswith(".zip"):
        target += ".zip"

    if not text_only:
        return shutil.make_archive(target[:-4], "zip", root_dir=root)

    # 只打包文字（跳过 images/），体积能小一个数量级，方便微信/邮件发送
    import zipfile

    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d != "images"]
            for name in filenames:
                full = os.path.join(dirpath, name)
                arc = os.path.relpath(full, root).replace("\\", "/")
                zf.write(full, arc)
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="wxarchive-pack", description="为归档生成离线索引页 / zip 包")
    parser.add_argument("root", help="归档根目录（wxarchive 的 --out）")
    parser.add_argument("--site", default="index.html", help="索引页文件名（相对归档根目录）")
    parser.add_argument("--title", default="", help="索引页标题，默认取目录名")
    parser.add_argument("--zip", default="", help="同时生成 zip 包（路径）")
    parser.add_argument("--text-only", action="store_true", help="zip 时跳过 images/，只打包文字")
    args = parser.parse_args(argv)

    if not os.path.isdir(args.root):
        print(f"目录不存在：{args.root}", file=sys.stderr)
        return 2

    items = collect(args.root)
    title = args.title or os.path.basename(os.path.abspath(args.root))
    site_path = os.path.join(args.root, args.site)
    write_site(args.root, items, site_path, title)
    print(f"索引页：{site_path}（{len(items)} 篇）")

    if args.zip:
        archive = make_zip(args.root, args.zip, text_only=args.text_only)
        size = os.path.getsize(archive) / 1048576
        print(f"压缩包：{archive}（{size:.1f} MB）")

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
