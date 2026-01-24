/**
 * Advanced Reporting & Analytics System
 * Reports: Sprint, Velocity, Burndown, Cumulative Flow, Control Chart, 
 * Version, Time Tracking - All with export capabilities
 */

class ReportingSystem {
    constructor() {
        this.currentReport = null;
        this.reportData = {};
        this.charts = {};
        
        this.init();
    }

    async init() {
        await this.loadReportData();
        console.log('ReportingSystem initialized');
    }

    async loadReportData() {
        try {
            const response = await fetch('/api/reports/data');
            this.reportData = await response.json();
        } catch (error) {
            console.error('Failed to load report data:', error);
            this.loadMockData();
        }
    }

    loadMockData() {
        this.reportData = {
            sprints: [
                { id: 1, name: 'Sprint 1', completed: 45, committed: 50, velocity: 45 },
                { id: 2, name: 'Sprint 2', completed: 48, committed: 50, velocity: 48 },
                { id: 3, name: 'Sprint 3', completed: 52, committed: 55, velocity: 52 }
            ],
            burndown: [
                { day: 'Day 1', remaining: 50, ideal: 50 },
                { day: 'Day 2', remaining: 45, ideal: 45 },
                { day: 'Day 3', remaining: 38, ideal: 40 },
                { day: 'Day 4', remaining: 32, ideal: 35 },
                { day: 'Day 5', remaining: 25, ideal: 30 },
                { day: 'Day 6', remaining: 18, ideal: 25 },
                { day: 'Day 7', remaining: 12, ideal: 20 },
                { day: 'Day 8', remaining: 8, ideal: 15 },
                { day: 'Day 9', remaining: 3, ideal: 10 },
                { day: 'Day 10', remaining: 0, ideal: 5 }
            ],
            cumulativeFlow: [
                { date: 'Jan 1', todo: 30, inProgress: 10, done: 5 },
                { date: 'Jan 7', todo: 25, inProgress: 15, done: 15 },
                { date: 'Jan 14', todo: 20, inProgress: 12, done: 28 },
                { date: 'Jan 21', todo: 15, inProgress: 8, done: 40 }
            ],
            controlChart: [
                { issue: 'PROJ-1', cycleTime: 3.5 },
                { issue: 'PROJ-2', cycleTime: 5.2 },
                { issue: 'PROJ-3', cycleTime: 2.8 },
                { issue: 'PROJ-4', cycleTime: 4.1 },
                { issue: 'PROJ-5', cycleTime: 6.3 },
                { issue: 'PROJ-6', cycleTime: 3.9 },
                { issue: 'PROJ-7', cycleTime: 4.7 }
            ]
        };
    }

    openReport(type, container) {
        this.currentReport = type;
        
        switch (type) {
            case 'velocity':
                this.renderVelocityChart(container);
                break;
            case 'burndown':
                this.renderBurndownChart(container);
                break;
            case 'cumulative-flow':
                this.renderCumulativeFlowChart(container);
                break;
            case 'control':
                this.renderControlChart(container);
                break;
            case 'sprint':
                this.renderSprintReport(container);
                break;
            case 'version':
                this.renderVersionReport(container);
                break;
            case 'time-tracking':
                this.renderTimeTrackingReport(container);
                break;
            default:
                container.innerHTML = '<div class="empty-state">Select a report type</div>';
        }
    }

