# Errors

Unexpected command failures, tool issues, exceptions, and external integration problems.

**Areas**: frontend | backend | infra | tests | docs | config
**Statuses**: pending | in_progress | resolved | wont_fix | promoted | promoted_to_skill

## Template

```markdown
## [ERR-YYYYMMDD-XXX] short_slug

**Logged**: 2026-03-25T10:00:00Z
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
Brief description of what failed

### Error
```
Actual error output
```

### Context
- Command or operation attempted
- Relevant input, flags, or environment details

### Suggested Fix
Best current hypothesis for resolving the issue

### Metadata
- Reproducible: yes | no | unknown
- Related Files: path/to/file.ext
- Tags: tag1, tag2
- See Also: ERR-YYYYMMDD-XXX

---
```
