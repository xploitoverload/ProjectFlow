/**
 * Issue Import/Export System
 * Features: CSV/JSON import with field mapping, bulk create, export with filters
 */

class ImportExportSystem {
    constructor() {
        this.importData = null;
        this.fieldMappings = {};
        this.importPreview = [];
        this.availableFields = this.getAvailableFields();
        
        this.init();
    }

    init() {
        this.createModal();
        this.setupEventListeners();
    }

    getAvailableFields() {
        return [
            { id: 'summary', name: 'Summary', required: true, type: 'text' },
            { id: 'description', name: 'Description', required: false, type: 'textarea' },
            { id: 'type', name: 'Issue Type', required: true, type: 'select' },
            { id: 'priority', name: 'Priority', required: false, type: 'select' },
            { id: 'status', name: 'Status', required: false, type: 'select' },
            { id: 'assignee', name: 'Assignee', required: false, type: 'user' },
            { id: 'reporter', name: 'Reporter', required: false, type: 'user' },
            { id: 'labels', name: 'Labels', required: false, type: 'array' },
            { id: 'storyPoints', name: 'Story Points', required: false, type: 'number' },
            { id: 'dueDate', name: 'Due Date', required: false, type: 'date' },
            { id: 'epic', name: 'Epic', required: false, type: 'text' },
            { id: 'sprint', name: 'Sprint', required: false, type: 'text' }
        ];
    }

