/**
 * Issue Navigator - Complete Jira Issue Navigator Implementation
 * Features: JQL Builder (Basic/Advanced/AI), Search, Filters, Multiple Views,
 * Native Issue Table, Export, Bulk Actions, Column Configuration
 */

class IssueNavigator {
    constructor() {
        this.currentView = 'list'; // list, split, detail
        this.issues = [];
        this.filteredIssues = [];
        this.selectedIssues = new Set();
        this.currentFilter = null;
        this.jqlQuery = '';
        this.jqlMode = 'basic'; // basic, advanced, ai
        this.columns = [
            { id: 'key', name: 'Key', width: 120, visible: true, sortable: true },
            { id: 'type', name: 'Type', width: 80, visible: true, sortable: true },
            { id: 'summary', name: 'Summary', width: 400, visible: true, sortable: true },
            { id: 'status', name: 'Status', width: 120, visible: true, sortable: true },
            { id: 'assignee', name: 'Assignee', width: 150, visible: true, sortable: true },
            { id: 'priority', name: 'Priority', width: 100, visible: true, sortable: true },
            { id: 'created', name: 'Created', width: 120, visible: true, sortable: true },
            { id: 'updated', name: 'Updated', width: 120, visible: true, sortable: true }
        ];
        this.sortField = 'key';
        this.sortOrder = 'asc';
        this.refinementFilters = {
            assignee: [],
            status: [],
            type: [],
            priority: []
        };
        
        this.init();
    }

    async init() {
        await this.loadIssues();
        this.createNavigatorUI();
        this.setupEventListeners();
        this.applyFilters();
        // Expose to window for onclick handlers
        window.issueNavigator = this;
    }

    async loadIssues() {
        try {
            const response = await fetch('/api/issues');
            this.issues = await response.json();
            this.filteredIssues = [...this.issues];
        } catch (error) {
            console.error('Failed to load issues:', error);
            this.loadMockData();
        }
    }

    loadMockData() {
        this.issues = [
            {
                id: 1, key: 'PROJ-123', type: 'Story', summary: 'Implement user authentication',
                status: 'In Progress', assignee: 'John Doe', priority: 'High',
                created: '2024-01-15', updated: '2024-01-20', project: 'PROJ',
                description: 'As a user, I want to login securely', labels: ['backend', 'security']
            },
            {
                id: 2, key: 'PROJ-124', type: 'Bug', summary: 'Fix navigation bar styling',
                status: 'To Do', assignee: 'Jane Smith', priority: 'Medium',
                created: '2024-01-16', updated: '2024-01-16', project: 'PROJ',
                description: 'Navigation bar breaks on mobile', labels: ['frontend', 'ui']
            },
            {
                id: 3, key: 'PROJ-125', type: 'Task', summary: 'Update documentation',
                status: 'Done', assignee: 'John Doe', priority: 'Low',
                created: '2024-01-10', updated: '2024-01-18', project: 'PROJ',
                description: 'Update README and API docs', labels: ['docs']
            }
        ];
        this.filteredIssues = [...this.issues];
    }

