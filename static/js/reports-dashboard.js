/**
 * Reports & Dashboards - JIRA-style analytics and metrics
 * Features: Burndown charts, velocity reports, cumulative flow, custom dashboards
 */

class ReportsDashboard {
    constructor() {
        this.dashboards = [];
        this.widgets = [];
        this.currentDashboard = null;
        this.editMode = false;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDashboards();
    }

    setupEventListeners() {
        // Dashboard selector
        document.getElementById('dashboardSelector')?.addEventListener('change', (e) => {
            this.switchDashboard(e.target.value);
        });

        // Edit mode toggle
        document.getElementById('editDashboardBtn')?.addEventListener('click', () => {
            this.toggleEditMode();
        });

        // Create dashboard
        document.getElementById('createDashboardBtn')?.addEventListener('click', () => {
            this.createDashboard();
        });

        // Add widget
        document.getElementById('addWidgetBtn')?.addEventListener('click', () => {
            this.openWidgetLibrary();
        });

        // Save dashboard
        document.getElementById('saveDashboardBtn')?.addEventListener('click', () => {
            this.saveDashboard();
        });
    }

    async loadDashboards() {
        try {
            const projectId = this.getCurrentProjectId();
            const response = await fetch(`/api/projects/${projectId}/dashboards`);
            if (response.ok) {
                this.dashboards = await response.json();
                
                if (this.dashboards.length > 0) {
                    this.currentDashboard = this.dashboards[0];
                    this.renderDashboard();
                } else {
                    this.renderEmptyState();
                }
            }
        } catch (error) {
            console.error('Failed to load dashboards:', error);
        }
    }

    renderDashboard() {
        const container = document.getElementById('dashboardGrid');
        if (!container || !this.currentDashboard) return;

        container.innerHTML = this.currentDashboard.widgets.map(widget => 
            this.renderWidget(widget)
        ).join('');

        // Initialize charts after rendering
        this.initializeCharts();

        if (this.editMode) {
            this.setupDragAndDrop();
        }
    }

    renderWidget(widget) {
        return `
            <div class="dashboard-widget" 
                 data-widget-id="${widget.id}"
                 data-widget-type="${widget.type}"
                 style="grid-column: span ${widget.width || 2}; grid-row: span ${widget.height || 2};">
                <div class="widget-header">
                    <h3 class="widget-title">${widget.title}</h3>
                    <div class="widget-actions">
                        ${this.editMode ? `
                            <button class="btn-icon-sm" onclick="window.reportsDashboard.configureWidget(${widget.id})">
                                <i data-lucide="settings"></i>
                            </button>
                            <button class="btn-icon-sm" onclick="window.reportsDashboard.removeWidget(${widget.id})">
                                <i data-lucide="x"></i>
                            </button>
                        ` : `
                            <button class="btn-icon-sm" onclick="window.reportsDashboard.refreshWidget(${widget.id})">
                                <i data-lucide="refresh-cw"></i>
                            </button>
                            <button class="btn-icon-sm" onclick="window.reportsDashboard.maximizeWidget(${widget.id})">
                                <i data-lucide="maximize-2"></i>
                            </button>
                        `}
                    </div>
                </div>
                <div class="widget-content" id="widget-${widget.id}">
                    ${this.getWidgetContent(widget)}
                </div>
            </div>
        `;
    }

    getWidgetContent(widget) {
        switch (widget.type) {
            case 'burndown':
                return `<canvas id="chart-burndown-${widget.id}"></canvas>`;
            case 'velocity':
                return `<canvas id="chart-velocity-${widget.id}"></canvas>`;
            case 'cumulative-flow':
                return `<canvas id="chart-cfd-${widget.id}"></canvas>`;
            case 'sprint-health':
                return this.renderSprintHealth(widget);
            case 'issue-statistics':
                return this.renderIssueStats(widget);
            case 'recent-activity':
                return this.renderRecentActivity(widget);
            case 'team-workload':
                return `<canvas id="chart-workload-${widget.id}"></canvas>`;
            default:
                return '<p>Widget type not supported</p>';
        }
    }

