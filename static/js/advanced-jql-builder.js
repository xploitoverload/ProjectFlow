/**
 * Advanced JQL Builder with AI
 * Visual query builder, Syntax highlighting, Autocomplete, AI conversion
 */

class AdvancedJQLBuilder {
    constructor() {
        this.mode = 'basic'; // 'basic' or 'advanced'
        this.queryHistory = [
            { query: 'project = TEST AND status = "In Progress"', timestamp: '2 hours ago' },
            { query: 'assignee = currentUser() AND sprint = 23', timestamp: '1 day ago' },
            { query: 'priority = High ORDER BY created DESC', timestamp: '3 days ago' }
        ];
        
        this.queryTemplates = [
            { name: 'My Open Issues', query: 'assignee = currentUser() AND resolution = Unresolved ORDER BY priority DESC', category: 'Personal' },
            { name: 'Recently Updated', query: 'updated >= -7d ORDER BY updated DESC', category: 'Time-based' },
            { name: 'Overdue Issues', query: 'duedate < now() AND resolution = Unresolved', category: 'Time-based' },
            { name: 'Sprint Issues', query: 'sprint in openSprints()', category: 'Agile' },
            { name: 'Unassigned Bugs', query: 'type = Bug AND assignee is EMPTY', category: 'Quality' }
        ];
        
        this.fields = [
            { name: 'project', values: ['TEST', 'PROJ', 'DEMO'] },
            { name: 'status', values: ['To Do', 'In Progress', 'In Review', 'Done'] },
            { name: 'priority', values: ['Critical', 'High', 'Medium', 'Low'] },
            { name: 'assignee', values: ['currentUser()', 'John Doe', 'Jane Smith'] },
            { name: 'type', values: ['Story', 'Bug', 'Task', 'Epic'] },
            { name: 'created', values: ['-1d', '-7d', '-30d'] },
            { name: 'updated', values: ['-1d', '-7d', '-30d'] }
        ];
        
        this.operators = ['=', '!=', '>', '<', '>=', '<=', 'IN', 'NOT IN', 'IS', 'IS NOT', '~', '!~'];
        this.logicalOps = ['AND', 'OR', 'AND NOT', 'OR NOT'];
        
        this.basicQuery = {
            project: 'TEST',
            status: '',
            assignee: '',
            priority: '',
            type: ''
        };
        
        this.currentQuery = '';
        this.validationErrors = [];
        
        this.init();
    }
    
    init() {
        console.log('Advanced JQL Builder initialized');
    }
    
    render(container) {
        container.innerHTML = `
            <div class="jql-builder-container">
                ${this.renderToolbar()}
                <div class="jql-builder-content">
                    ${this.renderQueryArea()}
                    ${this.renderSidebar()}
                </div>
                ${this.renderResults()}
            </div>
        `;
        
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
        
        this.attachEventListeners();
    }
    
    renderToolbar() {
        return `
            <div class="jql-toolbar">
                <div class="toolbar-left">
                    <div class="mode-switcher">
                        <button class="mode-btn ${this.mode === 'basic' ? 'active' : ''}" 
                            onclick="jqlBuilder.setMode('basic')">
                            <i data-lucide="sliders"></i>
                            Basic
                        </button>
                        <button class="mode-btn ${this.mode === 'advanced' ? 'active' : ''}" 
                            onclick="jqlBuilder.setMode('advanced')">
                            <i data-lucide="code"></i>
                            Advanced (JQL)
                        </button>
                    </div>
                </div>
                
                <div class="toolbar-right">
                    <button class="btn btn-secondary" onclick="jqlBuilder.showHistory()">
                        <i data-lucide="history"></i>
                        History
                    </button>
                    <button class="btn btn-secondary" onclick="jqlBuilder.showTemplates()">
                        <i data-lucide="bookmark"></i>
                        Templates
                    </button>
                    <button class="btn btn-secondary" onclick="jqlBuilder.shareQuery()">
                        <i data-lucide="share-2"></i>
                        Share
                    </button>
                    <button class="btn btn-primary" onclick="jqlBuilder.runQuery()">
                        <i data-lucide="play"></i>
                        Run Query
                    </button>
                </div>
            </div>
        `;
    }
    
    renderQueryArea() {
        return `
            <div class="query-area">
                ${this.mode === 'basic' ? this.renderBasicBuilder() : this.renderAdvancedEditor()}
                ${this.renderValidation()}
            </div>
        `;
    }
    
