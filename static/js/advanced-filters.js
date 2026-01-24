/**
 * Advanced Filters - JIRA-style JQL query builder
 * Features: Query builder with autocomplete, saved filters, favorites, quick filters
 */

class AdvancedFilters {
    constructor() {
        this.savedFilters = [];
        this.favoriteFilters = new Set();
        this.currentFilter = null;
        this.queryTokens = [];
        this.suggestions = [];
        
        // JQL field definitions
        this.fields = {
            'project': { type: 'text', operators: ['=', '!=', 'in', 'not in'] },
            'status': { type: 'select', operators: ['=', '!=', 'in', 'not in', 'was', 'was in', 'changed'] },
            'assignee': { type: 'user', operators: ['=', '!=', 'in', 'not in', 'was', 'changed'] },
            'reporter': { type: 'user', operators: ['=', '!=', 'in', 'not in'] },
            'priority': { type: 'select', operators: ['=', '!=', 'in', 'not in', 'changed'] },
            'type': { type: 'select', operators: ['=', '!=', 'in', 'not in'] },
            'created': { type: 'date', operators: ['=', '>', '<', '>=', '<=', 'between'] },
            'updated': { type: 'date', operators: ['=', '>', '<', '>=', '<=', 'between'] },
            'duedate': { type: 'date', operators: ['=', '>', '<', '>=', '<=', 'is empty', 'is not empty'] },
            'sprint': { type: 'text', operators: ['=', '!=', 'in', 'not in'] },
            'labels': { type: 'text', operators: ['=', '!=', 'in', 'not in', 'is empty', 'is not empty'] },
            'text': { type: 'text', operators: ['~', '!~'] },
            'description': { type: 'text', operators: ['~', '!~'] },
            'summary': { type: 'text', operators: ['~', '!~'] }
        };
        
        this.init();
    }

    init() {
        this.createFilterModal();
        this.setupEventListeners();
        this.loadSavedFilters();
    }

