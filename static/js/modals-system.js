/**
 * Complete Modals & Dialogs System
 * Create Issue, Edit Field, Custom Field, Share, Export, Settings
 */

class ModalsSystem {
    constructor() {
        this.activeModals = [];
        this.issueTypes = ['Story', 'Task', 'Bug', 'Epic'];
        this.fieldTypes = [
            'Text Field (single line)', 'Text Field (multi-line)', 'Number Field',
            'Select List (single choice)', 'Select List (multiple choice)', 'Radio Buttons',
            'Checkboxes', 'Date Picker', 'Date Time Picker', 'User Picker', 'Labels',
            'URL Field', 'Text Field (read only)', 'Cascading Select', 'Version Picker'
        ];
        
        this.init();
    }

    init() {
        this.setupGlobalListeners();
        console.log('ModalsSystem initialized');        // Expose to window for onclick handlers
        window.modalsSystem = this;    }

    setupGlobalListeners() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.activeModals.length > 0) {
                this.closeTopModal();
            }
        });
    }

    // CREATE ISSUE MODAL
    openCreateIssueModal(projectKey = 'PROJ') {
        const modal = this.createModal('create-issue-modal', 'large');
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-header">
                    <h2>Create Issue</h2>
                    <div class="header-actions">
                        <button class="btn-icon" onclick="modalsSystem.switchIssueTemplate()">
                            <i data-lucide="layout-template"></i>
                        </button>
                        <button class="btn-icon" onclick="modalsSystem.closeModal('create-issue-modal')">
                            <i data-lucide="x"></i>
                        </button>
                    </div>
                </div>

                <div class="modal-body create-issue-body">
                    <div class="form-section">
                        <div class="form-row">
                            <div class="form-group required">
                                <label>Project</label>
                                <select class="form-select" id="createProjectSelect">
                                    <option value="${projectKey}">${projectKey}</option>
                                    <option value="TEST">TEST</option>
                                    <option value="SUP">SUP</option>
                                </select>
                            </div>
                            <div class="form-group required">
                                <label>Issue Type</label>
                                <select class="form-select" id="createIssueType" 
                                        onchange="modalsSystem.onIssueTypeChange(this.value)">
                                    ${this.issueTypes.map(type => `
                                        <option value="${type}">${type}</option>
                                    `).join('')}
                                </select>
                            </div>
                        </div>

                        <div class="form-group required">
                            <label>Summary</label>
                            <input type="text" class="form-input" id="createSummary" 
                                   placeholder="Enter issue summary" autofocus>
                        </div>

                        <div class="form-group">
                            <label>Description</label>
                            <div class="wysiwyg-toolbar">
                                <button class="toolbar-btn" data-action="bold">
                                    <i data-lucide="bold"></i>
                                </button>
                                <button class="toolbar-btn" data-action="italic">
                                    <i data-lucide="italic"></i>
                                </button>
                                <button class="toolbar-btn" data-action="list">
                                    <i data-lucide="list"></i>
                                </button>
                                <button class="toolbar-btn" data-action="code">
                                    <i data-lucide="code"></i>
                                </button>
                                <button class="toolbar-btn" data-action="link">
                                    <i data-lucide="link"></i>
                                </button>
                            </div>
                            <textarea class="form-textarea description-textarea" id="createDescription"
                                      placeholder="Add a description..."></textarea>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label>Assignee</label>
                                <select class="form-select" id="createAssignee">
                                    <option value="">Unassigned</option>
                                    <option value="current">Assign to me</option>
                                    <option value="1">John Doe</option>
                                    <option value="2">Jane Smith</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Priority</label>
                                <select class="form-select" id="createPriority">
                                    <option value="Medium">Medium</option>
                                    <option value="High">High</option>
                                    <option value="Low">Low</option>
                                </select>
                            </div>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label>Story Points</label>
                                <input type="number" class="form-input" id="createStoryPoints" 
                                       min="0" max="100" step="0.5" placeholder="0">
                            </div>
                            <div class="form-group">
                                <label>Sprint</label>
                                <select class="form-select" id="createSprint">
                                    <option value="">None</option>
                                    <option value="1">Sprint 1</option>
                                    <option value="2">Sprint 2</option>
                                </select>
                            </div>
                        </div>

                        <div class="form-group">
                            <label>Labels</label>
                            <input type="text" class="form-input" id="createLabels" 
                                   placeholder="Enter labels (comma separated)">
                        </div>

                        <div class="epic-fields" style="display: none;">
                            <div class="form-group">
                                <label>Epic Name</label>
                                <input type="text" class="form-input" id="createEpicName" 
                                       placeholder="Enter epic name">
                            </div>
                            <div class="form-group">
                                <label>Epic Color</label>
                                <input type="color" class="form-input" id="createEpicColor" 
                                       value="#0052cc">
                            </div>
                        </div>
                    </div>
                </div>

                <div class="modal-footer">
                    <div class="footer-left">
                        <span class="keyboard-hint">
                            <i data-lucide="command"></i>
                            <span>Ctrl+Enter to create</span>
                        </span>
                    </div>
                    <div class="footer-right">
                        <button class="btn-secondary" onclick="modalsSystem.closeModal('create-issue-modal')">
                            Cancel
                        </button>
                        <button class="btn-primary" onclick="modalsSystem.createIssue()">
                            <i data-lucide="plus"></i>
                            Create Issue
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        this.activeModals.push('create-issue-modal');
        if (window.lucide) lucide.createIcons();
        
        // Keyboard shortcut
        const descTextarea = modal.querySelector('#createDescription');
        modal.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.createIssue();
            }
        });
    }

    // EDIT FIELD MODAL
    openEditFieldModal(fieldName, fieldValue, fieldType = 'text') {
        const modal = this.createModal('edit-field-modal', 'small');
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-header">
                    <h2>Edit ${fieldName}</h2>
                    <button class="btn-icon" onclick="modalsSystem.closeModal('edit-field-modal')">
                        <i data-lucide="x"></i>
                    </button>
                </div>

                <div class="modal-body">
                    ${this.renderFieldEditor(fieldType, fieldValue)}
                    <div class="field-validation-message" style="display: none;">
                        <i data-lucide="alert-circle"></i>
                        <span></span>
                    </div>
                </div>

                <div class="modal-footer">
                    <button class="btn-secondary" onclick="modalsSystem.closeModal('edit-field-modal')">
                        Cancel
                    </button>
                    <button class="btn-primary" onclick="modalsSystem.saveFieldValue()">
                        Save
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        this.activeModals.push('edit-field-modal');
        if (window.lucide) lucide.createIcons();
    }

    renderFieldEditor(type, value) {
        switch (type) {
            case 'text':
                return `<input type="text" class="form-input" id="fieldValue" value="${value}">`;
            case 'textarea':
                return `<textarea class="form-textarea" id="fieldValue">${value}</textarea>`;
            case 'number':
                return `<input type="number" class="form-input" id="fieldValue" value="${value}">`;
            case 'date':
                return `<input type="date" class="form-input" id="fieldValue" value="${value}">`;
            case 'select':
                return `
                    <select class="form-select" id="fieldValue">
                        <option value="Option 1" ${value === 'Option 1' ? 'selected' : ''}>Option 1</option>
                        <option value="Option 2" ${value === 'Option 2' ? 'selected' : ''}>Option 2</option>
                    </select>
                `;
            default:
                return `<input type="text" class="form-input" id="fieldValue" value="${value}">`;
        }
    }

    // CUSTOM FIELD MODAL
    openCustomFieldModal(fieldId = null) {
        const modal = this.createModal('custom-field-modal', 'medium');
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-header">
                    <h2>${fieldId ? 'Edit' : 'Create'} Custom Field</h2>
                    <button class="btn-icon" onclick="modalsSystem.closeModal('custom-field-modal')">
                        <i data-lucide="x"></i>
                    </button>
                </div>

                <div class="modal-body custom-field-body">
                    <div class="form-group required">
                        <label>Field Name</label>
                        <input type="text" class="form-input" id="customFieldName" 
                               placeholder="Enter field name">
                    </div>

                    <div class="form-group required">
                        <label>Field Type</label>
                        <select class="form-select" id="customFieldType" 
                                onchange="modalsSystem.onFieldTypeChange(this.value)">
                            ${this.fieldTypes.map(type => `
                                <option value="${type}">${type}</option>
                            `).join('')}
                        </select>
                    </div>

                    <div class="form-group">
                        <label>Description</label>
                        <textarea class="form-textarea" id="customFieldDescription" 
                                  placeholder="Describe what this field is for"></textarea>
                    </div>

                    <div class="field-options-section" style="display: none;">
                        <div class="form-group">
                            <label>Options (one per line)</label>
                            <textarea class="form-textarea" id="customFieldOptions" 
                                      placeholder="Option 1&#10;Option 2&#10;Option 3"></textarea>
                        </div>
                    </div>

                    <div class="field-validation-section">
                        <div class="form-group">
                            <label class="checkbox-label">
                                <input type="checkbox" id="customFieldRequired">
                                <span>Make this field required</span>
                            </label>
                        </div>
                        
                        <div class="number-validation" style="display: none;">
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Min Value</label>
                                    <input type="number" class="form-input" id="customFieldMin">
                                </div>
                                <div class="form-group">
                                    <label>Max Value</label>
                                    <input type="number" class="form-input" id="customFieldMax">
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Default Value</label>
                        <input type="text" class="form-input" id="customFieldDefault" 
                               placeholder="Enter default value">
                    </div>
                </div>

                <div class="modal-footer">
                    <button class="btn-secondary" onclick="modalsSystem.closeModal('custom-field-modal')">
                        Cancel
                    </button>
                    <button class="btn-primary" onclick="modalsSystem.saveCustomField()">
                        ${fieldId ? 'Update' : 'Create'} Field
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        this.activeModals.push('custom-field-modal');
        if (window.lucide) lucide.createIcons();
    }

    // SHARE DIALOG
    openShareDialog(itemType, itemId) {
        const modal = this.createModal('share-dialog', 'medium');
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-header">
                    <h2>Share ${itemType}</h2>
                    <button class="btn-icon" onclick="modalsSystem.closeModal('share-dialog')">
                        <i data-lucide="x"></i>
                    </button>
                </div>

                <div class="modal-body share-dialog-body">
                    <div class="share-link-section">
                        <label>Share Link</label>
                        <div class="link-input-group">
                            <input type="text" readonly class="form-input" 
                                   value="https://jira.example.com/${itemType}/${itemId}">
                            <button class="btn-secondary" onclick="modalsSystem.copyShareLink()">
                                <i data-lucide="copy"></i>
                                Copy
                            </button>
                        </div>
                    </div>

                    <div class="share-users-section">
                        <label>Share with People</label>
                        <div class="user-search-input">
                            <i data-lucide="search"></i>
                            <input type="text" placeholder="Search users or groups..." 
                                   oninput="modalsSystem.searchUsersForShare(this.value)">
                        </div>

                        <div class="shared-users-list">
                            <div class="shared-user-item">
                                <div class="avatar-sm">JD</div>
                                <div class="user-details">
                                    <span class="user-name">John Doe</span>
                                    <span class="user-email">john@example.com</span>
                                </div>
                                <select class="permission-dropdown">
                                    <option value="view">Can view</option>
                                    <option value="edit">Can edit</option>
                                </select>
                                <button class="btn-icon btn-sm" onclick="this.parentElement.remove()">
                                    <i data-lucide="x"></i>
                                </button>
                            </div>
                        </div>
                    </div>

                    <div class="public-access-section">
                        <div class="access-option">
                            <i data-lucide="globe"></i>
                            <div class="access-info">
                                <strong>Anyone with the link</strong>
                                <p>Anyone who has the link can view</p>
                            </div>
                            <label class="toggle-switch">
                                <input type="checkbox" id="publicAccessToggle">
                                <span class="toggle-slider"></span>
                            </label>
                        </div>
                    </div>
                </div>

                <div class="modal-footer">
                    <button class="btn-primary" onclick="modalsSystem.closeModal('share-dialog')">
                        Done
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        this.activeModals.push('share-dialog');
        if (window.lucide) lucide.createIcons();
    }

    // EXPORT DIALOG
    openExportDialog() {
        const modal = this.createModal('export-dialog', 'medium');
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-header">
                    <h2>Export Issues</h2>
                    <button class="btn-icon" onclick="modalsSystem.closeModal('export-dialog')">
                        <i data-lucide="x"></i>
                    </button>
                </div>

                <div class="modal-body export-dialog-body">
                    <div class="form-group">
                        <label>Export Format</label>
                        <div class="format-options">
                            <label class="format-option">
                                <input type="radio" name="exportFormat" value="csv" checked>
                                <div class="format-card">
                                    <i data-lucide="file-text"></i>
                                    <span>CSV</span>
                                </div>
                            </label>
                            <label class="format-option">
                                <input type="radio" name="exportFormat" value="pdf">
                                <div class="format-card">
                                    <i data-lucide="file"></i>
                                    <span>PDF</span>
                                </div>
                            </label>
                            <label class="format-option">
                                <input type="radio" name="exportFormat" value="excel">
                                <div class="format-card">
                                    <i data-lucide="file-spreadsheet"></i>
                                    <span>Excel</span>
                                </div>
                            </label>
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Fields to Export</label>
                        <div class="fields-checklist">
                            <label class="checkbox-label">
                                <input type="checkbox" checked>
                                <span>Issue Key</span>
                            </label>
                            <label class="checkbox-label">
                                <input type="checkbox" checked>
                                <span>Summary</span>
                            </label>
                            <label class="checkbox-label">
                                <input type="checkbox" checked>
                                <span>Status</span>
                            </label>
                            <label class="checkbox-label">
                                <input type="checkbox">
                                <span>Assignee</span>
                            </label>
                            <label class="checkbox-label">
                                <input type="checkbox">
                                <span>Priority</span>
                            </label>
                            <label class="checkbox-label">
                                <input type="checkbox">
                                <span>Created Date</span>
                            </label>
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Date Range</label>
                        <div class="form-row">
                            <input type="date" class="form-input" id="exportDateFrom">
                            <input type="date" class="form-input" id="exportDateTo">
                        </div>
                    </div>
                </div>

                <div class="modal-footer">
                    <button class="btn-secondary" onclick="modalsSystem.closeModal('export-dialog')">
                        Cancel
                    </button>
                    <button class="btn-primary" onclick="modalsSystem.exportData()">
                        <i data-lucide="download"></i>
                        Export
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        this.activeModals.push('export-dialog');
        if (window.lucide) lucide.createIcons();
    }

    // Helper Methods
    createModal(id, size = 'medium') {
        const overlay = document.createElement('div');
        overlay.className = `modal-overlay active modal-${size}`;
        overlay.id = id;
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                this.closeModal(id);
            }
        });
        return overlay;
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('active');
            setTimeout(() => modal.remove(), 300);
            this.activeModals = this.activeModals.filter(id => id !== modalId);
        }
    }

    closeTopModal() {
        if (this.activeModals.length > 0) {
            const topModalId = this.activeModals[this.activeModals.length - 1];
            this.closeModal(topModalId);
        }
    }

    // Event Handlers
    onIssueTypeChange(type) {
        const epicFields = document.querySelector('.epic-fields');
        if (epicFields) {
            epicFields.style.display = type === 'Epic' ? 'block' : 'none';
        }
    }

    onFieldTypeChange(type) {
        const optionsSection = document.querySelector('.field-options-section');
        const numberValidation = document.querySelector('.number-validation');
        
        const showOptions = type.includes('Select') || type.includes('Radio') || type.includes('Checkboxes');
        const showNumberValidation = type.includes('Number');
        
        if (optionsSection) optionsSection.style.display = showOptions ? 'block' : 'none';
        if (numberValidation) numberValidation.style.display = showNumberValidation ? 'block' : 'none';
    }

    createIssue() {
        const summary = document.getElementById('createSummary')?.value;
        if (!summary) {
            alert('Please enter a summary');
            return;
        }
        alert(`Issue created: ${summary}`);
        this.closeModal('create-issue-modal');
    }

    saveFieldValue() {
        const value = document.getElementById('fieldValue')?.value;
        alert(`Field updated: ${value}`);
        this.closeModal('edit-field-modal');
    }

    saveCustomField() {
        const name = document.getElementById('customFieldName')?.value;
        if (!name) {
            alert('Please enter a field name');
            return;
        }
        alert(`Custom field saved: ${name}`);
        this.closeModal('custom-field-modal');
    }

    copyShareLink() {
        alert('Link copied to clipboard!');
    }

    searchUsersForShare(query) {
        console.log('Search users:', query);
    }

    exportData() {
        alert('Exporting data...');
        this.closeModal('export-dialog');
    }

    switchIssueTemplate() {
        alert('Template selector would open here');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.modalsSystem = new ModalsSystem();
});
