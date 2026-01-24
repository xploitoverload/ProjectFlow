/**
 * Advanced Issue Fields System
 * All field types with inline editing, validation, and custom fields
 */

class AdvancedFieldsSystem {
    constructor() {
        this.currentIssue = null;
        this.editingField = null;
        this.customFields = [];
        this.users = [];
        this.assets = [];
        
        this.init();
    }

    async init() {
        await this.loadUsers();
        await this.loadCustomFields();
        console.log('AdvancedFieldsSystem initialized');
    }

    async loadUsers() {
        try {
            const response = await fetch('/api/users');
            this.users = await response.json();
        } catch (error) {
            this.loadMockUsers();
        }
    }

    loadMockUsers() {
        this.users = [
            { id: 1, name: 'John Doe', email: 'john@example.com', avatar: null },
            { id: 2, name: 'Jane Smith', email: 'jane@example.com', avatar: null },
            { id: 3, name: 'Bob Johnson', email: 'bob@example.com', avatar: null }
        ];
    }

    async loadCustomFields() {
        this.customFields = [
            { id: 1, name: 'Environment', type: 'select', options: ['Production', 'Staging', 'Development'] },
            { id: 2, name: 'Severity', type: 'select', options: ['Critical', 'High', 'Medium', 'Low'] },
            { id: 3, name: 'Story Points', type: 'number', validation: { min: 0, max: 100 } },
            { id: 4, name: 'Sprint', type: 'text' },
            { id: 5, name: 'Due Date', type: 'date' }
        ];
    }

    renderSummaryField(issue, container) {
        const html = `
            <div class="field-group summary-field">
                <div class="field-display" onclick="advancedFields.editSummary('${issue.key}')">
                    <h1 class="issue-summary">${issue.summary}</h1>
                    <i data-lucide="edit-2" class="field-edit-icon"></i>
                </div>
                <div class="field-editor" style="display: none;">
                    <input type="text" class="summary-input" value="${issue.summary}">
                    <div class="field-actions">
                        <button class="btn-primary btn-sm" onclick="advancedFields.saveSummary('${issue.key}')">
                            <i data-lucide="check"></i>
                        </button>
                        <button class="btn-secondary btn-sm" onclick="advancedFields.cancelEdit()">
                            <i data-lucide="x"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = html;
        if (window.lucide) lucide.createIcons();
    }

    renderDescriptionField(issue, container) {
        const html = `
            <div class="field-group description-field">
                <div class="field-header">
                    <label>Description</label>
                    ${issue.descriptionDraft ? '<span class="draft-indicator">Draft</span>' : ''}
                </div>
                <div class="field-display" onclick="advancedFields.editDescription('${issue.key}')">
                    <div class="description-content">
                        ${issue.description || '<span class="empty-value">Add a description...</span>'}
                    </div>
                </div>
                <div class="field-editor" style="display: none;">
                    <div class="wysiwyg-toolbar">
                        <button class="toolbar-btn" data-action="bold">
                            <i data-lucide="bold"></i>
                        </button>
                        <button class="toolbar-btn" data-action="italic">
                            <i data-lucide="italic"></i>
                        </button>
                        <button class="toolbar-btn" data-action="heading">
                            <i data-lucide="heading"></i>
                        </button>
                        <button class="toolbar-btn" data-action="list">
                            <i data-lucide="list"></i>
                        </button>
                        <button class="toolbar-btn" data-action="code">
                            <i data-lucide="code"></i>
                        </button>
                        <button class="toolbar-btn" data-action="link">
                            <i data-lucide="link"></i>
                        </button>
                        <button class="toolbar-btn" data-action="image">
                            <i data-lucide="image"></i>
                        </button>
                    </div>
                    <textarea class="description-textarea">${issue.description || ''}</textarea>
                    <div class="field-actions">
                        <button class="btn-primary" onclick="advancedFields.saveDescription('${issue.key}')">
                            Save
                        </button>
                        <button class="btn-secondary" onclick="advancedFields.cancelEdit()">
                            Cancel
                        </button>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = html;
        if (window.lucide) lucide.createIcons();
    }

    renderStatusField(issue, container) {
        const statuses = ['To Do', 'In Progress', 'In Review', 'Done'];
        const currentStatus = issue.status || 'To Do';
        
        const html = `
            <div class="field-group status-field">
                <label>Status</label>
                <div class="status-display" onclick="advancedFields.openStatusPicker('${issue.key}')">
                    <span class="status-badge status-${currentStatus.toLowerCase().replace(' ', '-')}">
                        ${currentStatus}
                    </span>
                    <i data-lucide="chevron-down"></i>
                </div>
                <div class="status-picker" style="display: none;">
                    <div class="status-workflow">
                        ${statuses.map(status => `
                            <div class="workflow-status" onclick="advancedFields.transitionStatus('${issue.key}', '${status}')">
                                <span class="status-badge status-${status.toLowerCase().replace(' ', '-')}">
                                    ${status}
                                </span>
                                <i data-lucide="arrow-right"></i>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = html;
        if (window.lucide) lucide.createIcons();
    }

