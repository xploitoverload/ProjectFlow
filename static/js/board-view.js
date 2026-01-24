/**
 * Board View - Complete Kanban & Scrum Features
 * Swimlanes, WIP limits, Card customization, Epics panel, Version releases
 */

class BoardView {
    constructor() {
        this.boardType = 'scrum'; // 'scrum' or 'kanban'
        this.swimlaneBy = 'none'; // 'none', 'assignee', 'epic', 'priority', 'custom'
        this.showEpicsPanel = true;
        this.showVersionsPanel = true;
        this.collapsedColumns = new Set();
        
        this.columns = [
            { id: 'backlog', name: 'Backlog', wipLimit: null, issueCount: 15 },
            { id: 'selected', name: 'Selected for Development', wipLimit: null, issueCount: 8 },
            { id: 'inprogress', name: 'In Progress', wipLimit: 5, issueCount: 6 },
            { id: 'review', name: 'In Review', wipLimit: 3, issueCount: 4 },
            { id: 'done', name: 'Done', wipLimit: null, issueCount: 23 }
        ];
        
        this.epics = [
            { id: 'epic1', key: 'TEST-100', name: 'User Authentication', color: '#0969da', completed: 5, total: 12, progress: 42 },
            { id: 'epic2', key: 'TEST-101', name: 'Payment Integration', color: '#6639ba', completed: 3, total: 8, progress: 38 },
            { id: 'epic3', key: 'TEST-102', name: 'Dashboard Redesign', color: '#36b37e', completed: 8, total: 10, progress: 80 }
        ];
        
        this.versions = [
            { id: 'v1', name: 'v2.0.0', releaseDate: 'Jan 31, 2025', completed: 18, total: 25, progress: 72 },
            { id: 'v2', name: 'v2.1.0', releaseDate: 'Feb 28, 2025', completed: 5, total: 15, progress: 33 }
        ];
        
        this.cardFields = ['key', 'summary', 'assignee', 'priority', 'estimate', 'labels'];
        this.cardColors = 'priority'; // 'priority', 'assignee', 'issueType', 'epic'
        this.showAgingIndicator = true;
        
        this.draggedCard = null;
        this.filteredEpic = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        console.log('Board View initialized');
    }
    
    render(container) {
        container.innerHTML = `
            <div class="board-view-container">
                ${this.renderToolbar()}
                <div class="board-content">
                    ${this.renderSidePanels()}
                    ${this.renderBoard()}
                </div>
            </div>
        `;
        
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }
    
    renderToolbar() {
        return `
            <div class="board-toolbar">
                <div class="toolbar-left">
                    <div class="board-type-toggle">
                        <button class="toggle-btn ${this.boardType === 'scrum' ? 'active' : ''}" 
                            onclick="boardView.switchBoardType('scrum')">
                            Scrum Board
                        </button>
                        <button class="toggle-btn ${this.boardType === 'kanban' ? 'active' : ''}" 
                            onclick="boardView.switchBoardType('kanban')">
                            Kanban Board
                        </button>
                    </div>
                    
                    <div class="swimlane-selector">
                        <button class="btn btn-secondary dropdown-trigger" onclick="boardView.toggleSwimlaneMenu(this)">
                            <i data-lucide="columns"></i>
                            Swimlanes: ${this.getSwimlaneLabel()}
                            <i data-lucide="chevron-down"></i>
                        </button>
                        <div class="dropdown-menu">
                            <button onclick="boardView.setSwimlane('none')">
                                <i data-lucide="x"></i> None
                            </button>
                            <button onclick="boardView.setSwimlane('assignee')">
                                <i data-lucide="user"></i> Assignee
                            </button>
                            <button onclick="boardView.setSwimlane('epic')">
                                <i data-lucide="bookmark"></i> Epic
                            </button>
                            <button onclick="boardView.setSwimlane('priority')">
                                <i data-lucide="alert-triangle"></i> Priority
                            </button>
                            <button onclick="boardView.setSwimlane('custom')">
                                <i data-lucide="sliders"></i> Custom Field
                            </button>
                        </div>
                    </div>
                    
                    <button class="btn btn-secondary" onclick="boardView.customizeCards()">
                        <i data-lucide="settings"></i>
                        Card Layout
                    </button>
                    
                    <button class="btn btn-secondary" onclick="boardView.quickFilters()">
                        <i data-lucide="filter"></i>
                        Quick Filters
                    </button>
                </div>
                
                <div class="toolbar-right">
                    <button class="btn btn-secondary ${this.showEpicsPanel ? 'active' : ''}" 
                        onclick="boardView.toggleEpicsPanel()">
                        <i data-lucide="bookmark"></i>
                        Epics
                    </button>
                    <button class="btn btn-secondary ${this.showVersionsPanel ? 'active' : ''}" 
                        onclick="boardView.toggleVersionsPanel()">
                        <i data-lucide="package"></i>
                        Versions
                    </button>
                    <button class="btn btn-primary" onclick="boardView.createIssue()">
                        <i data-lucide="plus"></i>
                        Create Issue
                    </button>
                </div>
            </div>
        `;
    }
    
