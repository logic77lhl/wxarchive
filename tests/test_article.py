import json
from pathlib import Path

import pytest

from wxarchive.article import localize_images, parse_article, save_article

FIXTURE = Path(__file__).parent / "fixtures" / "article.html"
URL = "https://mp.weixin.qq.com/s?__biz=MzA=&mid=1&idx=1&sn=deadbeef"


class FakeResponse:
    def __init__(self, content: bytes) -> None:
        self.content = content


class FakeFetcher:
    """只返回两种图：正常图 2KB、占位图 100B。"""

    def get(self, url: str) -> FakeResponse:
        if "tiny" in url:
            return FakeResponse(b"\x00" * 100)
        return FakeResponse(b"\xff" * 2048)


@pytest.fixture()
def article():
    html = FIXTURE.read_text(encoding="utf-8")
    return parse_article(html, URL), html


def test_parse_metadata(article):
    art, _ = article
    assert art.title == "测试文章标题"
    assert art.account == "测试公众号"
    assert art.author == "测试作者"
    assert art.date == "2025-06-07"
    assert art.is_original is True
    assert art.desc == "这是一段摘要"
    assert art.albums == ["4020951985321934849"]


def test_parse_content_node(article):
    art, _ = article
    assert art.node is not None
    assert "第一段正文" in art.node.get_text()
    # 脚本应被移除，懒加载图片应转成真实 src
    assert art.node.find("script") is None
    srcs = [img["src"] for img in art.node.find_all("img")]
    assert srcs[0].startswith("https://mmbiz.qpic.cn/")


def test_localize_images_filters_placeholder(article, tmp_path):
    art, _ = article
    localize_images(art.node, str(tmp_path / "images"), fetcher=FakeFetcher())
    files = list((tmp_path / "images").iterdir())
    assert len(files) == 1  # 占位图被过滤
    assert art.node.find("img")["src"] == "images/001.jpg"


def test_save_article_layout(article, tmp_path):
    art, html = article
    rec = save_article(art, html, out_root=str(tmp_path), fetcher=FakeFetcher())

    folder = tmp_path / rec["dir"]
    assert folder.exists()
    assert rec["dir"].replace("\\", "/").startswith("2025/2025-06/2025-06-07_")
    for name in ("original.html", "index.html", "article.md", "meta.json"):
        assert (folder / name).exists(), name

    md = (folder / "article.md").read_text(encoding="utf-8")
    assert md.startswith("# 测试文章标题")
    assert "![](images/001.jpg)" in md
    assert "###" not in md.split("---")[0]

    meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
    assert meta["url"] == URL
    assert meta["albums"] == ["4020951985321934849"]

    html_out = (folder / "index.html").read_text(encoding="utf-8")
    assert "images/001.jpg" in html_out
    assert "console.log" not in html_out
