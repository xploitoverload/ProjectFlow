/**
 * User Management & Permissions System
 * User directory, Permission schemes, Security levels, Roles, Bulk import
 */

class UserManagementSystem {
    constructor() {
        this.users = [
            { id: 'u1', name: 'John Doe', email: 'john@example.com', role: 'Administrator', status: 'active', groups: ['Developers', 'Admins'], lastLogin: '2 hours ago' },
            { id: 'u2', name: 'Jane Smith', email: 'jane@example.com', role: 'Developer', status: 'active', groups: ['Developers'], lastLogin: '1 day ago' },
            { id: 'u3', name: 'Bob Johnson', email: 'bob@example.com', role: 'Viewer', status: 'inactive', groups: ['Viewers'], lastLogin: '30 days ago' }
        ];
        
        this.groups = [
            { id: 'g1', name: 'Developers', members: 15, description: 'Development team members' },
            { id: 'g2', name: 'Admins', members: 3, description: 'System administrators' },
            { id: 'g3', name: 'Viewers', members: 25, description: 'Read-only users' }
        ];
        
        this.permissionSchemes = [
            { id: 'ps1', name: 'Default Permission Scheme', projects: 5, permissions: ['Browse Projects', 'Create Issues', 'Edit Issues'] },
            { id: 'ps2', name: 'Restricted Scheme', projects: 2, permissions: ['Browse Projects'] }
        ];
        
        this.securityLevels = [
            { id: 'sl1', name: 'Public', description: 'Visible to all users' },
            { id: 'sl2', name: 'Internal', description: 'Visible to team members only' },
            { id: 'sl3', name: 'Confidential', description: 'Visible to managers and above' }
        ];
        
        this.projectRoles = [
            { id: 'pr1', name: 'Project Administrator', description: 'Full project access', users: 5 },
            { id: 'pr2', name: 'Developer', description: 'Can edit issues', users: 20 },
            { id: 'pr3', name: 'Viewer', description: 'Read-only access', users: 30 }
        ];
        
        this.activeTab = 'users';
        
        this.init();
    }
    
    init() {
        console.log('User Management System initialized');
    }
    
