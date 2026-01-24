/**
 * Starred Items Module
 * Manages starring/favoriting of issues, projects, and other items
 */

class StarredItems {
    constructor() {
        this.starredCache = new Set();
        this.init();
    }

    async init() {
        await this.loadStarredItems();
        this.setupStarButtons();
        this.addStarredSidebar();
        console.log('StarredItems initialized');
    }

    async loadStarredItems() {
        try {
            const response = await fetch('/api/v1/starred-items');
            const data = await response.json();
            
            if (data.success) {
                this.starredCache.clear();
                data.data.forEach(item => {
                    this.starredCache.add(`${item.type}-${item.item_id}`);
                });
            }
        } catch (error) {
            console.error('Failed to load starred items:', error);
        }
    }

    setupStarButtons() {
        // Add star buttons to existing elements
        this.addStarButtonsToIssues();
        this.addStarButtonsToProjects();
    }

    addStarButtonsToIssues() {
        // Add to issue cards
        document.querySelectorAll('[data-issue-id]').forEach(element => {
            const issueId = element.dataset.issueId;
            const issueTitle = element.dataset.issueTitle || element.querySelector('.issue-title')?.textContent || 'Issue';
            const issueKey = element.dataset.issueKey || '';
            
            if (!element.querySelector('.star-button')) {
                this.addStarButton(element, 'issue', issueId, issueTitle, issueKey);
            }
        });
    }

    addStarButtonsToProjects() {
        // Add to project cards
        document.querySelectorAll('[data-project-id]').forEach(element => {
            const projectId = element.dataset.projectId;
            const projectName = element.dataset.projectName || element.querySelector('.project-name')?.textContent || 'Project';
            const projectKey = element.dataset.projectKey || '';
            
            if (!element.querySelector('.star-button')) {
                this.addStarButton(element, 'project', projectId, projectName, projectKey);
            }
        });
    }

