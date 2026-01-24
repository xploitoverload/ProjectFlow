/**
 * Issue Detail Modal - JIRA-style comprehensive issue view
 * Features: Comments, Attachments, Activity Log, Watchers, Linked Issues, Time Tracking
 */

class IssueDetailModal {
    constructor() {
        this.currentIssue = null;
        this.isOpen = false;
        this.modal = null;
        this.activeTab = 'details';
        
        this.init();
    }

    init() {
        this.createModal();
        this.setupEventListeners();
    }

    createModal() {
        if (document.getElementById('issueDetailModal')) return;

        const modalHTML = `
            <div id="issueDetailModal" class="issue-modal" style="display: none;">
                <div class="issue-modal-backdrop"></div>
                <div class="issue-modal-container">
                    <div class="issue-modal-header">
                        <div class="issue-modal-breadcrumb">
                            <span class="issue-project-key"></span>
                            <span class="breadcrumb-separator">/</span>
                            <span class="issue-key"></span>
                        </div>
                        <div class="issue-modal-actions">
                            <button class="btn-icon" id="issueWatchBtn" title="Watch issue">
                                <i data-lucide="eye"></i>
                            </button>
                            <button class="btn-icon" id="issueShareBtn" title="Share">
                                <i data-lucide="share-2"></i>
                            </button>
                            <button class="btn-icon" id="issueMoreBtn" title="More actions">
                                <i data-lucide="more-horizontal"></i>
                            </button>
                            <button class="btn-icon" id="closeIssueModal" title="Close">
                                <i data-lucide="x"></i>
                            </button>
                        </div>
                    </div>
                    
                    <div class="issue-modal-body">
                        <!-- Left Panel: Main Content -->
                        <div class="issue-modal-main">
                            <!-- Issue Type & Summary -->
                            <div class="issue-summary-section">
                                <div class="issue-type-icon">
                                    <i data-lucide="bookmark"></i>
                                </div>
                                <h1 class="issue-summary" contenteditable="false" id="issueSummary"></h1>
                                <button class="btn-icon-sm" id="editSummaryBtn">
                                    <i data-lucide="edit-2"></i>
                                </button>
                            </div>

                            <!-- Tab Navigation -->
                            <div class="issue-tabs">
                                <button class="issue-tab active" data-tab="details">Details</button>
                                <button class="issue-tab" data-tab="comments">
                                    <span>Comments</span>
                                    <span class="tab-count" id="commentCount">0</span>
                                </button>
                                <button class="issue-tab" data-tab="attachments">
                                    <span>Attachments</span>
                                    <span class="tab-count" id="attachmentCount">0</span>
                                </button>
                                <button class="issue-tab" data-tab="activity">Activity</button>
                                <button class="issue-tab" data-tab="linked">
                                    <span>Linked Issues</span>
                                    <span class="tab-count" id="linkedCount">0</span>
                                </button>
                            </div>

                            <!-- Tab Content -->
                            <div class="issue-tab-content">
                                <!-- Details Tab -->
                                <div class="tab-panel active" data-panel="details">
                                    <div class="issue-section">
                                        <h3 class="section-title">Description</h3>
                                        <div class="issue-description" id="issueDescription"></div>
                                        <button class="btn btn-ghost btn-sm" id="editDescriptionBtn">
                                            <i data-lucide="edit-2"></i>
                                            Edit Description
                                        </button>
                                    </div>

                                    <div class="issue-section">
                                        <h3 class="section-title">Acceptance Criteria</h3>
                                        <div class="acceptance-criteria" id="acceptanceCriteria"></div>
                                    </div>

                                    <div class="issue-section">
                                        <h3 class="section-title">Sub-tasks</h3>
                                        <div class="subtasks-list" id="subtasksList"></div>
                                        <button class="btn btn-ghost btn-sm" id="createSubtaskBtn">
                                            <i data-lucide="plus"></i>
                                            Create Sub-task
                                        </button>
                                    </div>
                                </div>

                                <!-- Comments Tab -->
                                <div class="tab-panel" data-panel="comments">
                                    <div class="comment-composer">
                                        <textarea class="comment-input" id="newCommentInput" 
                                                  placeholder="Add a comment..." rows="3"></textarea>
                                        <div class="comment-actions">
                                            <button class="btn btn-primary btn-sm" id="postCommentBtn">Comment</button>
                                            <button class="btn btn-ghost btn-sm">Cancel</button>
                                        </div>
                                    </div>
                                    <div class="comments-list" id="commentsList"></div>
                                </div>

                                <!-- Attachments Tab -->
                                <div class="tab-panel" data-panel="attachments">
                                    <div class="attachment-dropzone" id="attachmentDropzone">
                                        <i data-lucide="upload" style="width: 48px; height: 48px; margin-bottom: 12px;"></i>
                                        <p>Drop files here or <span class="link">browse</span></p>
                                        <input type="file" id="fileInput" multiple style="display: none;">
                                    </div>
                                    <div class="attachments-list" id="attachmentsList"></div>
                                </div>

                                <!-- Activity Tab -->
                                <div class="tab-panel" data-panel="activity">
                                    <div class="activity-feed" id="activityFeed"></div>
                                </div>

                                <!-- Linked Issues Tab -->
                                <div class="tab-panel" data-panel="linked">
                                    <div class="linked-issues-section">
                                        <button class="btn btn-ghost btn-sm" id="linkIssueBtn">
                                            <i data-lucide="link-2"></i>
                                            Link Issue
                                        </button>
                                        <div class="linked-issues-list" id="linkedIssuesList"></div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Right Panel: Details -->
                        <div class="issue-modal-sidebar">
                            <!-- Status -->
                            <div class="sidebar-field">
                                <label class="field-label">Status</label>
                                <select class="field-select" id="issueStatus">
                                    <option value="To Do">To Do</option>
                                    <option value="In Progress">In Progress</option>
                                    <option value="In Review">In Review</option>
                                    <option value="Done">Done</option>
                                </select>
                            </div>

                            <!-- Assignee -->
                            <div class="sidebar-field">
                                <label class="field-label">Assignee</label>
                                <div class="field-value" id="assigneeField">
                                    <div class="user-select" id="assigneeSelect">
                                        <span class="placeholder">Unassigned</span>
                                    </div>
                                </div>
                            </div>

                            <!-- Reporter -->
                            <div class="sidebar-field">
                                <label class="field-label">Reporter</label>
                                <div class="field-value" id="reporterField"></div>
                            </div>

                            <!-- Priority -->
                            <div class="sidebar-field">
                                <label class="field-label">Priority</label>
                                <select class="field-select" id="issuePriority">
                                    <option value="Highest">🔺 Highest</option>
                                    <option value="High">⬆️ High</option>
                                    <option value="Medium">➖ Medium</option>
                                    <option value="Low">⬇️ Low</option>
                                    <option value="Lowest">🔻 Lowest</option>
                                </select>
                            </div>

                            <!-- Labels -->
                            <div class="sidebar-field">
                                <label class="field-label">Labels</label>
                                <div class="field-value">
                                    <div class="labels-container" id="labelsContainer"></div>
                                    <button class="btn-link btn-sm" id="addLabelBtn">+ Add label</button>
                                </div>
                            </div>

                            <!-- Sprint -->
                            <div class="sidebar-field">
                                <label class="field-label">Sprint</label>
                                <select class="field-select" id="issueSprint">
                                    <option value="">No Sprint</option>
                                </select>
                            </div>

                            <!-- Story Points -->
                            <div class="sidebar-field">
                                <label class="field-label">Story Points</label>
                                <input type="number" class="field-input" id="issueStoryPoints" 
                                       placeholder="0" min="0" max="100">
                            </div>

                            <!-- Due Date -->
                            <div class="sidebar-field">
                                <label class="field-label">Due Date</label>
                                <input type="date" class="field-input" id="issueDueDate">
                            </div>

                            <!-- Time Tracking -->
                            <div class="sidebar-field">
                                <label class="field-label">Time Tracking</label>
                                <div class="time-tracking">
                                    <div class="time-bar">
                                        <div class="time-bar-fill" id="timeBarFill" style="width: 0%"></div>
                                    </div>
                                    <div class="time-info">
                                        <span id="timeLogged">0h logged</span>
                                        <span id="timeRemaining">0h remaining</span>
                                    </div>
                                    <button class="btn-link btn-sm" id="logTimeBtn">Log time</button>
                                </div>
                            </div>

                            <!-- Watchers -->
                            <div class="sidebar-field">
                                <label class="field-label">Watchers</label>
                                <div class="watchers-list" id="watchersList"></div>
                                <button class="btn-link btn-sm" id="addWatcherBtn">+ Add watcher</button>
                            </div>

                            <!-- Created/Updated -->
                            <div class="sidebar-field">
                                <label class="field-label">Created</label>
                                <div class="field-value field-muted" id="createdInfo"></div>
                            </div>
                            <div class="sidebar-field">
                                <label class="field-label">Updated</label>
                                <div class="field-value field-muted" id="updatedInfo"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
        this.modal = document.getElementById('issueDetailModal');

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    setupEventListeners() {
        // Close modal
        document.getElementById('closeIssueModal')?.addEventListener('click', () => {
            this.close();
        });

        // Close on backdrop click
        this.modal?.querySelector('.issue-modal-backdrop')?.addEventListener('click', () => {
            this.close();
        });

        // Tab switching
        document.querySelectorAll('.issue-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // Edit summary
        document.getElementById('editSummaryBtn')?.addEventListener('click', () => {
            this.editSummary();
        });

        // Post comment
        document.getElementById('postCommentBtn')?.addEventListener('click', () => {
            this.postComment();
        });

        // File upload
        document.getElementById('fileInput')?.addEventListener('change', (e) => {
            this.handleFileUpload(e.target.files);
        });

        // Watch toggle
        document.getElementById('issueWatchBtn')?.addEventListener('click', () => {
            this.toggleWatch();
        });

        // Field changes
        this.setupFieldListeners();

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (this.isOpen && e.key === 'Escape') {
                this.close();
            }
        });
    }

    setupFieldListeners() {
        // Status change
        document.getElementById('issueStatus')?.addEventListener('change', (e) => {
            this.updateField('status', e.target.value);
        });

        // Priority change
        document.getElementById('issuePriority')?.addEventListener('change', (e) => {
            this.updateField('priority', e.target.value);
        });

        // Story points
        document.getElementById('issueStoryPoints')?.addEventListener('change', (e) => {
            this.updateField('story_points', e.target.value);
        });

        // Due date
        document.getElementById('issueDueDate')?.addEventListener('change', (e) => {
            this.updateField('due_date', e.target.value);
        });

        // Sprint
        document.getElementById('issueSprint')?.addEventListener('change', (e) => {
            this.updateField('sprint_id', e.target.value);
        });
    }

    async open(issueId) {
        this.currentIssue = await this.fetchIssue(issueId);
        if (!this.currentIssue) return;

        this.renderIssue();
        this.modal.style.display = 'block';
        this.isOpen = true;
        document.body.style.overflow = 'hidden';

        // Update URL without reload
        const url = new URL(window.location);
        url.searchParams.set('issue', issueId);
        window.history.pushState({}, '', url);
    }

    close() {
        this.modal.style.display = 'none';
        this.isOpen = false;
        this.currentIssue = null;
        document.body.style.overflow = '';

        // Remove issue from URL
        const url = new URL(window.location);
        url.searchParams.delete('issue');
        window.history.pushState({}, '', url);
    }

    async fetchIssue(issueId) {
        try {
            const response = await fetch(`/api/issues/${issueId}`);
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Failed to fetch issue:', error);
        }
        return null;
    }

    renderIssue() {
        if (!this.currentIssue) return;

        const issue = this.currentIssue;

        // Breadcrumb
        document.querySelector('.issue-project-key').textContent = issue.project?.key || 'PROJ';
        document.querySelector('.issue-key').textContent = issue.key;

        // Summary
        document.getElementById('issueSummary').textContent = issue.title;

        // Description
        document.getElementById('issueDescription').innerHTML = 
            issue.description || '<em class="text-muted">No description provided.</em>';

        // Sidebar fields
        document.getElementById('issueStatus').value = issue.status;
        document.getElementById('issuePriority').value = issue.priority || 'Medium';
        document.getElementById('issueStoryPoints').value = issue.story_points || '';
        document.getElementById('issueDueDate').value = issue.due_date || '';
        document.getElementById('issueSprint').value = issue.sprint_id || '';

        // Assignee
        this.renderAssignee(issue.assignee);

        // Reporter
        this.renderReporter(issue.reporter);

        // Labels
        this.renderLabels(issue.labels);

        // Time tracking
        this.renderTimeTracking(issue.time_logged, issue.time_estimated);

        // Watchers
        this.renderWatchers(issue.watchers);

        // Created/Updated
        document.getElementById('createdInfo').textContent = 
            this.formatDateTime(issue.created_at);
        document.getElementById('updatedInfo').textContent = 
            this.formatDateTime(issue.updated_at);

        // Comments
        this.renderComments(issue.comments);

        // Attachments
        this.renderAttachments(issue.attachments);

        // Activity
        this.renderActivity(issue.activity);

        // Linked issues
        this.renderLinkedIssues(issue.linked_issues);

        // Update counts
        document.getElementById('commentCount').textContent = issue.comments?.length || 0;
        document.getElementById('attachmentCount').textContent = issue.attachments?.length || 0;
        document.getElementById('linkedCount').textContent = issue.linked_issues?.length || 0;
    }

    renderAssignee(assignee) {
        const container = document.getElementById('assigneeSelect');
        if (assignee) {
            container.innerHTML = `
                <div class="user-avatar" style="background: ${assignee.avatar_color}">
                    ${assignee.username.substring(0, 2).toUpperCase()}
                </div>
                <span>${assignee.username}</span>
            `;
        } else {
            container.innerHTML = '<span class="placeholder">Unassigned</span>';
        }
    }

    renderReporter(reporter) {
        const container = document.getElementById('reporterField');
        if (reporter) {
            container.innerHTML = `
                <div class="user-avatar" style="background: ${reporter.avatar_color}">
                    ${reporter.username.substring(0, 2).toUpperCase()}
                </div>
                <span>${reporter.username}</span>
            `;
        }
    }

    renderLabels(labels) {
        const container = document.getElementById('labelsContainer');
        if (labels && labels.length > 0) {
            container.innerHTML = labels.map(label => `
                <span class="label-tag">${label}</span>
            `).join('');
        } else {
            container.innerHTML = '<span class="placeholder">None</span>';
        }
    }

    renderTimeTracking(logged, estimated) {
        const loggedHours = logged || 0;
        const estimatedHours = estimated || 0;
        const percentage = estimated ? (logged / estimated) * 100 : 0;

        document.getElementById('timeBarFill').style.width = `${Math.min(percentage, 100)}%`;
        document.getElementById('timeLogged').textContent = `${loggedHours}h logged`;
        document.getElementById('timeRemaining').textContent = 
            `${Math.max(0, estimatedHours - loggedHours)}h remaining`;
    }

    renderWatchers(watchers) {
        const container = document.getElementById('watchersList');
        if (watchers && watchers.length > 0) {
            container.innerHTML = watchers.map(watcher => `
                <div class="watcher-item">
                    <div class="user-avatar-sm" style="background: ${watcher.avatar_color}">
                        ${watcher.username.substring(0, 2).toUpperCase()}
                    </div>
                    <span>${watcher.username}</span>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<span class="placeholder">No watchers</span>';
        }
    }

    renderComments(comments) {
        const container = document.getElementById('commentsList');
        if (!comments || comments.length === 0) {
            container.innerHTML = '<p class="empty-state">No comments yet</p>';
            return;
        }

        container.innerHTML = comments.map(comment => `
            <div class="comment-item" data-comment-id="${comment.id}">
                <div class="comment-avatar" style="background: ${comment.author.avatar_color}">
                    ${comment.author.username.substring(0, 2).toUpperCase()}
                </div>
                <div class="comment-content">
                    <div class="comment-header">
                        <span class="comment-author">${comment.author.username}</span>
                        <span class="comment-time">${this.formatRelativeTime(comment.created_at)}</span>
                    </div>
                    <div class="comment-body">${comment.text}</div>
                </div>
            </div>
        `).join('');
    }

    renderAttachments(attachments) {
        const container = document.getElementById('attachmentsList');
        if (!attachments || attachments.length === 0) {
            container.innerHTML = '<p class="empty-state">No attachments</p>';
            return;
        }

        container.innerHTML = attachments.map(file => `
            <div class="attachment-item">
                <i data-lucide="file"></i>
                <div class="attachment-info">
                    <div class="attachment-name">${file.name}</div>
                    <div class="attachment-meta">${this.formatFileSize(file.size)} • ${this.formatRelativeTime(file.uploaded_at)}</div>
                </div>
                <a href="${file.url}" download class="btn-icon-sm">
                    <i data-lucide="download"></i>
                </a>
            </div>
        `).join('');

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    renderActivity(activity) {
        const container = document.getElementById('activityFeed');
        if (!activity || activity.length === 0) {
            container.innerHTML = '<p class="empty-state">No activity</p>';
            return;
        }

        container.innerHTML = activity.map(item => `
            <div class="activity-item">
                <div class="activity-icon ${item.type}">
                    <i data-lucide="${this.getActivityIcon(item.type)}"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-text">${item.text}</div>
                    <div class="activity-time">${this.formatRelativeTime(item.timestamp)}</div>
                </div>
            </div>
        `).join('');

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    renderLinkedIssues(linked) {
        const container = document.getElementById('linkedIssuesList');
        if (!linked || linked.length === 0) {
            container.innerHTML = '<p class="empty-state">No linked issues</p>';
            return;
        }

        container.innerHTML = linked.map(issue => `
            <div class="linked-issue-item" onclick="window.issueDetailModal.open('${issue.id}')">
                <i data-lucide="link-2"></i>
                <span class="linked-issue-key">${issue.key}</span>
                <span class="linked-issue-summary">${issue.title}</span>
                <span class="linked-issue-status">${issue.status}</span>
            </div>
        `).join('');

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    switchTab(tabName) {
        this.activeTab = tabName;

        // Update tab buttons
        document.querySelectorAll('.issue-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.tab === tabName);
        });

        // Update panels
        document.querySelectorAll('.tab-panel').forEach(panel => {
            panel.classList.toggle('active', panel.dataset.panel === tabName);
        });
    }

    async updateField(field, value) {
        if (!this.currentIssue) return;

        try {
            const response = await fetch(`/api/issues/${this.currentIssue.id}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ [field]: value })
            });

            if (response.ok) {
                window.notificationManager?.addNotification({
                    title: 'Issue Updated',
                    message: `${field} updated successfully`,
                    type: 'success'
                });
                
                // Refresh issue data
                await this.open(this.currentIssue.id);
            }
        } catch (error) {
            console.error('Failed to update issue:', error);
        }
    }

    async postComment() {
        const input = document.getElementById('newCommentInput');
        const text = input.value.trim();
        
        if (!text) return;

        try {
            const response = await fetch(`/api/issues/${this.currentIssue.id}/comments`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });

            if (response.ok) {
                input.value = '';
                await this.open(this.currentIssue.id);
            }
        } catch (error) {
            console.error('Failed to post comment:', error);
        }
    }

    async handleFileUpload(files) {
        const formData = new FormData();
        Array.from(files).forEach(file => {
            formData.append('files', file);
        });

        try {
            const response = await fetch(`/api/issues/${this.currentIssue.id}/attachments`, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                await this.open(this.currentIssue.id);
            }
        } catch (error) {
            console.error('Failed to upload files:', error);
        }
    }

    async toggleWatch() {
        // Toggle watch status
        try {
            const response = await fetch(`/api/issues/${this.currentIssue.id}/watch`, {
                method: 'POST'
            });

            if (response.ok) {
                await this.open(this.currentIssue.id);
            }
        } catch (error) {
            console.error('Failed to toggle watch:', error);
        }
    }

    // Utility methods
    formatDateTime(dateStr) {
        if (!dateStr) return 'N/A';
        const date = new Date(dateStr);
        return date.toLocaleString('en-US', { 
            month: 'short', 
            day: 'numeric', 
            year: 'numeric',
            hour: 'numeric',
            minute: '2-digit'
        });
    }

    formatRelativeTime(dateStr) {
        if (!dateStr) return '';
        const date = new Date(dateStr);
        const now = new Date();
        const diff = now - date;
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days > 7) return date.toLocaleDateString();
        if (days > 0) return `${days}d ago`;
        if (hours > 0) return `${hours}h ago`;
        if (minutes > 0) return `${minutes}m ago`;
        return 'Just now';
    }

    formatFileSize(bytes) {
        if (bytes < 1024) return `${bytes} B`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    }

    getActivityIcon(type) {
        const icons = {
            'status_change': 'arrow-right',
            'comment': 'message-square',
            'assignment': 'user',
            'update': 'edit-2',
            'attachment': 'paperclip'
        };
        return icons[type] || 'activity';
    }

    editSummary() {
        const summaryEl = document.getElementById('issueSummary');
        summaryEl.contentEditable = true;
        summaryEl.focus();
        
        const saveEdit = () => {
            summaryEl.contentEditable = false;
            this.updateField('title', summaryEl.textContent.trim());
        };

        summaryEl.addEventListener('blur', saveEdit, { once: true });
        summaryEl.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                saveEdit();
            }
        }, { once: true });
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.issueDetailModal = new IssueDetailModal();
});

// Global function to open issue modal
function openIssueDetail(issueId) {
    window.issueDetailModal?.open(issueId);
}
