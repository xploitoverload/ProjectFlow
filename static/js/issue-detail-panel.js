/**
 * Issue Detail Panel - Complete Features
 * Attachments, Linked Issues, Subtasks, Approvals, SLA, Activity, History, More Fields
 */

class IssueDetailPanel {
    constructor() {
        this.currentIssue = null;
        this.activeTab = 'details';
        this.attachments = [];
        this.linkedIssues = [];
        this.subtasks = [];
        this.comments = [];
        this.history = [];
        this.approvals = [];
        
        this.linkTypes = [
            { id: 'blocks', label: 'blocks', reverse: 'is blocked by' },
            { id: 'relates', label: 'relates to', reverse: 'relates to' },
            { id: 'duplicates', label: 'duplicates', reverse: 'is duplicated by' },
            { id: 'clones', label: 'clones', reverse: 'is cloned by' },
            { id: 'causes', label: 'causes', reverse: 'is caused by' }
        ];
        
        this.init();
    }
    
    init() {
        this.setupDragDrop();
        console.log('Issue Detail Panel initialized');
    }
    
    render(container, issueKey) {
        this.currentIssue = issueKey;
        this.loadIssueData(issueKey);
        
        container.innerHTML = `
            <div class="issue-detail-panel">
                ${this.renderHeader()}
                ${this.renderTabBar()}
                ${this.renderTabContent()}
            </div>
        `;
        
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }
    
    renderHeader() {
        return `
            <div class="issue-detail-header">
                <div class="header-top">
                    <div class="issue-key-type">
                        <span class="issue-type-icon">
                            <i data-lucide="file-text"></i>
                        </span>
                        <h2 class="issue-key">${this.currentIssue}</h2>
                        <span class="issue-status-badge status-in-progress">In Progress</span>
                    </div>
                    <div class="header-actions">
                        <button class="btn-icon" onclick="issueDetailPanel.watchIssue()" title="Watch">
                            <i data-lucide="eye"></i>
                        </button>
                        <button class="btn-icon" onclick="issueDetailPanel.voteIssue()" title="Vote">
                            <i data-lucide="thumbs-up"></i>
                            <span class="vote-count">3</span>
                        </button>
                        <button class="btn-icon" onclick="issueDetailPanel.shareIssue()" title="Share">
                            <i data-lucide="share-2"></i>
                        </button>
                        <div class="dropdown">
                            <button class="btn-icon" onclick="issueDetailPanel.toggleActionsMenu(this)">
                                <i data-lucide="more-horizontal"></i>
                            </button>
                            <div class="dropdown-menu">
                                <button onclick="issueDetailPanel.editIssue()">
                                    <i data-lucide="edit"></i> Edit
                                </button>
                                <button onclick="issueDetailPanel.moveIssue()">
                                    <i data-lucide="folder"></i> Move
                                </button>
                                <button onclick="issueDetailPanel.cloneIssue()">
                                    <i data-lucide="copy"></i> Clone
                                </button>
                                <button onclick="issueDetailPanel.linkIssue()">
                                    <i data-lucide="link"></i> Link Issue
                                </button>
                                <button onclick="issueDetailPanel.logWork()">
                                    <i data-lucide="clock"></i> Log Work
                                </button>
                                <button onclick="issueDetailPanel.exportIssue()">
                                    <i data-lucide="download"></i> Export
                                </button>
                                <div class="dropdown-divider"></div>
                                <button onclick="issueDetailPanel.deleteIssue()" class="text-danger">
                                    <i data-lucide="trash-2"></i> Delete
                                </button>
                            </div>
                        </div>
                        <button class="btn-icon" onclick="issueDetailPanel.close()">
                            <i data-lucide="x"></i>
                        </button>
                    </div>
                </div>
                
                <div class="issue-summary-edit">
                    <h3 contenteditable="true" onblur="issueDetailPanel.updateSummary(this.textContent)">
                        Implement user authentication and authorization system
                    </h3>
                </div>
            </div>
        `;
    }
    
