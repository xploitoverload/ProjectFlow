/**
 * Board Filters Manager - JIRA-style filtering for Kanban boards
 * Enables filtering by assignee, priority, labels, sprint, and custom fields
 */

class BoardFiltersManager {
    constructor() {
        this.activeFilters = {
            assignees: [],
            priorities: [],
            labels: [],
            sprints: [],
            search: ''
        };
        
        this.allCards = [];
        this.init();
    }

    init() {
        this.cacheCards();
        this.setupFilterButtons();
        this.setupSearchFilter();
        this.setupQuickFilters();
    }

    cacheCards() {
        // Cache all cards for filtering
        this.allCards = Array.from(document.querySelectorAll('.kanban-card'));
        this.allCards.forEach(card => {
            card.dataset.originalDisplay = card.style.display || '';
        });
    }

    setupFilterButtons() {
        // Create filter panel if it doesn't exist
        this.createFilterPanel();
        
        // Setup filter toggle button
        const filterBtn = document.getElementById('filterToggleBtn');
        if (filterBtn) {
            filterBtn.addEventListener('click', () => this.toggleFilterPanel());
        }
    }

    createFilterPanel() {
        const toolbar = document.querySelector('.kanban-toolbar');
        if (!toolbar || document.getElementById('filterPanel')) return;

        // Check if filter button exists
        let filterBtn = document.getElementById('filterToggleBtn');
        if (!filterBtn) {
            // Create filter toggle button
            const btnContainer = document.createElement('div');
            btnContainer.innerHTML = `
                <button class="btn btn-ghost btn-sm" id="filterToggleBtn" title="Filter Board">
                    <i data-lucide="filter" class="icon-sm"></i>
                    Filters
                    <span class="filter-count-badge" style="display: none;">0</span>
                </button>
            `;
            
            // Insert before the Insights button or at the end
            const insightsBtn = toolbar.querySelector('[title="Insights"]');
            if (insightsBtn) {
                toolbar.insertBefore(btnContainer.firstElementChild, insightsBtn);
            } else {
                toolbar.appendChild(btnContainer.firstElementChild);
            }
            
            filterBtn = document.getElementById('filterToggleBtn');
        }

        // Create filter panel
        const panel = document.createElement('div');
        panel.id = 'filterPanel';
        panel.className = 'filter-panel';
        panel.style.display = 'none';
        panel.innerHTML = `
            <div class="filter-panel-header">
                <h3 class="filter-panel-title">Filter Board</h3>
                <button class="btn-icon-sm" id="closeFilterPanel">
                    <i data-lucide="x" style="width: 16px; height: 16px;"></i>
                </button>
            </div>
            
            <div class="filter-panel-body">
                <!-- Search Filter -->
                <div class="filter-section">
                    <label class="filter-label">
                        <i data-lucide="search" style="width: 14px; height: 14px;"></i>
                        Search
                    </label>
                    <input type="text" 
                           id="boardSearchInput" 
                           class="filter-input" 
                           placeholder="Search issues..."
                           autocomplete="off">
                </div>

                <!-- Assignee Filter -->
                <div class="filter-section">
                    <label class="filter-label">
                        <i data-lucide="user" style="width: 14px; height: 14px;"></i>
                        Assignee
                    </label>
                    <div class="filter-options" id="assigneeFilters"></div>
                </div>

                <!-- Priority Filter -->
                <div class="filter-section">
                    <label class="filter-label">
                        <i data-lucide="alert-circle" style="width: 14px; height: 14px;"></i>
                        Priority
                    </label>
                    <div class="filter-options" id="priorityFilters"></div>
                </div>

                <!-- Label Filter -->
                <div class="filter-section">
                    <label class="filter-label">
                        <i data-lucide="tag" style="width: 14px; height: 14px;"></i>
                        Labels
                    </label>
                    <div class="filter-options" id="labelFilters"></div>
                </div>
            </div>

            <div class="filter-panel-footer">
                <button class="btn btn-secondary btn-sm" id="clearFiltersBtn">Clear All</button>
                <button class="btn btn-primary btn-sm" id="applyFiltersBtn">Apply Filters</button>
            </div>
        `;

        document.body.appendChild(panel);

        // Setup panel event listeners
        document.getElementById('closeFilterPanel').addEventListener('click', () => this.toggleFilterPanel());
        document.getElementById('clearFiltersBtn').addEventListener('click', () => this.clearAllFilters());
        document.getElementById('applyFiltersBtn').addEventListener('click', () => {
            this.applyFilters();
            this.toggleFilterPanel();
        });

        // Populate filter options
        this.populateAssigneeFilters();
        this.populatePriorityFilters();
        this.populateLabelFilters();

        // Re-initialize Lucide icons
        if (window.lucide) {
            lucide.createIcons();
        }
    }

