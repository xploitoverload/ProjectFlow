/**
 * Collaboration Features Suite
 * Features: Comments (threaded, markdown), Mentions (@username), 
 * Notifications (real-time WebSocket), Activity Feed, Watchers, Team Management
 */

class CollaborationSystem {
    constructor() {
        this.currentUser = { id: 1, name: 'John Doe', avatar: 'JD' };
        this.comments = [];
        this.notifications = [];
        this.watchers = [];
        this.teamMembers = [];
        this.mentions = [];
        this.ws = null;
        this.unreadNotifications = 0;
        
        this.init();
    }

    async init() {
        await this.loadData();
        this.setupWebSocket();
        this.setupMentions();
        console.log('CollaborationSystem initialized');
    }

    async loadData() {
        try {
            const [comments, notifications, watchers, team] = await Promise.all([
                fetch('/api/comments').then(r => r.json()),
                fetch('/api/notifications').then(r => r.json()),
                fetch('/api/watchers').then(r => r.json()),
                fetch('/api/team').then(r => r.json())
            ]);
            
            this.comments = comments;
            this.notifications = notifications;
            this.watchers = watchers;
            this.teamMembers = team;
            this.unreadNotifications = notifications.filter(n => !n.read).length;
        } catch (error) {
            console.error('Failed to load collaboration data:', error);
            this.loadMockData();
        }
    }

    loadMockData() {
        this.comments = [
            {
                id: 1,
                issueKey: 'PROJ-123',
                author: { id: 1, name: 'John Doe', avatar: 'JD' },
                text: 'This looks great! 👍',
                created: '2024-01-20T10:30:00',
                updated: null,
                replies: [],
                mentions: []
            },
            {
                id: 2,
                issueKey: 'PROJ-123',
                author: { id: 2, name: 'Jane Smith', avatar: 'JS' },
                text: '@JohnDoe Can you review this implementation?',
                created: '2024-01-20T11:00:00',
                updated: null,
                replies: [
                    {
                        id: 3,
                        author: { id: 1, name: 'John Doe', avatar: 'JD' },
                        text: 'Sure, will do!',
                        created: '2024-01-20T11:15:00'
                    }
                ],
                mentions: ['JohnDoe']
            }
        ];

        this.notifications = [
            {
                id: 1,
                type: 'mention',
                title: 'Jane Smith mentioned you in PROJ-123',
                message: 'Can you review this implementation?',
                link: '/issue/PROJ-123',
                created: '2024-01-20T11:00:00',
                read: false,
                icon: 'at-sign'
            },
            {
                id: 2,
                type: 'comment',
                title: 'New comment on PROJ-124',
                message: 'Bob added a comment',
                link: '/issue/PROJ-124',
                created: '2024-01-20T09:30:00',
                read: false,
                icon: 'message-circle'
            },
            {
                id: 3,
                type: 'assignment',
                title: 'PROJ-125 assigned to you',
                message: 'Alice assigned this issue to you',
                link: '/issue/PROJ-125',
                created: '2024-01-19T15:00:00',
                read: true,
                icon: 'user-check'
            }
        ];

        this.watchers = [
            { id: 1, name: 'John Doe', avatar: 'JD', watching: true },
            { id: 2, name: 'Jane Smith', avatar: 'JS', watching: true },
            { id: 3, name: 'Bob Wilson', avatar: 'BW', watching: false }
        ];

        this.teamMembers = [
            { id: 1, name: 'John Doe', avatar: 'JD', role: 'Lead Developer', status: 'online' },
            { id: 2, name: 'Jane Smith', avatar: 'JS', role: 'Developer', status: 'online' },
            { id: 3, name: 'Bob Wilson', avatar: 'BW', role: 'Designer', status: 'away' },
            { id: 4, name: 'Alice Johnson', avatar: 'AJ', role: 'Product Manager', status: 'offline' }
        ];

        this.unreadNotifications = 2;
    }

    // ================== COMMENTS SYSTEM ==================

