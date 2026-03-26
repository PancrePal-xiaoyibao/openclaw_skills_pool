# Hook Setup

Wire the reminder scripts into Codex or Claude Code when you want automatic nudges to capture and promote learnings.

## Paths

If you use this exact workspace installation, the scripts live at:

- `/mnt/500G-1/clawdata/workspace/skills/self-improving-ontology/scripts/activator.sh`
- `/mnt/500G-1/clawdata/workspace/skills/self-improving-ontology/scripts/error-detector.sh`

If you move the skill elsewhere, update the paths accordingly.

## Codex CLI

Create `.codex/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "/mnt/500G-1/clawdata/workspace/skills/self-improving-ontology/scripts/activator.sh"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "/mnt/500G-1/clawdata/workspace/skills/self-improving-ontology/scripts/error-detector.sh"
          }
        ]
      }
    ]
  }
}
```

## Claude Code

Create `.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "/mnt/500G-1/clawdata/workspace/skills/self-improving-ontology/scripts/activator.sh"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "/mnt/500G-1/clawdata/workspace/skills/self-improving-ontology/scripts/error-detector.sh"
          }
        ]
      }
    ]
  }
}
```

## Recommended First Run

Before enabling hooks broadly, initialize the workspace once:

```bash
python3 /mnt/500G-1/clawdata/workspace/skills/self-improving-ontology/scripts/sync_learning_to_ontology.py bootstrap
```

Then run a dry test:

```bash
ls /definitely-missing
```

The error detector should emit a short reminder rather than changing files.

## Permission Notes

- `activator.sh` and `error-detector.sh` only print reminders.
- `sync_learning_to_ontology.py bootstrap` creates files if they do not exist.
- `sync_learning_to_ontology.py promote` appends ontology operations to `memory/ontology/graph.jsonl`.
