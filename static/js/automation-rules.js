/**
 * Automation Rules System
 * Visual rule builder with triggers, conditions, and actions
 */

class AutomationRules {
    constructor() {
        this.rules = [];
        this.selectedRule = null;
        this.editingRule = null;
        
        this.init();
    }

    init() {
        this.createModal();
        this.setupEventListeners();
    }

    getTriggers() {
        return [
            { id: 'issue_created', name: 'Issue Created', icon: 'plus-circle', description: 'When a new issue is created' },
            { id: 'issue_updated', name: 'Issue Updated', icon: 'edit', description: 'When an issue is updated' },
            { id: 'status_changed', name: 'Status Changed', icon: 'git-branch', description: 'When issue status changes' },
            { id: 'field_updated', name: 'Field Updated', icon: 'edit-3', description: 'When a specific field changes' },
            { id: 'comment_added', name: 'Comment Added', icon: 'message-square', description: 'When a comment is added' },
            { id: 'sprint_started', name: 'Sprint Started', icon: 'play-circle', description: 'When a sprint starts' },
            { id: 'sprint_completed', name: 'Sprint Completed', icon: 'check-circle', description: 'When a sprint completes' },
            { id: 'issue_assigned', name: 'Issue Assigned', icon: 'user-check', description: 'When an issue is assigned' }
        ];
    }

    getConditions() {
        return [
            { id: 'field_equals', name: 'Field Equals', params: ['field', 'value'] },
            { id: 'field_not_equals', name: 'Field Not Equals', params: ['field', 'value'] },
            { id: 'field_contains', name: 'Field Contains', params: ['field', 'value'] },
            { id: 'field_greater_than', name: 'Field Greater Than', params: ['field', 'value'] },
            { id: 'field_less_than', name: 'Field Less Than', params: ['field', 'value'] },
            { id: 'user_is', name: 'User Is', params: ['user'] },
            { id: 'user_is_in_role', name: 'User In Role', params: ['role'] },
            { id: 'issue_type_is', name: 'Issue Type Is', params: ['issueType'] },
            { id: 'priority_is', name: 'Priority Is', params: ['priority'] },
            { id: 'has_label', name: 'Has Label', params: ['label'] }
        ];
    }

    getActions() {
        return [
            { id: 'update_field', name: 'Update Field', icon: 'edit', params: ['field', 'value'] },
            { id: 'assign_issue', name: 'Assign Issue', icon: 'user-check', params: ['user'] },
            { id: 'transition_issue', name: 'Transition Issue', icon: 'git-branch', params: ['status'] },
            { id: 'send_notification', name: 'Send Notification', icon: 'bell', params: ['user', 'message'] },
            { id: 'create_subtask', name: 'Create Subtask', icon: 'plus-square', params: ['summary', 'description'] },
            { id: 'add_comment', name: 'Add Comment', icon: 'message-circle', params: ['comment'] },
            { id: 'add_label', name: 'Add Label', icon: 'tag', params: ['label'] },
            { id: 'remove_label', name: 'Remove Label', icon: 'x', params: ['label'] }
        ];
    }

