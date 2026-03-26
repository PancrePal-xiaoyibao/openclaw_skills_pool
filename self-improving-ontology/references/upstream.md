# Upstream Sources

This skill was assembled on 2026-03-25 from two upstream sources.

## 1. self-improving-agent

- Source: `https://github.com/peterskoett/self-improving-agent`
- Retrieved commit: `383ec57da7c917488cf6f26c4493826fb84463f6`
- Reused parts:
  - core capture workflow in `SKILL.md`
  - `scripts/activator.sh`
  - `scripts/error-detector.sh`
  - `scripts/extract-skill.sh`
  - `.learnings` examples and template assets

## 2. ontology

- Source: `https://wry-manatee-359.convex.site/api/v1/download?slug=ontology`
- Retrieved package: `ontology-1.0.4.zip`
- Reused parts:
  - `scripts/ontology.py`
  - `references/schema.md`
  - `references/queries.md`
  - ontology storage and validation model

## Local Integration Layer

The following file is local glue code added during integration:

- `scripts/sync_learning_to_ontology.py`

It connects the append-only `.learnings/` workflow to ontology entities and relations.
