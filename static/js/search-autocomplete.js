/**
 * Search Autocomplete Module
 * Provides intelligent search suggestions for issues, projects, and users
 */

class SearchAutocomplete {
    constructor() {
        this.searchInput = null;
        this.dropdown = null;
        this.debounceTimer = null;
        this.currentQuery = '';
        this.selectedIndex = -1;
        this.results = { issues: [], projects: [], users: [] };
        this.init();
    }

    init() {
        // Create hidden search input (the visible one is readonly)
        this.createRealSearchInput();
        this.setupEventListeners();
        console.log('SearchAutocomplete initialized');
    }

    createRealSearchInput() {
        // The visible search bar should trigger real search on click
        const visibleSearch = document.querySelector('.header-search');
        if (!visibleSearch) return;

        visibleSearch.addEventListener('click', (e) => {
            // Don't open command palette, open search autocomplete instead
            e.stopPropagation();
            this.openSearch();
        });
    }

    openSearch() {
        // Create overlay
        const overlay = document.createElement('div');
        overlay.id = 'searchAutocompleteOverlay';
        overlay.className = 'search-autocomplete-overlay';

        // Create search modal
        const modal = document.createElement('div');
        modal.id = 'searchAutocompleteModal';
        modal.className = 'search-autocomplete-modal';
        modal.innerHTML = `
            <div class="search-autocomplete-header">
                <i data-lucide="search"></i>
                <input type="text" class="search-autocomplete-input" placeholder="Search issues, projects, or @mention users..." autofocus>
                <button class="search-autocomplete-close">
                    <i data-lucide="x"></i>
                </button>
            </div>
            <div class="search-autocomplete-results">
                <div class="search-autocomplete-empty">
                    <i data-lucide="search"></i>
                    <p>Type to search issues, projects, or users</p>
                    <div class="search-autocomplete-tips">
                        <span><code>@username</code> to find users</span>
                        <span><code>PROJ-123</code> to find issues</span>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(overlay);
        document.body.appendChild(modal);

        // Initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }

        this.searchInput = modal.querySelector('.search-autocomplete-input');
        this.dropdown = modal.querySelector('.search-autocomplete-results');

        this.searchInput.focus();
        this.setupModalEvents(modal, overlay);
    }

    setupModalEvents(modal, overlay) {
        // Close button
        modal.querySelector('.search-autocomplete-close').addEventListener('click', () => {
            this.closeSearch();
        });

        // Close on overlay click
        overlay.addEventListener('click', () => {
            this.closeSearch();
        });

        // Search input
        this.searchInput.addEventListener('input', (e) => {
            this.handleInput(e.target.value);
        });

        // Keyboard navigation
        this.searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeSearch();
            } else if (e.key === 'ArrowDown') {
                e.preventDefault();
                this.navigateResults(1);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                this.navigateResults(-1);
            } else if (e.key === 'Enter') {
                e.preventDefault();
                this.selectResult();
            }
        });
    }

    setupEventListeners() {
        // Intercept the command palette trigger to use search instead
        document.addEventListener('keydown', (e) => {
            // Override CMD+K to open search instead of command palette
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                e.stopPropagation();
                this.openSearch();
            }
        }, true); // Use capture phase to intercept before global navigation
    }

    handleInput(value) {
        this.currentQuery = value;

        // Clear previous timer
        clearTimeout(this.debounceTimer);

        // Show empty state for short queries
        if (value.length < 2) {
            this.showEmptyState();
            return;
        }

        // Show loading
        this.showLoading();

        // Debounce API call
        this.debounceTimer = setTimeout(() => {
            this.fetchResults(value);
        }, 300);
    }

    async fetchResults(query) {
        try {
            const response = await fetch(`/api/v1/search/autocomplete?q=${encodeURIComponent(query)}`);
            const data = await response.json();

            if (data.success) {
                this.results = data.data;
                this.displayResults();
            }
        } catch (error) {
            console.error('Search failed:', error);
            this.showError();
        }
    }

    displayResults() {
        const { issues, projects, users } = this.results;
        const hasResults = issues.length > 0 || projects.length > 0 || users.length > 0;

        if (!hasResults) {
            this.showNoResults();
            return;
        }

        let html = '';

        // Issues section
        if (issues.length > 0) {
            html += `
                <div class="search-results-section">
                    <div class="search-results-title">Issues</div>
                    ${issues.map((issue, idx) => `
                        <div class="search-result-item ${idx === 0 ? 'selected' : ''}" data-type="issue" data-id="${issue.id}">
                            <div class="search-result-icon" data-issue-type="${issue.type}">
                                <i data-lucide="circle"></i>
                            </div>
                            <div class="search-result-content">
                                <div class="search-result-title">${issue.key}: ${issue.title}</div>
                                <div class="search-result-meta">${issue.type} • ${issue.status}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        }

        // Projects section
        if (projects.length > 0) {
            html += `
                <div class="search-results-section">
                    <div class="search-results-title">Projects</div>
                    ${projects.map(project => `
                        <div class="search-result-item" data-type="project" data-id="${project.id}">
                            <div class="search-result-icon" style="background: #FF8B00;">
                                <i data-lucide="folder"></i>
                            </div>
                            <div class="search-result-content">
                                <div class="search-result-title">${project.name}</div>
                                <div class="search-result-meta">${project.key}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        }

        // Users section
        if (users.length > 0) {
            html += `
                <div class="search-results-section">
                    <div class="search-results-title">Users</div>
                    ${users.map(user => `
                        <div class="search-result-item" data-type="user" data-id="${user.id}">
                            <div class="search-result-icon" style="background: #6554C0;">
                                <i data-lucide="user"></i>
                            </div>
                            <div class="search-result-content">
                                <div class="search-result-title">@${user.username}</div>
                                <div class="search-result-meta">${user.email}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        }

        this.dropdown.innerHTML = html;
        this.selectedIndex = 0;

        // Re-initialize icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }

        // Add click handlers
        document.querySelectorAll('.search-result-item').forEach(item => {
            item.addEventListener('click', () => {
                this.navigateToResult(item);
            });
        });
    }

    navigateResults(direction) {
        const items = document.querySelectorAll('.search-result-item');
        if (items.length === 0) return;

        // Remove current selection
        items[this.selectedIndex]?.classList.remove('selected');

        // Calculate new index
        this.selectedIndex += direction;
        if (this.selectedIndex < 0) this.selectedIndex = items.length - 1;
        if (this.selectedIndex >= items.length) this.selectedIndex = 0;

        // Add new selection
        items[this.selectedIndex].classList.add('selected');
        items[this.selectedIndex].scrollIntoView({ block: 'nearest' });
    }

    selectResult() {
        const selected = document.querySelector('.search-result-item.selected');
        if (selected) {
            this.navigateToResult(selected);
        }
    }

    navigateToResult(item) {
        const type = item.dataset.type;
        const id = item.dataset.id;

        const urlMap = {
            'issue': `/issues/${id}`,
            'project': `/project/${id}`,
            'user': `/profile/${id}`
        };

        if (urlMap[type]) {
            window.location.href = urlMap[type];
        }
    }

    showEmptyState() {
        this.dropdown.innerHTML = `
            <div class="search-autocomplete-empty">
                <i data-lucide="search"></i>
                <p>Type to search issues, projects, or users</p>
                <div class="search-autocomplete-tips">
                    <span><code>@username</code> to find users</span>
                    <span><code>PROJ-123</code> to find issues</span>
                </div>
            </div>
        `;
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }

    showLoading() {
        this.dropdown.innerHTML = `
            <div class="search-autocomplete-loading">
                <i data-lucide="loader" class="spin"></i>
                <span>Searching...</span>
            </div>
        `;
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }

    showNoResults() {
        this.dropdown.innerHTML = `
            <div class="search-autocomplete-empty">
                <i data-lucide="search-x"></i>
                <p>No results found for "${this.currentQuery}"</p>
            </div>
        `;
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }

    showError() {
        this.dropdown.innerHTML = `
            <div class="search-autocomplete-empty">
                <i data-lucide="alert-circle"></i>
                <p>Search failed. Please try again.</p>
            </div>
        `;
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }

    closeSearch() {
        document.getElementById('searchAutocompleteOverlay')?.remove();
        document.getElementById('searchAutocompleteModal')?.remove();
        this.searchInput = null;
        this.dropdown = null;
        this.selectedIndex = -1;
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.searchAutocomplete = new SearchAutocomplete();
    });
} else {
    window.searchAutocomplete = new SearchAutocomplete();
}