    render(container) {
        container.innerHTML = `
            <div class="user-management-container">
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
            <div class="user-mgmt-header">
                <h2>User Management</h2>
                <div class="header-actions">
                    ${this.activeTab === 'users' ? `
                        <button class="btn btn-secondary" onclick="userManagementSystem.bulkImport()">
                            <i data-lucide="upload"></i>
                            Bulk Import
                        </button>
                        <button class="btn btn-primary" onclick="userManagementSystem.addUser()">
                            <i data-lucide="user-plus"></i>
                            Add User
                        </button>
                    ` : this.activeTab === 'groups' ? `
                        <button class="btn btn-primary" onclick="userManagementSystem.createGroup()">
                            <i data-lucide="users"></i>
                            Create Group
                        </button>
                    ` : this.activeTab === 'permissions' ? `
                        <button class="btn btn-primary" onclick="userManagementSystem.createPermissionScheme()">
                            <i data-lucide="shield"></i>
                            Create Scheme
                        </button>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    renderTabs() {
        return `
            <div class="user-mgmt-tabs">
                <button class="tab ${this.activeTab === 'users' ? 'active' : ''}" 
                    onclick="userManagementSystem.switchTab('users')">
                    <i data-lucide="users"></i>
                    Users
                </button>
                <button class="tab ${this.activeTab === 'groups' ? 'active' : ''}" 
                    onclick="userManagementSystem.switchTab('groups')">
                    <i data-lucide="layers"></i>
                    Groups
                </button>
                <button class="tab ${this.activeTab === 'permissions' ? 'active' : ''}" 
                    onclick="userManagementSystem.switchTab('permissions')">
                    <i data-lucide="shield"></i>
                    Permission Schemes
                </button>
                <button class="tab ${this.activeTab === 'security' ? 'active' : ''}" 
                    onclick="userManagementSystem.switchTab('security')">
                    <i data-lucide="lock"></i>
                    Security Levels
                </button>
                <button class="tab ${this.activeTab === 'roles' ? 'active' : ''}" 
                    onclick="userManagementSystem.switchTab('roles')">
                    <i data-lucide="user-check"></i>
                    Project Roles
                </button>
                <button class="tab ${this.activeTab === 'global-perms' ? 'active' : ''}" 
                    onclick="userManagementSystem.switchTab('global-perms')">
                    <i data-lucide="globe"></i>
                    Global Permissions
                </button>
            </div>
        `;
    }
    
    renderContent() {
        switch(this.activeTab) {
            case 'users':
                return this.renderUsers();
            case 'groups':
                return this.renderGroups();
            case 'permissions':
                return this.renderPermissionSchemes();
            case 'security':
                return this.renderSecurityLevels();
            case 'roles':
                return this.renderProjectRoles();
            case 'global-perms':
                return this.renderGlobalPermissions();
            default:
                return '';
        }
    }
    
    renderUsers() {
        return `
            <div class="user-mgmt-content">
                <div class="users-toolbar">
                    <div class="search-bar">
                        <i data-lucide="search"></i>
                        <input type="text" placeholder="Search users..." />
                    </div>
                    <select class="filter-select">
                        <option>All statuses</option>
                        <option>Active only</option>
                        <option>Inactive only</option>
                    </select>
                    <select class="filter-select">
                        <option>All roles</option>
                        <option>Administrators</option>
                        <option>Developers</option>
                        <option>Viewers</option>
                    </select>
                </div>
                
                <div class="users-table">
                    <table>
                        <thead>
                            <tr>
                                <th>User</th>
                                <th>Email</th>
                                <th>Role</th>
                                <th>Groups</th>
                                <th>Status</th>
                                <th>Last Login</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${this.users.map(user => `
                                <tr>
                                    <td>
                                        <div class="user-cell">
                                            <img src="https://ui-avatars.com/api/?name=${user.name}" alt="" class="user-avatar-sm" />
                                            <span>${user.name}</span>
                                        </div>
                                    </td>
                                    <td>${user.email}</td>
                                    <td><span class="role-badge">${user.role}</span></td>
                                    <td><span class="groups-badge">${user.groups.join(', ')}</span></td>
                                    <td><span class="status-badge status-${user.status}">${user.status}</span></td>
                                    <td>${user.lastLogin}</td>
                                    <td>
                                        <button class="btn-icon-sm" onclick="userManagementSystem.viewUserProfile('${user.id}')">
                                            <i data-lucide="eye"></i>
                                        </button>
                                        <button class="btn-icon-sm" onclick="userManagementSystem.editUser('${user.id}')">
                                            <i data-lucide="edit-2"></i>
                                        </button>
                                        <button class="btn-icon-sm" onclick="userManagementSystem.deactivateUser('${user.id}')">
                                            <i data-lucide="user-x"></i>
                                        </button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }
    
    renderGroups() {
        return `
            <div class="user-mgmt-content">
                <div class="groups-grid">
                    ${this.groups.map(group => `
                        <div class="group-card">
                            <div class="group-header">
                                <div class="group-icon">
                                    <i data-lucide="users"></i>
                                </div>
                                <button class="btn-icon-sm" onclick="userManagementSystem.groupMenu('${group.id}', this)">
                                    <i data-lucide="more-horizontal"></i>
                                </button>
                            </div>
                            <h3>${group.name}</h3>
                            <p class="group-description">${group.description}</p>
                            <div class="group-stats">
                                <i data-lucide="users"></i>
                                <span>${group.members} members</span>
                            </div>
                            <div class="group-actions">
                                <button class="btn btn-secondary-sm" onclick="userManagementSystem.manageGroupMembers('${group.id}')">
                                    Manage Members
                                </button>
                                <button class="btn btn-link-sm" onclick="userManagementSystem.viewGroupPermissions('${group.id}')">
                                    View Permissions
                                </button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    renderPermissionSchemes() {
        return `
            <div class="user-mgmt-content">
                <div class="permission-schemes-list">
                    ${this.permissionSchemes.map(scheme => `
                        <div class="permission-scheme-card">
                            <div class="scheme-header">
                                <h3>${scheme.name}</h3>
                                <button class="btn-icon-sm" onclick="userManagementSystem.editPermissionScheme('${scheme.id}')">
                                    <i data-lucide="edit-2"></i>
                                </button>
                            </div>
                            <div class="scheme-info">
                                <span class="scheme-stat">Used in ${scheme.projects} projects</span>
                            </div>
                            <div class="scheme-permissions">
                                ${scheme.permissions.map(perm => `
                                    <span class="permission-chip">${perm}</span>
                                `).join('')}
                            </div>
                            <button class="btn btn-link" onclick="userManagementSystem.viewPermissionMatrix('${scheme.id}')">
                                View Full Matrix
                            </button>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    renderSecurityLevels() {
        return `
            <div class="user-mgmt-content">
                <div class="security-levels-list">
                    ${this.securityLevels.map(level => `
                        <div class="security-level-card">
                            <div class="level-header">
                                <i data-lucide="lock"></i>
                                <h3>${level.name}</h3>
                                <button class="btn-icon-sm" onclick="userManagementSystem.editSecurityLevel('${level.id}')">
                                    <i data-lucide="edit-2"></i>
                                </button>
                            </div>
                            <p>${level.description}</p>
                            <button class="btn btn-link" onclick="userManagementSystem.manageSecurityLevelAccess('${level.id}')">
                                Manage Access
                            </button>
                        </div>
                    `).join('')}
                    
                    <button class="btn btn-primary" onclick="userManagementSystem.createSecurityLevel()">
                        <i data-lucide="plus"></i>
                        Add Security Level
                    </button>
                </div>
            </div>
        `;
    }
    
    renderProjectRoles() {
        return `
            <div class="user-mgmt-content">
                <div class="project-roles-list">
                    ${this.projectRoles.map(role => `
                        <div class="project-role-card">
                            <div class="role-header">
                                <h3>${role.name}</h3>
                                <button class="btn-icon-sm" onclick="userManagementSystem.editProjectRole('${role.id}')">
                                    <i data-lucide="edit-2"></i>
                                </button>
                            </div>
                            <p>${role.description}</p>
                            <div class="role-stats">
                                <i data-lucide="user"></i>
                                <span>${role.users} users with this role</span>
                            </div>
                            <button class="btn btn-link" onclick="userManagementSystem.configureRolePermissions('${role.id}')">
                                Configure Permissions
                            </button>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    renderGlobalPermissions() {
        const permissions = [
            { category: 'System', permissions: ['Administer Jira', 'Create Projects', 'Browse Users'] },
            { category: 'Projects', permissions: ['Browse Projects', 'Create Issues', 'Edit Issues', 'Delete Issues'] },
            { category: 'Comments', permissions: ['Add Comments', 'Edit All Comments', 'Delete All Comments'] }
        ];
        
        const roles = ['Administrators', 'Developers', 'Viewers'];
        
        return `
            <div class="user-mgmt-content">
                <div class="global-permissions-matrix">
                    <h3>Global Permissions Matrix</h3>
                    <div class="permissions-table">
                        <table>
                            <thead>
                                <tr>
                                    <th>Permission</th>
                                    ${roles.map(role => `<th>${role}</th>`).join('')}
                                </tr>
                            </thead>
                            <tbody>
                                ${permissions.map(cat => `
                                    <tr class="category-row">
                                        <td colspan="${roles.length + 1}"><strong>${cat.category}</strong></td>
                                    </tr>
                                    ${cat.permissions.map(perm => `
                                        <tr>
                                            <td>${perm}</td>
                                            ${roles.map((role, idx) => `
                                                <td>
                                                    <input type="checkbox" ${idx === 0 ? 'checked' : ''} 
                                                        onchange="userManagementSystem.togglePermission('${perm}', '${role}', this.checked)" />
                                                </td>
                                            `).join('')}
                                        </tr>
                                    `).join('')}
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                    <div class="matrix-actions">
                        <button class="btn btn-secondary" onclick="userManagementSystem.resetToDefaults()">
                            Reset to Defaults
                        </button>
                        <button class="btn btn-primary" onclick="userManagementSystem.saveGlobalPermissions()">
                            Save Changes
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Methods
    switchTab(tab) {
        this.activeTab = tab;
        const container = document.querySelector('.user-management-container').parentElement;
        this.render(container);
    }
    
    addUser() {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h3>Add New User</h3>
                    <button class="btn-icon" onclick="this.closest('.modal-overlay').remove()">
                        <i data-lucide="x"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label>Full Name</label>
                        <input type="text" placeholder="Enter full name" />
                    </div>
                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" placeholder="user@example.com" />
                    </div>
                    <div class="form-group">
                        <label>Role</label>
                        <select>
                            <option>Administrator</option>
                            <option>Developer</option>
                            <option>Viewer</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Groups</label>
                        <select multiple>
                            <option>Developers</option>
                            <option>Admins</option>
                            <option>Viewers</option>
                        </select>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                    <button class="btn btn-primary" onclick="userManagementSystem.saveUser(); this.closest('.modal-overlay').remove()">
                        Add User
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        if (typeof lucide !== 'undefined') lucide.createIcons();
    }
    
    bulkImport() {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h3>Bulk Import Users</h3>
                    <button class="btn-icon" onclick="this.closest('.modal-overlay').remove()">
                        <i data-lucide="x"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <p>Upload a CSV file with user data. Required columns: Name, Email, Role</p>
                    <div class="file-upload-zone">
                        <i data-lucide="upload"></i>
                        <p>Drag and drop CSV file here, or click to browse</p>
                        <input type="file" accept=".csv" style="display: none;" />
                    </div>
                    <a href="#" class="download-template">Download CSV template</a>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                    <button class="btn btn-primary">Import Users</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        if (typeof lucide !== 'undefined') lucide.createIcons();
    }
    
    viewUserProfile(userId) {
        this.showToast('Opening user profile');
    }
    
    saveUser() {
        this.showToast('User added successfully');
    }
    
    saveGlobalPermissions() {
        this.showToast('Permissions saved');
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
const userManagementSystem = new UserManagementSystem();
