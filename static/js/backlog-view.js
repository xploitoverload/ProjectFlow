/**
 * Backlog View - JIRA-style product backlog
 * Features: Epic grouping, priority ordering, drag-drop reordering, estimation
 */

class BacklogView {
    constructor() {
        this.backlogItems = [];
        this.epics = [];
        this.groupBy = 'epic'; // epic, none, priority, assignee
        this.filterBy = {
            epic: null,
            priority: null,
            assignee: null,
            version: null
        };
        this.estimationMode = false;
        this.selectedIssues = new Set();
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadBacklog();
        this.loadEpics();
    }

    setupEventListeners() {
        // Group by selector
        document.getElementById('backlogGroupBy')?.addEventListener('change', (e) => {
            this.groupBy = e.target.value;
            this.renderBacklog();
        });

        // Filter selectors
        document.getElementById('backlogFilterEpic')?.addEventListener('change', (e) => {
            this.filterBy.epic = e.target.value || null;
            this.renderBacklog();
        });

        document.getElementById('backlogFilterPriority')?.addEventListener('change', (e) => {
            this.filterBy.priority = e.target.value || null;
            this.renderBacklog();
        });

        // Estimation mode toggle
        document.getElementById('toggleEstimationMode')?.addEventListener('click', () => {
            this.toggleEstimationMode();
        });

        // Bulk actions
        document.getElementById('bulkMoveToSprint')?.addEventListener('click', () => {
            this.bulkMoveToSprint();
        });

        document.getElementById('bulkSetPriority')?.addEventListener('click', () => {
            this.bulkSetPriority();
        });

        document.getElementById('bulkEstimate')?.addEventListener('click', () => {
            this.bulkEstimate();
        });

        // Create epic button
        document.getElementById('createEpicBtn')?.addEventListener('click', () => {
            this.openCreateEpicModal();
        });

        // Create issue in backlog
        document.getElementById('createBacklogIssueBtn')?.addEventListener('click', () => {
            this.openCreateIssueModal();
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                if (e.key === 'a' && this.isBacklogView()) {
                    e.preventDefault();
                    this.selectAll();
                }
            }
        });
    }

    async loadBacklog() {
        try {
            const projectId = this.getCurrentProjectId();
            const response = await fetch(`/api/projects/${projectId}/backlog`);
            if (response.ok) {
                this.backlogItems = await response.json();
                this.renderBacklog();
            }
        } catch (error) {
            console.error('Failed to load backlog:', error);
        }
    }

    async loadEpics() {
        try {
            const projectId = this.getCurrentProjectId();
            const response = await fetch(`/api/projects/${projectId}/epics`);
            if (response.ok) {
                this.epics = await response.json();
                this.renderEpicsFilter();
            }
        } catch (error) {
            console.error('Failed to load epics:', error);
        }
    }

    renderBacklog() {
        const container = document.getElementById('backlogContainer');
        if (!container) return;

        // Filter items
        let filteredItems = this.backlogItems.filter(item => {
            if (this.filterBy.epic && item.epic_id !== parseInt(this.filterBy.epic)) return false;
            if (this.filterBy.priority && item.priority !== this.filterBy.priority) return false;
            if (this.filterBy.assignee && item.assignee_id !== parseInt(this.filterBy.assignee)) return false;
            if (this.filterBy.version && item.version_id !== parseInt(this.filterBy.version)) return false;
            return true;
        });

        // Group items
        let groupedItems = this.groupItems(filteredItems);

        if (filteredItems.length === 0) {
            container.innerHTML = `
                <div class="backlog-empty">
                    <i data-lucide="inbox" style="width: 64px; height: 64px; margin-bottom: 16px;"></i>
                    <h3>Your backlog is empty</h3>
                    <p>Create issues to add them to your product backlog.</p>
                    <button class="btn btn-primary" onclick="window.backlogView.openCreateIssueModal()">
                        <i data-lucide="plus"></i>
                        Create Issue
                    </button>
                </div>
            `;
            if (window.lucide) lucide.createIcons();
            return;
        }

        // Render grouped items
        container.innerHTML = Object.entries(groupedItems).map(([groupKey, items]) => {
            return this.renderGroup(groupKey, items);
        }).join('');

        this.setupDragAndDrop();
        if (window.lucide) lucide.createIcons();
    }

    groupItems(items) {
        if (this.groupBy === 'none') {
            return { 'Backlog': items };
        }

        const grouped = {};

        items.forEach(item => {
            let key;
            switch (this.groupBy) {
                case 'epic':
                    key = item.epic?.name || 'No Epic';
                    break;
                case 'priority':
                    key = item.priority || 'No Priority';
                    break;
                case 'assignee':
                    key = item.assignee?.username || 'Unassigned';
                    break;
                default:
                    key = 'Backlog';
            }

            if (!grouped[key]) {
                grouped[key] = [];
            }
            grouped[key].push(item);
        });

        // Sort groups by priority if grouping by epic
        if (this.groupBy === 'epic') {
            Object.keys(grouped).forEach(key => {
                grouped[key].sort((a, b) => this.comparePriority(a.priority, b.priority));
            });
        }

        return grouped;
    }

    renderGroup(groupName, items) {
        const groupId = groupName.replace(/\s+/g, '-').toLowerCase();
        const totalPoints = items.reduce((sum, item) => sum + (item.story_points || 0), 0);
        const groupColor = this.getGroupColor(groupName);

        return `
            <div class="backlog-group" data-group="${groupId}">
                <div class="backlog-group-header" onclick="window.backlogView.toggleGroup('${groupId}')">
                    <div class="group-header-left">
                        <i data-lucide="chevron-down" class="group-toggle"></i>
                        ${this.groupBy === 'epic' && groupName !== 'No Epic' ? 
                            `<div class="epic-badge" style="background: ${groupColor}"></div>` : ''}
                        <h3 class="group-title">${groupName}</h3>
                        <span class="group-count">${items.length} issues</span>
                        ${totalPoints > 0 ? `<span class="group-points">${totalPoints} points</span>` : ''}
                    </div>
                    <div class="group-header-right">
                        ${this.groupBy === 'epic' && groupName !== 'No Epic' ? `
                            <button class="btn-icon-sm" onclick="event.stopPropagation(); window.backlogView.editEpic('${groupName}')">
                                <i data-lucide="edit-2"></i>
                            </button>
                        ` : ''}
                    </div>
                </div>
                <div class="backlog-group-body" data-group-body="${groupId}">
                    ${items.map(item => this.renderBacklogItem(item)).join('')}
                </div>
            </div>
        `;
    }

    renderBacklogItem(item) {
        const isSelected = this.selectedIssues.has(item.id);
        const priorityIcon = this.getPriorityIcon(item.priority);

        return `
            <div class="backlog-item ${isSelected ? 'selected' : ''}" 
                 data-issue-id="${item.id}"
                 draggable="true">
                <div class="backlog-item-checkbox">
                    <input type="checkbox" 
                           ${isSelected ? 'checked' : ''}
                           onclick="window.backlogView.toggleSelection(${item.id})">
                </div>
                
                <div class="backlog-item-content" onclick="openIssueDetail(${item.id})">
                    <div class="backlog-item-header">
                        <div class="backlog-item-left">
                            ${priorityIcon}
                            <span class="issue-key">${item.key}</span>
                            <span class="issue-type-badge ${item.issue_type?.toLowerCase()}">${item.issue_type}</span>
                        </div>
                        <div class="backlog-item-right">
                            ${item.assignee ? `
                                <div class="user-avatar-sm" style="background: ${item.assignee.avatar_color}"
                                     title="${item.assignee.username}">
                                    ${item.assignee.username.substring(0, 2).toUpperCase()}
                                </div>
                            ` : ''}
                            ${this.estimationMode ? `
                                <div class="estimation-input-wrapper">
                                    <input type="number" 
                                           class="estimation-input" 
                                           value="${item.story_points || ''}"
                                           placeholder="?"
                                           min="0"
                                           max="100"
                                           onclick="event.stopPropagation()"
                                           onchange="window.backlogView.updateEstimate(${item.id}, this.value)">
                                </div>
                            ` : item.story_points ? `
                                <div class="story-points-badge">${item.story_points}</div>
                            ` : ''}
                        </div>
                    </div>
                    <div class="backlog-item-title">${item.title}</div>
                    ${item.labels && item.labels.length > 0 ? `
                        <div class="backlog-item-labels">
                            ${item.labels.map(label => `<span class="label-tag">${label}</span>`).join('')}
                        </div>
                    ` : ''}
                </div>
                
                <div class="backlog-item-actions">
                    <button class="btn-icon-sm" 
                            onclick="event.stopPropagation(); window.backlogView.quickAddToSprint(${item.id})"
                            title="Add to sprint">
                        <i data-lucide="plus-circle"></i>
                    </button>
                    <button class="btn-icon-sm drag-handle" title="Drag to reorder">
                        <i data-lucide="grip-vertical"></i>
                    </button>
                </div>
            </div>
        `;
    }

    renderEpicsFilter() {
        const select = document.getElementById('backlogFilterEpic');
        if (!select) return;

        select.innerHTML = `
            <option value="">All Epics</option>
            ${this.epics.map(epic => `
                <option value="${epic.id}">${epic.name}</option>
            `).join('')}
        `;
    }

    toggleGroup(groupId) {
        const body = document.querySelector(`[data-group-body="${groupId}"]`);
        const toggle = document.querySelector(`[data-group="${groupId}"] .group-toggle`);
        
        if (body && toggle) {
            const isCollapsed = body.style.display === 'none';
            body.style.display = isCollapsed ? 'block' : 'none';
            toggle.style.transform = isCollapsed ? 'rotate(0deg)' : 'rotate(-90deg)';
        }
    }

    toggleSelection(issueId) {
        if (this.selectedIssues.has(issueId)) {
            this.selectedIssues.delete(issueId);
        } else {
            this.selectedIssues.add(issueId);
        }
        this.updateBulkActionsBar();
        this.renderBacklog();
    }

    selectAll() {
        this.backlogItems.forEach(item => this.selectedIssues.add(item.id));
        this.updateBulkActionsBar();
        this.renderBacklog();
    }

    updateBulkActionsBar() {
        const bar = document.getElementById('bulkActionsBar');
        const count = document.getElementById('selectedCount');
        
        if (bar && count) {
            if (this.selectedIssues.size > 0) {
                bar.style.display = 'flex';
                count.textContent = this.selectedIssues.size;
            } else {
                bar.style.display = 'none';
            }
        }
    }

    toggleEstimationMode() {
        this.estimationMode = !this.estimationMode;
        const btn = document.getElementById('toggleEstimationMode');
        if (btn) {
            btn.classList.toggle('active', this.estimationMode);
            btn.innerHTML = this.estimationMode ? 
                '<i data-lucide="x"></i> Exit Estimation' : 
                '<i data-lucide="target"></i> Estimate';
        }
        this.renderBacklog();
        if (window.lucide) lucide.createIcons();
    }

    async updateEstimate(issueId, points) {
        const value = points ? parseInt(points) : null;
        
        try {
            const response = await fetch(`/api/issues/${issueId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ story_points: value })
            });

            if (response.ok) {
                // Update local data
                const item = this.backlogItems.find(i => i.id === issueId);
                if (item) item.story_points = value;
            }
        } catch (error) {
            console.error('Failed to update estimate:', error);
        }
    }

    setupDragAndDrop() {
        const items = document.querySelectorAll('.backlog-item');
        
        items.forEach(item => {
            item.addEventListener('dragstart', (e) => {
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/plain', item.dataset.issueId);
                item.classList.add('dragging');
            });

            item.addEventListener('dragend', (e) => {
                item.classList.remove('dragging');
            });

            item.addEventListener('dragover', (e) => {
                e.preventDefault();
                const dragging = document.querySelector('.dragging');
                if (dragging && dragging !== item) {
                    const rect = item.getBoundingClientRect();
                    const midpoint = rect.top + rect.height / 2;
                    
                    if (e.clientY < midpoint) {
                        item.parentNode.insertBefore(dragging, item);
                    } else {
                        item.parentNode.insertBefore(dragging, item.nextSibling);
                    }
                }
            });

            item.addEventListener('drop', (e) => {
                e.preventDefault();
                this.saveBacklogOrder();
            });
        });
    }

    async saveBacklogOrder() {
        const items = document.querySelectorAll('.backlog-item');
        const order = Array.from(items).map((item, index) => ({
            id: parseInt(item.dataset.issueId),
            rank: index
        }));

        try {
            const projectId = this.getCurrentProjectId();
            await fetch(`/api/projects/${projectId}/backlog/reorder`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ order })
            });
        } catch (error) {
            console.error('Failed to save backlog order:', error);
        }
    }

    async quickAddToSprint(issueId) {
        // Show sprint selector
        const sprints = await this.getActiveSprints();
        
        if (sprints.length === 0) {
            window.notificationManager?.addNotification({
                title: 'No Active Sprint',
                message: 'Create or start a sprint first',
                type: 'warning'
            });
            return;
        }

        // For now, add to first active sprint
        await this.addIssuesToSprint([issueId], sprints[0].id);
    }

    async bulkMoveToSprint() {
        if (this.selectedIssues.size === 0) return;

        const sprints = await this.getActiveSprints();
        if (sprints.length === 0) {
            window.notificationManager?.addNotification({
                title: 'No Active Sprint',
                message: 'Create or start a sprint first',
                type: 'warning'
            });
            return;
        }

        await this.addIssuesToSprint(Array.from(this.selectedIssues), sprints[0].id);
        this.selectedIssues.clear();
        this.updateBulkActionsBar();
    }

    async addIssuesToSprint(issueIds, sprintId) {
        try {
            const response = await fetch(`/api/sprints/${sprintId}/issues`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ issue_ids: issueIds })
            });

            if (response.ok) {
                window.notificationManager?.addNotification({
                    title: 'Issues Moved',
                    message: `${issueIds.length} issue(s) added to sprint`,
                    type: 'success'
                });
                await this.loadBacklog();
            }
        } catch (error) {
            console.error('Failed to add issues to sprint:', error);
        }
    }

    async getActiveSprints() {
        try {
            const projectId = this.getCurrentProjectId();
            const response = await fetch(`/api/projects/${projectId}/sprints?status=active,planned`);
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Failed to get sprints:', error);
        }
        return [];
    }

    // Utility methods
    getPriorityIcon(priority) {
        const icons = {
            'Highest': '<i data-lucide="alert-circle" class="priority-icon highest"></i>',
            'High': '<i data-lucide="arrow-up" class="priority-icon high"></i>',
            'Medium': '<i data-lucide="equal" class="priority-icon medium"></i>',
            'Low': '<i data-lucide="arrow-down" class="priority-icon low"></i>',
            'Lowest': '<i data-lucide="arrow-down" class="priority-icon lowest"></i>'
        };
        return icons[priority] || '';
    }

    comparePriority(a, b) {
        const order = { 'Highest': 0, 'High': 1, 'Medium': 2, 'Low': 3, 'Lowest': 4 };
        return (order[a] || 5) - (order[b] || 5);
    }

    getGroupColor(groupName) {
        const colors = [
            '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
            '#EC4899', '#06B6D4', '#84CC16', '#F97316', '#6366F1'
        ];
        const hash = groupName.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
        return colors[hash % colors.length];
    }

    getCurrentProjectId() {
        const match = window.location.pathname.match(/\/project\/(\d+)/);
        return match ? match[1] : window.currentProjectId;
    }

    isBacklogView() {
        return window.location.pathname.includes('/backlog');
    }

    openCreateIssueModal() {
        // Integrate with existing create issue functionality
        if (window.globalNav) {
            window.globalNav.openCreateIssue();
        }
    }

    openCreateEpicModal() {
        // Create epic modal (simplified)
        alert('Create Epic modal - to be implemented');
    }

    editEpic(epicName) {
        // Edit epic
        alert(`Edit epic: ${epicName}`);
    }

    async bulkSetPriority() {
        // Bulk priority change
        alert('Bulk set priority - to be implemented');
    }

    async bulkEstimate() {
        // Bulk estimation
        this.toggleEstimationMode();
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('backlogContainer')) {
        window.backlogView = new BacklogView();
    }
});
