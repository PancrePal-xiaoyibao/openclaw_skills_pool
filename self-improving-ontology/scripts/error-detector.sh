#!/bin/bash
# Detect obvious shell/tool failures and remind the agent to log them.

set -e

OUTPUT="${CLAUDE_TOOL_OUTPUT:-}"

ERROR_PATTERNS=(
    "error:"
    "Error:"
    "ERROR:"
    "failed"
    "FAILED"
    "command not found"
    "No such file"
    "Permission denied"
    "fatal:"
    "Exception"
    "Traceback"
    "npm ERR!"
    "ModuleNotFoundError"
    "SyntaxError"
    "TypeError"
    "exit code"
    "non-zero"
)

contains_error=false
for pattern in "${ERROR_PATTERNS[@]}"; do
    if [[ "$OUTPUT" == *"$pattern"* ]]; then
        contains_error=true
        break
    fi
done

if [ "$contains_error" = true ]; then
    cat << 'EOF'
<self-improving-ontology-error>
A command failure was detected.
If the failure is non-obvious, reusable, or likely to recur:
1. Append it to .learnings/ERRORS.md
2. Promote it later with
   python3 scripts/sync_learning_to_ontology.py promote --entry-id ERR-...
</self-improving-ontology-error>
EOF
fi
