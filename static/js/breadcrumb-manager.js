/**
 * Breadcrumb Manager
 * Enhances breadcrumbs with overflow handling, dropdown, copy path, and keyboard navigation
 */

class BreadcrumbManager {
    constructor() {
        this.breadcrumbs = [];
        this.container = null;
        this.isDropdownOpen = false;
        this.dropdownElement = null;
        this.maxVisibleItems = 4;
        
        this.init();
    }

    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    setup() {
        // Find all breadcrumb containers
        const containers = document.querySelectorAll('.header-breadcrumb, .breadcrumb');
        
        containers.forEach(container => {
            this.enhanceBreadcrumb(container);
        });

        console.log(`Enhanced ${containers.length} breadcrumb(s)`);
    }

    enhanceBreadcrumb(container) {
        // Parse existing breadcrumb items
        const items = this.parseBreadcrumbItems(container);
        
        if (items.length === 0) return;

        // Add copy path button
        this.addCopyButton(container, items);

        // Handle overflow if needed
        if (items.length > this.maxVisibleItems) {
            this.handleOverflow(container, items);
        }

        // Add keyboard navigation
        this.addKeyboardNavigation(container);

        // Add tooltips for truncated text
        this.addTooltips(container);
    }

    parseBreadcrumbItems(container) {
        const items = [];
        
        // Find all links and current items
        const links = container.querySelectorAll('a, .header-breadcrumb-link');
        const current = container.querySelector('.header-breadcrumb-current, .breadcrumb-current');
        
        links.forEach(link => {
            items.push({
                text: link.textContent.trim(),
                href: link.href || link.getAttribute('href'),
                element: link,
                isCurrent: false
            });
        });

        if (current) {
            items.push({
                text: current.textContent.trim(),
                href: null,
                element: current,
                isCurrent: true
            });
        }

        return items;
    }

    addCopyButton(container, items) {
        // Don't add if already exists
        if (container.querySelector('.breadcrumb-copy-btn')) return;

        // Build full path
        const path = items.map(item => item.text).join(' / ');

        // Create copy button
        const copyBtn = document.createElement('button');
        copyBtn.className = 'breadcrumb-copy-btn';
        copyBtn.title = 'Copy path to clipboard';
        copyBtn.innerHTML = '<i data-lucide="copy" style="width: 14px; height: 14px;"></i>';
        
        copyBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            try {
                await navigator.clipboard.writeText(path);
                
                // Show success feedback
                const icon = copyBtn.querySelector('i');
                const originalIcon = icon.getAttribute('data-lucide');
                icon.setAttribute('data-lucide', 'check');
                copyBtn.classList.add('breadcrumb-copy-success');
                
                if (typeof lucide !== 'undefined') {
                    lucide.createIcons();
                }
                
                setTimeout(() => {
                    icon.setAttribute('data-lucide', originalIcon);
                    copyBtn.classList.remove('breadcrumb-copy-success');
                    if (typeof lucide !== 'undefined') {
                        lucide.createIcons();
                    }
                }, 1500);
            } catch (err) {
                console.error('Failed to copy path:', err);
            }
        });

        // Add to container
        container.appendChild(copyBtn);
        
        // Initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }

    handleOverflow(container, items) {
        // Don't handle if already processed
        if (container.querySelector('.breadcrumb-overflow')) return;

        // Keep first item, last 2 items, collapse middle
        const visibleItems = [
            items[0], // First (usually home/project)
            ...items.slice(-2) // Last 2 items
        ];
        
        const hiddenItems = items.slice(1, -2);

        if (hiddenItems.length === 0) return;

        // Find the separator after first item
        const separators = container.querySelectorAll('.header-breadcrumb-separator, .breadcrumb-separator');
        const firstSeparator = separators[0];

        if (!firstSeparator) return;

        // Create overflow button
        const overflowBtn = document.createElement('button');
        overflowBtn.className = 'breadcrumb-overflow';
        overflowBtn.innerHTML = `
            <i data-lucide="more-horizontal" style="width: 14px; height: 14px;"></i>
        `;
        overflowBtn.title = `Show ${hiddenItems.length} more level(s)`;

        // Create dropdown for hidden items
        const dropdown = document.createElement('div');
        dropdown.className = 'breadcrumb-overflow-dropdown';
        dropdown.style.display = 'none';
        
        dropdown.innerHTML = `
            <div class="breadcrumb-overflow-list">
                ${hiddenItems.map(item => `
                    <a href="${item.href || '#'}" class="breadcrumb-overflow-item">
                        <i data-lucide="folder" style="width: 14px; height: 14px;"></i>
                        ${this.escapeHtml(item.text)}
                    </a>
                `).join('')}
            </div>
        `;

        // Toggle dropdown
        overflowBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.toggleOverflowDropdown(dropdown, overflowBtn);
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!dropdown.contains(e.target) && !overflowBtn.contains(e.target)) {
                this.closeOverflowDropdown(dropdown);
            }
        });

        // Insert overflow button after first separator
        firstSeparator.after(overflowBtn);
        overflowBtn.after(dropdown);

        // Hide middle items and their separators
        hiddenItems.forEach(item => {
            item.element.style.display = 'none';
        });

        // Hide extra separators (keep only needed ones)
        const allSeparators = Array.from(separators);
        allSeparators.slice(1, -2).forEach(sep => {
            sep.style.display = 'none';
        });

        // Initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }

    toggleOverflowDropdown(dropdown, button) {
        const isOpen = dropdown.style.display === 'block';
        
        if (isOpen) {
            this.closeOverflowDropdown(dropdown);
        } else {
            this.openOverflowDropdown(dropdown, button);
        }
    }

    openOverflowDropdown(dropdown, button) {
        dropdown.style.display = 'block';
        setTimeout(() => {
            dropdown.classList.add('breadcrumb-overflow-dropdown-open');
        }, 10);
        button.classList.add('breadcrumb-overflow-active');
        this.isDropdownOpen = true;
        this.dropdownElement = dropdown;
    }

    closeOverflowDropdown(dropdown) {
        if (!dropdown) return;
        
        dropdown.classList.remove('breadcrumb-overflow-dropdown-open');
        setTimeout(() => {
            dropdown.style.display = 'none';
        }, 200);
        
        const button = dropdown.previousElementSibling;
        if (button?.classList.contains('breadcrumb-overflow')) {
            button.classList.remove('breadcrumb-overflow-active');
        }
        
        this.isDropdownOpen = false;
        this.dropdownElement = null;
    }

    addKeyboardNavigation(container) {
        const links = container.querySelectorAll('a, .breadcrumb-overflow-item');
        
        links.forEach((link, index) => {
            link.addEventListener('keydown', (e) => {
                if (e.key === 'ArrowRight' && index < links.length - 1) {
                    e.preventDefault();
                    links[index + 1].focus();
                } else if (e.key === 'ArrowLeft' && index > 0) {
                    e.preventDefault();
                    links[index - 1].focus();
                } else if (e.key === 'Home') {
                    e.preventDefault();
                    links[0].focus();
                } else if (e.key === 'End') {
                    e.preventDefault();
                    links[links.length - 1].focus();
                }
            });
        });
    }

    addTooltips(container) {
        const items = container.querySelectorAll('a, .header-breadcrumb-current, .breadcrumb-current');
        
        items.forEach(item => {
            // Add tooltip if text is truncated
            if (item.scrollWidth > item.offsetWidth) {
                item.title = item.textContent.trim();
            }
        });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize breadcrumb manager
const breadcrumbManager = new BreadcrumbManager();

// Expose globally for debugging
window.breadcrumbManager = breadcrumbManager;
