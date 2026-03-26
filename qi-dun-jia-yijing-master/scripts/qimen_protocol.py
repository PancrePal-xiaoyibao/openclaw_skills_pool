#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from qimen_core import QimenProtocolError, analyze_chart, load_json, render_markdown, result_to_dict



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run chart-driven qimen protocol analysis")
    parser.add_argument("--input", required=True, type=Path, help="Path to structured qimen input JSON")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    parser.add_argument("--output", type=Path, help="Optional output path")
    return parser



def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        payload = load_json(args.input.resolve())
        result = analyze_chart(payload)
    except (QimenProtocolError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"QIMEN_PROTOCOL_FAIL: {exc}")
        return 1

    if args.format == "json":
        body = json.dumps(result_to_dict(result), ensure_ascii=False, indent=2) + "\n"
    else:
        body = render_markdown(result)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(body, encoding="utf-8")
    else:
        print(body, end="")
    return 0



if __name__ == "__main__":
    raise SystemExit(main())