    renderSprintHealth(widget) {
        const data = widget.data || {};
        return `
            <div class="sprint-health-widget">
                <div class="health-metric">
                    <div class="metric-label">Sprint Progress</div>
                    <div class="progress-bar">
                        <div class="progress-bar-fill" style="width: ${data.progress || 0}%"></div>
                    </div>
                    <div class="metric-value">${data.progress || 0}%</div>
                </div>
                
                <div class="health-metrics-grid">
                    <div class="health-metric-card">
                        <div class="metric-icon" style="background: var(--color-green-light);">
                            <i data-lucide="check-circle"></i>
                        </div>
                        <div class="metric-info">
                            <div class="metric-value">${data.completed || 0}</div>
                            <div class="metric-label">Completed</div>
                        </div>
                    </div>
                    
                    <div class="health-metric-card">
                        <div class="metric-icon" style="background: var(--color-blue-light);">
                            <i data-lucide="loader"></i>
                        </div>
                        <div class="metric-info">
                            <div class="metric-value">${data.inProgress || 0}</div>
                            <div class="metric-label">In Progress</div>
                        </div>
                    </div>
                    
                    <div class="health-metric-card">
                        <div class="metric-icon" style="background: var(--color-gray-light);">
                            <i data-lucide="circle"></i>
                        </div>
                        <div class="metric-info">
                            <div class="metric-value">${data.todo || 0}</div>
                            <div class="metric-label">To Do</div>
                        </div>
                    </div>
                    
                    <div class="health-metric-card">
                        <div class="metric-icon" style="background: var(--color-red-light);">
                            <i data-lucide="alert-triangle"></i>
                        </div>
                        <div class="metric-info">
                            <div class="metric-value">${data.atRisk || 0}</div>
                            <div class="metric-label">At Risk</div>
                        </div>
                    </div>
                </div>

                <div class="health-summary">
                    <div class="summary-item">
                        <span class="summary-label">Days Remaining:</span>
                        <span class="summary-value">${data.daysRemaining || 0}</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">Velocity:</span>
                        <span class="summary-value">${data.velocity || 0} pts</span>
                    </div>
                </div>
            </div>
        `;
    }

