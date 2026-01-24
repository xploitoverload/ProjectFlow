/**
 * Custom Fields Manager - JIRA-style custom field system
 * Features: Field types library, configuration UI, schemes, context assignment
 */

class CustomFieldsManager {
    constructor() {
        this.fieldTypes = this.getFieldTypes();
        this.customFields = [];
        this.schemes = [];
        this.selectedField = null;
        
        this.init();
    }

    init() {
        this.createModal();
        this.setupEventListeners();
        this.loadCustomFields();
    }

    getFieldTypes() {
        return [
            {
                id: 'text',
                name: 'Text Field (single line)',
                icon: 'type',
                description: 'A single line text field',
                config: ['defaultValue', 'maxLength', 'placeholder']
            },
            {
                id: 'textarea',
                name: 'Text Area (multi-line)',
                icon: 'align-left',
                description: 'A multi-line text area',
                config: ['defaultValue', 'rows', 'maxLength', 'placeholder']
            },
            {
                id: 'number',
                name: 'Number Field',
                icon: 'hash',
                description: 'A numeric input field',
                config: ['defaultValue', 'min', 'max', 'step']
            },
            {
                id: 'select',
                name: 'Select List (single choice)',
                icon: 'list',
                description: 'A dropdown with single selection',
                config: ['options', 'defaultValue', 'allowEmpty']
            },
            {
                id: 'multiselect',
                name: 'Select List (multiple choice)',
                icon: 'list-checks',
                description: 'A dropdown with multiple selections',
                config: ['options', 'defaultValues', 'maxSelections']
            },
            {
                id: 'checkbox',
                name: 'Checkbox',
                icon: 'check-square',
                description: 'A single checkbox',
                config: ['defaultChecked', 'label']
            },
            {
                id: 'checkboxes',
                name: 'Checkboxes (multiple)',
                icon: 'square-check',
                description: 'Multiple checkboxes',
                config: ['options', 'defaultValues']
            },
            {
                id: 'radio',
                name: 'Radio Buttons',
                icon: 'circle-dot',
                description: 'Radio button group',
                config: ['options', 'defaultValue']
            },
            {
                id: 'date',
                name: 'Date Picker',
                icon: 'calendar',
                description: 'A date selector',
                config: ['defaultValue', 'minDate', 'maxDate', 'format']
            },
            {
                id: 'datetime',
                name: 'Date Time Picker',
                icon: 'calendar-clock',
                description: 'A date and time selector',
                config: ['defaultValue', 'minDate', 'maxDate', 'format']
            },
            {
                id: 'user',
                name: 'User Picker',
                icon: 'user',
                description: 'Select a user from the system',
                config: ['allowMultiple', 'defaultValue']
            },
            {
                id: 'url',
                name: 'URL Field',
                icon: 'link',
                description: 'A URL input with validation',
                config: ['defaultValue', 'placeholder']
            },
            {
                id: 'email',
                name: 'Email Field',
                icon: 'mail',
                description: 'An email input with validation',
                config: ['defaultValue', 'placeholder']
            },
            {
                id: 'labels',
                name: 'Labels',
                icon: 'tags',
                description: 'Multiple label tags',
                config: ['suggestions', 'maxLabels']
            },
            {
                id: 'cascading',
                name: 'Cascading Select',
                icon: 'git-branch',
                description: 'Hierarchical dropdown selection',
                config: ['options', 'defaultValue']
            }
        ];
    }

