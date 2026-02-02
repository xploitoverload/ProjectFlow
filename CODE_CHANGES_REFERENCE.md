# Code Changes Reference - Issue Creation & Filtering Fixes

## File 1: templates/kanban_board.html

### Change 1: Add missing data attributes (Line 717-722)
```html
<!-- BEFORE -->
<div class="kanban-card" draggable="true" ondragstart="drag(event)"
    data-issue-id="{{ issue.id }}"
    data-issue-key="{{ project.key or project.name[:3].upper() }}-{{ issue.id }}"
    data-assignee="{{ issue.assignee.username if issue.assignee else 'unassigned' }}"
    data-priority="{{ issue.priority|lower if issue.priority else 'medium' }}"
    data-labels="{{ issue.labels if issue.labels else '' }}">

<!-- AFTER -->
<div class="kanban-card" draggable="true" ondragstart="drag(event)"
    data-issue-id="{{ issue.id }}"
    data-issue-key="{{ project.key or project.name[:3].upper() }}-{{ issue.id }}"
    data-assignee="{{ issue.assignee.username if issue.assignee else 'unassigned' }}"
    data-priority="{{ issue.priority|lower if issue.priority else 'medium' }}"
    data-type="{{ issue.issue_type|lower if issue.issue_type else 'task' }}"
    data-sprint-id="{{ issue.sprint_id if issue.sprint_id else '' }}"
    data-labels="{{ issue.labels if issue.labels else '' }}">
```

### Change 2: Fix icon logic (Line 756)
```html
<!-- BEFORE -->
<span class="issue-label {{ issue.issue_type|lower }}">
    <i data-lucide="{{ 'bug' if issue.issue_type == 'Bug' else 'zap' if issue.issue_type == 'Feature' else 'bookmark' if issue.issue_type == 'Story' else 'check-square' }}"
        style="width: 10px; height: 10px;"></i>
    {{ issue.issue_type }}
</span>

<!-- AFTER -->
<span class="issue-label {{ issue.issue_type|lower }}">
    <i data-lucide="{{ 'bug' if issue.issue_type|lower == 'bug' else 'zap' if issue.issue_type|lower == 'task' else 'bookmark' if issue.issue_type|lower == 'story' else 'layers' if issue.issue_type|lower == 'epic' else 'check-square' }}"
        style="width: 10px; height: 10px;"></i>
    {{ issue.issue_type }}
</span>
```

### Change 3: Fix assignee dropdown variable (Line 859)
```html
<!-- BEFORE -->
<select name="assignee_id" class="form-select">
    <option value="">Unassigned</option>
    {% for user in users if users is defined %}
    <option value="{{ user.id }}">{{ user.username }}</option>
    {% endfor %}
</select>

<!-- AFTER -->
<select name="assignee_id" class="form-select">
    <option value="">Unassigned</option>
    {% for user in team_members_list if team_members_list is defined %}
    <option value="{{ user.id }}">{{ user.username }}</option>
    {% endfor %}
</select>
```

---

## File 2: templates/backlog.html

### Change 1: Replace issue.type with issue.issue_type (Line 42)
```html
<!-- BEFORE -->
<i data-lucide="{{ 'bug' if issue.type == 'bug' else 'bookmark' if issue.type == 'story' else 'circle-dot' }}" class="w-4 h-4 mr-2 text-gray-500"></i>

<!-- AFTER -->
<i data-lucide="{{ 'bug' if issue.issue_type == 'bug' else 'bookmark' if issue.issue_type == 'story' else 'circle-dot' }}" class="w-4 h-4 mr-2 text-gray-500"></i>
```

### Change 2: Replace issue.type with issue.issue_type (Line 51)
```html
<!-- BEFORE -->
{{ issue.type }}

<!-- AFTER -->
{{ issue.issue_type }}
```

---

## File 3: templates/issues_list.html

### Change 1: Replace issue.type with issue.issue_type (Line 60)
```html
<!-- BEFORE -->
<i data-lucide="{{ 'bug' if issue.type == 'bug' else 'bookmark' if issue.type == 'story' else 'circle-dot' }}"

<!-- AFTER -->
<i data-lucide="{{ 'bug' if issue.issue_type == 'bug' else 'bookmark' if issue.issue_type == 'story' else 'circle-dot' }}"
```

### Change 2: Replace issue.type with issue.issue_type (Line 64)
```html
<!-- BEFORE -->
{{ issue.type }}

<!-- AFTER -->
{{ issue.issue_type }}
```

---

## File 4: templates/issue_detail.html

### Change 1: Replace issue.type with issue.issue_type (Line 119)
```html
<!-- BEFORE -->
{% set issue_type = issue.type or 'task' %}

<!-- AFTER -->
{% set issue_type = issue.issue_type or 'task' %}
```

### Change 2: Replace issue.type with issue.issue_type (Lines 262-264)
```html
<!-- BEFORE -->
<span class="issue-type-badge {{ issue.type or 'task' }}">
    <i data-lucide="{{ 'bug' if issue.type == 'bug' else 'bookmark' if issue.type == 'story' else 'zap' if issue.type == 'epic' else 'circle-dot' }}" class="icon-xs"></i>
    {{ (issue.type or 'task').title() }}
</span>

<!-- AFTER -->
<span class="issue-type-badge {{ issue.issue_type or 'task' }}">
    <i data-lucide="{{ 'bug' if issue.issue_type == 'bug' else 'bookmark' if issue.issue_type == 'story' else 'zap' if issue.issue_type == 'epic' else 'circle-dot' }}" class="icon-xs"></i>
    {{ (issue.issue_type or 'task').title() }}
</span>
```

---

## File 5: app/routes/projects.py

### Change 1: Fix type filter field name (Line 1131)
```python
# BEFORE
if type_filter:
    query = query.filter_by(type=type_filter)

# AFTER
if type_filter:
    query = query.filter_by(issue_type=type_filter)
```

---

## Summary of Changes

| File | Line(s) | Change Type | Purpose |
|------|---------|-------------|---------|
| kanban_board.html | 717-722 | Add attributes | Enable filtering by type and sprint |
| kanban_board.html | 756 | Fix comparisons | Show correct icons for issue types |
| kanban_board.html | 859 | Fix variable | Populate assignee dropdown |
| backlog.html | 42, 51 | Replace field | Fix issue type display |
| issues_list.html | 60, 64 | Replace field | Fix issue type display |
| issue_detail.html | 119 | Replace field | Fix variable setup |
| issue_detail.html | 262-264 | Replace field | Fix issue type display |
| projects.py | 1131 | Fix column name | Enable type filtering |

**Total Changes:** 11 edits across 5 files
**Severity:** 1 CRITICAL + 5 HIGH + 0 MEDIUM
**Status:** ✅ ALL FIXED