    renderBasicBuilder() {
        return `
            <div class="basic-builder">
                <div class="builder-header">
                    <h3>Build Your Query</h3>
                    <button class="btn-link" onclick="jqlBuilder.convertToNaturalLanguage()">
                        <i data-lucide="sparkles"></i>
                        Convert to Plain English
                    </button>
                </div>
                
                <div class="builder-rows">
                    ${this.renderBasicRow('project', 'Project', '=')}
                    ${this.renderBasicRow('type', 'Issue Type', '=')}
                    ${this.renderBasicRow('status', 'Status', '=')}
                    ${this.renderBasicRow('priority', 'Priority', '=')}
                    ${this.renderBasicRow('assignee', 'Assignee', '=')}
                    
                    <button class="btn btn-secondary-sm add-criteria-btn" onclick="jqlBuilder.addCriteria()">
                        <i data-lucide="plus"></i>
                        Add Criteria
                    </button>
                </div>
                
                <div class="builder-preview">
                    <label>JQL Preview:</label>
                    <div class="jql-preview-text">${this.generateJQLFromBasic()}</div>
                </div>
            </div>
        `;
    }
    
    renderBasicRow(field, label, operator) {
        const fieldData = this.fields.find(f => f.name === field);
        
        return `
            <div class="builder-row">
                <div class="row-logic">
                    <select class="logic-select">
                        <option value="AND">AND</option>
                        <option value="OR">OR</option>
                    </select>
                </div>
                
                <div class="row-field">
                    <label>${label}</label>
                    <select class="field-select" onchange="jqlBuilder.updateBasicQuery('${field}', this.value)">
                        <option value="">Any</option>
                        ${fieldData?.values.map(val => `
                            <option value="${val}" ${this.basicQuery[field] === val ? 'selected' : ''}>${val}</option>
                        `).join('')}
                    </select>
                </div>
                
                <button class="btn-icon-sm remove-row-btn" onclick="jqlBuilder.removeRow(this)">
                    <i data-lucide="x"></i>
                </button>
            </div>
        `;
    }
    
    renderAdvancedEditor() {
        return `
            <div class="advanced-editor">
                <div class="editor-header">
                    <h3>JQL Editor</h3>
                    <div class="editor-actions">
                        <button class="btn-link" onclick="jqlBuilder.convertFromNaturalLanguage()">
                            <i data-lucide="sparkles"></i>
                            AI: Convert from Plain English
                        </button>
                        <button class="btn-link" onclick="jqlBuilder.formatQuery()">
                            <i data-lucide="align-left"></i>
                            Format
                        </button>
                    </div>
                </div>
                
                <div class="editor-wrapper">
                    <textarea id="jqlEditor" class="jql-editor" 
                        placeholder="Enter your JQL query here... (e.g., project = TEST AND status = 'In Progress')"
                        oninput="jqlBuilder.onQueryInput(this.value)">${this.currentQuery}</textarea>
                    <div class="autocomplete-popup" id="jqlAutocomplete" style="display: none;"></div>
                </div>
                
                <div class="editor-help">
                    <button class="btn-link" onclick="jqlBuilder.showSyntaxHelp()">
                        <i data-lucide="help-circle"></i>
                        JQL Syntax Help
                    </button>
                </div>
            </div>
        `;
    }
    
