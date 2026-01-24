/**
 * Integrations & Apps System
 * GitHub/GitLab, Slack, Teams, Webhooks, API tokens, OAuth, Marketplace
 */

class IntegrationsAppsSystem {
    constructor() {
        this.integrations = [
            { id: 'github', name: 'GitHub', icon: 'github', status: 'connected', description: 'Link commits and pull requests', configured: true },
            { id: 'gitlab', name: 'GitLab', icon: 'gitlab', status: 'disconnected', description: 'Track GitLab activities', configured: false },
            { id: 'slack', name: 'Slack', icon: 'message-square', status: 'connected', description: 'Send notifications to Slack', configured: true },
            { id: 'teams', name: 'Microsoft Teams', icon: 'users', status: 'disconnected', description: 'Integrate with Teams', configured: false }
        ];
        
        this.webhooks = [
            { id: 'wh1', name: 'Issue Created Webhook', url: 'https://api.example.com/webhook', events: ['issue_created'], enabled: true },
            { id: 'wh2', name: 'Status Changed', url: 'https://hooks.example.com/status', events: ['issue_updated'], enabled: true }
        ];
        
        this.apiTokens = [
            { id: 'at1', name: 'CI/CD Pipeline', token: 'eyJ0eXAi...', created: '2024-01-15', lastUsed: '1 hour ago', scopes: ['read:issues', 'write:issues'] },
            { id: 'at2', name: 'Analytics Service', token: 'eyJ0eXQi...', created: '2024-01-10', lastUsed: '3 days ago', scopes: ['read:projects'] }
        ];
        
        this.oauthApps = [
            { id: 'oa1', name: 'Custom Analytics Dashboard', clientId: 'abc123', redirectUri: 'https://analytics.example.com/callback', scopes: ['read:projects', 'read:issues'] }
        ];
        
        this.marketplaceApps = [
            { id: 'ma1', name: 'Time Tracking Pro', vendor: 'TimeTracker Inc', rating: 4.5, installs: 12500, category: 'Time Tracking' },
            { id: 'ma2', name: 'Advanced Reports', vendor: 'ReportLab', rating: 4.8, installs: 8300, category: 'Reports' },
            { id: 'ma3', name: 'Gantt Chart Plus', vendor: 'ChartSoft', rating: 4.3, installs: 5600, category: 'Planning' }
        ];
        
        this.activeTab = 'integrations';
        
        this.init();
    }
    
    init() {
        console.log('Integrations & Apps System initialized');
    }
    
    render(container) {
        container.innerHTML = `
            <div class="integrations-container">
                ${this.renderHeader()}
                ${this.renderTabs()}
                ${this.renderContent()}
            </div>
        `;
        
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }
    
