/**
 * Issue Navigator - Advanced Table Features
 * Column management, bulk operations, advanced export, keyboard shortcuts
 */

class IssueTableAdvanced {
    constructor() {
        this.columns = [
            { id: 'key', label: 'Key', width: 120, visible: true, sortable: true },
            { id: 'type', label: 'Type', width: 100, visible: true, sortable: true },
            { id: 'summary', label: 'Summary', width: 300, visible: true, sortable: true },
            { id: 'assignee', label: 'Assignee', width: 150, visible: true, sortable: true },
            { id: 'reporter', label: 'Reporter', width: 150, visible: false, sortable: true },
            { id: 'priority', label: 'Priority', width: 120, visible: true, sortable: true },
            { id: 'status', label: 'Status', width: 130, visible: true, sortable: true },
            { id: 'created', label: 'Created', width: 150, visible: false, sortable: true },
            { id: 'updated', label: 'Updated', width: 150, visible: true, sortable: true },
            { id: 'dueDate', label: 'Due Date', width: 150, visible: false, sortable: true },
            { id: 'resolution', label: 'Resolution', width: 130, visible: false, sortable: true },
            { id: 'labels', label: 'Labels', width: 200, visible: false, sortable: false },
            { id: 'components', label: 'Components', width: 200, visible: false, sortable: false },
            { id: 'fixVersions', label: 'Fix Versions', width: 150, visible: false, sortable: false }
        ];
        
        this.selectedIssues = new Set();
        this.viewMode = 'list'; // 'list', 'detail', 'split'
        this.splitRatio = 50; // percentage for split view
        this.sortColumn = 'updated';
        this.sortDirection = 'desc';
        
        this.bulkOperations = [
            { id: 'edit', label: 'Edit Issues', icon: 'edit-3' },
            { id: 'transition', label: 'Transition', icon: 'arrow-right' },
            { id: 'assign', label: 'Assign', icon: 'user' },
            { id: 'move', label: 'Move', icon: 'folder' },
            { id: 'delete', label: 'Delete', icon: 'trash-2' },
            { id: 'watch', label: 'Watch', icon: 'eye' },
            { id: 'label', label: 'Labels', icon: 'tag' },
            { id: 'link', label: 'Link', icon: 'link' }
        ];
        
        this.quickFilters = [
            { id: 'my-open', label: 'My Open Issues', count: 23, active: false },
            { id: 'recent', label: 'Recently Updated', count: 45, active: false },
            { id: 'unassigned', label: 'Unassigned', count: 12, active: false },
            { id: 'overdue', label: 'Overdue', count: 5, active: true }
        ];
        
        this.resizing = null;
        this.dragColumn = null;
        
        this.init();
    }
    
    init() {
        this.setupKeyboardShortcuts();
        console.log('Issue Table Advanced initialized');
    }
    
    renderTableHeader() {
        return `
            <div class="issue-table-toolbar">
                <div class="toolbar-left">
                    <div class="view-mode-switcher">
                        <button class="view-btn ${this.viewMode === 'list' ? 'active' : ''}" onclick="issueTableAdvanced.switchView('list')" title="List View">
                            <i data-lucide="list"></i>
                        </button>
                        <button class="view-btn ${this.viewMode === 'detail' ? 'active' : ''}" onclick="issueTableAdvanced.switchView('detail')" title="Detail View">
                            <i data-lucide="layout"></i>
                        </button>
                        <button class="view-btn ${this.viewMode === 'split' ? 'active' : ''}" onclick="issueTableAdvanced.switchView('split')" title="Split View">
                            <i data-lucide="columns"></i>
                        </button>
                    </div>
                    
                    <div class="quick-filters">
                        ${this.quickFilters.map(filter => `
                            <button class="quick-filter-chip ${filter.active ? 'active' : ''}" onclick="issueTableAdvanced.toggleQuickFilter('${filter.id}')">
                                ${filter.label}
                                <span class="chip-count">${filter.count}</span>
                                ${filter.active ? '<i data-lucide="x" style="width: 12px; height: 12px;"></i>' : ''}
                            </button>
                        `).join('')}
                    </div>
                    
                    ${this.selectedIssues.size > 0 ? this.renderBulkActionsBar() : ''}
                </div>
                
                <div class="toolbar-right">
                    <button class="btn btn-secondary" onclick="issueTableAdvanced.openColumnCustomizer()">
                        <i data-lucide="columns"></i>
                        Columns
                    </button>
                    <button class="btn btn-secondary" onclick="issueTableAdvanced.exportIssues()">
                        <i data-lucide="download"></i>
                        Export
                    </button>
                    <button class="btn btn-secondary" onclick="issueTableAdvanced.shareFilter()">
                        <i data-lucide="share-2"></i>
                        Share
                    </button>
                    <button class="btn-icon star-btn" onclick="issueTableAdvanced.toggleStar()" title="Star this filter">
                        <i data-lucide="star"></i>
                    </button>
                </div>
            </div>
        `;
    }
    
