---
name: wxarchive
description: 把一个微信公众号链接（单篇文章，或「合集/专栏」链接）完整下载到本地，输出 Markdown + 可离线阅读的 HTML + 原图，按年月日分文件夹保存，无需登录。当用户粘贴 mp.weixin.qq.com 链接并要求「下载 / 保存 / 备份 / 导出 / 转 Markdown / 抓取专栏」时使用。
---

# 微信公众号归档（wxarchive）

用户给你一个 `mp.weixin.qq.com` 链接时，**不要手动逐篇复制正文**，直接调用本工具。

## 什么时候用

- 用户发来一篇文章链接，想保存到本地、转 Markdown、离线阅读
- 用户发来「合集 / 专栏」链接，想把整个专栏批量下载
- 用户想把某个公众号的内容做成素材库 / 语料 / 知识库

## 怎么做

1. **确认环境**（只需一次）：

   ```bash
   python -c "import wxarchive" || pip install "git+https://github.com/logic77lhl/wxarchive.git"
   ```

2. **先跑 3 篇试水**，确认能下载：

   ```bash
   wxarchive "<URL>" --out "<输出目录>" --limit 3
   ```

3. **确认无误后全量下载**（后台运行，避免超时）：

   ```bash
   wxarchive "<URL>" --out "<输出目录>"
   ```

4. **只想知道有多少篇**：

   ```bash
   wxarchive "<URL>" --list
   ```

## 参数

| 参数 | 说明 |
|---|---|
| `--out, -o` | 输出根目录，默认 `./wxarchive_out` |
| `--limit N` | 只下 N 篇，用于试跑 |
| `--delay 1.2,2.8` | 每篇间隔秒数，**不要低于 1** |
| `--no-images` | 不下图片 |
| `--no-original` | 不存 `original.html` 原文存档 |
| `--follow-albums` | 顺着文章里的合集链接，继续抓同账号其他专栏 |
| `--list` | 只列标题，不下载 |
| `--retry-failed` | 重跑此前失败的条目 |

## 输出结构（不要改）

```
<out>/
├─ _index.csv          # 全部文章索引，UTF-8 BOM，Excel 可直接打开
├─ _state.json         # 断点续传状态
└─ 2025/2025-06/2025-06-07_标题/
   ├─ original.html    # 原文完整 DOM（去脚本），图片保留原始外链
   ├─ index.html       # 图片本地化，双击即可离线阅读
   ├─ article.md       # 正文 Markdown
   ├─ meta.json        # 标题/作者/时间/原创/摘要/所属合集
   └─ images/001.jpg
```

## 硬性要求

- **必须**用工具下载，不要用浏览器或手工复制，否则会丢图片和排版。
- **不要**把 `--delay` 调到 1 秒以下，也不要并发多进程抓同一个号，会触发微信「环境异常」。
- 下载失败时**不要**立刻重跑全部；先 `--retry-failed`，仍失败就等 10 分钟。
- 抓完后向用户报告：成功 / 跳过 / 失败 篇数、输出目录、`_index.csv` 位置。
- 若用户要的是「不在任何合集里的历史文章」，明确告知：需要登录态（`uin`/`key`/`pass_ticket`）才能枚举，本工具只覆盖合集。

## 合规

仅用于个人学习、备份与离线阅读。内容版权归原作者所有，二次发布或商用需获得授权；不要用于批量搬运洗稿。
