---
name: qi-dun-jia-yijing-master
description: 奇门遁甲易学宗师 - 协议化奇门 skill package，包含可测试的盘面输入协议、规则分析骨架、取象 reference 联络与 benchmark 回归工具。
version: 0.2.0
---

# 奇门遁甲 - 奇门遁甲易学宗师

这是一个**协议化的奇门遁甲 skill package**，用于在 Claw bot / OpenClaw 体系内测试和迭代奇门能力。

它不再只是单一 `SKILL.md`，而是一个完整目录：

- `SKILL.md`：协议层，定义输入、执行顺序、输出合同、能力边界
- `scripts/`：最小可运行的 deterministic 内核（盘面驱动分析、bench、smoke）
- `references/`：古籍逻辑、门星神宫位映射、现代场景映射、规则优先级
- `schemas/`：输入样例与字段说明
- `cases/`：benchmark case 与回归输出

当前版本的能力边界很明确：

- 已支持：**chart-driven** 奇门分析
  - 也就是你先提供结构化盘面，skill 负责用规则引擎 + reference 联络库生成分析与建议
- 未完全实现：**从公历时间自动精确排出全盘** 的完整数学引擎
  - 这部分可以作为下一阶段继续补

换句话说，本 skill 已经可以用于：

1. 协议测试
2. prompt/skill 回归
3. 参考逻辑回归
4. 输出结构与一致性 bench

但还不应伪装成“已经完整重建整套古法自动排盘软件”。

---

## 包结构

```text
qi-dun-jia-yijing-master/
  SKILL.md
  scripts/
    qimen_calendar.py
    qimen_auto.py
    qimen_core.py
    qimen_protocol.py
    qimen_bench.py
    qimen_smoke.py
  references/
    classical-principles.md
    five-dimension-playbook.md
    pattern-rules.json
    modern-scene-mapping.json
    rule-priority.json
    symbol-map.json
  schemas/
    README.md
    input-chart-driven.example.json
    input-auto-hour.example.json
  cases/
    README.md
    benchmark_cases.json
    teacher_goldens.json
    output/
```

---

## 核心协议

### 一、能力分层

本 skill 按三层执行：

#### 1. 确定性层

必须脚本化，不能靠灵感：

- 盘面字段校验
- 用神落宫读取
- 宫 / 门 / 星 / 神 / 奇仪 / 旬空 / 马星等结构化读取
- 季节对五行旺相休囚死的映射
- 问题类型对应的规则优先级选择

#### 2. 规则层

优先脚本化，允许继续增强：

- 取用神后的主线分析顺序
- 问题类型下的门星神权重
- 吉凶/推进/延迟/风险的带权判断
- 应期快慢和节奏判断
- 建议生成的模板化约束

#### 3. 定象层

依赖 reference 联络，而不是死记硬背：

- 宫位/卦宫的本性
- 八门的行为方式
- 九星的资质与外显
- 八神的潜意识与隐性动机
- 现代问题场景中的实体映射
- 输出时必须落到 `性 → 情 → 形 → 体 → 用 + 时空坐标`

---

### 二、取象总则

强制参考：

- `workspace/doc/2026-03-21-玄学skill取象参考整合手册.md`
- `workspace/doc/2026-03-20-八卦性情形体用学习手册.md`
- `references/classical-principles.md`
- `references/five-dimension-playbook.md`

核心要求：

- 宫、门、星、神不能各说各话，必须统一成一条 `性→情→形→体→用` 推导链。
- 结论不能只说“利/不利”，必须交代：
  - 何宫
  - 何门
  - 何星
  - 何神
  - 何季节旺衰
  - 何问题场景
- 每个正式结论后尽量补：

```markdown
### 五维落点
- 性：[根本气质/局中主轴]
- 情：[当前行为与心理状态]
- 形：[外在表征/盘面结构]
- 体：[当前场域中的具体人/事/地]
- 用：[在此局中的实际作用]
- 时空坐标：[何时 + 何宫/何方位/何场域]
```

---

## 输入协议

### 执行模式

当前支持：

- `chart-driven`
- `auto-hour`

其中：

- `chart-driven`：调用方提供结构化盘面
- `auto-hour`：调用方提供公历时间，本 skill 自动排出 hour chart 再进行断法

### 输入 JSON 结构

