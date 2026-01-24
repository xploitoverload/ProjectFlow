/**
 * Bulk Operations System
 * Multi-select and bulk edit capabilities
 */

class BulkOperations {
    constructor() {
        this.selectedIssues = new Set();
        this.allIssues = [];
        this.isActive = false;
        
        this.init();
    }

    init() {
        this.createToolbar();
        this.createBulkEditDialog();
        this.setupKeyboardShortcuts();
    }

    createToolbar() {
        const toolbarHTML = `
            <div id="bulkToolbar" class="bulk-toolbar" style="display: none;">
                <div class="bulk-toolbar-content">
                    <div class="bulk-selection-info">
                        <button class="btn-icon" onclick="bulkOps.clearSelection()">
                            <i data-lucide="x"></i>
                        </button>
                        <span class="selection-count">
                            <span id="selectedCount">0</span> selected
                        </span>
                    </div>

                    <div class="bulk-actions">
                        <button class="bulk-action-btn" onclick="bulkOps.selectAll()" title="Select All (Ctrl+A)">
                            <i data-lucide="check-square"></i>
                            Select All
                        </button>
                        
                        <div class="divider"></div>
                        
                        <button class="bulk-action-btn" onclick="bulkOps.openBulkEdit()">
                            <i data-lucide="edit"></i>
                            Edit
                        </button>
                        
                        <button class="bulk-action-btn" onclick="bulkOps.bulkMove()">
                            <i data-lucide="folder"></i>
                            Move to Sprint
                        </button>
                        
                        <button class="bulk-action-btn" onclick="bulkOps.bulkExport()">
                            <i data-lucide="download"></i>
                            Export
                        </button>
                        
                        <div class="divider"></div>
                        
                        <button class="bulk-action-btn danger" onclick="bulkOps.bulkDelete()">
                            <i data-lucide="trash-2"></i>
                            Delete
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', toolbarHTML);

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    createBulkEditDialog() {
        const dialogHTML = `
            <div id="bulkEditDialog" class="bulk-edit-dialog" style="display: none;">
                <div class="bulk-edit-backdrop"></div>
                <div class="bulk-edit-container">
                    <div class="bulk-edit-header">
                        <h3>Bulk Edit Issues</h3>
                        <button class="btn-icon-sm" onclick="bulkOps.closeBulkEdit()">
                            <i data-lucide="x"></i>
                        </button>
                    </div>

                    <div class="bulk-edit-content">
                        <p class="edit-description">
                            Editing <strong id="editingCount">0</strong> issues. 
                            Only changed fields will be updated.
                        </p>

                        <div class="edit-form">
                            <div class="form-section">
                                <h4>Issue Details</h4>
                                
                                <div class="form-row">
                                    <label>
                                        <input type="checkbox" id="changeType" onchange="bulkOps.toggleField('type')">
                                        Issue Type
                                    </label>
                                    <select id="bulkType" disabled>
                                        <option value="">Select Type</option>
                                        <option value="Bug">Bug</option>
                                        <option value="Feature">Feature</option>
                                        <option value="Task">Task</option>
                                        <option value="Story">Story</option>
                                        <option value="Epic">Epic</option>
                                    </select>
                                </div>

                                <div class="form-row">
                                    <label>
                                        <input type="checkbox" id="changeStatus" onchange="bulkOps.toggleField('status')">
                                        Status
                                    </label>
                                    <select id="bulkStatus" disabled>
                                        <option value="">Select Status</option>
                                        <option value="To Do">To Do</option>
                                        <option value="In Progress">In Progress</option>
                                        <option value="In Review">In Review</option>
                                        <option value="Done">Done</option>
                                    </select>
                                </div>

                                <div class="form-row">
                                    <label>
                                        <input type="checkbox" id="changePriority" onchange="bulkOps.toggleField('priority')">
                                        Priority
                                    </label>
                                    <select id="bulkPriority" disabled>
                                        <option value="">Select Priority</option>
                                        <option value="Critical">Critical</option>
                                        <option value="High">High</option>
                                        <option value="Medium">Medium</option>
                                        <option value="Low">Low</option>
                                    </select>
                                </div>

                                <div class="form-row">
                                    <label>
                                        <input type="checkbox" id="changeAssignee" onchange="bulkOps.toggleField('assignee')">
                                        Assignee
                                    </label>
                                    <select id="bulkAssignee" disabled>
                                        <option value="">Select Assignee</option>
                                        <option value="unassigned">Unassigned</option>
                                        <option value="1">John Doe</option>
                                        <option value="2">Jane Smith</option>
                                        <option value="3">Bob Johnson</option>
                                    </select>
                                </div>
                            </div>

                            <div class="form-section">
                                <h4>Sprint & Labels</h4>

                                <div class="form-row">
                                    <label>
                                        <input type="checkbox" id="changeSprint" onchange="bulkOps.toggleField('sprint')">
                                        Sprint
                                    </label>
                                    <select id="bulkSprint" disabled>
                                        <option value="">Select Sprint</option>
                                        <option value="backlog">Backlog</option>
                                        <option value="1">Sprint 1</option>
                                        <option value="2">Sprint 2</option>
                                        <option value="3">Sprint 3</option>
                                    </select>
                                </div>

                                <div class="form-row">
                                    <label>
                                        <input type="checkbox" id="changeLabels" onchange="bulkOps.toggleField('labels')">
                                        Labels
                                    </label>
                                    <div class="labels-input">
                                        <input type="text" 
                                               id="bulkLabels" 
                                               placeholder="Enter labels (comma separated)"
                                               disabled>
                                        <div class="label-action">
                                            <select id="labelAction" disabled>
                                                <option value="add">Add</option>
                                                <option value="remove">Remove</option>
                                                <option value="replace">Replace</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="form-section">
                                <h4>Additional Fields</h4>

                                <div class="form-row">
                                    <label>
                                        <input type="checkbox" id="changeStoryPoints" onchange="bulkOps.toggleField('storyPoints')">
                                        Story Points
                                    </label>
                                    <input type="number" 
                                           id="bulkStoryPoints" 
                                           min="0" 
                                           step="1"
                                           placeholder="0"
                                           disabled>
                                </div>

                                <div class="form-row">
                                    <label>
                                        <input type="checkbox" id="changeDueDate" onchange="bulkOps.toggleField('dueDate')">
                                        Due Date
                                    </label>
                                    <input type="date" id="bulkDueDate" disabled>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="bulk-edit-footer">
                        <button class="btn-secondary" onclick="bulkOps.closeBulkEdit()">
                            Cancel
                        </button>
                        <button class="btn-primary" onclick="bulkOps.applyBulkEdit()">
                            <i data-lucide="check"></i>
                            Apply Changes
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', dialogHTML);

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+A or Cmd+A to select all
            if ((e.ctrlKey || e.metaKey) && e.key === 'a' && this.isActive) {
                // Only if not in input
                if (!e.target.matches('input, textarea')) {
                    e.preventDefault();
                    this.selectAll();
                }
            }

            // Delete key to delete selected
            if (e.key === 'Delete' && this.selectedIssues.size > 0 && this.isActive) {
                if (!e.target.matches('input, textarea')) {
                    e.preventDefault();
                    this.bulkDelete();
                }
            }

            // Escape to clear selection
            if (e.key === 'Escape' && this.selectedIssues.size > 0) {
                this.clearSelection();
            }
        });
    }

    enableBulkMode(issues) {
        this.isActive = true;
        this.allIssues = issues;
        this.renderCheckboxes();
    }

    disableBulkMode() {
        this.isActive = false;
        this.clearSelection();
        this.hideToolbar();
        this.removeCheckboxes();
    }

    renderCheckboxes() {
        // Add checkboxes to issue cards
        const issueCards = document.querySelectorAll('.issue-card');
        issueCards.forEach(card => {
            if (!card.querySelector('.issue-checkbox')) {
                const checkbox = document.createElement('div');
                checkbox.className = 'issue-checkbox';
                checkbox.innerHTML = `
                    <input type="checkbox" 
                           class="bulk-checkbox" 
                           data-issue-id="${card.dataset.issueId}"
                           onchange="bulkOps.toggleIssue(${card.dataset.issueId})">
                `;
                card.prepend(checkbox);
            }
        });
    }

    removeCheckboxes() {
        document.querySelectorAll('.issue-checkbox').forEach(cb => cb.remove());
    }

    toggleIssue(issueId, shiftKey = false) {
        const id = String(issueId);
        
        // Handle shift-click range selection
        if (shiftKey && this.lastSelectedId) {
            this.selectRange(this.lastSelectedId, id);
        } else {
            if (this.selectedIssues.has(id)) {
                this.selectedIssues.delete(id);
            } else {
                this.selectedIssues.add(id);
                this.lastSelectedId = id;
            }
        }

        this.updateUI();
    }

    selectRange(startId, endId) {
        const issueIds = this.allIssues.map(i => String(i.id));
        const startIndex = issueIds.indexOf(String(startId));
        const endIndex = issueIds.indexOf(String(endId));
        
        if (startIndex === -1 || endIndex === -1) return;
        
        const [min, max] = [Math.min(startIndex, endIndex), Math.max(startIndex, endIndex)];
        
        for (let i = min; i <= max; i++) {
            this.selectedIssues.add(issueIds[i]);
        }
        
        this.updateUI();
    }

    selectAll() {
        this.allIssues.forEach(issue => {
            this.selectedIssues.add(String(issue.id));
        });
        this.updateUI();
    }

    clearSelection() {
        this.selectedIssues.clear();
        this.updateUI();
    }

    updateUI() {
        const count = this.selectedIssues.size;
        
        // Update toolbar
        if (count > 0) {
            this.showToolbar();
            document.getElementById('selectedCount').textContent = count;
        } else {
            this.hideToolbar();
        }

        // Update checkboxes
        document.querySelectorAll('.bulk-checkbox').forEach(cb => {
            const issueId = cb.dataset.issueId;
            cb.checked = this.selectedIssues.has(issueId);
            
            // Update card styling
            const card = cb.closest('.issue-card');
            if (cb.checked) {
                card?.classList.add('selected');
            } else {
                card?.classList.remove('selected');
            }
        });
    }

    showToolbar() {
        document.getElementById('bulkToolbar').style.display = 'block';
    }

    hideToolbar() {
        document.getElementById('bulkToolbar').style.display = 'none';
    }

    // Bulk Actions
    openBulkEdit() {
        document.getElementById('bulkEditDialog').style.display = 'flex';
        document.getElementById('editingCount').textContent = this.selectedIssues.size;
        
        if (window.lucide) {
            lucide.createIcons();
        }
    }

    closeBulkEdit() {
        document.getElementById('bulkEditDialog').style.display = 'none';
        
        // Reset form
        document.querySelectorAll('.bulk-edit-dialog input[type="checkbox"]').forEach(cb => {
            cb.checked = false;
        });
        this.toggleAllFields(false);
    }

    toggleField(fieldName) {
        const checkbox = document.getElementById(`change${fieldName.charAt(0).toUpperCase() + fieldName.slice(1)}`);
        const input = document.getElementById(`bulk${fieldName.charAt(0).toUpperCase() + fieldName.slice(1)}`);
        
        if (checkbox.checked) {
            input.disabled = false;
            if (fieldName === 'labels') {
                document.getElementById('labelAction').disabled = false;
            }
        } else {
            input.disabled = true;
            if (fieldName === 'labels') {
                document.getElementById('labelAction').disabled = true;
            }
        }
    }

    toggleAllFields(enabled) {
        const fields = ['type', 'status', 'priority', 'assignee', 'sprint', 'labels', 'storyPoints', 'dueDate'];
        fields.forEach(field => {
            const input = document.getElementById(`bulk${field.charAt(0).toUpperCase() + field.slice(1)}`);
            if (input) {
                input.disabled = !enabled;
            }
        });
    }

    async applyBulkEdit() {
        const changes = {};
        
        // Collect changed fields
        if (document.getElementById('changeType').checked) {
            changes.type = document.getElementById('bulkType').value;
        }
        if (document.getElementById('changeStatus').checked) {
            changes.status = document.getElementById('bulkStatus').value;
        }
        if (document.getElementById('changePriority').checked) {
            changes.priority = document.getElementById('bulkPriority').value;
        }
        if (document.getElementById('changeAssignee').checked) {
            changes.assignee = document.getElementById('bulkAssignee').value;
        }
        if (document.getElementById('changeSprint').checked) {
            changes.sprint = document.getElementById('bulkSprint').value;
        }
        if (document.getElementById('changeLabels').checked) {
            const labels = document.getElementById('bulkLabels').value.split(',').map(l => l.trim());
            const action = document.getElementById('labelAction').value;
            changes.labels = { action, values: labels };
        }
        if (document.getElementById('changeStoryPoints').checked) {
            changes.storyPoints = document.getElementById('bulkStoryPoints').value;
        }
        if (document.getElementById('changeDueDate').checked) {
            changes.dueDate = document.getElementById('bulkDueDate').value;
        }

        if (Object.keys(changes).length === 0) {
            alert('No changes selected');
            return;
        }

        try {
            const response = await fetch('/api/issues/bulk-edit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    issueIds: Array.from(this.selectedIssues),
                    changes
                })
            });

            if (response.ok) {
                alert(`Successfully updated ${this.selectedIssues.size} issues`);
                this.closeBulkEdit();
                this.clearSelection();
                
                // Reload page data
                if (window.loadBoardData) {
                    loadBoardData();
                }
            } else {
                alert('Failed to update issues');
            }
        } catch (error) {
            console.error('Bulk edit failed:', error);
            alert('Error updating issues');
        }
    }

    bulkMove() {
        const sprintId = prompt('Enter sprint ID to move issues:');
        if (!sprintId) return;

        this.applyBulkChanges({ sprint: sprintId });
    }

    async bulkExport() {
        try {
            const response = await fetch('/api/issues/export', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    issueIds: Array.from(this.selectedIssues),
                    format: 'csv'
                })
            });

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `issues-${Date.now()}.csv`;
            a.click();
        } catch (error) {
            console.error('Export failed:', error);
            alert('Failed to export issues');
        }
    }

    async bulkDelete() {
        const count = this.selectedIssues.size;
        
        if (!confirm(`Are you sure you want to delete ${count} issue(s)? This action cannot be undone.`)) {
            return;
        }

        try {
            const response = await fetch('/api/issues/bulk-delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    issueIds: Array.from(this.selectedIssues)
                })
            });

            if (response.ok) {
                alert(`Successfully deleted ${count} issues`);
                this.clearSelection();
                
                // Reload page data
                if (window.loadBoardData) {
                    loadBoardData();
                }
            } else {
                alert('Failed to delete issues');
            }
        } catch (error) {
            console.error('Bulk delete failed:', error);
            alert('Error deleting issues');
        }
    }

    async applyBulkChanges(changes) {
        try {
            const response = await fetch('/api/issues/bulk-edit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    issueIds: Array.from(this.selectedIssues),
                    changes
                })
            });

            if (response.ok) {
                this.clearSelection();
                if (window.loadBoardData) {
                    loadBoardData();
                }
            }
        } catch (error) {
            console.error('Bulk operation failed:', error);
        }
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.bulkOps = new BulkOperations();
});