    createModal() {
        const modalHTML = `
            <div id="importExportModal" class="ie-modal" style="display: none;">
                <div class="ie-modal-backdrop"></div>
                <div class="ie-modal-container">
                    <div class="ie-modal-header">
                        <h2 id="ieModalTitle">Import / Export Issues</h2>
                        <button class="btn-icon" id="closeIEModal">
                            <i data-lucide="x"></i>
                        </button>
                    </div>

                    <div class="ie-modal-body">
                        <div class="ie-tabs">
                            <button class="ie-tab active" data-tab="import">
                                <i data-lucide="upload"></i>
                                Import
                            </button>
                            <button class="ie-tab" data-tab="export">
                                <i data-lucide="download"></i>
                                Export
                            </button>
                        </div>

                        <!-- Import Tab -->
                        <div id="importTab" class="ie-tab-content active">
                            <div class="import-step" id="step1" style="display: block;">
                                <h3>Step 1: Upload File</h3>
                                <p class="step-desc">Upload a CSV or JSON file containing your issues</p>

                                <div class="upload-area" id="uploadArea">
                                    <i data-lucide="upload-cloud"></i>
                                    <h4>Drag and drop file here</h4>
                                    <p>or click to browse</p>
                                    <input type="file" id="fileInput" accept=".csv,.json" style="display: none;">
                                    <button class="btn btn-primary" id="browseBtn">
                                        <i data-lucide="folder-open"></i>
                                        Browse Files
                                    </button>
                                </div>

                                <div class="file-info" id="fileInfo" style="display: none;">
                                    <div class="file-details">
                                        <i data-lucide="file"></i>
                                        <div class="file-meta">
                                            <div class="file-name" id="fileName"></div>
                                            <div class="file-size" id="fileSize"></div>
                                        </div>
                                    </div>
                                    <button class="btn btn-ghost btn-sm" id="changeFileBtn">Change File</button>
                                </div>

                                <div class="step-actions">
                                    <button class="btn btn-primary" id="nextStep1Btn" disabled>
                                        Next
                                        <i data-lucide="arrow-right"></i>
                                    </button>
                                </div>
                            </div>

                            <div class="import-step" id="step2" style="display: none;">
                                <h3>Step 2: Map Fields</h3>
                                <p class="step-desc">Map columns from your file to issue fields</p>

                                <div class="field-mappings" id="fieldMappings">
                                    <!-- Populated by JS -->
                                </div>

                                <div class="step-actions">
                                    <button class="btn btn-ghost" id="backStep2Btn">
                                        <i data-lucide="arrow-left"></i>
                                        Back
                                    </button>
                                    <button class="btn btn-primary" id="nextStep2Btn">
                                        Next
                                        <i data-lucide="arrow-right"></i>
                                    </button>
                                </div>
                            </div>

                            <div class="import-step" id="step3" style="display: none;">
                                <h3>Step 3: Preview & Import</h3>
                                <p class="step-desc">Review the issues before importing</p>

                                <div class="preview-stats">
                                    <div class="stat-card">
                                        <div class="stat-value" id="previewCount">0</div>
                                        <div class="stat-label">Issues to Import</div>
                                    </div>
                                    <div class="stat-card">
                                        <div class="stat-value" id="validCount">0</div>
                                        <div class="stat-label">Valid</div>
                                    </div>
                                    <div class="stat-card">
                                        <div class="stat-value" id="errorCount">0</div>
                                        <div class="stat-label">Errors</div>
                                    </div>
                                </div>

                                <div class="preview-table-container">
                                    <table class="preview-table" id="previewTable">
                                        <!-- Populated by JS -->
                                    </table>
                                </div>

                                <div class="step-actions">
                                    <button class="btn btn-ghost" id="backStep3Btn">
                                        <i data-lucide="arrow-left"></i>
                                        Back
                                    </button>
                                    <button class="btn btn-primary" id="importBtn">
                                        <i data-lucide="upload"></i>
                                        Import Issues
                                    </button>
                                </div>
                            </div>

                            <div class="import-step" id="step4" style="display: none;">
                                <div class="import-progress">
                                    <div class="progress-icon">
                                        <i data-lucide="loader"></i>
                                    </div>
                                    <h3>Importing Issues...</h3>
                                    <div class="progress-bar">
                                        <div class="progress-fill" id="progressFill"></div>
                                    </div>
                                    <p id="progressText">0 of 0 imported</p>
                                </div>
                            </div>

                            <div class="import-step" id="step5" style="display: none;">
                                <div class="import-success">
                                    <div class="success-icon">
                                        <i data-lucide="check-circle"></i>
                                    </div>
                                    <h3>Import Complete!</h3>
                                    <div class="import-summary">
                                        <p><strong id="successCount">0</strong> issues imported successfully</p>
                                        <p id="failedSummary" style="display: none;">
                                            <strong id="failedCount">0</strong> issues failed
                                        </p>
                                    </div>
                                    <button class="btn btn-primary" onclick="importExportSystem.closeModal()">
                                        Done
                                    </button>
                                </div>
                            </div>
                        </div>

                        <!-- Export Tab -->
                        <div id="exportTab" class="ie-tab-content">
                            <h3>Export Issues</h3>
                            <p class="step-desc">Export issues to CSV or JSON format</p>

                            <div class="export-options">
                                <div class="form-group">
                                    <label>Export Format</label>
                                    <div class="format-options">
                                        <label class="radio-option">
                                            <input type="radio" name="exportFormat" value="csv" checked>
                                            <div class="option-content">
                                                <i data-lucide="file-text"></i>
                                                <span>CSV</span>
                                            </div>
                                        </label>
                                        <label class="radio-option">
                                            <input type="radio" name="exportFormat" value="json">
                                            <div class="option-content">
                                                <i data-lucide="code"></i>
                                                <span>JSON</span>
                                            </div>
                                        </label>
                                        <label class="radio-option">
                                            <input type="radio" name="exportFormat" value="excel">
                                            <div class="option-content">
                                                <i data-lucide="table"></i>
                                                <span>Excel</span>
                                            </div>
                                        </label>
                                    </div>
                                </div>

                                <div class="form-group">
                                    <label>Filter Issues</label>
                                    <select class="form-input" id="exportFilter">
                                        <option value="all">All Issues</option>
                                        <option value="current-sprint">Current Sprint</option>
                                        <option value="backlog">Backlog</option>
                                        <option value="custom">Custom Filter...</option>
                                    </select>
                                </div>

                                <div class="form-group">
                                    <label>Fields to Export</label>
                                    <div class="field-checkboxes">
                                        ${this.availableFields.map(field => `
                                            <label class="checkbox-label">
                                                <input type="checkbox" name="exportFields" value="${field.id}" ${field.required ? 'checked disabled' : 'checked'}>
                                                <span>${field.name}</span>
                                            </label>
                                        `).join('')}
                                    </div>
                                </div>

                                <div class="export-actions">
                                    <button class="btn btn-primary" id="exportBtn">
                                        <i data-lucide="download"></i>
                                        Export Issues
                                    </button>
                                </div>
                            </div>
                        </div>
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
        document.getElementById('closeIEModal')?.addEventListener('click', () => {
            this.closeModal();
        });

        // Tab switching
        document.querySelectorAll('.ie-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.switchTab(e.currentTarget.dataset.tab);
            });
        });

        // Import: File upload
        document.getElementById('browseBtn')?.addEventListener('click', () => {
            document.getElementById('fileInput').click();
        });

        document.getElementById('fileInput')?.addEventListener('change', (e) => {
            this.handleFileSelect(e.target.files[0]);
        });

        // Drag and drop
        const uploadArea = document.getElementById('uploadArea');
        uploadArea?.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });

        uploadArea?.addEventListener('dragleave', () => {
            uploadArea.classList.remove('drag-over');
        });

        uploadArea?.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            this.handleFileSelect(e.dataTransfer.files[0]);
        });

        // Step navigation
        document.getElementById('changeFileBtn')?.addEventListener('click', () => {
            document.getElementById('fileInput').value = '';
            document.getElementById('fileInfo').style.display = 'none';
            document.getElementById('uploadArea').style.display = 'flex';
            document.getElementById('nextStep1Btn').disabled = true;
        });

        document.getElementById('nextStep1Btn')?.addEventListener('click', () => {
            this.goToStep(2);
        });

        document.getElementById('backStep2Btn')?.addEventListener('click', () => {
            this.goToStep(1);
        });

        document.getElementById('nextStep2Btn')?.addEventListener('click', () => {
            this.preparePreview();
            this.goToStep(3);
        });

        document.getElementById('backStep3Btn')?.addEventListener('click', () => {
            this.goToStep(2);
        });

        document.getElementById('importBtn')?.addEventListener('click', () => {
            this.startImport();
        });

        // Export
        document.getElementById('exportBtn')?.addEventListener('click', () => {
            this.exportIssues();
        });
    }

    openModal() {
        document.getElementById('importExportModal').style.display = 'block';
        this.goToStep(1);
    }

    closeModal() {
        document.getElementById('importExportModal').style.display = 'none';
        this.resetImport();
    }

    switchTab(tab) {
        document.querySelectorAll('.ie-tab').forEach(t => t.classList.remove('active'));
        document.querySelector(`[data-tab="${tab}"]`).classList.add('active');

        document.querySelectorAll('.ie-tab-content').forEach(c => c.classList.remove('active'));
        document.getElementById(`${tab}Tab`).classList.add('active');
    }

    async handleFileSelect(file) {
        if (!file) return;

        const extension = file.name.split('.').pop().toLowerCase();
        if (!['csv', 'json'].includes(extension)) {
            alert('Please upload a CSV or JSON file');
            return;
        }

        document.getElementById('fileName').textContent = file.name;
        document.getElementById('fileSize').textContent = this.formatFileSize(file.size);
        document.getElementById('fileInfo').style.display = 'flex';
        document.getElementById('uploadArea').style.display = 'none';
        document.getElementById('nextStep1Btn').disabled = false;

        // Parse file
        try {
            const text = await file.text();
            if (extension === 'csv') {
                this.importData = this.parseCSV(text);
            } else {
                this.importData = JSON.parse(text);
            }
        } catch (error) {
            console.error('Failed to parse file:', error);
            alert('Failed to parse file');
        }
    }

    parseCSV(text) {
        const lines = text.split('\n').filter(line => line.trim());
        const headers = lines[0].split(',').map(h => h.trim());
        const data = [];

        for (let i = 1; i < lines.length; i++) {
            const values = lines[i].split(',').map(v => v.trim());
            const row = {};
            headers.forEach((header, index) => {
                row[header] = values[index] || '';
            });
            data.push(row);
        }

        return { headers, data };
    }

    formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }

    goToStep(step) {
        document.querySelectorAll('.import-step').forEach(s => s.style.display = 'none');
        document.getElementById(`step${step}`).style.display = 'block';

        if (step === 2) {
            this.renderFieldMappings();
        }
    }

    renderFieldMappings() {
        const container = document.getElementById('fieldMappings');
        const fileColumns = this.importData.headers;

        container.innerHTML = this.availableFields.map(field => `
            <div class="mapping-row">
                <div class="field-label">
                    <span>${field.name}</span>
                    ${field.required ? '<span class="required-badge">Required</span>' : ''}
                </div>
                <select class="form-input mapping-select" data-field="${field.id}">
                    <option value="">-- Do not map --</option>
                    ${fileColumns.map(col => `
                        <option value="${col}" ${this.autoMapField(field.id, col) ? 'selected' : ''}>
                            ${col}
                        </option>
                    `).join('')}
                </select>
            </div>
        `).join('');

        // Save mappings on change
        container.querySelectorAll('.mapping-select').forEach(select => {
            select.addEventListener('change', (e) => {
                this.fieldMappings[e.target.dataset.field] = e.target.value;
            });
            // Trigger initial change to save auto-mappings
            select.dispatchEvent(new Event('change'));
        });
    }

    autoMapField(fieldId, columnName) {
        const normalized = columnName.toLowerCase().replace(/[^a-z]/g, '');
        const fieldNormalized = fieldId.toLowerCase().replace(/[^a-z]/g, '');
        return normalized === fieldNormalized || normalized.includes(fieldNormalized);
    }

    preparePreview() {
        this.importPreview = this.importData.data.map(row => {
            const mapped = {};
            let errors = [];

            Object.entries(this.fieldMappings).forEach(([fieldId, column]) => {
                if (column) {
                    mapped[fieldId] = row[column];
                }
            });

            // Validate required fields
            this.availableFields.forEach(field => {
                if (field.required && !mapped[field.id]) {
                    errors.push(`Missing ${field.name}`);
                }
            });

            return { ...mapped, _errors: errors };
        });

        this.renderPreview();
    }

    renderPreview() {
        const validCount = this.importPreview.filter(i => i._errors.length === 0).length;
        const errorCount = this.importPreview.length - validCount;

        document.getElementById('previewCount').textContent = this.importPreview.length;
        document.getElementById('validCount').textContent = validCount;
        document.getElementById('errorCount').textContent = errorCount;

        const table = document.getElementById('previewTable');
        const mappedFields = Object.keys(this.fieldMappings).filter(k => this.fieldMappings[k]);

        table.innerHTML = `
            <thead>
                <tr>
                    <th>Status</th>
                    ${mappedFields.map(field => `<th>${this.availableFields.find(f => f.id === field)?.name}</th>`).join('')}
                </tr>
            </thead>
            <tbody>
                ${this.importPreview.slice(0, 10).map(issue => `
                    <tr class="${issue._errors.length > 0 ? 'error-row' : ''}">
                        <td>
                            ${issue._errors.length === 0 
                                ? '<i data-lucide="check-circle" class="success-icon"></i>' 
                                : `<i data-lucide="alert-circle" class="error-icon" title="${issue._errors.join(', ')}"></i>`
                            }
                        </td>
                        ${mappedFields.map(field => `<td>${issue[field] || '-'}</td>`).join('')}
                    </tr>
                `).join('')}
                ${this.importPreview.length > 10 ? `
                    <tr>
                        <td colspan="${mappedFields.length + 1}" class="more-row">
                            ... and ${this.importPreview.length - 10} more
                        </td>
                    </tr>
                ` : ''}
            </tbody>
        `;

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    async startImport() {
        this.goToStep(4);

        const validIssues = this.importPreview.filter(i => i._errors.length === 0);
        let imported = 0;
        let failed = 0;

        for (let i = 0; i < validIssues.length; i++) {
            try {
                await this.importIssue(validIssues[i]);
                imported++;
            } catch (error) {
                console.error('Failed to import issue:', error);
                failed++;
            }

            // Update progress
            const progress = ((i + 1) / validIssues.length) * 100;
            document.getElementById('progressFill').style.width = `${progress}%`;
            document.getElementById('progressText').textContent = `${i + 1} of ${validIssues.length} imported`;

            // Small delay to show progress
            await new Promise(resolve => setTimeout(resolve, 50));
        }

        // Show success
        document.getElementById('successCount').textContent = imported;
        if (failed > 0) {
            document.getElementById('failedCount').textContent = failed;
            document.getElementById('failedSummary').style.display = 'block';
        }

        this.goToStep(5);
    }

    async importIssue(issue) {
        const response = await fetch('/api/issues', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(issue)
        });

        if (!response.ok) {
            throw new Error('Import failed');
        }

        return response.json();
    }

    resetImport() {
        this.importData = null;
        this.fieldMappings = {};
        this.importPreview = [];
        document.getElementById('fileInput').value = '';
        document.getElementById('fileInfo').style.display = 'none';
        document.getElementById('uploadArea').style.display = 'flex';
        document.getElementById('nextStep1Btn').disabled = true;
    }

    async exportIssues() {
        const format = document.querySelector('input[name="exportFormat"]:checked').value;
        const filter = document.getElementById('exportFilter').value;
        const fields = Array.from(document.querySelectorAll('input[name="exportFields"]:checked'))
            .map(cb => cb.value);

        try {
            // Fetch issues based on filter
            const response = await fetch(`/api/issues/export?filter=${filter}&format=${format}&fields=${fields.join(',')}`);
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `issues-export.${format}`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            }
        } catch (error) {
            console.error('Export failed:', error);
            alert('Failed to export issues');
        }
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.importExportSystem = new ImportExportSystem();
});

// Global function to open import/export
function openImportExport() {
    window.importExportSystem?.openModal();
}