    renderSidePanels() {
        return `
            <div class="board-side-panels">
                ${this.showEpicsPanel ? this.renderEpicsPanel() : ''}
                ${this.showVersionsPanel ? this.renderVersionsPanel() : ''}
            </div>
        `;
    }
    
    renderEpicsPanel() {
        return `
            <div class="side-panel epics-panel">
                <div class="panel-header">
                    <h4>Epics</h4>
                    <button class="btn-icon-sm" onclick="boardView.toggleEpicsPanel()">
                        <i data-lucide="x"></i>
                    </button>
                </div>
                <div class="panel-body">
                    <div class="epic-filter-all ${!this.filteredEpic ? 'active' : ''}" 
                        onclick="boardView.filterByEpic(null)">
                        <span>All Epics</span>
                        <span class="epic-count">${this.getTotalIssueCount()}</span>
                    </div>
                    ${this.epics.map(epic => `
                        <div class="epic-item ${this.filteredEpic === epic.id ? 'active' : ''}" 
                            style="border-left-color: ${epic.color}"
                            onclick="boardView.filterByEpic('${epic.id}')">
                            <div class="epic-header">
                                <span class="epic-key">${epic.key}</span>
                                <span class="epic-name">${epic.name}</span>
                            </div>
                            <div class="epic-progress">
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: ${epic.progress}%; background: ${epic.color}"></div>
                                </div>
                                <span class="progress-text">${epic.completed}/${epic.total}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    renderVersionsPanel() {
        return `
            <div class="side-panel versions-panel">
                <div class="panel-header">
                    <h4>Versions</h4>
                    <button class="btn-icon-sm" onclick="boardView.toggleVersionsPanel()">
                        <i data-lucide="x"></i>
                    </button>
                </div>
                <div class="panel-body">
                    ${this.versions.map(version => `
                        <div class="version-item">
                            <div class="version-header">
                                <span class="version-name">${version.name}</span>
                                <span class="version-date">${version.releaseDate}</span>
                            </div>
                            <div class="version-progress">
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: ${version.progress}%"></div>
                                </div>
                                <span class="progress-text">${version.completed}/${version.total} issues</span>
                            </div>
                            <button class="btn-link" onclick="boardView.viewVersion('${version.id}')">
                                View release
                                <i data-lucide="arrow-right"></i>
                            </button>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    renderBoard() {
        return `
            <div class="board-main">
                <div class="board-columns-container">
                    ${this.renderColumns()}
                </div>
            </div>
        `;
    }
    
    renderColumns() {
        return this.columns.map(column => {
            const isCollapsed = this.collapsedColumns.has(column.id);
            const wipExceeded = column.wipLimit && column.issueCount > column.wipLimit;
            
            return `
                <div class="board-column ${isCollapsed ? 'collapsed' : ''} ${wipExceeded ? 'wip-exceeded' : ''}" 
                    data-column-id="${column.id}">
                    <div class="column-header">
                        <div class="column-header-top">
                            <button class="column-collapse-btn" onclick="boardView.toggleColumn('${column.id}')">
                                <i data-lucide="chevron-${isCollapsed ? 'right' : 'left'}"></i>
                            </button>
                            <h3 class="column-name">${column.name}</h3>
                            <span class="column-count ${wipExceeded ? 'wip-warning' : ''}">${column.issueCount}</span>
                            ${column.wipLimit ? `<span class="wip-limit">/ ${column.wipLimit}</span>` : ''}
                            <button class="column-menu-btn" onclick="boardView.openColumnMenu('${column.id}', this)">
                                <i data-lucide="more-horizontal"></i>
                            </button>
                        </div>
                        ${column.wipLimit && wipExceeded ? `
                            <div class="wip-warning-banner">
                                <i data-lucide="alert-triangle"></i>
                                WIP limit exceeded!
                            </div>
                        ` : ''}
                    </div>
                    
                    <div class="column-body" 
                        ondrop="boardView.onDrop(event, '${column.id}')"
                        ondragover="boardView.onDragOver(event)">
                        ${!isCollapsed ? this.renderCards(column.id) : ''}
                    </div>
                    
                    ${!isCollapsed ? `
                        <button class="column-create-btn" onclick="boardView.quickCreateIssue('${column.id}')">
                            <i data-lucide="plus"></i>
                            Create issue
                        </button>
                    ` : ''}
                </div>
            `;
        }).join('');
    }
    
    renderCards(columnId) {
        // Mock data - would come from API
        const cards = [
            { id: 'card1', key: 'TEST-142', summary: 'Implement user authentication', assignee: 'John Doe', priority: 'High', estimate: 8, labels: ['auth', 'security'], daysInColumn: 3, epic: 'epic1' },
            { id: 'card2', key: 'TEST-141', summary: 'Fix memory leak in cache', assignee: 'Jane Smith', priority: 'Critical', estimate: 5, labels: ['bug'], daysInColumn: 5, epic: 'epic1' },
            { id: 'card3', key: 'TEST-140', summary: 'Update dependencies', assignee: null, priority: 'Medium', estimate: 3, labels: ['maintenance'], daysInColumn: 1, epic: null }
        ];
        
        // Filter by epic if one is selected
        const filteredCards = this.filteredEpic 
            ? cards.filter(card => card.epic === this.filteredEpic)
            : cards;
        
        if (this.swimlaneBy === 'none') {
            return filteredCards.map(card => this.renderCard(card)).join('');
        } else {
            return this.renderSwimlanes(filteredCards);
        }
    }
    
    renderCard(card) {
        const priorityColors = {
            'Critical': '#cf222e',
            'High': '#fb8500',
            'Medium': '#0969da',
            'Low': '#57606a'
        };
        
        const borderColor = this.cardColors === 'priority' ? priorityColors[card.priority] : '#d0d7de';
        const agingClass = this.showAgingIndicator && card.daysInColumn > 3 ? 'aging' : '';
        
        return `
            <div class="issue-card ${agingClass}" 
                data-card-id="${card.id}"
                style="border-left-color: ${borderColor}"
                draggable="true"
                ondragstart="boardView.onDragStart(event, '${card.id}')"
                onclick="boardView.openIssue('${card.key}')">
                ${this.showAgingIndicator && card.daysInColumn > 3 ? `
                    <div class="aging-indicator">
                        <i data-lucide="clock"></i>
                        ${card.daysInColumn} days
                    </div>
                ` : ''}
                
                <div class="card-header">
                    <a href="#" class="card-key" onclick="event.stopPropagation(); boardView.openIssue('${card.key}')">${card.key}</a>
                    <div class="card-actions">
                        <button class="card-action-btn" onclick="event.stopPropagation(); boardView.quickEdit('${card.id}')" title="Quick Edit">
                            <i data-lucide="edit-2"></i>
                        </button>
                    </div>
                </div>
                
                <div class="card-summary">${card.summary}</div>
                
                <div class="card-footer">
                    <div class="card-meta">
                        ${card.assignee ? `
                            <img src="https://ui-avatars.com/api/?name=${card.assignee}" 
                                alt="${card.assignee}" 
                                class="card-avatar" 
                                title="${card.assignee}" />
                        ` : `
                            <div class="card-avatar unassigned" title="Unassigned">
                                <i data-lucide="user"></i>
                            </div>
                        `}
                        
                        <span class="card-priority priority-${card.priority.toLowerCase()}" title="${card.priority}">
                            <i data-lucide="alert-circle"></i>
                        </span>
                        
                        ${card.estimate ? `
                            <span class="card-estimate" title="Story Points">
                                ${card.estimate}
                            </span>
                        ` : ''}
                    </div>
                    
                    ${card.labels.length > 0 ? `
                        <div class="card-labels">
                            ${card.labels.map(label => `<span class="card-label">${label}</span>`).join('')}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    renderSwimlanes(cards) {
        // Group cards by swimlane
        const swimlanes = this.groupCardsBySwimlane(cards);
        
        return Object.entries(swimlanes).map(([swimlaneName, swimlaneCards]) => `
            <div class="swimlane">
                <div class="swimlane-header">
                    <span class="swimlane-name">${swimlaneName}</span>
                    <span class="swimlane-count">${swimlaneCards.length}</span>
                </div>
                <div class="swimlane-cards">
                    ${swimlaneCards.map(card => this.renderCard(card)).join('')}
                </div>
            </div>
        `).join('');
    }
    
    groupCardsBySwimlane(cards) {
        const grouped = {};
        
        cards.forEach(card => {
            let key;
            switch(this.swimlaneBy) {
                case 'assignee':
                    key = card.assignee || 'Unassigned';
                    break;
                case 'priority':
                    key = card.priority;
                    break;
                case 'epic':
                    key = card.epic ? `Epic ${card.epic}` : 'No Epic';
                    break;
                default:
                    key = 'Default';
            }
            
            if (!grouped[key]) grouped[key] = [];
            grouped[key].push(card);
        });
        
        return grouped;
    }
    
    // Methods
    switchBoardType(type) {
        this.boardType = type;
        const container = document.querySelector('.board-view-container').parentElement;
        this.render(container);
    }
    
    setSwimlane(type) {
        this.swimlaneBy = type;
        const container = document.querySelector('.board-view-container').parentElement;
        this.render(container);
    }
    
    getSwimlaneLabel() {
        const labels = {
            'none': 'None',
            'assignee': 'Assignee',
            'epic': 'Epic',
            'priority': 'Priority',
            'custom': 'Custom Field'
        };
        return labels[this.swimlaneBy] || 'None';
    }
    
    toggleColumn(columnId) {
        if (this.collapsedColumns.has(columnId)) {
            this.collapsedColumns.delete(columnId);
        } else {
            this.collapsedColumns.add(columnId);
        }
        const container = document.querySelector('.board-view-container').parentElement;
        this.render(container);
    }
    
    toggleEpicsPanel() {
        this.showEpicsPanel = !this.showEpicsPanel;
        const container = document.querySelector('.board-view-container').parentElement;
        this.render(container);
    }
    
    toggleVersionsPanel() {
        this.showVersionsPanel = !this.showVersionsPanel;
        const container = document.querySelector('.board-view-container').parentElement;
        this.render(container);
    }
    
    filterByEpic(epicId) {
        this.filteredEpic = epicId;
        const container = document.querySelector('.board-view-container').parentElement;
        this.render(container);
    }
    
    customizeCards() {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal card-layout-modal">
                <div class="modal-header">
                    <h3>Card Layout</h3>
                    <button class="btn-icon" onclick="this.closest('.modal-overlay').remove()">
                        <i data-lucide="x"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label>Fields to show</label>
                        <div class="checkbox-group">
                            <label><input type="checkbox" checked /> Key</label>
                            <label><input type="checkbox" checked /> Summary</label>
                            <label><input type="checkbox" checked /> Assignee</label>
                            <label><input type="checkbox" checked /> Priority</label>
                            <label><input type="checkbox" checked /> Story Points</label>
                            <label><input type="checkbox" checked /> Labels</label>
                            <label><input type="checkbox" /> Epic</label>
                            <label><input type="checkbox" /> Due Date</label>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Card colors based on</label>
                        <select>
                            <option value="priority">Priority</option>
                            <option value="assignee">Assignee</option>
                            <option value="issueType">Issue Type</option>
                            <option value="epic">Epic</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" checked /> Show aging indicator</label>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                    <button class="btn btn-primary" onclick="boardView.saveCardLayout(); this.closest('.modal-overlay').remove()">Save</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        if (typeof lucide !== 'undefined') lucide.createIcons();
    }
    
    openColumnMenu(columnId, button) {
        const menu = document.createElement('div');
        menu.className = 'context-menu';
        menu.innerHTML = `
            <button onclick="boardView.renameColumn('${columnId}'); this.closest('.context-menu').remove()">
                <i data-lucide="edit-2"></i> Rename
            </button>
            <button onclick="boardView.setWIPLimit('${columnId}'); this.closest('.context-menu').remove()">
                <i data-lucide="alert-triangle"></i> Set WIP Limit
            </button>
            <button onclick="boardView.deleteColumn('${columnId}'); this.closest('.context-menu').remove()" class="text-danger">
                <i data-lucide="trash-2"></i> Delete
            </button>
        `;
        
        const rect = button.getBoundingClientRect();
        menu.style.position = 'fixed';
        menu.style.top = rect.bottom + 'px';
        menu.style.left = rect.left + 'px';
        menu.style.zIndex = '10000';
        
        document.body.appendChild(menu);
        if (typeof lucide !== 'undefined') lucide.createIcons();
        
        // Close menu on click outside
        setTimeout(() => {
            document.addEventListener('click', function closeMenu(e) {
                if (!menu.contains(e.target)) {
                    menu.remove();
                    document.removeEventListener('click', closeMenu);
                }
            });
        }, 0);
    }
    
    onDragStart(event, cardId) {
        this.draggedCard = cardId;
        event.dataTransfer.effectAllowed = 'move';
        event.target.classList.add('dragging');
    }
    
    onDragOver(event) {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'move';
    }
    
    onDrop(event, columnId) {
        event.preventDefault();
        if (this.draggedCard) {
            console.log(`Moving card ${this.draggedCard} to column ${columnId}`);
            this.showToast(`Issue moved to ${columnId}`);
            this.draggedCard = null;
        }
    }
    
    quickEdit(cardId) {
        this.showToast(`Quick edit for card ${cardId}`);
    }
    
    openIssue(issueKey) {
        this.showToast(`Opening issue ${issueKey}`);
    }
    
    getTotalIssueCount() {
        return this.columns.reduce((sum, col) => sum + col.issueCount, 0);
    }
    
    setupEventListeners() {
        document.addEventListener('dragend', (e) => {
            const dragging = document.querySelector('.dragging');
            if (dragging) dragging.classList.remove('dragging');
        });
    }
    
    toggleSwimlaneMenu(button) {
        const menu = button.nextElementSibling;
        menu.classList.toggle('show');
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
const boardView = new BoardView();