    renderCommentsSection(container, issueKey) {
        const issueComments = this.comments.filter(c => c.issueKey === issueKey);
        
        const html = `
            <div class="comments-section" id="commentsSection">
                <div class="comments-header">
                    <h3>Comments (${issueComments.length})</h3>
                    <div class="comments-actions">
                        <button class="btn-icon" onclick="collaboration.sortComments('oldest')" title="Oldest first">
                            <i data-lucide="arrow-up"></i>
                        </button>
                        <button class="btn-icon active" onclick="collaboration.sortComments('newest')" title="Newest first">
                            <i data-lucide="arrow-down"></i>
                        </button>
                    </div>
                </div>

                <!-- Comment Input -->
                <div class="comment-input-container">
                    <div class="user-avatar">${this.currentUser.avatar}</div>
                    <div class="comment-input-box">
                        <textarea class="comment-textarea" 
                                  id="commentInput"
                                  placeholder="Add a comment... Use @ to mention someone"
                                  oninput="collaboration.handleCommentInput(event)"
                                  onkeydown="collaboration.handleCommentKeydown(event)"></textarea>
                        <div class="comment-input-footer">
                            <div class="formatting-toolbar">
                                <button class="btn-icon-sm" onclick="collaboration.insertMarkdown('**', '**')" title="Bold">
                                    <i data-lucide="bold"></i>
                                </button>
                                <button class="btn-icon-sm" onclick="collaboration.insertMarkdown('*', '*')" title="Italic">
                                    <i data-lucide="italic"></i>
                                </button>
                                <button class="btn-icon-sm" onclick="collaboration.insertMarkdown('`', '`')" title="Code">
                                    <i data-lucide="code"></i>
                                </button>
                                <button class="btn-icon-sm" onclick="collaboration.insertMarkdown('- ', '')" title="List">
                                    <i data-lucide="list"></i>
                                </button>
                                <button class="btn-icon-sm" onclick="collaboration.insertMarkdown('> ', '')" title="Quote">
                                    <i data-lucide="quote"></i>
                                </button>
                            </div>
                            <div class="input-actions">
                                <button class="btn-text" onclick="collaboration.cancelComment()">Cancel</button>
                                <button class="btn-primary" onclick="collaboration.saveComment('${issueKey}')">
                                    Comment
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Comments List -->
                <div class="comments-list" id="commentsList">
                    ${this.renderComments(issueComments)}
                </div>

                <!-- Mention Suggestions -->
                <div class="mention-suggestions" id="mentionSuggestions" style="display: none;"></div>
            </div>
        `;

        container.innerHTML = html;
        if (window.lucide) lucide.createIcons();
    }

    renderComments(comments) {
        if (comments.length === 0) {
            return `
                <div class="empty-state">
                    <i data-lucide="message-circle"></i>
                    <p>No comments yet</p>
                    <span>Be the first to comment</span>
                </div>
            `;
        }

        return comments.map(comment => this.renderComment(comment)).join('');
    }

