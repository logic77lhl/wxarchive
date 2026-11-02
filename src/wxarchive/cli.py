"""命令行入口：``wxarchive <url> --out <dir>``。"""

from __future__ import annotations

import argparse
import os
import sys
import time
from collections import deque
from collections.abc import Iterable

from . import __version__
from .album import AlbumItem, album_info, iter_album
from .article import parse_article, save_article
from .fetch import DEFAULT_BIZ, Fetcher, FetchError, human_sleep
from .store import State, url_key, write_index
from .urls import Target, parse_target


def _log(msg: str = "") -> None:
    print(msg, flush=True)


def _parse_delay(value: str) -> tuple[float, float]:
    try:
        low, high = (float(x) for x in value.split(","))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("--delay 格式应为 1.2,2.8") from exc
    if low < 0 or high < low:
        raise argparse.ArgumentTypeError("--delay 区间不合法")
    return low, high


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="wxarchive",
        description="把微信公众号文章 / 合集保存到本地（Markdown + HTML + 图片），无需登录。",
    )
    p.add_argument("url", nargs="*", help="文章或合集链接，可多个")
    p.add_argument("--out", "-o", default="wxarchive_out", help="保存根目录（默认 ./wxarchive_out）")
    p.add_argument("--limit", type=int, default=0, help="最多下载 N 篇（调试用）")
    p.add_argument("--delay", type=_parse_delay, default=(1.2, 2.8), help="每篇间隔秒数区间，默认 1.2,2.8")
    p.add_argument("--no-images", action="store_true", help="不下载图片（只存 HTML/Markdown）")
    p.add_argument("--no-original", action="store_true", help="不保存 original.html 原文存档")
    p.add_argument("--follow-albums", action="store_true", help="顺着文章里的合集链接，继续抓同账号其他专栏")
    p.add_argument("--max-albums", type=int, default=10, help="--follow-albums 时最多扩展几个合集")
    p.add_argument("--list", action="store_true", help="只列出将要下载的文章，不实际下载")
    p.add_argument("--retry-failed", action="store_true", help="忽略已有成功记录，重试此前失败的条目")
    p.add_argument("--version", action="version", version=f"wxarchive {__version__}")
    return p


def _single_articles(targets: Iterable[Target]) -> list[AlbumItem]:
    return [
        AlbumItem(title="", ts=0, msgid=t.msgid, itemidx=t.idx, url=t.url)
        for t in targets
        if t.kind == "article"
    ]


def run(args: argparse.Namespace) -> int:
    if not args.url:
        _log("请提供至少一个微信文章或合集链接，例如：")
        _log('  wxarchive "https://mp.weixin.qq.com/s?__biz=...&mid=...&idx=1&sn=..." -o ./archive')
        return 2

    targets = [parse_target(u) for u in args.url]
    fetcher = Fetcher(delay=args.delay)
    os.makedirs(args.out, exist_ok=True)
    state = State(args.out)

    albums: deque[tuple[str, str]] = deque(
        (t.album_id, t.biz or DEFAULT_BIZ) for t in targets if t.kind == "album"
    )
    queue: deque[AlbumItem] = deque(_single_articles(targets))
    seen_albums: set[str] = set()
    biz_of: dict[str, str] = {t.album_id: (t.biz or DEFAULT_BIZ) for t in targets if t.kind == "album"}

    ok = skipped = failed = 0
    started = time.time()

    def process(item: AlbumItem) -> dict | None:
        nonlocal ok, skipped, failed
        if state.done(item.url) and not args.retry_failed:
            skipped += 1
            return state.data.get(url_key(item.url))

        try:
            html = fetcher.article_html(item.url)
            art = parse_article(html, item.url)
            if art.node is None:
                raise FetchError("页面里没有正文（可能已删除、被折叠或需要登录）")
            rec = save_article(
                art,
                html,
                out_root=args.out,
                fetcher=fetcher,
                download_images=not args.no_images,
                keep_original=not args.no_original,
            )
            state.record(item.url, rec)
            state.save()
            ok += 1
            _log(f"[{ok + skipped}/{ok + skipped + failed}] OK  {rec['datetime']}  {rec['title'][:44]}")
            return rec
        except Exception as exc:  # noqa: BLE001 - 单篇失败不中断整批
            failed += 1
            rec = {"ok": False, "url": item.url, "title": item.title, "error": str(exc)}
            state.record(item.url, rec)
            state.save()
            _log(f"[FAIL] {item.url}  {exc}")
            return rec

    while albums or queue:
        while queue:
            item = queue.popleft()
            rec = process(item)

            if args.follow_albums and rec and rec.get("ok"):
                for aid in rec.get("albums") or []:
                    if aid not in seen_albums and len(seen_albums) < args.max_albums:
                        albums.append((aid, biz_of.get(aid, DEFAULT_BIZ)))

            if args.limit and ok >= args.limit:
                break
            human_sleep(*args.delay)

        if args.limit and ok >= args.limit:
            break
        if not albums:
            break

        album_id, biz = albums.popleft()
        if album_id in seen_albums:
            continue
        seen_albums.add(album_id)
        biz_of.setdefault(album_id, biz)

        try:
            info = album_info(fetcher, album_id, biz)
            _log(f"\n[合集] {info['title'] or album_id} · {info['count']} 篇 · {info['account']}")
        except Exception as exc:  # noqa: BLE001
            _log(f"[合集] {album_id} 信息获取失败：{exc}")

        for item in iter_album(fetcher, album_id, biz):
            if args.list:
                day = time.strftime("%Y-%m-%d", time.localtime(item.ts)) if item.ts else "????-??-??"
                _log(f"  {day}  {item.title}")
                continue
            queue.append(item)

    if args.list:
        return 0

    index_path = write_index(args.out, state.records)
    minutes = (time.time() - started) / 60
    _log(
        f"\n完成：成功 {ok}，跳过（已存在）{skipped}，失败 {failed}；"
        f"用时 {minutes:.1f} 分钟\n索引：{index_path}"
    )
    return 0 if failed == 0 else 1


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return run(args)
    except KeyboardInterrupt:
        _log("\n已中断，进度已保存，重新运行会从断点继续。")
        return 130
    except ValueError as exc:
        _log(f"错误：{exc}")
        return 2


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
