/**
 * Bulk Actions Manager - JIRA-style bulk operations
 * Enables multi-select with checkboxes and bulk update operations
 */

class BulkActionsManager {
    constructor() {
        this.selectedIssues = new Set();
        this.bulkMode = false;
        this.init();
    }

    init() {
        this.createBulkToolbar();
        this.setupEventListeners();
    }

    createBulkToolbar() {
        const toolbar = document.createElement('div');
        toolbar.id = 'bulkActionsToolbar';
        toolbar.className = 'bulk-actions-toolbar';
        toolbar.innerHTML = `
            <div class="bulk-actions-content">
                <button class="bulk-action-btn" id="toggleBulkMode" title="Enable bulk selection">
                    <i data-lucide="check-square"></i>
                    <span>Bulk actions</span>
                </button>
                <div class="bulk-actions-active" style="display: none;">
                    <div class="bulk-actions-count">
                        <span id="bulkSelectionCount">0</span> selected
                    </div>
                    <div class="bulk-actions-separator"></div>
                    <button class="bulk-action-btn" id="selectAllBtn">
                        <i data-lucide="check-square"></i>
                        Select all
                    </button>
                    <button class="bulk-action-btn" id="deselectAllBtn">
                        <i data-lucide="square"></i>
                        Deselect all
                    </button>
                    <div class="bulk-actions-separator"></div>
                    <button class="bulk-action-btn" id="bulkUpdateStatus">
                        <i data-lucide="refresh-cw"></i>
                        Update status
                    </button>
                    <button class="bulk-action-btn" id="bulkUpdateAssignee">
                        <i data-lucide="user-plus"></i>
                        Assign to
                    </button>
                    <button class="bulk-action-btn" id="bulkUpdatePriority">
                        <i data-lucide="flag"></i>
                        Set priority
                    </button>
                    <button class="bulk-action-btn" id="bulkMove">
                        <i data-lucide="move"></i>
                        Move
                    </button>
                    <button class="bulk-action-btn bulk-danger" id="bulkDelete">
                        <i data-lucide="trash-2"></i>
                        Delete
                    </button>
                    <div class="bulk-actions-separator"></div>
                    <button class="bulk-action-btn" id="cancelBulkMode">
                        <i data-lucide="x"></i>
                        Cancel
                    </button>
                </div>
            </div>
        `;

        // Insert after toolbar or before main content
        const mainToolbar = document.querySelector('.kanban-toolbar, .calendar-toolbar, .header-toolbar');
        if (mainToolbar) {
            mainToolbar.after(toolbar);
        }
    }

    setupEventListeners() {
        // Toggle bulk mode
        document.getElementById('toggleBulkMode')?.addEventListener('click', () => {
            this.toggleBulkMode();
        });

        // Cancel bulk mode
        document.getElementById('cancelBulkMode')?.addEventListener('click', () => {
            this.toggleBulkMode();
        });

        // Select all
        document.getElementById('selectAllBtn')?.addEventListener('click', () => {
            this.selectAll();
        });

        // Deselect all
        document.getElementById('deselectAllBtn')?.addEventListener('click', () => {
            this.deselectAll();
        });

        // Bulk actions
        document.getElementById('bulkUpdateStatus')?.addEventListener('click', () => {
            this.showBulkUpdateModal('status');
        });

        document.getElementById('bulkUpdateAssignee')?.addEventListener('click', () => {
            this.showBulkUpdateModal('assignee');
        });

        document.getElementById('bulkUpdatePriority')?.addEventListener('click', () => {
            this.showBulkUpdateModal('priority');
        });

        document.getElementById('bulkMove')?.addEventListener('click', () => {
            this.showBulkMoveModal();
        });

        document.getElementById('bulkDelete')?.addEventListener('click', () => {
            this.bulkDelete();
        });
    }

    toggleBulkMode() {
        this.bulkMode = !this.bulkMode;

        const toggleBtn = document.getElementById('toggleBulkMode');
        const activeToolbar = document.querySelector('.bulk-actions-active');

        if (this.bulkMode) {
            // Enable bulk mode
            toggleBtn.style.display = 'none';
            activeToolbar.style.display = 'flex';
            this.addCheckboxesToIssues();
            document.body.classList.add('bulk-mode-active');
        } else {
            // Disable bulk mode
            toggleBtn.style.display = 'flex';
            activeToolbar.style.display = 'none';
            this.removeCheckboxesFromIssues();
            this.deselectAll();
            document.body.classList.remove('bulk-mode-active');
        }

        lucide.createIcons();
    }

