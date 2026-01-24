/**
 * User Menu Module
 * Manages the expanded user avatar menu with profile, settings, shortcuts, and more
 */

class UserMenu {
    constructor() {
        this.isOpen = false;
        this.menuElement = null;
        this.triggerElement = null;
        this.shortcutsModal = null;
        this.whatsNewModal = null;
        
        this.init();
    }

    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    setup() {
        // Find the sidebar user element
        this.triggerElement = document.querySelector('.sidebar-user');
        if (!this.triggerElement) {
            console.warn('User menu trigger not found');
            return;
        }

        // Create the menu dropdown
        this.createMenu();

        // Add click handler to trigger
        this.triggerElement.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.toggleMenu();
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (this.isOpen && !this.menuElement.contains(e.target) && !this.triggerElement.contains(e.target)) {
                this.closeMenu();
            }
        });

        // Close menu on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.closeMenu();
            }
        });

        console.log('User menu initialized');
    }

    createMenu() {
        // Remove existing menu if present
        const existing = document.querySelector('.user-menu-dropdown');
        if (existing) {
            existing.remove();
        }

        // Get user info from the sidebar element
        const userName = this.triggerElement.querySelector('.sidebar-user-name')?.textContent || 'User';
        const userRole = this.triggerElement.querySelector('.sidebar-user-role')?.textContent || 'Guest';
        const userAvatar = this.triggerElement.querySelector('.sidebar-user-avatar');
        const avatarText = userAvatar?.textContent || 'U';
        const avatarColor = userAvatar?.style.background || 'var(--primary-100)';

        // Create menu HTML
        const menuHTML = `
            <div class="user-menu-dropdown" style="display: none;">
                <div class="user-menu-header">
                    <div class="user-menu-avatar" style="background: ${avatarColor};">
                        ${avatarText}
                    </div>
                    <div class="user-menu-user-info">
                        <div class="user-menu-name">${userName}</div>
                        <div class="user-menu-role">${userRole}</div>
                    </div>
                </div>
                
                <div class="user-menu-divider"></div>
                
                <div class="user-menu-section">
                    <a href="${this.getUrl('main.profile')}" class="user-menu-item">
                        <i data-lucide="user" class="user-menu-icon"></i>
                        <div class="user-menu-item-content">
                            <div class="user-menu-item-title">Profile</div>
                            <div class="user-menu-item-subtitle">View and edit your profile</div>
                        </div>
                    </a>
                    
                    <a href="${this.getUrl('main.settings')}" class="user-menu-item">
                        <i data-lucide="settings" class="user-menu-icon"></i>
                        <div class="user-menu-item-content">
                            <div class="user-menu-item-title">Settings</div>
                            <div class="user-menu-item-subtitle">Manage your preferences</div>
                        </div>
                    </a>
                </div>
                
                <div class="user-menu-divider"></div>
                
                <div class="user-menu-section">
                    <button class="user-menu-item user-menu-btn" data-action="shortcuts">
                        <i data-lucide="command" class="user-menu-icon"></i>
                        <div class="user-menu-item-content">
                            <div class="user-menu-item-title">Keyboard Shortcuts</div>
                            <div class="user-menu-item-subtitle">View all shortcuts</div>
                        </div>
                        <kbd class="user-menu-kbd">?</kbd>
                    </button>
                    
                    <button class="user-menu-item user-menu-btn" data-action="whats-new">
                        <i data-lucide="sparkles" class="user-menu-icon"></i>
                        <div class="user-menu-item-content">
                            <div class="user-menu-item-title">What's New</div>
                            <div class="user-menu-item-subtitle">Recent updates & features</div>
                        </div>
                        <span class="user-menu-badge">5</span>
                    </button>
                </div>
                
                <div class="user-menu-divider"></div>
                
                <div class="user-menu-section">
                    <button class="user-menu-item user-menu-btn" data-action="theme">
                        <i data-lucide="moon" class="user-menu-icon" data-theme-icon></i>
                        <div class="user-menu-item-content">
                            <div class="user-menu-item-title">Theme</div>
                            <div class="user-menu-item-subtitle" data-theme-text>Switch to dark mode</div>
                        </div>
                    </button>
                </div>
                
                <div class="user-menu-divider"></div>
                
                <div class="user-menu-section">
                    <a href="${this.getUrl('auth.logout')}" class="user-menu-item user-menu-danger">
                        <i data-lucide="log-out" class="user-menu-icon"></i>
                        <div class="user-menu-item-content">
                            <div class="user-menu-item-title">Sign Out</div>
                        </div>
                    </a>
                </div>
            </div>
        `;

        // Insert menu after sidebar footer
        const sidebarFooter = document.querySelector('.sidebar-footer');
        if (sidebarFooter) {
            sidebarFooter.insertAdjacentHTML('afterend', menuHTML);
            this.menuElement = document.querySelector('.user-menu-dropdown');
            
            // Initialize Lucide icons in the menu
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
            
            // Add event listeners to menu items
            this.setupMenuHandlers();
        }
    }

    setupMenuHandlers() {
        if (!this.menuElement) return;

        // Handle button clicks
        const buttons = this.menuElement.querySelectorAll('[data-action]');
        buttons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const action = btn.dataset.action;
                this.handleAction(action);
            });
        });

        // Update theme toggle based on current theme
        this.updateThemeToggle();
    }

    handleAction(action) {
        switch (action) {
            case 'shortcuts':
                this.showShortcutsModal();
                break;
            case 'whats-new':
                this.showWhatsNewModal();
                break;
            case 'theme':
                this.toggleTheme();
                break;
        }
        
        this.closeMenu();
    }

    toggleMenu() {
        if (this.isOpen) {
            this.closeMenu();
        } else {
            this.openMenu();
        }
    }

    openMenu() {
        if (!this.menuElement) return;
        
        this.menuElement.style.display = 'block';
        setTimeout(() => {
            this.menuElement.classList.add('user-menu-open');
        }, 10);
        
        this.isOpen = true;
    }

    closeMenu() {
        if (!this.menuElement) return;
        
        this.menuElement.classList.remove('user-menu-open');
        setTimeout(() => {
            this.menuElement.style.display = 'none';
        }, 200);
        
        this.isOpen = false;
    }

    toggleTheme() {
        // Check if ThemeManager exists
        if (typeof window.themeManager !== 'undefined') {
            window.themeManager.toggleTheme();
            setTimeout(() => this.updateThemeToggle(), 100);
        } else {
            // Fallback: toggle manually
            const html = document.documentElement;
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            this.updateThemeToggle();
        }
    }

    updateThemeToggle() {
        const themeIcon = this.menuElement?.querySelector('[data-theme-icon]');
        const themeText = this.menuElement?.querySelector('[data-theme-text]');
        
        if (!themeIcon || !themeText) return;

        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        
        if (currentTheme === 'dark') {
            themeIcon.setAttribute('data-lucide', 'sun');
            themeText.textContent = 'Switch to light mode';
        } else {
            themeIcon.setAttribute('data-lucide', 'moon');
            themeText.textContent = 'Switch to dark mode';
        }
        
        // Reinitialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }

    showShortcutsModal() {
        // Remove existing modal if present
        if (this.shortcutsModal) {
            this.shortcutsModal.remove();
        }

        const shortcuts = [
            { category: 'Navigation', items: [
                { keys: ['G', 'D'], description: 'Go to Dashboard' },
                { keys: ['G', 'P'], description: 'Go to Projects' },
                { keys: ['G', 'B'], description: 'Go to Board' },
                { keys: ['G', 'I'], description: 'Go to Issues' },
                { keys: ['G', 'R'], description: 'Go to Reports' },
            ]},
            { category: 'Search & Create', items: [
                { keys: ['Cmd/Ctrl', 'K'], description: 'Open Search' },
                { keys: ['C'], description: 'Create Issue' },
                { keys: ['?'], description: 'Show Shortcuts' },
            ]},
            { category: 'Actions', items: [
                { keys: ['Esc'], description: 'Close Modal/Dropdown' },
                { keys: ['↑', '↓'], description: 'Navigate Lists' },
                { keys: ['Enter'], description: 'Select Item' },
            ]}
        ];

        const modalHTML = `
            <div class="shortcuts-modal-overlay" id="shortcutsModal">
                <div class="shortcuts-modal">
                    <div class="shortcuts-modal-header">
                        <h2>Keyboard Shortcuts</h2>
                        <button class="shortcuts-modal-close" onclick="document.getElementById('shortcutsModal').remove()">
                            <i data-lucide="x"></i>
                        </button>
                    </div>
                    <div class="shortcuts-modal-body">
                        ${shortcuts.map(section => `
                            <div class="shortcuts-section">
                                <h3 class="shortcuts-category">${section.category}</h3>
                                <div class="shortcuts-list">
                                    ${section.items.map(item => `
                                        <div class="shortcut-item">
                                            <div class="shortcut-keys">
                                                ${item.keys.map(key => `<kbd class="shortcut-kbd">${key}</kbd>`).join(' + ')}
                                            </div>
                                            <div class="shortcut-description">${item.description}</div>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
        this.shortcutsModal = document.getElementById('shortcutsModal');
        
        // Initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }

        // Close on overlay click
        this.shortcutsModal.addEventListener('click', (e) => {
            if (e.target === this.shortcutsModal) {
                this.shortcutsModal.remove();
            }
        });

        // Close on Escape
        const escHandler = (e) => {
            if (e.key === 'Escape') {
                this.shortcutsModal?.remove();
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);
    }

    showWhatsNewModal() {
        // Remove existing modal if present
        if (this.whatsNewModal) {
            this.whatsNewModal.remove();
        }

        const updates = [
            {
                version: '2.1.0',
                date: 'Jan 15, 2024',
                features: [
                    'New search autocomplete with intelligent suggestions',
                    'Starred items system for quick access',
                    'Recent items tracking',
                    'Enhanced keyboard shortcuts'
                ]
            },
            {
                version: '2.0.5',
                date: 'Jan 10, 2024',
                features: [
                    'Project switcher with keyboard navigation',
                    'Improved command palette',
                    'Dark mode enhancements'
                ]
            }
        ];

        const modalHTML = `
            <div class="whats-new-modal-overlay" id="whatsNewModal">
                <div class="whats-new-modal">
                    <div class="whats-new-modal-header">
                        <div>
                            <h2>What's New</h2>
                            <p class="whats-new-subtitle">Recent updates and features</p>
                        </div>
                        <button class="whats-new-modal-close" onclick="document.getElementById('whatsNewModal').remove()">
                            <i data-lucide="x"></i>
                        </button>
                    </div>
                    <div class="whats-new-modal-body">
                        ${updates.map(update => `
                            <div class="whats-new-section">
                                <div class="whats-new-version">
                                    <span class="whats-new-version-number">v${update.version}</span>
                                    <span class="whats-new-date">${update.date}</span>
                                </div>
                                <ul class="whats-new-features">
                                    ${update.features.map(feature => `
                                        <li class="whats-new-feature">
                                            <i data-lucide="check-circle" class="whats-new-icon"></i>
                                            ${feature}
                                        </li>
                                    `).join('')}
                                </ul>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
        this.whatsNewModal = document.getElementById('whatsNewModal');
        
        // Initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }

        // Close on overlay click
        this.whatsNewModal.addEventListener('click', (e) => {
            if (e.target === this.whatsNewModal) {
                this.whatsNewModal.remove();
            }
        });

        // Close on Escape
        const escHandler = (e) => {
            if (e.key === 'Escape') {
                this.whatsNewModal?.remove();
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);
    }

    getUrl(endpoint) {
        // Try to get URL from Flask's url_for
        // Fallback to basic routing
        const routes = {
            'main.profile': '/profile',
            'main.settings': '/settings',
            'auth.logout': '/auth/logout'
        };
        
        return routes[endpoint] || '#';
    }
}

// Initialize user menu
const userMenu = new UserMenu();

// Also listen for the ? key to show shortcuts from anywhere
document.addEventListener('keydown', (e) => {
    if (e.key === '?' && !e.ctrlKey && !e.metaKey && !e.altKey) {
        const target = e.target;
        // Don't trigger if typing in an input
        if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
            return;
        }
        e.preventDefault();
        userMenu.showShortcutsModal();
    }
});
