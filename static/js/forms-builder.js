/**
 * Forms Builder & Management System
 * Drag-drop form builder, templates, submissions, analytics
 */

class FormsBuilder {
    constructor() {
        this.currentForm = null;
        this.formFields = [];
        this.forms = [];
        this.submissions = [];
        this.templates = [];
        
        this.fieldTypes = [
            { type: 'text', label: 'Short Text', icon: 'type' },
            { type: 'textarea', label: 'Long Text', icon: 'align-left' },
            { type: 'select', label: 'Dropdown', icon: 'chevron-down' },
            { type: 'checkbox', label: 'Checkbox', icon: 'check-square' },
            { type: 'radio', label: 'Radio Buttons', icon: 'circle' },
            { type: 'date', label: 'Date', icon: 'calendar' },
            { type: 'time', label: 'Time', icon: 'clock' },
            { type: 'email', label: 'Email', icon: 'mail' },
            { type: 'number', label: 'Number', icon: 'hash' },
            { type: 'file', label: 'File Upload', icon: 'upload' }
        ];
        
        this.init();
    }

    async init() {
        await this.loadForms();
        await this.loadTemplates();
        console.log('FormsBuilder initialized');
    }

    async loadForms() {
        try {
            const response = await fetch('/api/forms');
            this.forms = await response.json();
        } catch (error) {
            console.error('Failed to load forms:', error);
            this.loadMockForms();
        }
    }

    loadMockForms() {
        this.forms = [
            {
                id: 1,
                name: 'IT Help Request',
                description: 'Request IT assistance',
                submissions: 245,
                lastSubmission: '2026-01-23',
                status: 'active'
            },
            {
                id: 2,
                name: 'Bug Report',
                description: 'Report software issues',
                submissions: 189,
                lastSubmission: '2026-01-22',
                status: 'active'
            },
            {
                id: 3,
                name: 'Employee Onboarding',
                description: 'New employee information',
                submissions: 67,
                lastSubmission: '2026-01-20',
                status: 'active'
            }
        ];
    }

    async loadTemplates() {
        this.templates = [
            { id: 1, name: 'Incident Report', category: 'IT' },
            { id: 2, name: 'Change Request', category: 'IT' },
            { id: 3, name: 'Access Request', category: 'Security' },
            { id: 4, name: 'Feedback Form', category: 'General' },
            { id: 5, name: 'Expense Report', category: 'Finance' }
        ];
    }

    renderFormsView(container) {
        const html = `
            <div class="forms-container">
                <div class="forms-header">
                    <div class="forms-title">
                        <h1>Forms</h1>
                        <p>${this.forms.length} forms • ${this.calculateTotalSubmissions()} total submissions</p>
                    </div>
                    <div class="forms-actions">
                        <button class="btn-secondary" onclick="formsBuilder.openTemplatesModal()">
                            <i data-lucide="layout-template"></i>
                            Use Template
                        </button>
                        <button class="btn-primary" onclick="formsBuilder.createNewForm()">
                            <i data-lucide="plus"></i>
                            Create Form
                        </button>
                    </div>
                </div>

                <div class="forms-tabs">
                    <button class="tab-btn active" onclick="formsBuilder.switchTab('list')">
                        <i data-lucide="list"></i>
                        All Forms
                    </button>
                    <button class="tab-btn" onclick="formsBuilder.switchTab('templates')">
                        <i data-lucide="layout-template"></i>
                        Templates
                    </button>
                    <button class="tab-btn" onclick="formsBuilder.switchTab('analytics')">
                        <i data-lucide="bar-chart"></i>
                        Analytics
                    </button>
                </div>

                <div class="forms-list" id="formsListContent">
                    ${this.renderFormsList()}
                </div>
            </div>
        `;

        container.innerHTML = html;
        if (window.lucide) lucide.createIcons();
    }

    renderFormsList() {
        return this.forms.map(form => `
            <div class="form-card" onclick="formsBuilder.openForm(${form.id})">
                <div class="form-card-header">
                    <div class="form-icon">
                        <i data-lucide="file-text"></i>
                    </div>
                    <div class="form-card-actions" onclick="event.stopPropagation()">
                        <button class="btn-icon" onclick="formsBuilder.editForm(${form.id})">
                            <i data-lucide="edit"></i>
                        </button>
                        <button class="btn-icon" onclick="formsBuilder.showFormOptions(${form.id})">
                            <i data-lucide="more-vertical"></i>
                        </button>
                    </div>
                </div>
                <div class="form-card-content">
                    <h3>${form.name}</h3>
                    <p>${form.description}</p>
                    <div class="form-stats">
                        <div class="stat-item">
                            <i data-lucide="file-check"></i>
                            <span>${form.submissions} submissions</span>
                        </div>
                        <div class="stat-item">
                            <i data-lucide="clock"></i>
                            <span>Last: ${this.formatDate(form.lastSubmission)}</span>
                        </div>
                    </div>
                    <div class="form-status status-${form.status}">
                        ${form.status}
                    </div>
                </div>
            </div>
        `).join('');
    }

