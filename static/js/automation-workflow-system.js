/**
 * Automation & Workflows System
 * Rules builder, Visual workflow editor, Validators, Triggers/Conditions/Actions
 */

class AutomationWorkflowSystem {
    constructor() {
        this.activeTab = 'automation';
        
        this.automationRules = [
            { id: 'rule1', name: 'Auto-assign high priority bugs', enabled: true, executions: 156, trigger: 'Issue Created', conditions: ['type = Bug', 'priority = High'], actions: ['Assign to Team Lead'] },
            { id: 'rule2', name: 'Notify on SLA breach', enabled: true, executions: 23, trigger: 'SLA Breached', conditions: [], actions: ['Send email to manager'] },
            { id: 'rule3', name: 'Close old resolved issues', enabled: false, executions: 89, trigger: 'Scheduled', conditions: ['status = Resolved', 'resolved > 30d'], actions: ['Transition to Closed'] }
        ];
        
        this.triggers = [
            { id: 'issue-created', name: 'Issue created', category: 'Issue' },
            { id: 'issue-updated', name: 'Issue updated', category: 'Issue' },
            { id: 'issue-transitioned', name: 'Issue transitioned', category: 'Issue' },
            { id: 'comment-added', name: 'Comment added', category: 'Issue' },
            { id: 'field-changed', name: 'Field value changed', category: 'Issue' },
            { id: 'scheduled', name: 'Scheduled (cron)', category: 'Time' },
            { id: 'sla-breached', name: 'SLA breached', category: 'Service Desk' }
        ];
        
        this.actions = [
            { id: 'assign', name: 'Assign issue', category: 'Issue' },
            { id: 'transition', name: 'Transition issue', category: 'Issue' },
            { id: 'update-field', name: 'Update field value', category: 'Issue' },
            { id: 'add-comment', name: 'Add comment', category: 'Issue' },
            { id: 'send-email', name: 'Send email', category: 'Notifications' },
            { id: 'send-webhook', name: 'Send webhook', category: 'Integration' },
            { id: 'create-issue', name: 'Create linked issue', category: 'Issue' }
        ];
        
        this.workflows = [
            { id: 'wf1', name: 'Software Development Workflow', statuses: 6, transitions: 12, projects: 3 },
            { id: 'wf2', name: 'Bug Tracking Workflow', statuses: 5, transitions: 8, projects: 2 }
        ];
        
        this.init();
    }
    
    init() {
        console.log('Automation & Workflow System initialized');
    }
    
    render(container) {
        container.innerHTML = `
            <div class="automation-container">
                ${this.renderHeader()}
                ${this.renderTabs()}
                ${this.renderContent()}
            </div>
        `;
        
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }
    
    renderHeader() {
        return `
            <div class="automation-header">
                <h2>${this.activeTab === 'automation' ? 'Automation Rules' : 'Workflows'}</h2>
                <div class="header-actions">
                    ${this.activeTab === 'automation' ? `
                        <button class="btn btn-secondary" onclick="automationSystem.showTemplates()">
                            <i data-lucide="bookmark"></i>
                            Templates
                        </button>
                        <button class="btn btn-primary" onclick="automationSystem.createRule()">
                            <i data-lucide="plus"></i>
                            Create Rule
                        </button>
                    ` : `
                        <button class="btn btn-secondary" onclick="automationSystem.importWorkflow()">
                            <i data-lucide="upload"></i>
                            Import
                        </button>
                        <button class="btn btn-primary" onclick="automationSystem.createWorkflow()">
                            <i data-lucide="plus"></i>
                            Create Workflow
                        </button>
                    `}
                </div>
            </div>
        `;
    }
    
    renderTabs() {
        return `
            <div class="automation-tabs">
                <button class="tab ${this.activeTab === 'automation' ? 'active' : ''}" 
                    onclick="automationSystem.switchTab('automation')">
                    <i data-lucide="zap"></i>
                    Automation Rules
                </button>
                <button class="tab ${this.activeTab === 'workflows' ? 'active' : ''}" 
                    onclick="automationSystem.switchTab('workflows')">
                    <i data-lucide="git-branch"></i>
                    Workflows
                </button>
                <button class="tab ${this.activeTab === 'audit' ? 'active' : ''}" 
                    onclick="automationSystem.switchTab('audit')">
                    <i data-lucide="history"></i>
                    Audit Log
                </button>
            </div>
        `;
    }
    
