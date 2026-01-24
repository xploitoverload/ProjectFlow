/**
 * Home & Dashboards System
 * For You page, activity feed, work overview, organization home
 */

class HomeDashboard {
    constructor() {
        this.activities = [
            { type: 'created', issue: 'TEST-142', summary: 'Implement user authentication', author: 'John Doe', timestamp: '2026-01-24 15:30', project: 'TEST' },
            { type: 'commented', issue: 'TEST-141', summary: 'Fix memory leak in cache', author: 'Jane Smith', timestamp: '2026-01-24 14:45', project: 'TEST', comment: 'This should be fixed in the next release' },
            { type: 'updated', issue: 'TEST-140', summary: 'Update dependencies', author: 'Bob Johnson', timestamp: '2026-01-24 13:20', project: 'TEST', field: 'status', oldValue: 'In Progress', newValue: 'In Review' },
            { type: 'transitioned', issue: 'TEST-139', summary: 'Add dark mode support', author: 'Alice Brown', timestamp: '2026-01-24 11:15', project: 'TEST', from: 'To Do', to: 'In Progress' },
            { type: 'created', issue: 'DEV-85', summary: 'Refactor authentication module', author: 'John Doe', timestamp: '2026-01-24 10:00', project: 'DEV' },
            { type: 'commented', issue: 'DEV-84', summary: 'Optimize database queries', author: 'Jane Smith', timestamp: '2026-01-23 16:30', project: 'DEV', comment: 'Great improvements!' },
            { type: 'updated', issue: 'TEST-138', summary: 'Fix responsive layout', author: 'Bob Johnson', timestamp: '2026-01-23 15:45', project: 'TEST', field: 'assignee', oldValue: 'Unassigned', newValue: 'John Doe' },
            { type: 'created', issue: 'TEST-137', summary: 'Add export functionality', author: 'Alice Brown', timestamp: '2026-01-23 14:20', project: 'TEST' }
        ];
        
        this.assignedIssues = [
            { key: 'TEST-142', summary: 'Implement user authentication', priority: 'high', dueDate: '2026-01-28', status: 'In Progress' },
            { key: 'TEST-140', summary: 'Update dependencies', priority: 'medium', dueDate: '2026-01-30', status: 'In Review' },
            { key: 'DEV-85', summary: 'Refactor authentication module', priority: 'high', dueDate: '2026-01-27', status: 'In Progress' },
            { key: 'TEST-135', summary: 'Fix calendar integration', priority: 'low', dueDate: '2026-02-05', status: 'To Do' }
        ];
        
        this.workStats = {
            open: { count: 23, trend: 'up', change: '+3' },
            inProgress: { count: 15, trend: 'down', change: '-2' },
            inReview: { count: 8, trend: 'up', change: '+4' },
            done: { count: 142, trend: 'up', change: '+18' }
        };
        
        this.projects = [
            { id: 1, key: 'TEST', name: 'Test Project', type: 'software', lead: 'John Doe', issuesCount: 142, avatar: 'T' },
            { id: 2, key: 'DEV', name: 'Development', type: 'software', lead: 'Jane Smith', issuesCount: 85, avatar: 'D' },
            { id: 3, key: 'DESK', name: 'Service Desk', type: 'service_desk', lead: 'Bob Johnson', issuesCount: 67, avatar: 'SD' },
            { id: 4, key: 'OPS', name: 'Operations', type: 'ops', lead: 'Alice Brown', issuesCount: 34, avatar: 'O' }
        ];
        
        this.people = [
            { name: 'John Doe', email: 'john@company.com', role: 'Developer', status: 'online', avatar: 'JD' },
            { name: 'Jane Smith', email: 'jane@company.com', role: 'Senior Developer', status: 'online', avatar: 'JS' },
            { name: 'Bob Johnson', email: 'bob@company.com', role: 'Team Lead', status: 'offline', avatar: 'BJ' },
            { name: 'Alice Brown', email: 'alice@company.com', role: 'Developer', status: 'online', avatar: 'AB' },
            { name: 'Charlie Davis', email: 'charlie@company.com', role: 'QA Engineer', status: 'offline', avatar: 'CD' },
            { name: 'Diana Evans', email: 'diana@company.com', role: 'Product Manager', status: 'online', avatar: 'DE' }
        ];
        
        this.currentView = 'for-you'; // 'for-you' or 'organization'
        
        this.init();
    }
    
