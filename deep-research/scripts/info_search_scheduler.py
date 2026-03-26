#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


UTC = timezone.utc
SCRIPT_PATH = Path(__file__).resolve()
WORKSPACE_DIR = SCRIPT_PATH.parents[3]
DEFAULT_STATE_NAME = "info-search-router-state.json"

DOMAIN_KEYWORDS: dict[str, tuple[str, ...]] = {
    "medical": (
        "hospital",
        "medical",
        "medicine",
        "clinical",
        "patient",
        "guideline",
        "cancer",
        "oncology",
        "drug",
        "trial",
        "医院",
        "医疗",
        "医学",
        "临床",
        "患者",
        "诊疗",
        "指南",
        "癌",
        "胰腺",
        "肿瘤",
        "药",
        "试验",
    ),
    "finance": (
        "market",
        "stock",
        "equity",
        "earnings",
        "option",
        "trading",
        "macro",
        "price",
        "市场",
        "股票",
        "财报",
        "期权",
        "交易",
        "行情",
        "宏观",
        "利率",
        "做空",
        "做多",
        "美股",
        "港股",
        "a股",
    ),
    "geopolitical": (
        "war",
        "military",
        "conflict",
        "sanction",
        "diplomacy",
        "iran",
        "israel",
        "policy",
        "地缘",
        "冲突",
        "战争",
        "制裁",
        "外交",
        "军事",
        "政策",
    ),
}

PRIMARY_KEYWORDS = (
    "official",
    "primary-source",
    "primary source",
    "regulatory",
    "guideline",
    "一手",
    "官方",
    "原始",
    "监管",
    "指南",
    "政策文件",
)

SECONDARY_KEYWORDS = (
    "secondary",
    "commentary",
    "market commentary",
    "媒体",
    "解读",
    "评论",
    "分析",
    "二手",
)

BACKENDS: dict[str, dict[str, Any]] = {
    "finance-mcp": {
        "id": "finance-mcp",
        "label": "FinanceMCP",
        "family": "finance-mcp",
        "type": "mcp",
        "server": "finance-mcp-local",
        "tool": "stock_data",
        "why": "task-local market/fundamental data lane; avoid web-search quota when the task is finance-heavy",
        "example": (
            'mcp_call(action="call", server="finance-mcp-local", tool="stock_data", '
            'arguments={"code":"<symbol>","market_type":"cn|us|hk"})'
        ),
        "status": "stable",
    },
    "pubmed": {
        "id": "pubmed",
        "label": "PubMed MCP",
        "family": "pubmed",
        "type": "mcp",
        "server": "mcp-pubmed-llm-server",
        "tool": "pubmed_quick_search",
        "why": "highest-signal primary literature lane for medical and life-science tasks",
        "example": (
            'mcp_call(action="call", server="mcp-pubmed-llm-server", tool="pubmed_quick_search", '
            'arguments={"query":"<query>","max_results":5})'
        ),
        "status": "stable",
    },
    "openalex": {
        "id": "openalex",
        "label": "OpenAlex MCP",
        "family": "openalex",
        "type": "mcp",
        "server": "openalex-mcp-server",
        "tool": "openalex_search",
        "why": "stable cross-disciplinary paper lane; good for academic and policy evidence expansion",
        "example": (
            'mcp_call(action="call", server="openalex-mcp-server", tool="openalex_search", '
            'arguments={"query":"<query>","max_results":5})'
        ),
        "status": "stable",
    },
    "zhipu": {
        "id": "zhipu",
        "label": "Zhipu Web Search MCP",
        "family": "zhipu",
        "type": "mcp",
        "server": "zhipu-web-search-sse",
        "tool": "web_search",
        "why": "best current Chinese/general web MCP lane; alias `web_search` is normalized to the working Zhipu tool",
        "example": (
            'mcp_call(action="call", server="zhipu-web-search-sse", tool="web_search", '
            'arguments={"search_query":"<query>","count":5})'
        ),
        "status": "stable",
    },
    "metaso": {
        "id": "metaso",
        "label": "Metaso MCP",
        "family": "metaso",
        "type": "mcp",
        "server": "metaso-search-mcp",
        "tool": "metaso_search",
        "why": "Chinese web fallback only; keep behind Zhipu because upstream redirect failures are still observed",
        "example": (
            'mcp_call(action="call", server="metaso-search-mcp", tool="metaso_search", '
            'arguments={"q":"<query>","scope":"web","size":5})'
        ),
        "status": "degraded",
    },
    "brave": {
        "id": "brave",
        "label": "Brave Search",
        "family": "brave",
        "type": "native",
        "tool": "web_search",
        "why": "last-resort general web lane only; repeated 429/quota failures should cool down the whole Brave family",
        "example": 'web_search(query="<query>", count=5)',
        "status": "quota-sensitive",
    },
}

