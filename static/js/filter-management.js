/**
 * Filter Management System
 * Favourite filters, view all, create/edit/delete, share, search
 */

class FilterManagement {
    constructor() {
        this.filters = [];
        this.favouriteFilters = [];
        this.currentFilter = null;
        
        this.init();
    }

    async init() {
        await this.loadFilters();
        await this.loadFavouriteFilters();
        console.log('FilterManagement initialized');
    }

    async loadFilters() {
        try {
            const response = await fetch('/api/filters');
            this.filters = await response.json();
        } catch (error) {
            console.error('Failed to load filters:', error);
            this.loadMockFilters();
        }
    }

    loadMockFilters() {
        this.filters = [
            {
                id: 1,
                name: 'My Open Issues',
                jql: 'assignee = currentUser() AND resolution = Unresolved',
                owner: 'John Doe',
                starred: true,
                subscribers: 5,
                lastUpdated: '2026-01-20',
                isPublic: false
            },
            {
                id: 2,
                name: 'High Priority Bugs',
                jql: 'type = Bug AND priority = High',
                owner: 'Jane Smith',
                starred: true,
                subscribers: 12,
                lastUpdated: '2026-01-18',
                isPublic: true
            },
            {
                id: 3,
                name: 'Sprint Backlog',
                jql: 'sprint = currentSprint() AND status != Done',
                owner: 'John Doe',
                starred: false,
                subscribers: 8,
                lastUpdated: '2026-01-15',
                isPublic: false
            }
        ];
    }

    async loadFavouriteFilters() {
        this.favouriteFilters = [
            { id: -1, name: 'All Issues', jql: '', icon: 'inbox', count: 142 },
            { id: -2, name: 'My Open Issues', jql: 'assignee = currentUser() AND resolution = Unresolved', icon: 'user', count: 23 },
            { id: -3, name: 'Reported by Me', jql: 'reporter = currentUser()', icon: 'flag', count: 15 },
            { id: -4, name: 'Viewed Recently', jql: '', icon: 'clock', count: 8 }
        ];
    }

    renderFiltersView(container) {
        const html = `
            <div class="filters-container">
                <div class="filters-header">
                    <div class="filters-title">
                        <h1>Filters</h1>
                        <p>${this.filters.length} filters • ${this.calculateTotalSubscribers()} total subscribers</p>
                    </div>
                    <div class="filters-actions">
                        <button class="btn-secondary" onclick="filterManagement.importFilter()">
                            <i data-lucide="download"></i>
                            Import
                        </button>
                        <button class="btn-primary" onclick="filterManagement.createNewFilter()">
                            <i data-lucide="plus"></i>
                            Create Filter
                        </button>
                    </div>
                </div>

                <div class="filters-search">
                    <div class="search-box">
                        <i data-lucide="search"></i>
                        <input type="text" placeholder="Search filters..." 
                               oninput="filterManagement.searchFilters(this.value)">
                    </div>
                    <div class="filter-tabs">
                        <button class="tab-btn active" onclick="filterManagement.filterBy('all')">
                            All
                        </button>
                        <button class="tab-btn" onclick="filterManagement.filterBy('starred')">
                            <i data-lucide="star"></i>
                            Starred
                        </button>
                        <button class="tab-btn" onclick="filterManagement.filterBy('owned')">
                            <i data-lucide="user"></i>
                            Owned by me
                        </button>
                    </div>
                </div>

                <div class="filters-table-container">
                    <table class="filters-table">
                        <thead>
                            <tr>
                                <th width="40"></th>
                                <th>Name</th>
                                <th>Owner</th>
                                <th>Subscribers</th>
                                <th>Last Updated</th>
                                <th width="100">Actions</th>
                            </tr>
                        </thead>
                        <tbody id="filtersTableBody">
                            ${this.renderFilterRows()}
                        </tbody>
                    </table>
                </div>
            </div>
        `;

        container.innerHTML = html;
        if (window.lucide) lucide.createIcons();
    }

