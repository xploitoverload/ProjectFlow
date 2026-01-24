/**
 * Settings System
 * Project settings and Personal settings with auto-save
 */

class SettingsSystem {
    constructor() {
        this.currentSettingsType = 'project'; // 'project' or 'personal'
        this.currentProjectTab = 'details';
        this.currentPersonalTab = 'profile';
        
        // Mock project data
        this.projectSettings = {
            details: {
                name: 'Test Project',
                key: 'TEST',
                description: 'A software development project for testing',
                avatar: null,
                projectType: 'software',
                lead: 'John Doe'
            },
            access: {
                users: [
                    { name: 'John Doe', email: 'john@company.com', role: 'admin' },
                    { name: 'Jane Smith', email: 'jane@company.com', role: 'member' },
                    { name: 'Bob Johnson', email: 'bob@company.com', role: 'viewer' }
                ]
            },
            issueTypes: [
                { id: 1, name: 'Story', icon: 'book-open', description: 'User story', workflow: 'Default' },
                { id: 2, name: 'Task', icon: 'check-square', description: 'Task to be done', workflow: 'Default' },
                { id: 3, name: 'Bug', icon: 'bug', description: 'Bug report', workflow: 'Bug Workflow' },
                { id: 4, name: 'Epic', icon: 'layers', description: 'Large body of work', workflow: 'Default' }
            ],
            workflows: [
                { id: 1, name: 'Default', states: ['To Do', 'In Progress', 'In Review', 'Done'] },
                { id: 2, name: 'Bug Workflow', states: ['New', 'Investigating', 'In Progress', 'Testing', 'Resolved', 'Closed'] }
            ],
            screens: [
                { id: 1, name: 'Default Screen', fields: ['summary', 'description', 'assignee', 'priority', 'labels'] }
            ],
            customFields: [
                { id: 1, name: 'Story Points', type: 'number', required: false },
                { id: 2, name: 'Sprint', type: 'select', required: false },
                { id: 3, name: 'Epic Link', type: 'epic-link', required: false }
            ],
            permissions: {
                'Browse Projects': { admin: true, member: true, viewer: true },
                'Create Issues': { admin: true, member: true, viewer: false },
                'Edit Issues': { admin: true, member: true, viewer: false },
                'Delete Issues': { admin: true, member: false, viewer: false },
                'Assign Issues': { admin: true, member: true, viewer: false },
                'Manage Sprints': { admin: true, member: false, viewer: false },
                'Administer Project': { admin: true, member: false, viewer: false }
            }
        };
        
        // Mock personal settings
        this.personalSettings = {
            profile: {
                displayName: 'John Doe',
                email: 'john@company.com',
                bio: 'Senior Software Engineer',
                timezone: 'America/New_York',
                avatar: null
            },
            email: {
                frequency: 'instant',
                preferences: {
                    issueUpdates: true,
                    mentions: true,
                    comments: true,
                    assignments: true
                }
            },
            notifications: {
                inApp: true,
                desktop: true,
                sound: false,
                dndStart: '22:00',
                dndEnd: '08:00'
            },
            shortcuts: [
                { action: 'Create Issue', key: 'C', description: 'Open create issue dialog' },
                { action: 'Search', key: '/', description: 'Focus search bar' },
                { action: 'Quick Filters', key: 'F', description: 'Open filters menu' },
                { action: 'Help', key: '?', description: 'Show keyboard shortcuts' }
            ],
            theme: 'auto' // 'light', 'dark', 'auto'
        };
        
        this.init();
    }
    
    init() {
        console.log('Settings System initialized');
    }
    
