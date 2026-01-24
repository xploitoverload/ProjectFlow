/**
 * Service Desk - Complete Queue System
 * Queues, Triaging, Customer portal, Request types, Knowledge base, SLA, CSAT
 */

class ServiceDeskSystem {
    constructor() {
        this.queues = [
            { id: 'q1', name: 'All Open', count: 45, filters: 'status != Done' },
            { id: 'q2', name: 'Unassigned', count: 12, filters: 'assignee is EMPTY' },
            { id: 'q3', name: 'High Priority', count: 8, filters: 'priority = High OR priority = Critical' },
            { id: 'q4', name: 'SLA Breached', count: 5, filters: 'sla = breached' },
            { id: 'q5', name: 'Pending Customer', count: 15, filters: 'status = "Waiting for Customer"' }
        ];
        
        this.requestTypes = [
            { id: 'rt1', name: 'Get IT Help', description: 'Report technical issues', icon: 'laptop', fields: ['summary', 'description', 'priority', 'affected-users'] },
            { id: 'rt2', name: 'Request Access', description: 'Request system access', icon: 'key', fields: ['summary', 'system-name', 'access-level', 'business-justification'] },
            { id: 'rt3', name: 'Report Bug', description: 'Report software bugs', icon: 'bug', fields: ['summary', 'description', 'severity', 'steps-to-reproduce', 'attachments'] }
        ];
        
        this.organizations = [
            { id: 'org1', name: 'Acme Corp', contacts: 25, openRequests: 12 },
            { id: 'org2', name: 'TechStart Inc', contacts: 15, openRequests: 8 },
            { id: 'org3', name: 'Global Solutions', contacts: 40, openRequests: 20 }
        ];
        
        this.slaMetrics = [
            { name: 'Time to First Response', target: '4h', current: '3h 25m', status: 'met', percentage: 85 },
            { name: 'Time to Resolution', target: '24h', current: '18h 30m', status: 'met', percentage: 77 },
            { name: 'Customer Satisfaction', target: '4.5', current: '4.2', status: 'warning', percentage: 93 }
        ];
        
        this.activeView = 'queues';
        this.selectedQueue = null;
        
        this.init();
    }
    
    init() {
        console.log('Service Desk System initialized');
    }
    
    render(container) {
        container.innerHTML = `
            <div class="service-desk-container">
                ${this.renderHeader()}
                ${this.renderNavigation()}
                ${this.renderContent()}
            </div>
        `;
        
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }
    
    renderHeader() {
        return `
            <div class="service-desk-header">
                <div class="header-left">
                    <h2>Service Desk</h2>
                    <div class="project-selector">
                        <button class="btn btn-secondary dropdown-trigger">
                            <i data-lucide="briefcase"></i>
                            Support Portal (SUP)
                            <i data-lucide="chevron-down"></i>
                        </button>
                    </div>
                </div>
                <div class="header-right">
                    <button class="btn btn-secondary" onclick="serviceDeskSystem.openSettings()">
                        <i data-lucide="settings"></i>
                        Settings
                    </button>
                    <button class="btn btn-primary" onclick="serviceDeskSystem.createRequest()">
                        <i data-lucide="plus"></i>
                        Create Request
                    </button>
                </div>
            </div>
        `;
    }
    
