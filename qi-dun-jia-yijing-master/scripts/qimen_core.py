#!/usr/bin/env python3
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from qimen_auto import build_auto_chart

SKILL_DIR = Path(__file__).resolve().parent.parent
REFERENCES_DIR = SKILL_DIR / "references"


class QimenProtocolError(ValueError):
    pass


@dataclass
class AnalysisResult:
    payload: dict[str, Any]
    summary: str
    band: str
    confidence: str
    five_dimensions: dict[str, str]
    reasoning: list[str]
    timing: dict[str, str]
    risk_flags: list[str]
    advice: list[str]
    target_relation: str
    pattern_hits: list[dict[str, Any]]
    auto_meta: dict[str, Any] | None


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_references() -> dict[str, Any]:
    return {
        "symbol_map": load_json(REFERENCES_DIR / "symbol-map.json"),
        "rule_priority": load_json(REFERENCES_DIR / "rule-priority.json"),
        "modern_scene_mapping": load_json(REFERENCES_DIR / "modern-scene-mapping.json"),
        "pattern_rules": load_json(REFERENCES_DIR / "pattern-rules.json"),
    }


def normalize_payload(payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any] | None]:
    mode = str(payload.get("mode", "chart-driven") or "chart-driven")
    if mode == "auto-hour":
        auto_result = build_auto_chart(payload)
        return auto_result.payload, auto_result.auto_meta
    return payload, payload.get("auto_meta")


def validate_payload(payload: dict[str, Any]) -> None:
    if not isinstance(payload, dict):
        raise QimenProtocolError("input payload must be a JSON object")
    for field in ["question", "question_type", "chart"]:
        if not payload.get(field):
            raise QimenProtocolError(f"missing required field: {field}")
    chart = payload.get("chart") or {}
    if not chart.get("season"):
        raise QimenProtocolError("missing required field: chart.season")
    use_deity = chart.get("use_deity") or {}
    if not use_deity.get("palace"):
        raise QimenProtocolError("missing required field: chart.use_deity.palace")
    palaces = chart.get("palaces")
    if not isinstance(palaces, list) or not palaces:
        raise QimenProtocolError("chart.palaces must be a non-empty list")


