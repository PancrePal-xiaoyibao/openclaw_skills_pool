---
name: ralph
description: Ralph Agent Loop 系统 - 自主 AI Agent 循环系统，支持从 PRD 到代码实现的完整项目开发流程。提供两种执行模式：Classic Ralph（需要 Amp CLI）和 Ralph YOLO（推荐，无需 Amp CLI，只用 Claude Code）。
version: 0.1.0
---

# Ralph - 自主 AI Agent 循环系统

这是一个**自主 AI Agent 循环系统**，提供**两种执行模式**完成项目开发：
1. **Classic Ralph** - 通过重复运行 Amp 来完成 PRD（需要 Amp CLI）
2. **Ralph YOLO** - 直接使用 Claude Code 子 Agent 完成（无需 Amp！）✨

内存通过 git 历史、`prd-progress.txt` 和 `prd.json` 持久化。

---

## 核心理念

### 自主 Agent 循环系统

**核心思想**：每个 AI Agent 都有有限的上下文，大型任务需要分解为小故事
- **每次迭代都是全新的 Amp 实例**：没有之前工作的记忆
- **跨迭代状态**：Git 历史（之前迭代的提交）、`prd-progress.txt`（学习内容和上下文）、`prd.json`（已完成故事）

### 两种执行模式

#### 1. Classic Ralph（原版）

**优点**：
- 成熟稳定，经过验证
- 完全独立的 Amp 实例
- 适合大规模项目

**缺点**：
- ❌ 需要 Amp CLI
- ❌ 需要 jq 工具
- ❌ 需要配置 bash 脚本
- ❌ 外部循环管理

**使用场景**：
- 已有 Amp 环境的专业用户
- 需要完全隔离的开发环境

---

#### 2. Ralph YOLO（新版推荐！）✨

**优点**：
- ✅ 无需 Amp CLI！只用 Claude Code
- ✅ 无需 jq 和其他依赖
- ✅ 主会话保持完整上下文
- ✅ 实时进度跟踪和监控
- ✅ 可以随时中断和恢复
- ✅ 更容易调试和干预

**缺点**：
- 新功能，可能存在未知问题

**使用场景**：
- 快速原型开发
- 不想安装 Amp 的用户
- 需要实时监控开发进度
- 消费版 Claude Code 用户（无 Amp）✨

**推荐**：多数用户应该优先尝试 **Ralph YOLO**！

---

## 适用场景

**触发条件**：
- ✅ 需要完整的从 PRD 到代码实现的项目开发
- ✅ 需要将 PRD 转换为可执行的代码和任务
- ✅ 需要自动跟踪项目进度和状态
- ✅ 需要支持敏捷开发流程（用户故事、迭代）
- ✅ 需要持久的内存系统（Git、prd.json、prd-progress.txt）

**典型任务**：
- 从 PRD 到代码实现的完整项目开发
- 功能实现（用户故事、迭代）
- Bug 修复和重构
- 技术债务清理
- 文档生成和维护

---

## Agent 体系

### Agent A: PRD Generator（产品需求文档生成器）

**职责**：将用户需求转换为结构化的 PRD 文档
**核心能力**：
- 询问 3-5 个澄清问题（带选项）
- 生成结构化的 PRD 文档
- 保存到 `tasks/prd-[feature-name].md`
- 定义 3-5 个用户故事（User Stories）
- 定义验收标准（Acceptance Criteria）

**工具链**：
- Claude Code（与用户交互）
- 文本生成和格式化

**输出**：
- PRD 文档（Markdown 格式）
- 用户故事列表
- 验收标准

---

### Agent B: Story Implementer（故事实现器）

**职责**：将 PRD 中的用户故事转换为可执行的代码
**核心能力**：
- 读取 PRD 文档
- 转换为 `prd.json`（JSON 格式）
- 创建功能分支
- 实现每个用户故事
- 提交代码到 Git
- 更新 `prd-progress.txt`

**工具链**：
- Git（版本控制）
- Claude Code（代码生成）
- 代码调试器（code-debugger）
- AI 指令优化工程师（ai-spec）

