/**
 * Permissions System - JIRA-style permission schemes
 * Features: Permission schemes, role-based access, security levels
 */

class PermissionsSystem {
    constructor() {
        this.permissions = this.getPermissions();
        this.schemes = [];
        this.roles = [];
        this.securityLevels = [];
        this.selectedScheme = null;
        
        this.init();
    }

    init() {
        this.createModal();
        this.setupEventListeners();
        this.loadSchemes();
    }

    getPermissions() {
        return [
            // Project Permissions
            { id: 'project.admin', name: 'Administer Projects', category: 'project', description: 'Full project administration access' },
            { id: 'project.browse', name: 'Browse Projects', category: 'project', description: 'View project and its issues' },
            { id: 'project.view.readonly', name: 'View Read-Only Workflow', category: 'project', description: 'View read-only workflows' },
            
            // Issue Permissions
            { id: 'issue.create', name: 'Create Issues', category: 'issue', description: 'Create new issues' },
            { id: 'issue.edit', name: 'Edit Issues', category: 'issue', description: 'Edit existing issues' },
            { id: 'issue.delete', name: 'Delete Issues', category: 'issue', description: 'Delete issues' },
            { id: 'issue.assign', name: 'Assign Issues', category: 'issue', description: 'Assign issues to users' },
            { id: 'issue.assignable', name: 'Assignable User', category: 'issue', description: 'Can be assigned to issues' },
            { id: 'issue.close', name: 'Close Issues', category: 'issue', description: 'Close/resolve issues' },
            { id: 'issue.transition', name: 'Transition Issues', category: 'issue', description: 'Move issues through workflow' },
            { id: 'issue.move', name: 'Move Issues', category: 'issue', description: 'Move issues between projects' },
            { id: 'issue.link', name: 'Link Issues', category: 'issue', description: 'Create issue links' },
            
            // Comment Permissions
            { id: 'comment.add', name: 'Add Comments', category: 'comment', description: 'Add comments to issues' },
            { id: 'comment.edit.all', name: 'Edit All Comments', category: 'comment', description: 'Edit all comments' },
            { id: 'comment.edit.own', name: 'Edit Own Comments', category: 'comment', description: 'Edit own comments' },
            { id: 'comment.delete.all', name: 'Delete All Comments', category: 'comment', description: 'Delete all comments' },
            { id: 'comment.delete.own', name: 'Delete Own Comments', category: 'comment', description: 'Delete own comments' },
            
            // Attachment Permissions
            { id: 'attachment.create', name: 'Create Attachments', category: 'attachment', description: 'Add attachments to issues' },
            { id: 'attachment.delete.all', name: 'Delete All Attachments', category: 'attachment', description: 'Delete all attachments' },
            { id: 'attachment.delete.own', name: 'Delete Own Attachments', category: 'attachment', description: 'Delete own attachments' },
            
            // Voter/Watcher Permissions
            { id: 'issue.vote', name: 'Vote on Issues', category: 'voters', description: 'Vote on issues' },
            { id: 'voters.view', name: 'View Voters', category: 'voters', description: 'View who voted on issues' },
            { id: 'issue.watch', name: 'Watch Issues', category: 'watchers', description: 'Watch issues for updates' },
            { id: 'watchers.manage', name: 'Manage Watchers', category: 'watchers', description: 'Add/remove watchers' },
            { id: 'watchers.view', name: 'View Watchers', category: 'watchers', description: 'View who is watching' },
            
            // Time Tracking Permissions
            { id: 'worklog.create', name: 'Log Work', category: 'time', description: 'Log work on issues' },
            { id: 'worklog.edit.all', name: 'Edit All Work Logs', category: 'time', description: 'Edit all work logs' },
            { id: 'worklog.edit.own', name: 'Edit Own Work Logs', category: 'time', description: 'Edit own work logs' },
            { id: 'worklog.delete.all', name: 'Delete All Work Logs', category: 'time', description: 'Delete all work logs' },
            { id: 'worklog.delete.own', name: 'Delete Own Work Logs', category: 'time', description: 'Delete own work logs' },
            
            // Sprint Permissions
            { id: 'sprint.manage', name: 'Manage Sprints', category: 'agile', description: 'Create and manage sprints' },
            { id: 'backlog.view', name: 'View Backlog', category: 'agile', description: 'View product backlog' },
            { id: 'backlog.manage', name: 'Manage Backlog', category: 'agile', description: 'Reorder and manage backlog' }
        ];
    }