```json
{
  "question": "这次合作谈判能否顺利推进？",
  "question_type": "career",
  "subject_role": "self",
  "target_role": "counterparty",
  "analysis_focus": "合作推进与应期",
  "chart": {
    "method": "manual-chart",
    "dun": "yang",
    "ju": 3,
    "season": "autumn",
    "time_note": "2026-03-21 申时",
    "xunkong": "子丑",
    "horse": "寅",
    "use_deity": {
      "label": "求测人",
      "palace": "乾"
    },
    "counterparty": {
      "label": "对方",
      "palace": "坤"
    },
    "palaces": [
      {
        "name": "乾",
        "trigram": "乾",
        "element": "metal",
        "door": "开门",
        "star": "天心",
        "god": "六合",
        "heaven_stem": "乙",
        "earth_stem": "辛",
        "empty": false,
        "horse": false,
        "notes": ""
      }
    ]
  }
}
```

### auto-hour 输入 JSON 结构

```json
{
  "mode": "auto-hour",
  "question": "这次合作谈判能否顺利推进？",
  "question_type": "career",
  "calendar": {
    "year": 2026,
    "month": 3,
    "day": 21,
    "hour": 15,
    "minute": 0
  },
  "auto_chart": {
    "method": "chaibu",
    "use_deity_strategy": "day_stem_sky",
    "target_strategy": "custom",
    "target_palace": "坤"
  }
}
```

### 必填字段

- `question`
- `question_type`
- `chart-driven` 时：`chart.season`、`chart.use_deity.palace`、`chart.palaces[]`
- `auto-hour` 时：`calendar.year/month/day/hour`

### question_type 建议值

- `career`
- `relationship`
- `transaction`
- `competition`
- `health`
- `travel`
- `legal`
- `general`

---

## 执行顺序

### 阶段 1：输入校验

由 `scripts/qimen_protocol.py` 和 `scripts/qimen_core.py` 完成：

1. 校验输入结构是否完整
2. 校验用神落宫是否存在于盘面
3. 校验季节、问题类型是否在支持列表内
4. 若缺字段，返回结构化错误，而不是硬断

### 阶段 1.5：自动排局（auto-hour 模式）

由 `scripts/qimen_calendar.py` + `scripts/qimen_auto.py` 完成：

1. 用本地 vendored `lunar_python` 计算：
   - 年月日时干支
   - 当前节气
   - 旬空
2. 按固定 hour-chart 规则计算：
   - 阴遁/阳遁
   - 局数
   - 值符 / 值使
   - 地盘 / 天盘 / 八门 / 九星 / 八神
3. 按 `use_deity_strategy` 选出默认用神落宫
4. 生成标准化 `chart`，再进入统一分析主线

### 阶段 2：盘面主线分析

主线固定为：

1. 读取用神落宫
2. 读取该宫之：
   - 宫位
   - 五行
   - 八门
   - 九星
   - 八神
   - 天盘/地盘奇仪
   - 空亡与马星信息
3. 按问题类型加载 `references/rule-priority.json`
4. 计算：
   - 宫位本性
   - 门的行为倾向
   - 星的外显资质
   - 神的隐性动机
   - 季节旺衰
   - 格局/奇仪组合命中
   - 综合倾向分数

### 阶段 3：五维取象重写

把结构化结果重写成：

- 性：宫位根性 + 五行 + 问题主轴
- 情：八门行为 + 八神状态
- 形：九星外显 + 宫位场域轮廓
- 体：当前问题中的具体人/事/地点/对象
- 用：在当前问题里的推进/阻碍/掩护/延迟/转机作用
- 时空坐标：季节 + 问题阶段 + 宫位场域

### 阶段 4：结论与建议

输出：

- 局势总论
- 用神确认
- 五维落点
- 时间节奏判断
- 风险点
- 运筹建议
- 置信度

---

## 输出协议

### JSON 输出

字段最少包括：

- `input_summary`
- `use_deity`
- `target`
- `five_dimensions`
- `timing`
- `risk_flags`
- `advice`
- `confidence`
- `reasoning`

### Markdown 输出

严格推荐按以下结构：

```markdown
## 【输入摘要】
## 【盘面摘要】
## 【用神确认】
## 【局势总论】
## 【五维落点】
## 【应期与节奏】
## 【风险点】
## 【运筹建议】
## 【置信度】
```

