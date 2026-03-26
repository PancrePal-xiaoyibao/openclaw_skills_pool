# Query Reference

Query patterns and graph traversal examples.

## Basic Queries

### Get by ID

```bash
python3 scripts/ontology.py get --id task_001
```

### List by Type

```bash
python3 scripts/ontology.py list --type Task
python3 scripts/ontology.py list --type Person
python3 scripts/ontology.py list --type LearningRecord
```

### Filter by Properties

```bash
python3 scripts/ontology.py query --type Task --where '{"status":"open"}'
python3 scripts/ontology.py query --type Task --where '{"priority":"high"}'
python3 scripts/ontology.py query --type FeatureRequest --where '{"status":"pending"}'
```

## Relation Queries

### Get Related Entities

```bash
python3 scripts/ontology.py related --id proj_001 --rel has_task
python3 scripts/ontology.py related --id task_001 --rel part_of --dir incoming
python3 scripts/ontology.py related --id lrn_lrn_20260325_001 --rel logged_in
python3 scripts/ontology.py related --id p_001 --dir both
```

### Common Patterns

```bash
python3 scripts/ontology.py related --id proj_001 --rel has_owner
python3 scripts/ontology.py related --id p_001 --rel assigned_to --dir incoming
python3 scripts/ontology.py related --id err_err_20260325_001 --rel derived_from
```

## Programmatic Queries

### Python API

```python
from scripts.ontology import load_graph, query_entities, get_related

entities, relations = load_graph("memory/ontology/graph.jsonl")
open_tasks = query_entities("Task", {"status": "open"}, "memory/ontology/graph.jsonl")
project_tasks = get_related("proj_001", "has_task", "memory/ontology/graph.jsonl")
```

### Complex Queries

```python
def find_promoted_errors(graph_path):
    from scripts.ontology import query_entities

    return query_entities(
        "OperationalError",
        {"status": "promoted"},
        graph_path,
    )
```

### Path Queries

```python
from scripts.ontology import load_graph

def find_path(from_id, to_id, graph_path, max_depth=5):
    entities, relations = load_graph(graph_path)
    visited = set()
    queue = [(from_id, [])]

    while queue:
        current, path = queue.pop(0)
        if current == to_id:
            return path
        if current in visited or len(path) >= max_depth:
            continue
        visited.add(current)

        for rel in relations:
            if rel["from"] == current and rel["to"] not in visited:
                queue.append((rel["to"], path + [rel]))
            if rel["to"] == current and rel["from"] not in visited:
                queue.append((rel["from"], path + [{**rel, "direction": "incoming"}]))

    return None
```

## Query Patterns by Use Case

### Task Management

```bash
python3 scripts/ontology.py query --type Task --where '{"status":"open","assignee":"p_me"}'
python3 scripts/ontology.py related --id task_001 --rel blocks
```

### Learning Review

```bash
python3 scripts/ontology.py list --type LearningRecord
python3 scripts/ontology.py list --type OperationalError
python3 scripts/ontology.py query --type LearningRecord --where '{"area":"backend"}'
```

### Feature Triage

```bash
python3 scripts/ontology.py query --type FeatureRequest --where '{"priority":"high"}'
python3 scripts/ontology.py related --id feat_feat_20260325_001 --rel derived_from
```

## Validation

```bash
python3 scripts/ontology.py validate
python3 scripts/ontology.py validate --graph memory/ontology/graph.jsonl --schema memory/ontology/schema.yaml
```

Use validation after large imports, schema changes, or scripted promotions from `.learnings/`.
