/**
 * Jira Ops/Alerts System
 * Incident management, alerts configuration, monitoring
 */

class JiraOpsSystem {
    constructor() {
        this.alerts = [
            {
                id: 1,
                name: 'High CPU Usage',
                description: 'Alert when CPU usage exceeds 80% for 5 minutes',
                status: 'active',
                severity: 'critical',
                type: 'incident',
                query: 'metric.cpu.usage > 80',
                lastTriggered: '2026-01-24 14:30',
                schedule: '*/5 * * * *',
                notificationChannels: ['email', 'slack'],
                recipients: ['ops-team@company.com', '#alerts-channel'],
                escalationRules: [
                    { level: 1, delay: 0, notify: ['ops-team@company.com'] },
                    { level: 2, delay: 15, notify: ['senior-ops@company.com'] }
                ],
                triggerCount: 24
            },
            {
                id: 2,
                name: 'API Response Time',
                description: 'Alert when API response time exceeds 500ms',
                status: 'active',
                severity: 'high',
                type: 'incident',
                query: 'metric.api.response_time > 500',
                lastTriggered: '2026-01-24 10:15',
                schedule: '*/1 * * * *',
                notificationChannels: ['email', 'pagerduty'],
                recipients: ['dev-team@company.com'],
                escalationRules: [
                    { level: 1, delay: 0, notify: ['dev-team@company.com'] }
                ],
                triggerCount: 12
            },
            {
                id: 3,
                name: 'Disk Space Low',
                description: 'Alert when disk space falls below 10%',
                status: 'paused',
                severity: 'medium',
                type: 'change',
                query: 'metric.disk.free_percent < 10',
                lastTriggered: '2026-01-20 08:45',
                schedule: '*/10 * * * *',
                notificationChannels: ['email'],
                recipients: ['infra-team@company.com'],
                escalationRules: [],
                triggerCount: 3
            },
            {
                id: 4,
                name: 'Failed Login Attempts',
                description: 'Alert on multiple failed login attempts',
                status: 'active',
                severity: 'high',
                type: 'incident',
                query: 'event.login.failed > 5 in 5m',
                lastTriggered: '2026-01-23 16:20',
                schedule: '*/5 * * * *',
                notificationChannels: ['email', 'slack'],
                recipients: ['security-team@company.com', '#security'],
                escalationRules: [
                    { level: 1, delay: 0, notify: ['security-team@company.com'] },
                    { level: 2, delay: 10, notify: ['security-lead@company.com'] }
                ],
                triggerCount: 8
            },
            {
                id: 5,
                name: 'Database Connection Pool',
                description: 'Alert when database connection pool is exhausted',
                status: 'active',
                severity: 'critical',
                type: 'problem',
                query: 'metric.db.connections.available == 0',
                lastTriggered: 'Never',
                schedule: '*/2 * * * *',
                notificationChannels: ['email', 'slack', 'pagerduty'],
                recipients: ['dba-team@company.com', '#database-alerts'],
                escalationRules: [
                    { level: 1, delay: 0, notify: ['dba-team@company.com'] },
                    { level: 2, delay: 5, notify: ['senior-dba@company.com'] },
                    { level: 3, delay: 15, notify: ['cto@company.com'] }
                ],
                triggerCount: 0
            }
        ];
        
        this.currentView = 'list'; // 'list' or 'detail'
        this.selectedAlert = null;
        this.filters = {
            status: 'all', // all, active, paused
            severity: 'all', // all, critical, high, medium, low
            type: 'all' // all, incident, change, problem
        };
        
        this.init();
    }
    
    init() {
        console.log('Jira Ops System initialized with', this.alerts.length, 'alerts');
    }
    
    renderOpsView(container) {
        container.innerHTML = `
            <div class="ops-container">
                <div class="ops-header">
                    <div class="ops-title">
                        <i data-lucide="alert-circle"></i>
                        <h2>Jira Ops - Alerts & Monitoring</h2>
                    </div>
                    <div class="ops-actions">
                        <button class="btn btn-secondary" onclick="jiraOps.toggleView()">
                            <i data-lucide="${this.currentView === 'list' ? 'layout-grid' : 'list'}"></i>
                            ${this.currentView === 'list' ? 'Detail View' : 'List View'}
                        </button>
                        <button class="btn btn-primary" onclick="jiraOps.createAlert()">
                            <i data-lucide="plus"></i>
                            Create Alert
                        </button>
                    </div>
                </div>
                
                ${this.currentView === 'list' ? this.renderListView() : this.renderDetailView()}
            </div>
        `;
        
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }
    