**输出**：
- 功能分支（Git）
- 代码提交
- `prd.json`（更新的）
- `prd-progress.txt`（更新的）

---

### Agent C: Quality Checker（质量检查器）

**职责**：检查代码质量，运行测试，验证验收标准
**核心能力**：
- 运行测试套件
- 代码质量检查（lint、格式化）
- 验收标准验证
- 生成测试报告
- 识别需要修复的问题

**工具链**：
- 代码调试器（code-debugger）
- 测试框架（如 Jest、pytest）
- 代码质量工具（如 ESLint、Pylint）

**输出**：
- 测试报告
- 质量检查报告
- 需要修复的问题列表

---

### Agent D: Progress Tracker（进度跟踪器）

**职责**：跟踪项目进度，生成状态报告
**核心能力**：
- 读取 `prd.json` 和 `prd-progress.txt`
- 生成进度报告
- 识别未完成的任务
- 生成待办事项列表

**工具链**：
- Git（提交历史）
- 文本分析
- JSON 解析

**输出**：
- 进度报告（Markdown 格式）
- 待办事项列表
- 完成度百分比

---

## 工作流程

### 阶段 1: PRD 生成

**Agent A (PRD Generator)** 执行：
1. 接收用户需求描述
2. 询问 3-5 个澄清问题（带选项）
3. 生成结构化的 PRD 文档
4. 定义 3-5 个用户故事
5. 定义验收标准
6. 保存到 `tasks/prd-[feature-name].md`

**输出**：
- PRD 文档（Markdown 格式）
- 用户故事列表
- 验收标准

---

### 阶段 2: PRD 转换

**Agent B (Story Implementer)** 执行：
1. 读取 PRD 文档
2. 解析用户故事
3. 转换为 `prd.json`（JSON 格式）
4. 创建功能分支
5. 开始实现循环

**输出**：
- `prd.json`（JSON 格式）
- 功能分支（Git）

---

### 阶段 3: 实现循环（Implementation Loop）

**Agent B (Story Implementer)** 执行：
1. 读取 `prd.json`
2. 获取下一个未完成的用户故事
3. 生成代码（使用 ai-spec 和 code-debugger）
4. 提交代码到 Git
5. 更新 `prd.json`（标记故事为完成）
6. 更新 `prd-progress.txt`（记录日志）

**Agent C (Quality Checker)** 执行（可选）：
1. 读取最新的提交
2. 运行测试套件
3. 代码质量检查
4. 验收标准验证
5. 生成测试报告

**输出**：
- 代码提交
- `prd.json`（更新的）
- `prd-progress.txt`（更新的）
- 测试报告（可选）

---

### 阶段 4: 进度跟踪

**Agent D (Progress Tracker)** 执行：
1. 读取 `prd.json` 和 `prd-progress.txt`
2. 生成进度报告
3. 识别未完成的任务
4. 生成待办事项列表

**输出**：
- 进度报告（Markdown 格式）
- 待办事项列表
- 完成度百分比

---

## 输出格式

### PRD 文档格式

```markdown
# [功能名称] - PRD

## 功能概述

**目标**：[1-2 句话描述功能目标]

**用户痛点**：[1-2 句话描述用户痛点]

## 用户故事

### US-001: [用户故事标题]
**作为** [角色]
**我想要** [目标]
**以便** [利益]

**验收标准**：
- [ ] [标准 1]
- [ ] [标准 2]

### US-002: [用户故事标题]
...

## 技术要求

**功能需求**：
- [需求 1]
- [需求 2]

**非功能需求**：
- [需求 1]
- [需求 2]
```

---

### prd.json 格式

```json
{
  "featureName": "[功能名称]",
  "featureSlug": "[功能-slug]",
  "userStories": [
    {
      "id": "US-001",
      "title": "[用户故事标题]",
      "status": "pending",
      "passes": 0,
      "priority": "high"
    },
    {
      "id": "US-002",
      "title": "[用户故事标题]",
      "status": "pending",
      "passes": 0,
      "priority": "medium"
    }
  ]
}
```

---

### 进度报告格式