    createFilterModal() {
        const modalHTML = `
            <div id="advancedFilterModal" class="filter-modal" style="display: none;">
                <div class="filter-modal-backdrop"></div>
                <div class="filter-modal-container">
                    <div class="filter-modal-header">
                        <h2>Advanced Filters</h2>
                        <button class="btn-icon" id="closeFilterModal">
                            <i data-lucide="x"></i>
                        </button>
                    </div>
                    
                    <div class="filter-modal-body">
                        <!-- Query Builder -->
                        <div class="query-builder-section">
                            <div class="section-header">
                                <h3>Query Builder</h3>
                                <div class="builder-mode-toggle">
                                    <button class="mode-btn active" data-mode="visual">Visual</button>
                                    <button class="mode-btn" data-mode="jql">JQL</button>
                                </div>
                            </div>

                            <!-- Visual Mode -->
                            <div id="visualBuilder" class="builder-mode active">
                                <div class="filter-conditions" id="filterConditions">
                                    <!-- Conditions will be added here -->
                                </div>
                                <button class="btn btn-ghost btn-sm" id="addConditionBtn">
                                    <i data-lucide="plus"></i>
                                    Add Condition
                                </button>
                            </div>

                            <!-- JQL Mode -->
                            <div id="jqlBuilder" class="builder-mode">
                                <div class="jql-input-wrapper">
                                    <textarea id="jqlInput" class="jql-input" 
                                              placeholder="Enter JQL query (e.g., project = TEST AND status = 'In Progress')"
                                              rows="4"></textarea>
                                    <div class="jql-suggestions" id="jqlSuggestions"></div>
                                </div>
                                <div class="jql-syntax-help">
                                    <button class="btn-link" onclick="window.advancedFilters.showJQLHelp()">
                                        <i data-lucide="help-circle"></i>
                                        JQL Syntax Help
                                    </button>
                                </div>
                            </div>

                            <!-- Preview -->
                            <div class="query-preview">
                                <label>Query Preview:</label>
                                <div class="query-display" id="queryDisplay">No conditions added</div>
                            </div>
                        </div>

                        <!-- Results Preview -->
                        <div class="results-section">
                            <div class="results-header">
                                <h4>Results Preview</h4>
                                <span class="results-count" id="resultsCount">0 issues</span>
                            </div>
                            <div class="results-list" id="resultsPreview">
                                <!-- Results will be shown here -->
                            </div>
                        </div>

                        <!-- Actions -->
                        <div class="filter-actions">
                            <button class="btn btn-ghost" id="clearFilterBtn">Clear</button>
                            <button class="btn btn-ghost" id="saveFilterBtn">
                                <i data-lucide="save"></i>
                                Save Filter
                            </button>
                            <button class="btn btn-primary" id="applyFilterBtn">Apply Filter</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Save Filter Dialog -->
            <div id="saveFilterDialog" class="filter-dialog" style="display: none;">
                <div class="filter-modal-backdrop"></div>
                <div class="filter-dialog-container">
                    <div class="filter-dialog-header">
                        <h3>Save Filter</h3>
                        <button class="btn-icon" id="closeSaveDialog">
                            <i data-lucide="x"></i>
                        </button>
                    </div>
                    <div class="filter-dialog-body">
                        <div class="form-group">
                            <label for="filterName">Filter Name *</label>
                            <input type="text" id="filterName" class="form-input" 
                                   placeholder="My Custom Filter" required>
                        </div>
                        <div class="form-group">
                            <label for="filterDescription">Description</label>
                            <textarea id="filterDescription" class="form-input" rows="2"
                                      placeholder="Describe what this filter does..."></textarea>
                        </div>
                        <div class="form-group">
                            <label class="checkbox-label">
                                <input type="checkbox" id="filterFavorite">
                                <span>Add to favorites</span>
                            </label>
                        </div>
                        <div class="form-group">
                            <label class="checkbox-label">
                                <input type="checkbox" id="filterShared">
                                <span>Share with team</span>
                            </label>
                        </div>
                    </div>
                    <div class="filter-dialog-actions">
                        <button class="btn btn-ghost" onclick="document.getElementById('saveFilterDialog').style.display='none'">Cancel</button>
                        <button class="btn btn-primary" id="confirmSaveFilter">Save</button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        if (window.lucide) {
            lucide.createIcons();
        }
    }

    setupEventListeners() {
        // Modal controls
        document.getElementById('closeFilterModal')?.addEventListener('click', () => {
            this.closeModal();
        });

        // Mode toggle
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchMode(e.target.dataset.mode);
            });
        });

        // Add condition
        document.getElementById('addConditionBtn')?.addEventListener('click', () => {
            this.addCondition();
        });

        // JQL input with autocomplete
        document.getElementById('jqlInput')?.addEventListener('input', (e) => {
            this.handleJQLInput(e.target.value);
        });

        document.getElementById('jqlInput')?.addEventListener('keydown', (e) => {
            if (e.key === 'Tab' && this.suggestions.length > 0) {
                e.preventDefault();
                this.applySuggestion(this.suggestions[0]);
            }
        });

        // Filter actions
        document.getElementById('clearFilterBtn')?.addEventListener('click', () => {
            this.clearFilter();
        });

        document.getElementById('saveFilterBtn')?.addEventListener('click', () => {
            this.openSaveDialog();
        });

        document.getElementById('applyFilterBtn')?.addEventListener('click', () => {
            this.applyFilter();
        });

        // Save dialog
        document.getElementById('closeSaveDialog')?.addEventListener('click', () => {
            document.getElementById('saveFilterDialog').style.display = 'none';
        });

        document.getElementById('confirmSaveFilter')?.addEventListener('click', () => {
            this.saveFilter();
        });
    }

    async loadSavedFilters() {
        try {
            const projectId = this.getCurrentProjectId();
            const response = await fetch(`/api/projects/${projectId}/filters`);
            if (response.ok) {
                this.savedFilters = await response.json();
                this.renderSavedFilters();
            }
        } catch (error) {
            console.error('Failed to load filters:', error);
        }
    }

    renderSavedFilters() {
        const container = document.getElementById('savedFiltersList');
        if (!container) return;

        if (this.savedFilters.length === 0) {
            container.innerHTML = '<p class="empty-text">No saved filters</p>';
            return;
        }

        container.innerHTML = this.savedFilters.map(filter => `
            <div class="saved-filter-item ${this.currentFilter?.id === filter.id ? 'active' : ''}">
                <div class="filter-item-content" onclick="window.advancedFilters.loadFilter(${filter.id})">
                    <div class="filter-item-header">
                        <span class="filter-name">${filter.name}</span>
                        ${filter.is_favorite ? '<i data-lucide="star" class="favorite-icon"></i>' : ''}
                    </div>
                    ${filter.description ? `<p class="filter-description">${filter.description}</p>` : ''}
                    <div class="filter-meta">
                        <span class="filter-query">${filter.query}</span>
                    </div>
                </div>
                <div class="filter-item-actions">
                    <button class="btn-icon-sm" onclick="event.stopPropagation(); window.advancedFilters.toggleFavorite(${filter.id})">
                        <i data-lucide="${filter.is_favorite ? 'star' : 'star'}"></i>
                    </button>
                    <button class="btn-icon-sm" onclick="event.stopPropagation(); window.advancedFilters.editFilter(${filter.id})">
                        <i data-lucide="edit-2"></i>
                    </button>
                    <button class="btn-icon-sm" onclick="event.stopPropagation(); window.advancedFilters.deleteFilter(${filter.id})">
                        <i data-lucide="trash-2"></i>
                    </button>
                </div>
            </div>
        `).join('');

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    openModal() {
        document.getElementById('advancedFilterModal').style.display = 'block';
        this.updatePreview();
    }

    closeModal() {
        document.getElementById('advancedFilterModal').style.display = 'none';
    }

    switchMode(mode) {
        // Update button states
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.mode === mode);
        });

        // Update builder visibility
        document.getElementById('visualBuilder').classList.toggle('active', mode === 'visual');
        document.getElementById('jqlBuilder').classList.toggle('active', mode === 'jql');

        // Sync between modes
        if (mode === 'jql') {
            this.syncVisualToJQL();
        } else {
            this.syncJQLToVisual();
        }
    }

    addCondition(field = '', operator = '', value = '') {
        const container = document.getElementById('filterConditions');
        const conditionId = `condition-${Date.now()}`;
        
        const conditionHTML = `
            <div class="filter-condition" id="${conditionId}">
                <select class="condition-field" onchange="window.advancedFilters.updateConditionOperators('${conditionId}')">
                    <option value="">Select field...</option>
                    ${Object.keys(this.fields).map(f => 
                        `<option value="${f}" ${field === f ? 'selected' : ''}>${this.formatFieldName(f)}</option>`
                    ).join('')}
                </select>
                
                <select class="condition-operator">
                    <option value="">Operator</option>
                </select>
                
                <input type="text" class="condition-value" placeholder="Value" value="${value}">
                
                <button class="btn-icon-sm" onclick="window.advancedFilters.removeCondition('${conditionId}')">
                    <i data-lucide="x"></i>
                </button>
            </div>
        `;
        
        container.insertAdjacentHTML('beforeend', conditionHTML);
        
        if (field) {
            this.updateConditionOperators(conditionId);
        }
        
        // Add change listeners
        const condition = document.getElementById(conditionId);
        condition.querySelectorAll('select, input').forEach(el => {
            el.addEventListener('change', () => this.updatePreview());
        });
        
        if (window.lucide) {
            lucide.createIcons();
        }
    }

    removeCondition(conditionId) {
        document.getElementById(conditionId)?.remove();
        this.updatePreview();
    }

    updateConditionOperators(conditionId) {
        const condition = document.getElementById(conditionId);
        const fieldSelect = condition.querySelector('.condition-field');
        const operatorSelect = condition.querySelector('.condition-operator');
        
        const field = fieldSelect.value;
        if (!field) return;
        
        const operators = this.fields[field]?.operators || [];
        operatorSelect.innerHTML = operators.map(op => 
            `<option value="${op}">${op}</option>`
        ).join('');
        
        this.updatePreview();
    }

    buildJQLFromVisual() {
        const conditions = Array.from(document.querySelectorAll('.filter-condition'));
        
        const clauses = conditions.map(condition => {
            const field = condition.querySelector('.condition-field').value;
            const operator = condition.querySelector('.condition-operator').value;
            const value = condition.querySelector('.condition-value').value;
            
            if (!field || !operator || !value) return null;
            
            // Format value based on operator
            let formattedValue = value;
            if (operator === 'in' || operator === 'not in') {
                formattedValue = `(${value})`;
            } else if (operator === '~' || operator === '!~') {
                formattedValue = `"${value}"`;
            } else if (this.fields[field]?.type === 'text' && !value.startsWith('"')) {
                formattedValue = `"${value}"`;
            }
            
            return `${field} ${operator} ${formattedValue}`;
        }).filter(Boolean);
        
        return clauses.join(' AND ');
    }

    syncVisualToJQL() {
        const jql = this.buildJQLFromVisual();
        document.getElementById('jqlInput').value = jql;
    }

    syncJQLToVisual() {
        // Parse JQL and create visual conditions (simplified)
        const jql = document.getElementById('jqlInput').value;
        // This would require a full JQL parser - simplified for now
    }

    handleJQLInput(query) {
        const cursorPos = document.getElementById('jqlInput').selectionStart;
        const beforeCursor = query.substring(0, cursorPos);
        
        // Get current token
        const tokens = beforeCursor.split(/\s+/);
        const currentToken = tokens[tokens.length - 1];
        
        // Generate suggestions
        this.suggestions = this.generateSuggestions(currentToken, tokens);
        this.renderSuggestions();
        
        this.updatePreview();
    }

    generateSuggestions(token, tokens) {
        const suggestions = [];
        
        // Field suggestions
        if (tokens.length === 1 || tokens[tokens.length - 2].toUpperCase() === 'AND' || tokens[tokens.length - 2].toUpperCase() === 'OR') {
            Object.keys(this.fields).forEach(field => {
                if (field.toLowerCase().startsWith(token.toLowerCase())) {
                    suggestions.push({ type: 'field', value: field, label: this.formatFieldName(field) });
                }
            });
        }
        
        // Operator suggestions
        if (tokens.length >= 2 && this.fields[tokens[tokens.length - 2]]) {
            const field = tokens[tokens.length - 2];
            this.fields[field].operators.forEach(op => {
                if (op.toLowerCase().startsWith(token.toLowerCase())) {
                    suggestions.push({ type: 'operator', value: op, label: op });
                }
            });
        }
        
        // Logical operator suggestions
        if (tokens.length > 3) {
            ['AND', 'OR'].forEach(op => {
                if (op.toLowerCase().startsWith(token.toLowerCase())) {
                    suggestions.push({ type: 'logical', value: op, label: op });
                }
            });
        }
        
        return suggestions.slice(0, 5);
    }

    renderSuggestions() {
        const container = document.getElementById('jqlSuggestions');
        
        if (this.suggestions.length === 0) {
            container.style.display = 'none';
            return;
        }
        
        container.innerHTML = this.suggestions.map((s, i) => `
            <div class="suggestion-item ${i === 0 ? 'active' : ''}" 
                 onclick="window.advancedFilters.applySuggestion('${s.value}')">
                <span class="suggestion-type">${s.type}</span>
                <span class="suggestion-value">${s.label}</span>
            </div>
        `).join('');
        
        container.style.display = 'block';
    }

    applySuggestion(value) {
        const input = document.getElementById('jqlInput');
        const text = input.value;
        const cursorPos = input.selectionStart;
        const beforeCursor = text.substring(0, cursorPos);
        const afterCursor = text.substring(cursorPos);
        
        const tokens = beforeCursor.split(/\s+/);
        tokens[tokens.length - 1] = value;
        
        const newText = tokens.join(' ') + ' ' + afterCursor;
        input.value = newText;
        input.selectionStart = input.selectionEnd = tokens.join(' ').length + 1;
        
        this.suggestions = [];
        this.renderSuggestions();
        this.updatePreview();
    }

    updatePreview() {
        const mode = document.querySelector('.mode-btn.active').dataset.mode;
        const query = mode === 'jql' ? 
            document.getElementById('jqlInput').value : 
            this.buildJQLFromVisual();
        
        document.getElementById('queryDisplay').textContent = query || 'No conditions added';
        
        // Execute query and show results
        this.executeQuery(query);
    }

    async executeQuery(query) {
        if (!query) {
            document.getElementById('resultsPreview').innerHTML = '<p class="empty-text">Add conditions to see results</p>';
            document.getElementById('resultsCount').textContent = '0 issues';
            return;
        }
        
        try {
            const projectId = this.getCurrentProjectId();
            const response = await fetch(`/api/projects/${projectId}/search?jql=${encodeURIComponent(query)}`);
            if (response.ok) {
                const results = await response.json();
                this.renderResults(results);
            }
        } catch (error) {
            console.error('Failed to execute query:', error);
        }
    }

    renderResults(results) {
        document.getElementById('resultsCount').textContent = `${results.length} issue${results.length !== 1 ? 's' : ''}`;
        
        if (results.length === 0) {
            document.getElementById('resultsPreview').innerHTML = '<p class="empty-text">No issues match this filter</p>';
            return;
        }
        
        document.getElementById('resultsPreview').innerHTML = results.slice(0, 10).map(issue => `
            <div class="result-item" onclick="openIssueDetail(${issue.id})">
                <span class="result-key">${issue.key}</span>
                <span class="result-summary">${issue.title}</span>
                <span class="result-status">${issue.status}</span>
            </div>
        `).join('') + (results.length > 10 ? `<p class="results-more">...and ${results.length - 10} more</p>` : '');
    }

    clearFilter() {
        document.getElementById('filterConditions').innerHTML = '';
        document.getElementById('jqlInput').value = '';
        this.updatePreview();
    }

    openSaveDialog() {
        const mode = document.querySelector('.mode-btn.active').dataset.mode;
        const query = mode === 'jql' ? 
            document.getElementById('jqlInput').value : 
            this.buildJQLFromVisual();
        
        if (!query) {
            window.notificationManager?.addNotification({
                title: 'No Filter',
                message: 'Create a filter before saving',
                type: 'warning'
            });
            return;
        }
        
        document.getElementById('saveFilterDialog').style.display = 'block';
    }

    async saveFilter() {
        const name = document.getElementById('filterName').value;
        const description = document.getElementById('filterDescription').value;
        const isFavorite = document.getElementById('filterFavorite').checked;
        const isShared = document.getElementById('filterShared').checked;
        
        if (!name) {
            window.notificationManager?.addNotification({
                title: 'Validation Error',
                message: 'Filter name is required',
                type: 'error'
            });
            return;
        }
        
        const mode = document.querySelector('.mode-btn.active').dataset.mode;
        const query = mode === 'jql' ? 
            document.getElementById('jqlInput').value : 
            this.buildJQLFromVisual();
        
        try {
            const projectId = this.getCurrentProjectId();
            const response = await fetch(`/api/projects/${projectId}/filters`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name, description, query, is_favorite: isFavorite, is_shared: isShared
                })
            });
            
            if (response.ok) {
                window.notificationManager?.addNotification({
                    title: 'Filter Saved',
                    message: `"${name}" has been saved`,
                    type: 'success'
                });
                
                document.getElementById('saveFilterDialog').style.display = 'none';
                document.getElementById('filterName').value = '';
                document.getElementById('filterDescription').value = '';
                
                await this.loadSavedFilters();
            }
        } catch (error) {
            console.error('Failed to save filter:', error);
        }
    }

    async loadFilter(filterId) {
        const filter = this.savedFilters.find(f => f.id === filterId);
        if (!filter) return;
        
        this.currentFilter = filter;
        document.getElementById('jqlInput').value = filter.query;
        this.switchMode('jql');
        this.updatePreview();
        this.renderSavedFilters();
    }

    async toggleFavorite(filterId) {
        try {
            const response = await fetch(`/api/filters/${filterId}/favorite`, {
                method: 'POST'
            });
            
            if (response.ok) {
                await this.loadSavedFilters();
            }
        } catch (error) {
            console.error('Failed to toggle favorite:', error);
        }
    }

    async deleteFilter(filterId) {
        if (!confirm('Delete this filter?')) return;
        
        try {
            const response = await fetch(`/api/filters/${filterId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                window.notificationManager?.addNotification({
                    title: 'Filter Deleted',
                    message: 'Filter has been removed',
                    type: 'success'
                });
                
                await this.loadSavedFilters();
            }
        } catch (error) {
            console.error('Failed to delete filter:', error);
        }
    }

    applyFilter() {
        const mode = document.querySelector('.mode-btn.active').dataset.mode;
        const query = mode === 'jql' ? 
            document.getElementById('jqlInput').value : 
            this.buildJQLFromVisual();
        
        // Apply filter to current view
        if (window.applySearchFilter) {
            window.applySearchFilter(query);
        }
        
        this.closeModal();
    }

    showJQLHelp() {
        alert('JQL Syntax Help:\n\n' +
              'Basic: field operator value\n' +
              'Examples:\n' +
              '- project = "TEST"\n' +
              '- status = "In Progress"\n' +
              '- assignee = currentUser()\n' +
              '- created >= -7d\n\n' +
              'Logical operators: AND, OR\n' +
              'Functions: currentUser(), now(), startOfDay()');
    }

    formatFieldName(field) {
        return field.charAt(0).toUpperCase() + field.slice(1).replace(/([A-Z])/g, ' $1');
    }

    getCurrentProjectId() {
        const match = window.location.pathname.match(/\/project\/(\d+)/);
        return match ? match[1] : window.currentProjectId;
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.advancedFilters = new AdvancedFilters();
});

// Global function to open filter modal
function openAdvancedFilters() {
    window.advancedFilters?.openModal();
}
