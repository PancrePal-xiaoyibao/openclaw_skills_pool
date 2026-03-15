# OpenClaw Skills Pool

OpenClaw Agent Skills 技能库 —— 收录专为 [OpenClaw](https://openclaw.ai) 平台设计的高质量 Agent Skills，覆盖软件开发、学术研究、玄学命理、医疗健康、效率工具等多个领域。

---

## 目录

- [快速开始](#快速开始)
- [技能列表](#技能列表)
- [特别说明：依赖多 Agent 架构的技能](#特别说明依赖多-agent-架构的技能)
- [目录结构](#目录结构)
- [技能索引维护](#技能索引维护)
- [贡献指南](#贡献指南)

---

## 快速开始

所有技能以独立目录形式组织，每个目录下有一个 `SKILL.md` 作为技能入口文件。在 OpenClaw 平台中，将技能目录路径添加到 Workspace 的技能配置即可加载。

```
openclaw_skills_pool/
├── <skill-name>/
│   ├── SKILL.md          # 技能入口（必须）
│   ├── references/       # 参考资料与知识库
│   ├── scripts/          # 辅助脚本
│   └── templates/        # 输出模板
└── index.json            # 技能索引（由脚本自动维护）
```

---

## 技能列表

### 软件开发

| 技能 | 版本 | 描述 |
|------|------|------|
| [ai-spec](./ai-spec/SKILL.md) | — | 将用户需求转化为生产级技术规范与 AI 编码指令，适用于需求不清晰、架构选型、生成完整技术规格或可执行任务清单时 |
| [code-debugger](./code-debugger/SKILL.md) | — | 基于深度上下文的智能代码调试与增量开发，支持 Bug 定位修复、增量功能开发、Checkfix 闭环及 `.debug` 文档维护 |
| [debug-ui](./debug-ui/SKILL.md) | — | UI 调试与前端视觉审计技能 |
| [superpowers](./superpowers/SKILL.md) | 2.0.0 | 泛用式 AI 任务处理框架，基于系统化思考和任务拆解的复杂问题解决工作流，适用于软件开发、信息查询、问题分析等各种复杂任务 ⚠️ |
| [ralph](./ralph/SKILL.md) | 0.1.0 | Ralph Agent Loop 系统，自主 AI Agent 循环，支持从 PRD 到代码实现的完整项目开发流程，提供 Classic Ralph（需 Amp CLI）和 Ralph YOLO（仅需 Claude Code）两种模式 |

### 研究与知识

| 技能 | 版本 | 描述 |
|------|------|------|
| [deep-research](./deep-research/SKILL.md) | 2.3.0 | 深度调研技能，内置多 Agent 并行执行引擎，支持引用管理、文件发送、轻量量化验证和实时进度反馈，支持 2-8 个并发 Agent ⚠️ |
| [paper-reader](./paper-reader/SKILL.md) | 0.1.0 | 论文阅读助手，资深学术研究员级别的精读与批判性分析，生成结构化精读报告 |
| [network-search](./network-search/SKILL.md) | — | 综合网络搜索技能，集成多种搜索工具，提供可靠的信息检索能力 |
| [scrna-celltype-annotation](./scrna-celltype-annotation/SKILL.md) | 1.0.0 | 基于 Seurat FindAllMarkers 差异表达结果与文献 MCP 工具，对单细胞亚群进行 major/minor 细胞类型注释并生成带文献依据的 Markdown 报告 |

### 前端与设计

| 技能 | 版本 | 描述 |
|------|------|------|
| [frontend-slides](./frontend-slides/SKILL.md) | — | 创建零依赖、动画丰富的 HTML 演示文稿，支持从零创建、从 PowerPoint 转换，帮助非设计师通过视觉探索找到审美偏好 |
| [drawio-xml-roadmap](./drawio-xml-roadmap/SKILL.md) | — | 将文字版流程/路线图系统性转换为符合 draw.io 规范的 mxfile XML，可直接导入 draw.io Desktop，避免解析错误 |

### 效率与办公

| 技能 | 版本 | 描述 |
|------|------|------|
| [office-docs](./office-docs/SKILL.md) | — | Office 文档处理专家，支持 .pptx / .docx / .xlsx 的读取、编辑、创建与校验 |
| [executive-secretary](./executive-secretary/SKILL.md) | 0.1.1 | 高级行政秘书技能，系统化时间管理专家，可调用高德地图 MCP 进行路线规划与通勤时间估算 |
| [feishu-file-transfer](./feishu-file-transfer/SKILL.md) | — | 飞书文件传输任意门，通过 MCP 工具将 Workspace 中的任意文件发送到飞书聊天 |
| [image-recognition](./image-recognition/SKILL.md) | 0.1.0 | 图片识别基础工作流，自动调用 Gemini 进行图片内容分析，然后基于分析结果与用户对话 |

### 医疗健康

| 技能 | 版本 | 描述 |
|------|------|------|
| [medical-advisory](./medical-advisory/SKILL.md) | 0.1.0 | 首席私人医疗架构师，循证医学与中医结合的顶级私人医疗顾问，通过实时调用顶级医学数据库提供科学的健康管理与个性化医疗方案 |

### 玄学命理

| 技能 | 版本 | 描述 |
|------|------|------|
| [metaphysics-generalist](./metaphysics-generalist/SKILL.md) | 0.1.0 | 玄学通析师，综合八字、风水、奇门遁甲、梅花易数等玄学体系的资深专家 |
| [eight-characters-analysis](./eight-characters-analysis/SKILL.md) | 0.1.0 | 八字分析专家，基于天干地支、五行生克理论推算命理，提供专业命理分析与运势预测 |
| [bazi-marriage-matchmaker](./bazi-marriage-matchmaker/SKILL.md) | 0.1.0 | 八字合婚大师，基于日支密码和天干五合的合婚分析专家 |
| [senior-numerology-master](./senior-numerology-master/SKILL.md) | 0.1.0 | 资深命理师，综合八字命理、紫微斗数、风水和易经的全面命理分析大师 |
| [iching-divination](./iching-divination/SKILL.md) | 0.1.0 | 断卦占卜大师，基于易经六十四卦的占卜系统，支持蓍草、金钱卦、铜钱或数字卦等多种方式 |
| [meihua-ease-number-analysis](./meihua-ease-number-analysis/SKILL.md) | 0.1.0 | 梅花易数分析师，擅长数字起卦、体用分析、主互变推演、旺衰判定和外应解读 |
| [six-divines-expert](./six-divines-expert/SKILL.md) | 0.1.0 | 六爻断卦专家，基于易经六十四卦占卜、六爻解卦、动爻分析和预测建议 |
| [qi-dun-jia-yijing-master](./qi-dun-jia-yijing-master/SKILL.md) | 0.1.0 | 奇门遁甲易学宗师，擅长奇门遁甲起局、预测和化解，提供时空定点解析和运筹建议 |
| [fengshui-gardening-geography](./fengshui-gardening-geography/SKILL.md) | 0.1.0 | 阳宅风水园艺地理专家，结合传统风水理论、园艺学和地理学的综合环境分析专家 |

---

## 特别说明：依赖多 Agent 架构的技能

以下技能在完整功能模式下需要搭配 **OpenClaw 的优化版多 Agent 架构**才能发挥全部效能。在不支持并发子 Agent 的环境下，这些技能会自动退化为单 Agent 串行模式，功能可用但效率较低。

### `superpowers` — 泛用式 AI 任务处理框架

**多 Agent 特性**：
- `Subagent-Driven Development`（子代理驱动开发）：每个原子任务由独立子 Agent 完成，两阶段审查（规范符合性 → 代码质量），真正意义上的并发隔离执行
- 任务 capsule 机制：并发 Agent 共享最小化上下文（`task-capsule.md` + `skill-brief.md`），避免重复读取完整历史，显著降低 Token 消耗
- 通过 `superpowers-bootstrap.sh` 统一进入 task session，自动生成默认 agent brief 批次

**启用方式**（在 OpenClaw Workspace 内）：
```bash
bash workspace/scripts/superpowers-bootstrap.sh "<task-slug>" "<reason>" \
  --objective "<目标>" \
  --deliverable "<交付物>" \
  --scope "<范围>"
```

**退化模式**：在不支持子 Agent 的环境（如普通 Cursor/VS Code），技能仍可运行，但所有步骤由单 Agent 串行执行，适合中小型任务。

---

### `deep-research` — 深度调研技能

**多 Agent 特性**：
- 支持 **2–8 个专职 Agent 同时并行工作**：Info Collector（信息收集）、Deep Analyst（深度分析）、Technical Feasibility Analyst（技术可行性）、History Analyst（历史分析）、Synthesis Analyst（综合）、Report Generator（报告生成）、Quant Verifier（量化验证）
- 每个 Agent 只读取自己的 brief + 任务 capsule，不重放完整调研历史，Token 效率大幅提升
- 通过 `deep-research-bootstrap.sh` 统一进入 task session，自动生成 research agent brief 批次

**启用方式**（在 OpenClaw Workspace 内）：
```bash
bash workspace/scripts/deep-research-bootstrap.sh "<task-slug>" "<reason>" \
  --objective "<调研目标>" \
  --deliverable "<交付物>" \
  --scope "<范围>"
```

**退化模式**：在不支持并发子 Agent 的环境，由单 Agent 依次模拟各角色串行执行，调研质量不变，但速度和 Token 效率较低。

---

## 目录结构

```
openclaw_skills_pool/
├── index.json                          # 技能索引（自动维护，勿手动编辑）
├── SKILL_INDEXING.md                   # 索引维护规范与命令
├── SHOWCASE.md                         # 技能联动演示
│
├── superpowers/                        # 泛用式任务处理框架 ⚠️ 多 Agent
│   ├── SKILL.md
│   ├── README.md
│   ├── scripts/
│   ├── references/
│   └── templates/
│
├── deep-research/                      # 深度调研技能 ⚠️ 多 Agent
│   ├── SKILL.md
│   ├── scripts/                        # 量化验证脚本
│   └── references/                     # 研究方法论参考
│
├── code-debugger/                      # 代码调试技能
│   ├── SKILL.md
│   └── agents/                         # Agent 角色定义
│
├── <其他技能>/
│   ├── SKILL.md
│   ├── scripts/                        # 辅助脚本（可选）
│   └── references/                     # 知识库参考（可选）
│
└── ...
```

---

## 技能索引维护

`index.json` 由脚本自动维护，**请勿手动编辑**。在创建、更新或删除技能后，需运行以下命令同步索引：

```bash
# 重建一次索引
node workspace/scripts/rebuild-skills-index.js

# 检查索引与实际文件是否有漂移
node workspace/scripts/check-skills-index.js

# 启动自动监听（长时间编辑会话推荐）
bash workspace/scripts/start-skills-index-watcher.sh

# 停止自动监听
bash workspace/scripts/stop-skills-index-watcher.sh
```

完整的索引维护规范见 [SKILL_INDEXING.md](./SKILL_INDEXING.md)。

---

## 贡献指南

### 新建技能

1. 在仓库根目录创建以技能名称命名的目录（kebab-case）
2. 在目录下创建 `SKILL.md`，参考现有技能的 frontmatter 格式：
   ```markdown
   ---
   name: my-skill
   description: 一句话描述，用于 index.json 和触发判断
   version: 0.1.0
   ---
   ```
3. 按需添加 `references/`、`scripts/`、`templates/` 子目录
4. 运行 `node workspace/scripts/rebuild-skills-index.js` 更新索引

### 技能规范

- `SKILL.md` 的 `description` 字段应清晰描述**适用场景**和**核心能力**，这是 AI 判断是否触发该技能的依据
- 辅助脚本放入 `scripts/`，知识库/参考资料放入 `references/`，输出模板放入 `templates/`
- 运行时产生的中间文件（报告、任务记录等）不应提交到仓库

---

## 相关资源

- [OpenClaw 官方文档](https://docs.openclaw.ai/agent-skills)
- [Superpowers 原始项目](https://github.com/obra/superpowers)（superpowers 技能的灵感来源）