    renderSettingsPage(container) {
        container.innerHTML = `
            <div class="settings-container">
                <div class="settings-header">
                    <h2>Settings</h2>
                    <div class="settings-type-switcher">
                        <button class="type-btn ${this.currentSettingsType === 'project' ? 'active' : ''}" onclick="settingsSystem.switchSettingsType('project')">
                            <i data-lucide="folder"></i>
                            Project Settings
                        </button>
                        <button class="type-btn ${this.currentSettingsType === 'personal' ? 'active' : ''}" onclick="settingsSystem.switchSettingsType('personal')">
                            <i data-lucide="user"></i>
                            Personal Settings
                        </button>
                    </div>
                </div>
                
                ${this.currentSettingsType === 'project' ? this.renderProjectSettings() : this.renderPersonalSettings()}
            </div>
        `;
        
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }
    
    renderProjectSettings() {
        return `
            <div class="settings-layout">
                <div class="settings-sidebar">
                    <div class="settings-nav">
                        ${this.renderProjectTabs()}
                    </div>
                </div>
                <div class="settings-content">
                    ${this.renderProjectTabContent()}
                </div>
            </div>
        `;
    }
    
    renderProjectTabs() {
        const tabs = [
            { id: 'details', label: 'Details', icon: 'info' },
            { id: 'access', label: 'Access', icon: 'users' },
            { id: 'issue-types', label: 'Issue Types', icon: 'file-text' },
            { id: 'workflows', label: 'Workflows', icon: 'git-branch' },
            { id: 'screens', label: 'Screens', icon: 'layout' },
            { id: 'fields', label: 'Fields', icon: 'sliders' },
            { id: 'permissions', label: 'Permissions', icon: 'shield' }
        ];
        
        return tabs.map(tab => `
            <button class="settings-tab ${this.currentProjectTab === tab.id ? 'active' : ''}" onclick="settingsSystem.switchProjectTab('${tab.id}')">
                <i data-lucide="${tab.icon}"></i>
                ${tab.label}
            </button>
        `).join('');
    }
    
    renderProjectTabContent() {
        switch (this.currentProjectTab) {
            case 'details':
                return this.renderDetailsTab();
            case 'access':
                return this.renderAccessTab();
            case 'issue-types':
                return this.renderIssueTypesTab();
            case 'workflows':
                return this.renderWorkflowsTab();
            case 'screens':
                return this.renderScreensTab();
            case 'fields':
                return this.renderFieldsTab();
            case 'permissions':
                return this.renderPermissionsTab();
            default:
                return '';
        }
    }
    
    renderDetailsTab() {
        return `
            <div class="settings-section">
                <h3>Project Details</h3>
                <div class="settings-form">
                    <div class="form-group">
                        <label>Project Name</label>
                        <input type="text" value="${this.projectSettings.details.name}" onchange="settingsSystem.updateProjectDetail('name', this.value)" />
                    </div>
                    
                    <div class="form-group">
                        <label>Project Key</label>
                        <input type="text" value="${this.projectSettings.details.key}" readonly />
                        <small>Project key cannot be changed after creation</small>
                    </div>
                    
                    <div class="form-group">
                        <label>Description</label>
                        <textarea rows="4" onchange="settingsSystem.updateProjectDetail('description', this.value)">${this.projectSettings.details.description}</textarea>
                    </div>
                    
                    <div class="form-group">
                        <label>Project Avatar</label>
                        <div class="avatar-upload">
                            <div class="current-avatar">${this.projectSettings.details.key.substring(0, 2)}</div>
                            <button class="btn btn-secondary" onclick="settingsSystem.uploadAvatar()">
                                <i data-lucide="upload"></i>
                                Upload Image
                            </button>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label>Project Type</label>
                        <select onchange="settingsSystem.updateProjectDetail('projectType', this.value)">
                            <option value="software" ${this.projectSettings.details.projectType === 'software' ? 'selected' : ''}>Software</option>
                            <option value="service_desk" ${this.projectSettings.details.projectType === 'service_desk' ? 'selected' : ''}>Service Desk</option>
                            <option value="ops" ${this.projectSettings.details.projectType === 'ops' ? 'selected' : ''}>Operations</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Project Lead</label>
                        <input type="text" value="${this.projectSettings.details.lead}" onchange="settingsSystem.updateProjectDetail('lead', this.value)" />
                    </div>
                </div>
            </div>
        `;
    }
    
