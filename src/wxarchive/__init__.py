"""wxarchive —— 把微信公众号文章 / 合集保存成本地 Markdown + HTML。

设计目标：给一个 URL 就能用，不需要登录、不需要浏览器、不需要第三方服务。
"""

__version__ = "0.1.0"

from .article import Article, parse_article  # noqa: F401
from .urls import Target, parse_target  # noqa: F401

__all__ = ["Article", "Target", "__version__", "parse_article", "parse_target"]