    renderNavigation() {
        return `
            <nav class="service-desk-nav">
                <button class="nav-item ${this.activeView === 'queues' ? 'active' : ''}" 
                    onclick="serviceDeskSystem.switchView('queues')">
                    <i data-lucide="inbox"></i>
                    Queues
                </button>
                <button class="nav-item ${this.activeView === 'portal' ? 'active' : ''}" 
                    onclick="serviceDeskSystem.switchView('portal')">
                    <i data-lucide="globe"></i>
                    Customer Portal
                </button>
                <button class="nav-item ${this.activeView === 'customers' ? 'active' : ''}" 
                    onclick="serviceDeskSystem.switchView('customers')">
                    <i data-lucide="users"></i>
                    Customers
                </button>
                <button class="nav-item ${this.activeView === 'knowledge' ? 'active' : ''}" 
                    onclick="serviceDeskSystem.switchView('knowledge')">
                    <i data-lucide="book"></i>
                    Knowledge Base
                </button>
                <button class="nav-item ${this.activeView === 'sla' ? 'active' : ''}" 
                    onclick="serviceDeskSystem.switchView('sla')">
                    <i data-lucide="clock"></i>
                    SLA
                </button>
                <button class="nav-item ${this.activeView === 'reports' ? 'active' : ''}" 
                    onclick="serviceDeskSystem.switchView('reports')">
                    <i data-lucide="bar-chart"></i>
                    Reports
                </button>
            </nav>
        `;
    }
    
    renderContent() {
        switch(this.activeView) {
            case 'queues':
                return this.renderQueuesView();
            case 'portal':
                return this.renderPortalView();
            case 'customers':
                return this.renderCustomersView();
            case 'knowledge':
                return this.renderKnowledgeBaseView();
            case 'sla':
                return this.renderSLAView();
            case 'reports':
                return this.renderReportsView();
            default:
                return '';
        }
    }
    
    renderQueuesView() {
        return `
            <div class="queues-view">
                <div class="queues-sidebar">
                    <div class="queues-list">
                        <h4>My Queues</h4>
                        ${this.queues.map(queue => `
                            <div class="queue-item ${this.selectedQueue === queue.id ? 'active' : ''}" 
                                onclick="serviceDeskSystem.selectQueue('${queue.id}')">
                                <span class="queue-name">${queue.name}</span>
                                <span class="queue-count">${queue.count}</span>
                            </div>
                        `).join('')}
                        <button class="btn btn-link" onclick="serviceDeskSystem.createQueue()">
                            <i data-lucide="plus"></i>
                            Create Queue
                        </button>
                    </div>
                </div>
                
                <div class="queue-content">
                    ${this.renderQueueIssues()}
                </div>
            </div>
        `;
    }
    
    renderQueueIssues() {
        return `
            <div class="queue-issues">
                <div class="queue-toolbar">
                    <div class="toolbar-left">
                        <h3>${this.queues[0].name}</h3>
                        <span class="issue-count">${this.queues[0].count} issues</span>
                    </div>
                    <div class="toolbar-right">
                        <button class="btn btn-secondary" onclick="serviceDeskSystem.bulkTriage()">
                            <i data-lucide="layers"></i>
                            Bulk Actions
                        </button>
                        <button class="btn btn-secondary" onclick="serviceDeskSystem.exportQueue()">
                            <i data-lucide="download"></i>
                            Export
                        </button>
                    </div>
                </div>
                
                <div class="issues-list">
                    ${this.renderTriagingIssues()}
                </div>
            </div>
        `;
    }
    