    createModal() {
        const modalHTML = `
            <div id="automationModal" class="automation-modal" style="display: none;">
                <div class="automation-modal-backdrop"></div>
                <div class="automation-modal-container">
                    <div class="automation-modal-header">
                        <h2>Automation Rules</h2>
                        <div class="header-actions">
                            <button class="btn btn-primary btn-sm" id="createRuleBtn">
                                <i data-lucide="plus"></i>
                                Create Rule
                            </button>
                            <button class="btn-icon" id="closeAutomationModal">
                                <i data-lucide="x"></i>
                            </button>
                        </div>
                    </div>

                    <div class="automation-modal-body">
                        <!-- Rules List -->
                        <div class="rules-sidebar">
                            <div class="rules-search">
                                <input type="text" class="form-input" placeholder="Search rules..." id="rulesSearch">
                            </div>
                            <div class="rules-list" id="rulesList">
                                <!-- Populated by JS -->
                            </div>
                        </div>

                        <!-- Rule Editor -->
                        <div class="rule-editor" id="ruleEditor">
                            <div class="empty-state">
                                <i data-lucide="zap"></i>
                                <p>Select a rule to edit or create a new one</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Rule Dialog -->
            <div id="ruleDialog" class="automation-dialog" style="display: none;">
                <div class="automation-dialog-backdrop"></div>
                <div class="automation-dialog-container">
                    <div class="automation-dialog-header">
                        <h3 id="ruleDialogTitle">Create Rule</h3>
                        <button class="btn-icon-sm" onclick="automationRules.closeRuleDialog()">
                            <i data-lucide="x"></i>
                        </button>
                    </div>
                    <div class="automation-dialog-body">
                        <div class="form-group">
                            <label>Rule Name</label>
                            <input type="text" class="form-input" id="ruleName" placeholder="e.g., Auto-assign new bugs">
                        </div>
                        <div class="form-group">
                            <label>Description</label>
                            <textarea class="form-input" id="ruleDescription" rows="3" 
                                      placeholder="What does this rule do?"></textarea>
                        </div>
                        <div class="form-group">
                            <label>Status</label>
                            <div class="toggle-group">
                                <input type="checkbox" id="ruleEnabled" checked>
                                <label for="ruleEnabled">Enable this rule</label>
                            </div>
                        </div>
                    </div>
                    <div class="automation-dialog-footer">
                        <button class="btn btn-ghost" onclick="automationRules.closeRuleDialog()">Cancel</button>
                        <button class="btn btn-primary" id="saveRuleBtn">Continue to Rule Builder</button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    setupEventListeners() {
        document.getElementById('closeAutomationModal')?.addEventListener('click', () => {
            this.closeModal();
        });

        document.getElementById('createRuleBtn')?.addEventListener('click', () => {
            this.openRuleDialog();
        });

        document.getElementById('saveRuleBtn')?.addEventListener('click', () => {
            this.createRule();
        });

        document.getElementById('rulesSearch')?.addEventListener('input', (e) => {
            this.filterRules(e.target.value);
        });
    }

    openModal() {
        document.getElementById('automationModal').style.display = 'block';
        this.loadRules();
    }

    closeModal() {
        document.getElementById('automationModal').style.display = 'none';
    }

    async loadRules() {
        try {
            const response = await fetch('/api/automation/rules');
            if (response.ok) {
                this.rules = await response.json();
                this.renderRulesList();
            }
        } catch (error) {
            console.error('Failed to load rules:', error);
        }
    }

    renderRulesList() {
        const container = document.getElementById('rulesList');
        
        if (this.rules.length === 0) {
            container.innerHTML = `
                <div class="empty-sidebar">
                    <p>No automation rules yet</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.rules.map(rule => `
            <div class="rule-item ${this.selectedRule === rule.id ? 'active' : ''}" 
                 onclick="automationRules.selectRule('${rule.id}')">
                <div class="rule-status ${rule.enabled ? 'enabled' : 'disabled'}"></div>
                <div class="rule-info">
                    <div class="rule-name">${rule.name}</div>
                    <div class="rule-meta">
                        ${this.getTriggerName(rule.trigger)} → ${rule.actions?.length || 0} actions
                    </div>
                </div>
                <button class="btn-icon-sm" onclick="event.stopPropagation(); automationRules.toggleRule('${rule.id}')">
                    <i data-lucide="${rule.enabled ? 'toggle-right' : 'toggle-left'}"></i>
                </button>
            </div>
        `).join('');

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    selectRule(ruleId) {
        this.selectedRule = ruleId;
        this.renderRulesList();
        this.renderRuleEditor();
    }

    renderRuleEditor() {
        const rule = this.rules.find(r => r.id === this.selectedRule);
        if (!rule) return;

        const editorHTML = `
            <div class="rule-details">
                <div class="rule-header">
                    <div class="rule-title">
                        <h2>${rule.name}</h2>
                        <p class="rule-description">${rule.description || 'No description'}</p>
                    </div>
                    <div class="rule-actions">
                        <button class="btn btn-ghost btn-sm" onclick="automationRules.editRule('${rule.id}')">
                            <i data-lucide="edit"></i>
                            Edit
                        </button>
                        <button class="btn btn-ghost btn-sm" onclick="automationRules.duplicateRule('${rule.id}')">
                            <i data-lucide="copy"></i>
                            Duplicate
                        </button>
                        <button class="btn btn-ghost btn-sm" onclick="automationRules.deleteRule('${rule.id}')">
                            <i data-lucide="trash-2"></i>
                            Delete
                        </button>
                    </div>
                </div>

                <!-- Rule Builder -->
                <div class="rule-builder">
                    <!-- Trigger -->
                    <div class="builder-section">
                        <div class="section-label">
                            <i data-lucide="play"></i>
                            WHEN (Trigger)
                        </div>
                        <div class="builder-card trigger-card">
                            <div class="card-icon">
                                <i data-lucide="${this.getTriggerIcon(rule.trigger)}"></i>
                            </div>
                            <div class="card-content">
                                <div class="card-title">${this.getTriggerName(rule.trigger)}</div>
                                <div class="card-description">${this.getTriggerDescription(rule.trigger)}</div>
                            </div>
                            <button class="btn btn-ghost btn-sm" onclick="automationRules.editTrigger('${rule.id}')">
                                <i data-lucide="edit-2"></i>
                                Change
                            </button>
                        </div>
                    </div>

                    <!-- Conditions -->
                    <div class="builder-section">
                        <div class="section-label">
                            <i data-lucide="filter"></i>
                            IF (Conditions)
                        </div>
                        ${rule.conditions && rule.conditions.length > 0 ? rule.conditions.map((cond, index) => `
                            <div class="builder-card condition-card">
                                <div class="card-icon">
                                    <i data-lucide="check-circle"></i>
                                </div>
                                <div class="card-content">
                                    <div class="card-title">${this.getConditionName(cond.type)}</div>
                                    <div class="card-params">
                                        ${Object.entries(cond.params || {}).map(([key, val]) => 
                                            `<span class="param-badge">${key}: <strong>${val}</strong></span>`
                                        ).join(' ')}
                                    </div>
                                </div>
                                <button class="btn-icon-sm" onclick="automationRules.removeCondition('${rule.id}', ${index})">
                                    <i data-lucide="x"></i>
                                </button>
                            </div>
                        `).join('') : '<div class="empty-conditions">No conditions - rule will always execute</div>'}
                        <button class="btn btn-outline btn-sm" onclick="automationRules.addCondition('${rule.id}')">
                            <i data-lucide="plus"></i>
                            Add Condition
                        </button>
                    </div>

                    <!-- Actions -->
                    <div class="builder-section">
                        <div class="section-label">
                            <i data-lucide="zap"></i>
                            THEN (Actions)
                        </div>
                        ${rule.actions && rule.actions.length > 0 ? rule.actions.map((action, index) => `
                            <div class="builder-card action-card">
                                <div class="card-icon">
                                    <i data-lucide="${this.getActionIcon(action.type)}"></i>
                                </div>
                                <div class="card-content">
                                    <div class="card-title">${this.getActionName(action.type)}</div>
                                    <div class="card-params">
                                        ${Object.entries(action.params || {}).map(([key, val]) => 
                                            `<span class="param-badge">${key}: <strong>${val}</strong></span>`
                                        ).join(' ')}
                                    </div>
                                </div>
                                <button class="btn-icon-sm" onclick="automationRules.removeAction('${rule.id}', ${index})">
                                    <i data-lucide="x"></i>
                                </button>
                            </div>
                        `).join('') : '<div class="empty-actions">No actions defined</div>'}
                        <button class="btn btn-outline btn-sm" onclick="automationRules.addAction('${rule.id}')">
                            <i data-lucide="plus"></i>
                            Add Action
                        </button>
                    </div>
                </div>

                <!-- Execution Log -->
                <div class="execution-log">
                    <h3>Recent Executions</h3>
                    <div class="log-list">
                        ${rule.executions && rule.executions.length > 0 ? rule.executions.map(exec => `
                            <div class="log-item ${exec.success ? 'success' : 'failure'}">
                                <i data-lucide="${exec.success ? 'check-circle' : 'alert-circle'}"></i>
                                <div class="log-content">
                                    <div class="log-title">${exec.issue}</div>
                                    <div class="log-time">${this.formatTime(exec.timestamp)}</div>
                                </div>
                            </div>
                        `).join('') : '<div class="empty-log">No executions yet</div>'}
                    </div>
                </div>
            </div>
        `;

        document.getElementById('ruleEditor').innerHTML = editorHTML;

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    getTriggerName(triggerId) {
        const trigger = this.getTriggers().find(t => t.id === triggerId);
        return trigger?.name || triggerId;
    }

    getTriggerIcon(triggerId) {
        const trigger = this.getTriggers().find(t => t.id === triggerId);
        return trigger?.icon || 'circle';
    }

    getTriggerDescription(triggerId) {
        const trigger = this.getTriggers().find(t => t.id === triggerId);
        return trigger?.description || '';
    }

    getConditionName(conditionId) {
        const condition = this.getConditions().find(c => c.id === conditionId);
        return condition?.name || conditionId;
    }

    getActionName(actionId) {
        const action = this.getActions().find(a => a.id === actionId);
        return action?.name || actionId;
    }

    getActionIcon(actionId) {
        const action = this.getActions().find(a => a.id === actionId);
        return action?.icon || 'circle';
    }

    openRuleDialog(ruleId = null) {
        const dialog = document.getElementById('ruleDialog');
        const title = document.getElementById('ruleDialogTitle');
        
        if (ruleId) {
            const rule = this.rules.find(r => r.id === ruleId);
            title.textContent = 'Edit Rule';
            document.getElementById('ruleName').value = rule.name;
            document.getElementById('ruleDescription').value = rule.description || '';
            document.getElementById('ruleEnabled').checked = rule.enabled;
            this.editingRule = ruleId;
        } else {
            title.textContent = 'Create Rule';
            document.getElementById('ruleName').value = '';
            document.getElementById('ruleDescription').value = '';
            document.getElementById('ruleEnabled').checked = true;
            this.editingRule = null;
        }

        dialog.style.display = 'block';
        if (window.lucide) lucide.createIcons();
    }

    closeRuleDialog() {
        document.getElementById('ruleDialog').style.display = 'none';
        this.editingRule = null;
    }

    async createRule() {
        const name = document.getElementById('ruleName').value;
        const description = document.getElementById('ruleDescription').value;
        const enabled = document.getElementById('ruleEnabled').checked;

        if (!name) return;

        const newRule = {
            name,
            description,
            enabled,
            trigger: 'issue_created',
            conditions: [],
            actions: []
        };

        try {
            const response = await fetch('/api/automation/rules', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newRule)
            });

            if (response.ok) {
                const savedRule = await response.json();
                this.closeRuleDialog();
                this.loadRules();
                this.selectRule(savedRule.id);
            }
        } catch (error) {
            console.error('Failed to create rule:', error);
        }
    }

