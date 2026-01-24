/**
 * Advanced Search Manager - JIRA-style JQL (JIRA Query Language) search builder
 * Enables complex query building with field selectors, operators, and saved filters
 */

class AdvancedSearchManager {
    constructor() {
        this.filters = [];
        this.savedFilters = this.loadSavedFilters();
        this.fields = [
            { id: 'title', label: 'Summary', type: 'text' },
            { id: 'assignee', label: 'Assignee', type: 'user' },
            { id: 'status', label: 'Status', type: 'select', options: ['To Do', 'In Progress', 'In Review', 'Done'] },
            { id: 'priority', label: 'Priority', type: 'select', options: ['Critical', 'High', 'Medium', 'Low'] },
            { id: 'type', label: 'Type', type: 'select', options: ['Bug', 'Feature', 'Story', 'Task'] },
            { id: 'epic', label: 'Epic', type: 'text' },
            { id: 'sprint', label: 'Sprint', type: 'text' },
            { id: 'created', label: 'Created', type: 'date' },
            { id: 'updated', label: 'Updated', type: 'date' },
            { id: 'dueDate', label: 'Due Date', type: 'date' },
            { id: 'storyPoints', label: 'Story Points', type: 'number' }
        ];
        this.operators = {
            text: ['contains', 'does not contain', 'equals', 'does not equal', 'is empty', 'is not empty'],
            select: ['equals', 'does not equal', 'in', 'not in', 'is empty', 'is not empty'],
            user: ['equals', 'does not equal', 'is', 'is not', 'currentUser()', 'is empty', 'is not empty'],
            date: ['equals', 'before', 'after', 'between', 'is empty', 'is not empty'],
            number: ['equals', 'greater than', 'less than', 'between', 'is empty', 'is not empty']
        };
        this.init();
    }

    init() {
        this.createSearchModal();
        this.setupEventListeners();
    }