    renderListView() {
        return `
            <div class="ops-list-view">
                ${this.renderFiltersBar()}
                ${this.renderAlertsTable()}
            </div>
        `;
    }
    
    renderFiltersBar() {
        return `
            <div class="ops-filters-bar">
                <div class="filter-group">
                    <label>Status</label>
                    <select onchange="jiraOps.updateFilter('status', this.value)">
                        <option value="all" ${this.filters.status === 'all' ? 'selected' : ''}>All</option>
                        <option value="active" ${this.filters.status === 'active' ? 'selected' : ''}>Active</option>
                        <option value="paused" ${this.filters.status === 'paused' ? 'selected' : ''}>Paused</option>
                    </select>
                </div>
                
                <div class="filter-group">
                    <label>Severity</label>
                    <select onchange="jiraOps.updateFilter('severity', this.value)">
                        <option value="all" ${this.filters.severity === 'all' ? 'selected' : ''}>All</option>
                        <option value="critical" ${this.filters.severity === 'critical' ? 'selected' : ''}>Critical</option>
                        <option value="high" ${this.filters.severity === 'high' ? 'selected' : ''}>High</option>
                        <option value="medium" ${this.filters.severity === 'medium' ? 'selected' : ''}>Medium</option>
                        <option value="low" ${this.filters.severity === 'low' ? 'selected' : ''}>Low</option>
                    </select>
                </div>
                
                <div class="filter-group">
                    <label>Type</label>
                    <select onchange="jiraOps.updateFilter('type', this.value)">
                        <option value="all" ${this.filters.type === 'all' ? 'selected' : ''}>All</option>
                        <option value="incident" ${this.filters.type === 'incident' ? 'selected' : ''}>Incident</option>
                        <option value="change" ${this.filters.type === 'change' ? 'selected' : ''}>Change</option>
                        <option value="problem" ${this.filters.type === 'problem' ? 'selected' : ''}>Problem</option>
                    </select>
                </div>
            </div>
        `;
    }
    
