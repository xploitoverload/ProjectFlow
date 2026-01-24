/**
 * Advanced Search & Filters System
 * Quick search, Subscriptions, Sharing, Typo correction, Global search
 */

class AdvancedSearchFiltersSystem {
    constructor() {
        this.savedFilters = [
            { id: 'f1', name: 'My Open Issues', jql: 'assignee = currentUser() AND status != Done', starred: true, owner: 'me', shared: false },
            { id: 'f2', name: 'High Priority Bugs', jql: 'type = Bug AND priority = High', starred: false, owner: 'me', shared: true },
            { id: 'f3', name: 'Overdue Tasks', jql: 'duedate < now() AND status != Done', starred: true, owner: 'me', shared: false }
        ];
        
        this.recentSearches = [
            'type = Bug AND status = Open',
            'assignee = currentUser()',
            'project = TEST'
        ];
        
        this.searchHistory = [];
        this.activeFilter = null;
        this.searchMode = 'quick'; // quick or advanced
        
        this.init();
    }
    
    init() {
        console.log('Advanced Search & Filters System initialized');
        this.setupGlobalSearch();
    }
    
    setupGlobalSearch() {
        // Setup keyboard shortcut: Cmd/Ctrl + K for global search
        document.addEventListener('keydown', (e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                this.openGlobalSearch();
            }
        });
    }
    
    render(container) {
        container.innerHTML = `
            <div class="search-filters-container">
                ${this.renderHeader()}
                <div class="search-content">
                    ${this.renderSidebar()}
                    ${this.renderMainContent()}
                </div>
            </div>
        `;
        
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }
    
    renderHeader() {
        return `
            <div class="search-header">
                <h2>Filters & Search</h2>
                <div class="header-actions">
                    <button class="btn btn-secondary" onclick="searchFiltersSystem.openGlobalSearch()">
                        <i data-lucide="command"></i>
                        Global Search (⌘K)
                    </button>
                    <button class="btn btn-primary" onclick="searchFiltersSystem.createFilter()">
                        <i data-lucide="plus"></i>
                        Create Filter
                    </button>
                </div>
            </div>
        `;
    }
    
    renderSidebar() {
        return `
            <aside class="filters-sidebar">
                <div class="search-mode-toggle">
                    <button class="mode-btn ${this.searchMode === 'quick' ? 'active' : ''}" 
                        onclick="searchFiltersSystem.setSearchMode('quick')">
                        <i data-lucide="zap"></i>
                        Quick Search
                    </button>
                    <button class="mode-btn ${this.searchMode === 'advanced' ? 'active' : ''}" 
                        onclick="searchFiltersSystem.setSearchMode('advanced')">
                        <i data-lucide="sliders"></i>
                        Advanced
                    </button>
                </div>
                
                <div class="filters-list">
                    <div class="filters-section">
                        <h4>Starred Filters</h4>
                        ${this.savedFilters.filter(f => f.starred).map(filter => this.renderFilterItem(filter)).join('')}
                    </div>
                    
                    <div class="filters-section">
                        <h4>My Filters</h4>
                        ${this.savedFilters.filter(f => !f.starred).map(filter => this.renderFilterItem(filter)).join('')}
                    </div>
                    
                    <div class="filters-section">
                        <h4>Recent Searches</h4>
                        ${this.recentSearches.map((search, idx) => `
                            <div class="recent-search-item" onclick="searchFiltersSystem.useRecentSearch('${search}')">
                                <i data-lucide="clock"></i>
                                <span class="search-text">${search}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </aside>
        `;
    }
    
    renderFilterItem(filter) {
        return `
            <div class="filter-item ${this.activeFilter === filter.id ? 'active' : ''}" 
                onclick="searchFiltersSystem.selectFilter('${filter.id}')">
                <div class="filter-info">
                    <button class="star-btn ${filter.starred ? 'starred' : ''}" 
                        onclick="event.stopPropagation(); searchFiltersSystem.toggleStar('${filter.id}')">
                        <i data-lucide="${filter.starred ? 'star' : 'star'}"></i>
                    </button>
                    <span class="filter-name">${filter.name}</span>
                </div>
                <div class="filter-meta">
                    ${filter.shared ? '<i data-lucide="users" class="shared-icon"></i>' : ''}
                </div>
                <button class="btn-icon-sm" onclick="event.stopPropagation(); searchFiltersSystem.filterMenu('${filter.id}', this)">
                    <i data-lucide="more-horizontal"></i>
                </button>
            </div>
        `;
    }
    
    renderMainContent() {
        if (this.searchMode === 'quick') {
            return this.renderQuickSearch();
        } else {
            return this.renderAdvancedSearch();
        }
    }
    
    renderQuickSearch() {
        return `
            <div class="search-main">
                <div class="quick-search">
                    <div class="search-input-container">
                        <i data-lucide="search"></i>
                        <input type="text" 
                            class="quick-search-input" 
                            placeholder="Search issues, projects, or filters..."
                            oninput="searchFiltersSystem.handleQuickSearch(this.value)"
                            onkeydown="searchFiltersSystem.handleSearchKeydown(event)" />
                        <div class="search-suggestions" id="searchSuggestions" style="display: none;"></div>
                    </div>
                    
                    <div class="search-filters-bar">
                        <button class="filter-chip" onclick="searchFiltersSystem.addQuickFilter('type', 'Bug')">
                            <i data-lucide="bug"></i>
                            Type: Bug
                        </button>
                        <button class="filter-chip" onclick="searchFiltersSystem.addQuickFilter('status', 'Open')">
                            <i data-lucide="circle-dot"></i>
                            Status: Open
                        </button>
                        <button class="filter-chip" onclick="searchFiltersSystem.addQuickFilter('assignee', 'me')">
                            <i data-lucide="user"></i>
                            Assigned to me
                        </button>
                        <button class="filter-chip" onclick="searchFiltersSystem.addQuickFilter('priority', 'High')">
                            <i data-lucide="arrow-up"></i>
                            High Priority
                        </button>
                    </div>
                    
                    <div class="active-filters" id="activeFilters"></div>
                    
                    ${this.renderSearchResults()}
                </div>
            </div>
        `;
    }
    
    renderAdvancedSearch() {
        return `
            <div class="search-main">
                <div class="advanced-search">
                    <div class="search-builder">
                        <h3>Advanced Search Builder</h3>
                        
                        <div class="field-groups">
                            <div class="field-group">
                                <label>Project</label>
                                <select multiple>
                                    <option>TEST</option>
                                    <option>PROJ</option>
                                    <option>DEV</option>
                                </select>
                            </div>
                            
                            <div class="field-group">
                                <label>Issue Type</label>
                                <div class="checkbox-group">
                                    <label><input type="checkbox" /> Story</label>
                                    <label><input type="checkbox" /> Task</label>
                                    <label><input type="checkbox" /> Bug</label>
                                    <label><input type="checkbox" /> Epic</label>
                                </div>
                            </div>
                            
                            <div class="field-group">
                                <label>Status</label>
                                <div class="checkbox-group">
                                    <label><input type="checkbox" /> To Do</label>
                                    <label><input type="checkbox" /> In Progress</label>
                                    <label><input type="checkbox" /> Done</label>
                                </div>
                            </div>
                            
                            <div class="field-group">
                                <label>Assignee</label>
                                <input type="text" placeholder="Search users..." />
                            </div>
                            
                            <div class="field-group">
                                <label>Priority</label>
                                <select>
                                    <option value="">Any</option>
                                    <option>Critical</option>
                                    <option>High</option>
                                    <option>Medium</option>
                                    <option>Low</option>
                                </select>
                            </div>
                            
                            <div class="field-group">
                                <label>Created Date</label>
                                <select>
                                    <option>Any time</option>
                                    <option>Last 7 days</option>
                                    <option>Last 30 days</option>
                                    <option>Custom range...</option>
                                </select>
                            </div>
                            
                            <div class="field-group">
                                <label>Labels</label>
                                <input type="text" placeholder="Enter labels..." />
                            </div>
                            
                            <div class="field-group">
                                <label>Search in</label>
                                <div class="checkbox-group">
                                    <label><input type="checkbox" checked /> Summary</label>
                                    <label><input type="checkbox" checked /> Description</label>
                                    <label><input type="checkbox" /> Comments</label>
                                    <label><input type="checkbox" /> Attachments</label>
                                </div>
                            </div>
                        </div>
                        
                        <div class="search-actions">
                            <button class="btn btn-secondary" onclick="searchFiltersSystem.resetAdvancedSearch()">
                                Reset
                            </button>
                            <button class="btn btn-primary" onclick="searchFiltersSystem.executeAdvancedSearch()">
                                <i data-lucide="search"></i>
                                Search
                            </button>
                        </div>
                    </div>
                    
                    ${this.renderSearchResults()}
                </div>
            </div>
        `;
    }
    
    renderSearchResults() {
        const results = [
            { key: 'TEST-123', summary: 'Fix login bug', type: 'Bug', status: 'In Progress', assignee: 'John Doe' },
            { key: 'TEST-122', summary: 'Add new feature', type: 'Story', status: 'To Do', assignee: 'Jane Smith' },
            { key: 'TEST-121', summary: 'Update documentation', type: 'Task', status: 'Done', assignee: 'Bob Johnson' }
        ];
        
        return `
            <div class="search-results">
                <div class="results-header">
                    <h4>Search Results</h4>
                    <span class="results-count">${results.length} issues found</span>
                </div>
                
                <div class="results-list">
                    ${results.map(issue => `
                        <div class="result-item">
                            <a href="#" class="issue-key">${issue.key}</a>
                            <span class="issue-type">${issue.type}</span>
                            <div class="issue-summary">${issue.summary}</div>
                            <div class="issue-meta">
                                <span class="status-badge status-${issue.status.toLowerCase().replace(' ', '-')}">${issue.status}</span>
                                <span class="assignee">${issue.assignee}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    // Methods
    setSearchMode(mode) {
        this.searchMode = mode;
        const container = document.querySelector('.search-filters-container').parentElement;
        this.render(container);
    }
    
    selectFilter(filterId) {
        this.activeFilter = filterId;
        const container = document.querySelector('.search-filters-container').parentElement;
        this.render(container);
    }
    
    toggleStar(filterId) {
        const filter = this.savedFilters.find(f => f.id === filterId);
        if (filter) {
            filter.starred = !filter.starred;
            const container = document.querySelector('.search-filters-container').parentElement;
            this.render(container);
        }
    }
    
    handleQuickSearch(value) {
        if (value.length >= 2) {
            this.showSearchSuggestions(value);
        } else {
            document.getElementById('searchSuggestions').style.display = 'none';
        }
    }
    
    showSearchSuggestions(query) {
        const suggestions = this.getSearchSuggestions(query);
        const suggestionsEl = document.getElementById('searchSuggestions');
        
        if (suggestions.length > 0) {
            suggestionsEl.innerHTML = suggestions.map(s => `
                <div class="suggestion-item" onclick="searchFiltersSystem.selectSuggestion('${s.value}')">
                    <i data-lucide="${s.icon}"></i>
                    <span>${s.label}</span>
                </div>
            `).join('');
            suggestionsEl.style.display = 'block';
            if (typeof lucide !== 'undefined') lucide.createIcons();
        } else {
            suggestionsEl.style.display = 'none';
        }
    }
    
    getSearchSuggestions(query) {
        // Mock suggestions with typo correction
        const corrected = this.correctTypo(query);
        const suggestions = [];
        
        if (corrected !== query) {
            suggestions.push({ icon: 'alert-circle', label: `Did you mean: ${corrected}?`, value: corrected });
        }
        
        suggestions.push(
            { icon: 'file-text', label: `TEST-123: Fix ${query}`, value: 'TEST-123' },
            { icon: 'tag', label: `Label: ${query}`, value: `label:${query}` },
            { icon: 'user', label: `User: ${query}`, value: `assignee:${query}` }
        );
        
        return suggestions;
    }
    
    correctTypo(query) {
        // Simple typo correction examples
        const corrections = {
            'bug': ['bug', 'bgu', 'buh'],
            'task': ['task', 'taks', 'tasc'],
            'story': ['story', 'sotry', 'strory']
        };
        
        for (const [correct, typos] of Object.entries(corrections)) {
            if (typos.includes(query.toLowerCase())) {
                return correct;
            }
        }
        return query;
    }
    
    openGlobalSearch() {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay global-search-modal';
        modal.innerHTML = `
            <div class="modal global-search-dialog">
                <div class="global-search-input">
                    <i data-lucide="search"></i>
                    <input type="text" 
                        placeholder="Search everywhere..." 
                        autofocus
                        oninput="searchFiltersSystem.globalSearchInput(this.value)" />
                    <button class="btn-icon" onclick="this.closest('.modal-overlay').remove()">
                        <i data-lucide="x"></i>
                    </button>
                </div>
                <div class="global-search-results" id="globalSearchResults">
                    ${this.renderGlobalSearchEmpty()}
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        if (typeof lucide !== 'undefined') lucide.createIcons();
        
        // Close on Escape
        modal.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') modal.remove();
        });
    }
    
    renderGlobalSearchEmpty() {
        return `
            <div class="global-search-empty">
                <i data-lucide="search"></i>
                <p>Start typing to search issues, projects, filters...</p>
            </div>
        `;
    }
    
    globalSearchInput(value) {
        const resultsEl = document.getElementById('globalSearchResults');
        if (value.length >= 2) {
            resultsEl.innerHTML = `
                <div class="global-search-section">
                    <h5>Issues</h5>
                    <div class="global-result-item">TEST-123: Fix login bug</div>
                    <div class="global-result-item">TEST-122: Add feature</div>
                </div>
                <div class="global-search-section">
                    <h5>Filters</h5>
                    <div class="global-result-item">My Open Issues</div>
                </div>
            `;
        } else {
            resultsEl.innerHTML = this.renderGlobalSearchEmpty();
        }
    }
    
    createFilter() {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h3>Create Filter</h3>
                    <button class="btn-icon" onclick="this.closest('.modal-overlay').remove()">
                        <i data-lucide="x"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label>Filter Name</label>
                        <input type="text" placeholder="Enter filter name" />
                    </div>
                    <div class="form-group">
                        <label>JQL Query</label>
                        <textarea rows="3" placeholder="Enter JQL query"></textarea>
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" /> Share with others</label>
                        <label><input type="checkbox" /> Set as favorite</label>
                    </div>
                    <div class="form-group">
                        <label>Subscribe to notifications</label>
                        <select>
                            <option value="">Never</option>
                            <option>Daily</option>
                            <option>Weekly</option>
                            <option>Monthly</option>
                        </select>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                    <button class="btn btn-primary" onclick="searchFiltersSystem.saveFilter(); this.closest('.modal-overlay').remove()">
                        Create Filter
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        if (typeof lucide !== 'undefined') lucide.createIcons();
    }
    
    saveFilter() {
        this.showToast('Filter created successfully');
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
const searchFiltersSystem = new AdvancedSearchFiltersSystem();