    addCheckboxesToIssues() {
        const issues = document.querySelectorAll('[data-issue-id]');
        
        issues.forEach(issue => {
            if (issue.querySelector('.bulk-select-checkbox')) return; // Already has checkbox

            const checkbox = document.createElement('div');
            checkbox.className = 'bulk-select-checkbox';
            checkbox.innerHTML = '<i data-lucide="square"></i>';
            checkbox.dataset.issueId = issue.dataset.issueId;
            
            checkbox.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleIssueSelection(issue.dataset.issueId, checkbox);
            });

            issue.style.position = 'relative';
            issue.insertBefore(checkbox, issue.firstChild);
        });

        lucide.createIcons();
    }

    removeCheckboxesFromIssues() {
        document.querySelectorAll('.bulk-select-checkbox').forEach(cb => cb.remove());
    }

    toggleIssueSelection(issueId, checkbox) {
        if (this.selectedIssues.has(issueId)) {
            this.selectedIssues.delete(issueId);
            checkbox.innerHTML = '<i data-lucide="square"></i>';
            checkbox.closest('[data-issue-id]').classList.remove('bulk-selected');
        } else {
            this.selectedIssues.add(issueId);
            checkbox.innerHTML = '<i data-lucide="check-square"></i>';
            checkbox.closest('[data-issue-id]').classList.add('bulk-selected');
        }

        this.updateSelectionCount();
        lucide.createIcons();
    }

    selectAll() {
        const issues = document.querySelectorAll('[data-issue-id]');
        issues.forEach(issue => {
            const issueId = issue.dataset.issueId;
            if (!this.selectedIssues.has(issueId)) {
                const checkbox = issue.querySelector('.bulk-select-checkbox');
                this.toggleIssueSelection(issueId, checkbox);
            }
        });
    }

    deselectAll() {
        this.selectedIssues.forEach(issueId => {
            const issue = document.querySelector(`[data-issue-id="${issueId}"]`);
            if (issue) {
                const checkbox = issue.querySelector('.bulk-select-checkbox');
                this.toggleIssueSelection(issueId, checkbox);
            }
        });
    }

    updateSelectionCount() {
        document.getElementById('bulkSelectionCount').textContent = this.selectedIssues.size;
    }

    showBulkUpdateModal(field) {
        if (this.selectedIssues.size === 0) {
            window.notificationManager.addNotification({
                title: 'No Selection',
                message: 'Please select at least one issue',
                type: 'warning'
            });
            return;
        }

        // Create modal (simplified for demo)
        const modal = document.createElement('div');
        modal.className = 'modal-backdrop';
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h3>Bulk Update ${field}</h3>
                    <button class="modal-close" onclick="this.closest('.modal-backdrop').remove()">
                        <i data-lucide="x"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <p>Updating ${this.selectedIssues.size} issue(s)</p>
                    <select class="form-input" id="bulkUpdateValue">
                        ${this.getOptionsForField(field)}
                    </select>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-ghost" onclick="this.closest('.modal-backdrop').remove()">Cancel</button>
                    <button class="btn btn-primary" onclick="window.bulkActionsManager.executeBulkUpdate('${field}')">Update</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        lucide.createIcons();
    }

    getOptionsForField(field) {
        const options = {
            status: ['To Do', 'In Progress', 'In Review', 'Done'],
            priority: ['Critical', 'High', 'Medium', 'Low'],
            assignee: ['User 1', 'User 2', 'User 3', 'Unassigned']
        };

        return (options[field] || []).map(opt => 
            `<option value="${opt}">${opt}</option>`
        ).join('');
    }

    async executeBulkUpdate(field) {
        const value = document.getElementById('bulkUpdateValue').value;
        const issueIds = Array.from(this.selectedIssues);

        try {
            const response = await fetch('/api/issues/bulk-update', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    issueIds: issueIds,
                    field: field,
                    value: value
                })
            });

            if (response.ok) {
                window.notificationManager.addNotification({
                    title: 'Bulk Update Complete',
                    message: `Updated ${issueIds.length} issue(s)`,
                    type: 'success'
                });
                document.querySelector('.modal-backdrop').remove();
                setTimeout(() => window.location.reload(), 1000);
            }
        } catch (error) {
            window.notificationManager.addNotification({
                title: 'Update Failed',
                message: 'Could not complete bulk update',
                type: 'error'
            });
        }
    }

    async bulkDelete() {
        if (this.selectedIssues.size === 0) return;

        if (!confirm(`Delete ${this.selectedIssues.size} issue(s)? This cannot be undone.`)) {
            return;
        }

        const issueIds = Array.from(this.selectedIssues);

        try {
            const response = await fetch('/api/issues/bulk-delete', {
                method: 'DELETE',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ issueIds: issueIds })
            });

            if (response.ok) {
                window.notificationManager.addNotification({
                    title: 'Issues Deleted',
                    message: `Deleted ${issueIds.length} issue(s)`,
                    type: 'success'
                });
                setTimeout(() => window.location.reload(), 1000);
            }
        } catch (error) {
            window.notificationManager.addNotification({
                title: 'Delete Failed',
                message: 'Could not delete issues',
                type: 'error'
            });
        }
    }

    showBulkMoveModal() {
        if (this.selectedIssues.size === 0) return;

        window.notificationManager.addNotification({
            title: 'Bulk Move',
            message: 'Select target column and drag to move',
            type: 'info'
        });
    }
}

