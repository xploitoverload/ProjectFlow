// timeline.js - Enhanced JIRA-style Timeline/Roadmap with Zoom, Swimlanes & Dependencies

class TimelineChart {
    constructor() {
        this.draggedBar = null;
        this.dragStartX = 0;
        this.dragType = null; // 'move', 'resize-left', 'resize-right'
        this.chartElement = document.getElementById('timelineChart');
        this.zoomLevel = 'month'; // day, week, month, quarter, year
        this.groupBy = 'none'; // none, epic, assignee, priority, team
        this.dateRange = {
            start: null,
            end: null
        };
        this.swimlanes = [];
        this.issues = [];
        this.dependencies = [];
        this.milestones = [];
        
        this.init();
    }

    init() {
        this.loadData();
        this.setupControls();
        this.setupBarDragListeners();
        this.setupDateRangeListeners();
        this.setupTooltips();
        this.setupZoomControls();
        this.setupSwimlaneControls();
        this.calculateDateRange();
        this.render();
    }

    loadData() {
        // Load issues, dependencies, and milestones from DOM or API
        const issueElements = document.querySelectorAll('[data-issue-id]');
        this.issues = Array.from(issueElements).map(el => ({
            id: el.dataset.issueId,
            title: el.dataset.issueTitle || '',
            startDate: new Date(el.dataset.startDate),
            endDate: new Date(el.dataset.endDate),
            assignee: el.dataset.assignee || 'Unassigned',
            priority: el.dataset.priority || 'medium',
            epic: el.dataset.epic || 'No Epic',
            team: el.dataset.team || 'Default Team',
            progress: parseInt(el.dataset.progress) || 0,
            color: el.dataset.color || '#0052CC',
            element: el
        }));

        // Load dependencies
        const depElements = document.querySelectorAll('[data-depends-on]');
        this.dependencies = Array.from(depElements).map(el => ({
            from: el.dataset.issueId,
            to: el.dataset.dependsOn,
            type: el.dataset.dependencyType || 'blocks'
        }));

        // Load milestones
        const milestoneElements = document.querySelectorAll('[data-milestone]');
        this.milestones = Array.from(milestoneElements).map(el => ({
            id: el.dataset.milestoneId,
            title: el.dataset.milestoneTitle,
            date: new Date(el.dataset.milestoneDate),
            type: el.dataset.milestoneType || 'release'
        }));
    }

    setupControls() {
        // Create control panel if it doesn't exist
        if (!document.getElementById('timelineControls')) {
            this.createControlPanel();
        }
    }

    createControlPanel() {
        const toolbar = document.querySelector('.timeline-toolbar') || 
                       document.querySelector('.kanban-toolbar');
        
        if (!toolbar) return;

        const controlsHTML = `
            <div id="timelineControls" class="timeline-controls">
                <div class="timeline-control-group">
                    <label class="timeline-control-label">Zoom:</label>
                    <div class="btn-group">
                        <button class="btn btn-sm ${this.zoomLevel === 'day' ? 'active' : ''}" data-zoom="day">Day</button>
                        <button class="btn btn-sm ${this.zoomLevel === 'week' ? 'active' : ''}" data-zoom="week">Week</button>
                        <button class="btn btn-sm ${this.zoomLevel === 'month' ? 'active' : ''}" data-zoom="month">Month</button>
                        <button class="btn btn-sm ${this.zoomLevel === 'quarter' ? 'active' : ''}" data-zoom="quarter">Quarter</button>
                        <button class="btn btn-sm ${this.zoomLevel === 'year' ? 'active' : ''}" data-zoom="year">Year</button>
                    </div>
                </div>
                
                <div class="timeline-control-group">
                    <label class="timeline-control-label">Group by:</label>
                    <select id="groupBySelect" class="timeline-select">
                        <option value="none">None</option>
                        <option value="epic">Epic</option>
                        <option value="assignee">Assignee</option>
                        <option value="priority">Priority</option>
                        <option value="team">Team</option>
                    </select>
                </div>
                
                <div class="timeline-control-group">
                    <button class="btn btn-ghost btn-sm" id="todayBtn" title="Jump to today">
                        <i data-lucide="calendar"></i>
                        Today
                    </button>
                    <button class="btn btn-ghost btn-sm" id="fitAllBtn" title="Fit all items">
                        <i data-lucide="maximize-2"></i>
                        Fit All
                    </button>
                    <button class="btn btn-ghost btn-sm" id="exportTimelineBtn" title="Export timeline">
                        <i data-lucide="download"></i>
                        Export
                    </button>
                </div>
            </div>
        `;

        const controlsDiv = document.createElement('div');
        controlsDiv.innerHTML = controlsHTML;
        toolbar.appendChild(controlsDiv.firstElementChild);

        // Re-initialize Lucide icons
        if (window.lucide) {
            lucide.createIcons();
        }
    }