    createSearchModal() {
        const modal = document.createElement('div');
        modal.id = 'advancedSearchModal';
        modal.className = 'advanced-search-modal';
        modal.innerHTML = `
            <div class="advanced-search-overlay"></div>
            <div class="advanced-search-container">
                <div class="advanced-search-header">
                    <div>
                        <h2 class="advanced-search-title">Advanced Search</h2>
                        <p class="advanced-search-subtitle">Build complex queries with JQL-style filtering</p>
                    </div>
                    <button class="modal-close" id="closeAdvancedSearch">
                        <i data-lucide="x"></i>
                    </button>
                </div>

                <div class="advanced-search-body">
                    <!-- Saved Filters -->
                    <div class="saved-filters-section">
                        <div class="section-header">
                            <h3>Saved Filters</h3>
                            <button class="btn btn-sm btn-ghost" id="showSavedFilters">
                                <i data-lucide="bookmark"></i>
                                Manage
                            </button>
                        </div>
                        <div class="saved-filters-list" id="savedFiltersList"></div>
                    </div>

                    <!-- Query Builder -->
                    <div class="query-builder-section">
                        <div class="section-header">
                            <h3>Query Builder</h3>
                            <button class="btn btn-sm btn-ghost" id="clearAllFilters">
                                <i data-lucide="x-circle"></i>
                                Clear all
                            </button>
                        </div>
                        <div class="filter-rows" id="filterRows"></div>
                        <button class="btn btn-sm btn-secondary" id="addFilterRow">
                            <i data-lucide="plus"></i>
                            Add filter
                        </button>
                    </div>

                    <!-- JQL Preview -->
                    <div class="jql-preview-section">
                        <div class="section-header">
                            <h3>JQL Preview</h3>
                            <button class="btn btn-sm btn-ghost" id="copyJQL">
                                <i data-lucide="copy"></i>
                                Copy
                            </button>
                        </div>
                        <div class="jql-preview" id="jqlPreview">
                            <code>No filters applied</code>
                        </div>
                    </div>

                    <!-- Common Patterns -->
                    <div class="common-patterns-section">
                        <div class="section-header">
                            <h3>Common Patterns</h3>
                        </div>
                        <div class="pattern-chips">
                            <button class="pattern-chip" data-pattern="assigned-to-me">
                                Assigned to me
                            </button>
                            <button class="pattern-chip" data-pattern="created-by-me">
                                Created by me
                            </button>
                            <button class="pattern-chip" data-pattern="updated-recently">
                                Updated recently
                            </button>
                            <button class="pattern-chip" data-pattern="high-priority">
                                High priority
                            </button>
                            <button class="pattern-chip" data-pattern="overdue">
                                Overdue
                            </button>
                            <button class="pattern-chip" data-pattern="in-progress">
                                In progress
                            </button>
                        </div>
                    </div>
                </div>

                <div class="advanced-search-footer">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <input type="text" id="filterName" class="form-input" placeholder="Filter name..." style="width: 200px;">
                        <button class="btn btn-ghost" id="saveFilter">
                            <i data-lucide="save"></i>
                            Save filter
                        </button>
                    </div>
                    <div style="display: flex; gap: 8px;">
                        <button class="btn btn-ghost" id="cancelSearch">Cancel</button>
                        <button class="btn btn-primary" id="applySearch">
                            <i data-lucide="search"></i>
                            Search
                        </button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        this.renderSavedFilters();
        this.addFilterRow();
    }

    setupEventListeners() {
        document.getElementById('closeAdvancedSearch')?.addEventListener('click', () => this.close());
        document.getElementById('cancelSearch')?.addEventListener('click', () => this.close());
        document.getElementById('addFilterRow')?.addEventListener('click', () => this.addFilterRow());
        document.getElementById('clearAllFilters')?.addEventListener('click', () => this.clearAllFilters());
        document.getElementById('copyJQL')?.addEventListener('click', () => this.copyJQL());
        document.getElementById('saveFilter')?.addEventListener('click', () => this.saveCurrentFilter());
        document.getElementById('applySearch')?.addEventListener('click', () => this.applySearch());

        // Common patterns
        document.querySelectorAll('.pattern-chip').forEach(chip => {
            chip.addEventListener('click', () => this.applyPattern(chip.dataset.pattern));
        });

        // Overlay click to close
        document.querySelector('.advanced-search-overlay')?.addEventListener('click', () => this.close());
    }

    open() {
        document.getElementById('advancedSearchModal').classList.add('show');
        lucide.createIcons();
    }

    close() {
        document.getElementById('advancedSearchModal').classList.remove('show');
    }

    addFilterRow(filter = null) {
        const row = document.createElement('div');
        row.className = 'filter-row';
        row.innerHTML = `
            <div class="filter-row-content">
                <select class="filter-field form-input">
                    <option value="">Select field...</option>
                    ${this.fields.map(f => `<option value="${f.id}"${filter && filter.field === f.id ? ' selected' : ''}>${f.label}</option>`).join('')}
                </select>
                <select class="filter-operator form-input">
                    <option value="">Operator...</option>
                </select>
                <input type="text" class="filter-value form-input" placeholder="Value..." ${filter ? `value="${filter.value}"` : ''}>
                <button class="btn btn-icon btn-ghost remove-filter">
                    <i data-lucide="trash-2"></i>
                </button>
            </div>
            <div class="filter-row-logic">
                <select class="filter-logic form-input">
                    <option value="AND">AND</option>
                    <option value="OR">OR</option>
                </select>
            </div>
        `;

        const container = document.getElementById('filterRows');
        container.appendChild(row);

        // Setup field change handler
        const fieldSelect = row.querySelector('.filter-field');
        const operatorSelect = row.querySelector('.filter-operator');
        const valueInput = row.querySelector('.filter-value');

        fieldSelect.addEventListener('change', () => {
            const field = this.fields.find(f => f.id === fieldSelect.value);
            if (field) {
                operatorSelect.innerHTML = '<option value="">Operator...</option>' +
                    this.operators[field.type].map(op => `<option value="${op}">${op}</option>`).join('');
                
                // Update value input type
                if (field.type === 'date') {
                    valueInput.type = 'date';
                } else if (field.type === 'number') {
                    valueInput.type = 'number';
                } else if (field.type === 'select') {
                    const select = document.createElement('select');
                    select.className = 'filter-value form-input';
                    select.innerHTML = '<option value="">Select...</option>' +
                        field.options.map(opt => `<option value="${opt}">${opt}</option>`).join('');
                    valueInput.replaceWith(select);
                }
            }
            this.updateJQLPreview();
        });

        operatorSelect.addEventListener('change', () => this.updateJQLPreview());
        valueInput.addEventListener('input', () => this.updateJQLPreview());

        // Remove filter handler
        row.querySelector('.remove-filter').addEventListener('click', () => {
            row.remove();
            this.updateJQLPreview();
        });

        lucide.createIcons();
        this.updateJQLPreview();
    }

    clearAllFilters() {
        document.getElementById('filterRows').innerHTML = '';
        this.addFilterRow();
    }

    updateJQLPreview() {
        const rows = document.querySelectorAll('.filter-row');
        let jql = '';

        rows.forEach((row, index) => {
            const field = row.querySelector('.filter-field').value;
            const operator = row.querySelector('.filter-operator').value;
            const value = row.querySelector('.filter-value').value;
            const logic = row.querySelector('.filter-logic').value;

            if (field && operator) {
                if (index > 0) jql += ` ${logic} `;
                jql += `${field} ${operator} "${value}"`;
            }
        });

        const preview = document.getElementById('jqlPreview');
        preview.innerHTML = jql ? `<code>${jql}</code>` : '<code>No filters applied</code>';
    }

    copyJQL() {
        const jql = document.getElementById('jqlPreview').textContent;
        navigator.clipboard.writeText(jql);
        window.notificationManager.addNotification({
            title: 'Copied',
            message: 'JQL query copied to clipboard',
            type: 'success'
        });
    }

    applyPattern(pattern) {
        this.clearAllFilters();

        const patterns = {
            'assigned-to-me': [
                { field: 'assignee', operator: 'currentUser()' }
            ],
            'created-by-me': [
                { field: 'created', operator: 'currentUser()' }
            ],
            'updated-recently': [
                { field: 'updated', operator: 'after', value: '-7d' }
            ],
            'high-priority': [
                { field: 'priority', operator: 'in', value: 'Critical,High' }
            ],
            'overdue': [
                { field: 'dueDate', operator: 'before', value: 'today()' }
            ],
            'in-progress': [
                { field: 'status', operator: 'equals', value: 'In Progress' }
            ]
        };

        const filters = patterns[pattern];
        if (filters) {
            filters.forEach(filter => this.addFilterRow(filter));
        }
    }

    saveCurrentFilter() {
        const name = document.getElementById('filterName').value.trim();
        if (!name) {
            window.notificationManager.addNotification({
                title: 'Name Required',
                message: 'Please enter a name for this filter',
                type: 'warning'
            });
            return;
        }

        const rows = document.querySelectorAll('.filter-row');
        const filters = [];
        rows.forEach(row => {
            const field = row.querySelector('.filter-field').value;
            const operator = row.querySelector('.filter-operator').value;
            const value = row.querySelector('.filter-value').value;
            if (field && operator) {
                filters.push({ field, operator, value });
            }
        });

        this.savedFilters.push({ name, filters, created: new Date().toISOString() });
        localStorage.setItem('savedFilters', JSON.stringify(this.savedFilters));
        this.renderSavedFilters();

        window.notificationManager.addNotification({
            title: 'Filter Saved',
            message: `"${name}" saved successfully`,
            type: 'success'
        });

        document.getElementById('filterName').value = '';
    }

    loadSavedFilters() {
        const saved = localStorage.getItem('savedFilters');
        return saved ? JSON.parse(saved) : [];
    }

    renderSavedFilters() {
        const container = document.getElementById('savedFiltersList');
        if (this.savedFilters.length === 0) {
            container.innerHTML = '<p style="color: var(--jira-text-secondary); font-size: 13px;">No saved filters</p>';
            return;
        }

        container.innerHTML = this.savedFilters.map((filter, index) => `
            <div class="saved-filter-item">
                <div class="saved-filter-info">
                    <div class="saved-filter-name">${filter.name}</div>
                    <div class="saved-filter-meta">${filter.filters.length} filters</div>
                </div>
                <div class="saved-filter-actions">
                    <button class="btn btn-xs btn-ghost" onclick="window.advancedSearchManager.loadFilter(${index})">
                        <i data-lucide="download"></i>
                    </button>
                    <button class="btn btn-xs btn-ghost" onclick="window.advancedSearchManager.deleteFilter(${index})">
                        <i data-lucide="trash-2"></i>
                    </button>
                </div>
            </div>
        `).join('');
        lucide.createIcons();
    }

    loadFilter(index) {
        const filter = this.savedFilters[index];
        this.clearAllFilters();
        filter.filters.forEach(f => this.addFilterRow(f));
    }

    deleteFilter(index) {
        this.savedFilters.splice(index, 1);
        localStorage.setItem('savedFilters', JSON.stringify(this.savedFilters));
        this.renderSavedFilters();
    }

    applySearch() {
        const jql = document.getElementById('jqlPreview').textContent;
        console.log('Applying search:', jql);
        
        window.notificationManager.addNotification({
            title: 'Search Applied',
            message: 'Filtering results...',
            type: 'info'
        });

        this.close();
        // Here you would actually apply the filters to the issue list
    }
}

// CSS for advanced search
const style = document.createElement('style');
style.textContent = `
    .advanced-search-modal {
        display: none;
        position: fixed;
        inset: 0;
        z-index: 10000;
    }

    .advanced-search-modal.show {
        display: block;
    }

    .advanced-search-overlay {
        position: absolute;
        inset: 0;
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(4px);
    }

    .advanced-search-container {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 90%;
        max-width: 900px;
        max-height: 90vh;
        background: var(--jira-darker-bg, #161a1d);
        border: 1px solid var(--jira-border, #2c333a);
        border-radius: 8px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        display: flex;
        flex-direction: column;
    }

    .advanced-search-header {
        padding: 20px 24px;
        border-bottom: 1px solid var(--jira-border, #2c333a);
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
    }

    .advanced-search-title {
        font-size: 20px;
        font-weight: 600;
        color: var(--jira-text, #b6c2cf);
        margin: 0 0 4px 0;
    }

    .advanced-search-subtitle {
        font-size: 13px;
        color: var(--jira-text-secondary, #8c9bab);
        margin: 0;
    }

    .advanced-search-body {
        flex: 1;
        overflow-y: auto;
        padding: 24px;
    }

    .advanced-search-footer {
        padding: 16px 24px;
        border-top: 1px solid var(--jira-border, #2c333a);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .section-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
    }

    .section-header h3 {
        font-size: 14px;
        font-weight: 600;
        color: var(--jira-text-secondary, #8c9bab);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin: 0;
    }

    .saved-filters-section,
    .query-builder-section,
    .jql-preview-section,
    .common-patterns-section {
        margin-bottom: 24px;
    }

    .saved-filter-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px;
        background: var(--jira-card-bg, #22272b);
        border: 1px solid var(--jira-border, #2c333a);
        border-radius: 4px;
        margin-bottom: 8px;
    }

    .saved-filter-name {
        font-size: 14px;
        font-weight: 500;
        color: var(--jira-text, #b6c2cf);
    }

    .saved-filter-meta {
        font-size: 12px;
        color: var(--jira-text-secondary, #8c9bab);
    }

    .saved-filter-actions {
        display: flex;
        gap: 4px;
    }

    .filter-row {
        margin-bottom: 8px;
    }

    .filter-row-content {
        display: flex;
        gap: 8px;
        align-items: center;
        margin-bottom: 4px;
    }

    .filter-row-content .form-input {
        flex: 1;
        min-width: 120px;
    }

    .filter-row-logic {
        display: flex;
        justify-content: flex-end;
        padding-right: 48px;
    }

    .filter-row-logic .form-input {
        width: 80px;
        font-size: 12px;
        padding: 4px 8px;
    }

    .jql-preview {
        padding: 16px;
        background: var(--jira-card-bg, #22272b);
        border: 1px solid var(--jira-border, #2c333a);
        border-radius: 4px;
        font-family: 'Courier New', monospace;
        font-size: 13px;
        color: #00b8d9;
        overflow-x: auto;
    }

    .pattern-chips {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }

    .pattern-chip {
        padding: 8px 12px;
        background: var(--jira-card-bg, #22272b);
        border: 1px solid var(--jira-border, #2c333a);
        border-radius: 16px;
        font-size: 13px;
        color: var(--jira-text, #b6c2cf);
        cursor: pointer;
        transition: all 0.2s;
    }

    .pattern-chip:hover {
        background: var(--jira-hover, #2c3338);
        border-color: #0052cc;
    }
`;
document.head.appendChild(style);

// Initialize on DOM load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.advancedSearchManager = new AdvancedSearchManager();
    });
} else {
    window.advancedSearchManager = new AdvancedSearchManager();
}
