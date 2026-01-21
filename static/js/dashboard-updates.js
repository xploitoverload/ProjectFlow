/**
 * Dashboard Updates - Real-time project status and report updates
 */

class DashboardUpdates {
    constructor(refreshInterval = 30000) {
        this.refreshInterval = refreshInterval; // 30 seconds
        this.updateTimers = {};
        this.init();
    }

    init() {
        // Find all project cards with data-project-id
        const projectCards = document.querySelectorAll('[data-project-id]');
        projectCards.forEach(card => {
            const projectId = card.getAttribute('data-project-id');
            this.startLiveUpdates(projectId, card);
        });
    }

    startLiveUpdates(projectId, cardElement) {
        // Initial load
        this.fetchProjectStatus(projectId, cardElement);

        // Set up periodic refresh
        this.updateTimers[projectId] = setInterval(() => {
            this.fetchProjectStatus(projectId, cardElement);
        }, this.refreshInterval);
    }

    fetchProjectStatus(projectId, cardElement) {
        fetch(`/api/project/${projectId}/status`)
            .then(response => {
                if (!response.ok) throw new Error('Failed to fetch status');
                return response.json();
            })
            .then(data => {
                this.updateCard(cardElement, data);
            })
            .catch(error => {
                console.error('Error fetching project status:', error);
            });
    }

    updateCard(cardElement, data) {
        // Update project status indicator
        const statusElement = cardElement.querySelector('[data-status]');
        if (statusElement) {
            statusElement.textContent = data.status;
            statusElement.className = `status status-${data.status.toLowerCase().replace(/\s+/g, '-')}`;
        }

        // Update progress if available
        const progressElement = cardElement.querySelector('[data-progress]');
        if (progressElement && data.latest_update) {
            const progress = data.latest_update.progress || 0;
            progressElement.textContent = progress + '%';
            
            // Update progress bar if it exists
            const progressBar = cardElement.querySelector('[data-progress-bar]');
            if (progressBar) {
                progressBar.style.width = progress + '%';
            }
        }

        // Update last update info
        const lastUpdateElement = cardElement.querySelector('[data-last-update]');
        if (lastUpdateElement && data.latest_update) {
            const date = new Date(data.latest_update.date);
            const timeAgo = this.getTimeAgo(date);
            lastUpdateElement.textContent = `Last update: ${timeAgo}`;
            lastUpdateElement.title = date.toLocaleString();
        }

        // Update status badge color based on project status
        const statusBadge = cardElement.querySelector('[data-status-badge]');
        if (statusBadge && data.latest_update) {
            const statusMap = {
                'on_track': '#22a06b',      // Green
                'at_risk': '#e2b203',       // Yellow
                'blocked': '#ae2a19'        // Red
            };
            const color = statusMap[data.latest_update.status] || '#8b949e';
            statusBadge.style.borderColor = color;
        }

        // Add notification if status changed
        if (cardElement.getAttribute('data-prev-status') !== data.status) {
            this.showNotification(`Project "${data.name}" status changed to ${data.status}`);
            cardElement.setAttribute('data-prev-status', data.status);
        }
    }

    getTimeAgo(date) {
        const now = new Date();
        const seconds = Math.floor((now - date) / 1000);
        
        if (seconds < 60) return 'Just now';
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
        return `${Math.floor(seconds / 86400)}d ago`;
    }

    showNotification(message) {
        // Create notification element if not exists
        let notificationContainer = document.getElementById('dashboardNotifications');
        if (!notificationContainer) {
            notificationContainer = document.createElement('div');
            notificationContainer.id = 'dashboardNotifications';
            notificationContainer.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                max-width: 400px;
            `;
            document.body.appendChild(notificationContainer);
        }

        // Create notification
        const notification = document.createElement('div');
        notification.style.cssText = `
            background: #0c66e4;
            color: white;
            padding: 12px 16px;
            border-radius: 6px;
            margin-bottom: 10px;
            animation: slideInRight 0.3s ease-out;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        `;
        notification.textContent = message;
        notificationContainer.appendChild(notification);

        // Remove after 5 seconds
        setTimeout(() => {
            notification.style.animation = 'fadeOut 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }

    destroy() {
        // Clear all timers
        Object.keys(this.updateTimers).forEach(projectId => {
            clearInterval(this.updateTimers[projectId]);
        });
        this.updateTimers = {};
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    window.dashboardUpdates = new DashboardUpdates(30000);
});

// Clean up on page unload
window.addEventListener('beforeunload', function() {
    if (window.dashboardUpdates) {
        window.dashboardUpdates.destroy();
    }
});