    setupZoomControls() {
        document.addEventListener('click', (e) => {
            const zoomBtn = e.target.closest('[data-zoom]');
            if (zoomBtn) {
                const newZoom = zoomBtn.dataset.zoom;
                this.setZoomLevel(newZoom);
                
                // Update active state
                document.querySelectorAll('[data-zoom]').forEach(btn => {
                    btn.classList.remove('active');
                });
                zoomBtn.classList.add('active');
            }
        });

        // Today button
        document.getElementById('todayBtn')?.addEventListener('click', () => {
            this.jumpToToday();
        });

        // Fit all button
        document.getElementById('fitAllBtn')?.addEventListener('click', () => {
            this.fitAllIssues();
        });

        // Export button
        document.getElementById('exportTimelineBtn')?.addEventListener('click', () => {
            this.exportTimeline();
        });
    }

    setupSwimlaneControls() {
        const groupBySelect = document.getElementById('groupBySelect');
        if (groupBySelect) {
            groupBySelect.value = this.groupBy;
            groupBySelect.addEventListener('change', (e) => {
                this.groupBy = e.target.value;
                this.render();
            });
        }
    }

    setZoomLevel(level) {
        this.zoomLevel = level;
        this.calculateDateRange();
        this.render();
    }

    calculateDateRange() {
        if (this.issues.length === 0) {
            const today = new Date();
            this.dateRange.start = new Date(today.getFullYear(), today.getMonth(), 1);
            this.dateRange.end = new Date(today.getFullYear(), today.getMonth() + 3, 0);
            return;
        }

        // Find earliest and latest dates
        let earliest = new Date(Math.min(...this.issues.map(i => i.startDate)));
        let latest = new Date(Math.max(...this.issues.map(i => i.endDate)));

        // Add padding based on zoom level
        const padding = {
            'day': 7,
            'week': 14,
            'month': 30,
            'quarter': 60,
            'year': 180
        };

        earliest.setDate(earliest.getDate() - (padding[this.zoomLevel] || 30));
        latest.setDate(latest.getDate() + (padding[this.zoomLevel] || 30));

        this.dateRange.start = earliest;
        this.dateRange.end = latest;
    }

    render() {
        if (!this.chartElement) return;

        // Clear existing content
        this.chartElement.innerHTML = '';

        // Create swimlanes if grouping is enabled
        if (this.groupBy !== 'none') {
            this.createSwimlanes();
        }

        // Render timeline header (dates)
        this.renderTimelineHeader();

        // Render swimlanes or flat list
        if (this.groupBy !== 'none') {
            this.renderSwimlanes();
        } else {
            this.renderFlatTimeline();
        }

        // Render milestones
        this.renderMilestones();

        // Render dependencies
        this.renderDependencies();

        // Add "today" indicator line
        this.renderTodayLine();
    }

    createSwimlanes() {
        const groups = new Map();
        
        // Group issues
        this.issues.forEach(issue => {
            const groupKey = issue[this.groupBy];
            if (!groups.has(groupKey)) {
                groups.set(groupKey, []);
            }
            groups.get(groupKey).push(issue);
        });

        this.swimlanes = Array.from(groups.entries()).map(([name, issues]) => ({
            name,
            issues,
            collapsed: false
        }));
    }

    renderTimelineHeader() {
        const header = document.createElement('div');
        header.className = 'timeline-header';
        
        const totalDays = Math.ceil((this.dateRange.end - this.dateRange.start) / (1000 * 60 * 60 * 24));
        const headerHTML = this.generateHeaderHTML(totalDays);
        
        header.innerHTML = headerHTML;
        this.chartElement.appendChild(header);
    }

