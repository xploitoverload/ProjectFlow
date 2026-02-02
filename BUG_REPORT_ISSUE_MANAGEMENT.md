# Bug Report: Issue Creation, Filtering, and Form Issues

## Summary
Found 5 critical bugs related to issue type field naming inconsistencies and form variable mismatches that prevent proper issue creation and filtering.

---

## Bug #1: Issue Type Field Name Mismatch in issue_detail.html

**Severity:** HIGH

**File:** [templates/issue_detail.html](templates/issue_detail.html#L119)

**Lines:** 119, 262, 263, 264

**Current Incorrect Code:**
```html
{% set issue_type = issue.type or 'task' %}
...
<span class="issue-type-badge {{ issue.type or 'task' }}">
    <i data-lucide="{{ 'bug' if issue.type == 'bug' else 'bookmark' if issue.type == 'story' else 'zap' if issue.type == 'epic' else 'circle-dot' }}" class="icon-xs"></i>
    {{ (issue.type or 'task').title() }}
```

**Expected Correct Code:**
```html
{% set issue_type = issue.issue_type or 'task' %}
...
<span class="issue-type-badge {{ issue.issue_type or 'task' }}">
    <i data-lucide="{{ 'bug' if issue.issue_type == 'bug' else 'bookmark' if issue.issue_type == 'story' else 'zap' if issue.issue_type == 'epic' else 'circle-dot' }}" class="icon-xs"></i>
    {{ (issue.issue_type or 'task').title() }}
```

**Explanation:** 
The Issue model uses `issue_type` field (see issue_service.py line 77), but this template is accessing `issue.type` which doesn't exist. This causes the issue type icon and label to not display correctly. All four references to `issue.type` should be changed to `issue.issue_type`.

---

## Bug #2: Issue Type Field Name Mismatch in kanban_board.html

**Severity:** HIGH

**File:** [templates/kanban_board.html](templates/kanban_board.html#L754-L758)

**Lines:** 754, 755, 756, 758

**Current Incorrect Code:**
```html
{% if issue.issue_type %}
<span class="issue-label {{ issue.issue_type|lower }}">
    <i data-lucide="{{ 'bug' if issue.issue_type == 'Bug' else 'zap' if issue.issue_type == 'Feature' else 'bookmark' if issue.issue_type == 'Story' else 'check-square' }}"
        class="icon-xs"></i>
    {{ issue.issue_type }}
```

**Expected Correct Code:**
```html
{% if issue.issue_type %}
<span class="issue-label {{ issue.issue_type|lower }}">
    <i data-lucide="{{ 'bug' if issue.issue_type == 'bug' else 'zap' if issue.issue_type == 'task' else 'bookmark' if issue.issue_type == 'story' else 'check-square' if issue.issue_type == 'epic' else 'circle-dot' }}"
        class="icon-xs"></i>
    {{ issue.issue_type|title }}
```

**Explanation:** 
The issue type values are stored in lowercase ('bug', 'task', 'story', 'epic') but the template is comparing against capitalized values ('Bug', 'Feature', 'Story'). Also, 'Feature' is not a valid issue type - should be 'task'. Additionally, the icon for 'epic' and 'subtask' types are missing from the conditional. The comparisons should use lowercase values.

---

## Bug #3: Missing Assignee Data in kanban_board.html Form

**Severity:** CRITICAL

**File:** [templates/kanban_board.html](templates/kanban_board.html#L859)

**Lines:** 859

**Current Incorrect Code:**
```html
<select name="assignee_id" class="form-select">
    <option value="">Unassigned</option>
    {% for user in users if users is defined %}
    <option value="{{ user.id }}">{{ user.username }}</option>
    {% endfor %}
</select>
```

**Expected Correct Code:**
```html
<select name="assignee_id" class="form-select">
    <option value="">Unassigned</option>
    {% for user in team_members_list if team_members_list is defined %}
    <option value="{{ user.id }}">{{ user.username }}</option>
    {% endfor %}
</select>
```

**Explanation:** 
The template references `users` variable which is not passed from the route handler (line 104 in projects.py). The actual variable passed is `team_members_list`. This means the assignee dropdown will always be empty, preventing users from assigning issues. Check projects.py line 104 - the route only passes `team_members_list`, not `users`.

---

## Bug #4: Issue Type Filter Logic Issue in kanban_board.html Card Display

**Severity:** MEDIUM

**File:** [templates/kanban_board.html](templates/kanban_board.html#L720)

**Lines:** 720

**Current Incorrect Code:**
```html
<div class="kanban-card" data-issue-id="{{ issue.id }}"
    data-assignee="{{ issue.assignee.username if issue.assignee else 'unassigned' }}"
```

**Expected Correct Code:**
```html
<div class="kanban-card" data-issue-id="{{ issue.id }}"
    data-assignee="{{ issue.assignee.username if issue.assignee else 'unassigned' }}"
    data-issue-type="{{ issue.issue_type|lower if issue.issue_type else 'task' }}"
```

**Explanation:** 
The card element is missing the `data-issue-type` attribute that the board-filters.js script uses to filter issues by type. Line 152-162 in board-filters.js attempts to filter by type but the data attribute is not present on the cards, making type filtering non-functional.

---

## Bug #5: Incorrect Issue Type Comparisons in Multiple Templates

**Severity:** MEDIUM

**File:** [templates/issues.html](templates/issues.html#L102-L119)

**Lines:** 102-119

**Current Incorrect Code:**
```html
{% if issue.issue_type == 'bug' %}
    ...
{% elif issue.issue_type == 'task' %}
    ...
{% elif issue.issue_type == 'story' %}
    ...
{% elif issue.issue_type == 'epic' %}
    ...
{% else %}
    <span>{{ issue.issue_type|default('Task')|title }}</span>
```

**Expected Correct Code:** (template is correct, but ensure data is lowercase)
The template is correct, but ensure that Issue model stores type in lowercase.

**Explanation:** 
The icon mapping checks for lowercase issue types, which is correct. However, other templates like backlog.html, backlog_new.html, board.html, timeline.html use `issue.type` instead of `issue.issue_type`, same as bug #1.

---

## Bug #6: Form Field References in board-filters.js

**Severity:** MEDIUM  

**File:** [static/js/board-filters.js](static/js/board-filters.js#L152-L162)

**Lines:** 152-162

**Current Issue:** 
The filter tries to read data attributes from cards, but:
- `data-issue-type` attribute is missing from kanban cards (Bug #4)
- `data-priority` attribute is missing from kanban cards
- `data-sprint` attribute is missing from kanban cards

**Expected:** 
Add these data attributes to the kanban cards in the template:
```html
data-priority="{{ issue.priority|lower }}"
data-sprint="{{ issue.sprint_id if issue.sprint_id else 'no-sprint' }}"
```

**Explanation:**
The BoardFiltersManager reads various data attributes from cards to populate filter options, but these attributes are not present on the card elements, making most filters non-functional.

---

## Summary of Field Name Mismatches

| Issue Model Field | Correct Template Reference | Incorrect References |
|---|---|---|
| `issue_type` | `issue.issue_type` | `issue.type` |
| `priority` | `issue.priority` | Various inconsistencies |
| `assignee_id` | `issue.assignee_id` | N/A |
| `status` | `issue.status` | Correct in most places |

---

## Impact

1. **Issue creation won't work properly** - assignee dropdown is empty
2. **Issue type filtering won't work** - type comparisons fail and data attributes missing
3. **Issue type display is broken** - using wrong field name causes display to show nothing
4. **Filtering by assignee, priority, sprint won't work** - missing data attributes on cards

---

## Recommended Fix Priority

1. **CRITICAL:** Fix Bug #3 (assignee dropdown) - blocks issue creation
2. **HIGH:** Fix Bug #1 and Bug #2 (issue type field name) - blocks issue display and filtering
3. **MEDIUM:** Fix Bug #4, #5, #6 (data attributes and comparisons) - blocks filtering functionality

