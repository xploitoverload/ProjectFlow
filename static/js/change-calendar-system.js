/**
 * Change Calendar & Risk Management System
 * Freeze periods, Risk assessment, Approval workflow, Impact analysis, Rollback, Conflict detection
 */

class ChangeCalendarSystem {
    constructor() {
        this.currentDate = new Date();
        this.viewMode = 'calendar'; // calendar, list, timeline
        
        this.changes = [
            { id: 'ch1', title: 'Database Migration', type: 'normal', date: new Date(2026, 0, 25), status: 'pending-approval', risk: 'high', impact: 'critical', owner: 'John Doe', affectedSystems: ['Database', 'API'] },
            { id: 'ch2', title: 'UI Update', type: 'standard', date: new Date(2026, 0, 28), status: 'approved', risk: 'low', impact: 'minor', owner: 'Jane Smith', affectedSystems: ['Frontend'] },
            { id: 'ch3', title: 'Emergency Security Patch', type: 'emergency', date: new Date(2026, 0, 24), status: 'implemented', risk: 'medium', impact: 'major', owner: 'Bob Johnson', affectedSystems: ['All Systems'] }
        ];
        
        this.freezePeriods = [
            { id: 'fp1', name: 'Year End Freeze', start: new Date(2025, 11, 20), end: new Date(2026, 0, 5), reason: 'Holiday freeze period' },
            { id: 'fp2', name: 'Quarter End Freeze', start: new Date(2026, 2, 28), end: new Date(2026, 3, 2), reason: 'Financial quarter end' }
        ];
        
        this.riskMatrix = [
            { probability: 'high', impact: 'critical', level: 'critical', color: '#cf222e' },
            { probability: 'high', impact: 'major', level: 'high', color: '#fb8500' },
            { probability: 'medium', impact: 'major', level: 'medium', color: '#fb8500' },
            { probability: 'low', impact: 'major', level: 'low', color: '#1a7f37' }
        ];
        
        this.approvalStages = [
            { id: 'stage1', name: 'Technical Review', approver: 'Tech Lead', required: true },
            { id: 'stage2', name: 'Security Review', approver: 'Security Team', required: true },
            { id: 'stage3', name: 'Change Manager Approval', approver: 'Change Manager', required: true }
        ];
        
        this.init();
    }
    
    init() {
        console.log('Change Calendar & Risk Management System initialized');
    }
    
    render(container) {
        container.innerHTML = `
            <div class="change-calendar-container">
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
            <div class="change-header">
                <h2>Change Calendar & Risk Management</h2>
                <div class="header-actions">
                    <button class="btn btn-secondary" onclick="changeCalendarSystem.manageFreezePeriods()">
                        <i data-lucide="snowflake"></i>
                        Freeze Periods
                    </button>
                    <button class="btn btn-secondary" onclick="changeCalendarSystem.viewRiskMatrix()">
                        <i data-lucide="alert-triangle"></i>
                        Risk Matrix
                    </button>
                    <button class="btn btn-primary" onclick="changeCalendarSystem.createChange()">
                        <i data-lucide="plus"></i>
                        Create Change
                    </button>
                </div>
            </div>
        `;
    }
    
    renderTabs() {
        return `
            <div class="change-tabs">
                <button class="tab ${this.viewMode === 'calendar' ? 'active' : ''}" 
                    onclick="changeCalendarSystem.setViewMode('calendar')">
                    <i data-lucide="calendar"></i>
                    Calendar View
                </button>
                <button class="tab ${this.viewMode === 'list' ? 'active' : ''}" 
                    onclick="changeCalendarSystem.setViewMode('list')">
                    <i data-lucide="list"></i>
                    List View
                </button>
                <button class="tab ${this.viewMode === 'timeline' ? 'active' : ''}" 
                    onclick="changeCalendarSystem.setViewMode('timeline')">
                    <i data-lucide="gantt-chart"></i>
                    Timeline
                </button>
            </div>
        `;
    }
    
    renderContent() {
        switch(this.viewMode) {
            case 'calendar':
                return this.renderCalendarView();
            case 'list':
                return this.renderListView();
            case 'timeline':
                return this.renderTimelineView();
            default:
                return '';
        }
    }
    
