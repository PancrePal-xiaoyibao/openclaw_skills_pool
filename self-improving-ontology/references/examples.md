# Entry Examples

Concrete examples of well-formatted `.learnings/` entries.

## Learning: Correction

```markdown
## [LRN-20260325-001] correction

**Logged**: 2026-03-25T10:30:00Z
**Priority**: high
**Status**: pending
**Area**: tests

### Summary
Incorrectly assumed pytest fixtures are function-scoped in this workspace

### Details
I defaulted to function-scoped fixtures without checking local conventions.
The workspace uses broader fixture scopes for expensive setup, which changes
how new tests should be structured.

### Suggested Action
Check existing fixture scope patterns before introducing new test fixtures.

### Metadata
- Source: user_feedback
- Related Files: tests/conftest.py
- Tags: pytest, testing, fixtures

---
```

## Error Entry

```markdown
## [ERR-20260325-001] docker_build

**Logged**: 2026-03-25T09:15:00Z
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
Docker build fails due to platform mismatch

### Error
```
error: failed to solve: python:3.11-slim: no match for platform linux/arm64
```

### Context
- Command: `docker build -t myapp .`
- Dockerfile uses `FROM python:3.11-slim`
- Running on Apple Silicon

### Suggested Fix
Add a platform flag or use an architecture-aware base image.

### Metadata
- Reproducible: yes
- Related Files: Dockerfile
- Tags: docker, build, platform

---
```

## Feature Request

```markdown
## [FEAT-20260325-001] export_to_csv

**Logged**: 2026-03-25T16:45:00Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Requested Capability
Export analysis results to CSV format

### User Context
The user runs weekly reports and needs to share results with non-technical
stakeholders in spreadsheet tools.

### Complexity Estimate
simple

### Suggested Implementation
Add an `--output csv` flag and reuse the existing structured export path.

### Metadata
- Frequency: first_time
- Related Features: export_json
- Tags: reporting, csv, export

---
```

## Promotion Tip

Once an entry becomes stable knowledge, promote it:

```bash
python3 scripts/sync_learning_to_ontology.py promote --entry-id LRN-20260325-001
```
