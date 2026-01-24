/**
 * Card Context Menu - JIRA-style right-click quick actions menu
 */

class CardContextMenu {
    constructor() {
        this.menu = null;
        this.activeCard = null;
        this.init();
    }

    init() {
        this.createMenu();
        this.setupEventListeners();
    }

    createMenu() {
        if (document.getElementById('cardContextMenu')) return;

        const menu = document.createElement('div');
        menu.id = 'cardContextMenu';
        menu.className = 'context-menu';
        menu.style.display = 'none';
        menu.innerHTML = `
            <div class="context-menu-section">
                <div class="context-menu-item" data-action="edit">
                    <i data-lucide="edit-2"></i>
                    <span>Edit Issue</span>
                    <kbd>E</kbd>
                </div>
                <div class="context-menu-item" data-action="assign">
                    <i data-lucide="user-plus"></i>
                    <span>Assign to Me</span>
                    <kbd>M</kbd>
                </div>
                <div class="context-menu-item" data-action="priority">
                    <i data-lucide="alert-triangle"></i>
                    <span>Change Priority</span>
                </div>
            </div>
            <div class="context-menu-divider"></div>
            <div class="context-menu-section">
                <div class="context-menu-item" data-action="move">
                    <i data-lucide="move"></i>
                    <span>Move to Sprint...</span>
                </div>
                <div class="context-menu-item" data-action="clone">
                    <i data-lucide="copy"></i>
                    <span>Clone Issue</span>
                </div>
                <div class="context-menu-item" data-action="link">
                    <i data-lucide="link-2"></i>
                    <span>Link Issue...</span>
                </div>
            </div>
            <div class="context-menu-divider"></div>
            <div class="context-menu-section">
                <div class="context-menu-item" data-action="share">
                    <i data-lucide="share-2"></i>
                    <span>Share</span>
                </div>
                <div class="context-menu-item" data-action="copy-link">
                    <i data-lucide="clipboard"></i>
                    <span>Copy Link</span>
                </div>
                <div class="context-menu-item" data-action="watch">
                    <i data-lucide="eye"></i>
                    <span>Watch</span>
                </div>
            </div>
            <div class="context-menu-divider"></div>
            <div class="context-menu-section">
                <div class="context-menu-item context-menu-item-danger" data-action="delete">
                    <i data-lucide="trash-2"></i>
                    <span>Delete Issue</span>
                    <kbd>Del</kbd>
                </div>
            </div>
        `;

        document.body.appendChild(menu);
        this.menu = menu;

        // Initialize Lucide icons
        if (window.lucide) {
            lucide.createIcons();
        }
    }

    setupEventListeners() {
        // Right-click on kanban cards
        document.addEventListener('contextmenu', (e) => {
            const card = e.target.closest('.kanban-card');
            if (card) {
                e.preventDefault();
                this.showMenu(e.pageX, e.pageY, card);
            }
        });

        // Click outside to close
        document.addEventListener('click', (e) => {
            if (this.menu && !this.menu.contains(e.target)) {
                this.hideMenu();
            }
        });

        // Menu item clicks
        this.menu?.addEventListener('click', (e) => {
            const item = e.target.closest('.context-menu-item');
            if (item) {
                const action = item.dataset.action;
                this.handleAction(action);
                this.hideMenu();
            }
        });

        // Keyboard shortcuts on selected card
        document.addEventListener('keydown', (e) => {
            if (!this.activeCard) return;

            // E - Edit
            if (e.key === 'e' || e.key === 'E') {
                this.handleAction('edit');
            }
            // M - Assign to me
            else if (e.key === 'm' || e.key === 'M') {
                this.handleAction('assign');
            }
            // Delete
            else if (e.key === 'Delete') {
                this.handleAction('delete');
            }
        });

        // Hover menu on cards (alternative to right-click)
        this.setupHoverMenu();
    }