    createModal() {
        const modalHTML = `
            <div id="permissionsModal" class="perms-modal" style="display: none;">
                <div class="perms-modal-backdrop"></div>
                <div class="perms-modal-container">
                    <div class="perms-modal-header">
                        <h2>Permission Schemes</h2>
                        <div class="header-actions">
                            <button class="btn btn-primary btn-sm" id="createSchemeBtn">
                                <i data-lucide="plus"></i>
                                Create Scheme
                            </button>
                            <button class="btn btn-ghost btn-sm" id="manageRolesBtn">
                                <i data-lucide="users"></i>
                                Manage Roles
                            </button>
                            <button class="btn btn-ghost btn-sm" id="securityLevelsBtn">
                                <i data-lucide="shield"></i>
                                Security Levels
                            </button>
                            <button class="btn-icon" id="closePermsModal">
                                <i data-lucide="x"></i>
                            </button>
                        </div>
                    </div>

                    <div class="perms-modal-body">
                        <!-- Schemes List -->
                        <div class="schemes-sidebar">
                            <div class="sidebar-header">
                                <h3>Schemes</h3>
                            </div>
                            <div class="schemes-list" id="schemesList">
                                <!-- Populated by JS -->
                            </div>
                        </div>

                        <!-- Scheme Details -->
                        <div class="scheme-content">
                            <div id="schemeContentArea">
                                <div class="empty-state">
                                    <i data-lucide="shield-check"></i>
                                    <h3>Permission Schemes</h3>
                                    <p>Control who can do what in your projects</p>
                                    <button class="btn btn-primary" onclick="permissionsSystem.createScheme()">
                                        <i data-lucide="plus"></i>
                                        Create Permission Scheme
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Scheme Editor Dialog -->
            <div id="schemeEditorDialog" class="perm-dialog" style="display: none;">
                <div class="perm-dialog-backdrop"></div>
                <div class="perm-dialog-container large">
                    <div class="perm-dialog-header">
                        <h3 id="schemeEditorTitle">Create Permission Scheme</h3>
                        <button class="btn-icon-sm" onclick="permissionsSystem.closeSchemeEditor()">
                            <i data-lucide="x"></i>
                        </button>
                    </div>
                    <div class="perm-dialog-body">
                        <div class="form-group">
                            <label>Scheme Name *</label>
                            <input type="text" class="form-input" id="schemeNameInput" placeholder="Enter scheme name">
                        </div>

                        <div class="form-group">
                            <label>Description</label>
                            <textarea class="form-input" id="schemeDescInput" rows="2" 
                                      placeholder="Describe what this scheme is for"></textarea>
                        </div>

                        <hr>

                        <h4>Permissions Configuration</h4>
                        <p class="hint-text">Configure who can perform each action</p>

                        <div id="permissionsConfig">
                            <!-- Populated by JS -->
                        </div>
                    </div>
                    <div class="perm-dialog-footer">
                        <button class="btn btn-ghost" onclick="permissionsSystem.closeSchemeEditor()">Cancel</button>
                        <button class="btn btn-primary" id="saveSchemeBtn">Save Scheme</button>
                    </div>
                </div>
            </div>

            <!-- Grant Permission Dialog -->
            <div id="grantPermDialog" class="perm-dialog" style="display: none;">
                <div class="perm-dialog-backdrop"></div>
                <div class="perm-dialog-container">
                    <div class="perm-dialog-header">
                        <h3 id="grantPermTitle">Grant Permission</h3>
                        <button class="btn-icon-sm" onclick="permissionsSystem.closeGrantDialog()">
                            <i data-lucide="x"></i>
                        </button>
                    </div>
                    <div class="perm-dialog-body">
                        <div class="form-group">
                            <label>Grant Type</label>
                            <select class="form-input" id="grantTypeSelect">
                                <option value="role">Project Role</option>
                                <option value="user">Specific User</option>
                                <option value="group">User Group</option>
                                <option value="reporter">Issue Reporter</option>
                                <option value="assignee">Current Assignee</option>
                                <option value="projectlead">Project Lead</option>
                            </select>
                        </div>

                        <div class="form-group" id="grantValueGroup">
                            <!-- Dynamic based on grant type -->
                        </div>
                    </div>
                    <div class="perm-dialog-footer">
                        <button class="btn btn-ghost" onclick="permissionsSystem.closeGrantDialog()">Cancel</button>
                        <button class="btn btn-primary" id="saveGrantBtn">Grant</button>
                    </div>
                </div>
            </div>

            <!-- Roles Manager Dialog -->
            <div id="rolesDialog" class="perm-dialog" style="display: none;">
                <div class="perm-dialog-backdrop"></div>
                <div class="perm-dialog-container">
                    <div class="perm-dialog-header">
                        <h3>Project Roles</h3>
                        <button class="btn-icon-sm" onclick="permissionsSystem.closeRolesDialog()">
                            <i data-lucide="x"></i>
                        </button>
                    </div>
                    <div class="perm-dialog-body">
                        <div class="roles-list" id="rolesList">
                            <!-- Populated by JS -->
                        </div>
                        <button class="btn btn-ghost btn-sm" onclick="permissionsSystem.createRole()">
                            <i data-lucide="plus"></i>
                            Add Role
                        </button>
                    </div>
                    <div class="perm-dialog-footer">
                        <button class="btn btn-primary" onclick="permissionsSystem.closeRolesDialog()">Done</button>
                    </div>
                </div>
            </div>

            <!-- Security Levels Dialog -->
            <div id="securityDialog" class="perm-dialog" style="display: none;">
                <div class="perm-dialog-backdrop"></div>
                <div class="perm-dialog-container">
                    <div class="perm-dialog-header">
                        <h3>Issue Security Levels</h3>
                        <button class="btn-icon-sm" onclick="permissionsSystem.closeSecurityDialog()">
                            <i data-lucide="x"></i>
                        </button>
                    </div>
                    <div class="perm-dialog-body">
                        <p class="hint-text">Security levels restrict who can view issues</p>
                        <div class="security-levels-list" id="securityLevelsList">
                            <!-- Populated by JS -->
                        </div>
                        <button class="btn btn-ghost btn-sm" onclick="permissionsSystem.createSecurityLevel()">
                            <i data-lucide="plus"></i>
                            Add Security Level
                        </button>
                    </div>
                    <div class="perm-dialog-footer">
                        <button class="btn btn-primary" onclick="permissionsSystem.closeSecurityDialog()">Done</button>
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
        document.getElementById('closePermsModal')?.addEventListener('click', () => {
            this.closeModal();
        });

        document.getElementById('createSchemeBtn')?.addEventListener('click', () => {
            this.createScheme();
        });

        document.getElementById('manageRolesBtn')?.addEventListener('click', () => {
            this.showRolesDialog();
        });

        document.getElementById('securityLevelsBtn')?.addEventListener('click', () => {
            this.showSecurityDialog();
        });

        document.getElementById('saveSchemeBtn')?.addEventListener('click', () => {
            this.saveScheme();
        });

        document.getElementById('saveGrantBtn')?.addEventListener('click', () => {
            this.saveGrant();
        });

        document.getElementById('grantTypeSelect')?.addEventListener('change', (e) => {
            this.updateGrantValueField(e.target.value);
        });
    }

    openModal() {
        document.getElementById('permissionsModal').style.display = 'block';
        this.renderSchemesList();
    }

    closeModal() {
        document.getElementById('permissionsModal').style.display = 'none';
    }

    async loadSchemes() {
        try {
            const response = await fetch('/api/permission-schemes');
            if (response.ok) {
                this.schemes = await response.json();
                this.renderSchemesList();
            }
        } catch (error) {
            console.error('Failed to load schemes:', error);
        }

        // Load default roles
        this.roles = [
            { id: 'admin', name: 'Administrators', description: 'Project administrators' },
            { id: 'developer', name: 'Developers', description: 'Team members who work on issues' },
            { id: 'viewer', name: 'Viewers', description: 'Read-only access' }
        ];
    }

    renderSchemesList() {
        const container = document.getElementById('schemesList');
        
        if (this.schemes.length === 0) {
            container.innerHTML = '<p class="empty-text">No schemes yet</p>';
            return;
        }

        container.innerHTML = this.schemes.map(scheme => `
            <div class="scheme-item ${this.selectedScheme?.id === scheme.id ? 'active' : ''}" 
                 onclick="permissionsSystem.selectScheme('${scheme.id}')">
                <div class="scheme-icon">
                    <i data-lucide="shield"></i>
                </div>
                <div class="scheme-info">
                    <div class="scheme-name">${scheme.name}</div>
                    <div class="scheme-projects">${scheme.projects?.length || 0} projects</div>
                </div>
            </div>
        `).join('');

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    selectScheme(schemeId) {
        this.selectedScheme = this.schemes.find(s => s.id === schemeId);
        this.renderSchemeDetails(this.selectedScheme);
        this.renderSchemesList();
    }

    renderSchemeDetails(scheme) {
        const content = document.getElementById('schemeContentArea');

        // Group permissions by category
        const categories = [...new Set(this.permissions.map(p => p.category))];

        content.innerHTML = `
            <div class="scheme-details">
                <div class="scheme-header">
                    <div>
                        <h3>${scheme.name}</h3>
                        <p class="scheme-desc">${scheme.description || 'No description'}</p>
                    </div>
                    <div class="scheme-actions">
                        <button class="btn btn-ghost btn-sm" onclick="permissionsSystem.editScheme('${scheme.id}')">
                            <i data-lucide="edit-2"></i>
                            Edit
                        </button>
                        <button class="btn btn-ghost btn-sm" onclick="permissionsSystem.copyScheme('${scheme.id}')">
                            <i data-lucide="copy"></i>
                            Copy
                        </button>
                        <button class="btn btn-ghost btn-sm" onclick="permissionsSystem.deleteScheme('${scheme.id}')">
                            <i data-lucide="trash-2"></i>
                            Delete
                        </button>
                    </div>
                </div>

                <div class="permissions-table">
                    ${categories.map(category => `
                        <div class="perm-category">
                            <h4 class="category-title">${this.getCategoryName(category)}</h4>
                            ${this.permissions.filter(p => p.category === category).map(perm => `
                                <div class="perm-row">
                                    <div class="perm-info">
                                        <div class="perm-name">${perm.name}</div>
                                        <div class="perm-desc">${perm.description}</div>
                                    </div>
                                    <div class="perm-grants">
                                        ${this.renderPermissionGrants(scheme, perm.id)}
                                    </div>
                                    <button class="btn btn-ghost btn-sm" 
                                            onclick="permissionsSystem.grantPermission('${scheme.id}', '${perm.id}')">
                                        <i data-lucide="plus"></i>
                                        Grant
                                    </button>
                                </div>
                            `).join('')}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    getCategoryName(category) {
        const names = {
            project: 'Project Permissions',
            issue: 'Issue Permissions',
            comment: 'Comment Permissions',
            attachment: 'Attachment Permissions',
            voters: 'Voter Permissions',
            watchers: 'Watcher Permissions',
            time: 'Time Tracking Permissions',
            agile: 'Agile Permissions'
        };
        return names[category] || category;
    }

    renderPermissionGrants(scheme, permissionId) {
        const grants = scheme.permissions?.[permissionId] || [];
        
        if (grants.length === 0) {
            return '<span class="no-grants">Not granted</span>';
        }

        return grants.map(grant => {
            const label = this.getGrantLabel(grant);
            return `
                <span class="grant-tag">
                    ${label}
                    <button class="remove-grant" onclick="permissionsSystem.removeGrant('${scheme.id}', '${permissionId}', '${grant.type}', '${grant.value || ''}'); event.stopPropagation();">
                        <i data-lucide="x"></i>
                    </button>
                </span>
            `;
        }).join('');
    }

    getGrantLabel(grant) {
        switch (grant.type) {
            case 'role':
                return `Role: ${grant.value}`;
            case 'user':
                return `User: ${grant.value}`;
            case 'group':
                return `Group: ${grant.value}`;
            case 'reporter':
                return 'Issue Reporter';
            case 'assignee':
                return 'Current Assignee';
            case 'projectlead':
                return 'Project Lead';
            default:
                return grant.type;
        }
    }

    createScheme() {
        this.showSchemeEditor(null);
    }

    editScheme(schemeId) {
        const scheme = this.schemes.find(s => s.id === schemeId);
        this.showSchemeEditor(scheme);
    }

    showSchemeEditor(scheme) {
        const isEdit = !!scheme;
        document.getElementById('schemeEditorTitle').textContent = 
            isEdit ? `Edit ${scheme.name}` : 'Create Permission Scheme';

        document.getElementById('schemeNameInput').value = scheme?.name || '';
        document.getElementById('schemeDescInput').value = scheme?.description || '';

        const config = document.getElementById('permissionsConfig');
        const categories = [...new Set(this.permissions.map(p => p.category))];

        config.innerHTML = categories.map(category => `
            <div class="config-category">
                <h5>${this.getCategoryName(category)}</h5>
                ${this.permissions.filter(p => p.category === category).map(perm => `
                    <div class="config-perm">
                        <label>${perm.name}</label>
                        <p class="config-perm-desc">${perm.description}</p>
                    </div>
                `).join('')}
            </div>
        `).join('');

        document.getElementById('schemeEditorDialog').style.display = 'block';
        this.currentScheme = scheme;

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    closeSchemeEditor() {
        document.getElementById('schemeEditorDialog').style.display = 'none';
        this.currentScheme = null;
    }

    async saveScheme() {
        const name = document.getElementById('schemeNameInput').value.trim();
        const description = document.getElementById('schemeDescInput').value.trim();

        if (!name) {
            alert('Please enter a scheme name');
            return;
        }

        const schemeData = {
            id: this.currentScheme?.id || `scheme-${Date.now()}`,
            name,
            description,
            permissions: this.currentScheme?.permissions || {}
        };

        try {
            const url = this.currentScheme 
                ? `/api/permission-schemes/${schemeData.id}`
                : '/api/permission-schemes';
            
            const response = await fetch(url, {
                method: this.currentScheme ? 'PUT' : 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(schemeData)
            });

            if (response.ok) {
                if (this.currentScheme) {
                    const index = this.schemes.findIndex(s => s.id === schemeData.id);
                    this.schemes[index] = schemeData;
                } else {
                    this.schemes.push(schemeData);
                }
                
                this.closeSchemeEditor();
                this.renderSchemesList();
                this.selectScheme(schemeData.id);
            }
        } catch (error) {
            console.error('Failed to save scheme:', error);
        }
    }

    grantPermission(schemeId, permissionId) {
        this.currentGrantScheme = schemeId;
        this.currentGrantPermission = permissionId;
        
        this.updateGrantValueField('role');
        document.getElementById('grantPermDialog').style.display = 'block';

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    updateGrantValueField(grantType) {
        const group = document.getElementById('grantValueGroup');
        
        switch (grantType) {
            case 'role':
                group.innerHTML = `
                    <label>Project Role</label>
                    <select class="form-input" id="grantValueInput">
                        ${this.roles.map(role => `<option value="${role.id}">${role.name}</option>`).join('')}
                    </select>
                `;
                break;
            case 'user':
                group.innerHTML = `
                    <label>User</label>
                    <input type="text" class="form-input" id="grantValueInput" placeholder="Enter username">
                `;
                break;
            case 'group':
                group.innerHTML = `
                    <label>User Group</label>
                    <input type="text" class="form-input" id="grantValueInput" placeholder="Enter group name">
                `;
                break;
            default:
                group.innerHTML = '';
        }
    }

    closeGrantDialog() {
        document.getElementById('grantPermDialog').style.display = 'none';
        this.currentGrantScheme = null;
        this.currentGrantPermission = null;
    }

    async saveGrant() {
        const grantType = document.getElementById('grantTypeSelect').value;
        const grantValue = document.getElementById('grantValueInput')?.value;

        const scheme = this.schemes.find(s => s.id === this.currentGrantScheme);
        if (!scheme) return;

        if (!scheme.permissions) scheme.permissions = {};
        if (!scheme.permissions[this.currentGrantPermission]) {
            scheme.permissions[this.currentGrantPermission] = [];
        }

        const grant = { type: grantType };
        if (grantValue) grant.value = grantValue;

        scheme.permissions[this.currentGrantPermission].push(grant);

        try {
            const response = await fetch(`/api/permission-schemes/${scheme.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(scheme)
            });

            if (response.ok) {
                this.closeGrantDialog();
                this.renderSchemeDetails(scheme);
            }
        } catch (error) {
            console.error('Failed to save grant:', error);
        }
    }