    toggleFilterPanel() {
        const panel = document.getElementById('filterPanel');
        if (!panel) return;

        const isVisible = panel.style.display !== 'none';
        panel.style.display = isVisible ? 'none' : 'block';

        if (!isVisible) {
            // Position panel below the filter button
            const filterBtn = document.getElementById('filterToggleBtn');
            if (filterBtn) {
                const rect = filterBtn.getBoundingClientRect();
                panel.style.top = `${rect.bottom + 8}px`;
                panel.style.right = `${window.innerWidth - rect.right}px`;
            }
        }
    }

    populateAssigneeFilters() {
        const container = document.getElementById('assigneeFilters');
        if (!container) return;

        const assignees = new Set();
        this.allCards.forEach(card => {
            const assignee = card.dataset.assignee;
            if (assignee) assignees.add(assignee);
        });

        // Add "Unassigned" option
        assignees.add('unassigned');

        container.innerHTML = Array.from(assignees).map(assignee => `
            <label class="filter-checkbox">
                <input type="checkbox" value="${assignee}" data-filter-type="assignee">
                <span>${assignee === 'unassigned' ? 'Unassigned' : assignee}</span>
            </label>
        `).join('');

        // Add event listeners
        container.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                this.updateFilterArray('assignees', e.target.value, e.target.checked);
                this.applyFilters();
            });
        });
    }

    populatePriorityFilters() {
        const container = document.getElementById('priorityFilters');
        if (!container) return;

        const priorities = ['highest', 'high', 'medium', 'low', 'lowest'];
        const priorityIcons = {
            'highest': '⬆️',
            'high': '🔺',
            'medium': '➖',
            'low': '🔻',
            'lowest': '⬇️'
        };

        container.innerHTML = priorities.map(priority => `
            <label class="filter-checkbox">
                <input type="checkbox" value="${priority}" data-filter-type="priority">
                <span>${priorityIcons[priority]} ${priority.charAt(0).toUpperCase() + priority.slice(1)}</span>
            </label>
        `).join('');

        // Add event listeners
        container.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                this.updateFilterArray('priorities', e.target.value, e.target.checked);
                this.applyFilters();
            });
        });
    }

    populateLabelFilters() {
        const container = document.getElementById('labelFilters');
        if (!container) return;

        const labels = new Set();
        this.allCards.forEach(card => {
            const cardLabels = card.dataset.labels;
            if (cardLabels) {
                cardLabels.split(',').forEach(label => labels.add(label.trim()));
            }
        });

        if (labels.size === 0) {
            container.innerHTML = '<p class="filter-empty">No labels found</p>';
            return;
        }

        container.innerHTML = Array.from(labels).map(label => `
            <label class="filter-checkbox">
                <input type="checkbox" value="${label}" data-filter-type="label">
                <span>${label}</span>
            </label>
        `).join('');

        // Add event listeners
        container.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                this.updateFilterArray('labels', e.target.value, e.target.checked);
                this.applyFilters();
            });
        });
    }

    setupSearchFilter() {
        const searchInput = document.getElementById('boardSearchInput');
        if (!searchInput) return;

        let debounceTimer;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                this.activeFilters.search = e.target.value.toLowerCase();
                this.applyFilters();
            }, 300);
        });
    }

    setupQuickFilters() {
        // Setup quick filter buttons (e.g., "Only My Issues", "Recently Updated")
        const toolbar = document.querySelector('.kanban-toolbar');
        if (!toolbar) return;

        // Add quick filter for current user
        const quickFilterHTML = `
            <button class="btn btn-ghost btn-sm" id="myIssuesQuickFilter" title="Only my issues">
                <i data-lucide="user-check" class="icon-sm"></i>
                My Issues
            </button>
        `;

        // Insert if doesn't exist
        if (!document.getElementById('myIssuesQuickFilter')) {
            const filterBtn = document.getElementById('filterToggleBtn');
            if (filterBtn) {
                const btn = document.createElement('div');
                btn.innerHTML = quickFilterHTML;
                filterBtn.parentNode.insertBefore(btn.firstElementChild, filterBtn.nextSibling);
            }
        }

        // Add event listener
        const myIssuesBtn = document.getElementById('myIssuesQuickFilter');
        if (myIssuesBtn) {
            myIssuesBtn.addEventListener('click', () => {
                this.toggleMyIssuesFilter(myIssuesBtn);
            });
        }

        // Re-initialize Lucide icons
        if (window.lucide) {
            lucide.createIcons();
        }
    }

    toggleMyIssuesFilter(btn) {
        const currentUser = window.currentUser?.username;
        if (!currentUser) return;

        const isActive = btn.classList.contains('active');
        
        if (isActive) {
            // Remove filter
            btn.classList.remove('active');
            this.activeFilters.assignees = this.activeFilters.assignees.filter(a => a !== currentUser);
        } else {
            // Add filter
            btn.classList.add('active');
            if (!this.activeFilters.assignees.includes(currentUser)) {
                this.activeFilters.assignees.push(currentUser);
            }
        }

        this.applyFilters();
        this.updateFilterCount();
    }

    updateFilterArray(filterType, value, isChecked) {
        if (isChecked) {
            if (!this.activeFilters[filterType].includes(value)) {
                this.activeFilters[filterType].push(value);
            }
        } else {
            this.activeFilters[filterType] = this.activeFilters[filterType].filter(v => v !== value);
        }
    }

    applyFilters() {
        let visibleCount = 0;

        this.allCards.forEach(card => {
            const shouldShow = this.cardMatchesFilters(card);
            
            if (shouldShow) {
                card.style.display = card.dataset.originalDisplay;
                card.classList.remove('filtered-out');
                visibleCount++;
            } else {
                card.style.display = 'none';
                card.classList.add('filtered-out');
            }
        });

        // Update column counts
        this.updateColumnCounts();
        this.updateFilterCount();

        // Dispatch custom event for other components
        window.dispatchEvent(new CustomEvent('boardFiltered', {
            detail: {
                visibleCount,
                activeFilters: this.activeFilters
            }
        }));
    }

    cardMatchesFilters(card) {
        // Search filter
        if (this.activeFilters.search) {
            const title = card.querySelector('.issue-title, .kanban-card-title')?.textContent.toLowerCase() || '';
            const description = card.querySelector('.issue-description')?.textContent.toLowerCase() || '';
            const key = card.dataset.issueKey?.toLowerCase() || '';
            
            const searchTerm = this.activeFilters.search;
            if (!title.includes(searchTerm) && !description.includes(searchTerm) && !key.includes(searchTerm)) {
                return false;
            }
        }

        // Assignee filter
        if (this.activeFilters.assignees.length > 0) {
            const cardAssignee = card.dataset.assignee || 'unassigned';
            if (!this.activeFilters.assignees.includes(cardAssignee)) {
                return false;
            }
        }

        // Priority filter
        if (this.activeFilters.priorities.length > 0) {
            const cardPriority = card.dataset.priority?.toLowerCase();
            if (!cardPriority || !this.activeFilters.priorities.includes(cardPriority)) {
                return false;
            }
        }

        // Label filter
        if (this.activeFilters.labels.length > 0) {
            const cardLabels = card.dataset.labels?.split(',').map(l => l.trim()) || [];
            const hasMatchingLabel = this.activeFilters.labels.some(label => cardLabels.includes(label));
            if (!hasMatchingLabel) {
                return false;
            }
        }

        return true;
    }

    updateColumnCounts() {
        const columns = document.querySelectorAll('.kanban-column');
        columns.forEach(column => {
            const visibleCards = column.querySelectorAll('.kanban-card:not(.filtered-out)').length;
            const countBadge = column.querySelector('.kanban-column-count');
            if (countBadge) {
                countBadge.textContent = visibleCards;
            }
        });
    }

    updateFilterCount() {
        const totalFilters = 
            this.activeFilters.assignees.length +
            this.activeFilters.priorities.length +
            this.activeFilters.labels.length +
            (this.activeFilters.search ? 1 : 0);

        const badge = document.querySelector('#filterToggleBtn .filter-count-badge');
        if (badge) {
            if (totalFilters > 0) {
                badge.textContent = totalFilters;
                badge.style.display = 'inline-block';
            } else {
                badge.style.display = 'none';
            }
        }
    }

    clearAllFilters() {
        // Reset all filters
        this.activeFilters = {
            assignees: [],
            priorities: [],
            labels: [],
            sprints: [],
            search: ''
        };

        // Uncheck all checkboxes
        document.querySelectorAll('#filterPanel input[type="checkbox"]').forEach(cb => {
            cb.checked = false;
        });

        // Clear search input
        const searchInput = document.getElementById('boardSearchInput');
        if (searchInput) searchInput.value = '';

        // Remove quick filter active states
        document.querySelectorAll('.quick-filter-active').forEach(btn => {
            btn.classList.remove('active');
        });

        // Apply filters (show all)
        this.applyFilters();
    }

    refresh() {
        // Re-cache cards and reapply filters
        this.cacheCards();
        this.populateAssigneeFilters();
        this.populatePriorityFilters();
        this.populateLabelFilters();
        this.applyFilters();
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.kanban-board')) {
        window.boardFiltersManager = new BoardFiltersManager();
    }
});
