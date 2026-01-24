/**
 * Issue Templates System
 * Pre-configured templates for quick issue creation
 */

class IssueTemplates {
    constructor() {
        this.templates = [];
        this.selectedTemplate = null;
        
        this.init();
    }

    async init() {
        await this.loadTemplates();
        this.createModal();
    }

    createModal() {
        const modalHTML = `
            <div id="templatesModal" class="templates-modal" style="display: none;">
                <div class="templates-backdrop"></div>
                <div class="templates-container">
                    <div class="templates-sidebar">
                        <div class="sidebar-header">
                            <h3>Templates</h3>
                            <button class="btn-icon-sm" onclick="issueTemplates.closeModal()">
                                <i data-lucide="x"></i>
                            </button>
                        </div>
                        
                        <div class="template-categories">
                            <button class="category-btn active" data-category="all" onclick="issueTemplates.filterByCategory('all')">
                                <i data-lucide="layout-grid"></i>
                                All Templates
                            </button>
                            <button class="category-btn" data-category="bug" onclick="issueTemplates.filterByCategory('bug')">
                                <i data-lucide="bug"></i>
                                Bug Reports
                            </button>
                            <button class="category-btn" data-category="feature" onclick="issueTemplates.filterByCategory('feature')">
                                <i data-lucide="sparkles"></i>
                                Features
                            </button>
                            <button class="category-btn" data-category="task" onclick="issueTemplates.filterByCategory('task')">
                                <i data-lucide="check-square"></i>
                                Tasks
                            </button>
                            <button class="category-btn" data-category="story" onclick="issueTemplates.filterByCategory('story')">
                                <i data-lucide="book-open"></i>
                                User Stories
                            </button>
                        </div>
                        
                        <div class="template-list" id="templateList">
                            <!-- Populated by JS -->
                        </div>
                        
                        <div class="sidebar-footer">
                            <button class="btn-secondary btn-block" onclick="issueTemplates.createTemplate()">
                                <i data-lucide="plus"></i>
                                Create Template
                            </button>
                        </div>
                    </div>
                    
                    <div class="templates-content" id="templatesContent">
                        <!-- Populated by JS -->
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    async loadTemplates() {
        try {
            const response = await fetch('/api/templates');
            this.templates = await response.json();
            this.renderTemplateList();
        } catch (error) {
            console.error('Failed to load templates:', error);
            this.templates = this.getDefaultTemplates();
            this.renderTemplateList();
        }
    }

    getDefaultTemplates() {
        return [
            {
                id: 1,
                name: 'Bug Report',
                category: 'bug',
                icon: 'bug',
                description: 'Standard bug report template',
                issueType: 'Bug',
                priority: 'Medium',
                fields: {
                    summary: '',
                    description: `## Bug Description
Describe the bug in detail.

## Steps to Reproduce
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior
What should happen?

## Actual Behavior
What actually happens?

## Environment
- Browser: 
- OS: 
- Version: 

## Screenshots
If applicable, add screenshots.`,
                    labels: ['bug']
                }
            },
            {
                id: 2,
                name: 'Feature Request',
                category: 'feature',
                icon: 'sparkles',
                description: 'New feature proposal template',
                issueType: 'Feature',
                priority: 'Medium',
                fields: {
                    summary: '',
                    description: `## Feature Overview
Brief description of the feature.

## Problem Statement
What problem does this solve?

## Proposed Solution
How should this work?

## Alternatives Considered
What other approaches did you consider?

## Additional Context
Any other information or mockups.`,
                    labels: ['feature', 'enhancement']
                }
            },
            {
                id: 3,
                name: 'User Story',
                category: 'story',
                icon: 'book-open',
                description: 'Agile user story template',
                issueType: 'Story',
                priority: 'Medium',
                fields: {
                    summary: 'As a [user type], I want [goal] so that [benefit]',
                    description: `## User Story
As a [user type]
I want [goal]
So that [benefit]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Definition of Done
- [ ] Code complete
- [ ] Tests written
- [ ] Documentation updated
- [ ] Code reviewed
- [ ] Deployed to staging`,
                    labels: ['story']
                }
            },
            {
                id: 4,
                name: 'Technical Task',
                category: 'task',
                icon: 'code',
                description: 'Technical implementation task',
                issueType: 'Task',
                priority: 'Medium',
                fields: {
                    summary: '',
                    description: `## Task Description
What needs to be done?

## Technical Details
Implementation approach and considerations.

## Dependencies
List any dependencies or blockers.

## Checklist
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3`,
                    labels: ['technical']
                }
            },
            {
                id: 5,
                name: 'Research Spike',
                category: 'task',
                icon: 'search',
                description: 'Research and investigation task',
                issueType: 'Task',
                priority: 'Low',
                fields: {
                    summary: 'Research: [topic]',
                    description: `## Research Goal
What question needs to be answered?

## Approach
How will you investigate?

## Success Criteria
What constitutes a successful outcome?

## Findings
[To be filled during research]

## Recommendation
[To be filled after research]`,
                    labels: ['research', 'spike']
                }
            },
            {
                id: 6,
                name: 'Security Vulnerability',
                category: 'bug',
                icon: 'shield-alert',
                description: 'Security issue report',
                issueType: 'Bug',
                priority: 'Critical',
                fields: {
                    summary: '[SECURITY] ',
                    description: `## Vulnerability Type
Classification (e.g., XSS, SQL Injection, etc.)

## Severity
Critical / High / Medium / Low

## Affected Component
Which part of the system is affected?

## Description
Detailed description of the vulnerability.

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Impact
What damage could this cause?

## Remediation
How to fix this issue?`,
                    labels: ['security', 'critical']
                }
            },
            {
                id: 7,
                name: 'Documentation',
                category: 'task',
                icon: 'file-text',
                description: 'Documentation task',
                issueType: 'Task',
                priority: 'Low',
                fields: {
                    summary: 'Docs: ',
                    description: `## Documentation Need
What needs to be documented?

## Target Audience
Who is this documentation for?

## Content Outline
- Section 1
- Section 2
- Section 3

## Related Resources
Links to existing documentation or references.`,
                    labels: ['documentation']
                }
            },
            {
                id: 8,
                name: 'Performance Issue',
                category: 'bug',
                icon: 'gauge',
                description: 'Performance problem template',
                issueType: 'Bug',
                priority: 'High',
                fields: {
                    summary: '[PERFORMANCE] ',
                    description: `## Performance Issue
Description of the performance problem.

## Current Performance
Metrics showing current performance.

## Expected Performance
Target performance metrics.

## Profiling Data
Performance profiling results or screenshots.

## Proposed Optimization
Suggestions for improvement.`,
                    labels: ['performance', 'optimization']
                }
            }
        ];
    }

    openModal() {
        document.getElementById('templatesModal').style.display = 'flex';
        this.renderTemplateList();
        
        if (window.lucide) {
            lucide.createIcons();
        }
    }

    closeModal() {
        document.getElementById('templatesModal').style.display = 'none';
    }

    filterByCategory(category) {
        // Update active button
        document.querySelectorAll('.category-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-category="${category}"]`)?.classList.add('active');
        
