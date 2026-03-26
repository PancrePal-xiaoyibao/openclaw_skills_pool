---
name: self-improving-ontology
description: "Continuous self-improvement plus ontology-backed memory for coding agents. Use when Codex should capture failures, user corrections, feature requests, external tool issues, or recurring best practices in `.learnings/`, then promote stable knowledge into a typed graph under `memory/ontology/` for querying, linking, validation, and cross-skill shared state. Trigger on requests like 'remember this', 'log this error', 'record this learning', 'promote this to ontology', 'what do we know about X', 'link X to Y', 'show dependencies', or whenever a skill needs durable structured memory."
---

# Self Improving Ontology

Combine two memory layers:

- `.learnings/` for fast, append-only capture of failures, corrections, best practices, and feature requests.
- `memory/ontology/` for structured, queryable, cross-skill memory backed by a typed graph.

Use this skill when raw experience should not stay trapped in session text. Capture quickly first, then promote stable knowledge into ontology entities only after it is worth reusing.

## Decision Flow

| Situation | Action |
|-----------|--------|
| A command failed, the user corrected you, or a missing capability was exposed | Append an entry to `.learnings/ERRORS.md`, `.learnings/LEARNINGS.md`, or `.learnings/FEATURE_REQUESTS.md` |
| A captured entry is now stable, reusable, or should be visible to other skills | Run `python3 scripts/sync_learning_to_ontology.py promote --entry-id ...` |
| You need entity CRUD, graph traversal, relation management, or validation | Use `python3 scripts/ontology.py ...` directly |
| You want automatic reminders after prompts or failed shell commands | Wire `scripts/activator.sh` and `scripts/error-detector.sh`; see `references/hooks-setup.md` |
| A recurring learning has become reusable workflow knowledge | Run `scripts/extract-skill.sh <skill-name>` to scaffold a new skill |

## Bootstrap the Workspace

Start with:

```bash
python3 scripts/sync_learning_to_ontology.py bootstrap
```

This command:

- creates `.learnings/LEARNINGS.md`, `.learnings/ERRORS.md`, and `.learnings/FEATURE_REQUESTS.md` if they do not exist,
- ensures `memory/ontology/graph.jsonl` exists,
- appends a default schema fragment for `LearningRecord`, `OperationalError`, `FeatureRequest`, and `logged_in` / `derived_from` relations.

It does not overwrite existing log files or ontology data.

## Capture First, Promote Second

### 1. Capture raw experience

Use the templates in `assets/`:

- `assets/LEARNINGS.md`
- `assets/ERRORS.md`
- `assets/FEATURE_REQUESTS.md`

Keep entries append-only. Prefer logging a rough but accurate entry immediately over waiting for a perfect summary.

For detailed examples, read `references/examples.md`.

### 2. Promote stable knowledge into ontology

```bash
python3 scripts/sync_learning_to_ontology.py promote --entry-id LRN-20260325-001
python3 scripts/sync_learning_to_ontology.py promote --entry-id ERR-20260325-001
python3 scripts/sync_learning_to_ontology.py promote --entry-id FEAT-20260325-001 --relate-to proj_001 --relation derived_from
```

Promotion does the following:

- finds the entry in `.learnings/`,
- creates or updates a typed ontology entity,
- ensures a `Document` entity exists for the source markdown file,
- links the promoted record to its source file with `logged_in`,
- optionally links it to an existing ontology entity via `--relate-to`.

Use promotion only for entries that should survive beyond the immediate debugging context.

## Query and Validate the Graph

Use the ontology CLI directly once entities exist:

```bash
python3 scripts/ontology.py list --type LearningRecord
python3 scripts/ontology.py get --id lrn_lrn_20260325_001
python3 scripts/ontology.py related --id lrn_lrn_20260325_001 --rel logged_in
python3 scripts/ontology.py query --type FeatureRequest --where '{"status":"pending"}'
python3 scripts/ontology.py validate
```

Rules:

- Prefer append/merge operations; do not overwrite ontology history.
- Keep `graph.jsonl` and `schema.yaml` inside the current workspace.
- Use the schema/query references before inventing new relation names or entity layouts.

## Resources

### scripts/

- `scripts/sync_learning_to_ontology.py` bridges `.learnings/` entries into ontology entities.
- `scripts/ontology.py` provides graph create/query/update/relate/validate commands.
- `scripts/activator.sh` emits a lightweight reminder after prompt submission.
- `scripts/error-detector.sh` emits a reminder when shell/tool output looks like an error.
- `scripts/extract-skill.sh` scaffolds a new skill from a recurring learning.

### references/

- `references/schema.md` documents ontology entity and relation patterns.
- `references/queries.md` shows query and traversal examples.
- `references/hooks-setup.md` shows how to wire reminders into Codex or Claude Code.
- `references/examples.md` contains concrete `.learnings/` entries.
- `references/upstream.md` records the exact upstream sources merged into this skill.

### assets/

- `assets/LEARNINGS.md`, `assets/ERRORS.md`, and `assets/FEATURE_REQUESTS.md` are starter templates.
- `assets/SKILL-TEMPLATE.md` is the extraction template used by the skill scaffolder.

## Upstream

This skill merges:

- `https://github.com/peterskoett/self-improving-agent`
- `https://wry-manatee-359.convex.site/api/v1/download?slug=ontology`

The local glue code in `scripts/sync_learning_to_ontology.py` is the integration layer that connects the two.
