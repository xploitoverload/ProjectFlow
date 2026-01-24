/**
 * Notifications System - JIRA-style notifications
 * Features: Email notifications, in-app notifications, schemes, @mentions
 */

class NotificationsSystem {
    constructor() {
        this.notifications = [];
        this.unreadCount = 0;
        this.schemes = [];
        this.userPreferences = null;
        this.notificationTypes = this.getNotificationTypes();
        
        this.init();
    }

    init() {
        this.createNotificationBell();
        this.createNotificationPanel();
        this.createPreferencesModal();
        this.createSchemesModal();
        this.setupEventListeners();
        this.loadNotifications();
        this.startPolling();
    }

    getNotificationTypes() {
        return [
            { id: 'issue_created', name: 'Issue Created', category: 'issue', defaultEnabled: true },
            { id: 'issue_updated', name: 'Issue Updated', category: 'issue', defaultEnabled: true },
            { id: 'issue_deleted', name: 'Issue Deleted', category: 'issue', defaultEnabled: true },
            { id: 'issue_assigned', name: 'Issue Assigned to Me', category: 'issue', defaultEnabled: true },
            { id: 'issue_commented', name: 'Comment Added', category: 'comment', defaultEnabled: true },
            { id: 'issue_mentioned', name: 'I was Mentioned', category: 'mention', defaultEnabled: true },
            { id: 'status_changed', name: 'Status Changed', category: 'issue', defaultEnabled: true },
            { id: 'sprint_started', name: 'Sprint Started', category: 'agile', defaultEnabled: true },
            { id: 'sprint_completed', name: 'Sprint Completed', category: 'agile', defaultEnabled: true },
            { id: 'worklog_added', name: 'Work Logged', category: 'time', defaultEnabled: false },
            { id: 'attachment_added', name: 'Attachment Added', category: 'attachment', defaultEnabled: false },
            { id: 'watcher_added', name: 'Added as Watcher', category: 'watcher', defaultEnabled: true }
        ];
    }