    renderAssigneeField(issue, container) {
        const assignee = issue.assignee || null;
        
        const html = `
            <div class="field-group assignee-field">
                <label>Assignee</label>
                <div class="assignee-display" onclick="advancedFields.openUserPicker('${issue.key}', 'assignee')">
                    ${assignee ? `
                        <div class="user-avatar-with-name">
                            <div class="avatar-sm">${this.getInitials(assignee.name)}</div>
                            <span>${assignee.name}</span>
                        </div>
                    ` : `
                        <span class="empty-value">Unassigned</span>
                    `}
                    <i data-lucide="chevron-down"></i>
                </div>
                <div class="user-picker" style="display: none;">
                    <input type="text" class="user-search" placeholder="Search users..." 
                           oninput="advancedFields.searchUsers(this.value)">
                    <div class="user-list" id="userPickerList">
                        ${this.renderUserList()}
                    </div>
                    <div class="recent-users">
                        <label>Recent</label>
                        ${this.renderRecentUsers()}
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = html;
        if (window.lucide) lucide.createIcons();
    }

    renderPriorityField(issue, container) {
        const priorities = [
            { name: 'Highest', color: '#ff5630', icon: 'arrow-up' },
            { name: 'High', color: '#ff8b00', icon: 'arrow-up' },
            { name: 'Medium', color: '#ffab00', icon: 'minus' },
            { name: 'Low', color: '#36b37e', icon: 'arrow-down' },
            { name: 'Lowest', color: '#0065ff', icon: 'arrow-down' }
        ];
        
        const currentPriority = issue.priority || 'Medium';
        const priorityData = priorities.find(p => p.name === currentPriority);
        
        const html = `
            <div class="field-group priority-field">
                <label>Priority</label>
                <div class="priority-display" onclick="advancedFields.openPriorityPicker('${issue.key}')">
                    <div class="priority-badge">
                        <i data-lucide="${priorityData.icon}" style="color: ${priorityData.color}"></i>
                        <span>${currentPriority}</span>
                    </div>
                    <i data-lucide="chevron-down"></i>
                </div>
                <div class="priority-picker" style="display: none;">
                    ${priorities.map(priority => `
                        <div class="priority-option" onclick="advancedFields.setPriority('${issue.key}', '${priority.name}')">
                            <i data-lucide="${priority.icon}" style="color: ${priority.color}"></i>
                            <span>${priority.name}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        container.innerHTML = html;
        if (window.lucide) lucide.createIcons();
    }

    renderStoryPointsField(issue, container) {
        const html = `
            <div class="field-group number-field">
                <label>Story Points</label>
                <div class="field-display" onclick="advancedFields.editStoryPoints('${issue.key}')">
                    <span>${issue.storyPoints || '–'}</span>
                </div>
                <div class="field-editor" style="display: none;">
                    <input type="number" class="number-input" 
                           value="${issue.storyPoints || ''}" 
                           min="0" max="100" step="0.5">
                    <div class="field-actions">
                        <button class="btn-primary btn-sm" onclick="advancedFields.saveStoryPoints('${issue.key}')">
                            <i data-lucide="check"></i>
                        </button>
                        <button class="btn-secondary btn-sm" onclick="advancedFields.cancelEdit()">
                            <i data-lucide="x"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = html;
        if (window.lucide) lucide.createIcons();
    }

    renderTimeTrackingField(issue, container) {
        const html = `
            <div class="field-group time-tracking-field">
                <label>Time Tracking</label>
                <div class="time-tracking-display" onclick="advancedFields.openTimeTracker('${issue.key}')">
                    <div class="time-progress-bar">
                        <div class="time-progress" style="width: ${(issue.timeSpent / issue.timeEstimate) * 100}%"></div>
                    </div>
                    <div class="time-values">
                        <span>${issue.timeSpent || 0}h logged</span>
                        <span class="separator">/</span>
                        <span>${issue.timeEstimate || 0}h estimated</span>
                    </div>
                </div>
                <div class="time-tracker-modal" style="display: none;">
                    <input type="number" class="time-input" placeholder="Hours" step="0.5">
                    <textarea class="work-log-description" placeholder="What did you work on?"></textarea>
                    <button class="btn-primary" onclick="advancedFields.logTime('${issue.key}')">
                        Log Work
                    </button>
                </div>
            </div>
        `;

        container.innerHTML = html;
        if (window.lucide) lucide.createIcons();
    }

    renderCustomField(field, issue, container) {
        let html = '';
        const value = issue.customFields?.[field.id] || null;

        switch (field.type) {
            case 'text':
                html = `
                    <div class="field-group custom-field-text">
                        <label>${field.name}</label>
                        <input type="text" class="custom-field-input" 
                               value="${value || ''}"
                               onchange="advancedFields.saveCustomField('${issue.key}', ${field.id}, this.value)">
                    </div>
                `;
                break;
            
            case 'select':
                html = `
                    <div class="field-group custom-field-select">
                        <label>${field.name}</label>
                        <select class="custom-field-select" 
                                onchange="advancedFields.saveCustomField('${issue.key}', ${field.id}, this.value)">
                            <option value="">Select...</option>
                            ${field.options.map(opt => `
                                <option value="${opt}" ${value === opt ? 'selected' : ''}>${opt}</option>
                            `).join('')}
                        </select>
                    </div>
                `;
                break;
            
            case 'number':
                html = `
                    <div class="field-group custom-field-number">
                        <label>${field.name}</label>
                        <input type="number" class="custom-field-input" 
                               value="${value || ''}"
                               min="${field.validation?.min || 0}"
                               max="${field.validation?.max || ''}"
                               onchange="advancedFields.saveCustomField('${issue.key}', ${field.id}, this.value)">
                    </div>
                `;
                break;
            
            case 'date':
                html = `
                    <div class="field-group custom-field-date">
                        <label>${field.name}</label>
                        <input type="date" class="custom-field-input" 
                               value="${value || ''}"
                               onchange="advancedFields.saveCustomField('${issue.key}', ${field.id}, this.value)">
                    </div>
                `;
                break;
        }

        container.innerHTML = html;
    }

    renderAssetsField(issue, container) {
        const html = `
            <div class="field-group assets-field">
                <label>Assets</label>
                <div class="assets-list">
                    ${issue.assets?.map(asset => `
                        <div class="asset-item">
                            <i data-lucide="package"></i>
                            <span>${asset.name}</span>
                            <button class="btn-icon btn-sm" onclick="advancedFields.removeAsset('${issue.key}', ${asset.id})">
                                <i data-lucide="x"></i>
                            </button>
                        </div>
                    `).join('') || '<span class="empty-value">No assets linked</span>'}
                </div>
                <button class="btn-secondary btn-sm" onclick="advancedFields.linkAsset('${issue.key}')">
                    <i data-lucide="plus"></i>
                    Link Asset
                </button>
            </div>
        `;

        container.innerHTML = html;
        if (window.lucide) lucide.createIcons();
    }

    // Helper Methods
    renderUserList() {
        return this.users.map(user => `
            <div class="user-option" onclick="advancedFields.selectUser(${user.id})">
                <div class="avatar-sm">${this.getInitials(user.name)}</div>
                <div class="user-info">
                    <span class="user-name">${user.name}</span>
                    <span class="user-email">${user.email}</span>
                </div>
            </div>
        `).join('');
    }

    renderRecentUsers() {
        return this.users.slice(0, 3).map(user => `
            <div class="user-option" onclick="advancedFields.selectUser(${user.id})">
                <div class="avatar-sm">${this.getInitials(user.name)}</div>
                <span>${user.name}</span>
            </div>
        `).join('');
    }

    getInitials(name) {
        return name.split(' ').map(n => n[0]).join('').toUpperCase();
    }

    // Event Handlers (placeholders)
    editSummary(key) { console.log('Edit summary:', key); }
    saveSummary(key) { console.log('Save summary:', key); }
    editDescription(key) { console.log('Edit description:', key); }
    saveDescription(key) { console.log('Save description:', key); }
    openStatusPicker(key) { console.log('Open status picker:', key); }
    transitionStatus(key, status) { console.log('Transition to:', status); }
    openUserPicker(key, field) { console.log('Open user picker:', field); }
    openPriorityPicker(key) { console.log('Open priority picker:', key); }
    setPriority(key, priority) { console.log('Set priority:', priority); }
    editStoryPoints(key) { console.log('Edit story points:', key); }
    saveStoryPoints(key) { console.log('Save story points:', key); }
    openTimeTracker(key) { console.log('Open time tracker:', key); }
    logTime(key) { console.log('Log time:', key); }
    saveCustomField(key, fieldId, value) { console.log('Save custom field:', fieldId, value); }
    linkAsset(key) { console.log('Link asset:', key); }
    removeAsset(key, assetId) { console.log('Remove asset:', assetId); }
    searchUsers(query) { console.log('Search users:', query); }
    selectUser(userId) { console.log('Select user:', userId); }
    cancelEdit() { console.log('Cancel edit'); }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.advancedFields = new AdvancedFieldsSystem();
});
