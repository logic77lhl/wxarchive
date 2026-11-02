"""网络层：统一的 UA、重试、限速、反爬识别。

关键经验（这些细节决定能不能下下来）：

1. 文章页必须带 ``&scene=27``，否则经常返回「未知错误 / 失效的验证页面」。
2. 用手机微信 UA，命中率最高。
3. 合集接口不需要登录：``/mp/appmsgalbum?action=getalbum&...&f=json``，20 条/页。
4. 请求之间必须有随机间隔，否则很快进入「环境异常」。
"""

from __future__ import annotations

import random
import re
import time
from typing import Any

import requests

DEFAULT_BIZ = "MzkyMDQ5Mzk0Mg=="

UA_MOBILE = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.47(0x18002f2c) "
    "NetType/WIFI Language/zh_CN"
)
UA_DESKTOP = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

ALBUM_API = "https://mp.weixin.qq.com/mp/appmsgalbum"

# 判定为「被拦截」的页面特征
BLOCK_MARKERS = ("未知错误", "环境异常", "失效的验证页", "该内容已被发布者删除")


class FetchError(RuntimeError):
    """网络请求彻底失败（重试后仍不可用）。"""


class CaptchaError(FetchError):
    """被微信风控拦截（302 到 appmsgcaptcha），需要冷却一段时间。"""


def human_sleep(low: float = 1.2, high: float = 2.8) -> None:
    time.sleep(random.uniform(low, high))


class Fetcher:
    """带重试与限速的会话封装。"""

    def __init__(
        self,
        *,
        delay: tuple[float, float] = (1.2, 2.8),
        timeout: int = 40,
        retries: int = 4,
        user_agent: str = UA_MOBILE,
        log=print,
    ) -> None:
        self.delay = delay
        self.timeout = timeout
        self.retries = retries
        self.log = log
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": user_agent,
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Referer": "https://mp.weixin.qq.com/",
            }
        )

    # ---------- 基础请求 ----------
    def get(self, url: str, *, params: dict | None = None, headers: dict[str, str] | None = None) -> requests.Response:
        last: Exception | None = None
        for attempt in range(self.retries):
            try:
                resp = self.session.get(url, params=params, timeout=self.timeout, headers=headers)
                if resp.status_code == 200:
                    return resp
                last = FetchError(f"HTTP {resp.status_code}")
            except requests.RequestException as exc:  # 网络抖动
                last = exc
            time.sleep(1.5 * (attempt + 1))
        raise FetchError(f"请求失败：{url}（{last}）")

    # ---------- 文章 ----------
    def article_html(self, url: str) -> str:
        """下载文章页，返回原始 HTML；失败抛 FetchError。"""
        url = url.split("#")[0]
        # 统一改写 scene：微信对 scene=21 的分享链接更容易弹验证码
        url = re.sub(r"[?&]scene=\d+", "", url)
        url += ("&" if "?" in url else "?") + "scene=27"

        for attempt in range(self.retries):
            resp = self.get(url)
            if "appmsgcaptcha" in resp.url or any("appmsgcaptcha" in r.url for r in resp.history):
                raise CaptchaError("触发微信验证码（访问频率过高）")
            html = resp.text
            ok = len(html) > 20000 and "js_content" in html
            if ok:
                return html
            # 被拦截：换桌面 UA 再试一次，然后退避
            if attempt == 1:
                self.session.headers["User-Agent"] = UA_DESKTOP
            elif attempt >= 2:
                self.session.headers["User-Agent"] = UA_MOBILE
            time.sleep(3 * (attempt + 1))
        raise FetchError(f"文章页被拦截（{url}）")

    # ---------- 合集 ----------
    def album_page(
        self,
        album_id: str,
        biz: str = DEFAULT_BIZ,
        begin_msgid: str | None = None,
        begin_itemidx: str | None = None,
    ) -> dict[str, Any]:
        params = {
            "action": "getalbum",
            "__biz": biz,
            "album_id": album_id,
            "scene": "126",
            "count": "100",
            "is_reverse": "0",
            "f": "json",
        }
        if begin_msgid:
            params["begin_msgid"] = begin_msgid
            params["begin_itemidx"] = begin_itemidx

        resp = self.get(ALBUM_API, params=params)
        data = resp.json()
        base = (data.get("base_resp") or {}).get("ret", 0)
        if base not in (0, "0"):
            raise FetchError(f"合集接口返回错误：{data.get('base_resp')}")
        return data.get("getalbum_resp") or {}