    renderBulkActionsBar() {
        return `
            <div class="bulk-actions-bar">
                <span class="bulk-count">${this.selectedIssues.size} selected</span>
                <div class="bulk-actions">
                    ${this.bulkOperations.map(op => `
                        <button class="bulk-action-btn" onclick="issueTableAdvanced.bulkAction('${op.id}')" title="${op.label}">
                            <i data-lucide="${op.icon}"></i>
                            ${op.label}
                        </button>
                    `).join('')}
                </div>
                <button class="btn-icon" onclick="issueTableAdvanced.clearSelection()" title="Clear selection">
                    <i data-lucide="x"></i>
                </button>
            </div>
        `;
    }
    
    renderTable(container) {
        const visibleColumns = this.columns.filter(col => col.visible);
        
        container.innerHTML = `
            <div class="advanced-issue-table">
                ${this.renderTableHeader()}
                
                <div class="table-container ${this.viewMode}">
                    <table class="issue-table">
                        <thead>
                            <tr>
                                <th class="checkbox-col">
                                    <input type="checkbox" onchange="issueTableAdvanced.toggleSelectAll(this.checked)" />
                                </th>
                                ${visibleColumns.map(col => this.renderColumnHeader(col)).join('')}
                            </tr>
                        </thead>
                        <tbody>
                            ${this.renderTableRows()}
                        </tbody>
                    </table>
                    
                    ${this.viewMode === 'split' ? this.renderSplitPanel() : ''}
                </div>
            </div>
        `;
        
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }
    
    renderColumnHeader(column) {
        return `
            <th class="resizable-header sortable-header" 
                data-column="${column.id}" 
                style="width: ${column.width}px"
                draggable="true"
                ondragstart="issueTableAdvanced.onColumnDragStart(event, '${column.id}')"
                ondragover="issueTableAdvanced.onColumnDragOver(event)"
                ondrop="issueTableAdvanced.onColumnDrop(event, '${column.id}')">
                <div class="header-content">
                    <span onclick="issueTableAdvanced.sortBy('${column.id}')">${column.label}</span>
                    ${this.sortColumn === column.id ? `
                        <i data-lucide="arrow-${this.sortDirection === 'asc' ? 'up' : 'down'}"></i>
                    ` : ''}
                </div>
                <div class="resize-handle" 
                    onmousedown="issueTableAdvanced.startResize(event, '${column.id}')"></div>
            </th>
        `;
    }
    
    renderTableRows() {
        // Mock data - would come from API
        const issues = [
            { key: 'TEST-142', type: 'Story', summary: 'Implement user authentication', assignee: 'John Doe', priority: 'High', status: 'In Progress', updated: '2 hours ago' },
            { key: 'TEST-141', type: 'Bug', summary: 'Fix memory leak in cache', assignee: 'Jane Smith', priority: 'Critical', status: 'In Review', updated: '5 hours ago' },
            { key: 'TEST-140', type: 'Task', summary: 'Update dependencies', assignee: 'Bob Johnson', priority: 'Medium', status: 'To Do', updated: '1 day ago' }
        ];
        
        return issues.map(issue => `
            <tr class="issue-row ${this.selectedIssues.has(issue.key) ? 'selected' : ''}" 
                onclick="issueTableAdvanced.selectIssue(event, '${issue.key}')">
                <td class="checkbox-col">
                    <input type="checkbox" ${this.selectedIssues.has(issue.key) ? 'checked' : ''} 
                        onclick="event.stopPropagation(); issueTableAdvanced.toggleIssue('${issue.key}')" />
                </td>
                <td><a href="#" class="issue-key">${issue.key}</a></td>
                <td><span class="issue-type-badge">${issue.type}</span></td>
                <td><span class="issue-summary">${issue.summary}</span></td>
                <td><span class="assignee">${issue.assignee}</span></td>
                <td><span class="priority-badge priority-${issue.priority.toLowerCase()}">${issue.priority}</span></td>
                <td><span class="status-badge">${issue.status}</span></td>
                <td><span class="updated-time">${issue.updated}</span></td>
            </tr>
        `).join('');
    }
    