每个结论尽量跟一段：

> 【易理推导】：据 [宫位] 宫 + [门] + [星] + [神] + [旺衰] 所得

---

## 脚本说明

### `scripts/qimen_core.py`

核心库：

- 统一处理 `chart-driven` / `auto-hour`
- 加载 references
- 校验输入
- 读取用神宫
- 匹配格局/奇仪组合规则
- 计算旺衰与问题倾向分数
- 生成五维结构化结果
- 渲染 markdown

### `scripts/qimen_calendar.py`

历法库适配层：

- vendored `lunar_python` 导入
- 干支、节气、旬空、节气时间表快照

### `scripts/qimen_auto.py`

自动排局层：

- hour-chart 自动排盘
- 地盘 / 天盘 / 八门 / 九星 / 八神展开
- 自动模式下的用神默认落宫生成

### `scripts/qimen_protocol.py`

协议执行入口：

```bash
python3 workspace/skills/qi-dun-jia-yijing-master/scripts/qimen_protocol.py   --input workspace/skills/qi-dun-jia-yijing-master/schemas/input-chart-driven.example.json   --format markdown
```

### `scripts/qimen_bench.py`

回归 bench：

```bash
python3 workspace/skills/qi-dun-jia-yijing-master/scripts/qimen_bench.py   --cases workspace/skills/qi-dun-jia-yijing-master/cases/benchmark_cases.json   --output-dir workspace/skills/qi-dun-jia-yijing-master/cases/output
```

### `scripts/qimen_smoke.py`

最小 smoke：

```bash
python3 workspace/skills/qi-dun-jia-yijing-master/scripts/qimen_smoke.py
```

---

## Benchmark 协议

benchmark 的目标不是验证“玄学真伪”，而是验证：

- skill 是否按固定结构输出
- 是否给出五维取象链
- 是否对不同问题类型使用不同规则优先级
- 是否能保持稳定的易理依据表达
- 修改 skill 后有没有明显逻辑回退
- 自动排局模式给出的干支/节气/旬空/门星神是否稳定
- 与人工整理的金标准要点是否大体一致

### case 格式

见：

- `cases/benchmark_cases.json`

每个 case 包含：

- `id`
- `description`
- `input`
- `expected_substrings`
- `forbidden_substrings`
- `expected_band`

金标准文件：

- `cases/teacher_goldens.json`

### 打分方式

当前是轻量 rubric：

- expected 命中加分
- forbidden 未出现加分
- band 命中加分
- 最终输出 `PASS / REVIEW / FAIL`

---

## Reference 目录说明

### `references/classical-principles.md`

记录：

- 奇门断法主线
- 什么是可程序化规则
- 什么是必须 reference 化的定象层

### `references/five-dimension-playbook.md`

记录：

- 如何把宫门星神重写为 `性→情→形→体→用`
- 如何强制带出时空坐标

### `references/symbol-map.json`

机器可读：

- 宫位、八门、九星、八神、季节旺衰的结构化映射

### `references/rule-priority.json`

机器可读：

- 不同问题类型下，门/星/神/旺衰的权重与优先级

### `references/modern-scene-mapping.json`

机器可读：

- career / relationship / competition / legal 等现代问题中的实体映射

---

## 能力边界

当前版本**不声称**完整支持：

- 全量古籍格局自动演算
- 多流派盘法差异自动切换
- 大规模案例统计学习

当前版本**明确支持**：

- 把奇门 skill 变成一个可测试、可回归、可继续增强的 package
- 让 Claw bot 能基于结构化盘面或自动 hour chart 做稳定分析
- 让 skill 测试不再只靠主观印象，而能有 benchmark 回归线

---

## 下一阶段建议

若要继续提升到更高精度，推荐按顺序补：

1. 自动排盘数学引擎
2. 更细的格局与奇仪组合规则
3. 多流派 reference 权重差异
4. 案例校正层与金标准样本
5. 更细的应期规则

---

## 最终原则

- 排局与主断法尽量规则化
- 定象尽量 reference 化
- 输出尽量结构化
- bench 尽量可重复化

只有这样，奇门 skill 才适合在 Claw bot 里长期测试，而不是每次都靠“老师感”临场发挥。
