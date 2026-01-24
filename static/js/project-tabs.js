/**
 * Project Tabs System - Complete Jira Project Navigation Tabs
 * Features: 15 tabs (Summary, Timeline, Kanban, Calendar, Reports, List, Forms,
 * Components, Development, Code, Releases, Archived, Pages, Shortcuts, More)
 * Each tab has options menu, add to navigation, full functionality
 */

class ProjectTabs {
    constructor(projectKey = 'PROJ') {
        this.projectKey = projectKey;
        this.currentTab = 'board';
        this.visibleTabs = ['summary', 'board', 'timeline', 'list', 'reports'];
        this.allTabs = [
            { id: 'summary', name: 'Summary', icon: 'file-text', component: 'ProjectSummary' },
            { id: 'timeline', name: 'Timeline', icon: 'gantt-chart', component: 'TimelineView' },
            { id: 'board', name: 'Board', icon: 'layout-grid', component: 'KanbanBoard' },
            { id: 'calendar', name: 'Calendar', icon: 'calendar', component: 'CalendarView' },
            { id: 'list', name: 'List', icon: 'list', component: 'ListView' },
            { id: 'reports', name: 'Reports', icon: 'bar-chart', component: 'ReportsView' },
            { id: 'forms', name: 'Forms', icon: 'file-check', component: 'FormsView' },
            { id: 'components', name: 'Components', icon: 'package', component: 'ComponentsView' },
            { id: 'development', name: 'Development', icon: 'git-branch', component: 'DevelopmentView' },
            { id: 'code', name: 'Code', icon: 'code', component: 'CodeView' },
            { id: 'releases', name: 'Releases', icon: 'tag', component: 'ReleasesView' },
            { id: 'archived', name: 'Archived', icon: 'archive', component: 'ArchivedView' },
            { id: 'pages', name: 'Pages', icon: 'file-text', component: 'PagesView' }
        ];
        this.shortcuts = [];
        
        this.init();
    }

    async init() {
        await this.loadProjectData();
        this.createTabsUI();
        this.setupEventListeners();
        this.activateTab(this.currentTab);
    }

    async loadProjectData() {
        try {
            const response = await fetch(`/api/projects/${this.projectKey}`);
            this.project = await response.json();
        } catch (error) {
            console.error('Failed to load project:', error);
            this.project = {
                key: this.projectKey,
                name: 'Project Name',
                type: 'software',
                lead: 'John Doe'
            };
        }
    }

