# wxarchive

> 给一个微信公众号链接，把它完整存到本地：Markdown + 离线 HTML + 原图，按年月日分文件夹。**不需要登录，不需要浏览器。**

[![PyPI](https://img.shields.io/badge/pypi-wxarchive-blue)](https://pypi.org/project/wxarchive/)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Tests](https://github.com/logic77lhl/wxarchive/actions/workflows/ci.yml/badge.svg)](https://github.com/logic77lhl/wxarchive/actions/workflows/ci.yml)

```bash
wxarchive "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=...&album_id=4020951985321934849" -o ./工程塑料
```

```
工程塑料/
├─ _index.csv
└─ 2025/2025-06/2025-06-07_国内PPS发展历程与现状分析/
   ├─ original.html    原文完整 DOM（去脚本），图片保留原始外链
   ├─ index.html       图片已本地化，双击即可离线阅读
   ├─ article.md       正文 Markdown，可直接编辑
   ├─ meta.json        标题 / 作者 / 时间 / 原创 / 摘要 / 所属合集
   └─ images/001.jpg
```

---

## 特性

- **一个链接搞定**：自动识别「单篇文章」和「合集/专栏」，合集自动翻页拿全量。
- **原文保真**：同时保存原文 DOM 与转换后的 Markdown，图片按顺序落地，占位图过滤、重复图去重。
- **离线可读**：生成的 `index.html` 不依赖网络，样式内联，手机上也能看。
- **可断点续传**：中途 Ctrl+C 或断网，重跑自动跳过已完成，只补失败的。
- **不打扰服务器**：默认每篇随机间隔 1.2~2.8 秒，单线程，尽量不触发风控。
- **对 agent 友好**：自带 [SKILL.md](skills/wxarchive/SKILL.md)，opencode / Claude Code / Cursor 装上就能用。

## 安装

```bash
pip install wxarchive
# 或者从源码
git clone https://github.com/logic77lhl/wxarchive.git
cd wxarchive && pip install -e .
```

## 用法

```bash
# 1) 先试 3 篇
wxarchive "<链接>" -o ./out --limit 3

# 2) 全量下载
wxarchive "<链接>" -o ./out

# 3) 只看看有多少篇、都是什么
wxarchive "<链接>" --list

# 4) 顺着文章里的合集，把同账号其他专栏也抓了
wxarchive "<链接>" -o ./out --follow-albums --max-albums 20
```

### 参数

| 参数 | 默认 | 说明 |
|---|---|---|
| `url` | — | 文章或合集链接，可传多个 |
| `--out, -o` | `./wxarchive_out` | 保存根目录 |
| `--limit N` | 0（不限） | 最多下载 N 篇 |
| `--delay a,b` | `1.2,2.8` | 每篇间隔秒数区间 |
| `--no-images` | 关 | 不下载图片 |
| `--no-original` | 关 | 不保存 `original.html` |
| `--follow-albums` | 关 | 扩展抓取文章所属的其他合集 |
| `--max-albums N` | 10 | 扩展上限 |
| `--list` | 关 | 只列标题 |
| `--retry-failed` | 关 | 重试此前失败的条目 |

## 作为 agent skill 使用

把 `skills/wxarchive/` 整个目录拷到你的 agent 技能目录即可：

| 工具 | 放置位置 |
|---|---|
| opencode | `~/.config/opencode/skills/wxarchive/` |
| Claude Code | `~/.claude/skills/wxarchive/` |
| Cursor / 其他 | 项目内 `.agents/skills/wxarchive/`（按你的约定） |

之后直接对 agent 说「把这个链接下载下来」，它会自己调用 `wxarchive`。

也可以完全不用 skill，直接让 agent 执行：

```bash
wxarchive "<URL>" -o "<目录>"
```

## 工作原理（也是踩过的坑）

| 问题 | 解法 |
|---|---|
| 文章页经常返回「未知错误 / 失效的验证页面」 | URL 追加 `&scene=27`，并用手机微信 UA |
| 合集翻页 | `mp/appmsgalbum?action=getalbum&album_id=...&f=json`，20 条/页，用 `begin_msgid`+`begin_itemidx` 续翻 |
| 正文被懒加载 | 取 `#js_content`，把 `img[data-src]` 还原成 `src` |
| 图片防盗链 | 下载时带 `Referer: https://mp.weixin.qq.com/` |
| 1×1 占位图 / 重复二维码 | 小于 1KB 丢弃，同文 md5 去重 |
| 页面 3.7MB 太占空间 | 存原文时去掉 `script/style/link`，单篇降到约 100KB |
| 微信 HTML 转 Markdown 出现空 `###`、`2. 1.` | 转换后做针对性清理 |
| 请求过密被 302 到 `appmsgcaptcha` | 识别后直接报错提示等待，不硬刚 |

## 已知限制

- **只覆盖合集/专栏内的文章**。公众号没有公开的「全部历史消息」接口，不在任何合集中的文章需要登录态（`uin` / `key` / `pass_ticket`）才能枚举。
- **拿不到阅读量 / 点赞 / 在看**：这些走 JS 接口，静态页面里没有。
- 付费文章、已删除文章、被折叠的「分享型」内容无法下载正文。
- 微信风控随时可能变化，如遇大量失败请降低频率或稍后再试。

## 合规声明

本项目仅用于**个人学习、备份与离线阅读**。文章版权归原作者及公众号所有，二次发布、商用、批量搬运需获得授权。请遵守微信平台规则与当地法律，因使用本项目产生的任何后果由使用者自行承担。

## 开发

```bash
pip install -e ".[dev]"
ruff check .
pytest -q
```

## License

[MIT](LICENSE)
