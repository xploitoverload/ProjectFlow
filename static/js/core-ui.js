/**
 * Core UI Interactions - Essential JavaScript for dropdown, modal, and form functionality
 * This file provides the basic interactivity that makes the UI functional.
 */

// Global UI Controller
class UIController {
    constructor() {
        this.init();
    }
    
    init() {
        this.setupDropdowns();
        this.setupModals();
        this.setupFormValidation();
        this.setupKeyboardShortcuts();
        this.setupLoadingStates();
        
        console.log('✅ UI Controller initialized');
    }
    
    // ========== DROPDOWN FUNCTIONALITY ==========
    setupDropdowns() {
        // Handle all select elements
        document.querySelectorAll('select').forEach(select => {
            // Ensure change events work
            select.addEventListener('change', (e) => {
                // Trigger any onchange attributes
                if (e.target.onchange) {
                    e.target.onchange();
                }
            });
        });
        
        // Custom dropdown handling
        document.addEventListener('click', (e) => {
            // Close all dropdowns when clicking outside
            if (!e.target.closest('.dropdown')) {
                this.closeAllDropdowns();
            }
        });
    }
    
    closeAllDropdowns() {
        document.querySelectorAll('.dropdown.open').forEach(dropdown => {
            dropdown.classList.remove('open');
        });
    }
    
    // ========== MODAL FUNCTIONALITY ==========
    setupModals() {
        // Auto-setup modal close buttons
        document.querySelectorAll('.modal .btn-icon, .modal .modal-backdrop').forEach(btn => {
            btn.addEventListener('click', (e) => {
                if (e.target.classList.contains('modal-backdrop') || e.target.closest('.btn-icon')) {
                    this.closeModal(e.target.closest('.modal'));
                }
            });
        });
        
        // ESC key closes modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });
    }
    
    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'flex';
            modal.classList.add('show');
            
            // Focus first input
            const firstInput = modal.querySelector('input, select, textarea');
            if (firstInput) {
                setTimeout(() => firstInput.focus(), 100);
            }
            
            console.log(`Opened modal: ${modalId}`);
        }
    }
    
    closeModal(modal) {
        if (typeof modal === 'string') {
            modal = document.getElementById(modal);
        }
        
        if (modal) {
            modal.style.display = 'none';
            modal.classList.remove('show');
            
            // Reset form if present
            const form = modal.querySelector('form');
            if (form) {
                form.reset();
                this.clearFormErrors(form);
            }
        }
    }
    
    closeAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            this.closeModal(modal);
        });
    }
    
    // ========== FORM VALIDATION ==========
    setupFormValidation() {
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                    return false;
                }
                
                // Show loading state for submit buttons
                const submitBtn = form.querySelector('button[type=\"submit\"]');
                if (submitBtn) {
                    this.showLoadingState(submitBtn);
                }
            });
        });
    }
    
    validateForm(form) {
        let isValid = true;
        this.clearFormErrors(form);
        
        // Check required fields
        form.querySelectorAll('[required]').forEach(field => {
            if (!field.value.trim()) {
                this.showFieldError(field, 'This field is required');
                isValid = false;
            }
        });
        
        // Custom validations
        const customValidations = {
            email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            url: /^https?:\/\/.+/,
            number: /^\d+$/
        };
        
        form.querySelectorAll('[data-validate]').forEach(field => {
            const validateType = field.dataset.validate;
            if (customValidations[validateType] && field.value) {
                if (!customValidations[validateType].test(field.value)) {
                    this.showFieldError(field, `Please enter a valid ${validateType}`);
                    isValid = false;
                }
            }
        });
        
        return isValid;
    }
    
    showFieldError(field, message) {
        field.classList.add('error');
        
        // Remove existing error message
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
        
        // Add new error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.textContent = message;
        errorDiv.style.cssText = 'color: #dc3545; font-size: 12px; margin-top: 4px;';
        field.parentNode.appendChild(errorDiv);
        
        // Focus first error field
        if (!field.parentNode.querySelector('.error')) {
            field.focus();
        }
    }
    
    clearFormErrors(form) {
        form.querySelectorAll('.error').forEach(field => {
            field.classList.remove('error');
        });
        form.querySelectorAll('.field-error').forEach(error => {
            error.remove();
        });
    }
    
    // ========== LOADING STATES ==========
    setupLoadingStates() {
        // Auto-handle loading states for buttons with data-loading-text
        document.querySelectorAll('[data-loading-text]').forEach(btn => {
            btn.addEventListener('click', () => {
                this.showLoadingState(btn);
            });
        });
    }
    
    showLoadingState(button) {
        if (button.dataset.originalText) return; // Already loading
        
        button.dataset.originalText = button.textContent;
        button.textContent = button.dataset.loadingText || 'Loading...';
        button.disabled = true;
        
        // Auto-reset after 10 seconds (failsafe)
        setTimeout(() => {
            this.hideLoadingState(button);
        }, 10000);
    }
    
    hideLoadingState(button) {
        if (button.dataset.originalText) {
            button.textContent = button.dataset.originalText;
            delete button.dataset.originalText;
            button.disabled = false;
        }
    }
    
    // ========== KEYBOARD SHORTCUTS ==========
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+Enter to submit forms
            if (e.ctrlKey && e.key === 'Enter') {
                const activeForm = document.activeElement.closest('form');
                if (activeForm) {
                    e.preventDefault();
                    const submitBtn = activeForm.querySelector('button[type=\"submit\"]');
                    if (submitBtn) submitBtn.click();
                }
            }
        });
    }
    
    // ========== UTILITY METHODS ==========
    showNotification(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 6px;
            color: white;
            font-weight: 500;
            z-index: 10000;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease;
            max-width: 400px;
        `;
        
        // Set colors based on type
        const colors = {
            success: '#10b981',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#3b82f6'
        };
        notification.style.backgroundColor = colors[type] || colors.info;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Auto-remove
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }, duration);
    }
}

// Global functions for template compatibility
function openCreateIssueModal() {
    window.uiController.openModal('createIssueModal');
}

function closeCreateIssueModal() {
    window.uiController.closeModal('createIssueModal');
}

function updateFormAction(projectId) {
    const form = document.getElementById('createIssueForm');
    if (form && projectId) {
        form.action = `/project/${projectId}/issue/add`;
        console.log(`Form action updated to: ${form.action}`);
    }
}

function showNotification(message, type = 'info') {
    if (window.uiController) {
        window.uiController.showNotification(message, type);
    } else {
        alert(message); // Fallback
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.uiController = new UIController();
    
    // Initialize Lucide icons if available
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
        console.log('✅ Lucide icons initialized');
    }
    
    console.log('✅ Core UI initialized - Forms, modals, dropdowns are now functional');
});