    async removeGrant(schemeId, permissionId, grantType, grantValue) {
        const scheme = this.schemes.find(s => s.id === schemeId);
        if (!scheme) return;

        scheme.permissions[permissionId] = scheme.permissions[permissionId].filter(g => 
            !(g.type === grantType && (!grantValue || g.value === grantValue))
        );

        try {
            const response = await fetch(`/api/permission-schemes/${scheme.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(scheme)
            });

            if (response.ok) {
                this.renderSchemeDetails(scheme);
            }
        } catch (error) {
            console.error('Failed to remove grant:', error);
        }
    }

    async copyScheme(schemeId) {
        const scheme = this.schemes.find(s => s.id === schemeId);
        if (!scheme) return;

        const newScheme = {
            ...scheme,
            id: `scheme-${Date.now()}`,
            name: `${scheme.name} (Copy)`
        };

        this.schemes.push(newScheme);
        this.renderSchemesList();
        this.selectScheme(newScheme.id);
    }

    async deleteScheme(schemeId) {
        if (!confirm('Delete this permission scheme?')) return;

        try {
            const response = await fetch(`/api/permission-schemes/${schemeId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.schemes = this.schemes.filter(s => s.id !== schemeId);
                this.selectedScheme = null;
                this.renderSchemesList();
                
                document.getElementById('schemeContentArea').innerHTML = `
                    <div class="empty-state">
                        <i data-lucide="shield-check"></i>
                        <h3>Scheme Deleted</h3>
                    </div>
                `;

                if (window.lucide) {
                    lucide.createIcons();
                }
            }
        } catch (error) {
            console.error('Failed to delete scheme:', error);
        }
    }

    showRolesDialog() {
        this.renderRolesList();
        document.getElementById('rolesDialog').style.display = 'block';
    }

    closeRolesDialog() {
        document.getElementById('rolesDialog').style.display = 'none';
    }

    renderRolesList() {
        const container = document.getElementById('rolesList');
        container.innerHTML = this.roles.map(role => `
            <div class="role-item">
                <div class="role-info">
                    <div class="role-name">${role.name}</div>
                    <div class="role-desc">${role.description}</div>
                </div>
                <button class="btn-icon-sm" onclick="permissionsSystem.deleteRole('${role.id}')">
                    <i data-lucide="trash-2"></i>
                </button>
            </div>
        `).join('');

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    createRole() {
        const name = prompt('Enter role name:');
        if (!name) return;

        const description = prompt('Enter role description:');
        
        this.roles.push({
            id: `role-${Date.now()}`,
            name,
            description: description || ''
        });

        this.renderRolesList();
    }

    deleteRole(roleId) {
        this.roles = this.roles.filter(r => r.id !== roleId);
        this.renderRolesList();
    }

    showSecurityDialog() {
        this.renderSecurityLevels();
        document.getElementById('securityDialog').style.display = 'block';
    }

    closeSecurityDialog() {
        document.getElementById('securityDialog').style.display = 'none';
    }

    renderSecurityLevels() {
        const container = document.getElementById('securityLevelsList');
        
        if (this.securityLevels.length === 0) {
            container.innerHTML = '<p class="empty-text">No security levels defined</p>';
            return;
        }

        container.innerHTML = this.securityLevels.map(level => `
            <div class="security-level-item">
                <div class="level-info">
                    <div class="level-name">${level.name}</div>
                    <div class="level-desc">${level.description}</div>
                </div>
                <button class="btn-icon-sm" onclick="permissionsSystem.deleteSecurityLevel('${level.id}')">
                    <i data-lucide="trash-2"></i>
                </button>
            </div>
        `).join('');

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    createSecurityLevel() {
        const name = prompt('Enter security level name:');
        if (!name) return;

        const description = prompt('Enter description:');
        
        this.securityLevels.push({
            id: `level-${Date.now()}`,
            name,
            description: description || ''
        });

        this.renderSecurityLevels();
    }

    deleteSecurityLevel(levelId) {
        this.securityLevels = this.securityLevels.filter(l => l.id !== levelId);
        this.renderSecurityLevels();
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.permissionsSystem = new PermissionsSystem();
});

// Global function to open permissions
function openPermissions() {
    window.permissionsSystem?.openModal();
}