    renderSplitPanel() {
        return `
            <div class="split-panel" style="width: ${100 - this.splitRatio}%">
                <div class="split-resizer" 
                    onmousedown="issueTableAdvanced.startSplitResize(event)"></div>
                <div class="split-content">
                    <div class="split-header">
                        <h3>TEST-142</h3>
                        <button class="btn-icon" onclick="issueTableAdvanced.closeSplit()">
                            <i data-lucide="x"></i>
                        </button>
                    </div>
                    <div class="split-body">
                        <!-- Issue details would go here -->
                        <p>Issue detail panel content...</p>
                    </div>
                </div>
            </div>
        `;
    }
    
    openColumnCustomizer() {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal column-customizer-modal">
                <div class="modal-header">
                    <h3>Customize Columns</h3>
                    <button class="btn-icon" onclick="this.closest('.modal-overlay').remove()">
                        <i data-lucide="x"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="columns-list">
                        ${this.columns.map(col => `
                            <div class="column-item" draggable="true">
                                <i data-lucide="grip-vertical"></i>
                                <input type="checkbox" ${col.visible ? 'checked' : ''} 
                                    onchange="issueTableAdvanced.toggleColumn('${col.id}', this.checked)" />
                                <span>${col.label}</span>
                                <input type="number" value="${col.width}" 
                                    onchange="issueTableAdvanced.setColumnWidth('${col.id}', this.value)" 
                                    style="width: 80px; margin-left: auto;" placeholder="Width" />
                            </div>
                        `).join('')}
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="issueTableAdvanced.resetColumns()">Reset to Default</button>
                    <button class="btn btn-primary" onclick="this.closest('.modal-overlay').remove()">Done</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        if (typeof lucide !== 'undefined') lucide.createIcons();
    }
    
    exportIssues() {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal export-modal">
                <div class="modal-header">
                    <h3>Export Issues</h3>
                    <button class="btn-icon" onclick="this.closest('.modal-overlay').remove()">
                        <i data-lucide="x"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label>Format</label>
                        <select id="exportFormat">
                            <option value="csv">CSV</option>
                            <option value="excel">Excel (XLSX)</option>
                            <option value="pdf">PDF</option>
                            <option value="html">HTML</option>
                            <option value="xml">XML</option>
                            <option value="json">JSON</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Include</label>
                        <div class="checkbox-group">
                            <label><input type="checkbox" checked /> Current columns</label>
                            <label><input type="checkbox" /> All fields</label>
                            <label><input type="checkbox" /> Comments</label>
                            <label><input type="checkbox" /> Attachments</label>
                            <label><input type="checkbox" /> Work logs</label>
                            <label><input type="checkbox" /> Change history</label>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Issues to export</label>
                        <div class="radio-group">
                            <label><input type="radio" name="exportScope" checked /> Current page (${this.selectedIssues.size || 50})</label>
                            <label><input type="radio" name="exportScope" /> Selected issues (${this.selectedIssues.size})</label>
                            <label><input type="radio" name="exportScope" /> All matching issues (250)</label>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                    <button class="btn btn-primary" onclick="issueTableAdvanced.doExport(); this.closest('.modal-overlay').remove()">
                        <i data-lucide="download"></i>
                        Export
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        if (typeof lucide !== 'undefined') lucide.createIcons();
    }
    
    // Event handlers
    switchView(mode) {
        this.viewMode = mode;
        const container = document.querySelector('.advanced-issue-table').parentElement;
        this.renderTable(container);
    }
    
    toggleQuickFilter(filterId) {
        const filter = this.quickFilters.find(f => f.id === filterId);
        if (filter) {
            filter.active = !filter.active;
            const container = document.querySelector('.advanced-issue-table').parentElement;
            this.renderTable(container);
        }
    }
    
    toggleIssue(issueKey) {
        if (this.selectedIssues.has(issueKey)) {
            this.selectedIssues.delete(issueKey);
        } else {
            this.selectedIssues.add(issueKey);
        }
        const container = document.querySelector('.advanced-issue-table').parentElement;
        this.renderTable(container);
    }
    
    selectIssue(event, issueKey) {
        if (event.shiftKey) {
            // Range selection
            this.showToast('Shift+click range selection');
        } else if (event.ctrlKey || event.metaKey) {
            // Multi-select
            this.toggleIssue(issueKey);
        } else {
            // Single select
            this.selectedIssues.clear();
            this.selectedIssues.add(issueKey);
            const container = document.querySelector('.advanced-issue-table').parentElement;
            this.renderTable(container);
        }
    }
    
