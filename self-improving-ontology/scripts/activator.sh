#!/bin/bash
# Lightweight reminder for capture-first, promote-second memory workflow.

set -e

cat << 'EOF'
<self-improving-ontology-reminder>
Before you finish, check whether new knowledge should be captured:
- unexpected error or workaround?
- user correction?
- recurring best practice?
- missing capability?

If yes: append it to .learnings/.
If the pattern is stable or reusable: promote it with
python3 scripts/sync_learning_to_ontology.py promote --entry-id ...
</self-improving-ontology-reminder>
EOF
