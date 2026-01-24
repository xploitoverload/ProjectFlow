/**
 * Notifications System - Real-time notifications with persistence
 */

class NotificationManager {
    constructor() {
        this.notifications = this.loadNotifications();
        this.unreadCount = 0;
        this.updateUnreadCount();
    }
    
    loadNotifications() {
        const saved = localStorage.getItem('notifications');
        return saved ? JSON.parse(saved) : [];
    }
    
    saveNotifications() {
        localStorage.setItem('notifications', JSON.stringify(this.notifications));
    }
    
    addNotification(notification) {
        const newNotification = {
            id: Date.now(),
            title: notification.title,
            message: notification.message,
            type: notification.type || 'info', // success, error, warning, info
            timestamp: new Date().toISOString(),
            read: false,
            link: notification.link || null
        };
        
        this.notifications.unshift(newNotification);
        
        // Keep only last 100 notifications
        if (this.notifications.length > 100) {
            this.notifications = this.notifications.slice(0, 100);
        }
        
        this.saveNotifications();
        this.updateUnreadCount();
        this.showToast(newNotification);
        
        return newNotification;
    }
    
    markAsRead(notificationId) {
        const notification = this.notifications.find(n => n.id === notificationId);
        if (notification && !notification.read) {
            notification.read = true;
            this.saveNotifications();
            this.updateUnreadCount();
        }
    }
    
    markAllAsRead() {
        this.notifications.forEach(n => n.read = true);
        this.saveNotifications();
        this.updateUnreadCount();
    }
    
    deleteNotification(notificationId) {
        this.notifications = this.notifications.filter(n => n.id !== notificationId);
        this.saveNotifications();
        this.updateUnreadCount();
    }
    
    clearAll() {
        this.notifications = [];
        this.saveNotifications();
        this.updateUnreadCount();
    }
    
    updateUnreadCount() {
        this.unreadCount = this.notifications.filter(n => !n.read).length;
        
        // Update badge
        const badges = document.querySelectorAll('.notification-badge');
        badges.forEach(badge => {
            if (this.unreadCount > 0) {
                badge.textContent = this.unreadCount > 99 ? '99+' : this.unreadCount;
                badge.style.display = 'flex';
            } else {
                badge.style.display = 'none';
            }
        });
    }
    
    showToast(notification) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${notification.type}`;
        toast.innerHTML = `
            <div class="toast-icon">
                <i data-lucide="${this.getIconForType(notification.type)}"></i>
            </div>
            <div class="toast-content">
                <div class="toast-title">${notification.title}</div>
                <div class="toast-message">${notification.message}</div>
            </div>
            <button class="toast-close">
                <i data-lucide="x"></i>
            </button>
        `;
        
        document.body.appendChild(toast);
        
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
        
        // Close button
        toast.querySelector('.toast-close').addEventListener('click', () => {
            this.removeToast(toast);
        });
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            this.removeToast(toast);
        }, 5000);
        
        // Animate in
        requestAnimationFrame(() => {
            toast.classList.add('show');
        });
    }
    
    removeToast(toast) {
        toast.classList.remove('show');
        setTimeout(() => {
            if (toast.parentElement) {
                toast.parentElement.removeChild(toast);
            }
        }, 300);
    }
    
    getIconForType(type) {
        const icons = {
            success: 'check-circle',
            error: 'alert-circle',
            warning: 'alert-triangle',
            info: 'info'
        };
        return icons[type] || 'bell';
    }
    
    getNotifications() {
        return this.notifications;
    }
}

// Initialize notification manager when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.notificationManager = new NotificationManager();
        console.log('NotificationManager loaded on DOMContentLoaded');
    });
} else {
    window.notificationManager = new NotificationManager();
    console.log('NotificationManager loaded immediately');
}