    renderTabBar() {
        const tabs = [
            { id: 'details', label: 'Details', icon: 'file-text' },
            { id: 'activity', label: 'Activity', icon: 'activity', badge: 12 },
            { id: 'history', label: 'History', icon: 'clock', badge: 28 },
            { id: 'subtasks', label: 'Subtasks', icon: 'list', badge: 5 },
            { id: 'linkedIssues', label: 'Linked Issues', icon: 'link', badge: 3 },
            { id: 'attachments', label: 'Attachments', icon: 'paperclip', badge: 4 },
            { id: 'approvals', label: 'Approvals', icon: 'check-circle', badge: 2 }
        ];
        
        return `
            <div class="tab-bar">
                ${tabs.map(tab => `
                    <button class="tab ${this.activeTab === tab.id ? 'active' : ''}" 
                        onclick="issueDetailPanel.switchTab('${tab.id}')">
                        <i data-lucide="${tab.icon}"></i>
                        <span>${tab.label}</span>
                        ${tab.badge ? `<span class="tab-badge">${tab.badge}</span>` : ''}
                    </button>
                `).join('')}
            </div>
        `;
    }
    
    renderTabContent() {
        switch(this.activeTab) {
            case 'details':
                return this.renderDetailsTab();
            case 'activity':
                return this.renderActivityTab();
            case 'history':
                return this.renderHistoryTab();
            case 'subtasks':
                return this.renderSubtasksTab();
            case 'linkedIssues':
                return this.renderLinkedIssuesTab();
            case 'attachments':
                return this.renderAttachmentsTab();
            case 'approvals':
                return this.renderApprovalsTab();
            default:
                return '';
        }
    }
    
    renderDetailsTab() {
        return `
            <div class="tab-content">
                <div class="detail-layout">
                    <div class="detail-main">
                        ${this.renderDescription()}
                        ${this.renderSLAWidget()}
                        ${this.renderConfluenceLinks()}
                    </div>
                    <div class="detail-sidebar">
                        ${this.renderFieldsSection()}
                        ${this.renderMoreFieldsSection()}
                    </div>
                </div>
            </div>
        `;
    }
    
    renderDescription() {
        return `
            <div class="description-section">
                <div class="section-header">
                    <h4>Description</h4>
                    <button class="btn-icon-sm" onclick="issueDetailPanel.editDescription()">
                        <i data-lucide="edit-2"></i>
                    </button>
                </div>
                <div class="description-content" contenteditable="false">
                    <p>Implement a comprehensive authentication and authorization system with the following requirements:</p>
                    <ul>
                        <li>OAuth 2.0 integration</li>
                        <li>Multi-factor authentication</li>
                        <li>Role-based access control</li>
                        <li>Session management</li>
                    </ul>
                </div>
            </div>
        `;
    }
    
    renderSLAWidget() {
        return `
            <div class="sla-widget warning">
                <div class="sla-header">
                    <i data-lucide="alert-triangle"></i>
                    <span class="sla-title">Time to Resolution</span>
                    <span class="sla-status">Breached</span>
                </div>
                <div class="sla-progress">
                    <div class="sla-progress-bar" style="width: 120%"></div>
                </div>
                <div class="sla-details">
                    <span class="sla-time">12h 34m overdue</span>
                    <span class="sla-target">Target: 8h</span>
                </div>
            </div>
        `;
    }
    
    renderConfluenceLinks() {
        return `
            <div class="confluence-section">
                <div class="section-header">
                    <h4>Confluence Pages</h4>
                    <button class="btn btn-secondary-sm" onclick="issueDetailPanel.linkConfluence()">
                        <i data-lucide="plus"></i>
                        Link Page
                    </button>
                </div>
                <div class="confluence-links">
                    <a href="#" class="confluence-link">
                        <i data-lucide="file-text"></i>
                        <span>Authentication Architecture</span>
                    </a>
                    <a href="#" class="confluence-link">
                        <i data-lucide="file-text"></i>
                        <span>Security Requirements</span>
                    </a>
                </div>
            </div>
        `;
    }
    