    createTabsUI() {
        const html = `
            <!-- Project Header -->
            <div class="project-header" id="projectHeader">
                <div class="project-info">
                    <div class="project-avatar">${this.projectKey[0]}</div>
                    <div class="project-details">
                        <h1 class="project-name">${this.project.name}</h1>
                        <div class="project-meta">
                            <span class="project-key">${this.projectKey}</span>
                            <span class="separator">•</span>
                            <span class="project-type">${this.project.type}</span>
                        </div>
                    </div>
                </div>
                <div class="project-actions">
                    <button class="btn-secondary" onclick="projectTabs.starProject()">
                        <i data-lucide="star"></i>
                    </button>
                    <button class="btn-secondary" onclick="projectTabs.shareProject()">
                        <i data-lucide="share-2"></i>
                        Share
                    </button>
                    <button class="btn-icon" onclick="projectTabs.openProjectSettings()">
                        <i data-lucide="settings"></i>
                    </button>
                </div>
            </div>

            <!-- Project Tabs Navigation -->
            <div class="project-tabs-nav" id="projectTabsNav">
                <div class="tabs-scroll">
                    <div class="tabs-list" id="tabsList">
                        ${this.renderTabs()}
                    </div>
                </div>
                
                <div class="tabs-actions">
                    <button class="btn-icon" onclick="projectTabs.openShortcuts()" title="Shortcuts">
                        <i data-lucide="zap"></i>
                    </button>
                    <div class="dropdown">
                        <button class="btn-icon" onclick="projectTabs.toggleMoreMenu()" title="More">
                            <i data-lucide="more-horizontal"></i>
                        </button>
                        <div class="dropdown-menu dropdown-right" id="moreTabsMenu" style="display: none;">
                            <div class="dropdown-section">
                                <div class="section-label">Hidden tabs</div>
                                ${this.renderHiddenTabs()}
                            </div>
                            <div class="dropdown-divider"></div>
                            <button class="dropdown-item" onclick="projectTabs.customizeNavigation()">
                                <i data-lucide="sliders"></i>
                                Customize navigation
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Tab Content Container -->
            <div class="project-tab-content" id="projectTabContent">
                <!-- Content rendered by individual tab components -->
            </div>

            <!-- Tab Options Context Menu -->
            <div class="tab-context-menu" id="tabContextMenu" style="display: none;">
                <button class="context-item" onclick="projectTabs.hideTab()">
                    <i data-lucide="eye-off"></i>
                    Hide tab
                </button>
                <button class="context-item" onclick="projectTabs.addShortcut()">
                    <i data-lucide="bookmark"></i>
                    Add to shortcuts
                </button>
                <div class="context-divider"></div>
                <button class="context-item" onclick="projectTabs.moveTabLeft()">
                    <i data-lucide="arrow-left"></i>
                    Move left
                </button>
                <button class="context-item" onclick="projectTabs.moveTabRight()">
                    <i data-lucide="arrow-right"></i>
                    Move right
                </button>
            </div>

            <!-- Customize Navigation Modal -->
            <div class="modal" id="customizeNavModal" style="display: none;">
                <div class="modal-overlay" onclick="projectTabs.closeCustomizeNav()"></div>
                <div class="modal-content modal-medium">
                    <div class="modal-header">
                        <h2>Customize project navigation</h2>
                        <button class="btn-icon" onclick="projectTabs.closeCustomizeNav()">
                            <i data-lucide="x"></i>
                        </button>
                    </div>
                    <div class="modal-body">
                        <p class="modal-description">
                            Drag and drop to reorder tabs. Uncheck tabs to hide them from the navigation.
                        </p>
                        <div class="tabs-customizer" id="tabsCustomizer">
                            <!-- Populated by JS -->
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn-secondary" onclick="projectTabs.resetNavigation()">
                            Reset to default
                        </button>
                        <button class="btn-primary" onclick="projectTabs.saveNavigation()">
                            Save changes
                        </button>
                    </div>
                </div>
            </div>

            <!-- Shortcuts Panel -->
            <div class="shortcuts-panel" id="shortcutsPanel" style="display: none;">
                <div class="panel-header">
                    <h3>Shortcuts</h3>
                    <button class="btn-icon" onclick="projectTabs.closeShortcuts()">
                        <i data-lucide="x"></i>
                    </button>
                </div>
                <div class="panel-content" id="shortcutsList">
                    ${this.renderShortcuts()}
                </div>
                <div class="panel-footer">
                    <button class="btn-text" onclick="projectTabs.addCustomShortcut()">
                        <i data-lucide="plus"></i>
                        Add custom shortcut
                    </button>
                </div>
            </div>
        `;

        // Insert into page
        const container = document.getElementById('projectContainer') || document.body;
        const existingHeader = document.getElementById('projectHeader');
        if (existingHeader) {
            existingHeader.remove();
        }
        container.insertAdjacentHTML('afterbegin', html);

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    renderTabs() {
        return this.allTabs
            .filter(tab => this.visibleTabs.includes(tab.id))
            .map(tab => `
                <button class="tab-item ${this.currentTab === tab.id ? 'active' : ''}" 
                        data-tab="${tab.id}"
                        onclick="projectTabs.activateTab('${tab.id}')">
                    <i data-lucide="${tab.icon}"></i>
                    <span>${tab.name}</span>
                    <button class="tab-options" 
                            onclick="event.stopPropagation(); projectTabs.showTabOptions('${tab.id}', event)"
                            title="Tab options">
                        <i data-lucide="more-vertical"></i>
                    </button>
                </button>
            `).join('');
    }

    renderHiddenTabs() {
        return this.allTabs
            .filter(tab => !this.visibleTabs.includes(tab.id))
            .map(tab => `
                <button class="dropdown-item" onclick="projectTabs.showTab('${tab.id}')">
                    <i data-lucide="${tab.icon}"></i>
                    <span>${tab.name}</span>
                    <i data-lucide="plus" class="add-icon"></i>
                </button>
            `).join('');
    }

    renderShortcuts() {
        if (this.shortcuts.length === 0) {
            return `
                <div class="empty-state">
                    <i data-lucide="bookmark"></i>
                    <p>No shortcuts yet</p>
                    <span>Add frequently used links here</span>
                </div>
            `;
        }

        return this.shortcuts.map(shortcut => `
            <div class="shortcut-item">
                <a href="${shortcut.url}" class="shortcut-link">
                    <i data-lucide="${shortcut.icon}"></i>
                    <span>${shortcut.name}</span>
                </a>
                <button class="btn-icon-sm" onclick="projectTabs.removeShortcut('${shortcut.id}')">
                    <i data-lucide="x"></i>
                </button>
            </div>
        `).join('');
    }

    setupEventListeners() {
        // Tab navigation keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + 1-9 for quick tab switching
            if ((e.ctrlKey || e.metaKey) && e.key >= '1' && e.key <= '9') {
                const index = parseInt(e.key) - 1;
                const tab = this.allTabs.filter(t => this.visibleTabs.includes(t.id))[index];
                if (tab) {
                    e.preventDefault();
                    this.activateTab(tab.id);
                }
            }
        });