    createNewForm() {
        this.currentForm = {
            id: Date.now(),
            name: 'Untitled Form',
            description: '',
            fields: []
        };
        this.formFields = [];
        this.openFormBuilder();
    }

    openFormBuilder() {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay active';
        modal.innerHTML = `
            <div class="modal-dialog form-builder-modal">
                <div class="form-builder-header">
                    <div class="form-title-edit">
                        <input type="text" class="form-name-input" 
                               value="${this.currentForm.name}" 
                               placeholder="Form Name">
                        <input type="text" class="form-desc-input" 
                               value="${this.currentForm.description}" 
                               placeholder="Description">
                    </div>
                    <button class="btn-icon" onclick="formsBuilder.closeBuilder()">
                        <i data-lucide="x"></i>
                    </button>
                </div>

                <div class="form-builder-body">
                    <div class="field-palette">
                        <h3>Field Types</h3>
                        <div class="field-types-grid">
                            ${this.renderFieldPalette()}
                        </div>
                    </div>

                    <div class="form-canvas">
                        <div class="canvas-header">
                            <h3>Form Preview</h3>
                            <button class="btn-secondary" onclick="formsBuilder.previewForm()">
                                <i data-lucide="eye"></i>
                                Preview
                            </button>
                        </div>
                        <div class="form-fields-container" id="formFieldsContainer">
                            ${this.renderFormFields()}
                        </div>
                        <div class="canvas-empty-state" style="display: ${this.formFields.length === 0 ? 'flex' : 'none'}">
                            <i data-lucide="mouse-pointer-click"></i>
                            <p>Drag fields from the palette to start building your form</p>
                        </div>
                    </div>
                </div>

                <div class="form-builder-footer">
                    <button class="btn-secondary" onclick="formsBuilder.closeBuilder()">
                        Cancel
                    </button>
                    <button class="btn-primary" onclick="formsBuilder.saveForm()">
                        <i data-lucide="save"></i>
                        Save Form
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        this.setupDragAndDrop();
        if (window.lucide) lucide.createIcons();
    }

    renderFieldPalette() {
        return this.fieldTypes.map(field => `
            <div class="field-type-card" draggable="true" 
                 data-field-type="${field.type}">
                <i data-lucide="${field.icon}"></i>
                <span>${field.label}</span>
            </div>
        `).join('');
    }

    renderFormFields() {
        return this.formFields.map((field, index) => `
            <div class="form-field-item" data-field-id="${field.id}">
                <div class="field-drag-handle">
                    <i data-lucide="grip-vertical"></i>
                </div>
                <div class="field-content">
                    <div class="field-header">
                        <input type="text" class="field-label-input" 
                               value="${field.label}" 
                               placeholder="Field Label"
                               onchange="formsBuilder.updateFieldLabel(${field.id}, this.value)">
                        <label class="field-required-toggle">
                            <input type="checkbox" ${field.required ? 'checked' : ''}
                                   onchange="formsBuilder.toggleFieldRequired(${field.id})">
                            <span>Required</span>
                        </label>
                    </div>
                    <div class="field-preview">
                        ${this.renderFieldPreview(field)}
                    </div>
                    ${field.type === 'select' || field.type === 'radio' || field.type === 'checkbox' ? `
                        <div class="field-options">
                            <label>Options (one per line)</label>
                            <textarea class="field-options-input" 
                                      onchange="formsBuilder.updateFieldOptions(${field.id}, this.value)"
                            >${field.options ? field.options.join('\n') : ''}</textarea>
                        </div>
                    ` : ''}
                </div>
                <div class="field-actions">
                    <button class="btn-icon" onclick="formsBuilder.duplicateField(${field.id})">
                        <i data-lucide="copy"></i>
                    </button>
                    <button class="btn-icon btn-danger" onclick="formsBuilder.deleteField(${field.id})">
                        <i data-lucide="trash-2"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }

