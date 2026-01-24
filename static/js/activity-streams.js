/**
 * Activity Streams System
 * Real-time activity feed, threaded comments, reactions, @mentions
 */

class ActivityStreams {
    constructor() {
        this.activities = [];
        this.filter = 'all';
        this.ws = null;
        
        this.init();
    }

    init() {
        this.createPanel();
        this.setupEventListeners();
        this.connectWebSocket();
    }

    createPanel() {
        const panelHTML = `
            <div id="activityPanel" class="activity-panel" style="display: none;">
                <div class="activity-header">
                    <h3>Activity Stream</h3>
                    <div class="activity-filters">
                        <button class="filter-btn active" data-filter="all">All</button>
                        <button class="filter-btn" data-filter="issues">Issues</button>
                        <button class="filter-btn" data-filter="comments">Comments</button>
                        <button class="filter-btn" data-filter="changes">Changes</button>
                    </div>
                    <button class="btn-icon-sm" id="closeActivityPanel">
                        <i data-lucide="x"></i>
                    </button>
                </div>

                <div class="activity-content" id="activityContent">
                    <!-- Populated by JS -->
                </div>

                <div class="activity-input" id="activityInput" style="display: none;">
                    <div class="input-header">
                        <span id="replyToUser"></span>
                        <button class="btn-icon-sm" onclick="activityStreams.cancelReply()">
                            <i data-lucide="x"></i>
                        </button>
                    </div>
                    <div class="input-wrapper">
                        <textarea class="activity-textarea" id="commentText" 
                                  placeholder="Add a comment..." rows="3"></textarea>
                        <div class="input-actions">
                            <button class="btn btn-ghost btn-sm" id="emojiPickerBtn">
                                <i data-lucide="smile"></i>
                            </button>
                            <button class="btn btn-primary btn-sm" id="postCommentBtn">
                                <i data-lucide="send"></i>
                                Post
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Emoji Picker -->
            <div id="emojiPicker" class="emoji-picker" style="display: none;">
                <div class="emoji-grid">
                    ${['👍', '❤️', '😊', '😂', '🎉', '🚀', '👀', '🔥'].map(emoji => `
                        <button class="emoji-btn" onclick="activityStreams.insertEmoji('${emoji}')">${emoji}</button>
                    `).join('')}
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', panelHTML);

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    setupEventListeners() {
        document.getElementById('closeActivityPanel')?.addEventListener('click', () => {
            this.closePanel();
        });

        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.filter = e.target.dataset.filter;
                this.renderActivities();
            });
        });

        document.getElementById('postCommentBtn')?.addEventListener('click', () => {
            this.postComment();
        });

        document.getElementById('emojiPickerBtn')?.addEventListener('click', () => {
            this.toggleEmojiPicker();
        });

        // Auto-resize textarea
        document.getElementById('commentText')?.addEventListener('input', (e) => {
            e.target.style.height = 'auto';
            e.target.style.height = e.target.scrollHeight + 'px';
        });
    }

    openPanel(issueId = null) {
        document.getElementById('activityPanel').style.display = 'flex';
        this.issueId = issueId;
        this.loadActivities();
        
        if (issueId) {
            document.getElementById('activityInput').style.display = 'block';
        }
    }

    closePanel() {
        document.getElementById('activityPanel').style.display = 'none';
    }

    async loadActivities() {
        try {
            const url = this.issueId 
                ? `/api/issues/${this.issueId}/activity`
                : '/api/activity';
            
            const response = await fetch(url);
            if (response.ok) {
                this.activities = await response.json();
                this.renderActivities();
            }
        } catch (error) {
            console.error('Failed to load activities:', error);
        }
    }

    renderActivities() {
        const container = document.getElementById('activityContent');
        
        let filtered = this.activities;
        if (this.filter !== 'all') {
            filtered = this.activities.filter(a => a.type === this.filter);
        }

        if (filtered.length === 0) {
            container.innerHTML = `
                <div class="empty-activity">
                    <i data-lucide="activity"></i>
                    <p>No activity yet</p>
                </div>
            `;
            if (window.lucide) lucide.createIcons();
            return;
        }

        container.innerHTML = filtered.map(activity => this.renderActivity(activity)).join('');

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    renderActivity(activity) {
        const icon = this.getActivityIcon(activity.type);
        const color = this.getActivityColor(activity.type);

        if (activity.type === 'comment') {
            return this.renderComment(activity);
        }

        return `
            <div class="activity-item">
                <div class="activity-avatar ${color}">
                    <i data-lucide="${icon}"></i>
                </div>
                <div class="activity-body">
                    <div class="activity-header">
                        <span class="activity-user">${activity.user}</span>
                        <span class="activity-action">${activity.action}</span>
                        ${activity.issue ? `<span class="activity-issue">${activity.issue}</span>` : ''}
                    </div>
                    <div class="activity-time">${this.formatTime(activity.timestamp)}</div>
                    ${activity.changes ? this.renderChanges(activity.changes) : ''}
                </div>
            </div>
        `;
    }

    renderComment(comment) {
        const replies = comment.replies || [];
        
        return `
            <div class="comment-item" data-comment-id="${comment.id}">
                <div class="comment-avatar">
                    ${this.getInitials(comment.user)}
                </div>
                <div class="comment-body">
                    <div class="comment-header">
                        <span class="comment-user">${comment.user}</span>
                        <span class="comment-time">${this.formatTime(comment.timestamp)}</span>
                    </div>
                    <div class="comment-text">${this.parseComment(comment.text)}</div>
                    <div class="comment-actions">
                        <button class="comment-action-btn" onclick="activityStreams.toggleReactions('${comment.id}')">
                            <i data-lucide="smile"></i>
                            React
                        </button>
                        <button class="comment-action-btn" onclick="activityStreams.replyToComment('${comment.id}', '${comment.user}')">
                            <i data-lucide="message-circle"></i>
                            Reply
                        </button>
                        ${comment.userId === this.currentUserId ? `
                            <button class="comment-action-btn" onclick="activityStreams.editComment('${comment.id}')">
                                <i data-lucide="edit-2"></i>
                                Edit
                            </button>
                            <button class="comment-action-btn danger" onclick="activityStreams.deleteComment('${comment.id}')">
                                <i data-lucide="trash-2"></i>
                                Delete
                            </button>
                        ` : ''}
                    </div>
                    
                    ${comment.reactions && comment.reactions.length > 0 ? `
                        <div class="comment-reactions">
                            ${this.renderReactions(comment.reactions)}
                        </div>
                    ` : ''}

                    <div class="reaction-picker" id="reactions-${comment.id}" style="display: none;">
                        ${['👍', '❤️', '😊', '😂', '🎉', '🚀'].map(emoji => `
                            <button class="reaction-btn" onclick="activityStreams.addReaction('${comment.id}', '${emoji}')">
                                ${emoji}
                            </button>
                        `).join('')}
                    </div>

                    ${replies.length > 0 ? `
                        <div class="comment-replies">
                            ${replies.map(reply => this.renderReply(reply)).join('')}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    renderReply(reply) {
        return `
            <div class="reply-item">
                <div class="reply-avatar">
                    ${this.getInitials(reply.user)}
                </div>
                <div class="reply-body">
                    <div class="reply-header">
                        <span class="reply-user">${reply.user}</span>
                        <span class="reply-time">${this.formatTime(reply.timestamp)}</span>
                    </div>
                    <div class="reply-text">${this.parseComment(reply.text)}</div>
                </div>
            </div>
        `;
    }

    renderReactions(reactions) {
        const grouped = {};
        reactions.forEach(r => {
            if (!grouped[r.emoji]) {
                grouped[r.emoji] = [];
            }
            grouped[r.emoji].push(r.user);
        });

        return Object.entries(grouped).map(([emoji, users]) => `
            <button class="reaction-badge" title="${users.join(', ')}">
                ${emoji} ${users.length}
            </button>
        `).join('');
    }

    renderChanges(changes) {
        return `
            <div class="activity-changes">
                ${changes.map(change => `
                    <div class="change-item">
                        <span class="change-field">${change.field}</span>
                        <span class="change-arrow">→</span>
                        <span class="change-value">${change.to}</span>
                    </div>
                `).join('')}
            </div>
        `;
    }

    parseComment(text) {
        // Parse @mentions
        text = text.replace(/@(\w+)/g, '<span class="mention">@$1</span>');
        // Parse links
        text = text.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
        return text;
    }

    getActivityIcon(type) {
        const icons = {
            'created': 'plus-circle',
            'updated': 'edit',
            'status': 'git-branch',
            'assigned': 'user-check',
            'comment': 'message-square',
            'deleted': 'trash-2'
        };
        return icons[type] || 'circle';
    }

    getActivityColor(type) {
        const colors = {
            'created': 'green',
            'updated': 'blue',
            'status': 'purple',
            'assigned': 'orange',
            'comment': 'gray',
            'deleted': 'red'
        };
        return colors[type] || 'gray';
    }

    getInitials(name) {
        return name.split(' ').map(n => n[0]).join('').toUpperCase();
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
        if (diff < 604800000) return `${Math.floor(diff / 86400000)}d ago`;
        return date.toLocaleDateString();
    }

    async postComment() {
        const text = document.getElementById('commentText').value;
        if (!text.trim()) return;

        try {
            const response = await fetch(`/api/issues/${this.issueId}/comments`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    text,
                    parentId: this.replyToCommentId 
                })
            });

            if (response.ok) {
                document.getElementById('commentText').value = '';
                this.cancelReply();
                this.loadActivities();
            }
        } catch (error) {
            console.error('Failed to post comment:', error);
        }
    }

    replyToComment(commentId, userName) {
        this.replyToCommentId = commentId;
        document.getElementById('replyToUser').textContent = `Replying to ${userName}`;
        document.getElementById('activityInput').querySelector('.input-header').style.display = 'flex';
        document.getElementById('commentText').focus();
    }

    cancelReply() {
        this.replyToCommentId = null;
        document.getElementById('activityInput').querySelector('.input-header').style.display = 'none';
    }

    toggleReactions(commentId) {
        const picker = document.getElementById(`reactions-${commentId}`);
        const isVisible = picker.style.display !== 'none';
        
        // Hide all pickers
        document.querySelectorAll('.reaction-picker').forEach(p => p.style.display = 'none');
        
        if (!isVisible) {
            picker.style.display = 'flex';
        }
    }

    async addReaction(commentId, emoji) {
        try {
            const response = await fetch(`/api/comments/${commentId}/reactions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ emoji })
            });

            if (response.ok) {
                this.loadActivities();
                this.toggleReactions(commentId);
            }
        } catch (error) {
            console.error('Failed to add reaction:', error);
        }
    }

    toggleEmojiPicker() {
        const picker = document.getElementById('emojiPicker');
        picker.style.display = picker.style.display === 'none' ? 'block' : 'none';
    }

    insertEmoji(emoji) {
        const textarea = document.getElementById('commentText');
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const text = textarea.value;
        
        textarea.value = text.substring(0, start) + emoji + text.substring(end);
        textarea.focus();
        textarea.setSelectionRange(start + emoji.length, start + emoji.length);
        
        this.toggleEmojiPicker();
    }

    async editComment(commentId) {
        const comment = this.activities.find(a => a.id === commentId);
        if (!comment) return;

        const newText = prompt('Edit comment:', comment.text);
        if (!newText) return;

        try {
            const response = await fetch(`/api/comments/${commentId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: newText })
            });

            if (response.ok) {
                this.loadActivities();
            }
        } catch (error) {
            console.error('Failed to edit comment:', error);
        }
    }

    async deleteComment(commentId) {
        if (!confirm('Delete this comment?')) return;

        try {
            const response = await fetch(`/api/comments/${commentId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.loadActivities();
            }
        } catch (error) {
            console.error('Failed to delete comment:', error);
        }
    }

    connectWebSocket() {
        // WebSocket for real-time updates
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            this.ws = new WebSocket(`${protocol}//${window.location.host}/ws/activity`);

            this.ws.onmessage = (event) => {
                const activity = JSON.parse(event.data);
                this.activities.unshift(activity);
                this.renderActivities();
            };

            this.ws.onerror = () => {
                console.error('WebSocket connection failed, falling back to polling');
                this.startPolling();
            };
        } catch (error) {
            console.error('WebSocket not supported, using polling');
            this.startPolling();
        }
    }

    startPolling() {
        setInterval(() => {
            if (document.getElementById('activityPanel').style.display !== 'none') {
                this.loadActivities();
            }
        }, 30000); // Poll every 30 seconds
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.activityStreams = new ActivityStreams();
});

// Global function
function openActivityStream(issueId = null) {
    window.activityStreams?.openPanel(issueId);
}
