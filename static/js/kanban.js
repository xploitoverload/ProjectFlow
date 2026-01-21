// kanban.js - Kanban board drag and drop functionality

class KanbanBoard {
    constructor() {
        this.draggedElement = null;
        this.draggedIssue = null;
        this.sourceColumn = null;
        this.init();
    }

    init() {
        this.setupDragListeners();
        this.setupColumnListeners();
        this.setupFilterListeners();
    }

    setupDragListeners() {
        // Make all issue cards draggable
        document.addEventListener('dragstart', (e) => this.handleDragStart(e));
        document.addEventListener('dragend', (e) => this.handleDragEnd(e));
        document.addEventListener('dragover', (e) => this.handleDragOver(e));
        document.addEventListener('drop', (e) => this.handleDrop(e));
    }

    setupColumnListeners() {
        // Setup drop zones on columns
        const columns = document.querySelectorAll('[data-status]');
        columns.forEach(column => {
            column.addEventListener('dragover', (e) => this.handleColumnDragOver(e));
            column.addEventListener('drop', (e) => this.handleColumnDrop(e));
        });
    }

    setupFilterListeners() {
        // Epic filter
        const epicFilter = document.getElementById('epicFilter');
        if (epicFilter) {
            epicFilter.addEventListener('change', () => this.applyFilters());
        }

        // Type filter
        const typeFilter = document.getElementById('typeFilter');
        if (typeFilter) {
            typeFilter.addEventListener('change', () => this.applyFilters());
        }

        // Search
        const searchInput = document.getElementById('searchIssues');
        if (searchInput) {
            searchInput.addEventListener('input', () => this.applyFilters());
        }
    }

    handleDragStart(e) {
        const issueCard = e.target.closest('[draggable="true"]');
        if (!issueCard) return;

        this.draggedElement = issueCard;
        this.draggedIssue = issueCard.dataset.issueId;
        this.sourceColumn = issueCard.closest('[data-status]');

        issueCard.style.opacity = '0.5';
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/html', issueCard.innerHTML);
    }

    handleDragEnd(e) {
        if (this.draggedElement) {
            this.draggedElement.style.opacity = '1';
        }
        this.draggedElement = null;
        this.draggedIssue = null;
    }

    handleDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
    }

    handleColumnDragOver(e) {
        e.preventDefault();
        e.currentTarget.style.backgroundColor = 'rgba(12, 102, 228, 0.05)';
    }

    handleColumnDrop(e) {
        e.preventDefault();
        e.currentTarget.style.backgroundColor = '';

        if (!this.draggedIssue || !this.draggedElement) return;

        const targetColumn = e.currentTarget;
        const targetStatus = targetColumn.dataset.status;

        // Prevent dropping in same column
        if (this.sourceColumn === targetColumn) {
            this.draggedElement.style.opacity = '1';
            return;
        }

        // Move issue to new column
        this.moveIssueToColumn(this.draggedIssue, targetStatus, targetColumn);
    }

    moveIssueToColumn(issueId, newStatus, targetColumn) {
        // Update on server
        fetch(`/project/${this.getProjectId()}/issue/${issueId}/update_status`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken()
            },
            body: JSON.stringify({ status: newStatus })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update UI
                    const issuesContainer = targetColumn.querySelector('.issues-list');
                    if (issuesContainer && this.draggedElement) {
                        issuesContainer.appendChild(this.draggedElement);
                        this.draggedElement.style.opacity = '1';

                        // Update issue card appearance
                        this.updateIssueCardStatus(this.draggedElement, newStatus);
                    }
                } else {
                    console.error('Failed to update issue status:', data.error);
                    this.draggedElement.style.opacity = '1';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                this.draggedElement.style.opacity = '1';
            });
    }

    updateIssueCardStatus(element, newStatus) {
        const statusBadge = element.querySelector('[data-status-badge]');
        if (statusBadge) {
            statusBadge.textContent = this.formatStatus(newStatus);
            statusBadge.className = `status-badge status-${newStatus}`;
        }
    }

    formatStatus(status) {
        return status
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    applyFilters() {
        const epicFilter = document.getElementById('epicFilter')?.value;
        const typeFilter = document.getElementById('typeFilter')?.value;
        const searchQuery = document.getElementById('searchIssues')?.value.toLowerCase();

        const issueCards = document.querySelectorAll('[data-issue-id]');

        issueCards.forEach(card => {
            let show = true;

            // Epic filter
            if (epicFilter && epicFilter !== 'all') {
                const cardEpic = card.dataset.epic;
                if (cardEpic !== epicFilter) show = false;
            }

            // Type filter
            if (typeFilter && typeFilter !== 'all') {
                const cardType = card.dataset.type;
                if (cardType !== typeFilter) show = false;
            }

            // Search query
            if (searchQuery) {
                const cardText = card.textContent.toLowerCase();
                if (!cardText.includes(searchQuery)) show = false;
            }

            card.style.display = show ? 'block' : 'none';
        });
    }

    getProjectId() {
        // Extract from URL or data attribute
        const match = window.location.pathname.match(/\/project\/(\d+)/);
        return match ? match[1] : null;
    }

    getCsrfToken() {
        const token = document.querySelector('input[name="csrf_token"]');
        return token ? token.value : '';
    }

    // Issue detail modal
    openIssueDetail(issueId) {
        fetch(`/api/project/${this.getProjectId()}/issue/${issueId}`)
            .then(response => response.json())
            .then(data => this.showIssueDetail(data))
            .catch(error => console.error('Error loading issue:', error));
    }

    showIssueDetail(issueData) {
        const modal = document.getElementById('issueDetailModal');
        if (!modal) return;

        // Populate modal with issue data
        document.getElementById('issueKey').textContent = issueData.key;
        document.getElementById('issueTitle').textContent = issueData.title;
        document.getElementById('issueDescription').textContent = issueData.description || 'No description';
        document.getElementById('statusText').textContent = this.formatStatus(issueData.status);
        document.getElementById('typeText').textContent = this.formatStatus(issueData.type);
        document.getElementById('prioritySelect').value = issueData.priority;
        document.getElementById('createdDate').textContent = new Date(issueData.created_at).toLocaleDateString();
        document.getElementById('updatedDate').textContent = new Date(issueData.updated_at).toLocaleDateString();

        // Set assignee
        if (issueData.assignee) {
            document.getElementById('assigneeText').textContent = issueData.assignee.username;
        }

        // Set reporter
        if (issueData.reporter) {
            document.getElementById('reporterText').textContent = issueData.reporter.username;
        }

        // Load comments
        const commentsList = document.getElementById('commentsList');
        if (commentsList) {
            commentsList.innerHTML = issueData.comments.map(c => `
                <div class="comment-item">
                    <div class="comment-header">
                        <span class="comment-author">${c.author}</span>
                        <span class="comment-time">${new Date(c.created_at).toLocaleDateString()}</span>
                    </div>
                    <div class="comment-text">${c.text}</div>
                </div>
            `).join('');
        }

        // Show modal
        modal.classList.add('active');
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    window.kanban = new KanbanBoard();

    // Setup issue card click handlers
    document.addEventListener('click', (e) => {
        const issueCard = e.target.closest('[data-issue-id]');
        if (issueCard && !e.target.closest('[draggable]')) {
            const issueId = issueCard.dataset.issueId;
            window.kanban.openIssueDetail(issueId);
        }
    });
});
