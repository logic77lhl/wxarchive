"""断点续传状态与索引文件。"""

from __future__ import annotations

import csv
import hashlib
import json
import os


def url_key(url: str) -> str:
    return hashlib.md5(url.split("#")[0].encode("utf-8")).hexdigest()


class State:
    """``_state.json``：记录每篇的下载结果，支持中断后继续。"""

    def __init__(self, root: str) -> None:
        self.path = os.path.join(root, "_state.json")
        self.data: dict[str, dict] = {}
        if os.path.exists(self.path):
            try:
                with open(self.path, encoding="utf-8") as fh:
                    self.data = json.load(fh)
            except (OSError, json.JSONDecodeError):
                self.data = {}

    def done(self, url: str) -> bool:
        return bool(self.data.get(url_key(url), {}).get("ok"))

    def record(self, url: str, rec: dict) -> None:
        self.data[url_key(url)] = rec

    def save(self) -> None:
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(self.data, fh, ensure_ascii=False, indent=1)
        os.replace(tmp, self.path)

    @property
    def records(self) -> list[dict]:
        return [v for v in self.data.values() if v.get("ok")]


def write_index(root: str, records: list[dict]) -> str:
    """生成 ``_index.csv``（UTF-8 BOM，Excel 直接打开不乱码）。"""
    path = os.path.join(root, "_index.csv")
    rows = sorted(records, key=lambda r: r.get("datetime", ""))
    with open(path, "w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["序号", "日期", "时间", "标题", "本地目录", "原文链接"])
        for i, r in enumerate(rows, 1):
            writer.writerow(
                [i, r.get("date", ""), r.get("datetime", ""), r.get("title", ""), r.get("dir", ""), r.get("url", "")]
            )
    return path
