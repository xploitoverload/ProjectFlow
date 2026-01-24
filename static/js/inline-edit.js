/**
 * Inline Edit Manager - JIRA-style inline editing for issue fields
 * Enables click-to-edit functionality without modal popups
 */

class InlineEditManager {
    constructor() {
        this.editingElement = null;
        this.originalValue = null;
        this.init();
    }

    init() {
        // Setup event delegation for inline-editable elements
        document.addEventListener('click', (e) => {
            const editable = e.target.closest('[data-inline-edit]');
            if (editable && !editable.classList.contains('editing')) {
                this.startEdit(editable);
            }
        });

        // Handle clicks outside to save
        document.addEventListener('click', (e) => {
            if (this.editingElement && !e.target.closest('[data-inline-edit]')) {
                this.saveEdit(this.editingElement);
            }
        });

        // Handle keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (this.editingElement) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.saveEdit(this.editingElement);
                } else if (e.key === 'Escape') {
                    e.preventDefault();
                    this.cancelEdit(this.editingElement);
                }
            }
        });
    }

    startEdit(element) {
        // Don't start if another element is being edited
        if (this.editingElement && this.editingElement !== element) {
            this.saveEdit(this.editingElement);
        }

        this.editingElement = element;
        this.originalValue = element.textContent.trim();
        
        element.classList.add('editing');
        element.contentEditable = true;
        element.setAttribute('spellcheck', 'false');
        
        // Store original styles
        element.dataset.originalBorder = element.style.border;
        element.dataset.originalPadding = element.style.padding;
        
        // Apply editing styles
        element.style.border = '2px solid #0052cc';
        element.style.borderRadius = '3px';
        element.style.padding = '4px 6px';
        element.style.outline = 'none';
        element.style.background = 'rgba(255, 255, 255, 0.05)';
        
        // Select all text
        const range = document.createRange();
        range.selectNodeContents(element);
        const sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(range);

        // Show save indicator
        this.showEditIndicator(element);
    }

    async saveEdit(element) {
        if (!element || !element.classList.contains('editing')) return;

        const newValue = element.textContent.trim();
        
        // Don't save if value hasn't changed
        if (newValue === this.originalValue) {
            this.cancelEdit(element);
            return;
        }

        // Validate
        if (!newValue) {
            window.notificationManager.addNotification({
                title: 'Validation Error',
                message: 'Value cannot be empty',
                type: 'error'
            });
            element.textContent = this.originalValue;
            this.cancelEdit(element);
            return;
        }

        // Get update details
        const issueId = element.closest('[data-issue-id]')?.dataset.issueId;
        const field = element.dataset.inlineEdit;
        
        if (!issueId || !field) {
            console.error('Missing issueId or field for inline edit');
            this.cancelEdit(element);
            return;
        }

        // Show loading state
        element.classList.add('saving');
        element.contentEditable = false;

        try {
            // Make API call to update
            const response = await fetch(`/api/issues/${issueId}/update`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    field: field,
                    value: newValue
                })
            });

            if (response.ok) {
                // Success
                window.notificationManager.addNotification({
                    title: 'Field Updated',
                    message: `${field} updated successfully`,
                    type: 'success'
                });
                
                this.cleanupEdit(element);
                this.originalValue = newValue;
            } else {
                throw new Error('Update failed');
            }
        } catch (error) {
            // Revert on error
            element.textContent = this.originalValue;
            window.notificationManager.addNotification({
                title: 'Update Failed',
                message: 'Could not save changes',
                type: 'error'
            });
            this.cleanupEdit(element);
        }
    }

    cancelEdit(element) {
        if (!element) return;
        
        element.textContent = this.originalValue;
        this.cleanupEdit(element);
    }

    cleanupEdit(element) {
        element.classList.remove('editing', 'saving');
        element.contentEditable = false;
        
        // Restore original styles
        element.style.border = element.dataset.originalBorder || '';
        element.style.padding = element.dataset.originalPadding || '';
        element.style.background = '';
        element.style.outline = '';
        
        this.hideEditIndicator(element);
        this.editingElement = null;
        this.originalValue = null;
    }

    showEditIndicator(element) {
        const indicator = document.createElement('div');
        indicator.className = 'inline-edit-indicator';
        indicator.innerHTML = `
            <div class="inline-edit-tooltip">
                <span>Press <kbd>Enter</kbd> to save, <kbd>Esc</kbd> to cancel</span>
            </div>
        `;
        element.parentElement.style.position = 'relative';
        element.parentElement.appendChild(indicator);
    }

    hideEditIndicator(element) {
        const indicator = element.parentElement.querySelector('.inline-edit-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    // Public method to enable inline edit on elements
    static enableOn(selector, field) {
        document.querySelectorAll(selector).forEach(el => {
            el.dataset.inlineEdit = field;
            el.style.cursor = 'text';
            el.title = `Click to edit ${field}`;
        });
    }
}

// CSS for inline editing
const style = document.createElement('style');
style.textContent = `
    [data-inline-edit] {
        position: relative;
        transition: all 0.2s;
    }

    [data-inline-edit]:hover:not(.editing) {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 3px;
        outline: 1px dashed var(--jira-border, #ddd);
        outline-offset: 2px;
    }

    [data-inline-edit].editing {
        box-shadow: 0 0 0 3px rgba(0, 82, 204, 0.1);
        position: relative;
        z-index: 10;
    }

    [data-inline-edit].saving {
        opacity: 0.6;
        pointer-events: none;
        position: relative;
    }

    [data-inline-edit].saving::after {
        content: '';
        position: absolute;
        right: 8px;
        top: 50%;
        transform: translateY(-50%);
        width: 12px;
        height: 12px;
        border: 2px solid #0052cc;
        border-top-color: transparent;
        border-radius: 50%;
        animation: spin 0.6s linear infinite;
    }

    @keyframes spin {
        to { transform: translateY(-50%) rotate(360deg); }
    }

    .inline-edit-indicator {
        position: absolute;
        bottom: -32px;
        left: 0;
        z-index: 1000;
    }

    .inline-edit-tooltip {
        background: var(--jira-darker-bg, #1d2125);
        border: 1px solid var(--jira-border, #2c333a);
        border-radius: 4px;
        padding: 6px 10px;
        font-size: 11px;
        color: var(--jira-text, #b6c2cf);
        white-space: nowrap;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }

    .inline-edit-tooltip kbd {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 3px;
        padding: 2px 5px;
        font-size: 10px;
        font-family: monospace;
        margin: 0 2px;
    }

    /* Priority icons */
    .priority-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 20px;
        height: 20px;
        border-radius: 3px;
    }

    .priority-icon.critical {
        color: #ff5630;
        background: rgba(255, 86, 48, 0.1);
    }

    .priority-icon.highest {
        color: #ff5630;
    }

    .priority-icon.high {
        color: #ff8b00;
    }

    .priority-icon.medium {
        color: #ffab00;
    }

    .priority-icon.low {
        color: #36b37e;
    }

    .priority-icon.lowest {
        color: #6554c0;
    }

    /* Story points badge */
    .story-points-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 20px;
        height: 20px;
        padding: 0 6px;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid var(--jira-border, #2c333a);
        border-radius: 3px;
        font-size: 11px;
        font-weight: 600;
        color: var(--jira-text-secondary, #8c9bab);
    }

    /* Assignee avatar improvements */
    .assignee-avatar-enhanced {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 10px;
        font-weight: 700;
        color: white;
        border: 2px solid var(--jira-card-bg, #22272b);
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        cursor: pointer;
        transition: transform 0.2s;
    }

    .assignee-avatar-enhanced:hover {
        transform: scale(1.1);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }

    /* Due date indicator with color coding */
    .due-date-indicator {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 2px 6px;
        border-radius: 3px;
        font-size: 11px;
        font-weight: 500;
    }

    .due-date-indicator.overdue {
        background: rgba(255, 86, 48, 0.1);
        color: #ff5630;
    }

    .due-date-indicator.due-soon {
        background: rgba(255, 171, 0, 0.1);
        color: #ffab00;
    }

    .due-date-indicator.on-track {
        color: var(--jira-text-secondary, #8c9bab);
    }
`;
document.head.appendChild(style);

// Initialize on DOM load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.inlineEditManager = new InlineEditManager();
    });
} else {
    window.inlineEditManager = new InlineEditManager();
}