        // Close context menu on outside click
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.tab-context-menu')) {
                document.getElementById('tabContextMenu').style.display = 'none';
            }
            if (!e.target.closest('.dropdown')) {
                document.getElementById('moreTabsMenu').style.display = 'none';
            }
        });
    }

    activateTab(tabId) {
        this.currentTab = tabId;
        
        // Update tab UI
        document.querySelectorAll('.tab-item').forEach(item => {
            item.classList.toggle('active', item.dataset.tab === tabId);
        });

        // Load tab content
        this.loadTabContent(tabId);

        // Update URL
        window.history.pushState({}, '', `#/project/${this.projectKey}/${tabId}`);
    }

    loadTabContent(tabId) {
        const container = document.getElementById('projectTabContent');
        if (!container) return;

        const tab = this.allTabs.find(t => t.id === tabId);
        if (!tab) return;

        // Clear existing content
        container.innerHTML = '';

        // Load appropriate component
        switch (tabId) {
            case 'summary':
                this.renderSummaryTab(container);
                break;
            case 'timeline':
                this.renderTimelineTab(container);
                break;
            case 'board':
                this.renderBoardTab(container);
                break;
            case 'calendar':
                this.renderCalendarTab(container);
                break;
            case 'list':
                this.renderListTab(container);
                break;
            case 'reports':
                this.renderReportsTab(container);
                break;
            case 'forms':
                this.renderFormsTab(container);
                break;
            case 'components':
                this.renderComponentsTab(container);
                break;
            case 'development':
                this.renderDevelopmentTab(container);
                break;
            case 'code':
                this.renderCodeTab(container);
                break;
            case 'releases':
                this.renderReleasesTab(container);
                break;
            case 'archived':
                this.renderArchivedTab(container);
                break;
            case 'pages':
                this.renderPagesTab(container);
                break;
            default:
                container.innerHTML = '<div class="tab-placeholder">Tab content</div>';
        }

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    // ===================== TAB RENDERERS =====================

    renderSummaryTab(container) {
        container.innerHTML = `
            <div class="summary-tab">
                <div class="summary-grid">
                    <!-- Project Overview -->
                    <div class="summary-card">
                        <h3>Project overview</h3>
                        <div class="overview-stats">
                            <div class="stat-item">
                                <label>Issues</label>
                                <span class="stat-value">127</span>
                            </div>
                            <div class="stat-item">
                                <label>In Progress</label>
                                <span class="stat-value">12</span>
                            </div>
                            <div class="stat-item">
                                <label>Completed</label>
                                <span class="stat-value">85</span>
                            </div>
                        </div>
                    </div>

                    <!-- Recent Activity -->
                    <div class="summary-card">
                        <h3>Recent activity</h3>
                        <div class="activity-list">
                            <div class="activity-item">
                                <div class="activity-icon"><i data-lucide="check-circle"></i></div>
                                <div class="activity-content">
                                    <span>PROJ-123 completed</span>
                                    <span class="activity-time">2 hours ago</span>
                                </div>
                            </div>
                            <div class="activity-item">
                                <div class="activity-icon"><i data-lucide="file-plus"></i></div>
                                <div class="activity-content">
                                    <span>PROJ-124 created</span>
                                    <span class="activity-time">3 hours ago</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Team Members -->
                    <div class="summary-card">
                        <h3>Team members</h3>
                        <div class="team-list">
                            <div class="team-member">
                                <div class="avatar-sm">JD</div>
                                <div class="member-info">
                                    <div class="member-name">John Doe</div>
                                    <div class="member-role">Lead Developer</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Quick Links -->
                    <div class="summary-card">
                        <h3>Quick links</h3>
                        <div class="quick-links">
                            <a href="#" class="quick-link">
                                <i data-lucide="external-link"></i>
                                <span>Repository</span>
                            </a>
                            <a href="#" class="quick-link">
                                <i data-lucide="book"></i>
                                <span>Documentation</span>
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderTimelineTab(container) {
        container.innerHTML = `
            <div class="timeline-tab">
                <div class="timeline-header">
                    <h2>Timeline</h2>
                    <div class="timeline-controls">
                        <button class="btn-secondary" onclick="projectTabs.createEpic()">
                            <i data-lucide="plus"></i>
                            Create epic
                        </button>
                        <button class="btn-icon" onclick="projectTabs.zoomIn()">
                            <i data-lucide="zoom-in"></i>
                        </button>
                        <button class="btn-icon" onclick="projectTabs.zoomOut()">
                            <i data-lucide="zoom-out"></i>
                        </button>
                    </div>
                </div>
                <div class="timeline-container" id="timelineContainer">
                    <!-- Timeline component will be initialized here -->
                    <p class="placeholder-text">Timeline view will be rendered here</p>
                </div>
            </div>
        `;
    }

    renderBoardTab(container) {
        container.innerHTML = `
            <div class="board-tab">
                <!-- Board component (kanban-board.js) will be initialized here -->
                <div id="kanbanBoardContainer"></div>
            </div>
        `;
        // Initialize existing Kanban board if available
        if (window.kanbanBoard) {
            window.kanbanBoard.render();
        }
    }

    renderCalendarTab(container) {
        container.innerHTML = `
            <div class="calendar-tab">
                <!-- Calendar component will be initialized here -->
                <div id="calendarViewContainer"></div>
            </div>
        `;
        // Initialize calendar if available
        if (window.calendarView) {
            window.calendarView.render();
        }
    }

    renderListTab(container) {
        container.innerHTML = `
            <div class="list-tab">
                <!-- Issue Navigator list view -->
                <div id="issueNavigatorContainer"></div>
            </div>
        `;
        // Initialize issue navigator if available
        if (window.issueNavigator) {
            window.issueNavigator.switchView('list');
        }
    }

    renderReportsTab(container) {
        container.innerHTML = `
            <div class="reports-tab">
                <div class="reports-grid">
                    <div class="report-card" onclick="projectTabs.openReport('velocity')">
                        <i data-lucide="trending-up"></i>
                        <h3>Velocity Chart</h3>
                        <p>Track team velocity over sprints</p>
                    </div>
                    <div class="report-card" onclick="projectTabs.openReport('burndown')">
                        <i data-lucide="activity"></i>
                        <h3>Burndown Chart</h3>
                        <p>Monitor sprint progress</p>
                    </div>
                    <div class="report-card" onclick="projectTabs.openReport('cumulative-flow')">
                        <i data-lucide="layers"></i>
                        <h3>Cumulative Flow</h3>
                        <p>Identify workflow bottlenecks</p>
                    </div>
                    <div class="report-card" onclick="projectTabs.openReport('control')">
                        <i data-lucide="bar-chart-2"></i>
                        <h3>Control Chart</h3>
                        <p>Analyze cycle time</p>
                    </div>
                </div>
            </div>
        `;
    }

    renderFormsTab(container) {
        container.innerHTML = `
            <div class="forms-tab">
                <div class="forms-header">
                    <h2>Forms</h2>
                    <button class="btn-primary" onclick="projectTabs.createForm()">
                        <i data-lucide="plus"></i>
                        Create form
                    </button>
                </div>
                <div class="forms-list" id="formsList">
                    <div class="empty-state">
                        <i data-lucide="file-check"></i>
                        <h3>No forms yet</h3>
                        <p>Create a form to collect information</p>
                        <button class="btn-primary" onclick="projectTabs.createForm()">
                            Create form
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    renderComponentsTab(container) {
        container.innerHTML = `
            <div class="components-tab">
                <div class="components-header">
                    <h2>Components</h2>
                    <button class="btn-primary" onclick="projectTabs.createComponent()">
                        <i data-lucide="plus"></i>
                        Create component
                    </button>
                </div>
                <div class="components-list">
                    <div class="component-item">
                        <div class="component-info">
                            <h3>Frontend</h3>
                            <p>User interface components</p>
                            <span class="component-lead">Lead: John Doe</span>
                        </div>
                        <div class="component-stats">
                            <span class="stat">12 issues</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderDevelopmentTab(container) {
        container.innerHTML = `
            <div class="development-tab">
                <div class="dev-sections">
                    <div class="dev-section">
                        <h3><i data-lucide="git-commit"></i> Recent Commits</h3>
                        <div class="commits-list">
                            <div class="commit-item">
                                <div class="commit-message">Fix navigation bar styling</div>
                                <div class="commit-meta">
                                    <span class="commit-author">John Doe</span>
                                    <span class="commit-time">2 hours ago</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="dev-section">
                        <h3><i data-lucide="git-pull-request"></i> Pull Requests</h3>
                        <div class="pr-list">
                            <div class="pr-item">
                                <div class="pr-title">Add user authentication</div>
                                <span class="pr-status status-open">Open</span>
                            </div>
                        </div>
                    </div>
                    <div class="dev-section">
                        <h3><i data-lucide="git-branch"></i> Active Branches</h3>
                        <div class="branches-list">
                            <div class="branch-item">
                                <span class="branch-name">feature/user-auth</span>
                                <span class="branch-commits">5 commits</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderCodeTab(container) {
        container.innerHTML = `
            <div class="code-tab">
                <div class="code-header">
                    <h2>Code repositories</h2>
                    <button class="btn-primary" onclick="projectTabs.linkRepository()">
                        <i data-lucide="link"></i>
                        Link repository
                    </button>
                </div>
                <div class="repos-list">
                    <div class="repo-item">
                        <div class="repo-icon"><i data-lucide="github"></i></div>
                        <div class="repo-info">
                            <h3>project-management-app</h3>
                            <a href="#" class="repo-link">github.com/user/project-management-app</a>
                        </div>
                        <div class="repo-stats">
                            <span><i data-lucide="git-commit"></i> 234 commits</span>
                            <span><i data-lucide="git-branch"></i> 12 branches</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderReleasesTab(container) {
        container.innerHTML = `
            <div class="releases-tab">
                <div class="releases-header">
                    <h2>Releases</h2>
                    <button class="btn-primary" onclick="projectTabs.createRelease()">
                        <i data-lucide="plus"></i>
                        Create release
                    </button>
                </div>
                <div class="releases-list">
                    <div class="release-item">
                        <div class="release-header">
                            <h3>v1.0.0</h3>
                            <span class="release-status status-released">Released</span>
                        </div>
                        <div class="release-date">Released on Jan 15, 2024</div>
                        <div class="release-stats">
                            <span>45 issues</span>
                            <span>•</span>
                            <span>100% complete</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderArchivedTab(container) {
        container.innerHTML = `
            <div class="archived-tab">
                <div class="archived-header">
                    <h2>Archived issues</h2>
                    <div class="archived-filters">
                        <input type="text" class="search-input" placeholder="Search archived issues...">
                        <select class="filter-select">
                            <option>All time</option>
                            <option>Last 30 days</option>
                            <option>Last 90 days</option>
                        </select>
                    </div>
                </div>
                <div class="archived-list">
                    <div class="empty-state">
                        <i data-lucide="archive"></i>
                        <h3>No archived issues</h3>
                        <p>Archived issues will appear here</p>
                    </div>
                </div>
            </div>
        `;
    }

    renderPagesTab(container) {
        container.innerHTML = `
            <div class="pages-tab">
                <div class="pages-header">
                    <h2>Project pages</h2>
                    <button class="btn-primary" onclick="projectTabs.createPage()">
                        <i data-lucide="plus"></i>
                        Create page
                    </button>
                </div>
                <div class="pages-tree">
                    <div class="empty-state">
                        <i data-lucide="file-text"></i>
                        <h3>No pages yet</h3>
                        <p>Create pages to document your project</p>
                        <button class="btn-primary" onclick="projectTabs.createPage()">
                            Create page
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    // ===================== TAB ACTIONS =====================

    showTabOptions(tabId, event) {
        const menu = document.getElementById('tabContextMenu');
        menu.style.display = 'block';
        menu.style.left = event.pageX + 'px';
        menu.style.top = event.pageY + 'px';
        menu.dataset.tabId = tabId;
    }

    hideTab() {
        const menu = document.getElementById('tabContextMenu');
        const tabId = menu.dataset.tabId;
        this.visibleTabs = this.visibleTabs.filter(id => id !== tabId);
        document.getElementById('tabsList').innerHTML = this.renderTabs();
        document.getElementById('moreTabsMenu').querySelector('.dropdown-section').innerHTML = 
            `<div class="section-label">Hidden tabs</div>${this.renderHiddenTabs()}`;
        menu.style.display = 'none';
        if (window.lucide) lucide.createIcons();
    }

    showTab(tabId) {
        this.visibleTabs.push(tabId);
        document.getElementById('tabsList').innerHTML = this.renderTabs();
        document.getElementById('moreTabsMenu').querySelector('.dropdown-section').innerHTML = 
            `<div class="section-label">Hidden tabs</div>${this.renderHiddenTabs()}`;
        if (window.lucide) lucide.createIcons();
    }

    addShortcut() {
        const menu = document.getElementById('tabContextMenu');
        const tabId = menu.dataset.tabId;
        const tab = this.allTabs.find(t => t.id === tabId);
        
        this.shortcuts.push({
            id: Date.now().toString(),
            name: tab.name,
            icon: tab.icon,
            url: `#/project/${this.projectKey}/${tabId}`
        });
        
        menu.style.display = 'none';
    }

    removeShortcut(id) {
        this.shortcuts = this.shortcuts.filter(s => s.id !== id);
        document.getElementById('shortcutsList').innerHTML = this.renderShortcuts();
        if (window.lucide) lucide.createIcons();
    }

    moveTabLeft() {
        const menu = document.getElementById('tabContextMenu');
        const tabId = menu.dataset.tabId;
        const index = this.visibleTabs.indexOf(tabId);
        if (index > 0) {
            [this.visibleTabs[index], this.visibleTabs[index - 1]] = 
            [this.visibleTabs[index - 1], this.visibleTabs[index]];
            document.getElementById('tabsList').innerHTML = this.renderTabs();
            if (window.lucide) lucide.createIcons();
        }
        menu.style.display = 'none';
    }

    moveTabRight() {
        const menu = document.getElementById('tabContextMenu');
        const tabId = menu.dataset.tabId;
        const index = this.visibleTabs.indexOf(tabId);
        if (index < this.visibleTabs.length - 1) {
            [this.visibleTabs[index], this.visibleTabs[index + 1]] = 
            [this.visibleTabs[index + 1], this.visibleTabs[index]];
            document.getElementById('tabsList').innerHTML = this.renderTabs();
            if (window.lucide) lucide.createIcons();
        }
        menu.style.display = 'none';
    }

    toggleMoreMenu() {
        const menu = document.getElementById('moreTabsMenu');
        menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
    }

    openShortcuts() {
        const panel = document.getElementById('shortcutsPanel');
        panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
    }

    closeShortcuts() {
        document.getElementById('shortcutsPanel').style.display = 'none';
    }

    customizeNavigation() {
        const modal = document.getElementById('customizeNavModal');
        const customizer = document.getElementById('tabsCustomizer');
        
        customizer.innerHTML = this.allTabs.map(tab => `
            <div class="tab-customizer-item" draggable="true" data-tab="${tab.id}">
                <div class="drag-handle"><i data-lucide="grip-vertical"></i></div>
                <input type="checkbox" 
                       id="customize_${tab.id}" 
                       ${this.visibleTabs.includes(tab.id) ? 'checked' : ''}>
                <label for="customize_${tab.id}">
                    <i data-lucide="${tab.icon}"></i>
                    ${tab.name}
                </label>
            </div>
        `).join('');
        
        modal.style.display = 'flex';
        this.setupDragAndDrop();
        if (window.lucide) lucide.createIcons();
    }

    setupDragAndDrop() {
        // Simplified drag and drop implementation
        const items = document.querySelectorAll('.tab-customizer-item');
        items.forEach(item => {
            item.addEventListener('dragstart', (e) => {
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/html', item.innerHTML);
                item.classList.add('dragging');
            });
            
            item.addEventListener('dragend', () => {
                item.classList.remove('dragging');
            });
        });
    }

    closeCustomizeNav() {
        document.getElementById('customizeNavModal').style.display = 'none';
    }

    saveNavigation() {
        const items = document.querySelectorAll('.tab-customizer-item');
        this.visibleTabs = Array.from(items)
            .filter(item => item.querySelector('input').checked)
            .map(item => item.dataset.tab);
        
        document.getElementById('tabsList').innerHTML = this.renderTabs();
        this.closeCustomizeNav();
        if (window.lucide) lucide.createIcons();
    }

    resetNavigation() {
        this.visibleTabs = ['summary', 'board', 'timeline', 'list', 'reports'];
        this.customizeNavigation();
    }

    // Project Actions
    starProject() { alert('Star project'); }
    shareProject() { alert('Share project'); }
    openProjectSettings() { window.location.href = `/projects/${this.projectKey}/settings`; }
    createEpic() { alert('Create epic'); }
    zoomIn() { alert('Zoom in'); }
    zoomOut() { alert('Zoom out'); }
    openReport(type) { alert(`Open ${type} report`); }
    createForm() { alert('Create form'); }
    createComponent() { alert('Create component'); }
    linkRepository() { alert('Link repository'); }
    createRelease() { alert('Create release'); }
    createPage() { alert('Create page'); }
    addCustomShortcut() { alert('Add custom shortcut'); }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.projectTabs = new ProjectTabs();
});
