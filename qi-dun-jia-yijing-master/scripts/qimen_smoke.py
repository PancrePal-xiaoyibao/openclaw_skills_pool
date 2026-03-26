#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from qimen_core import analyze_chart, load_json, render_markdown



def main() -> int:
    schema_dir = Path(__file__).resolve().parent.parent / "schemas"
    required = ["## 【输入摘要】", "## 【五维落点】", "## 【运筹建议】", "【易理推导】"]
    for name in ["input-chart-driven.example.json", "input-auto-hour.example.json"]:
        payload = load_json(schema_dir / name)
        result = analyze_chart(payload)
        markdown = render_markdown(result)
        missing = [item for item in required if item not in markdown]
        if missing:
            print("QIMEN_SMOKE_FAIL")
            print(f"CASE={name}")
            print(f"MISSING={missing}")
            return 1
        print(f"QIMEN_SMOKE_CASE_OK={name}")
        print(f"BAND={result.band}")
        print(f"SUMMARY={result.summary}")
    print("QIMEN_SMOKE_OK")
    return 0



if __name__ == "__main__":
    raise SystemExit(main())
