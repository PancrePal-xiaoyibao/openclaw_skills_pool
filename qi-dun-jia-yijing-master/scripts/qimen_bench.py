#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from qimen_core import analyze_chart, load_json, render_markdown, result_to_dict, write_json



def score_case(markdown: str, result_band: str, case: dict[str, Any]) -> dict[str, Any]:
    expected = case.get("expected_substrings", [])
    forbidden = case.get("forbidden_substrings", [])
    expected_hits = [item for item in expected if item in markdown]
    forbidden_hits = [item for item in forbidden if item in markdown]
    band_match = result_band == case.get("expected_band")
    total = len(expected) + len(forbidden) + 1
    achieved = len(expected_hits) + (len(forbidden) - len(forbidden_hits)) + (1 if band_match else 0)
    ratio = achieved / total if total else 1.0
    if not forbidden_hits and len(expected_hits) == len(expected) and band_match:
        status = "PASS"
    elif not forbidden_hits and ratio >= 0.6:
        status = "REVIEW"
    else:
        status = "FAIL"
    return {
        "status": status,
        "ratio": round(ratio, 4),
        "expected_hits": expected_hits,
        "forbidden_hits": forbidden_hits,
        "band_match": band_match,
    }


def score_teacher_golden(markdown: str, result_band: str, teacher_golden: dict[str, Any] | None) -> dict[str, Any]:
    if not teacher_golden:
        return {"golden_hits": [], "golden_band_match": None, "golden_ratio": None}
    golden_points = teacher_golden.get("golden_points", [])
    hits = [item for item in golden_points if item in markdown]
    total = len(golden_points) + 1
    band_match = result_band == teacher_golden.get("teacher_band")
    ratio = (len(hits) + (1 if band_match else 0)) / total if total else 1.0
    return {
        "golden_hits": hits,
        "golden_band_match": band_match,
        "golden_ratio": round(ratio, 4),
    }



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run qimen benchmark cases")
    parser.add_argument("--cases", required=True, type=Path)
    parser.add_argument("--teacher-goldens", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    return parser



def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    cases = load_json(args.cases.resolve())
    teacher_goldens_path = args.teacher_goldens
    if teacher_goldens_path is None:
        candidate = args.cases.resolve().parent / "teacher_goldens.json"
        teacher_goldens_path = candidate if candidate.exists() else None
    teacher_goldens = {}
    if teacher_goldens_path and teacher_goldens_path.exists():
        teacher_goldens = {item["id"]: item for item in load_json(teacher_goldens_path)}
    args.output_dir.mkdir(parents=True, exist_ok=True)

    summary_rows = []
    for case in cases:
        result = analyze_chart(case["input"])
        markdown = render_markdown(result)
        case_file = args.output_dir / f"{case['id']}.md"
        case_file.write_text(markdown, encoding="utf-8")
        score = score_case(markdown, result.band, case)
        golden_score = score_teacher_golden(markdown, result.band, teacher_goldens.get(case["id"]))
        row = {
            "id": case["id"],
            "description": case.get("description", ""),
            "band": result.band,
            **score,
            **golden_score,
        }
        summary_rows.append(row)
        write_json(args.output_dir / f"{case['id']}.json", result_to_dict(result))

    summary_json = {"case_count": len(summary_rows), "rows": summary_rows}
    write_json(args.output_dir / "summary.json", summary_json)

    lines = ["# Qimen Bench Summary", ""]
    for row in summary_rows:
        lines.append(f"- `{row['id']}` | status={row['status']} | band={row['band']} | ratio={row['ratio']}")
        lines.append(f"  - description: {row['description']}")
        lines.append(f"  - expected_hits: {row['expected_hits']}")
        lines.append(f"  - forbidden_hits: {row['forbidden_hits']}")
        lines.append(f"  - band_match: {row['band_match']}")
        if row["golden_ratio"] is not None:
            lines.append(f"  - golden_hits: {row['golden_hits']}")
            lines.append(f"  - golden_band_match: {row['golden_band_match']}")
            lines.append(f"  - golden_ratio: {row['golden_ratio']}")
    (args.output_dir / "summary.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    failures = [row for row in summary_rows if row["status"] == "FAIL"]
    print("QIMEN_BENCH_DONE")
    print(f"CASE_COUNT={len(summary_rows)}")
    print(f"FAIL_COUNT={len(failures)}")
    print(f"SUMMARY_JSON={args.output_dir / 'summary.json'}")
    print(f"SUMMARY_MD={args.output_dir / 'summary.md'}")
    return 1 if failures else 0



if __name__ == "__main__":
    raise SystemExit(main())