    setupHoverMenu() {
        // Add quick action button to each card
        const style = document.createElement('style');
        style.textContent = `
            .card-quick-actions {
                position: absolute;
                top: 8px;
                right: 8px;
                opacity: 0;
                transition: opacity 0.2s;
            }
            .kanban-card {
                position: relative;
            }
            .kanban-card:hover .card-quick-actions {
                opacity: 1;
            }
        `;
        document.head.appendChild(style);

        // Add quick actions button to existing cards
        this.addQuickActionsToCards();

        // Observer for dynamically added cards
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.classList && node.classList.contains('kanban-card')) {
                        this.addQuickActionButton(node);
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    addQuickActionsToCards() {
        document.querySelectorAll('.kanban-card').forEach(card => {
            this.addQuickActionButton(card);
        });
    }

    addQuickActionButton(card) {
        if (card.querySelector('.card-quick-actions')) return;

        const button = document.createElement('button');
        button.className = 'btn-icon-sm card-quick-actions';
        button.innerHTML = '<i data-lucide="more-horizontal" style="width: 14px; height: 14px;"></i>';
        button.title = 'Quick actions';
        button.onclick = (e) => {
            e.stopPropagation();
            const rect = button.getBoundingClientRect();
            this.showMenu(rect.left, rect.bottom + 4, card);
        };

        card.appendChild(button);

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    showMenu(x, y, card) {
        if (!this.menu) return;

        this.activeCard = card;
        card.classList.add('context-menu-active');

        // Position menu
        this.menu.style.left = `${x}px`;
        this.menu.style.top = `${y}px`;
        this.menu.style.display = 'block';

        // Adjust if menu goes off-screen
        setTimeout(() => {
            const rect = this.menu.getBoundingClientRect();
            if (rect.right > window.innerWidth) {
                this.menu.style.left = `${x - rect.width}px`;
            }
            if (rect.bottom > window.innerHeight) {
                this.menu.style.top = `${y - rect.height}px`;
            }
        }, 0);
    }

    hideMenu() {
        if (!this.menu) return;

        this.menu.style.display = 'none';
        if (this.activeCard) {
            this.activeCard.classList.remove('context-menu-active');
            this.activeCard = null;
        }
    }

    async handleAction(action) {
        if (!this.activeCard) return;

        const issueId = this.activeCard.dataset.issueId;
        const issueKey = this.activeCard.dataset.issueKey;

        switch (action) {
            case 'edit':
                this.editIssue(issueId);
                break;
            
            case 'assign':
                await this.assignToMe(issueId);
                break;
            
            case 'priority':
                this.changePriority(issueId);
                break;
            
            case 'move':
                this.moveToSprint(issueId);
                break;
            
            case 'clone':
                await this.cloneIssue(issueId);
                break;
            
            case 'link':
                this.linkIssue(issueId);
                break;
            
            case 'share':
                this.shareIssue(issueKey);
                break;
            
            case 'copy-link':
                this.copyLink(issueKey);
                break;
            
            case 'watch':
                await this.toggleWatch(issueId);
                break;
            
            case 'delete':
                this.deleteIssue(issueId);
                break;
        }
    }

    editIssue(issueId) {
        // Open issue detail modal or page
        if (typeof openIssueDetail === 'function') {
            openIssueDetail(issueId);
        } else {
            window.location.href = `/issues/${issueId}`;
        }
    }

    async assignToMe(issueId) {
        try {
            const response = await fetch(`/api/issues/${issueId}/assign-to-me`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (response.ok) {
                // Update card UI
                const assigneeDiv = this.activeCard.querySelector('.assignee-avatar-enhanced');
                if (assigneeDiv && window.currentUser) {
                    assigneeDiv.textContent = window.currentUser.username.substring(0, 2).toUpperCase();
                    assigneeDiv.title = window.currentUser.username;
                }

                window.notificationManager?.addNotification({
                    title: 'Issue Assigned',
                    message: 'Issue assigned to you',
                    type: 'success'
                });
            }
        } catch (error) {
            console.error('Failed to assign issue:', error);
            window.notificationManager?.addNotification({
                title: 'Assignment Failed',
                message: 'Could not assign issue',
                type: 'error'
            });
        }
    }

    changePriority(issueId) {
        // Show priority picker modal
        const priorities = ['Highest', 'High', 'Medium', 'Low', 'Lowest'];
        const choice = prompt('Select priority:\n' + priorities.join('\n'));
        
        if (choice && priorities.includes(choice)) {
            this.updatePriority(issueId, choice);
        }
    }

    async updatePriority(issueId, priority) {
        try {
            const response = await fetch(`/api/issues/${issueId}/priority`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ priority })
            });

            if (response.ok) {
                window.notificationManager?.addNotification({
                    title: 'Priority Updated',
                    message: `Priority set to ${priority}`,
                    type: 'success'
                });
                location.reload(); // Refresh to show new priority
            }
        } catch (error) {
            console.error('Failed to update priority:', error);
        }
    }

    moveToSprint(issueId) {
        alert('Move to Sprint feature - Coming soon!');
    }

    async cloneIssue(issueId) {
        if (!confirm('Clone this issue?')) return;

        try {
            const response = await fetch(`/api/issues/${issueId}/clone`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (response.ok) {
                window.notificationManager?.addNotification({
                    title: 'Issue Cloned',
                    message: 'Issue has been cloned successfully',
                    type: 'success'
                });
                location.reload();
            }
        } catch (error) {
            console.error('Failed to clone issue:', error);
        }
    }

    linkIssue(issueId) {
        alert('Link Issue feature - Coming soon!');
    }

    shareIssue(issueKey) {
        const url = `${window.location.origin}/issues/${issueKey}`;
        
        if (navigator.share) {
            navigator.share({
                title: `Issue ${issueKey}`,
                url: url
            });
        } else {
            this.copyLink(issueKey);
        }
    }

    copyLink(issueKey) {
        const url = `${window.location.origin}/issues/${issueKey}`;
        
        navigator.clipboard.writeText(url).then(() => {
            window.notificationManager?.addNotification({
                title: 'Link Copied',
                message: 'Issue link copied to clipboard',
                type: 'success'
            });
        });
    }

    async toggleWatch(issueId) {
        try {
            const response = await fetch(`/api/issues/${issueId}/watch`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (response.ok) {
                window.notificationManager?.addNotification({
                    title: 'Watch Updated',
                    message: 'You are now watching this issue',
                    type: 'success'
                });
            }
        } catch (error) {
            console.error('Failed to toggle watch:', error);
        }
    }

    deleteIssue(issueId) {
        if (!confirm('Are you sure you want to delete this issue? This action cannot be undone.')) {
            return;
        }

        // Get project ID from URL or page context
        const projectId = new URLSearchParams(window.location.search).get('project_id') || 
                         window.location.pathname.match(/projects\/(\d+)/)?.[1];

        if (!projectId) {
            console.error('Project ID not found');
            return;
        }

        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/projects/${projectId}/issue/${issueId}/delete`;
        
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrf_token';
        csrfInput.value = document.querySelector('input[name="csrf_token"]')?.value || '';
        
        form.appendChild(csrfInput);
        document.body.appendChild(form);
        form.submit();
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.kanban-board')) {
        window.cardContextMenu = new CardContextMenu();
    }
});