    renderFilterRows() {
        return this.filters.map(filter => `
            <tr class="filter-row" onclick="filterManagement.viewFilter(${filter.id})">
                <td>
                    <button class="btn-icon star-btn ${filter.starred ? 'starred' : ''}" 
                            onclick="event.stopPropagation(); filterManagement.toggleStar(${filter.id})">
                        <i data-lucide="star"></i>
                    </button>
                </td>
                <td>
                    <div class="filter-name-cell">
                        <strong>${filter.name}</strong>
                        ${filter.isPublic ? '<span class="public-badge">Public</span>' : ''}
                    </div>
                </td>
                <td>${filter.owner}</td>
                <td>
                    <span class="subscribers-count">
                        <i data-lucide="users"></i>
                        ${filter.subscribers}
                    </span>
                </td>
                <td>${this.formatDate(filter.lastUpdated)}</td>
                <td>
                    <div class="row-actions" onclick="event.stopPropagation()">
                        <button class="btn-icon" onclick="filterManagement.editFilter(${filter.id})">
                            <i data-lucide="edit"></i>
                        </button>
                        <button class="btn-icon" onclick="filterManagement.shareFilter(${filter.id})">
                            <i data-lucide="share-2"></i>
                        </button>
                        <button class="btn-icon" onclick="filterManagement.deleteFilter(${filter.id})">
                            <i data-lucide="trash-2"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    renderFavouriteFiltersSidebar(container) {
        const html = `
            <div class="favourite-filters-sidebar">
                <h3>Favourite Filters</h3>
                <div class="favourite-filters-list">
                    ${this.favouriteFilters.map(filter => `
                        <div class="favourite-filter-item ${filter.id === this.currentFilter?.id ? 'active' : ''}" 
                             onclick="filterManagement.applyFilter(${filter.id})">
                            <i data-lucide="${filter.icon}"></i>
                            <span class="filter-name">${filter.name}</span>
                            <span class="filter-count">${filter.count}</span>
                        </div>
                    `).join('')}
                </div>
                <div class="custom-filters-section">
                    <h3>My Filters</h3>
                    <div class="custom-filters-list">
                        ${this.filters.filter(f => f.starred).map(filter => `
                            <div class="favourite-filter-item" onclick="filterManagement.applyFilter(${filter.id})">
                                <i data-lucide="filter"></i>
                                <span class="filter-name">${filter.name}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
                <button class="view-all-filters-btn" onclick="filterManagement.viewAllFilters()">
                    <i data-lucide="list"></i>
                    View all filters
                </button>
            </div>
        `;

        container.innerHTML = html;
        if (window.lucide) lucide.createIcons();
    }

    createNewFilter() {
        this.currentFilter = {
            id: Date.now(),
            name: '',
            jql: '',
            description: '',
            starred: false,
            isPublic: false
        };
        this.openFilterModal();
    }

    openFilterModal() {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay active';
        modal.innerHTML = `
            <div class="modal-dialog filter-modal">
                <div class="modal-header">
                    <h2>${this.currentFilter.id > 1000 ? 'Edit' : 'Create'} Filter</h2>
                    <button class="btn-icon" onclick="filterManagement.closeModal()">
                        <i data-lucide="x"></i>
                    </button>
                </div>

                <div class="modal-body">
                    <div class="form-group">
                        <label>Filter Name *</label>
                        <input type="text" id="filterName" class="form-input" 
                               value="${this.currentFilter.name}" 
                               placeholder="Enter filter name">
                    </div>

                    <div class="form-group">
                        <label>Description</label>
                        <textarea id="filterDescription" class="form-textarea" 
                                  placeholder="Describe what this filter shows"
                        >${this.currentFilter.description || ''}</textarea>
                    </div>

                    <div class="form-group">
                        <label>JQL Query *</label>
                        <div class="jql-editor">
                            <textarea id="filterJQL" class="jql-textarea" 
                                      placeholder="e.g. project = PROJ AND status = 'In Progress'"
                            >${this.currentFilter.jql}</textarea>
                            <button class="btn-secondary jql-builder-btn" 
                                    onclick="filterManagement.openJQLBuilder()">
                                <i data-lucide="code"></i>
                                Open Builder
                            </button>
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="checkbox-label">
                            <input type="checkbox" id="filterStarred" 
                                   ${this.currentFilter.starred ? 'checked' : ''}>
                            <span>Add to favourites</span>
                        </label>
                    </div>

                    <div class="form-group">
                        <label class="checkbox-label">
                            <input type="checkbox" id="filterPublic" 
                                   ${this.currentFilter.isPublic ? 'checked' : ''}>
                            <span>Share publicly</span>
                        </label>
                    </div>
                </div>

                <div class="modal-footer">
                    <button class="btn-secondary" onclick="filterManagement.closeModal()">
                        Cancel
                    </button>
                    <button class="btn-primary" onclick="filterManagement.saveFilter()">
                        <i data-lucide="save"></i>
                        Save Filter
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        if (window.lucide) lucide.createIcons();
    }

    shareFilter(filterId) {
        const filter = this.filters.find(f => f.id === filterId);
        if (!filter) return;

        const modal = document.createElement('div');
        modal.className = 'modal-overlay active';
        modal.innerHTML = `
            <div class="modal-dialog share-modal">
                <div class="modal-header">
                    <h2>Share Filter</h2>
                    <button class="btn-icon" onclick="filterManagement.closeModal()">
                        <i data-lucide="x"></i>
                    </button>
                </div>

                <div class="modal-body">
                    <div class="share-link-section">
                        <label>Share Link</label>
                        <div class="link-input-group">
                            <input type="text" readonly class="form-input" 
                                   value="https://jira.example.com/filters/${filterId}">
                            <button class="btn-secondary" onclick="filterManagement.copyLink()">
                                <i data-lucide="copy"></i>
                                Copy
                            </button>
                        </div>
                    </div>

                    <div class="share-permissions-section">
                        <label>Share with Users/Groups</label>
                        <div class="user-search-box">
                            <i data-lucide="search"></i>
                            <input type="text" placeholder="Search users or groups...">
                        </div>

                        <div class="shared-users-list">
                            <div class="shared-user-item">
                                <div class="avatar-sm">JD</div>
                                <div class="user-info">
                                    <span class="user-name">John Doe</span>
                                    <span class="user-email">john@example.com</span>
                                </div>
                                <select class="permission-select">
                                    <option value="view">Can view</option>
                                    <option value="edit">Can edit</option>
                                </select>
                                <button class="btn-icon btn-sm">
                                    <i data-lucide="x"></i>
                                </button>
                            </div>
                        </div>
                    </div>

                    <div class="public-access-section">
                        <label class="checkbox-label">
                            <input type="checkbox" ${filter.isPublic ? 'checked' : ''}>
                            <span>Anyone with the link can view</span>
                        </label>
                    </div>
                </div>

                <div class="modal-footer">
                    <button class="btn-primary" onclick="filterManagement.closeModal()">
                        Done
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        if (window.lucide) lucide.createIcons();
    }

    deleteFilter(filterId) {
        if (confirm('Are you sure you want to delete this filter?')) {
            this.filters = this.filters.filter(f => f.id !== filterId);
            this.refreshFiltersTable();
            alert('Filter deleted successfully');
        }
    }

    saveFilter() {
        const name = document.getElementById('filterName')?.value;
        const description = document.getElementById('filterDescription')?.value;
        const jql = document.getElementById('filterJQL')?.value;
        const starred = document.getElementById('filterStarred')?.checked;
        const isPublic = document.getElementById('filterPublic')?.checked;

        if (!name || !jql) {
            alert('Please fill in required fields');
            return;
        }

        this.currentFilter.name = name;
        this.currentFilter.description = description;
        this.currentFilter.jql = jql;
        this.currentFilter.starred = starred;
        this.currentFilter.isPublic = isPublic;

        alert(`Filter "${name}" saved successfully!`);
        this.closeModal();
        this.refreshFiltersTable();
    }

    toggleStar(filterId) {
        const filter = this.filters.find(f => f.id === filterId);
        if (filter) {
            filter.starred = !filter.starred;
            this.refreshFiltersTable();
        }
    }

    refreshFiltersTable() {
        const tbody = document.getElementById('filtersTableBody');
        if (tbody) {
            tbody.innerHTML = this.renderFilterRows();
            if (window.lucide) lucide.createIcons();
        }
    }

    calculateTotalSubscribers() {
        return this.filters.reduce((sum, filter) => sum + filter.subscribers, 0);
    }

    formatDate(dateStr) {
        const date = new Date(dateStr);
        const options = { month: 'short', day: 'numeric', year: 'numeric' };
        return date.toLocaleDateString('en-US', options);
    }

    searchFilters(query) {
        console.log('Search filters:', query);
    }

    filterBy(type) {
        console.log('Filter by:', type);
    }

    viewFilter(filterId) {
        console.log('View filter:', filterId);
    }

    editFilter(filterId) {
        const filter = this.filters.find(f => f.id === filterId);
        if (filter) {
            this.currentFilter = { ...filter };
            this.openFilterModal();
        }
    }

    applyFilter(filterId) {
        console.log('Apply filter:', filterId);
    }

    viewAllFilters() {
        console.log('View all filters');
    }

    openJQLBuilder() {
        alert('JQL Builder would open here');
    }

    copyLink() {
        alert('Link copied to clipboard!');
    }

    importFilter() {
        alert('Import filter dialog would open');
    }

    closeModal() {
        const modal = document.querySelector('.modal-overlay');
        if (modal) modal.remove();
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.filterManagement = new FilterManagement();
});