    toggleSelectAll(checked) {
        if (checked) {
            // Select all visible issues
            this.selectedIssues.add('TEST-142');
            this.selectedIssues.add('TEST-141');
            this.selectedIssues.add('TEST-140');
        } else {
            this.selectedIssues.clear();
        }
        const container = document.querySelector('.advanced-issue-table').parentElement;
        this.renderTable(container);
    }
    
    clearSelection() {
        this.selectedIssues.clear();
        const container = document.querySelector('.advanced-issue-table').parentElement;
        this.renderTable(container);
    }
    
    bulkAction(action) {
        this.showToast(`Bulk ${action} for ${this.selectedIssues.size} issues`);
    }
    
    sortBy(column) {
        if (this.sortColumn === column) {
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortColumn = column;
            this.sortDirection = 'asc';
        }
        const container = document.querySelector('.advanced-issue-table').parentElement;
        this.renderTable(container);
    }
    
    toggleColumn(columnId, visible) {
        const column = this.columns.find(c => c.id === columnId);
        if (column) {
            column.visible = visible;
            const container = document.querySelector('.advanced-issue-table').parentElement;
            this.renderTable(container);
        }
    }
    
    setColumnWidth(columnId, width) {
        const column = this.columns.find(c => c.id === columnId);
        if (column) {
            column.width = parseInt(width);
        }
    }
    
    resetColumns() {
        this.columns.forEach(col => {
            col.visible = ['key', 'type', 'summary', 'assignee', 'priority', 'status', 'updated'].includes(col.id);
        });
        const container = document.querySelector('.advanced-issue-table').parentElement;
        this.renderTable(container);
        this.showToast('Columns reset to default');
    }
    
    startResize(event, columnId) {
        event.preventDefault();
        this.resizing = { columnId, startX: event.clientX };
        
        const onMouseMove = (e) => {
            if (this.resizing) {
                const delta = e.clientX - this.resizing.startX;
                const column = this.columns.find(c => c.id === columnId);
                if (column) {
                    column.width = Math.max(50, column.width + delta);
                    this.resizing.startX = e.clientX;
                    const header = document.querySelector(`th[data-column="${columnId}"]`);
                    if (header) header.style.width = column.width + 'px';
                }
            }
        };
        
        const onMouseUp = () => {
            this.resizing = null;
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
        };
        
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
    }
    
    onColumnDragStart(event, columnId) {
        this.dragColumn = columnId;
        event.dataTransfer.effectAllowed = 'move';
    }
    
    onColumnDragOver(event) {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'move';
    }
    
    onColumnDrop(event, targetColumnId) {
        event.preventDefault();
        if (this.dragColumn && this.dragColumn !== targetColumnId) {
            const dragIndex = this.columns.findIndex(c => c.id === this.dragColumn);
            const dropIndex = this.columns.findIndex(c => c.id === targetColumnId);
            
            const [removed] = this.columns.splice(dragIndex, 1);
            this.columns.splice(dropIndex, 0, removed);
            
            const container = document.querySelector('.advanced-issue-table').parentElement;
            this.renderTable(container);
        }
        this.dragColumn = null;
    }
    
    shareFilter() {
        this.showToast('Share filter dialog');
    }
    
    toggleStar() {
        this.showToast('Filter starred');
    }
    
    closeSplit() {
        this.viewMode = 'list';
        const container = document.querySelector('.advanced-issue-table').parentElement;
        this.renderTable(container);
    }
    
    doExport() {
        const format = document.getElementById('exportFormat').value;
        this.showToast(`Exporting to ${format.toUpperCase()}...`);
    }
    
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Only handle if not in input/textarea
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
            
            switch(e.key) {
                case 'j':
                    // Next issue
                    this.showToast('Next issue (J)');
                    break;
                case 'k':
                    // Previous issue
                    this.showToast('Previous issue (K)');
                    break;
                case 'x':
                    // Toggle selection
                    this.showToast('Toggle selection (X)');
                    break;
                case 'o':
                case 'Enter':
                    // Open issue
                    this.showToast('Open issue (O/Enter)');
                    break;
                case 'e':
                    // Edit issue
                    this.showToast('Edit issue (E)');
                    break;
            }
        });
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
const issueTableAdvanced = new IssueTableAdvanced();