    addStarButton(element, type, itemId, title, key = null) {
        const isStarred = this.starredCache.has(`${type}-${itemId}`);
        
        const button = document.createElement('button');
        button.className = `star-button ${isStarred ? 'starred' : ''}`;
        button.dataset.type = type;
        button.dataset.itemId = itemId;
        button.dataset.title = title;
        button.dataset.key = key || '';
        button.title = isStarred ? 'Remove from starred' : 'Add to starred';
        button.innerHTML = `<i data-lucide="star" class="star-icon"></i>`;
        
        button.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.toggleStar(button, type, itemId, title, key);
        });
        
        // Add to appropriate location
        const header = element.querySelector('.issue-header, .project-header, .card-header');
        if (header) {
            header.appendChild(button);
        } else {
            element.appendChild(button);
        }
        
        // Initialize icon
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }

    async toggleStar(button, type, itemId, title, key) {
        const wasStarred = button.classList.contains('starred');
        
        // Optimistic UI update
        button.classList.toggle('starred');
        button.title = wasStarred ? 'Add to starred' : 'Remove from starred';
        
        try {
            const response = await fetch('/api/v1/starred-items/toggle', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    type: type,
                    item_id: parseInt(itemId),
                    title: title,
                    key: key
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                const cacheKey = `${type}-${itemId}`;
                if (data.starred) {
                    this.starredCache.add(cacheKey);
                    this.showNotification(`Added to starred`, 'success');
                } else {
                    this.starredCache.delete(cacheKey);
                    this.showNotification(`Removed from starred`, 'info');
                }
                
                // Refresh starred sidebar
                this.refreshStarredSidebar();
            } else {
                // Revert on error
                button.classList.toggle('starred');
                button.title = wasStarred ? 'Remove from starred' : 'Add to starred';
                this.showNotification('Failed to update starred status', 'error');
            }
        } catch (error) {
            console.error('Star toggle failed:', error);
            // Revert on error
            button.classList.toggle('starred');
            button.title = wasStarred ? 'Remove from starred' : 'Add to starred';
            this.showNotification('Failed to update starred status', 'error');
        }
    }

    addStarredSidebar() {
        const sidebar = document.querySelector('.sidebar-nav');
        if (!sidebar) return;
        
        // Check if already exists
        if (document.getElementById('starredSection')) return;
        
        // Find "For you" section
        const forYouSection = sidebar.querySelector('.sidebar-section');
        if (!forYouSection) return;
        
        // Add starred link
        const starredLink = document.createElement('a');
        starredLink.href = 'javascript:void(0)';
        starredLink.className = 'sidebar-nav-item';
        starredLink.id = 'starredLink';
        starredLink.innerHTML = `
            <i data-lucide="star" class="nav-icon"></i>
            <span>Starred</span>
            <span class="starred-count ml-auto">0</span>
        `;
        
        starredLink.addEventListener('click', (e) => {
            e.preventDefault();
            this.showStarredDropdown();
        });
        
        // Insert after Recent
        const recentLink = forYouSection.querySelector('[href*="Recent"]') || 
                          forYouSection.querySelector('a[href*="clock"]')?.parentElement;
        if (recentLink) {
            recentLink.insertAdjacentElement('afterend', starredLink);
        } else {
            forYouSection.appendChild(starredLink);
        }
        
        // Initialize icon
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
        
        // Update count
        this.updateStarredCount();
    }

    updateStarredCount() {
        const countBadge = document.querySelector('.starred-count');
        if (countBadge) {
            countBadge.textContent = this.starredCache.size;
        }
    }

    async showStarredDropdown() {
        const existingDropdown = document.getElementById('starredDropdown');
        if (existingDropdown) {
            existingDropdown.remove();
            return;
        }
        
        // Fetch fresh starred items
        try {
            const response = await fetch('/api/v1/starred-items');
            const data = await response.json();
            
            if (data.success) {
                this.displayStarredDropdown(data.data);
            }
        } catch (error) {
            console.error('Failed to fetch starred items:', error);
        }
    }

    displayStarredDropdown(items) {
        const starredLink = document.getElementById('starredLink');
        if (!starredLink) return;
        
        const dropdown = document.createElement('div');
        dropdown.id = 'starredDropdown';
        dropdown.className = 'starred-dropdown';
        dropdown.innerHTML = `
            <div class="starred-dropdown-header">
                <h3>Starred Items</h3>
                <button class="starred-dropdown-close" onclick="this.closest('.starred-dropdown').remove()">
                    <i data-lucide="x"></i>
                </button>
            </div>
            <div class="starred-dropdown-content">
                ${items.length === 0 ? `
                    <div class="starred-dropdown-empty">
                        <i data-lucide="star"></i>
                        <p>No starred items yet</p>
                        <span class="text-sm">Star items for quick access</span>
                    </div>
                ` : this.renderStarredItems(items)}
            </div>
        `;
        
        starredLink.parentElement.appendChild(dropdown);
        
        // Initialize icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
        
        // Close on outside click
        setTimeout(() => {
            document.addEventListener('click', (e) => {
                if (!dropdown.contains(e.target) && !starredLink.contains(e.target)) {
                    dropdown.remove();
                }
            }, { once: true });
        }, 100);
    }

    renderStarredItems(items) {
        // Group by type
        const grouped = items.reduce((acc, item) => {
            if (!acc[item.type]) acc[item.type] = [];
            acc[item.type].push(item);
            return acc;
        }, {});
        
        let html = '';
        
        for (const [type, typeItems] of Object.entries(grouped)) {
            html += `
                <div class="starred-dropdown-section">
                    <div class="starred-dropdown-label">${this.getTypeLabel(type)}</div>
                    ${typeItems.map(item => `
                        <a href="${this.getItemUrl(item)}" class="starred-dropdown-item">
                            <div class="starred-item-icon" data-type="${item.type}">
                                <i data-lucide="${this.getItemIcon(item.type)}"></i>
                            </div>
                            <div class="starred-item-content">
                                <div class="starred-item-title">${item.key ? item.key + ': ' : ''}${item.title}</div>
                                <div class="starred-item-meta">${this.formatDate(item.starred_at)}</div>
                            </div>
                            <button class="starred-item-unstar" onclick="event.preventDefault(); event.stopPropagation(); window.starredItems.toggleStar(this, '${item.type}', '${item.item_id}', '${item.title}', '${item.key || ''}')">
                                <i data-lucide="x"></i>
                            </button>
                        </a>
                    `).join('')}
                </div>
            `;
        }
        
        return html;
    }

    getTypeLabel(type) {
        const labels = {
            'issue': 'Issues',
            'project': 'Projects',
            'board': 'Boards',
            'filter': 'Filters'
        };
        return labels[type] || type;
    }

    getItemUrl(item) {
        const urlMap = {
            'issue': `/issues/${item.item_id}`,
            'project': `/project/${item.item_id}`,
            'board': `/board/${item.item_id}`,
            'filter': `/filters/${item.item_id}`
        };
        return urlMap[item.type] || '#';
    }

    getItemIcon(type) {
        const iconMap = {
            'issue': 'circle-dot',
            'project': 'folder',
            'board': 'kanban',
            'filter': 'filter'
        };
        return iconMap[type] || 'star';
    }

    formatDate(isoString) {
        const date = new Date(isoString);
        const now = new Date();
        const diffDays = Math.floor((now - date) / 86400000);
        
        if (diffDays === 0) return 'Today';
        if (diffDays === 1) return 'Yesterday';
        if (diffDays < 7) return `${diffDays} days ago`;
        return date.toLocaleDateString();
    }

    async refreshStarredSidebar() {
        await this.loadStarredItems();
        this.updateStarredCount();
    }

    showNotification(message, type = 'info') {
        if (window.notificationManager) {
            window.notificationManager.addNotification({
                message: message,
                type: type
            });
        }
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.starredItems = new StarredItems();
    });
} else {
    window.starredItems = new StarredItems();
}
