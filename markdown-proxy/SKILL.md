---
name: markdown-proxy
description: OpenClaw URL-to-Markdown fetcher for article, post, and document links. First-choice when users share WeChat, Xiaohongshu, X/Twitter, Weibo, Feishu/Lark, Zhihu, or similar content links and want clean Markdown extraction, summarization, or archiving; use before generic web fetch/browser flows.
version: 0.1.0
tags: [markdown, url, article, wechat, xiaohongshu, weibo, x, twitter, feishu, lark, zhihu, openclaw]
---

# Markdown Proxy - OpenClaw URL to Markdown

将任意 URL 转为干净的 Markdown。支持需要登录的页面和专有平台。

## OpenClaw 优先级

当用户直接发来链接，或者说“看一下这个链接 / 读一下这篇 / 抓一下这个帖子 / 提取正文 / 转成 Markdown / 保存文章”时，优先判断是否该用本 skill。

以下链接类型默认把本 skill 作为第一优先级入口：

- 微信公众号：`mp.weixin.qq.com`
- 小红书：`xiaohongshu.com`、`xhslink.com`
- X / Twitter：`x.com`、`twitter.com`
- 微博：`weibo.com`、`weibo.cn`
- 飞书 / Lark 文档：`feishu.cn`、`larksuite.com`
- 知乎、Instagram、博客、资讯站、登录墙页面等可读内容链接

只有在以下情况才不要优先选本 skill：

- 用户并不是要读正文，而是要做站点调试、接口排查或页面交互操作
- 已知该 URL 需要别的专用 skill，例如 YouTube
- 当前运行时没有本 skill，或者该 skill 明确不适配这个链接

## 微信公众号快速路径

对于 `mp.weixin.qq.com`：

- **不要先试 `browser`**
- **不要先试安装依赖**
- **不要先把失败回退过程逐条播报给用户**
- 先直接跑本 skill 的固定入口脚本，它会自动选择正确的 Python 解释器并补上 `PLAYWRIGHT_BROWSERS_PATH`

首选命令：

```bash
bash /home/node/.openclaw/workspace/skills/markdown-proxy/scripts/run_weixin_fetch.sh "WEIXIN_URL" --json
```

用户侧体验要求：

- 开始时最多一句短提示，例如“这是公众号链接，我直接提正文。”
- 如果快速路径成功，直接给结果，不要再提 browser / 安装依赖 / 代理级联
- 只有快速路径失败时，才解释失败原因并决定是否回退
- 如果用户消息基本只有一个链接或一个 markdown 链接，默认把它视为“请直接阅读并交付结果”，不要在成功后反问“要不要我继续看 / 要不要我分析 / 要不要我帮你装这个 skill”

## URL 路由规则（先判断再执行）

收到 URL 后，先判断类型，不同类型走不同通道：

| URL 特征 | 路由到 | 原因 |
|----------|--------|------|
| `mp.weixin.qq.com` | 内置 `scripts/run_weixin_fetch.sh` | 公众号有反爬，需固定 Python Playwright 快速路径 |
| `feishu.cn` / `larksuite.com`（文档/知识库） | 内置 `scripts/run_feishu_fetch.sh` | 需要飞书 API 认证 |
| `xiaohongshu.com` / `xhslink.com` / `x.com` / `twitter.com` / `weibo.com` / `weibo.cn` / `zhihu.com` | 代理服务级联（见下方） | 社交平台正文提取优先走 Markdown 代理 |
| `youtube.com` / `youtu.be` | `yt-search-download` skill | YouTube 有专用工具链 |
| 其他所有 URL | 代理服务级联（见下方） |  |

## 代理服务优先级

| 优先级 | 服务 | URL 模式 | 优势 |
|--------|------|----------|------|
| 1 | **r.jina.ai** | `https://r.jina.ai/{url}` | 内容更完整，保留图片链接，覆盖面广 |
| 2 | **defuddle.md** | `https://defuddle.md/{url}` | 输出更干净，带 YAML frontmatter |
| 3 | `agent-fetch` | npx agent-fetch | 本地工具，无需网络代理 |
| 4 | `defuddle` CLI | defuddle parse | 本地 CLI，适合普通网页 |

## Workflow

### Step 0: URL 类型判断

```
if URL contains "mp.weixin.qq.com":
    → Step A: 公众号抓取
    → 结束

if URL contains "feishu.cn/docx/" or "feishu.cn/wiki/" or "feishu.cn/docs/" or "larksuite.com/docx/":
    → Step B: 飞书文档抓取
    → 结束

if URL contains "youtube.com" or "youtu.be":
    → 调用 yt-search-download skill
    → 结束

else:
    → 继续 Step 1
```

