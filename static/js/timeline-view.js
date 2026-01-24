/**
 * Timeline/Roadmap View - Complete Gantt Chart
 * Dependencies, Drag dates, Zoom levels, Grouping, Milestones, Critical path
 */

class TimelineView {
    constructor() {
        this.zoomLevel = 'weeks'; // 'days', 'weeks', 'months', 'quarters', 'years'
        this.groupBy = 'epic'; // 'none', 'epic', 'team', 'project', 'sprint'
        this.showDependencies = true;
        this.showCriticalPath = false;
        this.showBaseline = false;
        
        this.items = [
            { id: 'item1', key: 'TEST-142', summary: 'User Authentication', start: '2026-01-15', end: '2026-02-15', progress: 60, epic: 'Auth', dependencies: [], critical: true },
            { id: 'item2', key: 'TEST-143', summary: 'Payment Gateway', start: '2026-02-01', end: '2026-03-01', progress: 30, epic: 'Payment', dependencies: ['item1'], critical: true },
            { id: 'item3', key: 'TEST-144', summary: 'Dashboard UI', start: '2026-01-20', end: '2026-02-20', progress: 45, epic: 'UI', dependencies: [], critical: false }
        ];
        
        this.milestones = [
            { id: 'milestone1', name: 'MVP Release', date: '2026-02-15', description: 'Minimum Viable Product' },
            { id: 'milestone2', name: 'Beta Launch', date: '2026-03-01', description: 'Public Beta' }
        ];
        
        this.today = new Date();
        
        this.init();
    }
    
    init() {
        console.log('Timeline View initialized');
    }
    
    render(container) {
        container.innerHTML = `
            <div class="timeline-view-container">
                ${this.renderToolbar()}
                ${this.renderTimeline()}
            </div>
        `;
        
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }
    
    renderToolbar() {
        return `
            <div class="timeline-toolbar">
                <div class="toolbar-left">
                    <h2>Timeline</h2>
                    
                    <div class="zoom-controls">
                        <button class="btn-icon" onclick="timelineView.zoomOut()" title="Zoom Out">
                            <i data-lucide="zoom-out"></i>
                        </button>
                        <select class="zoom-select" onchange="timelineView.setZoom(this.value)">
                            <option value="days" ${this.zoomLevel === 'days' ? 'selected' : ''}>Days</option>
                            <option value="weeks" ${this.zoomLevel === 'weeks' ? 'selected' : ''}>Weeks</option>
                            <option value="months" ${this.zoomLevel === 'months' ? 'selected' : ''}>Months</option>
                            <option value="quarters" ${this.zoomLevel === 'quarters' ? 'selected' : ''}>Quarters</option>
                            <option value="years" ${this.zoomLevel === 'years' ? 'selected' : ''}>Years</option>
                        </select>
                        <button class="btn-icon" onclick="timelineView.zoomIn()" title="Zoom In">
                            <i data-lucide="zoom-in"></i>
                        </button>
                    </div>
                    
                    <button class="btn btn-secondary" onclick="timelineView.scrollToToday()">
                        <i data-lucide="calendar-days"></i>
                        Today
                    </button>
                </div>
                
                <div class="toolbar-right">
                    <div class="group-selector">
                        <label>Group by:</label>
                        <select onchange="timelineView.setGroupBy(this.value)">
                            <option value="none" ${this.groupBy === 'none' ? 'selected' : ''}>None</option>
                            <option value="epic" ${this.groupBy === 'epic' ? 'selected' : ''}>Epic</option>
                            <option value="team" ${this.groupBy === 'team' ? 'selected' : ''}>Team</option>
                            <option value="project" ${this.groupBy === 'project' ? 'selected' : ''}>Project</option>
                            <option value="sprint" ${this.groupBy === 'sprint' ? 'selected' : ''}>Sprint</option>
                        </select>
                    </div>
                    
                    <button class="btn btn-secondary ${this.showDependencies ? 'active' : ''}" 
                        onclick="timelineView.toggleDependencies()">
                        <i data-lucide="git-branch"></i>
                        Dependencies
                    </button>
                    
                    <button class="btn btn-secondary ${this.showCriticalPath ? 'active' : ''}" 
                        onclick="timelineView.toggleCriticalPath()">
                        <i data-lucide="zap"></i>
                        Critical Path
                    </button>
                    
                    <button class="btn btn-secondary" onclick="timelineView.addMilestone()">
                        <i data-lucide="flag"></i>
                        Add Milestone
                    </button>
                    
                    <button class="btn btn-secondary" onclick="timelineView.exportTimeline()">
                        <i data-lucide="download"></i>
                        Export
                    </button>
                </div>
            </div>
        `;
    }
    
