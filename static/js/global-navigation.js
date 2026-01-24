/**
 * Global Navigation Manager - Atlassian NAV4 System
 * Handles top navigation, product switcher, command palette, and global actions
 */

class GlobalNavigation {
    constructor() {
        this.searchOpen = false;
        this.productSwitcherOpen = false;
        this.helpMenuOpen = false;
        this.userMenuOpen = false;
        this.createMenuOpen = false;
        this.init();
    }

    init() {
        this.setupCommandPalette();
        this.setupProductSwitcher();
        this.setupCreateMenu();
        this.setupHelpMenu();
        this.setupRecentItems();
        this.setupKeyboardShortcuts();
        console.log('GlobalNavigation initialized');
    }

    // ============================================
    // COMMAND PALETTE (CMD/CTRL+K)
    // ============================================
    setupCommandPalette() {
        const palette = document.getElementById('commandPalette');
        if (!palette) return;

        const input = palette.querySelector('.command-input');
        const results = palette.querySelector('.command-results');

        // Search data
        this.commands = this.getCommands();

        input?.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            this.filterCommands(query, results);
        });

        // Handle arrow keys and enter
        input?.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                e.preventDefault();
                this.navigateResults(e.key);
            } else if (e.key === 'Enter') {
                e.preventDefault();
                this.executeSelected();
            } else if (e.key === 'Escape') {
                this.closeCommandPalette();
            }
        });
    }

    getCommands() {
        return [
            // Navigation
            { icon: 'home', title: 'Go to Dashboard', action: () => window.location.href = '/dashboard', category: 'Navigation' },
            { icon: 'layout-kanban', title: 'Go to Board', action: () => window.location.href = '/project/1/kanban', category: 'Navigation' },
            { icon: 'list', title: 'Go to Backlog', action: () => window.location.href = '/project/1/backlog', category: 'Navigation' },
            { icon: 'calendar', title: 'Go to Calendar', action: () => window.location.href = '/calendar', category: 'Navigation' },
            { icon: 'gantt-chart', title: 'Go to Timeline', action: () => window.location.href = '/gantt', category: 'Navigation' },
            { icon: 'bar-chart-3', title: 'Go to Reports', action: () => window.location.href = '/project/1/reports', category: 'Navigation' },
            
            // Create actions
            { icon: 'plus-circle', title: 'Create Issue', action: () => this.openCreateIssue(), category: 'Create' },
            { icon: 'hexagon', title: 'Create Epic', action: () => this.openCreateEpic(), category: 'Create' },
            { icon: 'zap', title: 'Create Sprint', action: () => this.openCreateSprint(), category: 'Create' },
            { icon: 'folder-plus', title: 'Create Project', action: () => this.openCreateProject(), category: 'Create' },
            
            // View actions
            { icon: 'moon', title: 'Toggle Dark Mode', action: () => window.themeManager?.toggleTheme(), category: 'View' },
            { icon: 'sidebar', title: 'Toggle Sidebar', action: () => this.toggleSidebar(), category: 'View' },
            { icon: 'maximize-2', title: 'Toggle Fullscreen', action: () => this.toggleFullscreen(), category: 'View' },
            
            // Settings
            { icon: 'settings', title: 'Settings', action: () => window.location.href = '/settings', category: 'Settings' },
            { icon: 'user', title: 'Profile', action: () => window.location.href = '/profile', category: 'Settings' },
            { icon: 'shield', title: 'Security', action: () => window.location.href = '/admin/security', category: 'Settings' },
            
            // Help
            { icon: 'help-circle', title: 'Help Center', action: () => window.open('https://support.atlassian.com/jira/', '_blank'), category: 'Help' },
            { icon: 'keyboard', title: 'Keyboard Shortcuts', action: () => this.showShortcuts(), category: 'Help' },
            { icon: 'book-open', title: 'Documentation', action: () => window.open('https://confluence.atlassian.com/jira', '_blank'), category: 'Help' },
        ];
    }

    filterCommands(query, resultsContainer) {
        if (!query) {
            resultsContainer.innerHTML = this.renderAllCommands();
        } else {
            const filtered = this.commands.filter(cmd => 
                cmd.title.toLowerCase().includes(query) || 
                cmd.category.toLowerCase().includes(query)
            );
            resultsContainer.innerHTML = this.renderFilteredCommands(filtered);
        }
        lucide.createIcons();
    }

    renderAllCommands() {
        const categories = {};
        this.commands.forEach(cmd => {
            if (!categories[cmd.category]) categories[cmd.category] = [];
            categories[cmd.category].push(cmd);
        });

        let html = '';
        for (const [category, items] of Object.entries(categories)) {
            html += `
                <div class="command-category">
                    <div class="command-category-title">${category}</div>
                    ${items.map((cmd, idx) => this.renderCommandItem(cmd, idx === 0)).join('')}
                </div>
            `;
        }
        return html;
    }

    renderFilteredCommands(commands) {
        if (commands.length === 0) {
            return '<div class="command-empty">No commands found</div>';
        }
        return commands.map((cmd, idx) => this.renderCommandItem(cmd, idx === 0)).join('');
    }

    renderCommandItem(cmd, isFirst) {
        return `
            <div class="command-item ${isFirst ? 'selected' : ''}" data-action="${cmd.title}">
                <i data-lucide="${cmd.icon}" class="command-item-icon"></i>
                <span class="command-item-title">${cmd.title}</span>
                <span class="command-item-category">${cmd.category}</span>
            </div>
        `;
    }

    openCommandPalette() {
        const palette = document.getElementById('commandPalette');
        const overlay = document.getElementById('commandOverlay');
        const input = palette.querySelector('.command-input');
        
        palette.classList.add('open');
        overlay.classList.add('open');
        input.value = '';
        input.focus();
        
        const results = palette.querySelector('.command-results');
        results.innerHTML = this.renderAllCommands();
        lucide.createIcons();
        
        this.searchOpen = true;
    }

    closeCommandPalette() {
        const palette = document.getElementById('commandPalette');
        const overlay = document.getElementById('commandOverlay');
        
        palette.classList.remove('open');
        overlay.classList.remove('open');
        this.searchOpen = false;
    }

    navigateResults(direction) {
        const items = document.querySelectorAll('.command-item');
        const selected = document.querySelector('.command-item.selected');
        
        if (!selected && items.length > 0) {
            items[0].classList.add('selected');
            return;
        }
        
        let index = Array.from(items).indexOf(selected);
        selected.classList.remove('selected');
        
        if (direction === 'ArrowDown') {
            index = (index + 1) % items.length;
        } else {
            index = (index - 1 + items.length) % items.length;
        }
        
        items[index].classList.add('selected');
        items[index].scrollIntoView({ block: 'nearest' });
    }

    executeSelected() {
        const selected = document.querySelector('.command-item.selected');
        if (!selected) return;
        
        const title = selected.dataset.action;
        const command = this.commands.find(cmd => cmd.title === title);
        
        if (command) {
            this.closeCommandPalette();
            command.action();
        }
    }

    // ============================================
    // PRODUCT SWITCHER (9-DOT MENU)
    // ============================================
    setupProductSwitcher() {
        const switcher = document.getElementById('productSwitcher');
        const button = document.getElementById('productSwitcherBtn');
        
        button?.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleProductSwitcher();
        });
    }

    toggleProductSwitcher() {
        const switcher = document.getElementById('productSwitcher');
        this.productSwitcherOpen = !this.productSwitcherOpen;
        switcher.classList.toggle('open', this.productSwitcherOpen);
        
        if (this.productSwitcherOpen) {
            this.closeOtherMenus('product');
        }
    }

    // ============================================
    // CREATE MENU DROPDOWN
    // ============================================
    setupCreateMenu() {
        const createBtn = document.querySelector('.create-btn-wrapper');
        if (!createBtn) return;

        const mainBtn = createBtn.querySelector('.btn-create-main');
        const dropdownBtn = createBtn.querySelector('.btn-create-dropdown');
        const dropdown = document.getElementById('createDropdown');
        
        // Main button click - default to create issue
        mainBtn?.addEventListener('click', (e) => {
            e.preventDefault();
            this.openCreateIssue();
        });

        // Dropdown toggle button
        dropdownBtn?.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.toggleCreateMenu();
        });

        // Handle dropdown item clicks
        dropdown?.querySelectorAll('.create-dropdown-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const action = item.dataset.action;
                this.handleCreateAction(action);
                this.closeCreateMenu();
            });
        });

        // Close on outside click
        document.addEventListener('click', (e) => {
            if (this.createMenuOpen && !createBtn?.contains(e.target)) {
                this.closeCreateMenu();
            }
        });
    }

    toggleCreateMenu() {
        const dropdown = document.getElementById('createDropdown');
        if (!dropdown) return;

        this.createMenuOpen = !this.createMenuOpen;
        dropdown.classList.toggle('active', this.createMenuOpen);

        // Close other menus
        if (this.createMenuOpen) {
            this.closeOtherMenus('create');
        }
    }

    closeCreateMenu() {
        const dropdown = document.getElementById('createDropdown');
        if (dropdown) {
            this.createMenuOpen = false;
            dropdown.classList.remove('active');
        }
    }

    handleCreateAction(action) {
        const actionMap = {
            'issue': () => this.openCreateIssue(),
            'task': () => this.openCreateIssue('Task'),
            'story': () => this.openCreateIssue('Story'),
            'bug': () => this.openCreateIssue('Bug'),
            'epic': () => this.openCreateEpic(),
            'sprint': () => this.openCreateSprint(),
            'project': () => this.openCreateProject()
        };

        const handler = actionMap[action];
        if (handler) handler();
    }

    // ============================================
    // HELP MENU
    // ============================================
    setupHelpMenu() {
        const button = document.getElementById('helpMenuBtn');
        const menu = document.getElementById('helpMenu');
        
        button?.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleHelpMenu();
        });
    }

    toggleHelpMenu() {
        const menu = document.getElementById('helpMenu');
        this.helpMenuOpen = !this.helpMenuOpen;
        menu.classList.toggle('open', this.helpMenuOpen);
        
        if (this.helpMenuOpen) {
            this.closeOtherMenus('help');
        }
    }

    // ============================================
    // KEYBOARD SHORTCUTS
    // ============================================
    setupKeyboardShortcuts() {
        let gPressed = false;
        
        document.addEventListener('keydown', (e) => {
            // CMD/CTRL + K - Open command palette
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                this.openCommandPalette();
            }
            
            // CMD/CTRL + / - Show keyboard shortcuts
            if ((e.metaKey || e.ctrlKey) && e.key === '/') {
                e.preventDefault();
                this.showShortcuts();
            }
            
            // ESC - Close any open menu
            if (e.key === 'Escape') {
                this.closeAllMenus();
                this.closeProjectSwitcher();
            }
            
            // C - Create issue (when not in input)
            if (e.key === 'c' && !this.isInputFocused()) {
                e.preventDefault();
                this.openCreateIssue();
            }
            
            // G key shortcuts
            if (e.key === 'g' && !this.isInputFocused()) {
                if (!gPressed) {
                    gPressed = true;
                    setTimeout(() => { gPressed = false; }, 1000);
                } else {
                    // G is pressed twice - ignore for now
                }
            }
            
            // G+D - Go to dashboard
            if (e.key === 'd' && gPressed && !this.isInputFocused()) {
                window.location.href = '/dashboard';
                gPressed = false;
            }
            
            // G+P - Open project switcher
            if (e.key === 'p' && gPressed && !this.isInputFocused()) {
                e.preventDefault();
                this.openProjectSwitcher();
                gPressed = false;
            }
            
            // G+B - Go to board
            if (e.key === 'b' && gPressed && !this.isInputFocused()) {
                window.location.href = '/project/1/kanban';
                gPressed = false;
            }
        });
    }

    isInputFocused() {
        const active = document.activeElement;
        return active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA' || active.isContentEditable);
    }

    showShortcuts() {
        const shortcuts = [
            { keys: 'Ctrl/Cmd + K', action: 'Open command palette' },
            { keys: 'Ctrl/Cmd + /', action: 'Show keyboard shortcuts' },
            { keys: 'Ctrl/Cmd + D', action: 'Toggle dark mode' },
            { keys: 'C', action: 'Create issue' },
            { keys: 'G then D', action: 'Go to dashboard' },
            { keys: 'G then P', action: 'Open project switcher' },
            { keys: 'G then B', action: 'Go to board' },
            { keys: 'G then A', action: 'Go to backlog' },
            { keys: 'Esc', action: 'Close dialogs' },
            { keys: '/', action: 'Focus search' },
            { keys: '?', action: 'Show help' },
        ];
        
        // Create and show shortcuts modal
        window.notificationManager?.addNotification({
            title: 'Keyboard Shortcuts',
            message: shortcuts.map(s => `${s.keys}: ${s.action}`).join('\\n'),
            type: 'info'
        });
    }

    // ============================================
    // UTILITY METHODS
    // ============================================
    closeOtherMenus(except) {
        if (except !== 'product' && this.productSwitcherOpen) {
            document.getElementById('productSwitcher')?.classList.remove('open');
            this.productSwitcherOpen = false;
        }
        if (except !== 'create' && this.createMenuOpen) {
            document.getElementById('createDropdown')?.classList.remove('active');
            this.createMenuOpen = false;
        }
        if (except !== 'help' && this.helpMenuOpen) {
            document.getElementById('helpMenu')?.classList.remove('open');
            this.helpMenuOpen = false;
        }
        if (except !== 'user' && this.userMenuOpen) {
            document.getElementById('userMenu')?.classList.remove('open');
            this.userMenuOpen = false;
        }
    }

    closeAllMenus() {
        this.closeCommandPalette();
        this.closeOtherMenus();
    }

    // ============================================
    // RECENT ITEMS
    // ============================================
    setupRecentItems() {
        const recentBtn = document.querySelector('.sidebar-nav-item[href*="Recent"]');
        if (!recentBtn) return;

        // Make it clickable without navigation
        recentBtn.href = 'javascript:void(0)';
        recentBtn.addEventListener('click', (e) => {
            e.preventDefault();
            this.toggleRecentItems();
        });
    }

    async toggleRecentItems() {
        const existingDropdown = document.getElementById('recentItemsDropdown');
        
        if (existingDropdown) {
            existingDropdown.remove();
            return;
        }

        // Close other menus
        this.closeOtherMenus('recent');

        // Fetch recent items
        try {
            const response = await fetch('/api/v1/recent-items');
            const data = await response.json();

            if (data.success) {
                this.showRecentItemsDropdown(data.data);
            }
        } catch (error) {
            console.error('Failed to fetch recent items:', error);
        }
    }

    showRecentItemsDropdown(items) {
        const recentBtn = document.querySelector('.sidebar-nav-item[href="javascript:void(0)"]');
        if (!recentBtn) return;

        const dropdown = document.createElement('div');
        dropdown.id = 'recentItemsDropdown';
        dropdown.className = 'recent-dropdown';
        dropdown.innerHTML = `
            <div class="recent-dropdown-header">
                <h3>Recently Viewed</h3>
                <button class="recent-dropdown-close" onclick="this.closest('.recent-dropdown').remove()">
                    <i data-lucide="x"></i>
                </button>
            </div>
            <div class="recent-dropdown-content">
                ${items.length === 0 ? `
                    <div class="recent-dropdown-empty">
                        <i data-lucide="clock"></i>
                        <p>No recent items</p>
                    </div>
                ` : items.map(item => `
                    <a href="${this.getItemUrl(item)}" class="recent-dropdown-item">
                        <div class="recent-item-icon" data-type="${item.type}">
                            <i data-lucide="${this.getItemIcon(item.type)}"></i>
                        </div>
                        <div class="recent-item-content">
                            <div class="recent-item-title">${item.key ? item.key + ': ' : ''}${item.title}</div>
                            <div class="recent-item-meta">${item.type} • ${this.formatTime(item.viewed_at)}</div>
                        </div>
                    </a>
                `).join('')}
            </div>
        `;

        recentBtn.parentElement.appendChild(dropdown);
        
        // Re-initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }

        // Close on outside click
        setTimeout(() => {
            document.addEventListener('click', (e) => {
                if (!dropdown.contains(e.target) && !recentBtn.contains(e.target)) {
                    dropdown.remove();
                }
            }, { once: true });
        }, 100);
    }

    getItemUrl(item) {
        const urlMap = {
            'issue': `/issues/${item.item_id}`,
            'project': `/project/${item.item_id}`,
            'sprint': `/sprints/${item.item_id}`,
            'epic': `/epics/${item.item_id}`,
            'board': `/board/${item.item_id}`
        };
        return urlMap[item.type] || '#';
    }

    getItemIcon(type) {
        const iconMap = {
            'issue': 'circle-dot',
            'project': 'folder',
            'sprint': 'zap',
            'epic': 'flag',
            'board': 'kanban'
        };
        return iconMap[type] || 'file';
    }

    formatTime(isoString) {
        const date = new Date(isoString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        return date.toLocaleDateString();
    }

    // ============================================
    // PROJECT SWITCHER (G+P)
    // ============================================
    async openProjectSwitcher() {
        // Close other menus
        this.closeAllMenus();
        
        // Create modal overlay
        const overlay = document.createElement('div');
        overlay.id = 'projectSwitcherOverlay';
        overlay.className = 'command-overlay';
        
        const modal = document.createElement('div');
        modal.id = 'projectSwitcher';
        modal.className = 'project-switcher-modal';
        modal.innerHTML = `
            <div class="project-switcher-header">
                <i data-lucide="search"></i>
                <input type="text" class="project-switcher-input" placeholder="Search projects..." autofocus>
                <button class="project-switcher-close">
                    <i data-lucide="x"></i>
                </button>
            </div>
            <div class="project-switcher-content">
                <div class="project-switcher-loading">
                    <i data-lucide="loader" class="spin"></i>
                    <span>Loading projects...</span>
                </div>
            </div>
        `;
        
        document.body.appendChild(overlay);
        document.body.appendChild(modal);
        
        // Initialize icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
        
        // Focus input
        const input = modal.querySelector('.project-switcher-input');
        input.focus();
        
        // Setup event listeners
        modal.querySelector('.project-switcher-close').addEventListener('click', () => {
            this.closeProjectSwitcher();
        });
        
        overlay.addEventListener('click', () => {
            this.closeProjectSwitcher();
        });
        
        input.addEventListener('input', (e) => {
            this.filterProjects(e.target.value);
        });
        
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeProjectSwitcher();
            } else if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                e.preventDefault();
                this.navigateProjects(e.key);
            } else if (e.key === 'Enter') {
                e.preventDefault();
                this.selectProject();
            }
        });
        
        // Fetch projects
        await this.loadProjects();
    }

    async loadProjects() {
        try {
            const response = await fetch('/api/v1/projects');
            const data = await response.json();
            
            if (data.success) {
                this.projects = data.data;
                this.displayProjects(this.projects);
            }
        } catch (error) {
            console.error('Failed to load projects:', error);
            const content = document.querySelector('.project-switcher-content');
            if (content) {
                content.innerHTML = `
                    <div class="project-switcher-error">
                        <i data-lucide="alert-circle"></i>
                        <span>Failed to load projects</span>
                    </div>
                `;
                lucide.createIcons();
            }
        }
    }

    displayProjects(projects) {
        const content = document.querySelector('.project-switcher-content');
        if (!content) return;
        
        if (projects.length === 0) {
            content.innerHTML = `
                <div class="project-switcher-empty">
                    <i data-lucide="folder-x"></i>
                    <span>No projects found</span>
                </div>
            `;
        } else {
            content.innerHTML = `
                <div class="project-switcher-section">
                    <div class="project-switcher-section-title">All Projects</div>
                    ${projects.map((project, idx) => `
                        <div class="project-switcher-item ${idx === 0 ? 'selected' : ''}" data-id="${project.id}">
                            <div class="project-icon" style="background: ${project.color || '#0052CC'}">
                                <i data-lucide="folder"></i>
                            </div>
                            <div class="project-info">
                                <div class="project-name">${project.name}</div>
                                <div class="project-key">${project.key || 'PROJ'}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
            
            // Add click handlers
            document.querySelectorAll('.project-switcher-item').forEach(item => {
                item.addEventListener('click', () => {
                    window.location.href = `/project/${item.dataset.id}`;
                });
            });
        }
        
        lucide.createIcons();
    }

    filterProjects(query) {
        if (!this.projects) return;
        
        const filtered = this.projects.filter(p => 
            p.name.toLowerCase().includes(query.toLowerCase()) ||
            (p.key && p.key.toLowerCase().includes(query.toLowerCase()))
        );
        
        this.displayProjects(filtered);
    }

    navigateProjects(direction) {
        const items = document.querySelectorAll('.project-switcher-item');
        const selected = document.querySelector('.project-switcher-item.selected');
        
        if (!selected && items.length > 0) {
            items[0].classList.add('selected');
            return;
        }
        
        let index = Array.from(items).indexOf(selected);
        selected.classList.remove('selected');
        
        if (direction === 'ArrowDown') {
            index = (index + 1) % items.length;
        } else {
            index = (index - 1 + items.length) % items.length;
        }
        
        items[index].classList.add('selected');
        items[index].scrollIntoView({ block: 'nearest' });
    }

    selectProject() {
        const selected = document.querySelector('.project-switcher-item.selected');
        if (selected) {
            window.location.href = `/project/${selected.dataset.id}`;
        }
    }

    closeProjectSwitcher() {
        document.getElementById('projectSwitcherOverlay')?.remove();
        document.getElementById('projectSwitcher')?.remove();
    }

    toggleSidebar() {
        document.getElementById('sidebar')?.classList.toggle('collapsed');
    }

    toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    }

    openCreateIssue(type = 'Issue') {
        // Check if we're on a project page (kanban board)
        const modal = document.getElementById('addIssueModal');
        if (modal) {
            // We're on a project page with the modal
            if (window.openAddIssueModal) {
                window.openAddIssueModal();
            } else {
                modal.classList.add('active');
            }
        } else {
            // We're on dashboard or another page without project context
            // Navigate to first available project or show message
            const firstProjectLink = document.querySelector('.sidebar-nav-item[href*="/projects/"][href*="/kanban"]');
            if (firstProjectLink) {
                // Navigate to first project's kanban board where they can create an issue
                window.location.href = firstProjectLink.getAttribute('href');
            } else {
                // No projects available
                alert('Please select a project first to create an issue.');
            }
        }
    }

    openCreateEpic() {
        window.location.href = '/epics/new';
    }

    openCreateSprint() {
        window.location.href = '/sprints/new';
    }

    openCreateProject() {
        window.location.href = '/projects/new';
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.globalNavigation = new GlobalNavigation();
        console.log('GlobalNavigation loaded on DOMContentLoaded');
    });
} else {
    window.globalNavigation = new GlobalNavigation();
    console.log('GlobalNavigation loaded immediately');
}