    renderVelocityChart(container) {
        const html = `
            <div class="report-container">
                <div class="report-header">
                    <div class="report-title">
                        <h2>Velocity Chart</h2>
                        <p>Track team velocity over sprints</p>
                    </div>
                    <div class="report-actions">
                        <button class="btn-secondary" onclick="reportingSystem.exportReport('velocity', 'pdf')">
                            <i data-lucide="download"></i>
                            Export PDF
                        </button>
                        <button class="btn-secondary" onclick="reportingSystem.exportReport('velocity', 'csv')">
                            <i data-lucide="file-text"></i>
                            Export CSV
                        </button>
                        <button class="btn-icon" onclick="reportingSystem.printReport()">
                            <i data-lucide="printer"></i>
                        </button>
                    </div>
                </div>

                <div class="report-filters">
                    <select class="filter-select">
                        <option>Last 6 sprints</option>
                        <option>Last 12 sprints</option>
                        <option>All sprints</option>
                    </select>
                </div>

                <div class="chart-container" id="velocityChart">
                    <canvas id="velocityChartCanvas"></canvas>
                </div>

                <div class="report-insights">
                    <div class="insight-card">
                        <h4>Average Velocity</h4>
                        <div class="insight-value">48.3 pts</div>
                        <div class="insight-trend trend-up">
                            <i data-lucide="trending-up"></i>
                            <span>+5.2% from last sprint</span>
                        </div>
                    </div>
                    <div class="insight-card">
                        <h4>Commitment Accuracy</h4>
                        <div class="insight-value">92%</div>
                        <div class="insight-trend trend-up">
                            <i data-lucide="check-circle"></i>
                            <span>Above target (90%)</span>
                        </div>
                    </div>
                    <div class="insight-card">
                        <h4>Velocity Stability</h4>
                        <div class="insight-value">High</div>
                        <div class="insight-description">
                            Low variance between sprints
                        </div>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = html;
        this.drawVelocityChart();
        if (window.lucide) lucide.createIcons();
    }

    renderBurndownChart(container) {
        const html = `
            <div class="report-container">
                <div class="report-header">
                    <div class="report-title">
                        <h2>Sprint Burndown Chart</h2>
                        <p>Monitor sprint progress</p>
                    </div>
                    <div class="report-actions">
                        <button class="btn-secondary" onclick="reportingSystem.exportReport('burndown', 'png')">
                            <i data-lucide="download"></i>
                            Export PNG
                        </button>
                    </div>
                </div>

                <div class="report-filters">
                    <select class="filter-select">
                        <option>Current Sprint</option>
                        <option>Sprint 2</option>
                        <option>Sprint 1</option>
                    </select>
                </div>

                <div class="chart-container" id="burndownChart">
                    <canvas id="burndownChartCanvas"></canvas>
                </div>

                <div class="report-insights">
                    <div class="insight-card">
                        <h4>Sprint Status</h4>
                        <div class="insight-value">On Track</div>
                        <div class="insight-trend trend-neutral">
                            <i data-lucide="activity"></i>
                            <span>3 days remaining</span>
                        </div>
                    </div>
                    <div class="insight-card">
                        <h4>Remaining Work</h4>
                        <div class="insight-value">12 pts</div>
                        <div class="insight-description">
                            24% of committed work
                        </div>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = html;
        this.drawBurndownChart();
        if (window.lucide) lucide.createIcons();
    }

    renderCumulativeFlowChart(container) {
        const html = `
            <div class="report-container">
                <div class="report-header">
                    <div class="report-title">
                        <h2>Cumulative Flow Diagram</h2>
                        <p>Identify workflow bottlenecks</p>
                    </div>
                    <div class="report-actions">
                        <button class="btn-secondary" onclick="reportingSystem.exportReport('cfd', 'pdf')">
                            <i data-lucide="download"></i>
                            Export
                        </button>
                    </div>
                </div>

                <div class="chart-container" id="cfdChart">
                    <canvas id="cfdChartCanvas"></canvas>
                </div>

                <div class="report-insights">
                    <div class="insight-card">
                        <h4>Work in Progress</h4>
                        <div class="insight-value">8 issues</div>
                        <div class="insight-trend trend-down">
                            <i data-lucide="trending-down"></i>
                            <span>Decreased from last week</span>
                        </div>
                    </div>
                    <div class="insight-card">
                        <h4>Throughput</h4>
                        <div class="insight-value">5.2/week</div>
                        <div class="insight-description">
                            Average completion rate
                        </div>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = html;
        this.drawCumulativeFlowChart();
        if (window.lucide) lucide.createIcons();
    }

    renderControlChart(container) {
        const html = `
            <div class="report-container">
                <div class="report-header">
                    <div class="report-title">
                        <h2>Control Chart</h2>
                        <p>Analyze cycle time and predictability</p>
                    </div>
                    <div class="report-actions">
                        <button class="btn-secondary" onclick="reportingSystem.exportReport('control', 'csv')">
                            <i data-lucide="download"></i>
                            Export
                        </button>
                    </div>
                </div>

                <div class="chart-container" id="controlChart">
                    <canvas id="controlChartCanvas"></canvas>
                </div>

                <div class="report-insights">
                    <div class="insight-card">
                        <h4>Average Cycle Time</h4>
                        <div class="insight-value">4.4 days</div>
                        <div class="insight-description">
                            Mean time to completion
                        </div>
                    </div>
                    <div class="insight-card">
                        <h4>Predictability</h4>
                        <div class="insight-value">85%</div>
                        <div class="insight-trend trend-up">
                            <i data-lucide="target"></i>
                            <span>High consistency</span>
                        </div>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = html;
        this.drawControlChart();
        if (window.lucide) lucide.createIcons();
    }

