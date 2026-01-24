/**
 * Agile Metrics System
 * Features: Cycle time, lead time, throughput, WIP limits, flow efficiency
 */

class AgileMetrics {
    constructor() {
        this.metrics = null;
        this.charts = {};
        this.timeRange = '30d';
        
        this.init();
    }

    init() {
        this.createModal();
        this.setupEventListeners();
    }

    createModal() {
        const modalHTML = `
            <div id="agileMetricsModal" class="metrics-modal" style="display: none;">
                <div class="metrics-modal-backdrop"></div>
                <div class="metrics-modal-container">
                    <div class="metrics-modal-header">
                        <h2>Agile Metrics</h2>
                        <div class="header-controls">
                            <select class="form-input" id="metricsTimeRange">
                                <option value="7d">Last 7 Days</option>
                                <option value="30d" selected>Last 30 Days</option>
                                <option value="90d">Last 90 Days</option>
                                <option value="custom">Custom Range</option>
                            </select>
                            <button class="btn btn-ghost btn-sm" id="refreshMetricsBtn">
                                <i data-lucide="refresh-cw"></i>
                                Refresh
                            </button>
                            <button class="btn-icon" id="closeMetricsModal">
                                <i data-lucide="x"></i>
                            </button>
                        </div>
                    </div>

                    <div class="metrics-modal-body">
                        <!-- Summary Cards -->
                        <div class="metrics-summary">
                            <div class="metric-card">
                                <div class="metric-icon cycle-time">
                                    <i data-lucide="clock"></i>
                                </div>
                                <div class="metric-content">
                                    <div class="metric-label">Avg Cycle Time</div>
                                    <div class="metric-value" id="avgCycleTime">--</div>
                                    <div class="metric-change" id="cycleTimeChange"></div>
                                </div>
                            </div>

                            <div class="metric-card">
                                <div class="metric-icon lead-time">
                                    <i data-lucide="timer"></i>
                                </div>
                                <div class="metric-content">
                                    <div class="metric-label">Avg Lead Time</div>
                                    <div class="metric-value" id="avgLeadTime">--</div>
                                    <div class="metric-change" id="leadTimeChange"></div>
                                </div>
                            </div>

                            <div class="metric-card">
                                <div class="metric-icon throughput">
                                    <i data-lucide="trending-up"></i>
                                </div>
                                <div class="metric-content">
                                    <div class="metric-label">Throughput</div>
                                    <div class="metric-value" id="throughput">--</div>
                                    <div class="metric-change" id="throughputChange"></div>
                                </div>
                            </div>

                            <div class="metric-card">
                                <div class="metric-icon efficiency">
                                    <i data-lucide="zap"></i>
                                </div>
                                <div class="metric-content">
                                    <div class="metric-label">Flow Efficiency</div>
                                    <div class="metric-value" id="flowEfficiency">--</div>
                                    <div class="metric-change" id="efficiencyChange"></div>
                                </div>
                            </div>
                        </div>

                        <!-- Charts Grid -->
                        <div class="metrics-grid">
                            <!-- Cycle Time Distribution -->
                            <div class="metric-chart-card">
                                <div class="chart-header">
                                    <h3>Cycle Time Distribution</h3>
                                    <button class="btn-icon-sm" title="Info">
                                        <i data-lucide="info"></i>
                                    </button>
                                </div>
                                <div class="chart-container">
                                    <canvas id="cycleTimeChart"></canvas>
                                </div>
                            </div>

                            <!-- Lead Time Trend -->
                            <div class="metric-chart-card">
                                <div class="chart-header">
                                    <h3>Lead Time Trend</h3>
                                    <button class="btn-icon-sm" title="Info">
                                        <i data-lucide="info"></i>
                                    </button>
                                </div>
                                <div class="chart-container">
                                    <canvas id="leadTimeChart"></canvas>
                                </div>
                            </div>

                            <!-- Throughput Chart -->
                            <div class="metric-chart-card">
                                <div class="chart-header">
                                    <h3>Weekly Throughput</h3>
                                    <button class="btn-icon-sm" title="Info">
                                        <i data-lucide="info"></i>
                                    </button>
                                </div>
                                <div class="chart-container">
                                    <canvas id="throughputChart"></canvas>
                                </div>
                            </div>

                            <!-- WIP Limits -->
                            <div class="metric-chart-card">
                                <div class="chart-header">
                                    <h3>Work In Progress</h3>
                                    <button class="btn btn-ghost btn-sm" id="configureWIPBtn">
                                        <i data-lucide="settings"></i>
                                        Configure Limits
                                    </button>
                                </div>
                                <div class="wip-status">
                                    <div class="wip-column">
                                        <div class="wip-header">
                                            <span class="wip-name">To Do</span>
                                            <span class="wip-count" id="wipTodo">0 / 10</span>
                                        </div>
                                        <div class="wip-bar">
                                            <div class="wip-fill" id="wipTodoBar" style="width: 0%;"></div>
                                        </div>
                                    </div>
                                    <div class="wip-column">
                                        <div class="wip-header">
                                            <span class="wip-name">In Progress</span>
                                            <span class="wip-count" id="wipInProgress">0 / 5</span>
                                        </div>
                                        <div class="wip-bar">
                                            <div class="wip-fill warning" id="wipInProgressBar" style="width: 0%;"></div>
                                        </div>
                                    </div>
                                    <div class="wip-column">
                                        <div class="wip-header">
                                            <span class="wip-name">Review</span>
                                            <span class="wip-count" id="wipReview">0 / 3</span>
                                        </div>
                                        <div class="wip-bar">
                                            <div class="wip-fill" id="wipReviewBar" style="width: 0%;"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Flow Efficiency -->
                            <div class="metric-chart-card full-width">
                                <div class="chart-header">
                                    <h3>Flow Efficiency Breakdown</h3>
                                    <button class="btn-icon-sm" title="Info">
                                        <i data-lucide="info"></i>
                                    </button>
                                </div>
                                <div class="efficiency-breakdown">
                                    <div class="efficiency-chart">
                                        <canvas id="efficiencyChart"></canvas>
                                    </div>
                                    <div class="efficiency-legend">
                                        <div class="legend-item">
                                            <div class="legend-color active-time"></div>
                                            <div class="legend-content">
                                                <div class="legend-label">Active Time</div>
                                                <div class="legend-value" id="activeTime">--</div>
                                            </div>
                                        </div>
                                        <div class="legend-item">
                                            <div class="legend-color wait-time"></div>
                                            <div class="legend-content">
                                                <div class="legend-label">Wait Time</div>
                                                <div class="legend-value" id="waitTime">--</div>
                                            </div>
                                        </div>
                                        <div class="legend-item">
                                            <div class="legend-color blocked-time"></div>
                                            <div class="legend-content">
                                                <div class="legend-label">Blocked Time</div>
                                                <div class="legend-value" id="blockedTime">--</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Control Chart -->
                            <div class="metric-chart-card full-width">
                                <div class="chart-header">
                                    <h3>Control Chart</h3>
                                    <button class="btn-icon-sm" title="Info">
                                        <i data-lucide="info"></i>
                                    </button>
                                </div>
                                <div class="chart-container">
                                    <canvas id="controlChart"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- WIP Configuration Dialog -->
            <div id="wipConfigDialog" class="metrics-dialog" style="display: none;">
                <div class="metrics-dialog-backdrop"></div>
                <div class="metrics-dialog-container">
                    <div class="metrics-dialog-header">
                        <h3>Configure WIP Limits</h3>
                        <button class="btn-icon-sm" onclick="agileMetrics.closeWIPConfig()">
                            <i data-lucide="x"></i>
                        </button>
                    </div>
                    <div class="metrics-dialog-body">
                        <p class="hint-text">Set maximum work items allowed in each status</p>
                        
                        <div class="wip-config-list" id="wipConfigList">
                            <!-- Populated by JS -->
                        </div>
                    </div>
                    <div class="metrics-dialog-footer">
                        <button class="btn btn-ghost" onclick="agileMetrics.closeWIPConfig()">Cancel</button>
                        <button class="btn btn-primary" id="saveWIPBtn">Save Limits</button>
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
        document.getElementById('closeMetricsModal')?.addEventListener('click', () => {
            this.closeModal();
        });

        document.getElementById('metricsTimeRange')?.addEventListener('change', (e) => {
            this.timeRange = e.target.value;
            this.loadMetrics();
        });

        document.getElementById('refreshMetricsBtn')?.addEventListener('click', () => {
            this.loadMetrics();
        });

        document.getElementById('configureWIPBtn')?.addEventListener('click', () => {
            this.openWIPConfig();
        });

        document.getElementById('saveWIPBtn')?.addEventListener('click', () => {
            this.saveWIPLimits();
        });
    }

    openModal() {
        document.getElementById('agileMetricsModal').style.display = 'block';
        this.loadMetrics();
    }

    closeModal() {
        document.getElementById('agileMetricsModal').style.display = 'none';
        this.destroyCharts();
    }

    async loadMetrics() {
        try {
            const response = await fetch(`/api/metrics/agile?range=${this.timeRange}`);
            if (response.ok) {
                this.metrics = await response.json();
                this.renderMetrics();
                this.renderCharts();
            }
        } catch (error) {
            console.error('Failed to load metrics:', error);
        }
    }

    renderMetrics() {
        // Cycle Time
        document.getElementById('avgCycleTime').textContent = 
            this.formatDuration(this.metrics.cycleTime.average);
        document.getElementById('cycleTimeChange').textContent = 
            this.formatChange(this.metrics.cycleTime.change);

        // Lead Time
        document.getElementById('avgLeadTime').textContent = 
            this.formatDuration(this.metrics.leadTime.average);
        document.getElementById('leadTimeChange').textContent = 
            this.formatChange(this.metrics.leadTime.change);

        // Throughput
        document.getElementById('throughput').textContent = 
            `${this.metrics.throughput.count} issues/week`;
        document.getElementById('throughputChange').textContent = 
            this.formatChange(this.metrics.throughput.change);

        // Flow Efficiency
        document.getElementById('flowEfficiency').textContent = 
            `${this.metrics.flowEfficiency.percentage}%`;
        document.getElementById('efficiencyChange').textContent = 
            this.formatChange(this.metrics.flowEfficiency.change);

        // WIP Status
        this.renderWIPStatus();

        // Efficiency Breakdown
        document.getElementById('activeTime').textContent = 
            this.formatDuration(this.metrics.flowEfficiency.activeTime);
        document.getElementById('waitTime').textContent = 
            this.formatDuration(this.metrics.flowEfficiency.waitTime);
        document.getElementById('blockedTime').textContent = 
            this.formatDuration(this.metrics.flowEfficiency.blockedTime);
    }

    renderWIPStatus() {
        const wip = this.metrics.wip || {
            todo: { current: 8, limit: 10 },
            inProgress: { current: 4, limit: 5 },
            review: { current: 2, limit: 3 }
        };

        // To Do
        const todoPercent = (wip.todo.current / wip.todo.limit) * 100;
        document.getElementById('wipTodo').textContent = `${wip.todo.current} / ${wip.todo.limit}`;
        document.getElementById('wipTodoBar').style.width = `${todoPercent}%`;

        // In Progress
        const progressPercent = (wip.inProgress.current / wip.inProgress.limit) * 100;
        document.getElementById('wipInProgress').textContent = `${wip.inProgress.current} / ${wip.inProgress.limit}`;
        document.getElementById('wipInProgressBar').style.width = `${progressPercent}%`;
        document.getElementById('wipInProgressBar').className = 
            `wip-fill ${progressPercent >= 80 ? 'danger' : progressPercent >= 60 ? 'warning' : ''}`;

        // Review
        const reviewPercent = (wip.review.current / wip.review.limit) * 100;
        document.getElementById('wipReview').textContent = `${wip.review.current} / ${wip.review.limit}`;
        document.getElementById('wipReviewBar').style.width = `${reviewPercent}%`;
    }

    renderCharts() {
        // Destroy existing charts
        this.destroyCharts();

        // Cycle Time Distribution
        this.charts.cycleTime = new Chart(
            document.getElementById('cycleTimeChart'),
            {
                type: 'bar',
                data: {
                    labels: ['0-2d', '2-4d', '4-6d', '6-8d', '8-10d', '10+d'],
                    datasets: [{
                        label: 'Issues',
                        data: this.metrics.cycleTime.distribution || [12, 18, 8, 5, 3, 2],
                        backgroundColor: '#3B82F6'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } }
                }
            }
        );

        // Lead Time Trend
        this.charts.leadTime = new Chart(
            document.getElementById('leadTimeChart'),
            {
                type: 'line',
                data: {
                    labels: this.metrics.leadTime.labels || ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                    datasets: [{
                        label: 'Lead Time',
                        data: this.metrics.leadTime.trend || [6.2, 5.8, 6.5, 5.4],
                        borderColor: '#10B981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } }
                }
            }
        );

        // Throughput
        this.charts.throughput = new Chart(
            document.getElementById('throughputChart'),
            {
                type: 'bar',
                data: {
                    labels: this.metrics.throughput.labels || ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                    datasets: [{
                        label: 'Completed Issues',
                        data: this.metrics.throughput.data || [14, 18, 16, 20],
                        backgroundColor: '#8B5CF6'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } }
                }
            }
        );

        // Flow Efficiency
        this.charts.efficiency = new Chart(
            document.getElementById('efficiencyChart'),
            {
                type: 'doughnut',
                data: {
                    labels: ['Active Time', 'Wait Time', 'Blocked Time'],
                    datasets: [{
                        data: [
                            this.metrics.flowEfficiency.activeTime || 120,
                            this.metrics.flowEfficiency.waitTime || 180,
                            this.metrics.flowEfficiency.blockedTime || 60
                        ],
                        backgroundColor: ['#10B981', '#F59E0B', '#EF4444']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } }
                }
            }
        );

        // Control Chart
        this.charts.control = new Chart(
            document.getElementById('controlChart'),
            {
                type: 'scatter',
                data: {
                    datasets: [{
                        label: 'Cycle Time',
                        data: this.metrics.controlChart || [
                            {x: 1, y: 5}, {x: 2, y: 6}, {x: 3, y: 4}, {x: 4, y: 7},
                            {x: 5, y: 5}, {x: 6, y: 6}, {x: 7, y: 5}, {x: 8, y: 8}
                        ],
                        backgroundColor: '#3B82F6'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } }
                }
            }
        );
    }

    destroyCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        this.charts = {};
    }

    formatDuration(hours) {
        if (!hours) return '--';
        if (hours < 24) return `${hours.toFixed(1)}h`;
        const days = (hours / 24).toFixed(1);
        return `${days}d`;
    }

    formatChange(change) {
        if (!change) return '';
        const arrow = change > 0 ? '↑' : '↓';
        const className = change > 0 ? 'negative' : 'positive';
        return `<span class="change ${className}">${arrow} ${Math.abs(change)}%</span>`;
    }

    openWIPConfig() {
        const container = document.getElementById('wipConfigList');
        const statuses = ['To Do', 'In Progress', 'Review', 'Testing', 'Done'];

        container.innerHTML = statuses.map(status => `
            <div class="wip-config-item">
                <label>${status}</label>
                <input type="number" class="form-input" data-status="${status}" 
                       value="${this.getWIPLimit(status)}" min="1" max="50">
            </div>
        `).join('');

        document.getElementById('wipConfigDialog').style.display = 'block';

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    closeWIPConfig() {
        document.getElementById('wipConfigDialog').style.display = 'none';
    }

    getWIPLimit(status) {
        const defaults = { 'To Do': 10, 'In Progress': 5, 'Review': 3, 'Testing': 4, 'Done': 999 };
        return this.metrics?.wipLimits?.[status] || defaults[status] || 10;
    }

    async saveWIPLimits() {
        const limits = {};
        document.querySelectorAll('#wipConfigList input').forEach(input => {
            limits[input.dataset.status] = parseInt(input.value);
        });

        try {
            const response = await fetch('/api/metrics/wip-limits', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(limits)
            });

            if (response.ok) {
                this.closeWIPConfig();
                this.loadMetrics();
            }
        } catch (error) {
            console.error('Failed to save WIP limits:', error);
        }
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.agileMetrics = new AgileMetrics();
});

// Global function to open metrics
function openAgileMetrics() {
    window.agileMetrics?.openModal();
}
