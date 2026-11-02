"""URL 解析：判断用户给的是「单篇文章」还是「合集（专栏）」。

支持的形态：

    合集
    https://mp.weixin.qq.com/mp/appmsgalbum?__biz=XXX&action=getalbum&album_id=4020951985321934849
    https://mp.weixin.qq.com/mp/appmsgalbum?__biz=XXX&action=getalbum&album_id=4020951985321934849#wechat_redirect

    文章
    https://mp.weixin.qq.com/s?__biz=XXX&mid=2247497665&idx=1&sn=bd92...
    https://mp.weixin.qq.com/s/bd9214d7afe193dbb11f8bf5ddca0772
"""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse


@dataclass(frozen=True)
class Target:
    """一次下载任务的输入。"""

    kind: str  # "album" | "article"
    url: str
    biz: str = ""
    album_id: str = ""
    msgid: str = ""
    idx: str = ""
    sn: str = ""

    def __str__(self) -> str:  # pragma: no cover - 仅用于日志
        if self.kind == "album":
            return f"album({self.album_id})"
        return f"article({self.msgid or self.sn})"


def parse_target(raw: str) -> Target:
    """把用户粘贴的链接解析成 Target，识别失败时抛 ValueError。"""
    if not raw or not raw.strip():
        raise ValueError("URL 为空")

    url = raw.strip().split()[0]
    if url.startswith("//"):
        url = "https:" + url
    elif not url.lower().startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if not host.endswith("mp.weixin.qq.com"):
        raise ValueError(f"不是微信公众号链接：{url}")

    qs = parse_qs(parsed.query)
    biz = (qs.get("__biz") or [""])[0]
    path = parsed.path or ""

    # 合集 / 专栏
    if "appmsgalbum" in path:
        album_id = (qs.get("album_id") or [""])[0]
        if not album_id:
            raise ValueError("合集链接里缺少 album_id")
        return Target(kind="album", url=url, biz=biz, album_id=album_id)

    # 文章：/s?mid=..&idx=..&sn=..  或  /s/<sn>
    if path.startswith("/s"):
        msgid = (qs.get("mid") or [""])[0]
        idx = (qs.get("idx") or [""])[0]
        sn = (qs.get("sn") or [""])[0]
        if not sn and path.count("/") >= 2:
            sn = path.rstrip("/").split("/")[-1]
        if not sn:
            raise ValueError("文章链接里缺少 sn 参数")
        return Target(kind="article", url=url, biz=biz, msgid=msgid, idx=idx, sn=sn)

    raise ValueError(f"无法识别的微信链接：{url}")
