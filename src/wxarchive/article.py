"""文章解析与落盘。

目录约定（按日期分层，和项目一贯的做法保持一致）::

    <out>/2025/2025-06/2025-06-07_标题/
        original.html   原文完整 DOM（去脚本），图片保留原始外链
        index.html      图片本地化，可离线阅读
        article.md      正文 Markdown
        meta.json       结构化元数据
        images/001.jpg
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any

from bs4 import BeautifulSoup

from .fetch import Fetcher, human_sleep
from .render import node_to_markdown, standalone_html

MIN_IMAGE_BYTES = 1024  # 小于 1KB 基本都是 1x1 占位图 / 打点图


@dataclass
class Article:
    url: str
    title: str = ""
    account: str = ""
    author: str = ""
    ts: int = 0
    datetime: str = ""
    date: str = ""
    is_original: bool = False
    desc: str = ""
    albums: list[str] = field(default_factory=list)
    node: Any = None  # BeautifulSoup 节点
    soup: Any = None

    def meta(self) -> dict:
        return {
            "title": self.title,
            "account": self.account,
            "author": self.author,
            "datetime": self.datetime,
            "date": self.date,
            "url": self.url,
            "is_original": self.is_original,
            "desc": self.desc,
            "albums": self.albums,
        }


def _pick(patterns: list[str], html: str) -> str:
    for pat in patterns:
        m = re.search(pat, html)
        if m:
            return m.group(1)
    return ""


def _unescape(value: str) -> str:
    return (
        (value or "")
        .replace("\\x26", "&")
        .replace("\\x22", '"')
        .replace("\\x3c", "<")
        .replace("\\x3e", ">")
        .replace("\\/", "/")
        .replace("\\n", "\n")
    )


def parse_article(html: str, url: str) -> Article:
    """从文章 HTML 中抽取元信息与正文节点（不联网）。"""
    ts_raw = _pick([r'var ct = "(\d+)"', r'create_time\s*=\s*"(\d+)"'], html)
    ts = int(ts_raw) if ts_raw.isdigit() else int(time.time())
    tm = time.localtime(ts)

    art = Article(
        url=url,
        title=_unescape(
            _pick(
                [
                    r"var msg_title = '([^']*)'",
                    r'msg_title\s*=\s*"([^"]*)"',
                    r'<meta property="og:title" content="([^"]*)"',
                ],
                html,
            )
        ).strip(),
        account=_unescape(
            _pick([r'var nickname = "([^"]*)"', r"nick_name:\s*'([^']*)'"], html)
        ).strip(),
        author=_unescape(_pick([r'var author = "([^"]*)"', r"var author = '([^']*)'"], html)).strip(),
        ts=ts,
        datetime=time.strftime("%Y-%m-%d %H:%M:%S", tm),
        date=time.strftime("%Y-%m-%d", tm),
        is_original=bool(re.search(r'id="copyright_logo"', html)) or _pick([r'copyright_stat = "(\d+)"'], html) == "1",
        desc=_unescape(_pick([r'var msg_desc = "([^"]*)"', r'<meta name="description" content="([^"]*)"'], html)),
        albums=sorted(set(re.findall(r"album_id=(\d+)", html))),
    )

    soup = BeautifulSoup(html, "lxml")
    node = soup.find(id="js_content")
    art.soup = soup
    art.node = node
    if node is not None:
        _normalize_node(node)
    return art


def _normalize_node(node) -> None:
    """把懒加载图片转成真实 src，并清掉无用脚本。"""
    for img in node.find_all("img"):
        src = img.get("data-src") or img.get("src") or ""
        if src.startswith("//"):
            src = "https:" + src
        img["src"] = src
        for attr in ("data-src", "data-w", "data-ratio", "data-type", "data-fail"):
            img.attrs.pop(attr, None)
    for tag in node.find_all(["script", "style"]):
        tag.decompose()


def safe_filename(text: str, maxlen: int = 60) -> str:
    """生成 Windows/macOS/Linux 都能用的文件名。"""
    name = re.sub(r'[\\/:*?"<>|\r\n\t]', "_", text or "").strip().strip(".")
    name = re.sub(r"\s+", " ", name)
    if len(name) > maxlen:
        name = name[:maxlen].rstrip()
    return name or "untitled"


def localize_images(node, img_dir: str, *, fetcher: Fetcher, rel_prefix: str = "images") -> None:
    """下载正文图片到本地并改写 src；占位图过滤、重复图去重。"""
    os.makedirs(img_dir, exist_ok=True)
    seen_hashes: set[str] = set()

    for i, img in enumerate(node.find_all("img"), 1):
        src = img.get("src") or ""
        if not src or src.startswith("data:"):
            img.decompose()
            continue

        ext = os.path.splitext(src.split("?")[0])[1].lower()
        if ext not in (".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg"):
            ext = ".jpg"
        path = os.path.join(img_dir, f"{i:03d}{ext}")

        if not os.path.exists(path) or os.path.getsize(path) == 0:
            ok = False
            for _ in range(3):
                try:
                    resp = fetcher.get(src)
                    if len(resp.content) > MIN_IMAGE_BYTES:
                        with open(path, "wb") as fh:
                            fh.write(resp.content)
                        ok = True
                        break
                except Exception:  # 单张图失败不影响整篇
                    pass
                time.sleep(1.5)
            if not ok:
                img.decompose()
                continue
            human_sleep(0.15, 0.4)

        digest = hashlib.md5(open(path, "rb").read()).hexdigest()
        if digest in seen_hashes:  # 二维码 / 分隔线之类重复出现
            os.remove(path)
            img.decompose()
            continue
        seen_hashes.add(digest)

        img["src"] = f"{rel_prefix}/{os.path.basename(path)}"
        for attr in ("style", "class", "width", "height"):
            img.attrs.pop(attr, None)


def save_article(
    art: Article,
    html: str,
    *,
    out_root: str,
    fetcher: Fetcher,
    download_images: bool = True,
    keep_original: bool = True,
) -> dict:
    """把一篇文章写成一套文件，返回索引记录。"""
    folder = os.path.join(
        out_root,
        art.date[:4],
        art.date[:7],
        f"{art.date}_{safe_filename(art.title)}",
    )
    os.makedirs(folder, exist_ok=True)

    if keep_original:
        original = BeautifulSoup(html, "lxml")
        for tag in original.find_all(["script", "style", "noscript", "link"]):
            tag.decompose()
        with open(os.path.join(folder, "original.html"), "w", encoding="utf-8") as fh:
            fh.write(str(original))

    node = art.node
    if download_images:
        localize_images(node, os.path.join(folder, "images"), fetcher=fetcher)

    with open(os.path.join(folder, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(standalone_html(art, str(node)))

    with open(os.path.join(folder, "article.md"), "w", encoding="utf-8") as fh:
        fh.write(node_to_markdown(node, art))

    with open(os.path.join(folder, "meta.json"), "w", encoding="utf-8") as fh:
        json.dump(art.meta(), fh, ensure_ascii=False, indent=2)

    return {
        "ok": True,
        "url": art.url,
        "title": art.title,
        "date": art.date,
        "datetime": art.datetime,
        "dir": os.path.relpath(folder, out_root),
        "albums": art.albums,
    }