    renderAccessTab() {
        return `
            <div class="settings-section">
                <h3>Project Access</h3>
                <div class="access-header">
                    <button class="btn btn-primary" onclick="settingsSystem.inviteUser()">
                        <i data-lucide="user-plus"></i>
                        Invite User
                    </button>
                </div>
                
                <table class="access-table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Email</th>
                            <th>Role</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${this.projectSettings.access.users.map((user, index) => `
                            <tr>
                                <td>${user.name}</td>
                                <td>${user.email}</td>
                                <td>
                                    <select onchange="settingsSystem.updateUserRole(${index}, this.value)">
                                        <option value="admin" ${user.role === 'admin' ? 'selected' : ''}>Admin</option>
                                        <option value="member" ${user.role === 'member' ? 'selected' : ''}>Member</option>
                                        <option value="viewer" ${user.role === 'viewer' ? 'selected' : ''}>Viewer</option>
                                    </select>
                                </td>
                                <td>
                                    <button class="btn-icon" onclick="settingsSystem.removeUser(${index})" title="Remove">
                                        <i data-lucide="x"></i>
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }
    
    renderIssueTypesTab() {
        return `
            <div class="settings-section">
                <h3>Issue Types</h3>
                <div class="issue-types-header">
                    <button class="btn btn-primary" onclick="settingsSystem.addIssueType()">
                        <i data-lucide="plus"></i>
                        Add Issue Type
                    </button>
                </div>
                
                <div class="issue-types-list">
                    ${this.projectSettings.issueTypes.map(type => `
                        <div class="issue-type-card">
                            <div class="issue-type-icon">
                                <i data-lucide="${type.icon}"></i>
                            </div>
                            <div class="issue-type-info">
                                <h4>${type.name}</h4>
                                <p>${type.description}</p>
                                <span class="workflow-badge">${type.workflow}</span>
                            </div>
                            <div class="issue-type-actions">
                                <button class="btn-icon" onclick="settingsSystem.configureIssueType(${type.id})" title="Configure">
                                    <i data-lucide="settings"></i>
                                </button>
                                <button class="btn-icon" onclick="settingsSystem.deleteIssueType(${type.id})" title="Delete">
                                    <i data-lucide="trash-2"></i>
                                </button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    renderWorkflowsTab() {
        return `
            <div class="settings-section">
                <h3>Workflows</h3>
                <div class="workflows-header">
                    <button class="btn btn-primary" onclick="settingsSystem.createWorkflow()">
                        <i data-lucide="plus"></i>
                        Create Workflow
                    </button>
                </div>
                
                <div class="workflows-list">
                    ${this.projectSettings.workflows.map(workflow => `
                        <div class="workflow-card">
                            <div class="workflow-header">
                                <h4>${workflow.name}</h4>
                                <div class="workflow-actions">
                                    <button class="btn btn-secondary" onclick="settingsSystem.editWorkflow(${workflow.id})">
                                        <i data-lucide="edit"></i>
                                        Edit
                                    </button>
                                </div>
                            </div>
                            <div class="workflow-preview">
                                ${workflow.states.map((state, index) => `
                                    <div class="workflow-state">
                                        <span>${state}</span>
                                        ${index < workflow.states.length - 1 ? '<i data-lucide="arrow-right"></i>' : ''}
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    renderScreensTab() {
        return `
            <div class="settings-section">
                <h3>Screens</h3>
                <p class="section-description">Configure which fields appear on create, edit, and view screens</p>
                
                <div class="screens-list">
                    ${this.projectSettings.screens.map(screen => `
                        <div class="screen-card">
                            <h4>${screen.name}</h4>
                            <div class="screen-fields">
                                ${screen.fields.map(field => `
                                    <span class="field-badge">
                                        ${field}
                                        <i data-lucide="x"></i>
                                    </span>
                                `).join('')}
                            </div>
                            <button class="btn btn-secondary" onclick="settingsSystem.configureScreen(${screen.id})">
                                <i data-lucide="plus"></i>
                                Add Field
                            </button>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    renderFieldsTab() {
        return `
            <div class="settings-section">
                <h3>Custom Fields</h3>
                <div class="fields-header">
                    <button class="btn btn-primary" onclick="settingsSystem.createCustomField()">
                        <i data-lucide="plus"></i>
                        Create Field
                    </button>
                </div>
                
                <table class="fields-table">
                    <thead>
                        <tr>
                            <th>Field Name</th>
                            <th>Type</th>
                            <th>Required</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${this.projectSettings.customFields.map(field => `
                            <tr>
                                <td>${field.name}</td>
                                <td><span class="field-type-badge">${field.type}</span></td>
                                <td>
                                    <input type="checkbox" ${field.required ? 'checked' : ''} onchange="settingsSystem.toggleFieldRequired(${field.id}, this.checked)" />
                                </td>
                                <td>
                                    <button class="btn-icon" onclick="settingsSystem.editField(${field.id})" title="Edit">
                                        <i data-lucide="edit"></i>
                                    </button>
                                    <button class="btn-icon" onclick="settingsSystem.deleteField(${field.id})" title="Delete">
                                        <i data-lucide="trash-2"></i>
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }
    
    renderPermissionsTab() {
        const roles = ['admin', 'member', 'viewer'];
        
        return `
            <div class="settings-section">
                <h3>Permissions</h3>
                <p class="section-description">Configure what each role can do in this project</p>
                
                <div class="permissions-table-container">
                    <table class="permissions-table">
                        <thead>
                            <tr>
                                <th>Permission</th>
                                ${roles.map(role => `<th>${role}</th>`).join('')}
                            </tr>
                        </thead>
                        <tbody>
                            ${Object.entries(this.projectSettings.permissions).map(([permission, roles]) => `
                                <tr>
                                    <td>${permission}</td>
                                    ${Object.values(roles).map((allowed, index) => `
                                        <td>
                                            <input type="checkbox" ${allowed ? 'checked' : ''} onchange="settingsSystem.togglePermission('${permission}', '${Object.keys(roles)[index]}', this.checked)" />
                                        </td>
                                    `).join('')}
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }
    
    renderPersonalSettings() {
        return `
            <div class="settings-layout">
                <div class="settings-sidebar">
                    <div class="settings-nav">
                        ${this.renderPersonalTabs()}
                    </div>
                </div>
                <div class="settings-content">
                    ${this.renderPersonalTabContent()}
                </div>
            </div>
        `;
    }
    
    renderPersonalTabs() {
        const tabs = [
            { id: 'profile', label: 'Profile', icon: 'user' },
            { id: 'email', label: 'Email Preferences', icon: 'mail' },
            { id: 'notifications', label: 'Notifications', icon: 'bell' },
            { id: 'shortcuts', label: 'Keyboard Shortcuts', icon: 'command' },
            { id: 'theme', label: 'Theme', icon: 'palette' }
        ];
        
        return tabs.map(tab => `
            <button class="settings-tab ${this.currentPersonalTab === tab.id ? 'active' : ''}" onclick="settingsSystem.switchPersonalTab('${tab.id}')">
                <i data-lucide="${tab.icon}"></i>
                ${tab.label}
            </button>
        `).join('');
    }
    
    renderPersonalTabContent() {
        switch (this.currentPersonalTab) {
            case 'profile':
                return this.renderProfileTab();
            case 'email':
                return this.renderEmailTab();
            case 'notifications':
                return this.renderNotificationsTab();
            case 'shortcuts':
                return this.renderShortcutsTab();
            case 'theme':
                return this.renderThemeTab();
            default:
                return '';
        }
    }
    
    renderProfileTab() {
        return `
            <div class="settings-section">
                <h3>Your Profile</h3>
                <div class="settings-form">
                    <div class="form-group">
                        <label>Avatar</label>
                        <div class="avatar-upload">
                            <div class="current-avatar large">
                                ${this.personalSettings.profile.displayName.split(' ').map(n => n[0]).join('')}
                            </div>
                            <button class="btn btn-secondary" onclick="settingsSystem.uploadPersonalAvatar()">
                                <i data-lucide="upload"></i>
                                Upload Photo
                            </button>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label>Display Name</label>
                        <input type="text" value="${this.personalSettings.profile.displayName}" onchange="settingsSystem.updatePersonalSetting('profile', 'displayName', this.value)" />
                    </div>
                    
                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" value="${this.personalSettings.profile.email}" onchange="settingsSystem.updatePersonalSetting('profile', 'email', this.value)" />
                    </div>
                    
                    <div class="form-group">
                        <label>Bio</label>
                        <textarea rows="3" onchange="settingsSystem.updatePersonalSetting('profile', 'bio', this.value)">${this.personalSettings.profile.bio}</textarea>
                    </div>
                    
                    <div class="form-group">
                        <label>Timezone</label>
                        <select onchange="settingsSystem.updatePersonalSetting('profile', 'timezone', this.value)">
                            <option value="America/New_York" ${this.personalSettings.profile.timezone === 'America/New_York' ? 'selected' : ''}>Eastern Time (ET)</option>
                            <option value="America/Chicago">Central Time (CT)</option>
                            <option value="America/Denver">Mountain Time (MT)</option>
                            <option value="America/Los_Angeles">Pacific Time (PT)</option>
                            <option value="Europe/London">London (GMT)</option>
                            <option value="Europe/Paris">Paris (CET)</option>
                            <option value="Asia/Tokyo">Tokyo (JST)</option>
                        </select>
                    </div>
                </div>
            </div>
        `;
    }
    
    renderEmailTab() {
        return `
            <div class="settings-section">
                <h3>Email Preferences</h3>
                <div class="settings-form">
                    <div class="form-group">
                        <label>Email Frequency</label>
                        <div class="radio-group">
                            <label class="radio-label">
                                <input type="radio" name="frequency" value="instant" ${this.personalSettings.email.frequency === 'instant' ? 'checked' : ''} onchange="settingsSystem.updatePersonalSetting('email', 'frequency', this.value)" />
                                <span>Instant - Receive emails immediately</span>
                            </label>
                            <label class="radio-label">
                                <input type="radio" name="frequency" value="daily" ${this.personalSettings.email.frequency === 'daily' ? 'checked' : ''} onchange="settingsSystem.updatePersonalSetting('email', 'frequency', this.value)" />
                                <span>Daily Digest - Once per day</span>
                            </label>
                            <label class="radio-label">
                                <input type="radio" name="frequency" value="weekly" ${this.personalSettings.email.frequency === 'weekly' ? 'checked' : ''} onchange="settingsSystem.updatePersonalSetting('email', 'frequency', this.value)" />
                                <span>Weekly Digest - Once per week</span>
                            </label>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label>Email me when:</label>
                        <div class="checkbox-group">
                            <label class="checkbox-label">
                                <input type="checkbox" ${this.personalSettings.email.preferences.issueUpdates ? 'checked' : ''} onchange="settingsSystem.updateEmailPreference('issueUpdates', this.checked)" />
                                <span>Issues I'm watching are updated</span>
                            </label>
                            <label class="checkbox-label">
                                <input type="checkbox" ${this.personalSettings.email.preferences.mentions ? 'checked' : ''} onchange="settingsSystem.updateEmailPreference('mentions', this.checked)" />
                                <span>Someone @mentions me</span>
                            </label>
                            <label class="checkbox-label">
                                <input type="checkbox" ${this.personalSettings.email.preferences.comments ? 'checked' : ''} onchange="settingsSystem.updateEmailPreference('comments', this.checked)" />
                                <span>Someone comments on my issues</span>
                            </label>
                            <label class="checkbox-label">
                                <input type="checkbox" ${this.personalSettings.email.preferences.assignments ? 'checked' : ''} onchange="settingsSystem.updateEmailPreference('assignments', this.checked)" />
                                <span>Issues are assigned to me</span>
                            </label>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    renderNotificationsTab() {
        return `
            <div class="settings-section">
                <h3>Notification Settings</h3>
                <div class="settings-form">
                    <div class="form-group">
                        <div class="toggle-setting">
                            <div class="toggle-info">
                                <label>In-app Notifications</label>
                                <small>Show notifications in the app</small>
                            </div>
                            <label class="toggle-switch">
                                <input type="checkbox" ${this.personalSettings.notifications.inApp ? 'checked' : ''} onchange="settingsSystem.updateNotificationSetting('inApp', this.checked)" />
                                <span class="toggle-slider"></span>
                            </label>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <div class="toggle-setting">
                            <div class="toggle-info">
                                <label>Desktop Notifications</label>
                                <small>Show desktop notifications</small>
                            </div>
                            <label class="toggle-switch">
                                <input type="checkbox" ${this.personalSettings.notifications.desktop ? 'checked' : ''} onchange="settingsSystem.updateNotificationSetting('desktop', this.checked)" />
                                <span class="toggle-slider"></span>
                            </label>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <div class="toggle-setting">
                            <div class="toggle-info">
                                <label>Notification Sound</label>
                                <small>Play sound for notifications</small>
                            </div>
                            <label class="toggle-switch">
                                <input type="checkbox" ${this.personalSettings.notifications.sound ? 'checked' : ''} onchange="settingsSystem.updateNotificationSetting('sound', this.checked)" />
                                <span class="toggle-slider"></span>
                            </label>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label>Do Not Disturb Schedule</label>
                        <div class="time-range">
                            <input type="time" value="${this.personalSettings.notifications.dndStart}" onchange="settingsSystem.updateNotificationSetting('dndStart', this.value)" />
                            <span>to</span>
                            <input type="time" value="${this.personalSettings.notifications.dndEnd}" onchange="settingsSystem.updateNotificationSetting('dndEnd', this.value)" />
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    renderShortcutsTab() {
        return `
            <div class="settings-section">
                <h3>Keyboard Shortcuts</h3>
                <div class="shortcuts-header">
                    <button class="btn btn-secondary" onclick="settingsSystem.resetShortcuts()">
                        <i data-lucide="rotate-ccw"></i>
                        Reset to Defaults
                    </button>
                </div>
                
                <table class="shortcuts-table">
                    <thead>
                        <tr>
                            <th>Action</th>
                            <th>Shortcut</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${this.personalSettings.shortcuts.map(shortcut => `
                            <tr>
                                <td>${shortcut.action}</td>
                                <td><kbd>${shortcut.key}</kbd></td>
                                <td>${shortcut.description}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }
    
    renderThemeTab() {
        return `
            <div class="settings-section">
                <h3>Theme</h3>
                <div class="theme-selector">
                    <label class="theme-option">
                        <input type="radio" name="theme" value="light" ${this.personalSettings.theme === 'light' ? 'checked' : ''} onchange="settingsSystem.updatePersonalSetting('theme', null, this.value)" />
                        <div class="theme-preview light-theme">
                            <div class="theme-preview-header"></div>
                            <div class="theme-preview-content">
                                <div class="theme-preview-sidebar"></div>
                                <div class="theme-preview-main"></div>
                            </div>
                        </div>
                        <span>Light</span>
                    </label>
                    
                    <label class="theme-option">
                        <input type="radio" name="theme" value="dark" ${this.personalSettings.theme === 'dark' ? 'checked' : ''} onchange="settingsSystem.updatePersonalSetting('theme', null, this.value)" />
                        <div class="theme-preview dark-theme">
                            <div class="theme-preview-header"></div>
                            <div class="theme-preview-content">
                                <div class="theme-preview-sidebar"></div>
                                <div class="theme-preview-main"></div>
                            </div>
                        </div>
                        <span>Dark</span>
                    </label>
                    
                    <label class="theme-option">
                        <input type="radio" name="theme" value="auto" ${this.personalSettings.theme === 'auto' ? 'checked' : ''} onchange="settingsSystem.updatePersonalSetting('theme', null, this.value)" />
                        <div class="theme-preview auto-theme">
                            <div class="theme-preview-header"></div>
                            <div class="theme-preview-content">
                                <div class="theme-preview-sidebar"></div>
                                <div class="theme-preview-main"></div>
                            </div>
                        </div>
                        <span>Auto (System)</span>
                    </label>
                </div>
            </div>
        `;
    }
    
    // State management methods
    switchSettingsType(type) {
        this.currentSettingsType = type;
        const container = document.querySelector('.settings-container').parentElement;
        this.renderSettingsPage(container);
    }
    
    switchProjectTab(tab) {
        this.currentProjectTab = tab;
        const container = document.querySelector('.settings-container').parentElement;
        this.renderSettingsPage(container);
    }
    
    switchPersonalTab(tab) {
        this.currentPersonalTab = tab;
        const container = document.querySelector('.settings-container').parentElement;
        this.renderSettingsPage(container);
    }
    
    // Update methods with auto-save
    updateProjectDetail(field, value) {
        this.projectSettings.details[field] = value;
        this.showToast('Saved');
    }
    
    updateUserRole(index, role) {
        this.projectSettings.access.users[index].role = role;
        this.showToast('Role updated');
    }
    
    toggleFieldRequired(fieldId, required) {
        const field = this.projectSettings.customFields.find(f => f.id === fieldId);
        if (field) {
            field.required = required;
            this.showToast('Field updated');
        }
    }
    
    togglePermission(permission, role, allowed) {
        this.projectSettings.permissions[permission][role] = allowed;
        this.showToast('Permission updated');
    }
    
    updatePersonalSetting(section, field, value) {
        if (field) {
            this.personalSettings[section][field] = value;
        } else {
            this.personalSettings[section] = value;
        }
        this.showToast('Saved');
    }
    
    updateEmailPreference(preference, value) {
        this.personalSettings.email.preferences[preference] = value;
        this.showToast('Saved');
    }
    
    updateNotificationSetting(setting, value) {
        this.personalSettings.notifications[setting] = value;
        this.showToast('Saved');
    }
    
    // Action methods
    uploadAvatar() {
        alert('Avatar upload would open file picker');
    }
    
    uploadPersonalAvatar() {
        alert('Personal avatar upload would open file picker');
    }
    
    inviteUser() {
        alert('Invite user modal would open');
    }
    
    removeUser(index) {
        if (confirm('Remove this user from the project?')) {
            this.projectSettings.access.users.splice(index, 1);
            const container = document.querySelector('.settings-container').parentElement;
            this.renderSettingsPage(container);
            this.showToast('User removed');
        }
    }
    
    addIssueType() {
        alert('Add issue type modal would open');
    }
    
    configureIssueType(id) {
        alert(`Configure issue type ${id}`);
    }
    
    deleteIssueType(id) {
        alert(`Delete issue type ${id}`);
    }
    
    createWorkflow() {
        alert('Create workflow modal would open');
    }
    
    editWorkflow(id) {
        alert(`Edit workflow ${id} - Visual designer would open`);
    }
    
    configureScreen(id) {
        alert(`Configure screen ${id}`);
    }
    
    createCustomField() {
        alert('Create custom field modal would open');
    }
    
    editField(id) {
        alert(`Edit field ${id}`);
    }
    
    deleteField(id) {
        alert(`Delete field ${id}`);
    }
    
    resetShortcuts() {
        if (confirm('Reset all shortcuts to defaults?')) {
            this.showToast('Shortcuts reset');
        }
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
const settingsSystem = new SettingsSystem();
