import pytest

from wxarchive.urls import parse_target

ALBUM = (
    "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzkyMDQ5Mzk0Mg==&action=getalbum"
    "&album_id=4020951985321934849&scene=126#wechat_redirect"
)
ARTICLE = (
    "https://mp.weixin.qq.com/s?__biz=MzkyMDQ5Mzk0Mg==&mid=2247497665&idx=1"
    "&sn=bd9214d7afe193dbb11f8bf5ddca0772&chksm=abc#rd"
)
SHORT = "https://mp.weixin.qq.com/s/bd9214d7afe193dbb11f8bf5ddca0772"


def test_parse_album():
    t = parse_target(ALBUM)
    assert t.kind == "album"
    assert t.album_id == "4020951985321934849"
    assert t.biz == "MzkyMDQ5Mzk0Mg=="


def test_parse_article_with_query():
    t = parse_target(ARTICLE)
    assert t.kind == "article"
    assert t.msgid == "2247497665"
    assert t.idx == "1"
    assert t.sn == "bd9214d7afe193dbb11f8bf5ddca0772"


def test_parse_short_link():
    t = parse_target(SHORT)
    assert t.kind == "article"
    assert t.sn == "bd9214d7afe193dbb11f8bf5ddca0772"


def test_parse_accepts_whitespace_and_missing_scheme():
    t = parse_target("  mp.weixin.qq.com/s/bd9214d7afe193dbb11f8bf5ddca0772  ")
    assert t.kind == "article"


@pytest.mark.parametrize(
    "bad",
    [
        "",
        "https://example.com/s/abc",
        "https://mp.weixin.qq.com/mp/appmsgalbum?action=getalbum",
        "https://mp.weixin.qq.com/other/path",
    ],
)
def test_parse_invalid(bad):
    with pytest.raises(ValueError):
        parse_target(bad)