    renderIssueStats(widget) {
        const data = widget.data || {};
        return `
            <div class="issue-stats-widget">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon" style="background: var(--color-blue-light);">
                            <i data-lucide="bookmark"></i>
                        </div>
                        <div class="stat-info">
                            <div class="stat-value">${data.total || 0}</div>
                            <div class="stat-label">Total Issues</div>
                        </div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon" style="background: var(--color-green-light);">
                            <i data-lucide="check-circle-2"></i>
                        </div>
                        <div class="stat-info">
                            <div class="stat-value">${data.resolved || 0}</div>
                            <div class="stat-label">Resolved</div>
                        </div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon" style="background: var(--color-red-light);">
                            <i data-lucide="bug"></i>
                        </div>
                        <div class="stat-info">
                            <div class="stat-value">${data.bugs || 0}</div>
                            <div class="stat-label">Bugs</div>
                        </div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon" style="background: var(--color-purple-light);">
                            <i data-lucide="zap"></i>
                        </div>
                        <div class="stat-info">
                            <div class="stat-value">${data.stories || 0}</div>
                            <div class="stat-label">Stories</div>
                        </div>
                    </div>
                </div>
                
                <div class="issue-breakdown">
                    <h4>By Status</h4>
                    <div class="breakdown-list">
                        ${Object.entries(data.byStatus || {}).map(([status, count]) => `
                            <div class="breakdown-item">
                                <span class="breakdown-label">${status}</span>
                                <span class="breakdown-value">${count}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    renderRecentActivity(widget) {
        const activities = widget.data?.activities || [];
        return `
            <div class="activity-widget">
                ${activities.length > 0 ? `
                    <div class="activity-list">
                        ${activities.map(activity => `
                            <div class="activity-item">
                                <div class="activity-icon ${activity.type}">
                                    <i data-lucide="${this.getActivityIcon(activity.type)}"></i>
                                </div>
                                <div class="activity-content">
                                    <div class="activity-text">${activity.text}</div>
                                    <div class="activity-time">${this.formatRelativeTime(activity.timestamp)}</div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                ` : `
                    <div class="widget-empty">
                        <i data-lucide="activity"></i>
                        <p>No recent activity</p>
                    </div>
                `}
            </div>
        `;
    }

    async initializeCharts() {
        if (!window.Chart) {
            console.warn('Chart.js not loaded');
            return;
        }

        // Initialize burndown charts
        document.querySelectorAll('[id^="chart-burndown-"]').forEach(async canvas => {
            const widgetId = canvas.id.split('-').pop();
            await this.renderBurndownChart(canvas, widgetId);
        });

        // Initialize velocity charts
        document.querySelectorAll('[id^="chart-velocity-"]').forEach(async canvas => {
            const widgetId = canvas.id.split('-').pop();
            await this.renderVelocityChart(canvas, widgetId);
        });

        // Initialize cumulative flow diagrams
        document.querySelectorAll('[id^="chart-cfd-"]').forEach(async canvas => {
            const widgetId = canvas.id.split('-').pop();
            await this.renderCumulativeFlowChart(canvas, widgetId);
        });

        // Initialize workload charts
        document.querySelectorAll('[id^="chart-workload-"]').forEach(async canvas => {
            const widgetId = canvas.id.split('-').pop();
            await this.renderWorkloadChart(canvas, widgetId);
        });

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    async renderBurndownChart(canvas, widgetId) {
        const data = await this.fetchChartData('burndown', widgetId);
        
        new Chart(canvas, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Ideal',
                        data: data.ideal,
                        borderColor: '#94A3B8',
                        borderDash: [5, 5],
                        fill: false,
                        tension: 0
                    },
                    {
                        label: 'Actual',
                        data: data.actual,
                        borderColor: '#3B82F6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Story Points'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Sprint Days'
                        }
                    }
                }
            }
        });
    }

    async renderVelocityChart(canvas, widgetId) {
        const data = await this.fetchChartData('velocity', widgetId);
        
        new Chart(canvas, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Committed',
                        data: data.committed,
                        backgroundColor: '#94A3B8'
                    },
                    {
                        label: 'Completed',
                        data: data.completed,
                        backgroundColor: '#10B981'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Story Points'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Sprint'
                        }
                    }
                }
            }
        });
    }

    async renderCumulativeFlowChart(canvas, widgetId) {
        const data = await this.fetchChartData('cumulative-flow', widgetId);
        
        new Chart(canvas, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Done',
                        data: data.done,
                        backgroundColor: '#10B981',
                        borderColor: '#10B981',
                        fill: true
                    },
                    {
                        label: 'In Progress',
                        data: data.inProgress,
                        backgroundColor: '#3B82F6',
                        borderColor: '#3B82F6',
                        fill: true
                    },
                    {
                        label: 'To Do',
                        data: data.todo,
                        backgroundColor: '#94A3B8',
                        borderColor: '#94A3B8',
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                },
                scales: {
                    y: {
                        stacked: true,
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Issue Count'
                        }
                    },
                    x: {
                        stacked: true,
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    }
                }
            }
        });
    }

    async renderWorkloadChart(canvas, widgetId) {
        const data = await this.fetchChartData('workload', widgetId);
        
        new Chart(canvas, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Assigned',
                        data: data.assigned,
                        backgroundColor: '#3B82F6'
                    },
                    {
                        label: 'Capacity',
                        data: data.capacity,
                        backgroundColor: '#E5E7EB',
                        type: 'line',
                        borderColor: '#6B7280',
                        borderDash: [5, 5]
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Story Points'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Team Member'
                        }
                    }
                }
            }
        });
    }

    async fetchChartData(chartType, widgetId) {
        try {
            const projectId = this.getCurrentProjectId();
            const response = await fetch(`/api/projects/${projectId}/reports/${chartType}`);
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error(`Failed to fetch ${chartType} data:`, error);
        }
        
        // Return mock data
        return this.getMockChartData(chartType);
    }

    getMockChartData(chartType) {
        switch (chartType) {
            case 'burndown':
                return {
                    labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7', 'Day 8', 'Day 9', 'Day 10'],
                    ideal: [100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 0],
                    actual: [100, 95, 85, 75, 70, 55, 45, 35, 25, 15]
                };
            case 'velocity':
                return {
                    labels: ['Sprint 1', 'Sprint 2', 'Sprint 3', 'Sprint 4', 'Sprint 5'],
                    committed: [45, 50, 48, 52, 50],
                    completed: [42, 48, 45, 50, 48]
                };
            case 'cumulative-flow':
                return {
                    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                    done: [5, 12, 20, 28],
                    inProgress: [8, 10, 12, 10],
                    todo: [35, 25, 15, 8]
                };
            case 'workload':
                return {
                    labels: ['Alice', 'Bob', 'Charlie', 'Diana'],
                    assigned: [25, 30, 20, 28],
                    capacity: [30, 30, 30, 30]
                };
            default:
                return {};
        }
    }

    renderEmptyState() {
        const container = document.getElementById('dashboardGrid');
        if (container) {
            container.innerHTML = `
                <div class="dashboard-empty">
                    <i data-lucide="layout-dashboard" style="width: 64px; height: 64px; margin-bottom: 16px;"></i>
                    <h3>No Dashboards Yet</h3>
                    <p>Create your first dashboard to visualize your project metrics.</p>
                    <button class="btn btn-primary" onclick="window.reportsDashboard.createDashboard()">
                        <i data-lucide="plus"></i>
                        Create Dashboard
                    </button>
                </div>
            `;
            if (window.lucide) lucide.createIcons();
        }
    }

    // Utility methods
    getActivityIcon(type) {
        const icons = {
            'created': 'plus-circle',
            'updated': 'edit-2',
            'completed': 'check-circle',
            'commented': 'message-square',
            'assigned': 'user-plus'
        };
        return icons[type] || 'activity';
    }

    formatRelativeTime(dateStr) {
        const date = new Date(dateStr);
        const now = new Date();
        const diff = now - date;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days > 0) return `${days}d ago`;
        if (hours > 0) return `${hours}h ago`;
        if (minutes > 0) return `${minutes}m ago`;
        return 'Just now';
    }

    getCurrentProjectId() {
        const match = window.location.pathname.match(/\/project\/(\d+)/);
        return match ? match[1] : window.currentProjectId;
    }

    toggleEditMode() {
        this.editMode = !this.editMode;
        this.renderDashboard();
    }

    createDashboard() {
        alert('Create Dashboard modal - to be implemented');
    }

    openWidgetLibrary() {
        alert('Widget Library modal - to be implemented');
    }

    saveDashboard() {
        alert('Save Dashboard - to be implemented');
    }

    configureWidget(widgetId) {
        alert(`Configure widget ${widgetId} - to be implemented`);
    }

    removeWidget(widgetId) {
        if (confirm('Remove this widget from the dashboard?')) {
            // Remove widget logic
        }
    }

    refreshWidget(widgetId) {
        // Refresh widget data
    }

    maximizeWidget(widgetId) {
        // Open widget in fullscreen
    }

    setupDragAndDrop() {
        // Drag and drop for widget reordering
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('dashboardGrid')) {
        window.reportsDashboard = new ReportsDashboard();
    }
});