    renderSprintReport(container) {
        const html = `
            <div class="report-container">
                <div class="report-header">
                    <div class="report-title">
                        <h2>Sprint Report</h2>
                        <p>Comprehensive sprint analysis</p>
                    </div>
                    <div class="report-actions">
                        <button class="btn-secondary" onclick="reportingSystem.exportReport('sprint', 'pdf')">
                            <i data-lucide="download"></i>
                            Export
                        </button>
                    </div>
                </div>

                <div class="sprint-summary">
                    <div class="summary-stat">
                        <label>Committed</label>
                        <div class="stat-value">50 pts</div>
                    </div>
                    <div class="summary-stat">
                        <label>Completed</label>
                        <div class="stat-value">48 pts</div>
                    </div>
                    <div class="summary-stat">
                        <label>Not Completed</label>
                        <div class="stat-value">2 pts</div>
                    </div>
                    <div class="summary-stat">
                        <label>Completion</label>
                        <div class="stat-value">96%</div>
                    </div>
                </div>

                <div class="sprint-issues">
                    <h3>Completed Issues (24)</h3>
                    <div class="issue-list">
                        <div class="issue-item-compact">
                            <i data-lucide="check-circle"></i>
                            <span>PROJ-123 Implement authentication</span>
                            <span class="issue-points">5 pts</span>
                        </div>
                        <div class="issue-item-compact">
                            <i data-lucide="check-circle"></i>
                            <span>PROJ-124 Fix navigation bug</span>
                            <span class="issue-points">3 pts</span>
                        </div>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = html;
        if (window.lucide) lucide.createIcons();
    }

    renderVersionReport(container) {
        const html = `
            <div class="report-container">
                <div class="report-header">
                    <div class="report-title">
                        <h2>Version Report</h2>
                        <p>Track release progress</p>
                    </div>
                </div>

                <div class="version-progress">
                    <h3>Version 2.0</h3>
                    <div class="progress-stats">
                        <div class="stat">
                            <label>Total Issues</label>
                            <span>85</span>
                        </div>
                        <div class="stat">
                            <label>Resolved</label>
                            <span>72</span>
                        </div>
                        <div class="stat">
                            <label>In Progress</label>
                            <span>8</span>
                        </div>
                        <div class="stat">
                            <label>To Do</label>
                            <span>5</span>
                        </div>
                    </div>
                    <div class="progress-bar-large">
                        <div class="progress-segment done" style="width: 84.7%">
                            <span>84.7% Done</span>
                        </div>
                        <div class="progress-segment in-progress" style="width: 9.4%"></div>
                        <div class="progress-segment todo" style="width: 5.9%"></div>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = html;
        if (window.lucide) lucide.createIcons();
    }