// CSS for bulk actions
const style = document.createElement('style');
style.textContent = `
    .bulk-actions-toolbar {
        background: var(--jira-darker-bg, #161a1d);
        border-bottom: 1px solid var(--jira-border, #2c333a);
        padding: 8px 16px;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .bulk-actions-content {
        display: flex;
        align-items: center;
        gap: 8px;
        width: 100%;
    }

    .bulk-actions-active {
        display: flex;
        align-items: center;
        gap: 8px;
        flex: 1;
    }

    .bulk-actions-count {
        font-size: 13px;
        font-weight: 600;
        color: var(--jira-text, #b6c2cf);
        padding: 0 8px;
    }

    .bulk-actions-separator {
        width: 1px;
        height: 20px;
        background: var(--jira-border, #2c333a);
    }

    .bulk-action-btn {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        background: transparent;
        border: 1px solid var(--jira-border, #2c333a);
        border-radius: 3px;
        color: var(--jira-text, #b6c2cf);
        font-size: 13px;
        cursor: pointer;
        transition: all 0.2s;
    }

    .bulk-action-btn:hover {
        background: var(--jira-hover, #2c3338);
        border-color: var(--jira-text-secondary, #8c9bab);
    }

    .bulk-action-btn.bulk-danger {
        color: #ff5630;
        border-color: #ff5630;
    }

    .bulk-action-btn.bulk-danger:hover {
        background: rgba(255, 86, 48, 0.1);
    }

    .bulk-action-btn i {
        width: 14px;
        height: 14px;
    }

    .bulk-select-checkbox {
        position: absolute;
        left: -8px;
        top: 8px;
        width: 20px;
        height: 20px;
        background: var(--jira-card-bg, #22272b);
        border: 2px solid var(--jira-border, #2c333a);
        border-radius: 3px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        z-index: 10;
        transition: all 0.2s;
    }

    .bulk-select-checkbox:hover {
        background: var(--jira-hover, #2c3338);
        border-color: #0052cc;
    }

    .bulk-select-checkbox i {
        width: 14px;
        height: 14px;
        color: var(--jira-text-secondary, #8c9bab);
    }

    .bulk-mode-active [data-issue-id] {
        padding-left: 28px;
    }

    [data-issue-id].bulk-selected {
        outline: 2px solid #0052cc;
        outline-offset: 2px;
        background: rgba(0, 82, 204, 0.05);
    }
`;
document.head.appendChild(style);

// Initialize on DOM load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.bulkActionsManager = new BulkActionsManager();
    });
} else {
    window.bulkActionsManager = new BulkActionsManager();
}