def palace_map(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    chart = payload["chart"]
    result: dict[str, dict[str, Any]] = {}
    for palace in chart["palaces"]:
        name = str(palace.get("name") or "").strip()
        if name:
            result[name] = palace
    return result


def get_palace(payload: dict[str, Any], palace_name: str) -> dict[str, Any]:
    mapping = palace_map(payload)
    if palace_name not in mapping:
        raise QimenProtocolError(f"palace not found in chart.palaces: {palace_name}")
    return mapping[palace_name]


def score_from_rank(rank: str) -> float:
    return {
        "旺": 1.2,
        "相": 0.7,
        "休": 0.1,
        "囚": -0.6,
        "死": -1.0,
    }.get(rank, 0.0)


def band_from_score(score: float) -> str:
    if score >= 2.2:
        return "favorable"
    if score >= 0.7:
        return "lean-favorable"
    if score > -0.7:
        return "mixed"
    return "guarded"


def band_summary(question_type: str, band: str) -> str:
    topic = {
        "career": "事业/合作推进",
        "relationship": "关系推进",
        "transaction": "交易执行",
        "competition": "竞争局势",
        "health": "健康处理",
        "travel": "出行安排",
        "legal": "法务/纠纷处理",
        "general": "当前事项",
    }.get(question_type, "当前事项")
    mapping = {
        "favorable": f"当前盘面对{topic}偏有利，适合主动推进。",
        "lean-favorable": f"当前盘面对{topic}略偏有利，可推进，但要控节奏。",
        "mixed": f"当前盘面对{topic}有反复，宜先观望后推进。",
        "guarded": f"当前盘面对{topic}偏不利，宜降速避险。",
    }
    return mapping[band]


def element_relation(use_element: str, target_element: str, refs: dict[str, Any]) -> str:
    if not use_element or not target_element:
        return ""
    relations = refs["symbol_map"]["element_relations"]
    generate = relations["generate"]
    control = relations["control"]
    if use_element == target_element:
        return "比和：主客同频，容易同行、僵持或互相牵制。"
    if generate.get(use_element) == target_element:
        return "我生彼：我方更耗力，对方较易得益。"
    if generate.get(target_element) == use_element:
        return "彼生我：对方或环境能对我方形成支持。"
    if control.get(use_element) == target_element:
        return "我克彼：我方对对手或对象有制约力。"
    if control.get(target_element) == use_element:
        return "彼克我：对方或环境对我方形成压制。"
    return "主客五行关系不显。"


def compute_strength(element: str, season: str, refs: dict[str, Any], empty: bool) -> tuple[str, float]:
    ranks = refs["symbol_map"]["season_strength"].get(season, {})
    rank = ranks.get(element, "休")
    score = score_from_rank(rank)
    if empty:
        score -= 1.0
    return rank, score


def compute_base_score(payload: dict[str, Any], palace: dict[str, Any], refs: dict[str, Any]) -> tuple[float, list[str], str]:
    question_type = payload["question_type"]
    season = payload["chart"]["season"]
    priorities = refs["rule_priority"]["question_preferences"].get(
        question_type,
        refs["rule_priority"]["question_preferences"]["general"],
    )
    door = palace.get("door", "")
    star = palace.get("star", "")
    god = palace.get("god", "")
    element = palace.get("element", "")
    empty = bool(palace.get("empty", False))

    seasonal_rank, seasonal_score = compute_strength(element, season, refs, empty)
    score = seasonal_score
    reasons = [f"{element} 在 {season} 属 {seasonal_rank}"]

    if door in priorities.get("favorable_doors", []):
        score += 1.0
        reasons.append(f"{door} 对 {question_type} 属正向门")
    elif door in priorities.get("unfavorable_doors", []):
        score -= 1.0
        reasons.append(f"{door} 对 {question_type} 属风险门")
    else:
        reasons.append(f"{door} 对 {question_type} 为中性门")

    if star in priorities.get("favorable_stars", []):
        score += 0.6
        reasons.append(f"{star} 为此题型加分星")
    elif star in priorities.get("unfavorable_stars", []):
        score -= 0.6
        reasons.append(f"{star} 为此题型减分星")

    if god in priorities.get("favorable_gods", []):
        score += 0.4
        reasons.append(f"{god} 为助力神")
    elif god in priorities.get("unfavorable_gods", []):
        score -= 0.4
        reasons.append(f"{god} 为牵制神")

    if empty:
        reasons.append("宫位落空，主延后或暂不落实")

    return score, reasons, seasonal_rank


def rule_matches(match: dict[str, Any], palace: dict[str, Any]) -> bool:
    for key, value in match.items():
        if key.endswith("_in"):
            field = key[:-3]
            if palace.get(field) not in value:
                return False
            continue
        if palace.get(key) != value:
            return False
    return True


def apply_pattern_rules(palace: dict[str, Any], refs: dict[str, Any]) -> tuple[float, list[str], list[dict[str, Any]]]:
    score = 0.0
    reasons: list[str] = []
    hits: list[dict[str, Any]] = []
    for rule in refs["pattern_rules"]["rules"]:
        if not rule_matches(rule.get("match", {}), palace):
            continue
        score += float(rule.get("score", 0.0))
        reasons.append(f"{rule['label']}：{rule['reason']}")
        hits.append(
            {
                "id": rule["id"],
                "label": rule["label"],
                "category": rule.get("category", ""),
                "score": rule.get("score", 0.0),
                "reason": rule["reason"],
            }
        )
    return score, reasons, hits


def build_five_dimensions(payload: dict[str, Any], palace: dict[str, Any], refs: dict[str, Any], seasonal_rank: str, band: str) -> dict[str, str]:
    symbol_map = refs["symbol_map"]
    scene_map = refs["modern_scene_mapping"]
    qtype = payload["question_type"]
    palace_meta = symbol_map["palaces"].get(palace.get("name", ""), {})
    door_meta = symbol_map["doors"].get(palace.get("door", ""), {})
    star_meta = symbol_map["stars"].get(palace.get("star", ""), {})
    god_meta = symbol_map["gods"].get(palace.get("god", ""), {})
    scene_meta = scene_map.get(qtype, scene_map["general"])

    use_text = {
        "favorable": "主推动、主打开局面",
        "lean-favorable": "主可推进，但需控速与控边界",
        "mixed": "主反复与观望，宜先试探再推进",
        "guarded": "主受制、主拖延或主风险上浮",
    }[band]

    return {
        "性": f"{palace.get('name', '')}宫之{palace_meta.get('nature', '根性未明')}，在本题里主{scene_meta.get('axis', '当前事项主轴')}",
        "情": f"{palace.get('door', '')}主{door_meta.get('emotion', '状态未明')}；{palace.get('god', '')}主{god_meta.get('motivation', '潜意未明')}",
        "形": f"{palace.get('star', '')}显{star_meta.get('form', '外观未明')}；{palace_meta.get('image', '场域轮廓未明')}",
        "体": f"在{qtype}问题里，此宫更像{scene_meta.get('body', '当前事体载体')}，并落在{palace_meta.get('scene', '当前场域')}",
        "用": f"{use_text}；当前旺衰为{seasonal_rank}",
        "时空坐标": f"季节={payload['chart']['season']}；宫位={palace.get('name', '')}；问题场域={palace_meta.get('scene', '当前场域')}",
    }


def build_timing(palace: dict[str, Any], band: str, seasonal_rank: str) -> dict[str, str]:
    empty = bool(palace.get("empty", False))
    if empty:
        return {
            "pace": "慢",
            "trigger": "待出空、补实或条件补齐后再动",
            "basis": "用神宫落空，主结果不宜视为已实落。",
        }
    if band == "favorable" and seasonal_rank in {"旺", "相"}:
        return {
            "pace": "快",
            "trigger": "近期内容易有明确回应或动作",
            "basis": f"用神得{seasonal_rank}气且综合倾向偏正。",
        }
    if band in {"lean-favorable", "mixed"}:
        return {
            "pace": "中",
            "trigger": "需先出现试探、沟通或条件调整，再见推进",
            "basis": "盘面可动，但不宜把第一次反馈视为最终落地。",
        }
    return {
        "pace": "慢",
        "trigger": "短期宜稳守，待时令或局面改观后再动",
        "basis": "当前门星神与旺衰共同压制节奏。",
    }


def build_risk_flags(palace: dict[str, Any], band: str, target_relation: str, pattern_hits: list[dict[str, Any]]) -> list[str]:
    flags: list[str] = []
    if palace.get("empty"):
        flags.append("用神落空：事情容易延后、落差感强，先做准备动作。")
    if band == "guarded":
        flags.append("综合倾向偏弱：当前局面不适合硬推。")
    if palace.get("door") in {"死门", "伤门", "惊门"}:
        flags.append(f"{palace.get('door')} 入局：行动方式若过激，容易放大成本与冲突。")
    if palace.get("god") in {"白虎", "玄武", "腾蛇"}:
        flags.append(f"{palace.get('god')} 入局：需防硬伤、隐瞒、误判或反复。")
    if target_relation.startswith("彼克我"):
        flags.append("主客关系偏受压：对方或环境当前更占势。")
    if target_relation.startswith("我生彼"):
        flags.append("我方耗力偏大：推进过程中容易自己先付出。")
    for hit in pattern_hits:
        if float(hit.get("score", 0.0)) < 0:
            flags.append(f"{hit['label']}：{hit['reason']}")
    return flags or ["当前无硬性凶信，但仍需按盘面节奏推进。"]


def build_advice(payload: dict[str, Any], palace: dict[str, Any], band: str, timing: dict[str, str], target_relation: str, refs: dict[str, Any], pattern_hits: list[dict[str, Any]]) -> list[str]:
    scene_meta = refs["modern_scene_mapping"].get(payload["question_type"], refs["modern_scene_mapping"]["general"])
    focus = scene_meta.get("advice_focus", "主轴动作")
    advice: list[str] = []
    if band == "favorable":
        advice.append(f"主线可推进，优先围绕{focus}落地。")
        advice.append("先抓用神所在宫位代表的核心场域，再扩张外围动作。")
    elif band == "lean-favorable":
        advice.append(f"可以推进，但先做小步试探，围绕{focus}逐步放量。")
        advice.append("先确认对方或环境是否给出真实回应，再做下一步承诺。")
    elif band == "mixed":
        advice.append(f"先观望后推进，把动作拆小，重点观察{focus}是否出现转强信号。")
        advice.append("优先做低成本验证，不宜一口气把筹码压满。")
    else:
        advice.append(f"当前不宜硬推，先做风险隔离，再处理{focus}。")
        advice.append("若必须动作，采用降速、分段、留后手的策略。")

    if palace.get("empty"):
        advice.append("涉及空亡，先做准备与铺垫，不要把短期静默误判成彻底失败。")
    if target_relation.startswith("彼克我"):
        advice.append("对手或环境压制较明显，先换位、借势或等待窗口，不宜正面硬抗。")
    if target_relation.startswith("我生彼"):
        advice.append("当前我方投入容易偏大，需先设置边界和止损线。")
    if timing["pace"] == "快":
        advice.append("节奏较快时，重在决断，不在反复犹豫。")
    elif timing["pace"] == "慢":
        advice.append("节奏偏慢时，重在守节奏与蓄势，不在抢快。")
    for hit in pattern_hits:
        if float(hit.get("score", 0.0)) > 0.7:
            advice.append(f"{hit['label']} 已成主格，可围绕“{hit['reason']}”来安排动作。")
    return advice


def analyze_chart(payload: dict[str, Any]) -> AnalysisResult:
    normalized_payload, auto_meta = normalize_payload(payload)
    validate_payload(normalized_payload)
    refs = load_references()
    chart = normalized_payload["chart"]
    use_info = chart.get("use_deity") or {}
    use_palace = get_palace(normalized_payload, use_info["palace"])

    score, reasons, seasonal_rank = compute_base_score(normalized_payload, use_palace, refs)
    pattern_score, pattern_reasons, pattern_hits = apply_pattern_rules(use_palace, refs)
    score += pattern_score
    reasons.extend(pattern_reasons)

    target_relation = ""
    target_info = chart.get("counterparty") or {}
    if target_info.get("palace"):
        try:
            target_palace = get_palace(normalized_payload, target_info["palace"])
        except QimenProtocolError:
            target_palace = None
        if target_palace:
            target_relation = element_relation(use_palace.get("element", ""), target_palace.get("element", ""), refs)
            reasons.append(f"主客关系：{target_relation}")

    band = band_from_score(score)
    summary = band_summary(normalized_payload["question_type"], band)
    confidence = "high" if len(chart.get("palaces", [])) >= 8 else "medium" if len(chart.get("palaces", [])) >= 3 else "low"
    five_dimensions = build_five_dimensions(normalized_payload, use_palace, refs, seasonal_rank, band)
    timing = build_timing(use_palace, band, seasonal_rank)
    risk_flags = build_risk_flags(use_palace, band, target_relation, pattern_hits)
    advice = build_advice(normalized_payload, use_palace, band, timing, target_relation, refs, pattern_hits)

    reasoning = [
        f"用神取 {use_info.get('label', '用神')}，落 {use_palace.get('name', '')} 宫。",
        "；".join(reasons),
        f"综合分数={score:.2f}，判为 {band}。",
    ]
    return AnalysisResult(
        payload=normalized_payload,
        summary=summary,
        band=band,
        confidence=confidence,
        five_dimensions=five_dimensions,
        reasoning=reasoning,
        timing=timing,
        risk_flags=risk_flags,
        advice=advice,
        target_relation=target_relation,
        pattern_hits=pattern_hits,
        auto_meta=auto_meta,
    )


def result_to_dict(result: AnalysisResult) -> dict[str, Any]:
    payload = result.payload
    chart = payload["chart"]
    use_info = chart.get("use_deity") or {}
    target_info = chart.get("counterparty") or {}
    return {
        "input_summary": {
            "question": payload.get("question", ""),
            "question_type": payload.get("question_type", "general"),
            "analysis_focus": payload.get("analysis_focus", ""),
            "season": chart.get("season", ""),
            "time_note": chart.get("time_note", ""),
            "mode": payload.get("mode", "chart-driven"),
        },
        "auto_meta": result.auto_meta,
        "use_deity": use_info,
        "target": target_info,
        "summary": result.summary,
        "band": result.band,
        "confidence": result.confidence,
        "five_dimensions": result.five_dimensions,
        "timing": result.timing,
        "risk_flags": result.risk_flags,
        "advice": result.advice,
        "reasoning": result.reasoning,
        "target_relation": result.target_relation,
        "pattern_hits": result.pattern_hits,
    }


def render_markdown(result: AnalysisResult) -> str:
    payload = result.payload
    chart = payload["chart"]
    use_info = chart.get("use_deity") or {}
    use_palace = get_palace(payload, use_info["palace"])
    target_info = chart.get("counterparty") or {}
    door = use_palace.get("door", "")
    star = use_palace.get("star", "")
    god = use_palace.get("god", "")

    lines = [
        "## 【输入摘要】",
        f"- 问题：{payload.get('question', '')}",
        f"- 题型：{payload.get('question_type', '')}",
        f"- 模式：{payload.get('mode', 'chart-driven')}",
        f"- 分析焦点：{payload.get('analysis_focus', '') or '未额外指定'}",
        "",
        "## 【盘面摘要】",
        f"- 遁局：{chart.get('dun', 'unknown')} / {chart.get('ju', 'unknown')}局 / 季节={chart.get('season', '')}",
        f"- 时点：{chart.get('time_note', '') or '未提供'} | 节气：{chart.get('solar_term', '') or '未提供'} | 旬空：{chart.get('xunkong', '') or '未提供'} | 驿马：{chart.get('horse', '') or '未提供'}",
    ]
    if chart.get("gan_zhi"):
        gz = chart["gan_zhi"]
        lines.append(f"- 干支：{gz.get('year', '')}年 {gz.get('month', '')}月 {gz.get('day', '')}日 {gz.get('hour', '')}时")
    lines.append(f"- 用神宫：{use_palace.get('name', '')} | 门星神：{door} / {star} / {god}")
    if target_info.get("palace"):
        lines.append(f"- 对方/外部对象：{target_info.get('label', '对方')} -> {target_info.get('palace', '')}宫")
    lines.extend([
        "",
        "## 【用神确认】",
        f"- 用神：{use_info.get('label', '用神')} -> {use_palace.get('name', '')}宫",
        f"- 五行：{use_palace.get('element', '')} | 宫位：{use_palace.get('trigram', '')}",
    ])
    if result.target_relation:
        lines.append(f"- 主客关系：{result.target_relation}")
    lines.extend([
        f"> 【易理推导】：据 {use_palace.get('name', '')}宫 + {door} + {star} + {god} + 季节旺衰主线取用。",
        "",
        "## 【局势总论】",
        f"- {result.summary}",
        f"> 【易理推导】：{result.reasoning[1]}",
        "",
    ])
    if result.pattern_hits:
        lines.append("## 【格局与奇仪组合】")
        for hit in result.pattern_hits:
            lines.append(f"- {hit['label']}：{hit['reason']} (score={hit['score']})")
        lines.append("")
    lines.append("## 【五维落点】")
    for key in ["性", "情", "形", "体", "用", "时空坐标"]:
        lines.append(f"- {key}：{result.five_dimensions[key]}")
    lines.extend([
        "",
        "## 【应期与节奏】",
        f"- 节奏：{result.timing['pace']}",
        f"- 触发条件：{result.timing['trigger']}",
        f"> 【易理推导】：{result.timing['basis']}",
        "",
        "## 【风险点】",
    ])
    for item in result.risk_flags:
        lines.append(f"- {item}")
    lines.extend([
        "",
        "## 【运筹建议】",
    ])
    for item in result.advice:
        lines.append(f"- {item}")
    lines.extend([
        "",
        "## 【置信度】",
        f"- 置信度：{result.confidence}",
        f"- 结果 band：{result.band}",
    ])
    return "\n".join(lines).rstrip() + "\n"