    renderTimeTrackingReport(container) {
        const html = `
            <div class="report-container">
                <div class="report-header">
                    <div class="report-title">
                        <h2>Time Tracking Report</h2>
                        <p>Analyze time spent on issues</p>
                    </div>
                </div>

                <div class="time-summary">
                    <div class="time-stat">
                        <label>Total Logged</label>
                        <div class="stat-value">142h 30m</div>
                    </div>
                    <div class="time-stat">
                        <label>Estimated</label>
                        <div class="stat-value">160h</div>
                    </div>
                    <div class="time-stat">
                        <label>Remaining</label>
                        <div class="stat-value">17h 30m</div>
                    </div>
                </div>

                <div class="time-breakdown">
                    <h3>Time by Team Member</h3>
                    <div class="breakdown-list">
                        <div class="breakdown-item">
                            <div class="member-info">
                                <div class="avatar-sm">JD</div>
                                <span>John Doe</span>
                            </div>
                            <span class="time-value">48h 15m</span>
                        </div>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = html;
        if (window.lucide) lucide.createIcons();
    }

    // Chart Drawing (Simplified - would use Chart.js in production)
    drawVelocityChart() {
        const canvas = document.getElementById('velocityChartCanvas');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        canvas.width = canvas.offsetWidth;
        canvas.height = 300;
        
        // Simple bar chart visualization
        ctx.fillStyle = '#0052cc';
        const data = this.reportData.sprints;
        const barWidth = canvas.width / (data.length * 2);
        
        data.forEach((sprint, i) => {
            const x = i * barWidth * 2 + barWidth / 2;
            const height = (sprint.velocity / 60) * canvas.height;
            const y = canvas.height - height;
            
            ctx.fillRect(x, y, barWidth, height);
            
            // Labels
            ctx.fillStyle = '#666';
            ctx.font = '12px Arial';
            ctx.fillText(sprint.name, x, canvas.height - 10);
            ctx.fillStyle = '#0052cc';
        });
    }

    drawBurndownChart() {
        const canvas = document.getElementById('burndownChartCanvas');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        canvas.width = canvas.offsetWidth;
        canvas.height = 300;
        
        const data = this.reportData.burndown;
        const pointSpacing = canvas.width / (data.length - 1);
        
        // Ideal line
        ctx.strokeStyle = '#ccc';
        ctx.lineWidth = 2;
        ctx.setLineDash([5, 5]);
        ctx.beginPath();
        data.forEach((point, i) => {
            const x = i * pointSpacing;
            const y = canvas.height - (point.ideal / 50) * canvas.height;
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        });
        ctx.stroke();
        
        // Actual line
        ctx.strokeStyle = '#0052cc';
        ctx.setLineDash([]);
        ctx.beginPath();
        data.forEach((point, i) => {
            const x = i * pointSpacing;
            const y = canvas.height - (point.remaining / 50) * canvas.height;
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        });
        ctx.stroke();
    }

    drawCumulativeFlowChart() {
        const canvas = document.getElementById('cfdChartCanvas');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        canvas.width = canvas.offsetWidth;
        canvas.height = 300;
        
        // Stacked area chart (simplified)
        const data = this.reportData.cumulativeFlow;
        const pointSpacing = canvas.width / (data.length - 1);
        
        ['done', 'inProgress', 'todo'].forEach((status, idx) => {
            const colors = { done: '#36b37e', inProgress: '#0052cc', todo: '#97a0af' };
            ctx.fillStyle = colors[status];
            
            ctx.beginPath();
            ctx.moveTo(0, canvas.height);
            
            data.forEach((point, i) => {
                const x = i * pointSpacing;
                const total = point.todo + point.inProgress + (idx === 0 ? point.done : 0);
                const y = canvas.height - (total / 60) * canvas.height;
                ctx.lineTo(x, y);
            });
            
            ctx.lineTo(canvas.width, canvas.height);
            ctx.closePath();
            ctx.fill();
        });
    }

    drawControlChart() {
        const canvas = document.getElementById('controlChartCanvas');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        canvas.width = canvas.offsetWidth;
        canvas.height = 300;
        
        const data = this.reportData.controlChart;
        const pointSpacing = canvas.width / (data.length + 1);
        
        // Average line
        const avg = data.reduce((sum, d) => sum + d.cycleTime, 0) / data.length;
        ctx.strokeStyle = '#0052cc';
        ctx.lineWidth = 2;
        ctx.setLineDash([5, 5]);
        ctx.beginPath();
        ctx.moveTo(0, canvas.height - (avg / 10) * canvas.height);
        ctx.lineTo(canvas.width, canvas.height - (avg / 10) * canvas.height);
        ctx.stroke();
        
        // Data points
        ctx.setLineDash([]);
        ctx.fillStyle = '#0052cc';
        data.forEach((point, i) => {
            const x = (i + 1) * pointSpacing;
            const y = canvas.height - (point.cycleTime / 10) * canvas.height;
            
            ctx.beginPath();
            ctx.arc(x, y, 4, 0, 2 * Math.PI);
            ctx.fill();
        });
    }

    exportReport(type, format) {
        alert(`Exporting ${type} report as ${format.toUpperCase()}`);
    }

    printReport() {
        window.print();
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.reportingSystem = new ReportingSystem();
});
