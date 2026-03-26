#!/usr/bin/env python3
"""
Bridge self-improvement markdown logs into ontology graph memory.

Commands:
    python3 sync_learning_to_ontology.py bootstrap
    python3 sync_learning_to_ontology.py promote --entry-id LRN-20260325-001
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from ontology import (
    append_schema,
    create_entity,
    create_relation,
    get_entity,
    load_graph,
    resolve_safe_path,
    update_entity,
)

DEFAULT_LEARNINGS_DIR = ".learnings"
DEFAULT_GRAPH_PATH = "memory/ontology/graph.jsonl"
DEFAULT_SCHEMA_PATH = "memory/ontology/schema.yaml"
SKILL_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = SKILL_ROOT / "assets"

ENTRY_RE = re.compile(
    r"^## \[(?P<entry_id>[^\]]+)\]\s*(?P<label>[^\n]+)\n(?P<body>.*?)(?=^## \[|\Z)",
    re.MULTILINE | re.DOTALL,
)
FIELD_RE = re.compile(r"^\*\*(?P<name>[^*]+)\*\*:\s*(?P<value>.+)$", re.MULTILINE)
SECTION_RE = re.compile(
    r"^### (?P<name>[^\n]+)\n(?P<body>.*?)(?=^### |\Z)",
    re.MULTILINE | re.DOTALL,
)
METADATA_ITEM_RE = re.compile(r"^- (?P<key>[^:]+):\s*(?P<value>.+)$", re.MULTILINE)

DEFAULT_SCHEMA_FRAGMENT = {
    "types": {
        "Document": {
            "required": ["title"],
        },
        "Project": {
            "required": ["name"],
            "status_enum": ["planning", "active", "paused", "completed", "archived"],
        },
        "Task": {
            "required": ["title", "status"],
            "status_enum": ["open", "in_progress", "blocked", "done", "cancelled"],
            "priority_enum": ["low", "medium", "high", "urgent"],
        },
        "Note": {
            "required": ["content"],
        },
        "LearningRecord": {
            "required": ["entry_id", "category", "summary", "status"],
            "status_enum": [
                "pending",
                "in_progress",
                "resolved",
                "wont_fix",
                "promoted",
                "promoted_to_skill",
            ],
            "priority_enum": ["low", "medium", "high", "critical"],
        },
        "OperationalError": {
            "required": ["entry_id", "summary", "status"],
            "status_enum": [
                "pending",
                "in_progress",
                "resolved",
                "wont_fix",
                "promoted",
                "promoted_to_skill",
            ],
            "priority_enum": ["low", "medium", "high", "critical"],
        },
        "FeatureRequest": {
            "required": ["entry_id", "capability", "status"],
            "status_enum": [
                "pending",
                "in_progress",
                "resolved",
                "wont_fix",
                "promoted",
                "promoted_to_skill",
            ],
            "priority_enum": ["low", "medium", "high", "critical"],
            "complexity_enum": ["simple", "medium", "complex"],
        },
    },
    "relations": {
        "logged_in": {
            "from_types": ["LearningRecord", "OperationalError", "FeatureRequest"],
            "to_types": ["Document"],
            "cardinality": "many_to_one",
        },
        "derived_from": {
            "from_types": ["LearningRecord", "OperationalError", "FeatureRequest"],
            "to_types": ["Project", "Task", "Document", "Note"],
            "cardinality": "many_to_many",
        },
    },
}

TEMPLATE_FILES = {
    "LEARNINGS.md": ASSETS_DIR / "LEARNINGS.md",
    "ERRORS.md": ASSETS_DIR / "ERRORS.md",
    "FEATURE_REQUESTS.md": ASSETS_DIR / "FEATURE_REQUESTS.md",
}


def normalize_key(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def parse_listish(value: str) -> list[str]:
    if not value:
        return []
    parts = [item.strip() for item in value.split(",")]
    return [item for item in parts if item]


def stable_id(prefix: str, value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return f"{prefix}_{slug}"


def document_id(path: Path) -> str:
    digest = hashlib.sha1(str(path).encode("utf-8")).hexdigest()[:12]
    return f"doc_{digest}"


def ensure_template(target: Path, source: Path) -> bool:
    if target.exists():
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source.read_text())
    return True


def relation_exists(graph_path: str, from_id: str, rel_type: str, to_id: str) -> bool:
    _, relations = load_graph(graph_path)
    return any(
        rel["from"] == from_id and rel["rel"] == rel_type and rel["to"] == to_id
        for rel in relations
    )


def ensure_entity(entity_id: str, entity_type: str, properties: dict[str, Any], graph_path: str) -> tuple[dict[str, Any], str]:
    existing = get_entity(entity_id, graph_path)
    if existing:
        if existing["type"] != entity_type:
            raise SystemExit(
                f"Entity '{entity_id}' already exists with type '{existing['type']}', expected '{entity_type}'"
            )
        update_entity(entity_id, properties, graph_path)
        return get_entity(entity_id, graph_path), "updated"

    return create_entity(entity_type, properties, graph_path, entity_id), "created"


def bootstrap_workspace(learnings_dir: Path, graph_path: Path, schema_path: Path) -> dict[str, Any]:
    created: list[str] = []

    learnings_dir.mkdir(parents=True, exist_ok=True)
    for filename, source in TEMPLATE_FILES.items():
        target = learnings_dir / filename
        if ensure_template(target, source):
            created.append(str(target))

    graph_path.parent.mkdir(parents=True, exist_ok=True)
    if not graph_path.exists():
        graph_path.touch()
        created.append(str(graph_path))

    schema_path.parent.mkdir(parents=True, exist_ok=True)
    append_schema(str(schema_path), DEFAULT_SCHEMA_FRAGMENT)

    return {
        "learnings_dir": str(learnings_dir),
        "graph": str(graph_path),
        "schema": str(schema_path),
        "created": created,
    }


def locate_entry_file(entry_id: str, learnings_dir: Path, explicit_file: Path | None = None) -> Path:
    if explicit_file is not None:
        return explicit_file

    prefix = entry_id.split("-", 1)[0].upper()
    if prefix == "LRN":
        candidate = learnings_dir / "LEARNINGS.md"
    elif prefix == "ERR":
        candidate = learnings_dir / "ERRORS.md"
    elif prefix == "FEAT":
        candidate = learnings_dir / "FEATURE_REQUESTS.md"
    else:
        candidate = None

    if candidate is not None and candidate.exists():
        return candidate

    for fallback in TEMPLATE_FILES:
        path = learnings_dir / fallback
        if path.exists():
            text = path.read_text()
            if f"[{entry_id}]" in text:
                return path

    raise SystemExit(f"Could not find a source file for entry '{entry_id}'")


def parse_entry(source_file: Path, entry_id: str) -> dict[str, Any]:
    text = source_file.read_text()
    for match in ENTRY_RE.finditer(text):
        if match.group("entry_id") != entry_id:
            continue

        body = match.group("body").strip()
        body = re.sub(r"\n---\s*$", "", body).strip()
        heading = match.group("label").strip()

        section_start = body.find("\n### ")
        if section_start == -1:
            field_text = body
            section_text = ""
        else:
            field_text = body[:section_start]
            section_text = body[section_start + 1 :]

        fields = {
            normalize_key(found.group("name")): found.group("value").strip()
            for found in FIELD_RE.finditer(field_text)
        }

        sections = {}
        for found in SECTION_RE.finditer(section_text):
            sections[found.group("name").strip()] = found.group("body").strip()

        metadata_text = sections.get("Metadata", "")
        metadata = {
            normalize_key(found.group("key")): found.group("value").strip()
            for found in METADATA_ITEM_RE.finditer(metadata_text)
        }

        kind = infer_kind(entry_id, source_file)
        return {
            "kind": kind,
            "entry_id": entry_id,
            "heading": heading,
            "fields": fields,
            "sections": sections,
            "metadata": metadata,
            "source_file": source_file,
        }

    raise SystemExit(f"Entry '{entry_id}' was not found in '{source_file}'")


def infer_kind(entry_id: str, source_file: Path) -> str:
    prefix = entry_id.split("-", 1)[0].upper()
    if prefix == "LRN" or source_file.name == "LEARNINGS.md":
        return "learning"
    if prefix == "ERR" or source_file.name == "ERRORS.md":
        return "error"
    if prefix == "FEAT" or source_file.name == "FEATURE_REQUESTS.md":
        return "feature"
    raise SystemExit(f"Could not infer entry kind for '{entry_id}'")


def promote_properties(entry: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
    fields = entry["fields"]
    sections = entry["sections"]
    metadata = entry["metadata"]
    base = {
        "entry_id": entry["entry_id"],
        "status": fields.get("status", "pending").lower(),
        "priority": fields.get("priority", "medium").lower(),
        "area": fields.get("area", ""),
        "logged": fields.get("logged", ""),
        "source_file": str(entry["source_file"]),
        "tags": parse_listish(metadata.get("tags", "")),
        "related_files": parse_listish(metadata.get("related_files", "")),
        "metadata": metadata,
    }

    if entry["kind"] == "learning":
        return (
            stable_id("lrn", entry["entry_id"]),
            "LearningRecord",
            {
                **base,
                "category": entry["heading"],
                "summary": sections.get("Summary", entry["heading"]),
                "details": sections.get("Details", ""),
                "suggested_action": sections.get("Suggested Action", ""),
                "resolution": sections.get("Resolution", ""),
            },
        )

    if entry["kind"] == "error":
        return (
            stable_id("err", entry["entry_id"]),
            "OperationalError",
            {
                **base,
                "summary": sections.get("Summary", entry["heading"]),
                "error_key": entry["heading"],
                "error_text": sections.get("Error", ""),
                "context": sections.get("Context", ""),
                "suggested_fix": sections.get("Suggested Fix", ""),
                "reproducible": metadata.get("reproducible", "unknown"),
                "resolution": sections.get("Resolution", ""),
            },
        )

    return (
        stable_id("feat", entry["entry_id"]),
        "FeatureRequest",
        {
            **base,
            "capability": sections.get("Requested Capability", entry["heading"]),
            "summary": entry["heading"],
            "user_context": sections.get("User Context", ""),
            "complexity": sections.get("Complexity Estimate", "").lower(),
            "suggested_implementation": sections.get("Suggested Implementation", ""),
        },
    )


def promote_entry(
    entry_id: str,
    learnings_dir: Path,
    graph_path: Path,
    schema_path: Path,
    explicit_file: Path | None = None,
    relate_to: str | None = None,
    relation: str = "derived_from",
) -> dict[str, Any]:
    bootstrap_workspace(learnings_dir, graph_path, schema_path)

    source_file = locate_entry_file(entry_id, learnings_dir, explicit_file)
    entry = parse_entry(source_file, entry_id)
    record_id, record_type, properties = promote_properties(entry)

    record, record_action = ensure_entity(record_id, record_type, properties, str(graph_path))

    doc_id = document_id(source_file)
    document_props = {
        "title": source_file.name,
        "path": str(source_file),
        "summary": f"Self-improvement source log for {source_file.name}",
    }
    document, document_action = ensure_entity(doc_id, "Document", document_props, str(graph_path))

    relation_action = "exists"
    if not relation_exists(str(graph_path), record["id"], "logged_in", document["id"]):
        create_relation(record["id"], "logged_in", document["id"], {}, str(graph_path))
        relation_action = "created"

    linked_action = None
    if relate_to:
        if not relation_exists(str(graph_path), record["id"], relation, relate_to):
            create_relation(record["id"], relation, relate_to, {}, str(graph_path))
            linked_action = "created"
        else:
            linked_action = "exists"

    return {
        "record_id": record["id"],
        "record_type": record_type,
        "record_action": record_action,
        "document_id": document["id"],
        "document_action": document_action,
        "logged_in_relation": relation_action,
        "linked_entity": relate_to,
        "linked_relation": relation if relate_to else None,
        "linked_relation_action": linked_action,
        "source_file": str(source_file),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Promote learnings into ontology")
    subparsers = parser.add_subparsers(dest="command", required=True)

    bootstrap_p = subparsers.add_parser("bootstrap", help="Initialize learnings and ontology files")
    bootstrap_p.add_argument("--learnings-dir", default=DEFAULT_LEARNINGS_DIR)
    bootstrap_p.add_argument("--graph", default=DEFAULT_GRAPH_PATH)
    bootstrap_p.add_argument("--schema", default=DEFAULT_SCHEMA_PATH)

    promote_p = subparsers.add_parser("promote", help="Promote a learning entry into ontology")
    promote_p.add_argument("--entry-id", required=True, help="Learning/error/feature entry ID")
    promote_p.add_argument("--file", help="Specific source markdown file")
    promote_p.add_argument("--learnings-dir", default=DEFAULT_LEARNINGS_DIR)
    promote_p.add_argument("--graph", default=DEFAULT_GRAPH_PATH)
    promote_p.add_argument("--schema", default=DEFAULT_SCHEMA_PATH)
    promote_p.add_argument("--relate-to", help="Optional existing ontology entity ID to link to")
    promote_p.add_argument("--relation", default="derived_from", help="Relation name used with --relate-to")

    args = parser.parse_args()
    workspace_root = Path.cwd().resolve()

    learnings_dir = resolve_safe_path(
        args.learnings_dir,
        root=workspace_root,
        label="learnings dir",
    )
    graph_path = resolve_safe_path(args.graph, root=workspace_root, label="graph path")
    schema_path = resolve_safe_path(args.schema, root=workspace_root, label="schema path")

    if args.command == "bootstrap":
        result = bootstrap_workspace(learnings_dir, graph_path, schema_path)
        print(json.dumps(result, indent=2))
        return

    explicit_file = None
    if args.file:
        explicit_file = resolve_safe_path(
            args.file,
            root=workspace_root,
            must_exist=True,
            label="entry file",
        )

    result = promote_entry(
        args.entry_id,
        learnings_dir,
        graph_path,
        schema_path,
        explicit_file=explicit_file,
        relate_to=args.relate_to,
        relation=args.relation,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