    renderValidation() {
        if (this.validationErrors.length === 0) {
            return '<div class="validation-success"><i data-lucide="check-circle"></i> Query is valid</div>';
        }
        
        return `
            <div class="validation-errors">
                <div class="error-header">
                    <i data-lucide="alert-circle"></i>
                    <span>${this.validationErrors.length} error(s) found</span>
                </div>
                ${this.validationErrors.map(error => `
                    <div class="error-item">
                        <div class="error-message">${error.message}</div>
                        <div class="error-suggestion">${error.suggestion}</div>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    renderSidebar() {
        return `
            <aside class="jql-sidebar">
                <div class="sidebar-section">
                    <h4>Quick Filters</h4>
                    <div class="quick-filter-buttons">
                        <button class="quick-filter-btn" onclick="jqlBuilder.applyQuickFilter('myIssues')">
                            My Issues
                        </button>
                        <button class="quick-filter-btn" onclick="jqlBuilder.applyQuickFilter('recentlyUpdated')">
                            Recently Updated
                        </button>
                        <button class="quick-filter-btn" onclick="jqlBuilder.applyQuickFilter('openSprint')">
                            Open Sprints
                        </button>
                        <button class="quick-filter-btn" onclick="jqlBuilder.applyQuickFilter('overdue')">
                            Overdue
                        </button>
                    </div>
                </div>
                
                <div class="sidebar-section">
                    <h4>Recent Queries</h4>
                    <div class="recent-queries">
                        ${this.queryHistory.slice(0, 5).map(item => `
                            <div class="recent-query-item" onclick="jqlBuilder.loadQuery('${item.query}')">
                                <div class="query-text">${item.query}</div>
                                <div class="query-time">${item.timestamp}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                <div class="sidebar-section">
                    <h4>Field Reference</h4>
                    <div class="field-reference">
                        ${this.fields.slice(0, 7).map(field => `
                            <div class="field-ref-item" onclick="jqlBuilder.insertField('${field.name}')">
                                <code>${field.name}</code>
                                <button class="btn-icon-sm">
                                    <i data-lucide="plus"></i>
                                </button>
                            </div>
                        `).join('')}
                    </div>
                    <button class="btn-link" onclick="jqlBuilder.showAllFields()">
                        View all fields
                    </button>
                </div>
            </aside>
        `;
    }
    
    renderResults() {
        return `
            <div class="query-results">
                <div class="results-header">
                    <span class="results-count">0 issues found</span>
                    <button class="btn btn-secondary-sm" onclick="jqlBuilder.exportResults()">
                        <i data-lucide="download"></i>
                        Export
                    </button>
                </div>
                <div class="results-body">
                    <div class="empty-state">
                        <i data-lucide="search"></i>
                        <p>Run a query to see results</p>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Methods
    setMode(mode) {
        this.mode = mode;
        const container = document.querySelector('.jql-builder-container').parentElement;
        this.render(container);
    }
    
    generateJQLFromBasic() {
        const conditions = [];
        
        Object.entries(this.basicQuery).forEach(([field, value]) => {
            if (value) {
                conditions.push(`${field} = "${value}"`);
            }
        });
        
        return conditions.length > 0 ? conditions.join(' AND ') : 'No conditions set';
    }
    
    updateBasicQuery(field, value) {
        this.basicQuery[field] = value;
        const container = document.querySelector('.jql-builder-container').parentElement;
        this.render(container);
    }
    
    onQueryInput(value) {
        this.currentQuery = value;
        this.validateQuery(value);
        this.showAutocomplete(value);
    }
    
    validateQuery(query) {
        this.validationErrors = [];
        
        // Simple validation - would be more sophisticated in real implementation
        if (query && !query.includes('=') && !query.includes('IN') && !query.includes('IS')) {
            this.validationErrors.push({
                message: 'Query must contain at least one operator',
                suggestion: 'Try using =, !=, IN, or IS operators'
            });
        }
        
        // Re-render validation area
        const validationEl = document.querySelector('.query-area');
        if (validationEl) {
            const validationHtml = this.renderValidation();
            const existingValidation = validationEl.querySelector('.validation-success, .validation-errors');
            if (existingValidation) {
                existingValidation.outerHTML = validationHtml;
            }
        }
    }
    
    showAutocomplete(query) {
        const autocomplete = document.getElementById('jqlAutocomplete');
        if (!autocomplete) return;
        
        const cursorPos = document.getElementById('jqlEditor')?.selectionStart || 0;
        const currentWord = this.getCurrentWord(query, cursorPos);
        
        if (currentWord.length < 2) {
            autocomplete.style.display = 'none';
            return;
        }
        
        const suggestions = this.getSuggestions(currentWord);
        
        if (suggestions.length > 0) {
            autocomplete.innerHTML = suggestions.map(sug => `
                <div class="autocomplete-item" onclick="jqlBuilder.insertSuggestion('${sug.value}')">
                    <span class="suggestion-text">${sug.label}</span>
                    <span class="suggestion-type">${sug.type}</span>
                </div>
            `).join('');
            autocomplete.style.display = 'block';
        } else {
            autocomplete.style.display = 'none';
        }
    }
    
    getCurrentWord(text, pos) {
        const before = text.substring(0, pos);
        const match = before.match(/[a-zA-Z0-9_]+$/);
        return match ? match[0] : '';
    }
    
    getSuggestions(word) {
        const suggestions = [];
        
        // Field suggestions
        this.fields.forEach(field => {
            if (field.name.toLowerCase().startsWith(word.toLowerCase())) {
                suggestions.push({ value: field.name, label: field.name, type: 'field' });
            }
        });
        
        // Operator suggestions
        this.operators.forEach(op => {
            if (op.toLowerCase().startsWith(word.toLowerCase())) {
                suggestions.push({ value: op, label: op, type: 'operator' });
            }
        });
        
        return suggestions.slice(0, 10);
    }
    
    convertFromNaturalLanguage() {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal ai-convert-modal">
                <div class="modal-header">
                    <h3><i data-lucide="sparkles"></i> AI Query Converter</h3>
                    <button class="btn-icon" onclick="this.closest('.modal-overlay').remove()">
                        <i data-lucide="x"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <label>Describe what you're looking for in plain English:</label>
                    <textarea id="naturalLanguageInput" rows="3" placeholder="e.g., Show me all high priority bugs assigned to me that were created in the last week"></textarea>
                    
                    <div class="ai-result" id="aiResult" style="display: none;">
                        <label>Generated JQL:</label>
                        <div class="jql-result"></div>
                        <div class="ai-confidence">Confidence: <span class="confidence-score">95%</span></div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                    <button class="btn btn-primary" onclick="jqlBuilder.generateFromNL()">
                        <i data-lucide="sparkles"></i>
                        Convert
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        if (typeof lucide !== 'undefined') lucide.createIcons();
    }
    
    generateFromNL() {
        const input = document.getElementById('naturalLanguageInput').value;
        
        // Simulated AI conversion - would call actual API
        const jql = this.parseNaturalLanguage(input);
        
        const result = document.getElementById('aiResult');
        result.style.display = 'block';
        result.querySelector('.jql-result').textContent = jql;
        
        this.currentQuery = jql;
        
        setTimeout(() => {
            document.querySelector('.ai-convert-modal').closest('.modal-overlay').remove();
            const container = document.querySelector('.jql-builder-container').parentElement;
            this.render(container);
        }, 1500);
    }
    
    parseNaturalLanguage(text) {
        // Simple pattern matching - would use AI in production
        let jql = '';
        
        if (text.includes('assigned to me')) {
            jql += 'assignee = currentUser()';
        }
        
        if (text.includes('high priority')) {
            jql += (jql ? ' AND ' : '') + 'priority = High';
        }
        
        if (text.includes('bugs')) {
            jql += (jql ? ' AND ' : '') + 'type = Bug';
        }
        
        if (text.includes('last week')) {
            jql += (jql ? ' AND ' : '') + 'created >= -7d';
        }
        
        return jql || 'Unable to parse query';
    }
    
    showHistory() {
        this.showToast('Query history');
    }
    
    showTemplates() {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal templates-modal">
                <div class="modal-header">
                    <h3>Query Templates</h3>
                    <button class="btn-icon" onclick="this.closest('.modal-overlay').remove()">
                        <i data-lucide="x"></i>
                    </button>
                </div>
                <div class="modal-body">
                    ${this.renderTemplatesByCategory()}
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        if (typeof lucide !== 'undefined') lucide.createIcons();
    }
    
    renderTemplatesByCategory() {
        const categories = {};
        this.queryTemplates.forEach(template => {
            if (!categories[template.category]) categories[template.category] = [];
            categories[template.category].push(template);
        });
        
        return Object.entries(categories).map(([category, templates]) => `
            <div class="template-category">
                <h4>${category}</h4>
                <div class="template-list">
                    ${templates.map(t => `
                        <div class="template-item" onclick="jqlBuilder.loadTemplate('${t.query}'); this.closest('.modal-overlay').remove()">
                            <div class="template-name">${t.name}</div>
                            <code class="template-query">${t.query}</code>
                        </div>
                    `).join('')}
                </div>
            </div>
        `).join('');
    }
    
    loadTemplate(query) {
        this.currentQuery = query;
        this.mode = 'advanced';
        const container = document.querySelector('.jql-builder-container').parentElement;
        this.render(container);
        this.showToast('Template loaded');
    }
    
    runQuery() {
        this.showToast('Running query...');
    }
    
    shareQuery() {
        this.showToast('Share query link copied to clipboard');
    }
    
    attachEventListeners() {
        // Event listeners for autocomplete, etc.
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
const jqlBuilder = new AdvancedJQLBuilder();