    renderAlertsTable() {
        const filteredAlerts = this.getFilteredAlerts();
        
        return `
            <div class="ops-table-container">
                <table class="ops-table">
                    <thead>
                        <tr>
                            <th>Alert Name</th>
                            <th>Status</th>
                            <th>Severity</th>
                            <th>Type</th>
                            <th>Last Triggered</th>
                            <th>Trigger Count</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${filteredAlerts.map(alert => this.renderAlertRow(alert)).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }
    
    renderAlertRow(alert) {
        return `
            <tr class="alert-row" onclick="jiraOps.viewAlertDetail(${alert.id})">
                <td>
                    <div class="alert-name-cell">
                        <strong>${alert.name}</strong>
                        <div class="alert-description">${alert.description}</div>
                    </div>
                </td>
                <td>
                    <span class="status-badge status-${alert.status}">
                        <i data-lucide="${alert.status === 'active' ? 'play-circle' : 'pause-circle'}"></i>
                        ${alert.status}
                    </span>
                </td>
                <td>
                    <span class="severity-badge severity-${alert.severity}">
                        <span class="severity-dot"></span>
                        ${alert.severity}
                    </span>
                </td>
                <td>
                    <span class="type-badge">${alert.type}</span>
                </td>
                <td>${alert.lastTriggered}</td>
                <td>
                    <span class="trigger-count">${alert.triggerCount}</span>
                </td>
                <td class="actions-cell" onclick="event.stopPropagation()">
                    <button class="btn-icon" onclick="jiraOps.toggleAlertStatus(${alert.id})" title="${alert.status === 'active' ? 'Pause' : 'Resume'}">
                        <i data-lucide="${alert.status === 'active' ? 'pause' : 'play'}"></i>
                    </button>
                    <button class="btn-icon" onclick="jiraOps.editAlert(${alert.id})" title="Edit">
                        <i data-lucide="edit"></i>
                    </button>
                    <button class="btn-icon" onclick="jiraOps.deleteAlert(${alert.id})" title="Delete">
                        <i data-lucide="trash-2"></i>
                    </button>
                </td>
            </tr>
        `;
    }
    
    renderDetailView() {
        if (!this.selectedAlert) {
            this.selectedAlert = this.alerts[0];
        }
        
        return `
            <div class="ops-detail-view">
                <div class="alert-detail-header">
                    <div class="alert-detail-title">
                        <h3>${this.selectedAlert.name}</h3>
                        <span class="status-badge status-${this.selectedAlert.status}">
                            <i data-lucide="${this.selectedAlert.status === 'active' ? 'play-circle' : 'pause-circle'}"></i>
                            ${this.selectedAlert.status}
                        </span>
                        <span class="severity-badge severity-${this.selectedAlert.severity}">
                            <span class="severity-dot"></span>
                            ${this.selectedAlert.severity}
                        </span>
                    </div>
                    <div class="alert-detail-actions">
                        <button class="btn btn-secondary" onclick="jiraOps.toggleAlertStatus(${this.selectedAlert.id})">
                            <i data-lucide="${this.selectedAlert.status === 'active' ? 'pause' : 'play'}"></i>
                            ${this.selectedAlert.status === 'active' ? 'Pause' : 'Resume'}
                        </button>
                        <button class="btn btn-secondary" onclick="jiraOps.editAlert(${this.selectedAlert.id})">
                            <i data-lucide="edit"></i>
                            Edit
                        </button>
                        <button class="btn btn-danger" onclick="jiraOps.deleteAlert(${this.selectedAlert.id})">
                            <i data-lucide="trash-2"></i>
                            Delete
                        </button>
                    </div>
                </div>
                
                <div class="alert-detail-content">
                    ${this.renderAlertDetailTabs()}
                </div>
            </div>
        `;
    }
    
    renderAlertDetailTabs() {
        return `
            <div class="alert-tabs">
                <div class="alert-tab active" onclick="jiraOps.switchTab(event, 'configuration')">Configuration</div>
                <div class="alert-tab" onclick="jiraOps.switchTab(event, 'history')">History</div>
                <div class="alert-tab" onclick="jiraOps.switchTab(event, 'notifications')">Notifications</div>
            </div>
            
            <div class="alert-tab-content">
                <div class="tab-pane active" id="configuration">
                    ${this.renderConfigurationTab()}
                </div>
                <div class="tab-pane" id="history">
                    ${this.renderHistoryTab()}
                </div>
                <div class="tab-pane" id="notifications">
                    ${this.renderNotificationsTab()}
                </div>
            </div>
        `;
    }
    
    renderConfigurationTab() {
        return `
            <div class="config-section">
                <h4>Query Configuration</h4>
                <div class="query-editor">
                    <label>Alert Query</label>
                    <textarea class="query-input" rows="4">${this.selectedAlert.query}</textarea>
                    <div class="query-help">
                        Examples: <code>metric.cpu.usage > 80</code>, <code>event.error.count > 10 in 5m</code>
                    </div>
                </div>
            </div>
            
            <div class="config-section">
                <h4>Schedule Configuration</h4>
                <div class="schedule-config">
                    <label>Cron Expression</label>
                    <div class="schedule-input-group">
                        <input type="text" value="${this.selectedAlert.schedule}" placeholder="*/5 * * * *" />
                        <button class="btn btn-secondary" onclick="jiraOps.openSchedulePicker()">
                            <i data-lucide="calendar"></i>
                            Configure
                        </button>
                    </div>
                    <div class="schedule-help">
                        Current: Check every 5 minutes
                    </div>
                </div>
            </div>
            
            <div class="config-section">
                <h4>Notification Channels</h4>
                <div class="channels-config">
                    <div class="channel-option">
                        <input type="checkbox" id="channel-email" ${this.selectedAlert.notificationChannels.includes('email') ? 'checked' : ''} />
                        <label for="channel-email">
                            <i data-lucide="mail"></i>
                            Email
                        </label>
                    </div>
                    <div class="channel-option">
                        <input type="checkbox" id="channel-slack" ${this.selectedAlert.notificationChannels.includes('slack') ? 'checked' : ''} />
                        <label for="channel-slack">
                            <i data-lucide="hash"></i>
                            Slack
                        </label>
                    </div>
                    <div class="channel-option">
                        <input type="checkbox" id="channel-pagerduty" ${this.selectedAlert.notificationChannels.includes('pagerduty') ? 'checked' : ''} />
                        <label for="channel-pagerduty">
                            <i data-lucide="bell"></i>
                            PagerDuty
                        </label>
                    </div>
                </div>
            </div>
            
            <div class="config-section">
                <h4>Escalation Rules</h4>
                ${this.renderEscalationRules()}
            </div>
            
            <div class="config-actions">
                <button class="btn btn-primary" onclick="jiraOps.saveAlertConfig()">
                    <i data-lucide="save"></i>
                    Save Changes
                </button>
                <button class="btn btn-secondary" onclick="jiraOps.testAlert()">
                    <i data-lucide="play"></i>
                    Test Alert
                </button>
            </div>
        `;
    }
    
    renderEscalationRules() {
        if (this.selectedAlert.escalationRules.length === 0) {
            return `
                <div class="empty-escalation">
                    <p>No escalation rules configured</p>
                    <button class="btn btn-secondary" onclick="jiraOps.addEscalationRule()">
                        <i data-lucide="plus"></i>
                        Add Rule
                    </button>
                </div>
            `;
        }
        
        return `
            <div class="escalation-rules">
                ${this.selectedAlert.escalationRules.map((rule, index) => `
                    <div class="escalation-rule">
                        <div class="rule-header">
                            <span class="rule-level">Level ${rule.level}</span>
                            <button class="btn-icon" onclick="jiraOps.removeEscalationRule(${index})">
                                <i data-lucide="x"></i>
                            </button>
                        </div>
                        <div class="rule-config">
                            <div class="rule-field">
                                <label>Delay (minutes)</label>
                                <input type="number" value="${rule.delay}" min="0" />
                            </div>
                            <div class="rule-field">
                                <label>Notify</label>
                                <div class="recipients-list">
                                    ${rule.notify.map(recipient => `
                                        <span class="recipient-badge">
                                            ${recipient}
                                            <i data-lucide="x"></i>
                                        </span>
                                    `).join('')}
                                </div>
                                <button class="btn btn-sm" onclick="jiraOps.addRecipient(${index})">
                                    <i data-lucide="plus"></i>
                                    Add Recipient
                                </button>
                            </div>
                        </div>
                    </div>
                `).join('')}
                <button class="btn btn-secondary" onclick="jiraOps.addEscalationRule()">
                    <i data-lucide="plus"></i>
                    Add Another Level
                </button>
            </div>
        `;
    }
    
    renderHistoryTab() {
        // Mock trigger history
        const history = [
            { timestamp: '2026-01-24 14:30', status: 'triggered', message: 'CPU usage at 85%' },
            { timestamp: '2026-01-24 14:25', status: 'triggered', message: 'CPU usage at 82%' },
            { timestamp: '2026-01-24 14:20', status: 'resolved', message: 'CPU usage normalized' },
            { timestamp: '2026-01-24 14:15', status: 'triggered', message: 'CPU usage at 83%' },
            { timestamp: '2026-01-24 14:10', status: 'triggered', message: 'CPU usage at 81%' }
        ];
        
        return `
            <div class="alert-history">
                <div class="history-stats">
                    <div class="stat-card">
                        <div class="stat-value">24</div>
                        <div class="stat-label">Total Triggers</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">3</div>
                        <div class="stat-label">Active Incidents</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">21</div>
                        <div class="stat-label">Resolved</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">12m 30s</div>
                        <div class="stat-label">Avg Resolution Time</div>
                    </div>
                </div>
                
                <div class="history-timeline">
                    <h4>Recent Triggers</h4>
                    ${history.map(event => `
                        <div class="history-event">
                            <span class="event-status event-${event.status}">
                                <i data-lucide="${event.status === 'triggered' ? 'alert-triangle' : 'check-circle'}"></i>
                            </span>
                            <div class="event-details">
                                <div class="event-message">${event.message}</div>
                                <div class="event-timestamp">${event.timestamp}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    renderNotificationsTab() {
        return `
            <div class="notifications-config">
                <div class="config-section">
                    <h4>Email Recipients</h4>
                    <div class="recipients-list">
                        ${this.selectedAlert.recipients.filter(r => r.includes('@')).map(email => `
                            <div class="recipient-item">
                                <i data-lucide="mail"></i>
                                <span>${email}</span>
                                <button class="btn-icon">
                                    <i data-lucide="x"></i>
                                </button>
                            </div>
                        `).join('')}
                    </div>
                    <button class="btn btn-secondary" onclick="jiraOps.addEmailRecipient()">
                        <i data-lucide="plus"></i>
                        Add Email
                    </button>
                </div>
                
                <div class="config-section">
                    <h4>Slack Channels</h4>
                    <div class="recipients-list">
                        ${this.selectedAlert.recipients.filter(r => r.startsWith('#')).map(channel => `
                            <div class="recipient-item">
                                <i data-lucide="hash"></i>
                                <span>${channel}</span>
                                <button class="btn-icon">
                                    <i data-lucide="x"></i>
                                </button>
                            </div>
                        `).join('')}
                    </div>
                    <button class="btn btn-secondary" onclick="jiraOps.addSlackChannel()">
                        <i data-lucide="plus"></i>
                        Add Channel
                    </button>
                </div>
            </div>
        `;
    }
    
    getFilteredAlerts() {
        return this.alerts.filter(alert => {
            if (this.filters.status !== 'all' && alert.status !== this.filters.status) return false;
            if (this.filters.severity !== 'all' && alert.severity !== this.filters.severity) return false;
            if (this.filters.type !== 'all' && alert.type !== this.filters.type) return false;
            return true;
        });
    }
    
    updateFilter(filterType, value) {
        this.filters[filterType] = value;
        const container = document.querySelector('.ops-container').parentElement;
        this.renderOpsView(container);
    }
    
    toggleView() {
        this.currentView = this.currentView === 'list' ? 'detail' : 'list';
        const container = document.querySelector('.ops-container').parentElement;
        this.renderOpsView(container);
    }
    
    viewAlertDetail(alertId) {
        this.selectedAlert = this.alerts.find(a => a.id === alertId);
        this.currentView = 'detail';
        const container = document.querySelector('.ops-container').parentElement;
        this.renderOpsView(container);
    }
    
    toggleAlertStatus(alertId) {
        const alert = this.alerts.find(a => a.id === alertId);
        if (alert) {
            alert.status = alert.status === 'active' ? 'paused' : 'active';
            const container = document.querySelector('.ops-container').parentElement;
            this.renderOpsView(container);
            this.showToast(`Alert ${alert.status === 'active' ? 'resumed' : 'paused'}`);
        }
    }
    
    createAlert() {
        alert('Create Alert modal would open here');
    }
    
    editAlert(alertId) {
        alert(`Edit Alert ${alertId} modal would open here`);
    }
    
    deleteAlert(alertId) {
        if (confirm('Are you sure you want to delete this alert?')) {
            this.alerts = this.alerts.filter(a => a.id !== alertId);
            const container = document.querySelector('.ops-container').parentElement;
            this.renderOpsView(container);
            this.showToast('Alert deleted');
        }
    }
    
    switchTab(event, tabName) {
        // Remove active class from all tabs
        document.querySelectorAll('.alert-tab').forEach(tab => tab.classList.remove('active'));
        document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
        
        // Add active class to clicked tab
        event.target.classList.add('active');
        document.getElementById(tabName).classList.add('active');
    }
    
    saveAlertConfig() {
        this.showToast('Alert configuration saved');
    }
    
    testAlert() {
        this.showToast('Test alert sent');
    }
    
    openSchedulePicker() {
        alert('Schedule picker would open here');
    }
    
    addEscalationRule() {
        alert('Add escalation rule modal would open here');
    }
    
    removeEscalationRule(index) {
        if (confirm('Remove this escalation rule?')) {
            this.selectedAlert.escalationRules.splice(index, 1);
            const container = document.querySelector('.ops-container').parentElement;
            this.renderOpsView(container);
        }
    }
    
    addRecipient(ruleIndex) {
        alert(`Add recipient to rule ${ruleIndex} modal would open here`);
    }
    
    addEmailRecipient() {
        const email = prompt('Enter email address:');
        if (email && email.includes('@')) {
            this.selectedAlert.recipients.push(email);
            const container = document.querySelector('.ops-container').parentElement;
            this.renderOpsView(container);
        }
    }
    
    addSlackChannel() {
        const channel = prompt('Enter Slack channel name:');
        if (channel) {
            this.selectedAlert.recipients.push(channel.startsWith('#') ? channel : `#${channel}`);
            const container = document.querySelector('.ops-container').parentElement;
            this.renderOpsView(container);
        }
    }
    
    showToast(message) {
        // Simple toast notification
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;
        toast.style.cssText = 'position: fixed; bottom: 20px; right: 20px; background: #36b37e; color: white; padding: 12px 20px; border-radius: 6px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); z-index: 10000;';
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }
}

// Initialize
const jiraOps = new JiraOpsSystem();
