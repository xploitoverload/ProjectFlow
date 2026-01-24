/**
 * Quick Actions Menu
 * Global keyboard shortcuts and quick action palette
 */

class QuickActionsMenu {
    constructor() {
        this.isOpen = false;
        this.actions = [];
        this.filteredActions = [];
        this.selectedIndex = 0;
        
        this.init();
    }

    init() {
        this.defineActions();
        this.createMenu();
        this.setupEventListeners();
        this.registerKeyboardShortcuts();
    }

    defineActions() {
        this.actions = [
            // Navigation
            { id: 'nav_board', name: 'Go to Board', icon: 'layout', shortcut: 'g b', category: 'Navigation', action: () => window.location.href = '/board' },
            { id: 'nav_backlog', name: 'Go to Backlog', icon: 'list', shortcut: 'g l', category: 'Navigation', action: () => window.location.href = '/backlog' },
            { id: 'nav_timeline', name: 'Go to Timeline', icon: 'gantt-chart', shortcut: 'g t', category: 'Navigation', action: () => window.location.href = '/timeline' },
            { id: 'nav_reports', name: 'Go to Reports', icon: 'bar-chart', shortcut: 'g r', category: 'Navigation', action: () => openReportsDashboard() },
            { id: 'nav_calendar', name: 'Go to Calendar', icon: 'calendar', shortcut: 'g c', category: 'Navigation', action: () => window.location.href = '/calendar' },
            
            // Create
            { id: 'create_issue', name: 'Create Issue', icon: 'plus', shortcut: 'c', category: 'Create', action: () => this.openCreateIssue() },
            { id: 'create_epic', name: 'Create Epic', icon: 'package', shortcut: 'e', category: 'Create', action: () => this.openCreateEpic() },
            { id: 'create_sprint', name: 'Create Sprint', icon: 'play-circle', shortcut: 's', category: 'Create', action: () => sprintManager?.openSprintDialog() },
            
            // Views
            { id: 'view_filters', name: 'Open Filters', icon: 'filter', shortcut: 'f', category: 'View', action: () => advancedFilters?.openModal() },
            { id: 'view_search', name: 'Search', icon: 'search', shortcut: '/', category: 'View', action: () => this.openSearch() },
            { id: 'view_notifications', name: 'View Notifications', icon: 'bell', shortcut: 'n', category: 'View', action: () => notificationsSystem?.togglePanel() },
            { id: 'view_activity', name: 'Activity Stream', icon: 'activity', shortcut: 'a', category: 'View', action: () => openActivityStream() },
            
            // Management
            { id: 'manage_teams', name: 'Manage Teams', icon: 'users', category: 'Management', action: () => openTeamManagement() },
            { id: 'manage_versions', name: 'Manage Versions', icon: 'package', category: 'Management', action: () => openVersionManagement() },
            { id: 'manage_workflows', name: 'Edit Workflows', icon: 'git-branch', category: 'Management', action: () => workflowEditor?.openModal() },
            { id: 'manage_fields', name: 'Custom Fields', icon: 'edit-3', category: 'Management', action: () => customFieldsManager?.openModal() },
            { id: 'manage_permissions', name: 'Permissions', icon: 'shield', category: 'Management', action: () => permissionsSystem?.openModal() },
            { id: 'manage_automation', name: 'Automation Rules', icon: 'zap', category: 'Management', action: () => openAutomationRules() },
            
            // Tools
            { id: 'tool_import', name: 'Import Issues', icon: 'upload', category: 'Tools', action: () => importExportSystem?.openModal() },
            { id: 'tool_export', name: 'Export Issues', icon: 'download', category: 'Tools', action: () => this.openExport() },
            { id: 'tool_metrics', name: 'Agile Metrics', icon: 'trending-up', category: 'Tools', action: () => openAgileMetrics() },
            
            // Settings
            { id: 'settings_profile', name: 'Edit Profile', icon: 'user', shortcut: ',', category: 'Settings', action: () => this.openProfile() },
            { id: 'settings_theme', name: 'Toggle Dark Mode', icon: 'moon', shortcut: 'd', category: 'Settings', action: () => this.toggleTheme() },
            { id: 'settings_shortcuts', name: 'Keyboard Shortcuts', icon: 'command', shortcut: '?', category: 'Settings', action: () => this.showShortcuts() }
        ];
    }