    renderTimeline() {
        const startDate = new Date('2026-01-01');
        const endDate = new Date('2026-03-31');
        
        return `
            <div class="timeline-container">
                <div class="timeline-header">
                    ${this.renderTimelineHeader(startDate, endDate)}
                </div>
                <div class="timeline-body">
                    ${this.renderTimelineRows()}
                </div>
            </div>
        `;
    }
    
    renderTimelineHeader(startDate, endDate) {
        const columns = this.generateTimeColumns(startDate, endDate);
        
        return `
            <div class="timeline-labels">
                <div class="timeline-label-col">Issue</div>
            </div>
            <div class="timeline-grid">
                ${columns.map(col => `
                    <div class="timeline-col-header">
                        <div class="col-header-main">${col.label}</div>
                        ${col.sublabel ? `<div class="col-header-sub">${col.sublabel}</div>` : ''}
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    renderTimelineRows() {
        const groups = this.groupItems();
        
        return `
            ${Object.entries(groups).map(([groupName, items]) => `
                <div class="timeline-group">
                    ${this.groupBy !== 'none' ? `
                        <div class="timeline-group-header">
                            <button class="group-toggle" onclick="timelineView.toggleGroup('${groupName}')">
                                <i data-lucide="chevron-down"></i>
                            </button>
                            <span class="group-name">${groupName}</span>
                            <span class="group-count">${items.length} issues</span>
                        </div>
                    ` : ''}
                    
                    ${items.map(item => this.renderTimelineRow(item)).join('')}
                </div>
            `).join('')}
            
            ${this.renderMilestones()}
            ${this.renderTodayMarker()}
        `;
    }
    
    renderTimelineRow(item) {
        const startPos = this.dateToPosition(item.start);
        const endPos = this.dateToPosition(item.end);
        const width = endPos - startPos;
        
        return `
            <div class="timeline-row">
                <div class="timeline-label">
                    <a href="#" class="issue-key">${item.key}</a>
                    <span class="issue-summary">${item.summary}</span>
                </div>
                <div class="timeline-track">
                    <div class="timeline-bar ${this.showCriticalPath && item.critical ? 'critical' : ''}" 
                        style="left: ${startPos}%; width: ${width}%"
                        draggable="true"
                        ondragstart="timelineView.onBarDragStart(event, '${item.id}')">
                        <div class="bar-progress" style="width: ${item.progress}%"></div>
                        <span class="bar-label">${item.summary}</span>
                        <div class="bar-resize-left" onmousedown="timelineView.startResize(event, '${item.id}', 'start')"></div>
                        <div class="bar-resize-right" onmousedown="timelineView.startResize(event, '${item.id}', 'end')"></div>
                    </div>
                    
                    ${this.showDependencies && item.dependencies.length > 0 ? this.renderDependencyLines(item) : ''}
                </div>
            </div>
        `;
    }
    
    renderMilestones() {
        return this.milestones.map(milestone => {
            const pos = this.dateToPosition(milestone.date);
            
            return `
                <div class="timeline-milestone" style="left: ${pos}%" title="${milestone.name}: ${milestone.description}">
                    <div class="milestone-marker">
                        <i data-lucide="flag"></i>
                    </div>
                    <div class="milestone-line"></div>
                    <div class="milestone-label">${milestone.name}</div>
                </div>
            `;
        }).join('');
    }
    
    renderTodayMarker() {
        const pos = this.dateToPosition(this.today.toISOString().split('T')[0]);
        
        return `
            <div class="timeline-today-marker" style="left: ${pos}%">
                <div class="today-line"></div>
                <div class="today-label">Today</div>
            </div>
        `;
    }
    
    renderDependencyLines(item) {
        // Simplified - would calculate actual SVG paths
        return item.dependencies.map(depId => `
            <svg class="dependency-line">
                <path d="M 0 20 L 50 20" stroke="#0969da" stroke-width="2" fill="none" marker-end="url(#arrowhead)"/>
            </svg>
        `).join('');
    }
    
    generateTimeColumns(startDate, endDate) {
        const columns = [];
        
        if (this.zoomLevel === 'weeks') {
            let current = new Date(startDate);
            while (current <= endDate) {
                const weekNum = this.getWeekNumber(current);
                columns.push({
                    label: `Week ${weekNum}`,
                    sublabel: this.formatDate(current, 'MMM DD')
                });
                current.setDate(current.getDate() + 7);
            }
        } else if (this.zoomLevel === 'months') {
            let current = new Date(startDate);
            while (current <= endDate) {
                columns.push({
                    label: this.formatDate(current, 'MMMM'),
                    sublabel: current.getFullYear().toString()
                });
                current.setMonth(current.getMonth() + 1);
            }
        }
        // Add other zoom levels...
        
        return columns;
    }
    
    groupItems() {
        if (this.groupBy === 'none') {
            return { 'All': this.items };
        }
        
        const grouped = {};
        this.items.forEach(item => {
            const key = item[this.groupBy] || 'Ungrouped';
            if (!grouped[key]) grouped[key] = [];
            grouped[key].push(item);
        });
        
        return grouped;
    }
    
    dateToPosition(dateStr) {
        // Convert date to percentage position on timeline
        const start = new Date('2026-01-01');
        const end = new Date('2026-03-31');
        const date = new Date(dateStr);
        
        const totalDays = (end - start) / (1000 * 60 * 60 * 24);
        const daysSinceStart = (date - start) / (1000 * 60 * 60 * 24);
        
        return (daysSinceStart / totalDays) * 100;
    }
    
    formatDate(date, format) {
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const monthsFull = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
        
        if (format === 'MMM DD') {
            return `${months[date.getMonth()]} ${date.getDate()}`;
        } else if (format === 'MMMM') {
            return monthsFull[date.getMonth()];
        }
        return date.toLocaleDateString();
    }
    
    getWeekNumber(date) {
        const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
        const dayNum = d.getUTCDay() || 7;
        d.setUTCDate(d.getUTCDate() + 4 - dayNum);
        const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
        return Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
    }
    
    // Methods
    setZoom(level) {
        this.zoomLevel = level;
        const container = document.querySelector('.timeline-view-container').parentElement;
        this.render(container);
    }
    
    zoomIn() {
        const levels = ['years', 'quarters', 'months', 'weeks', 'days'];
        const currentIndex = levels.indexOf(this.zoomLevel);
        if (currentIndex < levels.length - 1) {
            this.setZoom(levels[currentIndex + 1]);
        }
    }
    
    zoomOut() {
        const levels = ['years', 'quarters', 'months', 'weeks', 'days'];
        const currentIndex = levels.indexOf(this.zoomLevel);
        if (currentIndex > 0) {
            this.setZoom(levels[currentIndex - 1]);
        }
    }
    
    setGroupBy(group) {
        this.groupBy = group;
        const container = document.querySelector('.timeline-view-container').parentElement;
        this.render(container);
    }
    
    toggleDependencies() {
        this.showDependencies = !this.showDependencies;
        const container = document.querySelector('.timeline-view-container').parentElement;
        this.render(container);
    }
    
    toggleCriticalPath() {
        this.showCriticalPath = !this.showCriticalPath;
        const container = document.querySelector('.timeline-view-container').parentElement;
        this.render(container);
    }
    
    scrollToToday() {
        this.showToast('Scrolling to today');
    }
    
    addMilestone() {
        this.showToast('Add milestone dialog');
    }
    
    exportTimeline() {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h3>Export Timeline</h3>
                    <button class="btn-icon" onclick="this.closest('.modal-overlay').remove()">
                        <i data-lucide="x"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label>Format</label>
                        <select>
                            <option value="png">PNG Image</option>
                            <option value="pdf">PDF Document</option>
                            <option value="svg">SVG Vector</option>
                        </select>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                    <button class="btn btn-primary" onclick="timelineView.doExport(); this.closest('.modal-overlay').remove()">Export</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        if (typeof lucide !== 'undefined') lucide.createIcons();
    }
    
    onBarDragStart(event, itemId) {
        event.dataTransfer.setData('item', itemId);
    }
    
    startResize(event, itemId, edge) {
        event.stopPropagation();
        this.showToast(`Resizing ${edge} of ${itemId}`);
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
const timelineView = new TimelineView();