    generateHeaderHTML(totalDays) {
        let html = '<div class="timeline-header-row">';
        
        const current = new Date(this.dateRange.start);
        const cellWidth = 100 / totalDays;

        if (this.zoomLevel === 'day') {
            while (current <= this.dateRange.end) {
                html += `<div class="timeline-header-cell" style="width: ${cellWidth}%">
                    ${current.getDate()}
                </div>`;
                current.setDate(current.getDate() + 1);
            }
        } else if (this.zoomLevel === 'week') {
            while (current <= this.dateRange.end) {
                const weekNum = this.getWeekNumber(current);
                html += `<div class="timeline-header-cell" style="min-width: 50px">
                    W${weekNum}
                </div>`;
                current.setDate(current.getDate() + 7);
            }
        } else if (this.zoomLevel === 'month') {
            while (current <= this.dateRange.end) {
                const monthName = current.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
                html += `<div class="timeline-header-cell" style="min-width: 80px">
                    ${monthName}
                </div>`;
                current.setMonth(current.getMonth() + 1);
            }
        } else if (this.zoomLevel === 'quarter') {
            while (current <= this.dateRange.end) {
                const quarter = Math.floor(current.getMonth() / 3) + 1;
                const year = current.getFullYear();
                html += `<div class="timeline-header-cell" style="min-width: 100px">
                    Q${quarter} ${year}
                </div>`;
                current.setMonth(current.getMonth() + 3);
            }
        } else if (this.zoomLevel === 'year') {
            while (current <= this.dateRange.end) {
                html += `<div class="timeline-header-cell" style="min-width: 120px">
                    ${current.getFullYear()}
                </div>`;
                current.setFullYear(current.getFullYear() + 1);
            }
        }

        html += '</div>';
        return html;
    }