ROUTES: dict[tuple[str, str], list[str]] = {
    ("medical", "primary"): ["pubmed", "openalex", "zhipu", "metaso", "brave"],
    ("medical", "secondary"): ["openalex", "pubmed", "zhipu", "metaso", "brave"],
    ("finance", "primary"): ["finance-mcp", "zhipu", "metaso", "brave"],
    ("finance", "secondary"): ["zhipu", "finance-mcp", "metaso", "brave"],
    ("geopolitical", "primary"): ["zhipu", "metaso", "brave"],
    ("geopolitical", "secondary"): ["zhipu", "metaso", "brave"],
    ("general", "primary"): ["zhipu", "openalex", "metaso", "brave"],
    ("general", "secondary"): ["zhipu", "metaso", "brave"],
}

COOLDOWN_SECONDS: dict[str, int] = {
    "ok": 0,
    "success": 0,
    "rate_limit": 1800,
    "quota": 1800,
    "transport_error": 900,
    "redirect_error": 900,
    "error": 600,
}


def utc_now() -> datetime:
    return datetime.now(UTC)


def iso_now() -> str:
    return utc_now().replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    normalized = ts.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(normalized).astimezone(UTC)
    except ValueError:
        return None


def relative_to_workspace(path: Path) -> str:
    try:
        return str(path.relative_to(WORKSPACE_DIR))
    except ValueError:
        return str(path)


def load_task_capsule(task_dir: Path) -> dict[str, str]:
    capsule_json = task_dir / "capsules" / "task-capsule.json"
    if capsule_json.exists():
        try:
            payload = json.loads(capsule_json.read_text(encoding="utf-8"))
            return {
                "objective": str(payload.get("objective") or "").strip(),
                "scope": str(payload.get("scope") or "").strip(),
                "deliverable": str(payload.get("deliverable") or "").strip(),
            }
        except json.JSONDecodeError:
            pass
    capsule_md = task_dir / "capsules" / "task-capsule.md"
    fields = {"objective": "", "scope": "", "deliverable": ""}
    if capsule_md.exists():
        for line in capsule_md.read_text(encoding="utf-8").splitlines():
            for key in fields:
                marker = f"- {key.capitalize()}:"
                if line.startswith(marker):
                    fields[key] = line.split(":", 1)[1].strip()
    return fields


def detect_domain(text: str) -> str:
    lowered = text.lower()
    scores = {domain: 0 for domain in DOMAIN_KEYWORDS}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in lowered:
                scores[domain] += 1
    best_domain = max(scores, key=scores.get)
    return best_domain if scores[best_domain] > 0 else "general"


def detect_collector_mode(text: str) -> str:
    lowered = text.lower()
    primary_hits = sum(1 for keyword in PRIMARY_KEYWORDS if keyword.lower() in lowered)
    secondary_hits = sum(1 for keyword in SECONDARY_KEYWORDS if keyword.lower() in lowered)
    if primary_hits > secondary_hits:
        return "primary"
    if secondary_hits > 0:
        return "secondary"
    return "secondary"


def default_state_path(task_dir: Path) -> Path:
    return task_dir / "scratch" / DEFAULT_STATE_NAME


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"updated_at_utc": None, "backends": {}}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"updated_at_utc": None, "backends": {}}
    if not isinstance(payload, dict):
        return {"updated_at_utc": None, "backends": {}}
    payload.setdefault("updated_at_utc", None)
    payload.setdefault("backends", {})
    return payload


