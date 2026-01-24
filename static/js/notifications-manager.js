/**
 * Notifications Module
 * Manages real-time notifications with dropdown display
 */

class NotificationsManager {
    constructor() {
        this.notifications = [];
        this.unreadCount = 0;
        this.isOpen = false;
        this.dropdownElement = null;
        this.bellButton = null;
        this.pollInterval = 30000; // Poll every 30 seconds
        this.pollTimer = null;
        
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
        // Find the notifications bell button
        this.bellButton = document.getElementById('notificationsBtn');
        if (!this.bellButton) {
            console.warn('Notifications button not found');
            return;
        }

        // Create dropdown
        this.createDropdown();

        // Add click handler to bell button
        this.bellButton.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.toggleDropdown();
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (this.isOpen && 
                !this.dropdownElement.contains(e.target) && 
                !this.bellButton.contains(e.target)) {
                this.closeDropdown();
            }
        });

        // Load notifications
        this.loadNotifications();

        // Start polling for new notifications
        this.startPolling();

        console.log('Notifications initialized');
    }

    createDropdown() {
        // Remove existing dropdown if present
        const existing = document.querySelector('.notifications-dropdown');
        if (existing) {
            existing.remove();
        }

        // Create dropdown HTML
        const dropdownHTML = `
            <div class="notifications-dropdown" style="display: none;">
                <div class="notifications-header">
                    <h3 class="notifications-title">Notifications</h3>
                    <button class="notifications-mark-all" title="Mark all as read">
                        <i data-lucide="check-check"></i>
                    </button>
                </div>
                <div class="notifications-body">
                    <div class="notifications-loading">
                        <i data-lucide="loader-2" class="notifications-loading-icon"></i>
                        Loading notifications...
                    </div>
                </div>
                <div class="notifications-footer">
                    <a href="/notifications" class="notifications-view-all">
                        View all notifications
                        <i data-lucide="arrow-right"></i>
                    </a>
                </div>
            </div>
        `;

        // Insert dropdown after the bell button
        this.bellButton.insertAdjacentHTML('afterend', dropdownHTML);
        this.dropdownElement = document.querySelector('.notifications-dropdown');

        // Initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }

        // Add mark all as read handler
        const markAllBtn = this.dropdownElement.querySelector('.notifications-mark-all');
        markAllBtn?.addEventListener('click', () => this.markAllAsRead());
    }

    async loadNotifications() {
        try {
            const response = await fetch('/api/v1/notifications?limit=20');
            const data = await response.json();

            if (data.success) {
                this.notifications = data.data;
                this.unreadCount = data.unread_count;
                this.updateBadge();
                this.renderNotifications();
            }
        } catch (error) {
            console.error('Failed to load notifications:', error);
            this.renderError();
        }
    }

    async loadUnreadCount() {
        try {
            const response = await fetch('/api/v1/notifications/unread-count');
            const data = await response.json();

            if (data.success) {
                this.unreadCount = data.count;
                this.updateBadge();
            }
        } catch (error) {
            console.error('Failed to load unread count:', error);
        }
    }

    updateBadge() {
        // Update or create badge
        let badge = this.bellButton.querySelector('.notification-badge');
        
        if (this.unreadCount > 0) {
            if (!badge) {
                badge = document.createElement('span');
                badge.className = 'notification-badge';
                this.bellButton.appendChild(badge);
            }
            badge.textContent = this.unreadCount > 99 ? '99+' : this.unreadCount;
            badge.style.display = 'flex';
        } else if (badge) {
            badge.style.display = 'none';
        }
    }

    renderNotifications() {
        const body = this.dropdownElement.querySelector('.notifications-body');
        
        if (this.notifications.length === 0) {
            body.innerHTML = `
                <div class="notifications-empty">
                    <i data-lucide="inbox" class="notifications-empty-icon"></i>
                    <p class="notifications-empty-text">No notifications</p>
                    <p class="notifications-empty-subtext">You're all caught up!</p>
                </div>
            `;
        } else {
            body.innerHTML = `
                <div class="notifications-list">
                    ${this.notifications.map(notif => this.renderNotification(notif)).join('')}
                </div>
            `;

            // Add click handlers to notifications
            this.attachNotificationHandlers();
        }

        // Initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }

    renderNotification(notif) {
        const timeAgo = this.formatTimeAgo(new Date(notif.created_at));
        const unreadClass = notif.is_read ? '' : 'notification-unread';
        
        return `
            <div class="notification-item ${unreadClass}" data-id="${notif.id}" data-link="${notif.link || ''}">
                <div class="notification-icon notification-icon-${notif.type}">
                    <i data-lucide="${notif.icon || 'bell'}"></i>
                </div>
                <div class="notification-content">
                    <div class="notification-title">${this.escapeHtml(notif.title)}</div>
                    ${notif.message ? `<div class="notification-message">${this.escapeHtml(notif.message)}</div>` : ''}
                    <div class="notification-time">${timeAgo}</div>
                </div>
                <div class="notification-actions">
                    ${!notif.is_read ? `
                        <button class="notification-mark-read" data-id="${notif.id}" title="Mark as read">
                            <i data-lucide="check"></i>
                        </button>
                    ` : ''}
                    <button class="notification-delete" data-id="${notif.id}" title="Delete">
                        <i data-lucide="x"></i>
                    </button>
                </div>
            </div>
        `;
    }

    attachNotificationHandlers() {
        // Click on notification to navigate
        const items = this.dropdownElement.querySelectorAll('.notification-item');
        items.forEach(item => {
            item.addEventListener('click', (e) => {
                if (e.target.closest('.notification-actions')) {
                    return; // Don't navigate if clicking action buttons
                }
                
                const link = item.dataset.link;
                const id = parseInt(item.dataset.id);
                
                if (link) {
                    this.markAsRead(id);
                    window.location.href = link;
                }
            });
        });

        // Mark as read buttons
        const markReadBtns = this.dropdownElement.querySelectorAll('.notification-mark-read');
        markReadBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const id = parseInt(btn.dataset.id);
                this.markAsRead(id);
            });
        });

        // Delete buttons
        const deleteBtns = this.dropdownElement.querySelectorAll('.notification-delete');
        deleteBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const id = parseInt(btn.dataset.id);
                this.deleteNotification(id);
            });
        });
    }

    async markAsRead(notificationId) {
        try {
            const response = await fetch(`/api/v1/notifications/${notificationId}/read`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (data.success) {
                // Update local state
                const notif = this.notifications.find(n => n.id === notificationId);
                if (notif && !notif.is_read) {
                    notif.is_read = true;
                    notif.read_at = new Date().toISOString();
                    this.unreadCount = Math.max(0, this.unreadCount - 1);
                    this.updateBadge();
                    this.renderNotifications();
                }
            }
        } catch (error) {
            console.error('Failed to mark notification as read:', error);
        }
    }

    async markAllAsRead() {
        try {
            const response = await fetch('/api/v1/notifications/mark-all-read', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (data.success) {
                // Update local state
                this.notifications.forEach(notif => {
                    notif.is_read = true;
                    notif.read_at = new Date().toISOString();
                });
                this.unreadCount = 0;
                this.updateBadge();
                this.renderNotifications();
            }
        } catch (error) {
            console.error('Failed to mark all as read:', error);
        }
    }

    async deleteNotification(notificationId) {
        try {
            const response = await fetch(`/api/v1/notifications/${notificationId}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (data.success) {
                // Remove from local state
                const index = this.notifications.findIndex(n => n.id === notificationId);
                if (index !== -1) {
                    const wasUnread = !this.notifications[index].is_read;
                    this.notifications.splice(index, 1);
                    
                    if (wasUnread) {
                        this.unreadCount = Math.max(0, this.unreadCount - 1);
                        this.updateBadge();
                    }
                    
                    this.renderNotifications();
                }
            }
        } catch (error) {
            console.error('Failed to delete notification:', error);
        }
    }

    renderError() {
        const body = this.dropdownElement.querySelector('.notifications-body');
        body.innerHTML = `
            <div class="notifications-error">
                <i data-lucide="alert-circle" class="notifications-error-icon"></i>
                <p>Failed to load notifications</p>
                <button class="btn btn-sm btn-ghost" onclick="window.notificationsManager.loadNotifications()">
                    Retry
                </button>
            </div>
        `;
        
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }

    toggleDropdown() {
        if (this.isOpen) {
            this.closeDropdown();
        } else {
            this.openDropdown();
        }
    }

    openDropdown() {
        if (!this.dropdownElement) return;
        
        this.dropdownElement.style.display = 'block';
        setTimeout(() => {
            this.dropdownElement.classList.add('notifications-dropdown-open');
        }, 10);
        
        this.isOpen = true;
        
        // Reload notifications when opening
        this.loadNotifications();
    }

    closeDropdown() {
        if (!this.dropdownElement) return;
        
        this.dropdownElement.classList.remove('notifications-dropdown-open');
        setTimeout(() => {
            this.dropdownElement.style.display = 'none';
        }, 200);
        
        this.isOpen = false;
    }

    startPolling() {
        // Poll for new notifications periodically
        this.pollTimer = setInterval(() => {
            if (!this.isOpen) {
                // Only poll for unread count if dropdown is closed
                this.loadUnreadCount();
            }
        }, this.pollInterval);
    }

    stopPolling() {
        if (this.pollTimer) {
            clearInterval(this.pollTimer);
            this.pollTimer = null;
        }
    }

    formatTimeAgo(date) {
        const now = new Date();
        const seconds = Math.floor((now - date) / 1000);
        
        if (seconds < 60) return 'Just now';
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
        if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
        
        return date.toLocaleDateString();
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize notifications manager
const notificationsManager = new NotificationsManager();

// Expose globally for debugging
window.notificationsManager = notificationsManager;