    renderSwimlanes() {
        this.swimlanes.forEach((swimlane, index) => {
            const swimlaneDiv = document.createElement('div');
            swimlaneDiv.className = 'timeline-swimlane';
            swimlaneDiv.dataset.swimlaneIndex = index;
            
            // Swimlane header
            const headerDiv = document.createElement('div');
            headerDiv.className = 'timeline-swimlane-header';
            headerDiv.innerHTML = `
                <button class="swimlane-toggle" data-swimlane="${index}">
                    <i data-lucide="${swimlane.collapsed ? 'chevron-right' : 'chevron-down'}" 
                       style="width: 14px; height: 14px;"></i>
                </button>
                <span class="swimlane-title">${swimlane.name}</span>
                <span class="swimlane-count">${swimlane.issues.length}</span>
            `;
            
            headerDiv.addEventListener('click', () => {
                swimlane.collapsed = !swimlane.collapsed;
                this.render();
            });
            
            swimlaneDiv.appendChild(headerDiv);
            
            // Swimlane content
            if (!swimlane.collapsed) {
                const contentDiv = document.createElement('div');
                contentDiv.className = 'timeline-swimlane-content';
                
                swimlane.issues.forEach(issue => {
                    const issueBar = this.createIssueBar(issue);
                    contentDiv.appendChild(issueBar);
                });
                
                swimlaneDiv.appendChild(contentDiv);
            }
            
            this.chartElement.appendChild(swimlaneDiv);
        });

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    renderFlatTimeline() {
        const container = document.createElement('div');
        container.className = 'timeline-flat-content';
        
        this.issues.forEach(issue => {
            const issueBar = this.createIssueBar(issue);
            container.appendChild(issueBar);
        });
        
        this.chartElement.appendChild(container);
    }

    createIssueBar(issue) {
        const row = document.createElement('div');
        row.className = 'timeline-row';
        row.dataset.issueId = issue.id;
        
        // Calculate position and width
        const totalDuration = this.dateRange.end - this.dateRange.start;
        const startOffset = issue.startDate - this.dateRange.start;
        const duration = issue.endDate - issue.startDate;
        
        const leftPercent = (startOffset / totalDuration) * 100;
        const widthPercent = (duration / totalDuration) * 100;
        
        // Issue info (left side)
        const infoDiv = document.createElement('div');
        infoDiv.className = 'timeline-row-info';
        infoDiv.innerHTML = `
            <span class="issue-key">${issue.id}</span>
            <span class="issue-title">${issue.title}</span>
        `;
        
        // Issue bar (right side on timeline)
        const barContainer = document.createElement('div');
        barContainer.className = 'timeline-row-bar-container';
        
        const bar = document.createElement('div');
        bar.className = 'timeline-bar';
        bar.style.left = `${Math.max(0, leftPercent)}%`;
        bar.style.width = `${Math.max(1, widthPercent)}%`;
        bar.style.backgroundColor = issue.color;
        bar.dataset.issueId = issue.id;
        
        // Progress indicator
        if (issue.progress > 0) {
            const progressBar = document.createElement('div');
            progressBar.className = 'timeline-bar-progress';
            progressBar.style.width = `${issue.progress}%`;
            bar.appendChild(progressBar);
        }
        
        // Resize handles
        const leftHandle = document.createElement('div');
        leftHandle.className = 'timeline-bar-handle timeline-bar-handle-left';
        bar.appendChild(leftHandle);
        
        const rightHandle = document.createElement('div');
        rightHandle.className = 'timeline-bar-handle timeline-bar-handle-right';
        bar.appendChild(rightHandle);
        
        // Bar content
        const barContent = document.createElement('div');
        barContent.className = 'timeline-bar-content';
        barContent.textContent = issue.title;
        bar.appendChild(barContent);
        
        barContainer.appendChild(bar);
        row.appendChild(infoDiv);
        row.appendChild(barContainer);
        
        return row;
    }

    renderMilestones() {
        if (this.milestones.length === 0) return;

        this.milestones.forEach(milestone => {
            const totalDuration = this.dateRange.end - this.dateRange.start;
            const offset = milestone.date - this.dateRange.start;
            const leftPercent = (offset / totalDuration) * 100;

            if (leftPercent < 0 || leftPercent > 100) return;

            const marker = document.createElement('div');
            marker.className = 'timeline-milestone';
            marker.style.left = `${leftPercent}%`;
            marker.innerHTML = `
                <div class="timeline-milestone-line"></div>
                <div class="timeline-milestone-label">
                    <i data-lucide="flag" style="width: 12px; height: 12px;"></i>
                    ${milestone.title}
                </div>
            `;

            this.chartElement.appendChild(marker);
        });

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    renderTodayLine() {
        const today = new Date();
        const totalDuration = this.dateRange.end - this.dateRange.start;
        const offset = today - this.dateRange.start;
        const leftPercent = (offset / totalDuration) * 100;

        if (leftPercent < 0 || leftPercent > 100) return;

        const line = document.createElement('div');
        line.className = 'timeline-today-line';
        line.style.left = `${leftPercent}%`;
        line.innerHTML = `
            <div class="timeline-today-marker">TODAY</div>
        `;

        this.chartElement.appendChild(line);
    }

    renderDependencies() {
        if (this.dependencies.length === 0) return;

        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.id = 'dependencyLines';
        svg.className = 'timeline-dependency-svg';
        svg.style.position = 'absolute';
        svg.style.top = '0';
        svg.style.left = '0';
        svg.style.width = '100%';
        svg.style.height = '100%';
        svg.style.pointerEvents = 'none';
        svg.style.zIndex = '1';

        this.chartElement.appendChild(svg);

        this.dependencies.forEach(dep => {
            this.drawDependencyLine(dep.from, dep.to, dep.type);
        });
    }

    drawDependencyLine(fromId, toId, type) {
        const fromBar = document.querySelector(`[data-issue-id="${fromId}"] .timeline-bar`);
        const toBar = document.querySelector(`[data-issue-id="${toId}"] .timeline-bar`);
        
        if (!fromBar || !toBar) return;

        const svg = document.getElementById('dependencyLines');
        if (!svg) return;

        const chartRect = this.chartElement.getBoundingClientRect();
        const fromRect = fromBar.getBoundingClientRect();
        const toRect = toBar.getBoundingClientRect();

        const x1 = fromRect.right - chartRect.left;
        const y1 = fromRect.top - chartRect.top + fromRect.height / 2;
        const x2 = toRect.left - chartRect.left;
        const y2 = toRect.top - chartRect.top + toRect.height / 2;

        // Create curved path
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        const midX = (x1 + x2) / 2;
        
        const d = `M ${x1} ${y1} C ${midX} ${y1}, ${midX} ${y2}, ${x2} ${y2}`;
        path.setAttribute('d', d);
        path.setAttribute('class', `dependency-line dependency-${type}`);
        path.setAttribute('stroke', type === 'blocks' ? '#E34C26' : '#0052CC');
        path.setAttribute('stroke-width', '2');
        path.setAttribute('fill', 'none');
        path.setAttribute('marker-end', 'url(#arrowhead)');

        svg.appendChild(path);

        // Add arrowhead marker (once)
        if (!svg.querySelector('#arrowhead')) {
            this.addArrowMarker(svg);
        }
    }

    addArrowMarker(svg) {
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
        marker.setAttribute('id', 'arrowhead');
        marker.setAttribute('markerWidth', '10');
        marker.setAttribute('markerHeight', '10');
        marker.setAttribute('refX', '9');
        marker.setAttribute('refY', '3');
        marker.setAttribute('orient', 'auto');

        const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        polygon.setAttribute('points', '0 0, 10 3, 0 6');
        polygon.setAttribute('fill', '#0052CC');

        marker.appendChild(polygon);
        defs.appendChild(marker);
        svg.appendChild(defs);
    }

    getWeekNumber(date) {
        const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
        const dayNum = d.getUTCDay() || 7;
        d.setUTCDate(d.getUTCDate() + 4 - dayNum);
        const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
        return Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
    }

    jumpToToday() {
        const today = new Date();
        this.dateRange.start = new Date(today.getFullYear(), today.getMonth() - 1, 1);
        this.dateRange.end = new Date(today.getFullYear(), today.getMonth() + 2, 0);
        this.render();
    }

    fitAllIssues() {
        this.calculateDateRange();
        this.render();
    }

    exportTimeline() {
        // Export as PNG or PDF (placeholder)
        alert('Export timeline - Coming soon!\n\nWill support PNG and PDF export.');
    }

    setupBarDragListeners() {
        this.chartElement?.addEventListener('mousedown', (e) => {
            const bar = e.target.closest('.timeline-bar');
            if (!bar) return;

            // Check if clicking on resize handle
            if (e.target.classList.contains('timeline-bar-handle-left')) {
                this.dragType = 'resize-left';
            } else if (e.target.classList.contains('timeline-bar-handle-right')) {
                this.dragType = 'resize-right';
            } else {
                this.dragType = 'move';
            }

            this.draggedBar = bar;
            this.dragStartX = e.clientX;
            this.originalLeft = parseFloat(bar.style.left);
            this.originalWidth = parseFloat(bar.style.width);
            
            bar.classList.add('dragging');
            document.body.style.cursor = this.dragType === 'move' ? 'grabbing' : 'ew-resize';
            
            e.preventDefault();
        });

        document.addEventListener('mousemove', (e) => {
            if (!this.draggedBar) return;

            const container = this.draggedBar.closest('.timeline-row-bar-container');
            if (!container) return;

            const deltaX = e.clientX - this.dragStartX;
            const containerWidth = container.clientWidth;
            const deltaPercent = (deltaX / containerWidth) * 100;

            if (this.dragType === 'move') {
                const newLeft = Math.max(0, Math.min(100, this.originalLeft + deltaPercent));
                this.draggedBar.style.left = `${newLeft}%`;
            } else if (this.dragType === 'resize-left') {
                const newLeft = Math.max(0, this.originalLeft + deltaPercent);
                const newWidth = Math.max(1, this.originalWidth - deltaPercent);
                this.draggedBar.style.left = `${newLeft}%`;
                this.draggedBar.style.width = `${newWidth}%`;
            } else if (this.dragType === 'resize-right') {
                const newWidth = Math.max(1, this.originalWidth + deltaPercent);
                this.draggedBar.style.width = `${newWidth}%`;
            }

            // Redraw dependency lines
            this.updateDependencyLines();
            
            e.preventDefault();
        });

        document.addEventListener('mouseup', (e) => {
            if (!this.draggedBar) return;

            const issueId = this.draggedBar.dataset.issueId;
            if (issueId) {
                this.updateIssueDates(issueId);
            }

            this.draggedBar.classList.remove('dragging');
            this.draggedBar = null;
            this.dragType = null;
            document.body.style.cursor = '';
        });
    }

    updateIssueDates(issueId) {
        const bar = document.querySelector(`[data-issue-id="${issueId}"] .timeline-bar`);
        if (!bar) return;

        const leftPercent = parseFloat(bar.style.left);
        const widthPercent = parseFloat(bar.style.width);

        const startDate = this.percentToDate(leftPercent);
        const endDate = this.percentToDate(leftPercent + widthPercent);

        // Update issue in memory
        const issue = this.issues.find(i => i.id === issueId);
        if (issue) {
            issue.startDate = startDate;
            issue.endDate = endDate;
        }

        // Send to server
        this.saveIssueDates(issueId, startDate, endDate);
    }

    async saveIssueDates(issueId, startDate, endDate) {
        const projectId = this.getProjectId();
        if (!projectId) return;

        try {
            const response = await fetch(`/api/projects/${projectId}/issues/${issueId}/dates`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    start_date: startDate.toISOString().split('T')[0],
                    end_date: endDate.toISOString().split('T')[0]
                })
            });

            if (response.ok) {
                window.notificationManager?.addNotification({
                    title: 'Dates Updated',
                    message: 'Issue dates saved successfully',
                    type: 'success'
                });
            } else {
                throw new Error('Update failed');
            }
        } catch (error) {
            console.error('Error updating dates:', error);
            window.notificationManager?.addNotification({
                title: 'Update Failed',
                message: 'Could not save issue dates',
                type: 'error'
            });
        }
    }

    percentToDate(percent) {
        const totalDuration = this.dateRange.end - this.dateRange.start;
        const offset = (totalDuration * percent) / 100;
        return new Date(this.dateRange.start.getTime() + offset);
    }

    updateDependencyLines() {
        const svg = document.getElementById('dependencyLines');
        if (svg) {
            svg.innerHTML = '';
            // Re-add marker
            this.addArrowMarker(svg);
            // Re-draw all dependencies
            this.dependencies.forEach(dep => {
                this.drawDependencyLine(dep.from, dep.to, dep.type);
            });
        }
    }

    setupDateRangeListeners() {
        const startDateInput = document.getElementById('timelineStartDate');
        const endDateInput = document.getElementById('timelineEndDate');

        if (startDateInput) {
            startDateInput.addEventListener('change', () => {
                this.dateRange.start = new Date(startDateInput.value);
                this.render();
            });
        }

        if (endDateInput) {
            endDateInput.addEventListener('change', () => {
                this.dateRange.end = new Date(endDateInput.value);
                this.render();
            });
        }
    }

    setupTooltips() {
        this.chartElement?.addEventListener('mouseover', (e) => {
            const bar = e.target.closest('.timeline-bar');
            if (bar) {
                this.showTooltip(bar, e);
            }
        });

        this.chartElement?.addEventListener('mouseout', (e) => {
            const bar = e.target.closest('.timeline-bar');
            if (bar) {
                this.hideTooltip();
            }
        });
    }

    showTooltip(bar, event) {
        const issueId = bar.dataset.issueId;
        const issue = this.issues.find(i => i.id === issueId);
        if (!issue) return;

        const existing = document.getElementById('timelineTooltip');
        if (existing) existing.remove();

        const tooltip = document.createElement('div');
        tooltip.id = 'timelineTooltip';
        tooltip.className = 'timeline-tooltip';
        tooltip.innerHTML = `
            <div class="timeline-tooltip-header">
                <span class="issue-key">${issue.id}</span>
                <span class="issue-priority priority-${issue.priority}">${issue.priority}</span>
            </div>
            <div class="timeline-tooltip-title">${issue.title}</div>
            <div class="timeline-tooltip-dates">
                <i data-lucide="calendar" style="width: 12px; height: 12px;"></i>
                ${issue.startDate.toLocaleDateString()} - ${issue.endDate.toLocaleDateString()}
            </div>
            <div class="timeline-tooltip-assignee">
                <i data-lucide="user" style="width: 12px; height: 12px;"></i>
                ${issue.assignee}
            </div>
            ${issue.progress > 0 ? `
                <div class="timeline-tooltip-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${issue.progress}%"></div>
                    </div>
                    <span>${issue.progress}% complete</span>
                </div>
            ` : ''}
        `;

        document.body.appendChild(tooltip);

        // Position tooltip
        const rect = bar.getBoundingClientRect();
        tooltip.style.left = `${rect.left + rect.width / 2 - tooltip.clientWidth / 2}px`;
        tooltip.style.top = `${rect.top - tooltip.clientHeight - 8}px`;

        // Adjust if off-screen
        const tooltipRect = tooltip.getBoundingClientRect();
        if (tooltipRect.right > window.innerWidth) {
            tooltip.style.left = `${window.innerWidth - tooltipRect.width - 10}px`;
        }
        if (tooltipRect.left < 0) {
            tooltip.style.left = '10px';
        }

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    hideTooltip() {
        const tooltip = document.getElementById('timelineTooltip');
        if (tooltip) {
            tooltip.remove();
        }
    }

    getProjectId() {
        const match = window.location.pathname.match(/projects\/(\d+)/);
        return match ? match[1] : null;
    }

    getCsrfToken() {
        const token = document.querySelector('input[name="csrf_token"]');
        return token ? token.value : '';
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('timelineChart')) {
        window.timelineChart = new TimelineChart();
    }
});