    renderFieldPreview(field) {
        switch (field.type) {
            case 'text':
            case 'email':
            case 'number':
                return `<input type="${field.type}" placeholder="Enter ${field.label}" disabled>`;
            case 'textarea':
                return `<textarea placeholder="Enter ${field.label}" disabled></textarea>`;
            case 'select':
                return `<select disabled><option>Select option</option></select>`;
            case 'checkbox':
                return `<label><input type="checkbox" disabled> Checkbox option</label>`;
            case 'radio':
                return `<label><input type="radio" disabled> Radio option</label>`;
            case 'date':
                return `<input type="date" disabled>`;
            case 'time':
                return `<input type="time" disabled>`;
            case 'file':
                return `<div class="file-upload-preview">
                    <i data-lucide="upload"></i>
                    <span>Click to upload or drag and drop</span>
                </div>`;
            default:
                return `<input type="text" placeholder="${field.type}" disabled>`;
        }
    }

    setupDragAndDrop() {
        const fieldTypes = document.querySelectorAll('.field-type-card');
        const container = document.getElementById('formFieldsContainer');

        fieldTypes.forEach(card => {
            card.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('fieldType', card.dataset.fieldType);
            });
        });

        if (container) {
            container.addEventListener('dragover', (e) => {
                e.preventDefault();
                container.classList.add('drag-over');
            });

            container.addEventListener('dragleave', () => {
                container.classList.remove('drag-over');
            });

            container.addEventListener('drop', (e) => {
                e.preventDefault();
                container.classList.remove('drag-over');
                
                const fieldType = e.dataTransfer.getData('fieldType');
                this.addField(fieldType);
            });
        }
    }

    addField(type) {
        const field = {
            id: Date.now(),
            type: type,
            label: this.fieldTypes.find(f => f.type === type)?.label || type,
            required: false,
            options: type === 'select' || type === 'radio' || type === 'checkbox' 
                ? ['Option 1', 'Option 2', 'Option 3'] : null
        };

        this.formFields.push(field);
        this.refreshFormCanvas();
    }

    refreshFormCanvas() {
        const container = document.getElementById('formFieldsContainer');
        if (container) {
            container.innerHTML = this.renderFormFields();
            if (window.lucide) lucide.createIcons();
        }

        const emptyState = document.querySelector('.canvas-empty-state');
        if (emptyState) {
            emptyState.style.display = this.formFields.length === 0 ? 'flex' : 'none';
        }
    }

    updateFieldLabel(fieldId, label) {
        const field = this.formFields.find(f => f.id === fieldId);
        if (field) field.label = label;
    }

    toggleFieldRequired(fieldId) {
        const field = this.formFields.find(f => f.id === fieldId);
        if (field) field.required = !field.required;
    }

    updateFieldOptions(fieldId, optionsText) {
        const field = this.formFields.find(f => f.id === fieldId);
        if (field) {
            field.options = optionsText.split('\n').filter(o => o.trim());
        }
    }

    duplicateField(fieldId) {
        const field = this.formFields.find(f => f.id === fieldId);
        if (field) {
            const duplicate = { ...field, id: Date.now(), label: field.label + ' (Copy)' };
            this.formFields.push(duplicate);
            this.refreshFormCanvas();
        }
    }

    deleteField(fieldId) {
        this.formFields = this.formFields.filter(f => f.id !== fieldId);
        this.refreshFormCanvas();
    }

    saveForm() {
        const nameInput = document.querySelector('.form-name-input');
        const descInput = document.querySelector('.form-desc-input');

        this.currentForm.name = nameInput?.value || 'Untitled Form';
        this.currentForm.description = descInput?.value || '';
        this.currentForm.fields = this.formFields;

        alert(`Form "${this.currentForm.name}" saved successfully!`);
        this.closeBuilder();
    }

    closeBuilder() {
        const modal = document.querySelector('.modal-overlay');
        if (modal) modal.remove();
    }

    calculateTotalSubmissions() {
        return this.forms.reduce((sum, form) => sum + form.submissions, 0);
    }

    formatDate(dateStr) {
        const date = new Date(dateStr);
        const options = { month: 'short', day: 'numeric' };
        return date.toLocaleDateString('en-US', options);
    }

    switchTab(tab) {
        // Tab switching logic
        console.log('Switching to tab:', tab);
    }

    openForm(formId) {
        console.log('Opening form:', formId);
    }

    editForm(formId) {
        const form = this.forms.find(f => f.id === formId);
        if (form) {
            this.currentForm = form;
            this.formFields = form.fields || [];
            this.openFormBuilder();
        }
    }

    previewForm() {
        alert('Form preview would open here');
    }

    openTemplatesModal() {
        alert('Templates modal would open here');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.formsBuilder = new FormsBuilder();
});
