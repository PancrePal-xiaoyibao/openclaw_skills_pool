# Skill Indexing

## Goal

Keep `workspace/skills/index.json` in sync whenever a skill is created, imported, edited, renamed, or deleted.

## Canonical Commands

Enter a skill task:

```bash
bash workspace/scripts/skill-task-bootstrap.sh "create-skill"
```

Rebuild once:

```bash
node workspace/scripts/rebuild-skills-index.js
```

Check drift:

```bash
node workspace/scripts/check-skills-index.js
```

Start auto-watch:

```bash
bash workspace/scripts/start-skills-index-watcher.sh
```

Stop auto-watch:

```bash
bash workspace/scripts/stop-skills-index-watcher.sh
```

Heartbeat guard:

```bash
bash workspace/scripts/skill-task-heartbeat.sh
```

Finish a skill task:

```bash
bash workspace/scripts/skill-task-finish.sh
```

## UX Rules

- Do not hand-edit `skills/index.json`.
- Any create, import, update, rename, or delete under `workspace/skills/` must flow through the indexer.
- At skill-task entry, run `skill-task-bootstrap.sh`.
- For long skill-editing sessions, keep the watcher running.
- During heartbeat, if a skill task session is active, run `skill-task-heartbeat.sh`.
- At task exit, run `skill-task-finish.sh`.
- Before ending a task that touched skills, run the drift checker.

## Indexed Fields

- `name`
- `path`
- `relative_path`
- `description`
- `tags`
- `last_updated`
- optional `version`
- optional `homepage`