    renderFieldsSection() {
        return `
            <div class="fields-section">
                <div class="field-group">
                    <label>Assignee</label>
                    <div class="field-value editable" onclick="issueDetailPanel.editField('assignee')">
                        <img src="https://ui-avatars.com/api/?name=John+Doe" alt="" class="avatar-sm" />
                        <span>John Doe</span>
                        <i data-lucide="edit-2"></i>
                    </div>
                </div>
                
                <div class="field-group">
                    <label>Reporter</label>
                    <div class="field-value">
                        <img src="https://ui-avatars.com/api/?name=Jane+Smith" alt="" class="avatar-sm" />
                        <span>Jane Smith</span>
                    </div>
                </div>
                
                <div class="field-group">
                    <label>Priority</label>
                    <div class="field-value editable" onclick="issueDetailPanel.editField('priority')">
                        <span class="priority-badge priority-high">High</span>
                        <i data-lucide="edit-2"></i>
                    </div>
                </div>
                
                <div class="field-group">
                    <label>Labels</label>
                    <div class="field-value labels-value">
                        <span class="label-tag">authentication</span>
                        <span class="label-tag">security</span>
                        <button class="btn-icon-sm" onclick="issueDetailPanel.addLabel()">
                            <i data-lucide="plus"></i>
                        </button>
                    </div>
                </div>
                
                <div class="field-group">
                    <label>Components</label>
                    <div class="field-value">
                        <span class="component-tag">Backend</span>
                        <span class="component-tag">API</span>
                    </div>
                </div>
                
                <div class="field-group">
                    <label>Fix Versions</label>
                    <div class="field-value editable" onclick="issueDetailPanel.editField('fixVersions')">
                        <span>v2.0.0</span>
                        <i data-lucide="edit-2"></i>
                    </div>
                </div>
                
                <div class="field-group">
                    <label>Story Points</label>
                    <div class="field-value editable" onclick="issueDetailPanel.editField('storyPoints')">
                        <span class="story-points">8</span>
                        <i data-lucide="edit-2"></i>
                    </div>
                </div>
                
                <div class="field-group">
                    <label>Sprint</label>
                    <div class="field-value">
                        <span>Sprint 23</span>
                    </div>
                </div>
                
                <div class="field-group">
                    <label>Due Date</label>
                    <div class="field-value editable" onclick="issueDetailPanel.editField('dueDate')">
                        <span>Dec 31, 2024</span>
                        <i data-lucide="edit-2"></i>
                    </div>
                </div>
            </div>
        `;
    }
    
    renderMoreFieldsSection() {
        return `
            <div class="more-fields-section collapsed">
                <button class="more-fields-toggle" onclick="issueDetailPanel.toggleMoreFields()">
                    <i data-lucide="chevron-right"></i>
                    <span>Show 12 more fields</span>
                </button>
                <div class="more-fields-content">
                    <div class="field-group">
                        <label>Environment</label>
                        <div class="field-value">Production</div>
                    </div>
                    <div class="field-group">
                        <label>Affects Versions</label>
                        <div class="field-value">v1.9.5</div>
                    </div>
                    <!-- More fields... -->
                </div>
            </div>
        `;
    }
    