    createNavigatorUI() {
        const html = `
            <!-- Issue Navigator Container -->
            <div class="issue-navigator" id="issueNavigator">
                <!-- Navigator Header -->
                <div class="navigator-header">
                    <div class="header-top">
                        <div class="header-left">
                            <h1 class="navigator-title">Issues</h1>
                            <button class="btn-icon" onclick="issueNavigator.refreshIssues()" title="Refresh">
                                <i data-lucide="refresh-cw"></i>
                            </button>
                        </div>
                        <div class="header-right">
                            <div class="view-toggles">
                                <button class="btn-icon ${this.currentView === 'list' ? 'active' : ''}" 
                                        onclick="issueNavigator.switchView('list')" 
                                        title="List View">
                                    <i data-lucide="list"></i>
                                </button>
                                <button class="btn-icon ${this.currentView === 'split' ? 'active' : ''}" 
                                        onclick="issueNavigator.switchView('split')" 
                                        title="Split View">
                                    <i data-lucide="columns"></i>
                                </button>
                                <button class="btn-icon ${this.currentView === 'detail' ? 'active' : ''}" 
                                        onclick="issueNavigator.switchView('detail')" 
                                        title="Detail View">
                                    <i data-lucide="layout"></i>
                                </button>
                            </div>
                            <button class="btn-secondary" onclick="issueNavigator.openColumnConfig()">
                                <i data-lucide="columns"></i>
                                Columns
                            </button>
                            <button class="btn-secondary" onclick="issueNavigator.exportIssues()">
                                <i data-lucide="download"></i>
                                Export
                            </button>
                            <div class="dropdown">
                                <button class="btn-icon" onclick="issueNavigator.toggleActionsMenu()">
                                    <i data-lucide="more-horizontal"></i>
                                </button>
                                <div class="dropdown-menu" id="navigatorActionsMenu" style="display: none;">
                                    <button class="dropdown-item" onclick="issueNavigator.saveFilter()">
                                        <i data-lucide="save"></i>
                                        Save filter
                                    </button>
                                    <button class="dropdown-item" onclick="issueNavigator.resetFilters()">
                                        <i data-lucide="rotate-ccw"></i>
                                        Reset filters
                                    </button>
                                    <button class="dropdown-item" onclick="issueNavigator.copyFilterUrl()">
                                        <i data-lucide="link"></i>
                                        Copy filter URL
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- JQL Builder -->
                    <div class="jql-builder">
                        <div class="jql-mode-switcher">
                            <button class="mode-btn ${this.jqlMode === 'basic' ? 'active' : ''}" 
                                    onclick="issueNavigator.switchJQLMode('basic')">
                                Basic
                            </button>
                            <button class="mode-btn ${this.jqlMode === 'advanced' ? 'active' : ''}" 
                                    onclick="issueNavigator.switchJQLMode('advanced')">
                                JQL
                            </button>
                            <button class="mode-btn ${this.jqlMode === 'ai' ? 'active' : ''}" 
                                    onclick="issueNavigator.switchJQLMode('ai')">
                                <i data-lucide="sparkles"></i>
                                AI
                            </button>
                        </div>

                        <!-- Basic Mode -->
                        <div class="jql-mode-content" id="jqlBasicMode" style="display: ${this.jqlMode === 'basic' ? 'flex' : 'none'}">
                            <div class="basic-filters">
                                <div class="filter-group">
                                    <label>Project</label>
                                    <select class="filter-select" onchange="issueNavigator.applyBasicFilters()">
                                        <option value="">All projects</option>
                                        <option value="PROJ">PROJ</option>
                                        <option value="TEST">TEST</option>
                                    </select>
                                </div>
                                <div class="filter-group">
                                    <label>Type</label>
                                    <select class="filter-select" onchange="issueNavigator.applyBasicFilters()">
                                        <option value="">All types</option>
                                        <option value="Story">Story</option>
                                        <option value="Bug">Bug</option>
                                        <option value="Task">Task</option>
                                    </select>
                                </div>
                                <div class="filter-group">
                                    <label>Status</label>
                                    <select class="filter-select" onchange="issueNavigator.applyBasicFilters()">
                                        <option value="">All statuses</option>
                                        <option value="To Do">To Do</option>
                                        <option value="In Progress">In Progress</option>
                                        <option value="Done">Done</option>
                                    </select>
                                </div>
                                <div class="filter-group">
                                    <label>Assignee</label>
                                    <select class="filter-select" onchange="issueNavigator.applyBasicFilters()">
                                        <option value="">All assignees</option>
                                        <option value="currentUser()">Current user</option>
                                        <option value="unassigned">Unassigned</option>
                                    </select>
                                </div>
                                <button class="btn-text" onclick="issueNavigator.addFilter()">
                                    <i data-lucide="plus"></i>
                                    Add filter
                                </button>
                            </div>
                        </div>

                        <!-- Advanced JQL Mode -->
                        <div class="jql-mode-content" id="jqlAdvancedMode" style="display: ${this.jqlMode === 'advanced' ? 'block' : 'none'}">
                            <div class="jql-editor">
                                <textarea class="jql-input" 
                                          placeholder="Enter JQL query... (e.g., project = PROJ AND status = 'In Progress')"
                                          onkeyup="issueNavigator.handleJQLInput(event)">${this.jqlQuery}</textarea>
                                <div class="jql-actions">
                                    <button class="btn-secondary" onclick="issueNavigator.executeJQL()">
                                        <i data-lucide="play"></i>
                                        Search
                                    </button>
                                    <button class="btn-text" onclick="issueNavigator.clearJQL()">
                                        Clear
                                    </button>
                                    <button class="btn-text" onclick="issueNavigator.showJQLHelp()">
                                        <i data-lucide="help-circle"></i>
                                        JQL help
                                    </button>
                                </div>
                                <div class="jql-suggestions" id="jqlSuggestions" style="display: none;"></div>
                            </div>
                        </div>

                        <!-- AI Mode -->
                        <div class="jql-mode-content" id="jqlAIMode" style="display: ${this.jqlMode === 'ai' ? 'block' : 'none'}">
                            <div class="ai-query-box">
                                <div class="ai-icon">
                                    <i data-lucide="sparkles"></i>
                                </div>
                                <textarea class="ai-input" 
                                          placeholder="Describe what you're looking for in plain English...&#10;Example: Show me all high priority bugs assigned to me"
                                          onkeyup="issueNavigator.handleAIInput(event)"></textarea>
                                <button class="btn-primary" onclick="issueNavigator.convertToJQL()">
                                    <i data-lucide="sparkles"></i>
                                    Generate JQL
                                </button>
                            </div>
                            <div class="ai-result" id="aiResult" style="display: none;">
                                <div class="ai-result-header">
                                    <span>Generated JQL:</span>
                                    <button class="btn-text-sm" onclick="issueNavigator.useGeneratedJQL()">Use this query</button>
                                </div>
                                <code class="ai-jql"></code>
                            </div>
                        </div>
                    </div>

                    <!-- Refinement Bar -->
                    <div class="refinement-bar" id="refinementBar">
                        <div class="refinement-filters">
                            <button class="refinement-chip" onclick="issueNavigator.openRefinementFilter('assignee')">
                                <span>Assignee</span>
                                <i data-lucide="chevron-down"></i>
                            </button>
                            <button class="refinement-chip" onclick="issueNavigator.openRefinementFilter('status')">
                                <span>Status</span>
                                <i data-lucide="chevron-down"></i>
                            </button>
                            <button class="refinement-chip" onclick="issueNavigator.openRefinementFilter('type')">
                                <span>Type</span>
                                <i data-lucide="chevron-down"></i>
                            </button>
                            <button class="refinement-chip" onclick="issueNavigator.openRefinementFilter('priority')">
                                <span>Priority</span>
                                <i data-lucide="chevron-down"></i>
                            </button>
                        </div>
                        <div class="active-refinements" id="activeRefinements"></div>
                    </div>
                </div>

                <!-- Navigator Content -->
                <div class="navigator-content" id="navigatorContent">
                    <!-- List View -->
                    <div class="list-view" id="listView" style="display: ${this.currentView === 'list' ? 'block' : 'none'}">
                        <div class="issue-table-container">
                            <table class="issue-table" id="issueTable">
                                <thead>
                                    <tr>
                                        <th class="checkbox-col">
                                            <input type="checkbox" onchange="issueNavigator.toggleSelectAll(this.checked)">
                                        </th>
                                        ${this.columns.filter(c => c.visible).map(col => `
                                            <th class="sortable ${this.sortField === col.id ? 'sorted-' + this.sortOrder : ''}" 
                                                style="width: ${col.width}px"
                                                onclick="issueNavigator.sortBy('${col.id}')">
                                                <div class="th-content">
                                                    <span>${col.name}</span>
                                                    ${col.sortable ? '<i data-lucide="chevron-down" class="sort-icon"></i>' : ''}
                                                </div>
                                                <div class="resize-handle"></div>
                                            </th>
                                        `).join('')}
                                    </tr>
                                </thead>
                                <tbody id="issueTableBody">
                                    <!-- Populated by JS -->
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <!-- Split View -->
                    <div class="split-view" id="splitView" style="display: ${this.currentView === 'split' ? 'flex' : 'none'}">
                        <div class="split-list">
                            <div id="splitIssueList"></div>
                        </div>
                        <div class="split-detail">
                            <div class="no-selection">
                                <i data-lucide="file-text"></i>
                                <p>Select an issue to view details</p>
                            </div>
                            <div id="splitIssueDetail" style="display: none;"></div>
                        </div>
                    </div>

                    <!-- Detail View -->
                    <div class="detail-view" id="detailView" style="display: ${this.currentView === 'detail' ? 'block' : 'none'}">
                        <div class="detail-cards" id="detailCards">
                            <!-- Populated by JS -->
                        </div>
                    </div>
                </div>

                <!-- Bulk Actions Toolbar -->
                <div class="bulk-actions-toolbar" id="bulkActionsToolbar" style="display: none;">
                    <div class="toolbar-left">
                        <span class="selected-count">0 selected</span>
                    </div>
                    <div class="toolbar-actions">
                        <button class="btn-secondary" onclick="issueNavigator.bulkEdit()">
                            <i data-lucide="edit-2"></i>
                            Edit
                        </button>
                        <button class="btn-secondary" onclick="issueNavigator.bulkMove()">
                            <i data-lucide="folder"></i>
                            Move
                        </button>
                        <button class="btn-secondary" onclick="issueNavigator.bulkTransition()">
                            <i data-lucide="git-branch"></i>
                            Transition
                        </button>
                        <button class="btn-secondary btn-danger" onclick="issueNavigator.bulkDelete()">
                            <i data-lucide="trash-2"></i>
                            Delete
                        </button>
                        <button class="btn-text" onclick="issueNavigator.clearSelection()">
                            Clear
                        </button>
                    </div>
                </div>
            </div>

            <!-- Column Configuration Modal -->
            <div class="modal" id="columnConfigModal" style="display: none;">
                <div class="modal-overlay" onclick="issueNavigator.closeColumnConfig()"></div>
                <div class="modal-content modal-medium">
                    <div class="modal-header">
                        <h2>Column Configuration</h2>
                        <button class="btn-icon" onclick="issueNavigator.closeColumnConfig()">
                            <i data-lucide="x"></i>
                        </button>
                    </div>
                    <div class="modal-body">
                        <div class="column-list" id="columnList">
                            <!-- Populated by JS -->
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn-secondary" onclick="issueNavigator.resetColumns()">Reset to default</button>
                        <button class="btn-primary" onclick="issueNavigator.saveColumns()">Save</button>
                    </div>
                </div>
            </div>
        `;

        // Insert into page
        const container = document.getElementById('issueNavigatorContainer') || document.body;
        container.innerHTML = html;

        // Render content
        this.renderIssues();

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    renderIssues() {
        if (this.currentView === 'list') {
            this.renderListView();
        } else if (this.currentView === 'split') {
            this.renderSplitView();
        } else if (this.currentView === 'detail') {
            this.renderDetailView();
        }
    }

    renderListView() {
        const tbody = document.getElementById('issueTableBody');
        if (!tbody) return;

        tbody.innerHTML = this.filteredIssues.map(issue => `
            <tr class="issue-row ${this.selectedIssues.has(issue.id) ? 'selected' : ''}" 
                onclick="issueNavigator.selectIssue(${issue.id}, event)">
                <td class="checkbox-col">
                    <input type="checkbox" 
                           ${this.selectedIssues.has(issue.id) ? 'checked' : ''}
                           onclick="event.stopPropagation(); issueNavigator.toggleIssueSelect(${issue.id})">
                </td>
                <td>
                    <a href="#/issue/${issue.key}" class="issue-key">${issue.key}</a>
                </td>
                <td>
                    <div class="issue-type">
                        <i data-lucide="${this.getTypeIcon(issue.type)}"></i>
                        <span>${issue.type}</span>
                    </div>
                </td>
                <td>
                    <div class="issue-summary">${issue.summary}</div>
                </td>
                <td>
                    <span class="status-badge status-${issue.status.toLowerCase().replace(' ', '-')}">
                        ${issue.status}
                    </span>
                </td>
                <td>
                    <div class="assignee">
                        <div class="avatar-sm">${this.getInitials(issue.assignee)}</div>
                        <span>${issue.assignee}</span>
                    </div>
                </td>
                <td>
                    <span class="priority-badge priority-${issue.priority.toLowerCase()}">
                        <i data-lucide="${this.getPriorityIcon(issue.priority)}"></i>
                        ${issue.priority}
                    </span>
                </td>
                <td>${this.formatDate(issue.created)}</td>
                <td>${this.formatDate(issue.updated)}</td>
            </tr>
        `).join('');

        if (window.lucide) {
            lucide.createIcons();
        }

        this.updateBulkActionsToolbar();
    }

    renderSplitView() {
        const listContainer = document.getElementById('splitIssueList');
        if (!listContainer) return;

        listContainer.innerHTML = this.filteredIssues.map(issue => `
            <div class="split-issue-card" onclick="issueNavigator.showIssueInSplit(${issue.id})">
                <div class="card-header">
                    <span class="issue-key">${issue.key}</span>
                    <span class="issue-type">
                        <i data-lucide="${this.getTypeIcon(issue.type)}"></i>
                    </span>
                </div>
                <div class="card-title">${issue.summary}</div>
                <div class="card-meta">
                    <span class="status-badge status-${issue.status.toLowerCase().replace(' ', '-')}">
                        ${issue.status}
                    </span>
                    <div class="assignee">
                        <div class="avatar-xs">${this.getInitials(issue.assignee)}</div>
                    </div>
                </div>
            </div>
        `).join('');

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    renderDetailView() {
        const container = document.getElementById('detailCards');
        if (!container) return;

        container.innerHTML = this.filteredIssues.map(issue => `
            <div class="detail-card">
                <div class="card-header">
                    <div class="header-left">
                        <span class="issue-type">
                            <i data-lucide="${this.getTypeIcon(issue.type)}"></i>
                            ${issue.type}
                        </span>
                        <a href="#/issue/${issue.key}" class="issue-key">${issue.key}</a>
                    </div>
                    <div class="header-right">
                        <button class="btn-icon" onclick="issueNavigator.openIssueDetail(${issue.id})">
                            <i data-lucide="external-link"></i>
                        </button>
                    </div>
                </div>
                <h3 class="card-title">${issue.summary}</h3>
                <div class="card-description">${issue.description}</div>
                <div class="card-meta">
                    <div class="meta-item">
                        <label>Status:</label>
                        <span class="status-badge status-${issue.status.toLowerCase().replace(' ', '-')}">
                            ${issue.status}
                        </span>
                    </div>
                    <div class="meta-item">
                        <label>Assignee:</label>
                        <div class="assignee">
                            <div class="avatar-sm">${this.getInitials(issue.assignee)}</div>
                            <span>${issue.assignee}</span>
                        </div>
                    </div>
                    <div class="meta-item">
                        <label>Priority:</label>
                        <span class="priority-badge priority-${issue.priority.toLowerCase()}">
                            <i data-lucide="${this.getPriorityIcon(issue.priority)}"></i>
                            ${issue.priority}
                        </span>
                    </div>
                    <div class="meta-item">
                        <label>Updated:</label>
                        <span>${this.formatDate(issue.updated)}</span>
                    </div>
                </div>
                ${issue.labels && issue.labels.length > 0 ? `
                    <div class="card-labels">
                        ${issue.labels.map(label => `<span class="label-tag">${label}</span>`).join('')}
                    </div>
                ` : ''}
            </div>
        `).join('');

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    setupEventListeners() {
        // Close dropdowns when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.dropdown')) {
                document.querySelectorAll('.dropdown-menu').forEach(menu => {
                    menu.style.display = 'none';
                });
            }
        });

        // Column resize
        this.setupColumnResize();

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + A - Select all
            if ((e.ctrlKey || e.metaKey) && e.key === 'a' && this.currentView === 'list') {
                e.preventDefault();
                this.selectAll();
            }
            
            // Delete - Bulk delete
            if (e.key === 'Delete' && this.selectedIssues.size > 0) {
                e.preventDefault();
                this.bulkDelete();
            }
            
            // Escape - Clear selection
            if (e.key === 'Escape' && this.selectedIssues.size > 0) {
                this.clearSelection();
            }
        });
    }

    setupColumnResize() {
        const table = document.getElementById('issueTable');
        if (!table) return;

        let resizing = null;
        let startX = 0;
        let startWidth = 0;

        table.addEventListener('mousedown', (e) => {
            if (e.target.classList.contains('resize-handle')) {
                resizing = e.target.parentElement;
                startX = e.pageX;
                startWidth = resizing.offsetWidth;
                document.body.style.cursor = 'col-resize';
                e.preventDefault();
            }
        });

        document.addEventListener('mousemove', (e) => {
            if (resizing) {
                const diff = e.pageX - startX;
                const newWidth = Math.max(50, startWidth + diff);
                resizing.style.width = newWidth + 'px';
            }
        });

        document.addEventListener('mouseup', () => {
            if (resizing) {
                const colId = resizing.textContent.trim();
                const col = this.columns.find(c => c.name === colId);
                if (col) {
                    col.width = parseInt(resizing.style.width);
                }
                resizing = null;
                document.body.style.cursor = '';
            }
        });
    }

    // View Switching
    switchView(view) {
        this.currentView = view;
        
        document.getElementById('listView').style.display = view === 'list' ? 'block' : 'none';
        document.getElementById('splitView').style.display = view === 'split' ? 'flex' : 'none';
        document.getElementById('detailView').style.display = view === 'detail' ? 'block' : 'none';
        
        document.querySelectorAll('.view-toggles .btn-icon').forEach(btn => {
            btn.classList.remove('active');
        });
        event.target.closest('.btn-icon').classList.add('active');
        
        this.renderIssues();
    }

    // JQL Mode Switching
    switchJQLMode(mode) {
        this.jqlMode = mode;
        
        document.querySelectorAll('.mode-btn').forEach(btn => btn.classList.remove('active'));
        event.target.closest('.mode-btn').classList.add('active');
        
        document.getElementById('jqlBasicMode').style.display = mode === 'basic' ? 'flex' : 'none';
        document.getElementById('jqlAdvancedMode').style.display = mode === 'advanced' ? 'block' : 'none';
        document.getElementById('jqlAIMode').style.display = mode === 'ai' ? 'block' : 'none';
    }

    // JQL Execution
    executeJQL() {
        const jqlInput = document.querySelector('.jql-input');
        this.jqlQuery = jqlInput.value.trim();
        
        if (!this.jqlQuery) {
            this.filteredIssues = [...this.issues];
        } else {
            // Parse and execute JQL (simplified)
            this.filteredIssues = this.parseJQL(this.jqlQuery);
        }
        
        this.renderIssues();
    }

    parseJQL(jql) {
        // Simplified JQL parser
        const lower = jql.toLowerCase();
        let filtered = [...this.issues];
        
        // Project filter
        const projectMatch = lower.match(/project\s*=\s*['"]?(\w+)['"]?/);
        if (projectMatch) {
            filtered = filtered.filter(i => i.project === projectMatch[1].toUpperCase());
        }
        
        // Status filter
        const statusMatch = lower.match(/status\s*=\s*['"]([^'"]+)['"]?/);
        if (statusMatch) {
            filtered = filtered.filter(i => i.status.toLowerCase() === statusMatch[1].toLowerCase());
        }
        
        // Assignee filter
        if (lower.includes('assignee = currentuser()')) {
            filtered = filtered.filter(i => i.assignee === 'John Doe'); // Mock current user
        }
        
        return filtered;
    }

    // AI JQL Generation
    async convertToJQL() {
        const aiInput = document.querySelector('.ai-input');
        const query = aiInput.value.trim();
        
        if (!query) return;
        
        // Mock AI conversion
        const generatedJQL = this.mockAIConversion(query);
        
        const resultDiv = document.getElementById('aiResult');
        resultDiv.querySelector('.ai-jql').textContent = generatedJQL;
        resultDiv.style.display = 'block';
    }

    mockAIConversion(query) {
        const lower = query.toLowerCase();
        
        if (lower.includes('high priority') && lower.includes('assigned to me')) {
            return 'priority = High AND assignee = currentUser()';
        }
        if (lower.includes('bugs')) {
            return 'type = Bug';
        }
        if (lower.includes('in progress')) {
            return 'status = "In Progress"';
        }
        
        return 'project = PROJ';
    }

    useGeneratedJQL() {
        const jql = document.querySelector('.ai-jql').textContent;
        this.switchJQLMode('advanced');
        document.querySelector('.jql-input').value = jql;
        this.executeJQL();
    }

    // Selection
    toggleIssueSelect(id) {
        if (this.selectedIssues.has(id)) {
            this.selectedIssues.delete(id);
        } else {
            this.selectedIssues.add(id);
        }
        this.renderIssues();
    }

    toggleSelectAll(checked) {
        if (checked) {
            this.selectAll();
        } else {
            this.clearSelection();
        }
    }

    selectAll() {
        this.filteredIssues.forEach(issue => this.selectedIssues.add(issue.id));
        this.renderIssues();
    }

    clearSelection() {
        this.selectedIssues.clear();
        this.renderIssues();
    }

    updateBulkActionsToolbar() {
        const toolbar = document.getElementById('bulkActionsToolbar');
        if (!toolbar) return;
        
        if (this.selectedIssues.size > 0) {
            toolbar.style.display = 'flex';
            toolbar.querySelector('.selected-count').textContent = `${this.selectedIssues.size} selected`;
        } else {
            toolbar.style.display = 'none';
        }
    }

    // Sorting
    sortBy(field) {
        if (this.sortField === field) {
            this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortField = field;
            this.sortOrder = 'asc';
        }
        
        this.filteredIssues.sort((a, b) => {
            const aVal = a[field];
            const bVal = b[field];
            const mult = this.sortOrder === 'asc' ? 1 : -1;
            
            if (aVal < bVal) return -1 * mult;
            if (aVal > bVal) return 1 * mult;
            return 0;
        });
        
        this.renderIssues();
    }

    // Column Configuration
    openColumnConfig() {
        const modal = document.getElementById('columnConfigModal');
        const list = document.getElementById('columnList');
        
        list.innerHTML = this.columns.map((col, idx) => `
            <div class="column-item">
                <input type="checkbox" id="col_${col.id}" ${col.visible ? 'checked' : ''}>
                <label for="col_${col.id}">${col.name}</label>
            </div>
        `).join('');
        
        modal.style.display = 'flex';
        if (window.lucide) lucide.createIcons();
    }

    closeColumnConfig() {
        document.getElementById('columnConfigModal').style.display = 'none';
    }

    saveColumns() {
        this.columns.forEach(col => {
            const checkbox = document.getElementById(`col_${col.id}`);
            col.visible = checkbox.checked;
        });
        this.closeColumnConfig();
        this.renderIssues();
    }

    resetColumns() {
        this.columns.forEach(col => col.visible = true);
        this.openColumnConfig();
    }

    // Export
    exportIssues() {
        const csv = this.convertToCSV(this.filteredIssues);
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'issues.csv';
        a.click();
        URL.revokeObjectURL(url);
    }

    convertToCSV(issues) {
        const headers = this.columns.filter(c => c.visible).map(c => c.name).join(',');
        const rows = issues.map(issue => 
            this.columns.filter(c => c.visible).map(c => issue[c.id] || '').join(',')
        ).join('\n');
        return headers + '\n' + rows;
    }

    // Bulk Actions
    bulkEdit() {
        if (window.bulkOperations) {
            bulkOperations.openBulkEdit(Array.from(this.selectedIssues));
        }
    }

    bulkMove() {
        alert(`Moving ${this.selectedIssues.size} issues`);
    }

    bulkTransition() {
        alert(`Transitioning ${this.selectedIssues.size} issues`);
    }

    bulkDelete() {
        if (confirm(`Delete ${this.selectedIssues.size} issues?`)) {
            this.selectedIssues.forEach(id => {
                const idx = this.issues.findIndex(i => i.id === id);
                if (idx !== -1) this.issues.splice(idx, 1);
            });
            this.clearSelection();
            this.applyFilters();
            this.renderIssues();
        }
    }

    // Utilities
    getTypeIcon(type) {
        const icons = { Story: 'bookmark', Bug: 'bug', Task: 'check-square', Epic: 'package' };
        return icons[type] || 'file';
    }

    getPriorityIcon(priority) {
        const icons = { High: 'arrow-up', Medium: 'minus', Low: 'arrow-down' };
        return icons[priority] || 'minus';
    }

    getInitials(name) {
        return name.split(' ').map(n => n[0]).join('').toUpperCase();
    }

    formatDate(date) {
        return new Date(date).toLocaleDateString();
    }

    applyBasicFilters() { /* Implementation */ }
    applyFilters() { this.filteredIssues = [...this.issues]; }
    refreshIssues() { this.loadIssues(); }
    toggleActionsMenu() { /* Implementation */ }
    addFilter() { /* Implementation */ }
    handleJQLInput(e) { /* Implementation */ }
    clearJQL() { document.querySelector('.jql-input').value = ''; }
    showJQLHelp() { alert('JQL Help'); }
    handleAIInput(e) { /* Implementation */ }
    openRefinementFilter(type) { /* Implementation */ }
    selectIssue(id, e) { if (!e.target.closest('input')) this.openIssueDetail(id); }
    openIssueDetail(id) { alert(`Open issue ${id}`); }
    showIssueInSplit(id) { /* Implementation */ }
    saveFilter() { alert('Save filter'); }
    resetFilters() { this.applyFilters(); this.renderIssues(); }
    copyFilterUrl() { alert('URL copied'); }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.issueNavigator = new IssueNavigator();
});