    renderCalendarView() {
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const startingDayOfWeek = firstDay.getDay();
        const monthLength = lastDay.getDate();
        
        let html = `
            <div class="change-calendar-view">
                <div class="calendar-nav">
                    <button class="btn-icon" onclick="changeCalendarSystem.previousMonth()">
                        <i data-lucide="chevron-left"></i>
                    </button>
                    <h3>${firstDay.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}</h3>
                    <button class="btn-icon" onclick="changeCalendarSystem.nextMonth()">
                        <i data-lucide="chevron-right"></i>
                    </button>
                </div>
                
                <div class="change-legend">
                    <span class="legend-item"><span class="legend-dot standard"></span>Standard</span>
                    <span class="legend-item"><span class="legend-dot normal"></span>Normal</span>
                    <span class="legend-item"><span class="legend-dot emergency"></span>Emergency</span>
                    <span class="legend-item"><span class="legend-dot freeze"></span>Freeze Period</span>
                </div>
                
                <div class="change-calendar-grid">
                    <div class="day-header">Sun</div>
                    <div class="day-header">Mon</div>
                    <div class="day-header">Tue</div>
                    <div class="day-header">Wed</div>
                    <div class="day-header">Thu</div>
                    <div class="day-header">Fri</div>
                    <div class="day-header">Sat</div>
        `;
        
        // Empty cells
        for (let i = 0; i < startingDayOfWeek; i++) {
            html += '<div class="change-day-cell empty"></div>';
        }
        
        // Days
        for (let day = 1; day <= monthLength; day++) {
            const date = new Date(year, month, day);
            const isToday = date.toDateString() === new Date().toDateString();
            const isFrozen = this.isDateFrozen(date);
            const changes = this.getChangesForDate(date);
            
            html += `
                <div class="change-day-cell ${isToday ? 'today' : ''} ${isFrozen ? 'frozen' : ''}" 
                    onclick="changeCalendarSystem.selectDate(new Date(${year}, ${month}, ${day}))">
                    <div class="day-number">${day}</div>
                    ${isFrozen ? '<div class="freeze-indicator"><i data-lucide="snowflake"></i></div>' : ''}
                    <div class="day-changes">
                        ${changes.map(change => `
                            <div class="change-indicator change-${change.type}" 
                                title="${change.title}"
                                onclick="event.stopPropagation(); changeCalendarSystem.viewChange('${change.id}')">
                                ${change.type === 'emergency' ? '⚡' : change.type === 'standard' ? '📋' : '🔧'}
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        html += `
                </div>
            </div>
        `;
        
        return html;
    }
    
    renderListView() {
        return `
            <div class="change-list-view">
                <div class="list-filters">
                    <select onchange="changeCalendarSystem.filterByStatus(this.value)">
                        <option value="">All Statuses</option>
                        <option value="pending-approval">Pending Approval</option>
                        <option value="approved">Approved</option>
                        <option value="implemented">Implemented</option>
                        <option value="rejected">Rejected</option>
                    </select>
                    <select onchange="changeCalendarSystem.filterByRisk(this.value)">
                        <option value="">All Risk Levels</option>
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                        <option value="critical">Critical</option>
                    </select>
                    <select onchange="changeCalendarSystem.filterByType(this.value)">
                        <option value="">All Types</option>
                        <option value="standard">Standard</option>
                        <option value="normal">Normal</option>
                        <option value="emergency">Emergency</option>
                    </select>
                </div>
                
                <div class="changes-list">
                    ${this.changes.map(change => this.renderChangeCard(change)).join('')}
                </div>
            </div>
        `;
    }
    
    renderChangeCard(change) {
        return `
            <div class="change-card" onclick="changeCalendarSystem.viewChange('${change.id}')">
                <div class="change-card-header">
                    <div class="change-type-badge change-${change.type}">${change.type}</div>
                    <div class="change-status-badge status-${change.status}">${change.status}</div>
                </div>
                <h3>${change.title}</h3>
                <div class="change-meta">
                    <span><i data-lucide="calendar"></i> ${change.date.toLocaleDateString()}</span>
                    <span><i data-lucide="user"></i> ${change.owner}</span>
                </div>
                <div class="change-risk">
                    <div class="risk-indicator risk-${change.risk}">
                        <i data-lucide="alert-triangle"></i>
                        Risk: ${change.risk}
                    </div>
                    <div class="impact-indicator impact-${change.impact}">
                        Impact: ${change.impact}
                    </div>
                </div>
                <div class="affected-systems">
                    ${change.affectedSystems.map(sys => `<span class="system-tag">${sys}</span>`).join('')}
                </div>
            </div>
        `;
    }
    
    renderTimelineView() {
        const sortedChanges = [...this.changes].sort((a, b) => a.date - b.date);
        
        return `
            <div class="change-timeline-view">
                <div class="timeline-container">
                    ${sortedChanges.map((change, idx) => `
                        <div class="timeline-item">
                            <div class="timeline-marker change-${change.type}"></div>
                            <div class="timeline-content">
                                <div class="timeline-date">${change.date.toLocaleDateString()}</div>
                                <div class="timeline-change">
                                    <h4>${change.title}</h4>
                                    <p>${change.owner} • ${change.type} change</p>
                                    <div class="timeline-meta">
                                        <span class="risk-badge risk-${change.risk}">${change.risk} risk</span>
                                        <span class="status-badge status-${change.status}">${change.status}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    // Helper methods
    getChangesForDate(date) {
        return this.changes.filter(change => change.date.toDateString() === date.toDateString());
    }
    
    isDateFrozen(date) {
        return this.freezePeriods.some(period => date >= period.start && date <= period.end);
    }
    
    // Actions
    setViewMode(mode) {
        this.viewMode = mode;
        const container = document.querySelector('.change-calendar-container').parentElement;
        this.render(container);
    }
    
    previousMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() - 1);
        const container = document.querySelector('.change-calendar-container').parentElement;
        this.render(container);
    }
    
    nextMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() + 1);
        const container = document.querySelector('.change-calendar-container').parentElement;
        this.render(container);
    }
    
    createChange() {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal change-modal">
                <div class="modal-header">
                    <h3>Create Change Request</h3>
                    <button class="btn-icon" onclick="this.closest('.modal-overlay').remove()">
                        <i data-lucide="x"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label>Change Title</label>
                        <input type="text" placeholder="Enter change title" />
                    </div>
                    <div class="form-group">
                        <label>Change Type</label>
                        <select>
                            <option value="standard">Standard</option>
                            <option value="normal">Normal</option>
                            <option value="emergency">Emergency</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Scheduled Date</label>
                        <input type="date" />
                    </div>
                    <div class="form-group">
                        <label>Description</label>
                        <textarea rows="4" placeholder="Describe the change"></textarea>
                    </div>
                    
                    <h4>Risk Assessment</h4>
                    <div class="risk-assessment">
                        <div class="form-group">
                            <label>Probability</label>
                            <select id="changeProbability">
                                <option value="low">Low</option>
                                <option value="medium">Medium</option>
                                <option value="high">High</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Impact</label>
                            <select id="changeImpact">
                                <option value="minor">Minor</option>
                                <option value="major">Major</option>
                                <option value="critical">Critical</option>
                            </select>
                        </div>
                    </div>
                    
                    <h4>Impact Analysis</h4>
                    <div class="form-group">
                        <label>Affected Systems</label>
                        <select multiple>
                            <option>Database</option>
                            <option>API</option>
                            <option>Frontend</option>
                            <option>Authentication</option>
                            <option>All Systems</option>
                        </select>
                    </div>
                    
                    <h4>Rollback Plan</h4>
                    <div class="form-group">
                        <textarea rows="3" placeholder="Describe rollback procedure"></textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                    <button class="btn btn-primary" onclick="changeCalendarSystem.saveChange(); this.closest('.modal-overlay').remove()">
                        Create Change
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        if (typeof lucide !== 'undefined') lucide.createIcons();
    }
    
    viewChange(changeId) {
        const change = this.changes.find(c => c.id === changeId);
        if (!change) return;
        
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal change-detail-modal">
                <div class="modal-header">
                    <h3>${change.title}</h3>
                    <button class="btn-icon" onclick="this.closest('.modal-overlay').remove()">
                        <i data-lucide="x"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="change-detail-section">
                        <h4>Change Details</h4>
                        <div class="detail-grid">
                            <div class="detail-item">
                                <span class="label">Type:</span>
                                <span class="value change-type-badge change-${change.type}">${change.type}</span>
                            </div>
                            <div class="detail-item">
                                <span class="label">Status:</span>
                                <span class="value status-badge status-${change.status}">${change.status}</span>
                            </div>
                            <div class="detail-item">
                                <span class="label">Scheduled:</span>
                                <span class="value">${change.date.toLocaleDateString()}</span>
                            </div>
                            <div class="detail-item">
                                <span class="label">Owner:</span>
                                <span class="value">${change.owner}</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="change-detail-section">
                        <h4>Risk Assessment</h4>
                        <div class="risk-matrix-display">
                            <div class="risk-level risk-${change.risk}">
                                <i data-lucide="alert-triangle"></i>
                                Risk Level: ${change.risk}
                            </div>
                            <div class="impact-level impact-${change.impact}">
                                Impact: ${change.impact}
                            </div>
                        </div>
                    </div>
                    
                    <div class="change-detail-section">
                        <h4>Approval Workflow</h4>
                        ${this.approvalStages.map(stage => `
                            <div class="approval-stage">
                                <div class="stage-icon ${stage.required ? 'required' : ''}">
                                    <i data-lucide="check-circle"></i>
                                </div>
                                <div class="stage-info">
                                    <div class="stage-name">${stage.name}</div>
                                    <div class="stage-approver">${stage.approver}</div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                    
                    <div class="change-detail-section">
                        <h4>Affected Systems</h4>
                        <div class="systems-list">
                            ${change.affectedSystems.map(sys => `<span class="system-tag">${sys}</span>`).join('')}
                        </div>
                    </div>
                    
                    <div class="change-detail-section">
                        <h4>Post-Implementation Review</h4>
                        <div class="review-checklist">
                            <label><input type="checkbox" /> Verify all systems operational</label>
                            <label><input type="checkbox" /> Check monitoring alerts</label>
                            <label><input type="checkbox" /> Validate user acceptance</label>
                            <label><input type="checkbox" /> Document lessons learned</label>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Close</button>
                    ${change.status === 'pending-approval' ? `
                        <button class="btn btn-danger" onclick="changeCalendarSystem.rejectChange('${change.id}')">Reject</button>
                        <button class="btn btn-primary" onclick="changeCalendarSystem.approveChange('${change.id}')">Approve</button>
                    ` : ''}
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        if (typeof lucide !== 'undefined') lucide.createIcons();
    }
    
    manageFreezePeriods() {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h3>Freeze Periods</h3>
                    <button class="btn-icon" onclick="this.closest('.modal-overlay').remove()">
                        <i data-lucide="x"></i>
                    </button>
                </div>
                <div class="modal-body">
                    ${this.freezePeriods.map(period => `
                        <div class="freeze-period-item">
                            <div class="freeze-icon"><i data-lucide="snowflake"></i></div>
                            <div class="freeze-info">
                                <h4>${period.name}</h4>
                                <p>${period.start.toLocaleDateString()} - ${period.end.toLocaleDateString()}</p>
                                <p class="freeze-reason">${period.reason}</p>
                            </div>
                            <button class="btn-icon-sm" onclick="changeCalendarSystem.deleteFreezeperiod('${period.id}')">
                                <i data-lucide="trash-2"></i>
                            </button>
                        </div>
                    `).join('')}
                    <button class="btn btn-link" onclick="changeCalendarSystem.addFreezePeriod()">
                        <i data-lucide="plus"></i>
                        Add Freeze Period
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        if (typeof lucide !== 'undefined') lucide.createIcons();
    }
    
    viewRiskMatrix() {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h3>Risk Assessment Matrix</h3>
                    <button class="btn-icon" onclick="this.closest('.modal-overlay').remove()">
                        <i data-lucide="x"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <table class="risk-matrix-table">
                        <thead>
                            <tr>
                                <th>Probability</th>
                                <th>Minor Impact</th>
                                <th>Major Impact</th>
                                <th>Critical Impact</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>High</td>
                                <td class="risk-cell risk-medium">Medium</td>
                                <td class="risk-cell risk-high">High</td>
                                <td class="risk-cell risk-critical">Critical</td>
                            </tr>
                            <tr>
                                <td>Medium</td>
                                <td class="risk-cell risk-low">Low</td>
                                <td class="risk-cell risk-medium">Medium</td>
                                <td class="risk-cell risk-high">High</td>
                            </tr>
                            <tr>
                                <td>Low</td>
                                <td class="risk-cell risk-low">Low</td>
                                <td class="risk-cell risk-low">Low</td>
                                <td class="risk-cell risk-medium">Medium</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        if (typeof lucide !== 'undefined') lucide.createIcons();
    }
    
    saveChange() {
        this.showToast('Change request created');
    }
    
    approveChange(changeId) {
        this.showToast('Change approved');
        document.querySelector('.modal-overlay').remove();
    }
    
    rejectChange(changeId) {
        this.showToast('Change rejected');
        document.querySelector('.modal-overlay').remove();
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
const changeCalendarSystem = new ChangeCalendarSystem();