    renderContent() {
        switch(this.activeTab) {
            case 'automation':
                return this.renderAutomationRules();
            case 'workflows':
                return this.renderWorkflows();
            case 'audit':
                return this.renderAuditLog();
            default:
                return '';
        }
    }
    
    renderAutomationRules() {
        return `
            <div class="automation-content">
                <div class="rules-list">
                    ${this.automationRules.map(rule => `
                        <div class="rule-card">
                            <div class="rule-header">
                                <div class="rule-status">
                                    <label class="toggle-switch">
                                        <input type="checkbox" ${rule.enabled ? 'checked' : ''} 
                                            onchange="automationSystem.toggleRule('${rule.id}', this.checked)" />
                                        <span class="toggle-slider"></span>
                                    </label>
                                </div>
                                <div class="rule-info">
                                    <h3>${rule.name}</h3>
                                    <span class="rule-executions">${rule.executions} executions</span>
                                </div>
                                <div class="rule-actions">
                                    <button class="btn-icon" onclick="automationSystem.editRule('${rule.id}')">
                                        <i data-lucide="edit-2"></i>
                                    </button>
                                    <button class="btn-icon" onclick="automationSystem.duplicateRule('${rule.id}')">
                                        <i data-lucide="copy"></i>
                                    </button>
                                    <button class="btn-icon" onclick="automationSystem.deleteRule('${rule.id}')">
                                        <i data-lucide="trash-2"></i>
                                    </button>
                                </div>
                            </div>
                            
                            <div class="rule-details">
                                <div class="rule-section">
                                    <span class="section-label">WHEN</span>
                                    <div class="section-content trigger">${rule.trigger}</div>
                                </div>
                                
                                ${rule.conditions.length > 0 ? `
                                    <div class="rule-section">
                                        <span class="section-label">IF</span>
                                        <div class="section-content conditions">
                                            ${rule.conditions.map(c => `<div class="condition">${c}</div>`).join('')}
                                        </div>
                                    </div>
                                ` : ''}
                                
                                <div class="rule-section">
                                    <span class="section-label">THEN</span>
                                    <div class="section-content actions">
                                        ${rule.actions.map(a => `<div class="action">${a}</div>`).join('')}
                                    </div>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                    
                    ${this.automationRules.length === 0 ? `
                        <div class="empty-state">
                            <i data-lucide="zap"></i>
                            <h4>No automation rules yet</h4>
                            <p>Create your first rule to automate repetitive tasks</p>
                            <button class="btn btn-primary" onclick="automationSystem.createRule()">
                                Create Rule
                            </button>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    renderWorkflows() {
        return `
            <div class="workflows-content">
                <div class="workflows-list">
                    ${this.workflows.map(wf => `
                        <div class="workflow-card">
                            <div class="workflow-header">
                                <h3>${wf.name}</h3>
                                <button class="btn-icon" onclick="automationSystem.workflowMenu('${wf.id}', this)">
                                    <i data-lucide="more-horizontal"></i>
                                </button>
                            </div>
                            <div class="workflow-stats">
                                <span>${wf.statuses} statuses</span>
                                <span>${wf.transitions} transitions</span>
                                <span>Used in ${wf.projects} projects</span>
                            </div>
                            <div class="workflow-actions">
                                <button class="btn btn-secondary-sm" onclick="automationSystem.editWorkflow('${wf.id}')">
                                    <i data-lucide="edit-2"></i>
                                    Edit
                                </button>
                                <button class="btn btn-secondary-sm" onclick="automationSystem.viewWorkflowDiagram('${wf.id}')">
                                    <i data-lucide="eye"></i>
                                    View Diagram
                                </button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    renderAuditLog() {
        const logs = [
            { timestamp: '2 hours ago', user: 'Admin', action: 'Enabled rule', detail: 'Auto-assign high priority bugs' },
            { timestamp: '1 day ago', user: 'John Doe', action: 'Created rule', detail: 'Notify on SLA breach' },
            { timestamp: '3 days ago', user: 'Jane Smith', action: 'Modified workflow', detail: 'Software Development Workflow' }
        ];
        
        return `
            <div class="audit-content">
                <div class="audit-filters">
                    <input type="text" placeholder="Search audit log..." />
                    <select>
                        <option>All actions</option>
                        <option>Rule changes</option>
                        <option>Workflow changes</option>
                    </select>
                    <select>
                        <option>All users</option>
                        <option>Admins only</option>
                    </select>
                </div>
                
                <div class="audit-log">
                    ${logs.map(log => `
                        <div class="audit-entry">
                            <div class="audit-time">${log.timestamp}</div>
                            <div class="audit-content">
                                <strong>${log.user}</strong> ${log.action}: ${log.detail}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    // Methods
    switchTab(tab) {
        this.activeTab = tab;
        const container = document.querySelector('.automation-container').parentElement;
        this.render(container);
    }
    
    createRule() {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal rule-builder-modal">
                <div class="modal-header">
                    <h3>Create Automation Rule</h3>
                    <button class="btn-icon" onclick="this.closest('.modal-overlay').remove()">
                        <i data-lucide="x"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="rule-builder">
                        <div class="builder-section">
                            <h4>WHEN (Trigger)</h4>
                            <select class="trigger-select">
                                <option value="">Select trigger...</option>
                                ${this.triggers.map(t => `<option value="${t.id}">${t.name}</option>`).join('')}
                            </select>
                        </div>
                        
                        <div class="builder-section">
                            <h4>IF (Conditions)</h4>
                            <div class="conditions-list">
                                <button class="btn btn-secondary-sm" onclick="automationSystem.addCondition()">
                                    <i data-lucide="plus"></i>
                                    Add Condition
                                </button>
                            </div>
                        </div>
                        
                        <div class="builder-section">
                            <h4>THEN (Actions)</h4>
                            <div class="actions-list">
                                <button class="btn btn-secondary-sm" onclick="automationSystem.addAction()">
                                    <i data-lucide="plus"></i>
                                    Add Action
                                </button>
                            </div>
                        </div>
                        
                        <div class="builder-section">
                            <h4>Rule Details</h4>
                            <input type="text" placeholder="Rule name" />
                            <textarea placeholder="Description (optional)" rows="2"></textarea>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                    <button class="btn btn-primary" onclick="automationSystem.saveRule(); this.closest('.modal-overlay').remove()">
                        Create Rule
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        if (typeof lucide !== 'undefined') lucide.createIcons();
    }
    
    viewWorkflowDiagram(workflowId) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal workflow-diagram-modal">
                <div class="modal-header">
                    <h3>Workflow Diagram</h3>
                    <button class="btn-icon" onclick="this.closest('.modal-overlay').remove()">
                        <i data-lucide="x"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="workflow-diagram">
                        ${this.renderWorkflowDiagram()}
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        if (typeof lucide !== 'undefined') lucide.createIcons();
    }
    
    renderWorkflowDiagram() {
        return `
            <div class="diagram-canvas">
                <div class="workflow-status" style="top: 50px; left: 100px;">
                    <div class="status-node">To Do</div>
                </div>
                <div class="workflow-status" style="top: 50px; left: 300px;">
                    <div class="status-node">In Progress</div>
                </div>
                <div class="workflow-status" style="top: 50px; left: 500px;">
                    <div class="status-node">Done</div>
                </div>
                
                <svg class="workflow-connections">
                    <line x1="190" y1="80" x2="290" y2="80" stroke="#0969da" stroke-width="2" />
                    <line x1="390" y1="80" x2="490" y2="80" stroke="#0969da" stroke-width="2" />
                </svg>
            </div>
        `;
    }
    
    showTemplates() {
        this.showToast('Automation rule templates');
    }
    
    toggleRule(ruleId, enabled) {
        const rule = this.automationRules.find(r => r.id === ruleId);
        if (rule) {
            rule.enabled = enabled;
            this.showToast(enabled ? 'Rule enabled' : 'Rule disabled');
        }
    }
    
    editRule(ruleId) {
        this.showToast('Edit rule ' + ruleId);
    }
    
    saveRule() {
        this.showToast('Rule created successfully');
    }
    
    showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;
        toast.style.cssText = 'position: fixed; bottom: 20px; right: 20px; background: #36b37e; color: white; padding: 12px 20px; border-radius: 6px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); z-index: 10000;';
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 2000);
    }
}

// Initialize
const automationSystem = new AutomationWorkflowSystem();