    renderHeader() {
        return `
            <div class="integrations-header">
                <h2>Integrations & Apps</h2>
                <div class="header-actions">
                    ${this.activeTab === 'webhooks' ? `
                        <button class="btn btn-primary" onclick="integrationsSystem.createWebhook()">
                            <i data-lucide="plus"></i>
                            Create Webhook
                        </button>
                    ` : this.activeTab === 'api-tokens' ? `
                        <button class="btn btn-primary" onclick="integrationsSystem.generateToken()">
                            <i data-lucide="key"></i>
                            Generate Token
                        </button>
                    ` : this.activeTab === 'oauth' ? `
                        <button class="btn btn-primary" onclick="integrationsSystem.registerOAuthApp()">
                            <i data-lucide="shield"></i>
                            Register App
                        </button>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    renderTabs() {
        return `
            <div class="integrations-tabs">
                <button class="tab ${this.activeTab === 'integrations' ? 'active' : ''}" 
                    onclick="integrationsSystem.switchTab('integrations')">
                    <i data-lucide="plug"></i>
                    Integrations
                </button>
                <button class="tab ${this.activeTab === 'webhooks' ? 'active' : ''}" 
                    onclick="integrationsSystem.switchTab('webhooks')">
                    <i data-lucide="webhook"></i>
                    Webhooks
                </button>
                <button class="tab ${this.activeTab === 'api-tokens' ? 'active' : ''}" 
                    onclick="integrationsSystem.switchTab('api-tokens')">
                    <i data-lucide="key"></i>
                    API Tokens
                </button>
                <button class="tab ${this.activeTab === 'oauth' ? 'active' : ''}" 
                    onclick="integrationsSystem.switchTab('oauth')">
                    <i data-lucide="shield-check"></i>
                    OAuth Apps
                </button>
                <button class="tab ${this.activeTab === 'marketplace' ? 'active' : ''}" 
                    onclick="integrationsSystem.switchTab('marketplace')">
                    <i data-lucide="shopping-cart"></i>
                    Marketplace
                </button>
                <button class="tab ${this.activeTab === 'status' ? 'active' : ''}" 
                    onclick="integrationsSystem.switchTab('status')">
                    <i data-lucide="activity"></i>
                    Status Monitor
                </button>
            </div>
        `;
    }
    
    renderContent() {
        switch(this.activeTab) {
            case 'integrations':
                return this.renderIntegrations();
            case 'webhooks':
                return this.renderWebhooks();
            case 'api-tokens':
                return this.renderAPITokens();
            case 'oauth':
                return this.renderOAuthApps();
            case 'marketplace':
                return this.renderMarketplace();
            case 'status':
                return this.renderStatusMonitor();
            default:
                return '';
        }
    }
    
    renderIntegrations() {
        return `
            <div class="integrations-content">
                <div class="integrations-grid">
                    ${this.integrations.map(int => `
                        <div class="integration-card ${int.status}">
                            <div class="integration-header">
                                <div class="integration-icon">
                                    <i data-lucide="${int.icon}"></i>
                                </div>
                                <span class="status-indicator status-${int.status}">${int.status}</span>
                            </div>
                            <h3>${int.name}</h3>
                            <p>${int.description}</p>
                            <div class="integration-actions">
                                ${int.configured ? `
                                    <button class="btn btn-secondary-sm" onclick="integrationsSystem.configureIntegration('${int.id}')">
                                        <i data-lucide="settings"></i>
                                        Configure
                                    </button>
                                    <button class="btn btn-link-sm" onclick="integrationsSystem.disconnectIntegration('${int.id}')">
                                        Disconnect
                                    </button>
                                ` : `
                                    <button class="btn btn-primary-sm" onclick="integrationsSystem.connectIntegration('${int.id}')">
                                        <i data-lucide="plus"></i>
                                        Connect
                                    </button>
                                `}
                            </div>
                        </div>
                    `).join('')}
                </div>
                
                <div class="integration-details" id="integrationDetails"></div>
            </div>
        `;
    }
    
    renderWebhooks() {
        return `
            <div class="integrations-content">
                <div class="webhooks-list">
                    ${this.webhooks.map(webhook => `
                        <div class="webhook-card">
                            <div class="webhook-header">
                                <div class="webhook-info">
                                    <h3>${webhook.name}</h3>
                                    <code class="webhook-url">${webhook.url}</code>
                                </div>
                                <label class="toggle-switch">
                                    <input type="checkbox" ${webhook.enabled ? 'checked' : ''} 
                                        onchange="integrationsSystem.toggleWebhook('${webhook.id}', this.checked)" />
                                    <span class="toggle-slider"></span>
                                </label>
                            </div>
                            <div class="webhook-events">
                                ${webhook.events.map(event => `
                                    <span class="event-chip">${event}</span>
                                `).join('')}
                            </div>
                            <div class="webhook-actions">
                                <button class="btn btn-link-sm" onclick="integrationsSystem.testWebhook('${webhook.id}')">
                                    <i data-lucide="send"></i>
                                    Test
                                </button>
                                <button class="btn btn-link-sm" onclick="integrationsSystem.editWebhook('${webhook.id}')">
                                    <i data-lucide="edit-2"></i>
                                    Edit
                                </button>
                                <button class="btn btn-link-sm" onclick="integrationsSystem.deleteWebhook('${webhook.id}')">
                                    <i data-lucide="trash-2"></i>
                                    Delete
                                </button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    renderAPITokens() {
        return `
            <div class="integrations-content">
                <div class="tokens-list">
                    ${this.apiTokens.map(token => `
                        <div class="token-card">
                            <div class="token-header">
                                <h3>${token.name}</h3>
                                <button class="btn-icon-sm" onclick="integrationsSystem.revokeToken('${token.id}')">
                                    <i data-lucide="trash-2"></i>
                                </button>
                            </div>
                            <div class="token-value">
                                <code>${token.token}...</code>
                                <button class="btn-icon-sm" onclick="integrationsSystem.copyToken('${token.token}')">
                                    <i data-lucide="copy"></i>
                                </button>
                            </div>
                            <div class="token-meta">
                                <span>Created: ${token.created}</span>
                                <span>Last used: ${token.lastUsed}</span>
                            </div>
                            <div class="token-scopes">
                                ${token.scopes.map(scope => `
                                    <span class="scope-chip">${scope}</span>
                                `).join('')}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    renderOAuthApps() {
        return `
            <div class="integrations-content">
                <div class="oauth-apps-list">
                    ${this.oauthApps.map(app => `
                        <div class="oauth-app-card">
                            <div class="app-header">
                                <h3>${app.name}</h3>
                                <button class="btn-icon-sm" onclick="integrationsSystem.editOAuthApp('${app.id}')">
                                    <i data-lucide="edit-2"></i>
                                </button>
                            </div>
                            <div class="app-details">
                                <div class="detail-row">
                                    <span class="detail-label">Client ID:</span>
                                    <code>${app.clientId}</code>
                                    <button class="btn-icon-sm" onclick="integrationsSystem.copyClientId('${app.clientId}')">
                                        <i data-lucide="copy"></i>
                                    </button>
                                </div>
                                <div class="detail-row">
                                    <span class="detail-label">Redirect URI:</span>
                                    <span>${app.redirectUri}</span>
                                </div>
                            </div>
                            <div class="app-scopes">
                                ${app.scopes.map(scope => `
                                    <span class="scope-chip">${scope}</span>
                                `).join('')}
                            </div>
                            <button class="btn btn-link" onclick="integrationsSystem.regenerateClientSecret('${app.id}')">
                                Regenerate Client Secret
                            </button>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    renderMarketplace() {
        return `
            <div class="integrations-content">
                <div class="marketplace-header">
                    <div class="search-bar">
                        <i data-lucide="search"></i>
                        <input type="text" placeholder="Search apps..." />
                    </div>
                    <select class="category-filter">
                        <option>All Categories</option>
                        <option>Time Tracking</option>
                        <option>Reports</option>
                        <option>Planning</option>
                        <option>Automation</option>
                    </select>
                </div>
                
                <div class="marketplace-apps">
                    ${this.marketplaceApps.map(app => `
                        <div class="marketplace-app-card">
                            <div class="app-icon">
                                <i data-lucide="package"></i>
                            </div>
                            <div class="app-info">
                                <h3>${app.name}</h3>
                                <p class="app-vendor">by ${app.vendor}</p>
                                <div class="app-rating">
                                    ${'★'.repeat(Math.floor(app.rating))}${'☆'.repeat(5 - Math.floor(app.rating))}
                                    <span>${app.rating}</span>
                                </div>
                                <p class="app-installs">${app.installs.toLocaleString()} installs</p>
                                <span class="app-category">${app.category}</span>
                            </div>
                            <button class="btn btn-primary-sm" onclick="integrationsSystem.installApp('${app.id}')">
                                Install
                            </button>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    renderStatusMonitor() {
        const statuses = [
            { integration: 'GitHub', status: 'operational', latency: '45ms', uptime: '99.9%' },
            { integration: 'Slack', status: 'operational', latency: '32ms', uptime: '99.8%' },
            { integration: 'Webhooks', status: 'degraded', latency: '145ms', uptime: '98.5%' },
            { integration: 'API', status: 'operational', latency: '28ms', uptime: '99.9%' }
        ];
        
        return `
            <div class="integrations-content">
                <div class="status-monitor">
                    <h3>Integration Status</h3>
                    <div class="status-list">
                        ${statuses.map(s => `
                            <div class="status-item">
                                <div class="status-name">
                                    <div class="status-dot status-${s.status}"></div>
                                    <span>${s.integration}</span>
                                </div>
                                <div class="status-metrics">
                                    <span class="metric">Latency: ${s.latency}</span>
                                    <span class="metric">Uptime: ${s.uptime}</span>
                                </div>
                                <span class="status-label status-${s.status}">${s.status}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }
    
    // Methods
    switchTab(tab) {
        this.activeTab = tab;
        const container = document.querySelector('.integrations-container').parentElement;
        this.render(container);
    }
    
    connectIntegration(intId) {
        const int = this.integrations.find(i => i.id === intId);
        if (int) {
            this.showToast(`Connecting to ${int.name}...`);
            // Show OAuth flow or configuration modal
        }
    }
    
    configureIntegration(intId) {
        const int = this.integrations.find(i => i.id === intId);
        if (intId === 'github') {
            this.showGitHubConfig();
        } else if (intId === 'slack') {
            this.showSlackConfig();
        }
    }
    
    showGitHubConfig() {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h3>GitHub Configuration</h3>
                    <button class="btn-icon" onclick="this.closest('.modal-overlay').remove()">
                        <i data-lucide="x"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label>GitHub Organization/User</label>
                        <input type="text" placeholder="organization-name" />
                    </div>
                    <div class="form-group">
                        <label>Repositories</label>
                        <select multiple>
                            <option>repo-1</option>
                            <option>repo-2</option>
                            <option>repo-3</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Events to track</label>
                        <label><input type="checkbox" checked /> Commits</label>
                        <label><input type="checkbox" checked /> Pull Requests</label>
                        <label><input type="checkbox" /> Issues</label>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                    <button class="btn btn-primary" onclick="this.closest('.modal-overlay').remove()">Save</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        if (typeof lucide !== 'undefined') lucide.createIcons();
    }
    
    showSlackConfig() {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h3>Slack Configuration</h3>
                    <button class="btn-icon" onclick="this.closest('.modal-overlay').remove()">
                        <i data-lucide="x"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label>Slack Workspace</label>
                        <input type="text" value="myworkspace.slack.com" readonly />
                    </div>
                    <div class="form-group">
                        <label>Default Channel</label>
                        <select>
                            <option>#general</option>
                            <option>#development</option>
                            <option>#alerts</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Notification Events</label>
                        <label><input type="checkbox" checked /> Issue Created</label>
                        <label><input type="checkbox" checked /> Issue Updated</label>
                        <label><input type="checkbox" /> Comment Added</label>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                    <button class="btn btn-primary" onclick="this.closest('.modal-overlay').remove()">Save</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        if (typeof lucide !== 'undefined') lucide.createIcons();
    }
    
    createWebhook() {
        this.showToast('Create webhook dialog');
    }
    
    generateToken() {
        this.showToast('Generate API token');
    }
    
    copyToken(token) {
        navigator.clipboard.writeText(token);
        this.showToast('Token copied to clipboard');
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
const integrationsSystem = new IntegrationsAppsSystem();