    createNotificationBell() {
        const bellHTML = `
            <div class="notification-bell" id="notificationBell">
                <button class="bell-button" id="bellButton">
                    <i data-lucide="bell"></i>
                    <span class="notification-badge" id="notificationBadge" style="display: none;">0</span>
                </button>
            </div>
        `;

        // Insert into header/nav (adjust selector as needed)
        const header = document.querySelector('.navbar') || document.querySelector('header');
        if (header) {
            header.insertAdjacentHTML('beforeend', bellHTML);
        }

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    createNotificationPanel() {
        const panelHTML = `
            <div id="notificationPanel" class="notification-panel" style="display: none;">
                <div class="panel-header">
                    <h3>Notifications</h3>
                    <div class="panel-actions">
                        <button class="btn-icon-sm" id="markAllReadBtn" title="Mark all as read">
                            <i data-lucide="check-check"></i>
                        </button>
                        <button class="btn-icon-sm" id="notifPrefsBtn" title="Preferences">
                            <i data-lucide="settings"></i>
                        </button>
                    </div>
                </div>

                <div class="panel-tabs">
                    <button class="panel-tab active" data-tab="all">All</button>
                    <button class="panel-tab" data-tab="unread">Unread</button>
                    <button class="panel-tab" data-tab="mentions">Mentions</button>
                </div>

                <div class="panel-content" id="notificationList">
                    <!-- Populated by JS -->
                </div>

                <div class="panel-footer">
                    <a href="#" id="viewAllNotificationsLink">View all notifications</a>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', panelHTML);

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    createPreferencesModal() {
        const modalHTML = `
            <div id="notifPreferencesModal" class="notif-modal" style="display: none;">
                <div class="notif-modal-backdrop"></div>
                <div class="notif-modal-container">
                    <div class="notif-modal-header">
                        <h2>Notification Preferences</h2>
                        <button class="btn-icon" id="closePrefsModal">
                            <i data-lucide="x"></i>
                        </button>
                    </div>

                    <div class="notif-modal-body">
                        <div class="prefs-section">
                            <h3>Email Notifications</h3>
                            <p class="section-desc">Choose which notifications you want to receive via email</p>
                            
                            <div class="prefs-list" id="emailPrefsList">
                                <!-- Populated by JS -->
                            </div>
                        </div>

                        <div class="prefs-section">
                            <h3>In-App Notifications</h3>
                            <p class="section-desc">Choose which notifications appear in your notification panel</p>
                            
                            <div class="prefs-list" id="inAppPrefsList">
                                <!-- Populated by JS -->
                            </div>
                        </div>

                        <div class="prefs-section">
                            <h3>Notification Frequency</h3>
                            <select class="form-input" id="notifFrequency">
                                <option value="instant">Instant (as they happen)</option>
                                <option value="hourly">Hourly Digest</option>
                                <option value="daily">Daily Digest</option>
                                <option value="never">Never</option>
                            </select>
                        </div>

                        <div class="prefs-section">
                            <h3>Watch Settings</h3>
                            <label class="checkbox-label">
                                <input type="checkbox" id="autoWatchCreated">
                                <span>Automatically watch issues I create</span>
                            </label>
                            <label class="checkbox-label">
                                <input type="checkbox" id="autoWatchCommented">
                                <span>Automatically watch issues I comment on</span>
                            </label>
                            <label class="checkbox-label">
                                <input type="checkbox" id="autoWatchAssigned">
                                <span>Automatically watch issues assigned to me</span>
                            </label>
                        </div>
                    </div>

                    <div class="notif-modal-footer">
                        <button class="btn btn-ghost" onclick="notificationsSystem.closePreferencesModal()">Cancel</button>
                        <button class="btn btn-primary" id="savePrefsBtn">Save Preferences</button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    createSchemesModal() {
        const modalHTML = `
            <div id="notifSchemesModal" class="notif-modal" style="display: none;">
                <div class="notif-modal-backdrop"></div>
                <div class="notif-modal-container large">
                    <div class="notif-modal-header">
                        <h2>Notification Schemes</h2>
                        <div class="header-actions">
                            <button class="btn btn-primary btn-sm" id="createNotifSchemeBtn">
                                <i data-lucide="plus"></i>
                                Create Scheme
                            </button>
                            <button class="btn-icon" id="closeSchemesModal">
                                <i data-lucide="x"></i>
                            </button>
                        </div>
                    </div>

                    <div class="notif-modal-body">
                        <div class="schemes-list" id="notifSchemesList">
                            <!-- Populated by JS -->
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    setupEventListeners() {
        // Bell button
        document.getElementById('bellButton')?.addEventListener('click', () => {
            this.togglePanel();
        });

        // Panel tabs
        document.querySelectorAll('.panel-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // Mark all read
        document.getElementById('markAllReadBtn')?.addEventListener('click', () => {
            this.markAllAsRead();
        });

        // Preferences button
        document.getElementById('notifPrefsBtn')?.addEventListener('click', () => {
            this.openPreferencesModal();
        });

        // Close modals
        document.getElementById('closePrefsModal')?.addEventListener('click', () => {
            this.closePreferencesModal();
        });

        document.getElementById('closeSchemesModal')?.addEventListener('click', () => {
            this.closeSchemesModal();
        });

        // Save preferences
        document.getElementById('savePrefsBtn')?.addEventListener('click', () => {
            this.savePreferences();
        });

        // Click outside to close panel
        document.addEventListener('click', (e) => {
            const panel = document.getElementById('notificationPanel');
            const bell = document.getElementById('notificationBell');
            
            if (panel && bell && 
                !panel.contains(e.target) && 
                !bell.contains(e.target) && 
                panel.style.display === 'block') {
                this.closePanel();
            }
        });
    }

    togglePanel() {
        const panel = document.getElementById('notificationPanel');
        if (panel.style.display === 'none') {
            this.openPanel();
        } else {
            this.closePanel();
        }
    }

    openPanel() {
        document.getElementById('notificationPanel').style.display = 'block';
        this.renderNotifications('all');
    }

    closePanel() {
        document.getElementById('notificationPanel').style.display = 'none';
    }

    switchTab(tab) {
        document.querySelectorAll('.panel-tab').forEach(t => t.classList.remove('active'));
        document.querySelector(`[data-tab="${tab}"]`).classList.add('active');
        this.renderNotifications(tab);
    }

    async loadNotifications() {
        try {
            const response = await fetch('/api/notifications');
            if (response.ok) {
                this.notifications = await response.json();
                this.updateBadge();
            }
        } catch (error) {
            console.error('Failed to load notifications:', error);
        }
    }

    renderNotifications(filter = 'all') {
        let filtered = this.notifications;

        if (filter === 'unread') {
            filtered = this.notifications.filter(n => !n.read);
        } else if (filter === 'mentions') {
            filtered = this.notifications.filter(n => n.type === 'issue_mentioned');
        }

        const container = document.getElementById('notificationList');

        if (filtered.length === 0) {
            container.innerHTML = `
                <div class="empty-notifications">
                    <i data-lucide="inbox"></i>
                    <p>No notifications</p>
                </div>
            `;
            if (window.lucide) {
                lucide.createIcons();
            }
            return;
        }

        container.innerHTML = filtered.map(notif => this.renderNotification(notif)).join('');

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    renderNotification(notif) {
        const timeAgo = this.getTimeAgo(notif.timestamp);
        const icon = this.getNotificationIcon(notif.type);

        return `
            <div class="notification-item ${notif.read ? 'read' : 'unread'}" 
                 onclick="notificationsSystem.handleNotificationClick('${notif.id}')">
                <div class="notif-icon">
                    <i data-lucide="${icon}"></i>
                </div>
                <div class="notif-content">
                    <div class="notif-title">${notif.title}</div>
                    <div class="notif-message">${notif.message}</div>
                    <div class="notif-meta">
                        <span class="notif-time">${timeAgo}</span>
                        ${notif.issueKey ? `<span class="notif-issue">${notif.issueKey}</span>` : ''}
                    </div>
                </div>
                ${!notif.read ? '<div class="unread-indicator"></div>' : ''}
            </div>
        `;
    }

    getNotificationIcon(type) {
        const icons = {
            'issue_created': 'plus-circle',
            'issue_updated': 'edit',
            'issue_assigned': 'user-check',
            'issue_commented': 'message-square',
            'issue_mentioned': 'at-sign',
            'status_changed': 'git-branch',
            'sprint_started': 'play-circle',
            'sprint_completed': 'check-circle',
            'worklog_added': 'clock',
            'attachment_added': 'paperclip',
            'watcher_added': 'eye'
        };
        return icons[type] || 'bell';
    }

    getTimeAgo(timestamp) {
        const now = new Date();
        const then = new Date(timestamp);
        const diff = Math.floor((now - then) / 1000);

        if (diff < 60) return 'Just now';
        if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
        if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
        if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`;
        return then.toLocaleDateString();
    }

    async handleNotificationClick(notifId) {
        const notif = this.notifications.find(n => n.id === notifId);
        if (!notif) return;

        // Mark as read
        if (!notif.read) {
            await this.markAsRead(notifId);
        }

        // Navigate to issue or relevant page
        if (notif.issueKey) {
            window.location.href = `/issue/${notif.issueKey}`;
        } else if (notif.link) {
            window.location.href = notif.link;
        }

        this.closePanel();
    }

    async markAsRead(notifId) {
        try {
            const response = await fetch(`/api/notifications/${notifId}/read`, {
                method: 'POST'
            });

            if (response.ok) {
                const notif = this.notifications.find(n => n.id === notifId);
                if (notif) {
                    notif.read = true;
                    this.updateBadge();
                    this.renderNotifications(
                        document.querySelector('.panel-tab.active').dataset.tab
                    );
                }
            }
        } catch (error) {
            console.error('Failed to mark as read:', error);
        }
    }

    async markAllAsRead() {
        try {
            const response = await fetch('/api/notifications/read-all', {
                method: 'POST'
            });

            if (response.ok) {
                this.notifications.forEach(n => n.read = true);
                this.updateBadge();
                this.renderNotifications(
                    document.querySelector('.panel-tab.active').dataset.tab
                );
            }
        } catch (error) {
            console.error('Failed to mark all as read:', error);
        }
    }

    updateBadge() {
        this.unreadCount = this.notifications.filter(n => !n.read).length;
        const badge = document.getElementById('notificationBadge');
        
        if (this.unreadCount > 0) {
            badge.textContent = this.unreadCount > 99 ? '99+' : this.unreadCount;
            badge.style.display = 'block';
        } else {
            badge.style.display = 'none';
        }
    }

    openPreferencesModal() {
        this.closePanel();
        this.loadUserPreferences();
        this.renderPreferences();
        document.getElementById('notifPreferencesModal').style.display = 'block';
    }

    closePreferencesModal() {
        document.getElementById('notifPreferencesModal').style.display = 'none';
    }

    async loadUserPreferences() {
        try {
            const response = await fetch('/api/user/notification-preferences');
            if (response.ok) {
                this.userPreferences = await response.json();
            } else {
                // Default preferences
                this.userPreferences = {
                    email: {},
                    inApp: {},
                    frequency: 'instant',
                    autoWatch: {
                        created: true,
                        commented: true,
                        assigned: true
                    }
                };
            }
        } catch (error) {
            console.error('Failed to load preferences:', error);
        }
    }

    renderPreferences() {
        // Email preferences
        const emailList = document.getElementById('emailPrefsList');
        emailList.innerHTML = this.notificationTypes.map(type => {
            const enabled = this.userPreferences.email[type.id] !== false;
            return `
                <label class="pref-item">
                    <input type="checkbox" data-email="${type.id}" ${enabled ? 'checked' : ''}>
                    <div class="pref-info">
                        <div class="pref-name">${type.name}</div>
                    </div>
                </label>
            `;
        }).join('');

        // In-app preferences
        const inAppList = document.getElementById('inAppPrefsList');
        inAppList.innerHTML = this.notificationTypes.map(type => {
            const enabled = this.userPreferences.inApp[type.id] !== false;
            return `
                <label class="pref-item">
                    <input type="checkbox" data-inapp="${type.id}" ${enabled ? 'checked' : ''}>
                    <div class="pref-info">
                        <div class="pref-name">${type.name}</div>
                    </div>
                </label>
            `;
        }).join('');

        // Frequency
        document.getElementById('notifFrequency').value = this.userPreferences.frequency || 'instant';

        // Auto-watch
        document.getElementById('autoWatchCreated').checked = this.userPreferences.autoWatch?.created !== false;
        document.getElementById('autoWatchCommented').checked = this.userPreferences.autoWatch?.commented !== false;
        document.getElementById('autoWatchAssigned').checked = this.userPreferences.autoWatch?.assigned !== false;
    }

    async savePreferences() {
        const preferences = {
            email: {},
            inApp: {},
            frequency: document.getElementById('notifFrequency').value,
            autoWatch: {
                created: document.getElementById('autoWatchCreated').checked,
                commented: document.getElementById('autoWatchCommented').checked,
                assigned: document.getElementById('autoWatchAssigned').checked
            }
        };

        // Gather email preferences
        document.querySelectorAll('[data-email]').forEach(input => {
            preferences.email[input.dataset.email] = input.checked;
        });

        // Gather in-app preferences
        document.querySelectorAll('[data-inapp]').forEach(input => {
            preferences.inApp[input.dataset.inapp] = input.checked;
        });

        try {
            const response = await fetch('/api/user/notification-preferences', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(preferences)
            });

            if (response.ok) {
                this.userPreferences = preferences;
                this.closePreferencesModal();
                this.showToast('Preferences saved successfully');
            }
        } catch (error) {
            console.error('Failed to save preferences:', error);
            this.showToast('Failed to save preferences', 'error');
        }
    }

    openSchemesModal() {
        document.getElementById('notifSchemesModal').style.display = 'block';
        this.loadSchemes();
    }

    closeSchemesModal() {
        document.getElementById('notifSchemesModal').style.display = 'none';
    }

    async loadSchemes() {
        try {
            const response = await fetch('/api/notification-schemes');
            if (response.ok) {
                this.schemes = await response.json();
                this.renderSchemes();
            }
        } catch (error) {
            console.error('Failed to load schemes:', error);
        }
    }

    renderSchemes() {
        const container = document.getElementById('notifSchemesList');
        
        if (this.schemes.length === 0) {
            container.innerHTML = '<p class="empty-text">No notification schemes yet</p>';
            return;
        }

        container.innerHTML = this.schemes.map(scheme => `
            <div class="scheme-card">
                <div class="scheme-header">
                    <h4>${scheme.name}</h4>
                    <div class="scheme-actions">
                        <button class="btn btn-ghost btn-sm" onclick="notificationsSystem.editScheme('${scheme.id}')">
                            <i data-lucide="edit-2"></i>
                            Edit
                        </button>
                        <button class="btn btn-ghost btn-sm" onclick="notificationsSystem.deleteScheme('${scheme.id}')">
                            <i data-lucide="trash-2"></i>
                            Delete
                        </button>
                    </div>
                </div>
                <p class="scheme-desc">${scheme.description || 'No description'}</p>
                <div class="scheme-projects">${scheme.projects?.length || 0} projects using this scheme</div>
            </div>
        `).join('');

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    startPolling() {
        // Poll for new notifications every 30 seconds
        setInterval(() => {
            this.loadNotifications();
        }, 30000);
    }

    // Utility: Show toast notification
    showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('show');
        }, 10);

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // Public method to add notification (for testing or real-time)
    addNotification(notification) {
        this.notifications.unshift(notification);
        this.updateBadge();
        
        // Show toast for new notification if preferences allow
        if (this.userPreferences?.inApp[notification.type] !== false) {
            this.showToast(notification.title);
        }

        // If panel is open, refresh
        const panel = document.getElementById('notificationPanel');
        if (panel && panel.style.display === 'block') {
            this.renderNotifications(
                document.querySelector('.panel-tab.active').dataset.tab
            );
        }
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.notificationsSystem = new NotificationsSystem();
});

// Global function to open notification schemes
function openNotificationSchemes() {
    window.notificationsSystem?.openSchemesModal();
}