    editRule(ruleId) {
        this.openRuleDialog(ruleId);
    }

    async duplicateRule(ruleId) {
        const rule = this.rules.find(r => r.id === ruleId);
        if (!rule) return;

        const duplicatedRule = {
            ...rule,
            name: `${rule.name} (Copy)`,
            id: undefined
        };

        try {
            const response = await fetch('/api/automation/rules', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(duplicatedRule)
            });

            if (response.ok) {
                this.loadRules();
            }
        } catch (error) {
            console.error('Failed to duplicate rule:', error);
        }
    }

    async deleteRule(ruleId) {
        if (!confirm('Delete this automation rule? This cannot be undone.')) return;

        try {
            const response = await fetch(`/api/automation/rules/${ruleId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.selectedRule = null;
                this.loadRules();
                document.getElementById('ruleEditor').innerHTML = `
                    <div class="empty-state">
                        <i data-lucide="zap"></i>
                        <p>Select a rule to edit or create a new one</p>
                    </div>
                `;
                if (window.lucide) lucide.createIcons();
            }
        } catch (error) {
            console.error('Failed to delete rule:', error);
        }
    }

    async toggleRule(ruleId) {
        const rule = this.rules.find(r => r.id === ruleId);
        if (!rule) return;

        try {
            const response = await fetch(`/api/automation/rules/${ruleId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ enabled: !rule.enabled })
            });

            if (response.ok) {
                rule.enabled = !rule.enabled;
                this.renderRulesList();
            }
        } catch (error) {
            console.error('Failed to toggle rule:', error);
        }
    }

    addCondition(ruleId) {
        // Open condition selector dialog
        const conditions = this.getConditions();
        const html = `
            <div class="condition-selector">
                <h3>Add Condition</h3>
                <div class="condition-grid">
                    ${conditions.map(cond => `
                        <div class="condition-option" onclick="automationRules.selectCondition('${ruleId}', '${cond.id}')">
                            <div class="condition-name">${cond.name}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        // For now, just alert
        alert('Condition selector dialog would open here');
    }

    addAction(ruleId) {
        // Open action selector dialog
        alert('Action selector dialog would open here');
    }

    removeCondition(ruleId, index) {
        const rule = this.rules.find(r => r.id === ruleId);
        if (!rule) return;
        
        rule.conditions.splice(index, 1);
        this.renderRuleEditor();
    }

    removeAction(ruleId, index) {
        const rule = this.rules.find(r => r.id === ruleId);
        if (!rule) return;
        
        rule.actions.splice(index, 1);
        this.renderRuleEditor();
    }

    filterRules(query) {
        const filtered = this.rules.filter(r => 
            r.name.toLowerCase().includes(query.toLowerCase())
        );
        // Re-render with filtered rules
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
        return `${Math.floor(diff / 86400000)}d ago`;
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.automationRules = new AutomationRules();
});

// Global function
function openAutomationRules() {
    window.automationRules?.openModal();
}
