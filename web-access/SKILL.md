---
name: web-access
description: OpenClaw global network-routing skill for search, web fetch, dynamic pages, login-gated browsing, and browser interaction. Default choice for broad online research and website tasks; use before ad hoc web_search/web_fetch/browser flows, but defer article/social/document body extraction to markdown-proxy when the primary goal is clean Markdown.
version: 0.1.0
homepage: https://github.com/eze-is/web-access
tags: [web, network, search, fetch, browser, openclaw, dynamic-page, login, routing]
---

# Web Access - OpenClaw Network Routing

这是一个 **OpenClaw 联网总控 skill**。

它的职责不是替代 OpenClaw 原生工具，而是为下面这些能力提供统一的路由策略：

- `web_search`
- `web_fetch`
- `browser`
- `markdown-proxy`
- 必要时的 MCP 搜索通道

核心原则：

- **广义联网任务默认先想起本 skill**
- **文章 / 帖子 / 文档正文提取不要抢 `markdown-proxy` 的活**
- **优先一手来源，优先最小代价达成目标**

## 何时使用

当用户要你做这些事情时，优先使用本 skill：

- 搜索最新信息、新闻、政策、公司动态、工具用法
- 查看某个网站的内容，但还不确定该走搜索、抓取还是浏览器
- 访问动态渲染页面
- 访问登录后网站
- 在网页里点击、翻页、填表、下载、登录后继续操作
- 需要在多个网页 / 多个来源之间做探索式调研
- 明确说“帮我搜一下 / 查一下 / 看官网 / 去网站里找 / 打开网页看看 / 帮我浏览这个站”

## 何时不要优先用本 skill

如果满足以下条件，优先考虑 `markdown-proxy` 而不是本 skill：

- 用户给了一个明确的文章 / 帖子 / 文档链接
- 目标是**提取正文**、**转 Markdown**、**总结内容**、**归档文章**
- 链接属于这些类型之一：
  - 微信公众号
  - 小红书帖子
  - X / Twitter
  - 微博
  - 飞书 / Lark 文档
  - 知乎 / 博客 / 资讯正文页

简化判断：

- **“去网上找 / 搜一下 / 浏览站点 / 登录后操作” -> `web-access`**
- **“把这个链接正文提出来 / 转 Markdown” -> `markdown-proxy`**

如果你误选了本 skill，但发现任务本质只是文章正文提取，应立刻切换到 `markdown-proxy` 的处理方式。

特别地：

- `mp.weixin.qq.com` 正文提取不要升级到 `browser`
- 直接交给 `markdown-proxy` 的本地 Python Playwright 快速路径：
- `bash /home/node/.openclaw/workspace/skills/markdown-proxy/scripts/run_weixin_fetch.sh "<url>" --json`

## OpenClaw 工具映射

原始上游 skill 依赖 Claude Code 的 `WebSearch` / `WebFetch` / 自建 CDP Proxy。

在当前 OpenClaw 工作区里，应映射为：

| 任务场景 | OpenClaw 首选 |
|---------|---------------|
| 发现信息来源、搜索关键词结果 | `web_search` 或 MCP 搜索通道 |
| 已知公开 URL，需要正文 / 可读内容 | `web_fetch` |
| 已知文章 / 帖子 / 文档链接，目标是正文提取和 Markdown | `markdown-proxy` |
| 动态渲染、登录态、站内导航、点击交互 | `browser` |
| 需要原始 HTML / 特定响应头 / 特定结构字段，且运行时允许命令执行 | `curl` / `exec` 作为补充，而不是默认首选 |

## 默认路由顺序

### 1. 先定义成功标准

在真正联网前，先明确：

- 用户到底要什么结果
- 什么算完成
- 是要“发现信息”，还是“拿正文”，还是“操作网页”

不要一上来机械调用工具。

### 2. 决定第一条路径

优先按下面顺序判断：

1. **文章 / 帖子 / 文档正文提取**
   - 直接走 `markdown-proxy`
   - 如果是 `mp.weixin.qq.com`，优先本地 Python Playwright 包装脚本，不要先试 `browser`