    createMenu() {
        const menuHTML = `
            <div id="quickActionsMenu" class="quick-actions-menu" style="display: none;">
                <div class="quick-actions-backdrop"></div>
                <div class="quick-actions-container">
                    <div class="quick-actions-header">
                        <div class="search-icon">
                            <i data-lucide="search"></i>
                        </div>
                        <input type="text" 
                               class="quick-search-input" 
                               id="quickSearchInput" 
                               placeholder="Type a command or search..."
                               autocomplete="off">
                        <div class="quick-shortcut">⌘K</div>
                    </div>
                    
                    <div class="quick-actions-content" id="quickActionsContent">
                        <!-- Populated by JS -->
                    </div>
                </div>
            </div>

            <!-- Keyboard Shortcuts Help -->
            <div id="shortcutsHelp" class="shortcuts-help" style="display: none;">
                <div class="shortcuts-backdrop"></div>
                <div class="shortcuts-container">
                    <div class="shortcuts-header">
                        <h3>Keyboard Shortcuts</h3>
                        <button class="btn-icon-sm" onclick="quickActions.closeShortcuts()">
                            <i data-lucide="x"></i>
                        </button>
                    </div>
                    <div class="shortcuts-content">
                        <div class="shortcuts-section">
                            <h4>Navigation</h4>
                            <div class="shortcut-list">
                                <div class="shortcut-item">
                                    <span class="shortcut-name">Go to Board</span>
                                    <span class="shortcut-keys"><kbd>g</kbd> <kbd>b</kbd></span>
                                </div>
                                <div class="shortcut-item">
                                    <span class="shortcut-name">Go to Backlog</span>
                                    <span class="shortcut-keys"><kbd>g</kbd> <kbd>l</kbd></span>
                                </div>
                                <div class="shortcut-item">
                                    <span class="shortcut-name">Go to Timeline</span>
                                    <span class="shortcut-keys"><kbd>g</kbd> <kbd>t</kbd></span>
                                </div>
                                <div class="shortcut-item">
                                    <span class="shortcut-name">Go to Reports</span>
                                    <span class="shortcut-keys"><kbd>g</kbd> <kbd>r</kbd></span>
                                </div>
                            </div>
                        </div>

                        <div class="shortcuts-section">
                            <h4>Actions</h4>
                            <div class="shortcut-list">
                                <div class="shortcut-item">
                                    <span class="shortcut-name">Create Issue</span>
                                    <span class="shortcut-keys"><kbd>c</kbd></span>
                                </div>
                                <div class="shortcut-item">
                                    <span class="shortcut-name">Create Epic</span>
                                    <span class="shortcut-keys"><kbd>e</kbd></span>
                                </div>
                                <div class="shortcut-item">
                                    <span class="shortcut-name">Create Sprint</span>
                                    <span class="shortcut-keys"><kbd>s</kbd></span>
                                </div>
                                <div class="shortcut-item">
                                    <span class="shortcut-name">Search</span>
                                    <span class="shortcut-keys"><kbd>/</kbd></span>
                                </div>
                            </div>
                        </div>

                        <div class="shortcuts-section">
                            <h4>General</h4>
                            <div class="shortcut-list">
                                <div class="shortcut-item">
                                    <span class="shortcut-name">Command Palette</span>
                                    <span class="shortcut-keys"><kbd>⌘</kbd> <kbd>K</kbd></span>
                                </div>
                                <div class="shortcut-item">
                                    <span class="shortcut-name">Toggle Dark Mode</span>
                                    <span class="shortcut-keys"><kbd>d</kbd></span>
                                </div>
                                <div class="shortcut-item">
                                    <span class="shortcut-name">Keyboard Shortcuts</span>
                                    <span class="shortcut-keys"><kbd>?</kbd></span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', menuHTML);

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    setupEventListeners() {
        const backdrop = document.querySelector('.quick-actions-backdrop');
        backdrop?.addEventListener('click', () => this.closeMenu());

        const input = document.getElementById('quickSearchInput');
        input?.addEventListener('input', (e) => this.handleSearch(e.target.value));
        input?.addEventListener('keydown', (e) => this.handleKeydown(e));
    }

    registerKeyboardShortcuts() {
        let sequenceKeys = '';
        let sequenceTimeout = null;

        document.addEventListener('keydown', (e) => {
            // Ignore if typing in input/textarea
            if (e.target.matches('input, textarea')) {
                // Except for command palette and search
                if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
                    e.preventDefault();
                    this.openMenu();
                    return;
                }
                if (e.key === '/' && !e.metaKey && !e.ctrlKey) {
                    e.preventDefault();
                    this.openMenu();
                    return;
                }
                return;
            }

            // Command palette
            if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
                e.preventDefault();
                this.openMenu();
                return;
            }

            // Escape to close
            if (e.key === 'Escape' && this.isOpen) {
                e.preventDefault();
                this.closeMenu();
                return;
            }

            // Single key shortcuts
            const singleKeyActions = this.actions.filter(a => a.shortcut && a.shortcut.length === 1);
            const action = singleKeyActions.find(a => a.shortcut === e.key);
            if (action) {
                e.preventDefault();
                action.action();
                return;
            }

            // Sequence shortcuts (e.g., "g b")
            sequenceKeys += e.key;
            
            const sequenceAction = this.actions.find(a => 
                a.shortcut && a.shortcut.includes(' ') && a.shortcut.replace(/\s/g, '') === sequenceKeys
            );
            
            if (sequenceAction) {
                e.preventDefault();
                sequenceAction.action();
                sequenceKeys = '';
                clearTimeout(sequenceTimeout);
                return;
            }

            // Reset sequence after 1 second
            clearTimeout(sequenceTimeout);
            sequenceTimeout = setTimeout(() => {
                sequenceKeys = '';
            }, 1000);
        });
    }

    openMenu() {
        document.getElementById('quickActionsMenu').style.display = 'flex';
        this.isOpen = true;
        this.filteredActions = [...this.actions];
        this.selectedIndex = 0;
        this.renderActions();
        
        // Focus input
        setTimeout(() => {
            document.getElementById('quickSearchInput')?.focus();
        }, 100);
    }

    closeMenu() {
        document.getElementById('quickActionsMenu').style.display = 'none';
        this.isOpen = false;
        document.getElementById('quickSearchInput').value = '';
    }

    handleSearch(query) {
        if (!query.trim()) {
            this.filteredActions = [...this.actions];
        } else {
            const lowerQuery = query.toLowerCase();
            this.filteredActions = this.actions.filter(action => 
                action.name.toLowerCase().includes(lowerQuery) ||
                action.category.toLowerCase().includes(lowerQuery) ||
                (action.shortcut && action.shortcut.toLowerCase().includes(lowerQuery))
            );
        }
        
        this.selectedIndex = 0;
        this.renderActions();
    }

    handleKeydown(e) {
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            this.selectedIndex = Math.min(this.selectedIndex + 1, this.filteredActions.length - 1);
            this.renderActions();
            this.scrollToSelected();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            this.selectedIndex = Math.max(this.selectedIndex - 1, 0);
            this.renderActions();
            this.scrollToSelected();
        } else if (e.key === 'Enter') {
            e.preventDefault();
            const action = this.filteredActions[this.selectedIndex];
            if (action) {
                this.executeAction(action);
            }
        }
    }

    renderActions() {
        const container = document.getElementById('quickActionsContent');
        
        if (this.filteredActions.length === 0) {
            container.innerHTML = `
                <div class="no-results">
                    <i data-lucide="search-x"></i>
                    <p>No actions found</p>
                </div>
            `;
            if (window.lucide) lucide.createIcons();
            return;
        }

        // Group by category
        const grouped = {};
        this.filteredActions.forEach(action => {
            if (!grouped[action.category]) {
                grouped[action.category] = [];
            }
            grouped[action.category].push(action);
        });

        container.innerHTML = Object.entries(grouped).map(([category, actions]) => `
            <div class="action-category">
                <div class="category-label">${category}</div>
                ${actions.map((action, index) => {
                    const globalIndex = this.filteredActions.indexOf(action);
                    return `
                        <div class="action-item ${globalIndex === this.selectedIndex ? 'selected' : ''}" 
                             data-index="${globalIndex}"
                             onclick="quickActions.executeAction(quickActions.filteredActions[${globalIndex}])">
                            <div class="action-icon">
                                <i data-lucide="${action.icon}"></i>
                            </div>
                            <div class="action-content">
                                <div class="action-name">${action.name}</div>
                            </div>
                            ${action.shortcut ? `
                                <div class="action-shortcut">
                                    ${action.shortcut.split(' ').map(k => `<kbd>${k}</kbd>`).join(' ')}
                                </div>
                            ` : ''}
                        </div>
                    `;
                }).join('')}
            </div>
        `).join('');

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    scrollToSelected() {
        const selected = document.querySelector('.action-item.selected');
        if (selected) {
            selected.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        }
    }

    executeAction(action) {
        this.closeMenu();
        action.action();
    }

    // Action implementations
    openCreateIssue() {
        // Open create issue modal (implementation depends on existing modal)
        alert('Create Issue - Integration point');
    }

    openCreateEpic() {
        alert('Create Epic - Integration point');
    }

    openSearch() {
        advancedFilters?.openModal();
    }

    openExport() {
        importExportSystem?.openModal();
        setTimeout(() => {
            document.querySelector('[data-tab="export"]')?.click();
        }, 100);
    }

    openProfile() {
        window.location.href = '/profile';
    }

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    }

    showShortcuts() {
        document.getElementById('shortcutsHelp').style.display = 'flex';
        if (window.lucide) lucide.createIcons();
    }

    closeShortcuts() {
        document.getElementById('shortcutsHelp').style.display = 'none';
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.quickActions = new QuickActionsMenu();
});