    init() {
        console.log('Home Dashboard initialized');
    }
    
    renderHomePage(container) {
        container.innerHTML = `
            <div class="home-dashboard">
                <div class="home-header">
                    <div class="view-switcher">
                        <button class="view-btn ${this.currentView === 'for-you' ? 'active' : ''}" onclick="homeDashboard.switchView('for-you')">
                            <i data-lucide="user"></i>
                            For You
                        </button>
                        <button class="view-btn ${this.currentView === 'organization' ? 'active' : ''}" onclick="homeDashboard.switchView('organization')">
                            <i data-lucide="building"></i>
                            Organization
                        </button>
                    </div>
                </div>
                
                ${this.currentView === 'for-you' ? this.renderForYouView() : this.renderOrganizationView()}
            </div>
        `;
        
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }
    
    renderForYouView() {
        return `
            <div class="for-you-view">
                <div class="dashboard-grid">
                    <div class="main-content">
                        ${this.renderWorkOverview()}
                        ${this.renderActivityFeed()}
                    </div>
                    <div class="sidebar-content">
                        ${this.renderAssignedToMe()}
                        ${this.renderQuickActions()}
                    </div>
                </div>
            </div>
        `;
    }
    
    renderWorkOverview() {
        return `
            <div class="work-overview">
                <h3>Your Work Overview</h3>
                <div class="stats-grid">
                    <div class="stat-card stat-open">
                        <div class="stat-icon">
                            <i data-lucide="circle"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-value">${this.workStats.open.count}</div>
                            <div class="stat-label">Open</div>
                            <div class="stat-trend trend-${this.workStats.open.trend}">
                                <i data-lucide="trending-${this.workStats.open.trend}"></i>
                                ${this.workStats.open.change}
                            </div>
                        </div>
                    </div>
                    
                    <div class="stat-card stat-in-progress">
                        <div class="stat-icon">
                            <i data-lucide="loader"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-value">${this.workStats.inProgress.count}</div>
                            <div class="stat-label">In Progress</div>
                            <div class="stat-trend trend-${this.workStats.inProgress.trend}">
                                <i data-lucide="trending-${this.workStats.inProgress.trend}"></i>
                                ${this.workStats.inProgress.change}
                            </div>
                        </div>
                    </div>
                    
                    <div class="stat-card stat-in-review">
                        <div class="stat-icon">
                            <i data-lucide="eye"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-value">${this.workStats.inReview.count}</div>
                            <div class="stat-label">In Review</div>
                            <div class="stat-trend trend-${this.workStats.inReview.trend}">
                                <i data-lucide="trending-${this.workStats.inReview.trend}"></i>
                                ${this.workStats.inReview.change}
                            </div>
                        </div>
                    </div>
                    
                    <div class="stat-card stat-done">
                        <div class="stat-icon">
                            <i data-lucide="check-circle"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-value">${this.workStats.done.count}</div>
                            <div class="stat-label">Done</div>
                            <div class="stat-trend trend-${this.workStats.done.trend}">
                                <i data-lucide="trending-${this.workStats.done.trend}"></i>
                                ${this.workStats.done.change}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    renderActivityFeed() {
        const groupedActivities = this.groupActivitiesByDate();
        
        return `
            <div class="activity-feed">
                <div class="feed-header">
                    <h3>Activity Feed</h3>
                    <button class="btn btn-sm" onclick="homeDashboard.refreshFeed()">
                        <i data-lucide="refresh-cw"></i>
                        Refresh
                    </button>
                </div>
                
                <div class="feed-timeline">
                    ${Object.entries(groupedActivities).map(([date, activities]) => `
                        <div class="feed-day">
                            <div class="feed-date">${date}</div>
                            ${activities.map(activity => this.renderActivityItem(activity)).join('')}
                        </div>
                    `).join('')}
                </div>
                
                <button class="btn btn-secondary load-more" onclick="homeDashboard.loadMoreActivities()">
                    Load More
                </button>
            </div>
        `;
    }
    
    groupActivitiesByDate() {
        const grouped = {};
        
        this.activities.forEach(activity => {
            const date = activity.timestamp.split(' ')[0];
            const displayDate = this.formatDate(date);
            
            if (!grouped[displayDate]) {
                grouped[displayDate] = [];
            }
            grouped[displayDate].push(activity);
        });
        
        return grouped;
    }
    
    formatDate(dateStr) {
        const today = '2026-01-24';
        const yesterday = '2026-01-23';
        
        if (dateStr === today) return 'Today';
        if (dateStr === yesterday) return 'Yesterday';
        return dateStr;
    }
    
    renderActivityItem(activity) {
        const iconMap = {
            created: 'plus-circle',
            commented: 'message-circle',
            updated: 'edit',
            transitioned: 'arrow-right-circle'
        };
        
        return `
            <div class="activity-item">
                <div class="activity-icon activity-${activity.type}">
                    <i data-lucide="${iconMap[activity.type] || 'circle'}"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-header">
                        <strong>${activity.author}</strong>
                        ${this.getActivityDescription(activity)}
                    </div>
                    <div class="activity-issue">
                        <a href="#" onclick="return false">${activity.issue}</a>
                        <span>${activity.summary}</span>
                    </div>
                    ${activity.comment ? `<div class="activity-comment">"${activity.comment}"</div>` : ''}
                    <div class="activity-time">${activity.timestamp}</div>
                </div>
            </div>
        `;
    }
    
    getActivityDescription(activity) {
        switch (activity.type) {
            case 'created':
                return 'created';
            case 'commented':
                return 'commented on';
            case 'updated':
                return `updated <strong>${activity.field}</strong> from <span class="old-value">${activity.oldValue}</span> to <span class="new-value">${activity.newValue}</span> in`;
            case 'transitioned':
                return `moved from <strong>${activity.from}</strong> to <strong>${activity.to}</strong>`;
            default:
                return 'updated';
        }
    }
    
    renderAssignedToMe() {
        return `
            <div class="assigned-widget">
                <div class="widget-header">
                    <h3>Assigned to Me</h3>
                    <a href="#" onclick="return false">View all</a>
                </div>
                <div class="assigned-list">
                    ${this.assignedIssues.map(issue => `
                        <div class="assigned-item">
                            <div class="issue-header">
                                <a href="#" onclick="return false" class="issue-key">${issue.key}</a>
                                <span class="priority-badge priority-${issue.priority}">
                                    <i data-lucide="arrow-${issue.priority === 'high' ? 'up' : issue.priority === 'low' ? 'down' : 'right'}"></i>
                                </span>
                            </div>
                            <div class="issue-summary">${issue.summary}</div>
                            <div class="issue-footer">
                                <span class="issue-status status-${issue.status.toLowerCase().replace(' ', '-')}">${issue.status}</span>
                                <span class="issue-due ${this.isDueSoon(issue.dueDate) ? 'due-soon' : ''}">
                                    <i data-lucide="calendar"></i>
                                    ${issue.dueDate}
                                </span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    isDueSoon(dueDate) {
        // Simple check if due within 3 days
        const date = new Date(dueDate);
        const today = new Date('2026-01-24');
        const diffDays = Math.ceil((date - today) / (1000 * 60 * 60 * 24));
        return diffDays <= 3;
    }
    
    renderQuickActions() {
        return `
            <div class="quick-actions-widget">
                <h3>Quick Actions</h3>
                <div class="actions-list">
                    <button class="action-btn" onclick="alert('Create Issue')">
                        <i data-lucide="plus-circle"></i>
                        <span>Create Issue</span>
                        <kbd>C</kbd>
                    </button>
                    <button class="action-btn" onclick="alert('View Sprint')">
                        <i data-lucide="layout-grid"></i>
                        <span>View Sprint</span>
                        <kbd>S</kbd>
                    </button>
                    <button class="action-btn" onclick="alert('My Filters')">
                        <i data-lucide="filter"></i>
                        <span>My Filters</span>
                        <kbd>F</kbd>
                    </button>
                    <button class="action-btn" onclick="alert('Reports')">
                        <i data-lucide="bar-chart-2"></i>
                        <span>Reports</span>
                        <kbd>R</kbd>
                    </button>
                </div>
            </div>
        `;
    }
    
    renderOrganizationView() {
        return `
            <div class="organization-view">
                <div class="org-overview">
                    <div class="org-header">
                        <h2>Organization Overview</h2>
                        <button class="btn btn-primary" onclick="alert('Create Project')">
                            <i data-lucide="plus"></i>
                            Create Project
                        </button>
                    </div>
                    
                    <div class="org-stats">
                        <div class="org-stat-card">
                            <i data-lucide="folder"></i>
                            <div>
                                <div class="org-stat-value">${this.projects.length}</div>
                                <div class="org-stat-label">Projects</div>
                            </div>
                        </div>
                        <div class="org-stat-card">
                            <i data-lucide="users"></i>
                            <div>
                                <div class="org-stat-value">${this.people.length}</div>
                                <div class="org-stat-label">Team Members</div>
                            </div>
                        </div>
                        <div class="org-stat-card">
                            <i data-lucide="file-text"></i>
                            <div>
                                <div class="org-stat-value">328</div>
                                <div class="org-stat-label">Total Issues</div>
                            </div>
                        </div>
                        <div class="org-stat-card">
                            <i data-lucide="activity"></i>
                            <div>
                                <div class="org-stat-value">89%</div>
                                <div class="org-stat-label">Team Velocity</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                ${this.renderProjectsGrid()}
                ${this.renderPeopleDirectory()}
            </div>
        `;
    }
    
    renderProjectsGrid() {
        return `
            <div class="projects-section">
                <h3>Projects</h3>
                <div class="projects-grid">
                    ${this.projects.map(project => `
                        <div class="project-card">
                            <div class="project-avatar">${project.avatar}</div>
                            <div class="project-info">
                                <h4>${project.name}</h4>
                                <div class="project-key">${project.key}</div>
                                <div class="project-meta">
                                    <span class="project-type">
                                        <i data-lucide="${this.getProjectTypeIcon(project.type)}"></i>
                                        ${project.type.replace('_', ' ')}
                                    </span>
                                    <span class="project-issues">
                                        ${project.issuesCount} issues
                                    </span>
                                </div>
                                <div class="project-lead">
                                    <i data-lucide="user"></i>
                                    ${project.lead}
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    getProjectTypeIcon(type) {
        const icons = {
            software: 'code',
            service_desk: 'headphones',
            ops: 'activity'
        };
        return icons[type] || 'folder';
    }
    
    renderPeopleDirectory() {
        return `
            <div class="people-section">
                <h3>Team Directory</h3>
                <div class="people-grid">
                    ${this.people.map(person => `
                        <div class="person-card">
                            <div class="person-avatar ${person.status === 'online' ? 'online' : ''}">
                                ${person.avatar}
                            </div>
                            <div class="person-info">
                                <h4>${person.name}</h4>
                                <div class="person-role">${person.role}</div>
                                <div class="person-email">${person.email}</div>
                                <div class="person-status status-${person.status}">
                                    <span class="status-dot"></span>
                                    ${person.status}
                                </div>
                            </div>
                            <div class="person-actions">
                                <button class="btn-icon" title="Message">
                                    <i data-lucide="message-circle"></i>
                                </button>
                                <button class="btn-icon" title="View Profile">
                                    <i data-lucide="user"></i>
                                </button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    switchView(view) {
        this.currentView = view;
        const container = document.querySelector('.home-dashboard').parentElement;
        this.renderHomePage(container);
    }
    
    refreshFeed() {
        const container = document.querySelector('.home-dashboard').parentElement;
        this.renderHomePage(container);
        this.showToast('Feed refreshed');
    }
    
    loadMoreActivities() {
        this.showToast('Loading more activities...');
    }
    
    showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;
        toast.style.cssText = 'position: fixed; bottom: 20px; right: 20px; background: #36b37e; color: white; padding: 12px 20px; border-radius: 6px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); z-index: 10000;';
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }
}

// Initialize
const homeDashboard = new HomeDashboard();