def save_state(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload["updated_at_utc"] = iso_now()
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def backend_state_entry(state: dict[str, Any], family: str) -> dict[str, Any]:
    backends = state.setdefault("backends", {})
    entry = backends.setdefault(family, {"status": "unknown", "failures": 0})
    return entry


def is_backend_cooling(state: dict[str, Any], family: str, now: datetime | None = None) -> tuple[bool, str | None]:
    now = now or utc_now()
    entry = state.get("backends", {}).get(family, {})
    cooldown_until = parse_iso(entry.get("cooldown_until_utc"))
    if cooldown_until and cooldown_until > now:
        return True, cooldown_until.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return False, None


def build_plan(task_dir: Path, agent_name: str, role: str = "", mission: str = "", state_path: Path | None = None) -> dict[str, Any]:
    state_path = state_path or default_state_path(task_dir)
    capsule = load_task_capsule(task_dir)
    context_text = "\n".join(
        [
            capsule.get("objective", ""),
            capsule.get("scope", ""),
            role,
            mission,
            agent_name,
        ]
    )
    domain = detect_domain(context_text)
    collector_mode = detect_collector_mode("\n".join([role, mission, agent_name]))
    route = ROUTES.get((domain, collector_mode), ROUTES[("general", "secondary")])
    state = load_state(state_path)

    active: list[dict[str, Any]] = []
    cooling: list[dict[str, Any]] = []
    for backend_id in route:
        backend = BACKENDS[backend_id].copy()
        backend["probe"] = (
            f'mcp_call(action="list_tools", server="{backend["server"]}")'
            if backend["type"] == "mcp"
            else 'No MCP probe; native tool is already known.'
        )
        cooling_now, cooldown_until = is_backend_cooling(state, backend["family"])
        if cooling_now:
            cooling.append(
                {
                    "id": backend_id,
                    "label": backend["label"],
                    "family": backend["family"],
                    "cooldown_until_utc": cooldown_until,
                    "last_status": state.get("backends", {}).get(backend["family"], {}).get("status"),
                    "last_reason": state.get("backends", {}).get(backend["family"], {}).get("reason"),
                }
            )
            continue
        active.append(backend)

    return {
        "task_dir": str(task_dir),
        "agent_name": agent_name,
        "role": role,
        "mission": mission,
        "domain": domain,
        "collector_mode": collector_mode,
        "state_path": str(state_path),
        "generated_at_utc": iso_now(),
        "active_backends": active,
        "cooling_backends": cooling,
        "rules": [
            "Run MCP-first for info collectors; do not open with Brave unless every higher lane is exhausted.",
            "For any unfamiliar MCP server, call mcp_call(action=list_tools, server=...) before the first real call.",
            "If Brave returns 429, quota, or rate-limit text once, cool down the whole Brave family and move on instead of retrying in loops.",
            "Treat redirect loops, repeated 400s, and transport failures as backend failures; record them once and switch lanes.",
        ],
    }


def record_backend_status(
    task_dir: Path,
    backend_id: str,
    status: str,
    reason: str = "",
    *,
    state_path: Path | None = None,
    cooldown_seconds: int | None = None,
) -> dict[str, Any]:
    state_path = state_path or default_state_path(task_dir)
    state = load_state(state_path)
    if backend_id not in BACKENDS:
        raise ValueError(f"Unknown backend id: {backend_id}")
    family = BACKENDS[backend_id]["family"]
    entry = backend_state_entry(state, family)
    if cooldown_seconds is None:
        cooldown_seconds = COOLDOWN_SECONDS.get(status, COOLDOWN_SECONDS["error"])
    entry["status"] = status
    entry["reason"] = reason
    entry["updated_at_utc"] = iso_now()
    if status in {"ok", "success"}:
        entry["failures"] = 0
        entry.pop("cooldown_until_utc", None)
    else:
        entry["failures"] = int(entry.get("failures", 0) or 0) + 1
        if cooldown_seconds > 0:
            until = utc_now() + timedelta(seconds=cooldown_seconds)
            entry["cooldown_until_utc"] = until.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    save_state(state_path, state)
    return {
        "ok": True,
        "backend": backend_id,
        "family": family,
        "status": status,
        "state_path": str(state_path),
        "cooldown_until_utc": entry.get("cooldown_until_utc"),
        "reason": reason,
    }


def render_markdown(plan: dict[str, Any], title: str = "## Search Scheduling") -> str:
    lines = [
        title,
        "",
        f'- Detected domain: `{plan["domain"]}`',
        f'- Collector mode: `{plan["collector_mode"]}`',
        f'- Task-local scheduler state: `{relative_to_workspace(Path(plan["state_path"]))}`',
        "",
        "### Runtime rules",
        "",
    ]
    lines.extend([f"- {rule}" for rule in plan["rules"]])
    lines.extend(["", "### Recommended backend order", ""])
    if plan["active_backends"]:
        for index, backend in enumerate(plan["active_backends"], start=1):
            lines.extend(
                [
                    f"{index}. `{backend['label']}`",
                    f"   - route: `{backend['type']}`",
                    f"   - why: {backend['why']}",
                    f"   - first probe: `{backend['probe']}`",
                    f"   - first call example: `{backend['example']}`",
                    f"   - current status: `{backend['status']}`",
                ]
            )
    else:
        lines.append("- No backend is currently available; wait for the earliest cooldown or shift to already-landed task-local sources.")
    if plan["cooling_backends"]:
        lines.extend(["", "### Cooling backends", ""])
        for backend in plan["cooling_backends"]:
            reason = backend.get("last_reason") or backend.get("last_status") or "previous failure"
            lines.append(
                f'- `{backend["label"]}` cooling until `{backend["cooldown_until_utc"]}` because of `{reason}`'
            )
    lines.extend(
        [
            "",
            "### Failure recording",
            "",
            "- Record one backend failure, then switch lanes. Example:",
            "",
            "```bash",
            (
                "python3 workspace/skills/deep-research/scripts/info_search_scheduler.py "
                f'record --task-dir "{plan["task_dir"]}" --backend brave --status rate_limit '
                '--reason "Brave 429 quota"'
            ),
            "```",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def build_brief_section(task_dir: Path, agent_name: str, role: str, mission: str) -> list[str]:
    plan = build_plan(task_dir=task_dir, agent_name=agent_name, role=role, mission=mission)
    return render_markdown(plan).strip().splitlines()


def cmd_plan(args: argparse.Namespace) -> int:
    task_dir = Path(args.task_dir).resolve()
    state_path = Path(args.state_path).resolve() if args.state_path else default_state_path(task_dir)
    plan = build_plan(
        task_dir=task_dir,
        agent_name=args.agent_name,
        role=args.role or "",
        mission=args.mission or "",
        state_path=state_path,
    )
    rendered = json.dumps(plan, ensure_ascii=False, indent=2) + "\n"
    if args.format == "markdown":
        rendered = render_markdown(plan)
    if args.write:
        target = Path(args.write).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


def cmd_record(args: argparse.Namespace) -> int:
    task_dir = Path(args.task_dir).resolve()
    state_path = Path(args.state_path).resolve() if args.state_path else None
    result = record_backend_status(
        task_dir=task_dir,
        backend_id=args.backend,
        status=args.status,
        reason=args.reason or "",
        state_path=state_path,
        cooldown_seconds=args.cooldown_seconds,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Minimal MCP-first scheduler for deep-research info collectors")
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan = subparsers.add_parser("plan")
    plan.add_argument("--task-dir", required=True)
    plan.add_argument("--agent-name", required=True)
    plan.add_argument("--role")
    plan.add_argument("--mission")
    plan.add_argument("--state-path")
    plan.add_argument("--format", choices=["json", "markdown"], default="markdown")
    plan.add_argument("--write")
    plan.set_defaults(func=cmd_plan)

    record = subparsers.add_parser("record")
    record.add_argument("--task-dir", required=True)
    record.add_argument("--backend", required=True, choices=sorted(BACKENDS.keys()))
    record.add_argument("--status", required=True)
    record.add_argument("--reason")
    record.add_argument("--cooldown-seconds", type=int)
    record.add_argument("--state-path")
    record.set_defaults(func=cmd_record)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