        this.renderTemplateList(category);
    }

    renderTemplateList(category = 'all') {
        const filtered = category === 'all' 
            ? this.templates 
            : this.templates.filter(t => t.category === category);

        const container = document.getElementById('templateList');
        
        if (filtered.length === 0) {
            container.innerHTML = `
                <div class="empty-templates">
                    <i data-lucide="inbox"></i>
                    <p>No templates found</p>
                </div>
            `;
            if (window.lucide) lucide.createIcons();
            return;
        }

        container.innerHTML = filtered.map(template => `
            <div class="template-item ${this.selectedTemplate?.id === template.id ? 'active' : ''}"
                 onclick="issueTemplates.selectTemplate(${template.id})">
                <div class="template-icon">
                    <i data-lucide="${template.icon}"></i>
                </div>
                <div class="template-info">
                    <div class="template-name">${template.name}</div>
                    <div class="template-desc">${template.description}</div>
                </div>
            </div>
        `).join('');

        if (window.lucide) {
            lucide.createIcons();
        }

        // Select first template if none selected
        if (!this.selectedTemplate && filtered.length > 0) {
            this.selectTemplate(filtered[0].id);
        }
    }

    selectTemplate(templateId) {
        this.selectedTemplate = this.templates.find(t => t.id === templateId);
        
        // Update UI
        document.querySelectorAll('.template-item').forEach(item => {
            item.classList.remove('active');
        });
        event?.currentTarget?.classList.add('active');
        
        this.renderTemplatePreview();
    }

    renderTemplatePreview() {
        if (!this.selectedTemplate) {
            document.getElementById('templatesContent').innerHTML = `
                <div class="empty-preview">
                    <i data-lucide="file"></i>
                    <p>Select a template to preview</p>
                </div>
            `;
            if (window.lucide) lucide.createIcons();
            return;
        }

        const template = this.selectedTemplate;

        document.getElementById('templatesContent').innerHTML = `
            <div class="template-preview">
                <div class="preview-header">
                    <div class="preview-title">
                        <div class="preview-icon">
                            <i data-lucide="${template.icon}"></i>
                        </div>
                        <div>
                            <h3>${template.name}</h3>
                            <p>${template.description}</p>
                        </div>
                    </div>
                    <div class="preview-actions">
                        <button class="btn-secondary" onclick="issueTemplates.editTemplate(${template.id})">
                            <i data-lucide="edit-2"></i>
                            Edit
                        </button>
                        <button class="btn-primary" onclick="issueTemplates.useTemplate(${template.id})">
                            <i data-lucide="plus-circle"></i>
                            Use Template
                        </button>
                    </div>
                </div>

                <div class="preview-body">
                    <div class="preview-section">
                        <h4>Default Values</h4>
                        <div class="preview-fields">
                            <div class="field-item">
                                <span class="field-label">Type:</span>
                                <span class="field-value type-badge ${template.issueType.toLowerCase()}">${template.issueType}</span>
                            </div>
                            <div class="field-item">
                                <span class="field-label">Priority:</span>
                                <span class="field-value priority-badge ${template.priority.toLowerCase()}">${template.priority}</span>
                            </div>
                            ${template.fields.labels ? `
                                <div class="field-item">
                                    <span class="field-label">Labels:</span>
                                    <span class="field-value">
                                        ${template.fields.labels.map(l => `<span class="label-badge">${l}</span>`).join('')}
                                    </span>
                                </div>
                            ` : ''}
                        </div>
                    </div>

                    <div class="preview-section">
                        <h4>Description Template</h4>
                        <div class="description-preview">
                            <pre>${template.fields.description}</pre>
                        </div>
                    </div>
                </div>
            </div>
        `;

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    async useTemplate(templateId) {
        const template = this.templates.find(t => t.id === templateId);
        if (!template) return;

        // Create issue with template data
        try {
            // Open issue detail modal pre-filled with template
            if (window.issueDetailModal) {
                this.closeModal();
                issueDetailModal.openForCreate({
                    type: template.issueType,
                    priority: template.priority,
                    summary: template.fields.summary,
                    description: template.fields.description,
                    labels: template.fields.labels || []
                });
            } else {
                alert('Issue creation not available');
            }
        } catch (error) {
            console.error('Failed to use template:', error);
        }
    }

    createTemplate() {
        alert('Create Template - Integration point for form dialog');
    }

    editTemplate(templateId) {
        alert(`Edit Template ${templateId} - Integration point`);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.issueTemplates = new IssueTemplates();
});