```markdown
# [功能名称] - 进度报告

## 总体进度

**完成度**：[X]%
**已完成故事**：[N]/[M]
**未完成故事**：[M-N]/[M]

## 已完成的用户故事

- US-001: [标题] ✓
- US-002: [标题] ✓

## 未完成的用户故事

- US-003: [标题] (priority: [high/medium/low])
- US-004: [标题] (priority: [high/medium/low])
```

---

## 使用指南

### 何时使用本 skill

**推荐使用场景**：
- 🚀 完整的项目开发（从 PRD 到代码实现）
- 🔄 功能实现（用户故事、迭代）
- 🐛 Bug 修复和重构
- 📝 技术债务清理
- 📊 项目进度跟踪

**不推荐使用场景**：
- ❌ 简单的单个任务实现（直接实现即可）
- ❌ 不需要 PRD 的小型功能
- ❌ 不需要版本控制的修改

---

### Ralph YOLO 模式使用

**推荐使用场景**：
- ✅ 快速原型开发
- ✅ 不想安装 Amp 的用户
- ✅ 需要实时监控开发进度
- ✅ 消费版 Claude Code 用户（无 Amp）✨

**使用步骤**：

1. **生成 PRD**：
   ```
   /prd "添加用户认证功能"
   ```

2. **运行 Ralph**：
   ```
   /ralph tasks/prd-user-auth.md
   ```

3. **监控进度**：
   ```bash
   # 查看已完成的用户故事
   cat prd.json | jq '.userStories[] | {id, title, passes}'

   # 查看进度日志
   cat prd-progress.txt

   # 查看 git 提交历史
   git log --oneline -10
   ```

---

### Classic Ralph 模式使用

**使用场景**：
- 已有 Amp 环境的专业用户
- 需要完全隔离的开发环境

**使用步骤**：

1. **生成 PRD**：
   ```
   /prd "添加用户认证功能"
   ```

2. **运行 Ralph 脚本**：
   ```bash
   # 使用默认循环次数（10次）
   bash .claude/scripts/ralph.sh

   # 指定循环次数
   bash .claude/scripts/ralph.sh 20
   ```

---

## 质量标准

### PRD 质量标准
- ✅ 需求清晰：PRD 中的需求必须清晰、无歧义
- ✅ 用户故事完整：每个用户故事都必须包含 As a... I want... So that... 格式
- ✅ 验收标准可验证：每个验收标准都必须是可验证的
- ✅ 技术需求合理：技术需求必须合理、可实现

### 代码质量标准
- ✅ 代码可读性：代码必须易于阅读和维护
- ✅ 代码功能性：代码必须正确实现用户故事
- ✅ 代码测试性：代码必须可测试
- ✅ 代码性能：代码性能必须满足要求

---

## 与其他 skill 的协作

### ai-spec skill
- **关系**：Ralph 使用 ai-spec 将用户故事转换为技术规范
- **协作**：Ralph 生成 PRD，ai-spec 转换为技术规范

### code-debugger skill
- **关系**：Ralph 使用 code-debugger 进行代码调试和测试
- **协作**：Ralph 实现代码，code-debugger 进行调试

### deep-research skill
- **关系**：Ralph 生成 PRD，deep-research 进行背景调研
- **协作**：Ralph 生成 PRD，deep-research 进行技术背景调研

---

## 注意事项

### 限制
- **循环次数限制**：当前支持 10-50 次迭代（取决于 Ralph YOLO 模式或 Classic Ralph 模式）
- **上下文限制**：大型任务需要分解为小故事
- **依赖管理**：Classic Ralph 需要 Amp CLI、jq、Git

### 最佳实践
- **用户故事大小**：每个故事必须在一个迭代内完成（2-3 段对话）
- **依赖顺序**：故事按 `priority` 顺序执行，前面的故事不能依赖后面的
- **验收标准**：每个标准必须可验证
- **Git 状态**：始终从干净的 Git 状态开始 Ralph 运行

---

*本 skill 基于自主 AI Agent 循环系统设计，支持从 PRD 到代码实现的完整项目开发流程。版本 0.1.0*