    renderActivityTab() {
        return `
            <div class="tab-content">
                <div class="activity-filters">
                    <button class="filter-btn active" onclick="issueDetailPanel.filterActivity('all')">All</button>
                    <button class="filter-btn" onclick="issueDetailPanel.filterActivity('comments')">Comments</button>
                    <button class="filter-btn" onclick="issueDetailPanel.filterActivity('history')">History</button>
                    <button class="filter-btn" onclick="issueDetailPanel.filterActivity('worklog')">Work Log</button>
                </div>
                
                <div class="activity-list">
                    ${this.renderActivityItems()}
                </div>
                
                <div class="comment-box">
                    <img src="https://ui-avatars.com/api/?name=Current+User" alt="" class="avatar" />
                    <div class="comment-input">
                        <textarea placeholder="Add a comment..." rows="3"></textarea>
                        <div class="comment-actions">
                            <button class="btn btn-secondary" onclick="issueDetailPanel.cancelComment()">Cancel</button>
                            <button class="btn btn-primary" onclick="issueDetailPanel.saveComment()">Comment</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    renderActivityItems() {
        const items = [
            { type: 'comment', user: 'John Doe', time: '2 hours ago', content: 'I\'ve started implementing the OAuth integration.' },
            { type: 'field_change', user: 'Jane Smith', time: '3 hours ago', field: 'Status', from: 'To Do', to: 'In Progress' },
            { type: 'worklog', user: 'John Doe', time: '4 hours ago', timeSpent: '2h 30m', content: 'Initial OAuth setup' }
        ];
        
        return items.map(item => `
            <div class="activity-item activity-${item.type}">
                <img src="https://ui-avatars.com/api/?name=${item.user}" alt="" class="avatar" />
                <div class="activity-content">
                    <div class="activity-header">
                        <span class="activity-user">${item.user}</span>
                        <span class="activity-time">${item.time}</span>
                    </div>
                    <div class="activity-body">
                        ${item.content || `changed <strong>${item.field}</strong> from <span class="field-value-old">${item.from}</span> to <span class="field-value-new">${item.to}</span>`}
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    renderHistoryTab() {
        return `
            <div class="tab-content">
                <div class="history-list">
                    ${this.renderHistoryItems()}
                </div>
            </div>
        `;
    }
    
    renderHistoryItems() {
        const history = [
            { field: 'Status', from: 'To Do', to: 'In Progress', user: 'Jane Smith', time: '3 hours ago' },
            { field: 'Assignee', from: 'Unassigned', to: 'John Doe', user: 'Jane Smith', time: '5 hours ago' },
            { field: 'Priority', from: 'Medium', to: 'High', user: 'Bob Johnson', time: '1 day ago' }
        ];
        
        return history.map(item => `
            <div class="history-item">
                <div class="history-icon">
                    <i data-lucide="edit-3"></i>
                </div>
                <div class="history-content">
                    <div class="history-header">
                        <span class="history-user">${item.user}</span>
                        <span class="history-time">${item.time}</span>
                    </div>
                    <div class="history-change">
                        <strong>${item.field}</strong>
                        <div class="change-diff">
                            <div class="diff-old">- ${item.from}</div>
                            <div class="diff-new">+ ${item.to}</div>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    renderSubtasksTab() {
        return `
            <div class="tab-content">
                <div class="subtasks-header">
                    <h4>Subtasks (3 of 5 completed)</h4>
                    <button class="btn btn-primary-sm" onclick="issueDetailPanel.createSubtask()">
                        <i data-lucide="plus"></i>
                        Create Subtask
                    </button>
                </div>
                
                <div class="subtasks-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 60%"></div>
                    </div>
                    <span class="progress-text">60%</span>
                </div>
                
                <div class="subtasks-list">
                    ${this.renderSubtaskItems()}
                </div>
            </div>
        `;
    }
    
    renderSubtaskItems() {
        const subtasks = [
            { key: 'TEST-143', summary: 'Setup OAuth provider', status: 'Done', assignee: 'John Doe' },
            { key: 'TEST-144', summary: 'Implement JWT tokens', status: 'Done', assignee: 'John Doe' },
            { key: 'TEST-145', summary: 'Add MFA support', status: 'Done', assignee: 'Jane Smith' },
            { key: 'TEST-146', summary: 'Create RBAC system', status: 'In Progress', assignee: 'John Doe' },
            { key: 'TEST-147', summary: 'Add session management', status: 'To Do', assignee: 'Unassigned' }
        ];
        
        return subtasks.map(subtask => `
            <div class="subtask-item" draggable="true">
                <i data-lucide="grip-vertical" class="drag-handle"></i>
                <input type="checkbox" ${subtask.status === 'Done' ? 'checked' : ''} 
                    onchange="issueDetailPanel.toggleSubtask('${subtask.key}')" />
                <a href="#" class="subtask-key">${subtask.key}</a>
                <span class="subtask-summary ${subtask.status === 'Done' ? 'completed' : ''}">${subtask.summary}</span>
                <span class="subtask-status status-${subtask.status.toLowerCase().replace(' ', '-')}">${subtask.status}</span>
                <img src="https://ui-avatars.com/api/?name=${subtask.assignee}" alt="" class="avatar-sm" title="${subtask.assignee}" />
            </div>
        `).join('');
    }
    
    renderLinkedIssuesTab() {
        return `
            <div class="tab-content">
                <div class="linked-issues-header">
                    <h4>Linked Issues</h4>
                    <button class="btn btn-primary-sm" onclick="issueDetailPanel.linkIssue()">
                        <i data-lucide="link"></i>
                        Link Issue
                    </button>
                </div>
                
                <div class="linked-issues-list">
                    ${this.renderLinkedIssueGroups()}
                </div>
                
                <button class="btn btn-secondary-sm" onclick="issueDetailPanel.showRelationshipGraph()">
                    <i data-lucide="git-branch"></i>
                    View Relationship Graph
                </button>
            </div>
        `;
    }
    
    renderLinkedIssueGroups() {
        const links = [
            { type: 'blocks', issues: [
                { key: 'TEST-135', summary: 'Setup authentication database', status: 'Done' }
            ]},
            { type: 'relates', issues: [
                { key: 'TEST-150', summary: 'Update user profile API', status: 'To Do' },
                { key: 'TEST-151', summary: 'Add audit logging', status: 'To Do' }
            ]}
        ];
        
        return links.map(group => {
            const linkType = this.linkTypes.find(lt => lt.id === group.type);
            return `
                <div class="linked-group">
                    <div class="link-type-header">
                        <i data-lucide="arrow-right"></i>
                        <span>${linkType.label}</span>
                        <span class="link-count">(${group.issues.length})</span>
                    </div>
                    <div class="linked-issues">
                        ${group.issues.map(issue => `
                            <div class="linked-issue">
                                <a href="#" class="issue-key">${issue.key}</a>
                                <span class="issue-summary">${issue.summary}</span>
                                <span class="issue-status status-${issue.status.toLowerCase().replace(' ', '-')}">${issue.status}</span>
                                <button class="btn-icon-sm" onclick="issueDetailPanel.unlinkIssue('${issue.key}')">
                                    <i data-lucide="x"></i>
                                </button>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }).join('');
    }
    
    renderAttachmentsTab() {
        return `
            <div class="tab-content">
                <div class="attachments-header">
                    <h4>Attachments</h4>
                    <button class="btn btn-primary-sm" onclick="document.getElementById('fileInput').click()">
                        <i data-lucide="upload"></i>
                        Upload Files
                    </button>
                    <input type="file" id="fileInput" multiple style="display:none" onchange="issueDetailPanel.uploadFiles(this.files)" />
                </div>
                
                <div class="dropzone" id="attachmentDropzone">
                    <i data-lucide="upload-cloud"></i>
                    <p>Drag & drop files here or click to browse</p>
                </div>
                
                <div class="attachments-grid">
                    ${this.renderAttachmentItems()}
                </div>
            </div>
        `;
    }
    
    renderAttachmentItems() {
        const attachments = [
            { name: 'authentication-flow.png', type: 'image', size: '245 KB', thumbnail: 'https://via.placeholder.com/200x150', uploaded: '2 hours ago', user: 'John Doe' },
            { name: 'api-documentation.pdf', type: 'pdf', size: '1.2 MB', uploaded: '1 day ago', user: 'Jane Smith' },
            { name: 'oauth-config.json', type: 'code', size: '5 KB', uploaded: '3 days ago', user: 'Bob Johnson' }
        ];
        
        return attachments.map(file => `
            <div class="attachment-card">
                ${file.type === 'image' ? `
                    <div class="attachment-preview image">
                        <img src="${file.thumbnail}" alt="${file.name}" />
                    </div>
                ` : `
                    <div class="attachment-preview ${file.type}">
                        <i data-lucide="file-${file.type === 'pdf' ? 'text' : 'code'}"></i>
                    </div>
                `}
                <div class="attachment-info">
                    <div class="attachment-name" title="${file.name}">${file.name}</div>
                    <div class="attachment-meta">
                        <span class="attachment-size">${file.size}</span>
                        <span class="attachment-time">${file.uploaded}</span>
                    </div>
                    <div class="attachment-user">by ${file.user}</div>
                </div>
                <div class="attachment-actions">
                    <button class="btn-icon-sm" onclick="issueDetailPanel.downloadAttachment('${file.name}')" title="Download">
                        <i data-lucide="download"></i>
                    </button>
                    <button class="btn-icon-sm" onclick="issueDetailPanel.deleteAttachment('${file.name}')" title="Delete">
                        <i data-lucide="trash-2"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }
    
    renderApprovalsTab() {
        return `
            <div class="tab-content">
                <div class="approvals-header">
                    <h4>Approvals</h4>
                    <button class="btn btn-primary-sm" onclick="issueDetailPanel.addApprover()">
                        <i data-lucide="user-plus"></i>
                        Add Approver
                    </button>
                </div>
                
                <div class="approval-stages">
                    ${this.renderApprovalStages()}
                </div>
            </div>
        `;
    }
    
    renderApprovalStages() {
        const stages = [
            { name: 'Technical Review', approvers: [
                { name: 'John Doe', status: 'approved', time: '2 hours ago', comment: 'Looks good!' }
            ], status: 'approved' },
            { name: 'Security Review', approvers: [
                { name: 'Jane Smith', status: 'pending', time: null, comment: null },
                { name: 'Bob Johnson', status: 'pending', time: null, comment: null }
            ], status: 'pending' }
        ];
        
        return stages.map(stage => `
            <div class="approval-stage approval-${stage.status}">
                <div class="stage-header">
                    <i data-lucide="${stage.status === 'approved' ? 'check-circle' : 'clock'}"></i>
                    <h5>${stage.name}</h5>
                    <span class="stage-status">${stage.status}</span>
                </div>
                <div class="stage-approvers">
                    ${stage.approvers.map(approver => `
                        <div class="approver-item approver-${approver.status}">
                            <img src="https://ui-avatars.com/api/?name=${approver.name}" alt="" class="avatar" />
                            <div class="approver-info">
                                <div class="approver-name">${approver.name}</div>
                                <div class="approver-status">
                                    ${approver.status === 'approved' ? `
                                        <i data-lucide="check-circle"></i>
                                        Approved ${approver.time}
                                    ` : `
                                        <i data-lucide="clock"></i>
                                        Pending approval
                                    `}
                                </div>
                                ${approver.comment ? `<div class="approver-comment">${approver.comment}</div>` : ''}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `).join('');
    }
    
    // Methods
    switchTab(tabId) {
        this.activeTab = tabId;
        const container = document.querySelector('.issue-detail-panel').parentElement;
        this.render(container, this.currentIssue);
    }
    
    loadIssueData(issueKey) {
        // Load issue data from API
        console.log('Loading issue:', issueKey);
    }
    
    setupDragDrop() {
        document.addEventListener('dragover', (e) => {
            const dropzone = document.getElementById('attachmentDropzone');
            if (dropzone && e.target.closest('.tab-content')) {
                e.preventDefault();
                dropzone.classList.add('dragover');
            }
        });
        
        document.addEventListener('dragleave', (e) => {
            const dropzone = document.getElementById('attachmentDropzone');
            if (dropzone) {
                dropzone.classList.remove('dragover');
            }
        });
        
        document.addEventListener('drop', (e) => {
            const dropzone = document.getElementById('attachmentDropzone');
            if (dropzone && e.target.closest('.tab-content')) {
                e.preventDefault();
                dropzone.classList.remove('dragover');
                this.uploadFiles(e.dataTransfer.files);
            }
        });
    }
    
    uploadFiles(files) {
        console.log('Uploading files:', files);
        this.showToast(`Uploading ${files.length} file(s)...`);
    }
    
    createSubtask() {
        this.showToast('Create subtask dialog');
    }
    
    linkIssue() {
        this.showToast('Link issue dialog');
    }
    
    toggleMoreFields() {
        const section = document.querySelector('.more-fields-section');
        section.classList.toggle('collapsed');
    }
    
    editField(fieldName) {
        this.showToast(`Edit ${fieldName}`);
    }
    
    watchIssue() {
        this.showToast('Watching issue');
    }
    
    voteIssue() {
        this.showToast('Voted for issue');
    }
    
    shareIssue() {
        this.showToast('Share issue dialog');
    }
    
    toggleActionsMenu(button) {
        const menu = button.nextElementSibling;
        menu.classList.toggle('show');
    }
    
    close() {
        this.showToast('Close panel');
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
const issueDetailPanel = new IssueDetailPanel();