    renderTriagingIssues() {
        const issues = [
            { key: 'SUP-245', summary: 'Cannot login to system', customer: 'John Customer', sla: 'breached', priority: 'High', created: '2h ago' },
            { key: 'SUP-244', summary: 'Need access to CRM', customer: 'Jane User', sla: 'warning', priority: 'Medium', created: '4h ago' },
            { key: 'SUP-243', summary: 'Software installation request', customer: 'Bob Client', sla: 'ok', priority: 'Low', created: '1d ago' }
        ];
        
        return issues.map(issue => `
            <div class="triage-issue">
                <div class="issue-checkbox">
                    <input type="checkbox" />
                </div>
                <div class="issue-main">
                    <div class="issue-header">
                        <a href="#" class="issue-key">${issue.key}</a>
                        <span class="sla-indicator sla-${issue.sla}" title="SLA Status">
                            <i data-lucide="clock"></i>
                        </span>
                    </div>
                    <div class="issue-summary">${issue.summary}</div>
                    <div class="issue-meta">
                        <span class="customer-name">
                            <i data-lucide="user"></i>
                            ${issue.customer}
                        </span>
                        <span class="priority-badge priority-${issue.priority.toLowerCase()}">${issue.priority}</span>
                        <span class="created-time">${issue.created}</span>
                    </div>
                </div>
                <div class="issue-actions">
                    <button class="btn btn-sm btn-secondary" onclick="serviceDeskSystem.assignToMe('${issue.key}')">
                        Assign to me
                    </button>
                    <button class="btn-icon" onclick="serviceDeskSystem.triageMenu('${issue.key}', this)">
                        <i data-lucide="more-horizontal"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }
    
    renderPortalView() {
        return `
            <div class="portal-view">
                <div class="portal-preview">
                    <div class="preview-header">
                        <h3>Customer Portal Preview</h3>
                        <button class="btn btn-secondary" onclick="serviceDeskSystem.customizePortal()">
                            <i data-lucide="palette"></i>
                            Customize Theme
                        </button>
                    </div>
                    
                    <div class="portal-mockup">
                        <div class="portal-header-mockup">
                            <h2>Support Portal</h2>
                            <div class="portal-search">
                                <i data-lucide="search"></i>
                                <input type="text" placeholder="How can we help you?" />
                            </div>
                        </div>
                        
                        <div class="request-types-grid">
                            ${this.requestTypes.map(rt => `
                                <div class="request-type-card">
                                    <div class="rt-icon">
                                        <i data-lucide="${rt.icon}"></i>
                                    </div>
                                    <h4>${rt.name}</h4>
                                    <p>${rt.description}</p>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
                
                <div class="portal-config">
                    <h4>Request Types</h4>
                    ${this.requestTypes.map(rt => `
                        <div class="request-type-item">
                            <div class="rt-info">
                                <i data-lucide="${rt.icon}"></i>
                                <span>${rt.name}</span>
                            </div>
                            <button class="btn-icon-sm" onclick="serviceDeskSystem.editRequestType('${rt.id}')">
                                <i data-lucide="edit-2"></i>
                            </button>
                        </div>
                    `).join('')}
                    <button class="btn btn-link" onclick="serviceDeskSystem.createRequestType()">
                        <i data-lucide="plus"></i>
                        Add Request Type
                    </button>
                </div>
            </div>
        `;
    }
    
    renderCustomersView() {
        return `
            <div class="customers-view">
                <div class="customers-toolbar">
                    <div class="search-bar">
                        <i data-lucide="search"></i>
                        <input type="text" placeholder="Search customers..." />
                    </div>
                    <button class="btn btn-secondary" onclick="serviceDeskSystem.importCustomers()">
                        <i data-lucide="upload"></i>
                        Import
                    </button>
                    <button class="btn btn-primary" onclick="serviceDeskSystem.addCustomer()">
                        <i data-lucide="user-plus"></i>
                        Add Customer
                    </button>
                </div>
                
                <div class="organizations-list">
                    <h3>Organizations</h3>
                    ${this.organizations.map(org => `
                        <div class="organization-card">
                            <div class="org-header">
                                <h4>${org.name}</h4>
                                <button class="btn-icon-sm" onclick="serviceDeskSystem.orgMenu('${org.id}', this)">
                                    <i data-lucide="more-horizontal"></i>
                                </button>
                            </div>
                            <div class="org-stats">
                                <span><i data-lucide="users"></i> ${org.contacts} contacts</span>
                                <span><i data-lucide="inbox"></i> ${org.openRequests} open requests</span>
                            </div>
                            <button class="btn btn-link" onclick="serviceDeskSystem.viewOrganization('${org.id}')">
                                View details
                            </button>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    renderKnowledgeBaseView() {
        return `
            <div class="knowledge-base-view">
                <div class="kb-toolbar">
                    <div class="search-bar">
                        <i data-lucide="search"></i>
                        <input type="text" placeholder="Search articles..." />
                    </div>
                    <button class="btn btn-primary" onclick="serviceDeskSystem.createArticle()">
                        <i data-lucide="plus"></i>
                        Create Article
                    </button>
                </div>
                
                <div class="kb-content">
                    <div class="kb-categories">
                        <h4>Categories</h4>
                        <div class="category-list">
                            <div class="category-item">
                                <i data-lucide="folder"></i>
                                <span>Getting Started</span>
                                <span class="article-count">12</span>
                            </div>
                            <div class="category-item">
                                <i data-lucide="folder"></i>
                                <span>Troubleshooting</span>
                                <span class="article-count">25</span>
                            </div>
                            <div class="category-item">
                                <i data-lucide="folder"></i>
                                <span>How-To Guides</span>
                                <span class="article-count">18</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="kb-articles">
                        <h3>Popular Articles</h3>
                        <div class="articles-list">
                            <div class="article-item">
                                <h4>How to reset your password</h4>
                                <p>Step-by-step guide to reset your account password...</p>
                                <div class="article-meta">
                                    <span>👍 125 helpful</span>
                                    <span>Updated 2 days ago</span>
                                </div>
                            </div>
                            <div class="article-item">
                                <h4>Setting up two-factor authentication</h4>
                                <p>Secure your account with 2FA...</p>
                                <div class="article-meta">
                                    <span>👍 98 helpful</span>
                                    <span>Updated 1 week ago</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    renderSLAView() {
        return `
            <div class="sla-view">
                <div class="sla-metrics">
                    <h3>SLA Performance</h3>
                    <div class="metrics-grid">
                        ${this.slaMetrics.map(metric => `
                            <div class="metric-card metric-${metric.status}">
                                <h4>${metric.name}</h4>
                                <div class="metric-value">
                                    <span class="current">${metric.current}</span>
                                    <span class="target">Target: ${metric.target}</span>
                                </div>
                                <div class="metric-progress">
                                    <div class="progress-bar">
                                        <div class="progress-fill" style="width: ${metric.percentage}%"></div>
                                    </div>
                                    <span class="percentage">${metric.percentage}%</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                <div class="sla-config">
                    <h3>SLA Policies</h3>
                    <button class="btn btn-primary" onclick="serviceDeskSystem.createSLAPolicy()">
                        <i data-lucide="plus"></i>
                        Add Policy
                    </button>
                </div>
            </div>
        `;
    }
    
    renderReportsView() {
        return `
            <div class="service-reports-view">
                <h3>Customer Satisfaction</h3>
                <div class="csat-summary">
                    <div class="csat-score">
                        <div class="score-value">4.2</div>
                        <div class="score-label">Average Rating</div>
                        <div class="score-responses">Based on 156 responses</div>
                    </div>
                    <div class="csat-chart">
                        <!-- CSAT visualization would go here -->
                    </div>
                </div>
            </div>
        `;
    }
    
    // Methods
    switchView(view) {
        this.activeView = view;
        const container = document.querySelector('.service-desk-container').parentElement;
        this.render(container);
    }
    
    selectQueue(queueId) {
        this.selectedQueue = queueId;
        const container = document.querySelector('.service-desk-container').parentElement;
        this.render(container);
    }
    
    createRequest() {
        this.showToast('Create request dialog');
    }
    
    bulkTriage() {
        this.showToast('Bulk triage actions');
    }
    
    customizePortal() {
        this.showToast('Portal theme customization');
    }
    
    showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;
        toast.style.cssText = 'position: fixed; bottom: 20px; right: 20px; background: #36b37e; color: white; padding: 12px 20px; border-radius: 6px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); z-index: 10000;';
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 2000);
    }
}

// Initialize
const serviceDeskSystem = new ServiceDeskSystem();
