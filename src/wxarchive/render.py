"""正文渲染：Markdown 清理 + 可离线阅读的独立 HTML。"""

from __future__ import annotations

import re

from markdownify import markdownify

_EMPTY_HEADING = re.compile(r"^#{1,6}$")
_NESTED_ORDERED = re.compile(r"^(\d+)\.\s+\d+\.\s+")
_NESTED_BULLET = re.compile(r"^([-*+])\s+[-*+]\s+")
_LIST_ITEM = re.compile(r"^([-*+]|\d+\.)\s")


def clean_markdown(text: str) -> str:
    """修掉微信 HTML 转换后常见的三类噪音：

    1. 空标题 ``###``
    2. 嵌套列表导致的 ``2. 1.`` 双重编号
    3. 列表项之间多余空行（会把一个列表拆成多个）
    """
    lines: list[str] = []
    for raw in text.split("\n"):
        indent = raw[: len(raw) - len(raw.lstrip())]
        stripped = raw.strip()
        if _EMPTY_HEADING.match(stripped):
            continue
        stripped = _NESTED_ORDERED.sub(r"\1. ", stripped)
        stripped = _NESTED_BULLET.sub(r"\1 ", stripped)
        lines.append(indent + stripped)

    kept: list[str] = []
    for i, line in enumerate(lines):
        if not line.strip() and 0 < i < len(lines) - 1:
            prev, nxt = lines[i - 1].strip(), lines[i + 1].strip()
            if _LIST_ITEM.match(prev) and _LIST_ITEM.match(nxt):
                continue
        kept.append(line)

    return re.sub(r"\n{3,}", "\n\n", "\n".join(kept))


def node_to_markdown(node, article) -> str:
    body = clean_markdown(markdownify(str(node), heading_style="ATX", bullets="-")).strip()
    header = [
        f"# {article.title}",
        "",
        f"- 公众号：{article.account}",
        f"- 作者：{article.author or article.account}",
        f"- 发布：{article.datetime}",
        f"- 原文：{article.url}",
        "",
    ]
    if article.desc:
        header += [f"> {article.desc}", ""]
    return "\n".join(header) + "\n" + body + "\n"


HTML_TEMPLATE = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  body{{max-width:760px;margin:32px auto;padding:0 18px;color:#222;
       font:16px/1.8 -apple-system,"PingFang SC","Microsoft YaHei",sans-serif}}
  img{{max-width:100%;height:auto;display:block;margin:14px auto}}
  h1{{font-size:24px;line-height:1.45;margin-bottom:6px}}
  .meta{{color:#888;font-size:13px;border-bottom:1px solid #eee;
        padding-bottom:12px;margin-bottom:22px;word-break:break-all}}
  blockquote{{border-left:3px solid #ddd;margin:16px 0;padding:2px 14px;color:#666}}
  pre{{background:#f6f8fa;padding:12px;overflow:auto;border-radius:6px}}
  table{{border-collapse:collapse;width:100%;font-size:14px}}
  th,td{{border:1px solid #ddd;padding:6px 10px}}
</style>
</head>
<body>
<h1>{title}</h1>
<div class="meta">{account} · {author} · {datetime}<br>原文：<a href="{url}">{url}</a></div>
{content}
</body>
</html>
"""


def standalone_html(article, content_html: str) -> str:
    return HTML_TEMPLATE.format(
        title=article.title,
        account=article.account,
        author=article.author or article.account,
        datetime=article.datetime,
        url=article.url,
        content=content_html,
    )