    renderComment(comment) {
        const isAuthor = comment.author.id === this.currentUser.id;
        const timeAgo = this.getTimeAgo(comment.created);
        const edited = comment.updated ? '(edited)' : '';

        return `
            <div class="comment-item" data-comment-id="${comment.id}">
                <div class="comment-avatar">${comment.author.avatar}</div>
                <div class="comment-content">
                    <div class="comment-header">
                        <div class="comment-author-info">
                            <span class="comment-author">${comment.author.name}</span>
                            <span class="comment-time">${timeAgo} ${edited}</span>
                        </div>
                        ${isAuthor ? `
                            <div class="comment-actions">
                                <button class="btn-icon-sm" onclick="collaboration.editComment(${comment.id})" title="Edit">
                                    <i data-lucide="edit-2"></i>
                                </button>
                                <button class="btn-icon-sm" onclick="collaboration.deleteComment(${comment.id})" title="Delete">
                                    <i data-lucide="trash-2"></i>
                                </button>
                            </div>
                        ` : ''}
                    </div>
                    <div class="comment-text">${this.renderMarkdown(comment.text)}</div>
                    <div class="comment-footer">
                        <button class="btn-text-sm" onclick="collaboration.replyToComment(${comment.id})">
                            <i data-lucide="corner-up-left"></i>
                            Reply
                        </button>
                        ${comment.mentions.length > 0 ? `
                            <span class="mentions-indicator">
                                <i data-lucide="at-sign"></i>
                                ${comment.mentions.length}
                            </span>
                        ` : ''}
                    </div>

                    <!-- Replies -->
                    ${comment.replies && comment.replies.length > 0 ? `
                        <div class="comment-replies">
                            ${comment.replies.map(reply => this.renderReply(reply)).join('')}
                        </div>
                    ` : ''}

                    <!-- Reply Input (hidden by default) -->
                    <div class="reply-input" id="replyInput_${comment.id}" style="display: none;">
                        <div class="comment-input-box">
                            <textarea class="comment-textarea" 
                                      placeholder="Write a reply..."
                                      oninput="collaboration.handleCommentInput(event)"></textarea>
                            <div class="comment-input-footer">
                                <div class="input-actions">
                                    <button class="btn-text" onclick="collaboration.cancelReply(${comment.id})">Cancel</button>
                                    <button class="btn-primary" onclick="collaboration.saveReply(${comment.id})">Reply</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderReply(reply) {
        const timeAgo = this.getTimeAgo(reply.created);
        return `
            <div class="reply-item">
                <div class="reply-avatar">${reply.author.avatar}</div>
                <div class="reply-content">
                    <div class="reply-header">
                        <span class="reply-author">${reply.author.name}</span>
                        <span class="reply-time">${timeAgo}</span>
                    </div>
                    <div class="reply-text">${this.renderMarkdown(reply.text)}</div>
                </div>
            </div>
        `;
    }

    renderMarkdown(text) {
        // Simple markdown rendering
        return text
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.+?)\*/g, '<em>$1</em>')
            .replace(/`(.+?)`/g, '<code>$1</code>')
            .replace(/@(\w+)/g, '<span class="mention">@$1</span>')
            .replace(/\n/g, '<br>');
    }

    handleCommentInput(event) {
        const textarea = event.target;
        const text = textarea.value;
        const cursorPos = textarea.selectionStart;

        // Check for @ mention
        const beforeCursor = text.substring(0, cursorPos);
        const mentionMatch = beforeCursor.match(/@(\w*)$/);

        if (mentionMatch) {
            const query = mentionMatch[1].toLowerCase();
            this.showMentionSuggestions(textarea, query);
        } else {
            this.hideMentionSuggestions();
        }
    }

    showMentionSuggestions(textarea, query) {
        const suggestions = this.teamMembers.filter(member => 
            member.name.toLowerCase().includes(query)
        );

        if (suggestions.length === 0) {
            this.hideMentionSuggestions();
            return;
        }

        const container = document.getElementById('mentionSuggestions');
        container.innerHTML = suggestions.map((member, index) => `
            <div class="mention-suggestion ${index === 0 ? 'selected' : ''}" 
                 data-name="${member.name}"
                 onclick="collaboration.insertMention('${member.name}', this)">
                <div class="avatar-xs">${member.avatar}</div>
                <div class="mention-info">
                    <div class="mention-name">${member.name}</div>
                    <div class="mention-role">${member.role}</div>
                </div>
            </div>
        `).join('');

        // Position below textarea
        const rect = textarea.getBoundingClientRect();
        container.style.display = 'block';
        container.style.top = rect.bottom + 'px';
        container.style.left = rect.left + 'px';

        if (window.lucide) lucide.createIcons();
    }

    hideMentionSuggestions() {
        document.getElementById('mentionSuggestions').style.display = 'none';
    }

    insertMention(name, element) {
        const textarea = document.getElementById('commentInput');
        const text = textarea.value;
        const cursorPos = textarea.selectionStart;

        // Replace @query with @Name
        const beforeCursor = text.substring(0, cursorPos);
        const afterCursor = text.substring(cursorPos);
        const replaced = beforeCursor.replace(/@\w*$/, `@${name.replace(' ', '')} `);

        textarea.value = replaced + afterCursor;
        textarea.selectionStart = textarea.selectionEnd = replaced.length;
        textarea.focus();

        this.hideMentionSuggestions();
    }

    handleCommentKeydown(event) {
        const suggestions = document.getElementById('mentionSuggestions');
        if (suggestions.style.display === 'none') return;

        const selected = suggestions.querySelector('.mention-suggestion.selected');
        
        if (event.key === 'ArrowDown') {
            event.preventDefault();
            const next = selected?.nextElementSibling || suggestions.firstElementChild;
            selected?.classList.remove('selected');
            next?.classList.add('selected');
        } else if (event.key === 'ArrowUp') {
            event.preventDefault();
            const prev = selected?.previousElementSibling || suggestions.lastElementChild;
            selected?.classList.remove('selected');
            prev?.classList.add('selected');
        } else if (event.key === 'Enter' && selected) {
            event.preventDefault();
            const name = selected.dataset.name;
            this.insertMention(name, selected);
        } else if (event.key === 'Escape') {
            this.hideMentionSuggestions();
        }
    }

    insertMarkdown(before, after) {
        const textarea = document.getElementById('commentInput');
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const text = textarea.value;
        const selectedText = text.substring(start, end);

        textarea.value = text.substring(0, start) + before + selectedText + after + text.substring(end);
        textarea.selectionStart = start + before.length;
        textarea.selectionEnd = end + before.length;
        textarea.focus();
    }

    async saveComment(issueKey) {
        const textarea = document.getElementById('commentInput');
        const text = textarea.value.trim();

        if (!text) return;

        const comment = {
            id: Date.now(),
            issueKey,
            author: this.currentUser,
            text,
            created: new Date().toISOString(),
            updated: null,
            replies: [],
            mentions: this.extractMentions(text)
        };

        this.comments.push(comment);
        textarea.value = '';

        // Send notification to mentioned users
        comment.mentions.forEach(mention => {
            this.sendMentionNotification(mention, issueKey, text);
        });

        // Re-render
        const container = document.getElementById('commentsList');
        container.innerHTML = this.renderComments(this.comments.filter(c => c.issueKey === issueKey));
        if (window.lucide) lucide.createIcons();
    }

    extractMentions(text) {
        const mentions = text.match(/@(\w+)/g) || [];
        return mentions.map(m => m.substring(1));
    }

    sendMentionNotification(username, issueKey, text) {
        const notification = {
            id: Date.now(),
            type: 'mention',
            title: `${this.currentUser.name} mentioned you in ${issueKey}`,
            message: text.substring(0, 100),
            link: `/issue/${issueKey}`,
            created: new Date().toISOString(),
            read: false,
            icon: 'at-sign'
        };

        this.notifications.unshift(notification);
        this.unreadNotifications++;
        this.broadcastNotification(notification);
    }

    replyToComment(commentId) {
        const replyInput = document.getElementById(`replyInput_${commentId}`);
        replyInput.style.display = 'block';
        replyInput.querySelector('textarea').focus();
    }

    cancelReply(commentId) {
        const replyInput = document.getElementById(`replyInput_${commentId}`);
        replyInput.style.display = 'none';
        replyInput.querySelector('textarea').value = '';
    }

    saveReply(commentId) {
        const replyInput = document.getElementById(`replyInput_${commentId}`);
        const textarea = replyInput.querySelector('textarea');
        const text = textarea.value.trim();

        if (!text) return;

        const comment = this.comments.find(c => c.id === commentId);
        if (!comment) return;

        const reply = {
            id: Date.now(),
            author: this.currentUser,
            text,
            created: new Date().toISOString()
        };

        comment.replies.push(reply);
        this.cancelReply(commentId);

        // Re-render
        const container = document.getElementById('commentsList');
        container.innerHTML = this.renderComments(this.comments.filter(c => c.issueKey === comment.issueKey));
        if (window.lucide) lucide.createIcons();
    }

    editComment(commentId) {
        alert(`Edit comment ${commentId}`);
    }

    deleteComment(commentId) {
        if (confirm('Delete this comment?')) {
            this.comments = this.comments.filter(c => c.id !== commentId);
            const container = document.getElementById('commentsList');
            if (container) {
                container.innerHTML = this.renderComments(this.comments);
                if (window.lucide) lucide.createIcons();
            }
        }
    }

    cancelComment() {
        document.getElementById('commentInput').value = '';
    }

    sortComments(order) {
        // Toggle active state
        document.querySelectorAll('.comments-actions .btn-icon').forEach(btn => {
            btn.classList.remove('active');
        });
        event.target.closest('.btn-icon').classList.add('active');

        // Sort
        if (order === 'oldest') {
            this.comments.sort((a, b) => new Date(a.created) - new Date(b.created));
        } else {
            this.comments.sort((a, b) => new Date(b.created) - new Date(a.created));
        }

        // Re-render
        const container = document.getElementById('commentsList');
        if (container) {
            container.innerHTML = this.renderComments(this.comments);
            if (window.lucide) lucide.createIcons();
        }
    }

    // ================== NOTIFICATIONS SYSTEM ==================

    setupWebSocket() {
        // WebSocket connection for real-time notifications
        try {
            this.ws = new WebSocket(`ws://${window.location.host}/ws/notifications`);
            
            this.ws.onopen = () => {
                console.log('WebSocket connected');
            };

            this.ws.onmessage = (event) => {
                const notification = JSON.parse(event.data);
                this.handleIncomingNotification(notification);
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };

            this.ws.onclose = () => {
                console.log('WebSocket closed, reconnecting...');
                setTimeout(() => this.setupWebSocket(), 5000);
            };
        } catch (error) {
            console.error('WebSocket not available:', error);
        }
    }

    handleIncomingNotification(notification) {
        this.notifications.unshift(notification);
        this.unreadNotifications++;

        // Update badge
        this.updateNotificationBadge();

        // Show toast notification
        this.showToastNotification(notification);

        // Play sound
        this.playNotificationSound();
    }

    broadcastNotification(notification) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(notification));
        }
    }

    showToastNotification(notification) {
        const toast = document.createElement('div');
        toast.className = 'notification-toast';
        toast.innerHTML = `
            <div class="toast-icon">
                <i data-lucide="${notification.icon}"></i>
            </div>
            <div class="toast-content">
                <div class="toast-title">${notification.title}</div>
                <div class="toast-message">${notification.message}</div>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i data-lucide="x"></i>
            </button>
        `;

        document.body.appendChild(toast);
        if (window.lucide) lucide.createIcons();

        // Auto remove after 5 seconds
        setTimeout(() => toast.remove(), 5000);
    }

    playNotificationSound() {
        const audio = new Audio('/static/sounds/notification.mp3');
        audio.volume = 0.3;
        audio.play().catch(e => console.log('Audio play failed:', e));
    }

    updateNotificationBadge() {
        const badge = document.getElementById('notificationBadge');
        if (badge) {
            badge.textContent = this.unreadNotifications;
            badge.style.display = this.unreadNotifications > 0 ? 'flex' : 'none';
        }
    }

    markNotificationAsRead(id) {
        const notification = this.notifications.find(n => n.id === id);
        if (notification && !notification.read) {
            notification.read = true;
            this.unreadNotifications = Math.max(0, this.unreadNotifications - 1);
            this.updateNotificationBadge();
        }
    }

    markAllNotificationsAsRead() {
        this.notifications.forEach(n => n.read = true);
        this.unreadNotifications = 0;
        this.updateNotificationBadge();
    }

    // ================== WATCHERS SYSTEM ==================

    renderWatchersPanel(container, issueKey) {
        const html = `
            <div class="watchers-panel">
                <div class="panel-header">
                    <h4>Watchers</h4>
                    <button class="btn-text-sm" onclick="collaboration.toggleWatch('${issueKey}')">
                        ${this.isWatching(issueKey) ? 'Stop watching' : 'Start watching'}
                    </button>
                </div>
                <div class="watchers-list">
                    ${this.watchers.filter(w => w.watching).map(watcher => `
                        <div class="watcher-item">
                            <div class="avatar-sm">${watcher.avatar}</div>
                            <span class="watcher-name">${watcher.name}</span>
                            ${watcher.id === this.currentUser.id ? `
                                <button class="btn-icon-sm" onclick="collaboration.removeWatcher(${watcher.id})">
                                    <i data-lucide="x"></i>
                                </button>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>
                <button class="btn-text" onclick="collaboration.addWatcher('${issueKey}')">
                    <i data-lucide="plus"></i>
                    Add watcher
                </button>
            </div>
        `;

        container.innerHTML = html;
        if (window.lucide) lucide.createIcons();
    }

    isWatching(issueKey) {
        const watcher = this.watchers.find(w => w.id === this.currentUser.id);
        return watcher?.watching || false;
    }

    toggleWatch(issueKey) {
        const watcher = this.watchers.find(w => w.id === this.currentUser.id);
        if (watcher) {
            watcher.watching = !watcher.watching;
        }
        // Re-render
        const container = document.querySelector('.watchers-panel').parentElement;
        this.renderWatchersPanel(container, issueKey);
    }

    addWatcher(issueKey) {
        alert('Add watcher');
    }

    removeWatcher(watcherId) {
        const watcher = this.watchers.find(w => w.id === watcherId);
        if (watcher) {
            watcher.watching = false;
        }
        // Re-render
        const container = document.querySelector('.watchers-panel').parentElement;
        this.renderWatchersPanel(container, issueKey);
    }

    // ================== TEAM MANAGEMENT ==================

    renderTeamPanel(container) {
        const html = `
            <div class="team-panel">
                <div class="panel-header">
                    <h4>Team Members</h4>
                    <button class="btn-primary-sm" onclick="collaboration.inviteTeamMember()">
                        <i data-lucide="user-plus"></i>
                        Invite
                    </button>
                </div>
                <div class="team-list">
                    ${this.teamMembers.map(member => `
                        <div class="team-member-item">
                            <div class="member-avatar-status">
                                <div class="avatar-md">${member.avatar}</div>
                                <span class="status-indicator status-${member.status}"></span>
                            </div>
                            <div class="member-details">
                                <div class="member-name">${member.name}</div>
                                <div class="member-role">${member.role}</div>
                            </div>
                            <button class="btn-icon-sm" onclick="collaboration.memberActions(${member.id})">
                                <i data-lucide="more-vertical"></i>
                            </button>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        container.innerHTML = html;
        if (window.lucide) lucide.createIcons();
    }

    inviteTeamMember() {
        alert('Invite team member');
    }

    memberActions(memberId) {
        alert(`Member actions for ${memberId}`);
    }

    // ================== ACTIVITY FEED ==================

    renderActivityFeed(container, issueKey) {
        const activities = [
            { type: 'comment', user: 'John Doe', action: 'added a comment', time: '2 hours ago', icon: 'message-circle' },
            { type: 'status', user: 'Jane Smith', action: 'changed status to In Progress', time: '3 hours ago', icon: 'git-branch' },
            { type: 'assignment', user: 'Bob Wilson', action: 'assigned to John Doe', time: '5 hours ago', icon: 'user-check' }
        ];

        const html = `
            <div class="activity-feed">
                <h4>Activity</h4>
                <div class="activity-timeline">
                    ${activities.map(activity => `
                        <div class="activity-item">
                            <div class="activity-icon">
                                <i data-lucide="${activity.icon}"></i>
                            </div>
                            <div class="activity-content">
                                <div class="activity-text">
                                    <strong>${activity.user}</strong> ${activity.action}
                                </div>
                                <div class="activity-time">${activity.time}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        container.innerHTML = html;
        if (window.lucide) lucide.createIcons();
    }

    // ================== UTILITIES ==================

    getTimeAgo(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const seconds = Math.floor((now - date) / 1000);

        if (seconds < 60) return 'just now';
        if (seconds < 3600) return `${Math.floor(seconds / 60)} minutes ago`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`;
        if (seconds < 2592000) return `${Math.floor(seconds / 86400)} days ago`;
        return date.toLocaleDateString();
    }

    setupMentions() {
        // Setup @ mention trigger globally
        document.addEventListener('keydown', (e) => {
            if (e.key === '@' && e.target.matches('textarea, input[type="text"]')) {
                // Mentions will be handled by handleCommentInput
            }
        });
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.collaboration = new CollaborationSystem();
});
