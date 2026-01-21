// timeline.js - Timeline/Gantt chart interactions

class TimelineChart {
    constructor() {
        this.draggedBar = null;
        this.dragStartX = 0;
        this.chartElement = document.getElementById('timelineChart');
        this.init();
    }

    init() {
        this.setupBarDragListeners();
        this.setupDateRangeListeners();
        this.setupTooltips();
    }

    setupBarDragListeners() {
        document.addEventListener('mousedown', (e) => this.handleBarMouseDown(e));
        document.addEventListener('mousemove', (e) => this.handleBarMouseMove(e));
        document.addEventListener('mouseup', (e) => this.handleBarMouseUp(e));
    }

    handleBarMouseDown(e) {
        const bar = e.target.closest('.gantt-bar');
        if (!bar || !this.chartElement) return;

        this.draggedBar = bar;
        this.dragStartX = e.clientX;
        bar.style.cursor = 'grabbing';
    }

    handleBarMouseMove(e) {
        if (!this.draggedBar) return;

        const deltaX = e.clientX - this.dragStartX;
        const chart = this.draggedBar.closest('.gantt-bar-container');
        
        if (chart) {
            const style = window.getComputedStyle(this.draggedBar);
            const currentLeft = parseFloat(style.left);
            const newLeft = currentLeft + (deltaX / chart.clientWidth * 100);
            
            this.draggedBar.style.left = Math.max(0, Math.min(newLeft, 100)) + '%';
        }
    }

    handleBarMouseUp(e) {
        if (!this.draggedBar) return;

        const issueId = this.draggedBar.closest('[data-issue-id]')?.dataset.issueId;
        if (issueId) {
            // Calculate new dates based on bar position
            this.updateIssueDates(issueId);
        }

        this.draggedBar.style.cursor = 'grab';
        this.draggedBar = null;
    }

    updateIssueDates(issueId) {
        // Extract dates from bar position and update
        const bar = document.querySelector(`[data-issue-id="${issueId}"] .gantt-bar`);
        if (!bar) return;

        const style = window.getComputedStyle(bar);
        const leftPercent = parseFloat(style.left);
        const widthPercent = parseFloat(style.width);

        // Calculate dates (placeholder - implement based on calendar)
        const startDate = this.percentToDate(leftPercent);
        const endDate = this.percentToDate(leftPercent + widthPercent);

        // Send update to server
        fetch(`/api/project/${this.getProjectId()}/issue/${issueId}/update_dates`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken()
            },
            body: JSON.stringify({
                start_date: startDate.toISOString(),
                end_date: endDate.toISOString()
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log('Issue dates updated successfully');
                    // Redraw dependency lines
                    this.redrawDependencyLines();
                }
            })
            .catch(error => console.error('Error updating dates:', error));
    }

    percentToDate(percent) {
        // This is a simplified conversion - implement based on your calendar
        const startDate = new Date(document.getElementById('startDate')?.value);
        const endDate = new Date(document.getElementById('endDate')?.value);
        const totalDays = (endDate - startDate) / (1000 * 60 * 60 * 24);
        
        const date = new Date(startDate);
        date.setDate(date.getDate() + (totalDays * percent / 100));
        
        return date;
    }

    redrawDependencyLines() {
        const svg = document.getElementById('dependencyLines');
        if (!svg) return;

        svg.innerHTML = '';

        // Redraw all dependency lines
        const dependencies = document.querySelectorAll('[data-depends-on]');
        dependencies.forEach(element => {
            const targetId = element.dataset.dependsOn;
            const targetElement = document.querySelector(`[data-issue-id="${targetId}"] .gantt-bar`);
            
            if (targetElement) {
                this.drawDependencyLine(element.closest('.gantt-bar'), targetElement);
            }
        });
    }

    drawDependencyLine(fromBar, toBar) {
        if (!fromBar || !toBar) return;

        const svg = document.getElementById('dependencyLines');
        const chart = document.getElementById('timelineChart');
        
        if (!svg || !chart) return;

        const fromRect = fromBar.getBoundingClientRect();
        const toRect = toBar.getBoundingClientRect();
        const chartRect = chart.getBoundingClientRect();

        const x1 = fromRect.right - chartRect.left;
        const y1 = fromRect.top - chartRect.top + fromRect.height / 2;
        const x2 = toRect.left - chartRect.left;
        const y2 = toRect.top - chartRect.top + toRect.height / 2;

        // Draw curved line
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        const cp1x = (x1 + x2) / 2;
        const d = `M ${x1} ${y1} C ${cp1x} ${y1}, ${cp1x} ${y2}, ${x2} ${y2}`;

        path.setAttribute('d', d);
        path.setAttribute('class', 'dependency-line');
        svg.appendChild(path);

        // Add arrow head
        this.addArrowhead(svg, x2, y2);
    }

    addArrowhead(svg, x, y) {
        const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
        marker.setAttribute('id', 'arrowhead');
        marker.setAttribute('markerWidth', '10');
        marker.setAttribute('markerHeight', '10');
        marker.setAttribute('refX', '9');
        marker.setAttribute('refY', '3');
        marker.setAttribute('orient', 'auto');

        const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        polygon.setAttribute('points', '0 0, 10 3, 0 6');
        polygon.setAttribute('fill', '#0c66e4');

        marker.appendChild(polygon);
        svg.appendChild(marker);
    }

    setupDateRangeListeners() {
        const startDateInput = document.getElementById('startDate');
        const endDateInput = document.getElementById('endDate');

        if (startDateInput) {
            startDateInput.addEventListener('change', () => this.onDateRangeChange());
        }

        if (endDateInput) {
            endDateInput.addEventListener('change', () => this.onDateRangeChange());
        }
    }

    onDateRangeChange() {
        // Regenerate timeline chart
        window.location.reload(); // Simple approach - could be optimized
    }

    setupTooltips() {
        document.addEventListener('mouseover', (e) => {
            const bar = e.target.closest('.gantt-bar');
            if (bar) {
                this.showTooltip(bar);
            }
        });

        document.addEventListener('mouseout', (e) => {
            const bar = e.target.closest('.gantt-bar');
            if (bar) {
                this.hideTooltip();
            }
        });
    }

    showTooltip(bar) {
        const title = bar.querySelector('.bar-title')?.textContent || 'Issue';
        const existing = document.getElementById('timelineTooltip');
        
        if (existing) {
            existing.remove();
        }

        const tooltip = document.createElement('div');
        tooltip.id = 'timelineTooltip';
        tooltip.className = 'tooltip';
        tooltip.textContent = title;
        tooltip.style.position = 'fixed';
        tooltip.style.zIndex = '1000';
        tooltip.style.backgroundColor = '#2c333a';
        tooltip.style.color = '#b6c2cf';
        tooltip.style.padding = '8px 12px';
        tooltip.style.borderRadius = '3px';
        tooltip.style.fontSize = '12px';
        tooltip.style.border = '1px solid #3d444d';

        document.body.appendChild(tooltip);

        const rect = bar.getBoundingClientRect();
        tooltip.style.left = (rect.left + rect.width / 2 - tooltip.clientWidth / 2) + 'px';
        tooltip.style.top = (rect.top - 30) + 'px';
    }

    hideTooltip() {
        const tooltip = document.getElementById('timelineTooltip');
        if (tooltip) {
            tooltip.remove();
        }
    }

    getProjectId() {
        const match = window.location.pathname.match(/\/project\/(\d+)/);
        return match ? match[1] : null;
    }

    getCsrfToken() {
        const token = document.querySelector('input[name="csrf_token"]');
        return token ? token.value : '';
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    window.timeline = new TimelineChart();
});
