"""合集（专栏）枚举：翻页拿到全部文章的标题 / 链接 / 发布时间。"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from .fetch import DEFAULT_BIZ, Fetcher, human_sleep


@dataclass
class AlbumItem:
    title: str
    ts: int
    msgid: str
    itemidx: str
    url: str

    @property
    def key(self) -> str:
        return f"{self.msgid}_{self.itemidx}"


def iter_album(
    fetcher: Fetcher,
    album_id: str,
    biz: str = DEFAULT_BIZ,
    *,
    max_items: int = 0,
    pause: tuple[float, float] = (0.5, 1.2),
) -> Iterator[AlbumItem]:
    """逐页产出合集内的文章，自带去重与终止条件。"""
    seen: set[str] = set()
    begin_msgid = begin_itemidx = None
    total = 0

    while True:
        resp = fetcher.album_page(album_id, biz, begin_msgid, begin_itemidx)
        arts = resp.get("article_list") or []
        if not arts:
            return

        for a in arts:
            key = a.get("key") or a.get("url") or ""
            if key in seen:
                continue
            seen.add(key)
            item = AlbumItem(
                title=(a.get("title") or "").strip(),
                ts=int(a.get("create_time") or 0),
                msgid=str(a.get("msgid") or ""),
                itemidx=str(a.get("itemidx") or ""),
                url=a.get("url") or "",
            )
            total += 1
            yield item
            if max_items and total >= max_items:
                return

        last = arts[-1]
        next_msgid = str(last.get("msgid") or "")
        next_idx = str(last.get("itemidx") or "")
        if (next_msgid, next_idx) == (begin_msgid, begin_itemidx):
            return  # 翻不动了，防死循环
        begin_msgid, begin_itemidx = next_msgid, next_idx

        if resp.get("continue_flag") != "1" and len(arts) < 100:
            return
        human_sleep(*pause)


def album_info(fetcher: Fetcher, album_id: str, biz: str = DEFAULT_BIZ) -> dict:
    """合集标题、简介、总篇数。"""
    resp = fetcher.album_page(album_id, biz)
    base = resp.get("base_info") or {}
    return {
        "id": album_id,
        "title": base.get("title", ""),
        "description": base.get("description", ""),
        "count": base.get("article_count") or len(resp.get("article_list") or []),
        "account": base.get("nickname", ""),
    }
