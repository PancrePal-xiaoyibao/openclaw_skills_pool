#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

resolve_python() {
  if [ -n "${OPENCLAW_RUNTIME_PYTHON:-}" ] && [ -x "${OPENCLAW_RUNTIME_PYTHON}" ]; then
    printf '%s\n' "${OPENCLAW_RUNTIME_PYTHON}"
    return
  fi
  if [ -x /opt/conda/bin/python ]; then
    printf '%s\n' "/opt/conda/bin/python"
    return
  fi
  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return
  fi
  if command -v python >/dev/null 2>&1; then
    command -v python
    return
  fi
  echo "No suitable Python runtime found for fetch_feishu.py" >&2
  exit 127
}

PYTHON_BIN="$(resolve_python)"
exec "${PYTHON_BIN}" "${SCRIPT_DIR}/fetch_feishu.py" "$@"