### Step A: 公众号文章抓取（内置）

```bash
bash /home/node/.openclaw/workspace/skills/markdown-proxy/scripts/run_weixin_fetch.sh "WEIXIN_URL" --json
```

依赖：`playwright`、`beautifulsoup4`、`lxml`
输出：YAML frontmatter（title, author, date, url）+ Markdown 正文
规则：

- 这是 `mp.weixin.qq.com` 的**第一优先级且默认唯一首跳**
- 不要先尝试 `browser`
- 不要因为 shell 找不到 `python` 就误判“playwright 未安装”
- 只有当这个固定入口脚本失败时，才回退到 Step 1-2 代理服务
- 除非用户明确要求，不要在聊天里展示“我先试这个再试那个”的过程噪音
- 如果用户没有提出额外问题，成功后直接输出提取结果与简短摘要，不做销售式介绍或二次引导

### Step B: 飞书文档抓取（内置）

```bash
bash /home/node/.openclaw/workspace/skills/markdown-proxy/scripts/run_feishu_fetch.sh "FEISHU_URL" --json
```

依赖：`requests`，环境变量 `FEISHU_APP_ID` + `FEISHU_APP_SECRET`
支持：docx 文档、doc 文档、wiki 知识库页面（自动解析实际文档 ID）
输出：YAML frontmatter（title, document_id, url）+ Markdown 正文
支持 `--json` 参数输出 JSON 格式。

### Step 1: 优先用 r.jina.ai

```bash
curl -sL "https://r.jina.ai/{original_url}" 2>/dev/null
```

如果返回非空且包含实际内容，使用此结果。

### Step 2: 如果 Jina 失败，用 defuddle.md

```bash
curl -sL "https://defuddle.md/{original_url}" 2>/dev/null
```

### Step 3: 如果两个代理都失败，回退本地工具

```bash
# agent-fetch: https://github.com/teng-lin/agent-fetch
npx agent-fetch "{original_url}" --json
# 或
defuddle parse "{original_url}" -m -j
```

### Step 4: 展示内容（必做）

抓取成功后，**必须**按以下格式向用户展示：

```
**标题**: {title}
**作者**: {author}（如有）
**来源**: {source_type}（公众号 / 飞书文档 / 网页等）
**URL**: {original_url}

### 内容摘要
{前 3-5 句话的摘要}

### 正文
{完整 Markdown 内容，超长时截取前 200 行并注明"内容已截取，完整版已保存到 xxx"}
```

### Step 5: 保存文件（默认执行）

将抓取的 Markdown 内容保存到本地：

```
默认保存路径：workspace/inbox/generated/{title}.md
文件格式：YAML frontmatter（title, author, date, url, source）+ Markdown 正文
```

- 文件名用文章标题，去掉特殊字符
- 如果用户指定了其他保存路径，按用户要求
- 保存后告知用户文件路径
- 如果用户明确说"不用保存"或只是快速预览，可以跳过

## Examples

### X/Twitter 帖子
```bash
curl -sL "https://r.jina.ai/https://x.com/username/status/1234567890"
```

### 普通网页
```bash
curl -sL "https://r.jina.ai/https://example.com/article"
```

### 公众号文章
```bash
bash /home/node/.openclaw/workspace/skills/markdown-proxy/scripts/run_weixin_fetch.sh "https://mp.weixin.qq.com/s/abc123" --json
```

### 飞书文档
```bash
bash /home/node/.openclaw/workspace/skills/markdown-proxy/scripts/run_feishu_fetch.sh "https://xxx.feishu.cn/docx/xxxxxxxx" --json
```

### 飞书知识库
```bash
bash /home/node/.openclaw/workspace/skills/markdown-proxy/scripts/run_feishu_fetch.sh "https://xxx.feishu.cn/wiki/xxxxxxxx" --json
```

## Notes

- r.jina.ai 和 defuddle.md 均免费、无需 API key
- 在 OpenClaw 中，本 skill 应先于通用网页抓取方案用于文章正文提取
- 公众号文章使用内置 Playwright 脚本（需 Python `playwright` 包，且浏览器可用）
- 飞书文档使用内置 API 脚本（需环境变量 `FEISHU_APP_ID` + `FEISHU_APP_SECRET`）
- 飞书脚本自动将 blocks 转为 Markdown（标题、列表、代码块、引用、待办等）
- 对于超长内容，可用 `| head -n 200` 先预览