    createModal() {
        const modalHTML = `
            <div id="customFieldsModal" class="fields-modal" style="display: none;">
                <div class="fields-modal-backdrop"></div>
                <div class="fields-modal-container">
                    <div class="fields-modal-header">
                        <h2>Custom Fields</h2>
                        <div class="header-actions">
                            <button class="btn btn-primary btn-sm" id="createFieldBtn">
                                <i data-lucide="plus"></i>
                                Create Field
                            </button>
                            <button class="btn btn-ghost btn-sm" id="manageSchemesBtn">
                                <i data-lucide="layers"></i>
                                Manage Schemes
                            </button>
                            <button class="btn-icon" id="closeFieldsModal">
                                <i data-lucide="x"></i>
                            </button>
                        </div>
                    </div>

                    <div class="fields-modal-body">
                        <div class="fields-sidebar">
                            <div class="fields-search">
                                <i data-lucide="search"></i>
                                <input type="text" placeholder="Search fields..." id="fieldsSearchInput">
                            </div>

                            <div class="fields-list" id="fieldsList">
                                <!-- Populated by JS -->
                            </div>
                        </div>

                        <div class="fields-content">
                            <div id="fieldsContentArea">
                                <div class="empty-state">
                                    <i data-lucide="package"></i>
                                    <h3>Custom Fields</h3>
                                    <p>Create custom fields to capture additional information for your issues</p>
                                    <button class="btn btn-primary" onclick="customFieldsManager.showFieldTypeSelector()">
                                        <i data-lucide="plus"></i>
                                        Create Your First Field
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Field Type Selector Dialog -->
            <div id="fieldTypeSelectorDialog" class="field-dialog" style="display: none;">
                <div class="field-dialog-backdrop"></div>
                <div class="field-dialog-container large">
                    <div class="field-dialog-header">
                        <h3>Select Field Type</h3>
                        <button class="btn-icon-sm" onclick="customFieldsManager.closeFieldTypeSelector()">
                            <i data-lucide="x"></i>
                        </button>
                    </div>
                    <div class="field-dialog-body">
                        <div class="field-types-grid" id="fieldTypesGrid">
                            <!-- Populated by JS -->
                        </div>
                    </div>
                </div>
            </div>

            <!-- Field Configuration Dialog -->
            <div id="fieldConfigDialog" class="field-dialog" style="display: none;">
                <div class="field-dialog-backdrop"></div>
                <div class="field-dialog-container">
                    <div class="field-dialog-header">
                        <h3 id="configDialogTitle">Configure Field</h3>
                        <button class="btn-icon-sm" onclick="customFieldsManager.closeConfigDialog()">
                            <i data-lucide="x"></i>
                        </button>
                    </div>
                    <div class="field-dialog-body" id="configDialogContent">
                        <!-- Populated by JS -->
                    </div>
                    <div class="field-dialog-footer">
                        <button class="btn btn-ghost" onclick="customFieldsManager.closeConfigDialog()">Cancel</button>
                        <button class="btn btn-primary" id="saveFieldBtn">Save Field</button>
                    </div>
                </div>
            </div>

            <!-- Context Configuration Dialog -->
            <div id="contextDialog" class="field-dialog" style="display: none;">
                <div class="field-dialog-backdrop"></div>
                <div class="field-dialog-container">
                    <div class="field-dialog-header">
                        <h3>Field Context Configuration</h3>
                        <button class="btn-icon-sm" onclick="customFieldsManager.closeContextDialog()">
                            <i data-lucide="x"></i>
                        </button>
                    </div>
                    <div class="field-dialog-body" id="contextDialogContent">
                        <!-- Populated by JS -->
                    </div>
                    <div class="field-dialog-footer">
                        <button class="btn btn-ghost" onclick="customFieldsManager.closeContextDialog()">Cancel</button>
                        <button class="btn btn-primary" id="saveContextBtn">Save Context</button>
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
        document.getElementById('closeFieldsModal')?.addEventListener('click', () => {
            this.closeModal();
        });

        document.getElementById('createFieldBtn')?.addEventListener('click', () => {
            this.showFieldTypeSelector();
        });

        document.getElementById('manageSchemesBtn')?.addEventListener('click', () => {
            this.showSchemesManager();
        });

        document.getElementById('fieldsSearchInput')?.addEventListener('input', (e) => {
            this.filterFields(e.target.value);
        });

        document.getElementById('saveFieldBtn')?.addEventListener('click', () => {
            this.saveField();
        });

        document.getElementById('saveContextBtn')?.addEventListener('click', () => {
            this.saveContext();
        });
    }

    openModal() {
        document.getElementById('customFieldsModal').style.display = 'block';
        this.renderFieldsList();
    }

    closeModal() {
        document.getElementById('customFieldsModal').style.display = 'none';
    }

    async loadCustomFields() {
        try {
            const response = await fetch('/api/custom-fields');
            if (response.ok) {
                this.customFields = await response.json();
                this.renderFieldsList();
            }
        } catch (error) {
            console.error('Failed to load custom fields:', error);
        }
    }

    renderFieldsList() {
        const container = document.getElementById('fieldsList');
        
        if (this.customFields.length === 0) {
            container.innerHTML = '<p class="empty-text">No custom fields yet</p>';
            return;
        }

        container.innerHTML = this.customFields.map(field => {
            const fieldType = this.fieldTypes.find(t => t.id === field.type);
            return `
                <div class="field-item ${this.selectedField?.id === field.id ? 'active' : ''}" 
                     onclick="customFieldsManager.selectField('${field.id}')">
                    <div class="field-icon">
                        <i data-lucide="${fieldType?.icon || 'box'}"></i>
                    </div>
                    <div class="field-info">
                        <div class="field-name">${field.name}</div>
                        <div class="field-type">${fieldType?.name || field.type}</div>
                    </div>
                    <div class="field-actions">
                        <button class="btn-icon-sm" onclick="customFieldsManager.editField('${field.id}'); event.stopPropagation();">
                            <i data-lucide="edit-2"></i>
                        </button>
                    </div>
                </div>
            `;
        }).join('');

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    selectField(fieldId) {
        this.selectedField = this.customFields.find(f => f.id === fieldId);
        this.renderFieldDetails(this.selectedField);
        this.renderFieldsList();
    }

    renderFieldDetails(field) {
        const fieldType = this.fieldTypes.find(t => t.id === field.type);
        const content = document.getElementById('fieldsContentArea');

        content.innerHTML = `
            <div class="field-details">
                <div class="field-header">
                    <div class="field-header-left">
                        <div class="field-icon-large">
                            <i data-lucide="${fieldType?.icon || 'box'}"></i>
                        </div>
                        <div>
                            <h3>${field.name}</h3>
                            <p class="field-type-badge">${fieldType?.name || field.type}</p>
                        </div>
                    </div>
                    <div class="field-header-actions">
                        <button class="btn btn-ghost btn-sm" onclick="customFieldsManager.editField('${field.id}')">
                            <i data-lucide="edit-2"></i>
                            Edit
                        </button>
                        <button class="btn btn-ghost btn-sm" onclick="customFieldsManager.configureContext('${field.id}')">
                            <i data-lucide="settings"></i>
                            Configure Context
                        </button>
                        <button class="btn btn-ghost btn-sm" onclick="customFieldsManager.deleteField('${field.id}')">
                            <i data-lucide="trash-2"></i>
                            Delete
                        </button>
                    </div>
                </div>

                <div class="field-sections">
                    <div class="detail-section">
                        <h4>Description</h4>
                        <p>${field.description || 'No description provided'}</p>
                    </div>

                    <div class="detail-section">
                        <h4>Field Key</h4>
                        <code>${field.key}</code>
                    </div>

                    <div class="detail-section">
                        <h4>Configuration</h4>
                        <div class="config-grid">
                            ${this.renderFieldConfig(field)}
                        </div>
                    </div>

                    <div class="detail-section">
                        <h4>Context</h4>
                        <div class="context-list">
                            ${this.renderFieldContext(field)}
                        </div>
                    </div>

                    <div class="detail-section">
                        <h4>Preview</h4>
                        <div class="field-preview">
                            ${this.renderFieldPreview(field)}
                        </div>
                    </div>
                </div>
            </div>
        `;

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    renderFieldConfig(field) {
        if (!field.config) return '<p class="empty-text">No configuration</p>';

        return Object.entries(field.config).map(([key, value]) => `
            <div class="config-item">
                <span class="config-key">${key}:</span>
                <span class="config-value">${JSON.stringify(value)}</span>
            </div>
        `).join('');
    }

    renderFieldContext(field) {
        if (!field.contexts || field.contexts.length === 0) {
            return '<p class="empty-text">Available in all projects and issue types</p>';
        }

        return field.contexts.map(ctx => `
            <div class="context-item">
                <div class="context-info">
                    <strong>Projects:</strong> ${ctx.projects?.join(', ') || 'All'}
                    <br>
                    <strong>Issue Types:</strong> ${ctx.issueTypes?.join(', ') || 'All'}
                </div>
            </div>
        `).join('');
    }

    renderFieldPreview(field) {
        // Generate HTML preview based on field type
        switch (field.type) {
            case 'text':
                return `<input type="text" class="form-input" placeholder="${field.config?.placeholder || 'Enter text...'}" disabled>`;
            case 'textarea':
                return `<textarea class="form-input" rows="${field.config?.rows || 3}" placeholder="${field.config?.placeholder || 'Enter text...'}" disabled></textarea>`;
            case 'number':
                return `<input type="number" class="form-input" placeholder="Enter number..." disabled>`;
            case 'select':
                return `
                    <select class="form-input" disabled>
                        <option>Select option...</option>
                        ${field.config?.options?.map(opt => `<option>${opt}</option>`).join('') || ''}
                    </select>
                `;
            case 'checkbox':
                return `<label class="checkbox-label"><input type="checkbox" disabled> ${field.config?.label || 'Checkbox'}</label>`;
            case 'date':
                return `<input type="date" class="form-input" disabled>`;
            case 'datetime':
                return `<input type="datetime-local" class="form-input" disabled>`;
            case 'url':
                return `<input type="url" class="form-input" placeholder="https://..." disabled>`;
            case 'email':
                return `<input type="email" class="form-input" placeholder="email@example.com" disabled>`;
            default:
                return `<input type="text" class="form-input" disabled>`;
        }
    }

    showFieldTypeSelector() {
        const grid = document.getElementById('fieldTypesGrid');
        grid.innerHTML = this.fieldTypes.map(type => `
            <div class="field-type-card" onclick="customFieldsManager.selectFieldType('${type.id}')">
                <div class="type-icon">
                    <i data-lucide="${type.icon}"></i>
                </div>
                <h4>${type.name}</h4>
                <p>${type.description}</p>
            </div>
        `).join('');

        document.getElementById('fieldTypeSelectorDialog').style.display = 'block';

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    closeFieldTypeSelector() {
        document.getElementById('fieldTypeSelectorDialog').style.display = 'none';
    }

    selectFieldType(typeId) {
        this.closeFieldTypeSelector();
        this.showConfigDialog(typeId);
    }

    showConfigDialog(typeId, field = null) {
        const fieldType = this.fieldTypes.find(t => t.id === typeId);
        const isEdit = !!field;

        document.getElementById('configDialogTitle').textContent = 
            isEdit ? `Edit ${field.name}` : `Create ${fieldType.name}`;

        const content = document.getElementById('configDialogContent');
        content.innerHTML = `
            <div class="form-group">
                <label>Field Name *</label>
                <input type="text" class="form-input" id="fieldNameInput" 
                       value="${field?.name || ''}" placeholder="Enter field name">
            </div>

            <div class="form-group">
                <label>Description</label>
                <textarea class="form-input" id="fieldDescInput" rows="3" 
                          placeholder="Describe what this field is used for">${field?.description || ''}</textarea>
            </div>

            <div class="form-group">
                <label>Field Key *</label>
                <input type="text" class="form-input" id="fieldKeyInput" 
                       value="${field?.key || ''}" placeholder="e.g., custom_field_1">
                <small>Used for API access and integrations</small>
            </div>

            <hr>

            <h4>Field Configuration</h4>
            <div id="fieldConfigInputs">
                ${this.renderConfigInputs(fieldType, field?.config)}
            </div>
        `;

        document.getElementById('fieldConfigDialog').style.display = 'block';

        if (window.lucide) {
            lucide.createIcons();
        }

        // Store type and field for saving
        this.currentFieldType = typeId;
        this.currentEditField = field;
    }

    closeConfigDialog() {
        document.getElementById('fieldConfigDialog').style.display = 'none';
        this.currentFieldType = null;
        this.currentEditField = null;
    }

    renderConfigInputs(fieldType, config = {}) {
        if (!fieldType.config || fieldType.config.length === 0) {
            return '<p class="empty-text">No additional configuration needed</p>';
        }

        return fieldType.config.map(configKey => {
            switch (configKey) {
                case 'options':
                    return `
                        <div class="form-group">
                            <label>Options (one per line)</label>
                            <textarea class="form-input" data-config="options" rows="5" 
                                      placeholder="Option 1\nOption 2\nOption 3">${(config.options || []).join('\n')}</textarea>
                        </div>
                    `;
                case 'defaultValue':
                    return `
                        <div class="form-group">
                            <label>Default Value</label>
                            <input type="text" class="form-input" data-config="defaultValue" 
                                   value="${config.defaultValue || ''}">
                        </div>
                    `;
                case 'maxLength':
                    return `
                        <div class="form-group">
                            <label>Maximum Length</label>
                            <input type="number" class="form-input" data-config="maxLength" 
                                   value="${config.maxLength || ''}" min="1">
                        </div>
                    `;
                case 'placeholder':
                    return `
                        <div class="form-group">
                            <label>Placeholder Text</label>
                            <input type="text" class="form-input" data-config="placeholder" 
                                   value="${config.placeholder || ''}">
                        </div>
                    `;
                case 'rows':
                    return `
                        <div class="form-group">
                            <label>Number of Rows</label>
                            <input type="number" class="form-input" data-config="rows" 
                                   value="${config.rows || 3}" min="1" max="20">
                        </div>
                    `;
                case 'min':
                case 'max':
                case 'step':
                    return `
                        <div class="form-group">
                            <label>${configKey.charAt(0).toUpperCase() + configKey.slice(1)}</label>
                            <input type="number" class="form-input" data-config="${configKey}" 
                                   value="${config[configKey] || ''}">
                        </div>
                    `;
                default:
                    return '';
            }
        }).join('');
    }

    async saveField() {
        const name = document.getElementById('fieldNameInput').value.trim();
        const description = document.getElementById('fieldDescInput').value.trim();
        const key = document.getElementById('fieldKeyInput').value.trim();

        if (!name || !key) {
            alert('Please fill in required fields');
            return;
        }

        // Gather config values
        const config = {};
        document.querySelectorAll('[data-config]').forEach(input => {
            const configKey = input.getAttribute('data-config');
            let value = input.value.trim();
            
            if (configKey === 'options') {
                value = value.split('\n').filter(o => o.trim());
            } else if (input.type === 'number') {
                value = value ? Number(value) : null;
            }
            
            if (value) {
                config[configKey] = value;
            }
        });

        const fieldData = {
            id: this.currentEditField?.id || `field-${Date.now()}`,
            name,
            description,
            key,
            type: this.currentFieldType,
            config,
            contexts: this.currentEditField?.contexts || []
        };

        try {
            const url = this.currentEditField 
                ? `/api/custom-fields/${fieldData.id}`
                : '/api/custom-fields';
            
            const response = await fetch(url, {
                method: this.currentEditField ? 'PUT' : 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(fieldData)
            });

            if (response.ok) {
                if (this.currentEditField) {
                    const index = this.customFields.findIndex(f => f.id === fieldData.id);
                    this.customFields[index] = fieldData;
                } else {
                    this.customFields.push(fieldData);
                }
                
                this.closeConfigDialog();
                this.renderFieldsList();
                this.selectField(fieldData.id);
            }
        } catch (error) {
            console.error('Failed to save field:', error);
        }
    }

    editField(fieldId) {
        const field = this.customFields.find(f => f.id === fieldId);
        if (field) {
            this.showConfigDialog(field.type, field);
        }
    }

    async deleteField(fieldId) {
        if (!confirm('Are you sure you want to delete this field? This cannot be undone.')) return;

        try {
            const response = await fetch(`/api/custom-fields/${fieldId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.customFields = this.customFields.filter(f => f.id !== fieldId);
                this.selectedField = null;
                this.renderFieldsList();
                
                document.getElementById('fieldsContentArea').innerHTML = `
                    <div class="empty-state">
                        <i data-lucide="package"></i>
                        <h3>Field Deleted</h3>
                        <p>Select another field or create a new one</p>
                    </div>
                `;
                
                if (window.lucide) {
                    lucide.createIcons();
                }
            }
        } catch (error) {
            console.error('Failed to delete field:', error);
        }
    }

    configureContext(fieldId) {
        const field = this.customFields.find(f => f.id === fieldId);
        if (!field) return;

        const content = document.getElementById('contextDialogContent');
        content.innerHTML = `
            <p>Configure where this field should appear</p>
            
            <div class="form-group">
                <label>Projects</label>
                <select class="form-input" id="contextProjects" multiple size="5">
                    <option value="all">All Projects</option>
                    <option value="test">TEST Project</option>
                    <option value="demo">DEMO Project</option>
                </select>
                <small>Hold Ctrl/Cmd to select multiple</small>
            </div>

            <div class="form-group">
                <label>Issue Types</label>
                <select class="form-input" id="contextIssueTypes" multiple size="5">
                    <option value="all">All Issue Types</option>
                    <option value="story">Story</option>
                    <option value="bug">Bug</option>
                    <option value="task">Task</option>
                    <option value="epic">Epic</option>
                </select>
                <small>Hold Ctrl/Cmd to select multiple</small>
            </div>
        `;

        document.getElementById('contextDialog').style.display = 'block';
        this.currentContextField = field;
    }

    closeContextDialog() {
        document.getElementById('contextDialog').style.display = 'none';
        this.currentContextField = null;
    }

    async saveContext() {
        if (!this.currentContextField) return;

        const projects = Array.from(document.getElementById('contextProjects').selectedOptions)
            .map(opt => opt.value);
        const issueTypes = Array.from(document.getElementById('contextIssueTypes').selectedOptions)
            .map(opt => opt.value);

        const context = {
            projects: projects.includes('all') ? null : projects,
            issueTypes: issueTypes.includes('all') ? null : issueTypes
        };

        this.currentContextField.contexts = [context];
        
        try {
            const response = await fetch(`/api/custom-fields/${this.currentContextField.id}/context`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(context)
            });

            if (response.ok) {
                this.closeContextDialog();
                this.renderFieldDetails(this.currentContextField);
            }
        } catch (error) {
            console.error('Failed to save context:', error);
        }
    }

    filterFields(query) {
        const filtered = query 
            ? this.customFields.filter(f => 
                f.name.toLowerCase().includes(query.toLowerCase()) ||
                f.type.toLowerCase().includes(query.toLowerCase())
            )
            : this.customFields;

        const container = document.getElementById('fieldsList');
        container.innerHTML = filtered.map(field => {
            const fieldType = this.fieldTypes.find(t => t.id === field.type);
            return `
                <div class="field-item" onclick="customFieldsManager.selectField('${field.id}')">
                    <div class="field-icon">
                        <i data-lucide="${fieldType?.icon || 'box'}"></i>
                    </div>
                    <div class="field-info">
                        <div class="field-name">${field.name}</div>
                        <div class="field-type">${fieldType?.name || field.type}</div>
                    </div>
                </div>
            `;
        }).join('');

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    showSchemesManager() {
        alert('Field Schemes Manager - To be implemented');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.customFieldsManager = new CustomFieldsManager();
});

// Global function to open custom fields
function openCustomFields() {
    window.customFieldsManager?.openModal();
}