2. **当前事实 / 新闻 / 政策 / 推荐 / 最新信息**
   - 搜索是必需动作
   - 优先参考 `workspace/doc/general-search-routing.md`
3. **已知公开 URL，目标是读页面主内容**
   - 先 `web_fetch`
4. **页面明显依赖 JS、登录态、滚动加载或交互**
   - 直接 `browser`
5. **已知 `web_fetch` 和静态抓取对该站不稳定**
   - 直接 `browser`

### 3. 如果第一条路径失败，怎么切

- `web_search` 找不到信息：
  - 换搜索词
  - 换搜索通道
  - 升级到一手来源页面
- `web_fetch` 结果噪音太大或正文缺失：
  - 如果是文章正文页，切到 `markdown-proxy`
  - 如果是动态页，切到 `browser`
- `browser` 被登录墙挡住：
  - 先判断目标内容是否其实已经可读
  - 确认必须登录后，再提示用户处理登录态
- 多轮尝试没有质变：
  - 不要在同一方法上死磕
  - 重新判断是不是路径错了、目标不存在、或原请求需要降级回答

## 搜索规则

### 当前事实默认必须搜索

这些问题默认不能只靠记忆：

- 新闻
- 最新政策
- 公司近况
- 新版工具能力
- 行情 / 宏观 / 推荐
- 任何带“最新 / 最近 / 今天 / 现在 / current / latest”语义的问题

### 搜索通道优先级

优先遵循：

- `workspace/doc/general-search-routing.md`

如果当前会话已知有 MCP 搜索能力，优先 MCP；否则再用原生 `web_search`。

### 一手来源优先

搜索引擎是发现入口，不是最终证据。

一旦定位到高可信来源，就应尽快切到：

- 官网
- 官方文档
- 原始公告
- 原始论文
- 平台原始页面

不要拿多个二手结果互相循环印证。

## 抓取与浏览规则

### `web_fetch`

适合：

- 已知公开 URL
- 需要读取主内容
- 不依赖登录态
- 不需要复杂交互

不适合：

- 强前端渲染
- 滚动加载
- 登录后页面
- 站内搜索 / 多步点击

### `browser`

适合：

- 动态页面
- 登录态页面
- 多步导航
- 点击、翻页、展开、下载、上传、填表
- 需要像真人一样探索页面

进入浏览器层后：

- 先看页面结构，再决定下一步动作
- 只开自己需要的 tab
- 完成后关闭自己创建的 tab
- 不要碰用户原有 tab，除非用户明确要求

### `markdown-proxy`

适合：

- 微信公众号
- 小红书 / 微博 / X / Twitter 正文
- 飞书 / Lark 文档
- 博客 / 资讯 / 正文页 Markdown 提取

这类任务里，`markdown-proxy` 应视为本 skill 的**特化下游路由**。

## 站点经验

如果 `references/site-patterns/` 下有对应域名经验文件，优先读取。

如需手动辅助匹配，可用：

```bash
bash workspace/skills/web-access/scripts/match-site.sh "<domain-or-user-request>"
```

注意：

- 当前工作区保留了上游 `scripts/cdp-proxy.mjs` 作为参考件
- **在 OpenClaw 集成模式下，默认不要把它当第一选择**
- 原生 `browser` 工具优先；只有在明确做兼容性研究或手工调试时才考虑这些 legacy 脚本

## 强规则

- 不要把所有网页任务都粗暴丢给浏览器，先判断能否用更轻的方式完成
- 不要把所有链接正文提取都丢给 `web_fetch`，文章正文优先 `markdown-proxy`
- 不要把搜索结果本身当作最终证据
- 不要在一个失败路径上重复重试而不换策略
- 如果所有联网路径都失败，要明确告诉用户：
  - 试了哪些路径
  - 哪条失败
  - 为什么失败
  - 当前回答是降级版还是无法完成

## 参考件

按需读取：

| 文件 | 何时读取 |
|------|---------|
| `references/cdp-api.md` | 需要理解原始上游 skill 的 CDP 设计思想或低层浏览器控制模式时 |
| `references/site-patterns/{domain}.md` | 目标网站已有经验文件时 |
