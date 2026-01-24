/**
 * Sidebar Resize Module
 * Allows users to resize the sidebar by dragging a handle
 */

class SidebarResize {
    constructor() {
        this.sidebar = null;
        this.handle = null;
        this.isDragging = false;
        this.startX = 0;
        this.startWidth = 0;
        this.minWidth = 200;
        this.maxWidth = 400;
        this.defaultWidth = 260;
        this.storageKey = 'sidebar-width';
        
        this.init();
    }

    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    setup() {
        this.sidebar = document.getElementById('sidebar') || document.querySelector('.app-sidebar');
        if (!this.sidebar) {
            console.warn('Sidebar not found for resize functionality');
            return;
        }

        // Create resize handle
        this.createHandle();

        // Restore saved width
        this.restoreWidth();

        // Add event listeners
        this.handle.addEventListener('mousedown', (e) => this.onMouseDown(e));
        document.addEventListener('mousemove', (e) => this.onMouseMove(e));
        document.addEventListener('mouseup', () => this.onMouseUp());

        // Touch support for mobile
        this.handle.addEventListener('touchstart', (e) => this.onTouchStart(e));
        document.addEventListener('touchmove', (e) => this.onTouchMove(e));
        document.addEventListener('touchend', () => this.onTouchEnd());

        console.log('Sidebar resize initialized');
    }

    createHandle() {
        // Remove existing handle if present
        const existing = this.sidebar.querySelector('.sidebar-resize-handle');
        if (existing) {
            existing.remove();
        }

        // Create handle element
        this.handle = document.createElement('div');
        this.handle.className = 'sidebar-resize-handle';
        this.handle.innerHTML = '<div class="sidebar-resize-handle-line"></div>';
        
        // Add to sidebar
        this.sidebar.appendChild(this.handle);
    }

    onMouseDown(e) {
        e.preventDefault();
        this.isDragging = true;
        this.startX = e.clientX;
        this.startWidth = this.sidebar.offsetWidth;
        
        // Add dragging class for visual feedback
        document.body.classList.add('sidebar-resizing');
        this.handle.classList.add('sidebar-resize-handle-active');
        
        // Disable text selection during drag
        document.body.style.userSelect = 'none';
        document.body.style.cursor = 'ew-resize';
    }

    onMouseMove(e) {
        if (!this.isDragging) return;
        
        const deltaX = e.clientX - this.startX;
        let newWidth = this.startWidth + deltaX;
        
        // Clamp width between min and max
        newWidth = Math.max(this.minWidth, Math.min(this.maxWidth, newWidth));
        
        // Apply new width
        this.setSidebarWidth(newWidth);
    }

    onMouseUp() {
        if (!this.isDragging) return;
        
        this.isDragging = false;
        
        // Remove dragging class
        document.body.classList.remove('sidebar-resizing');
        this.handle.classList.remove('sidebar-resize-handle-active');
        
        // Re-enable text selection
        document.body.style.userSelect = '';
        document.body.style.cursor = '';
        
        // Save width to localStorage
        this.saveWidth();
    }

    onTouchStart(e) {
        const touch = e.touches[0];
        this.isDragging = true;
        this.startX = touch.clientX;
        this.startWidth = this.sidebar.offsetWidth;
        
        document.body.classList.add('sidebar-resizing');
        this.handle.classList.add('sidebar-resize-handle-active');
    }

    onTouchMove(e) {
        if (!this.isDragging) return;
        
        e.preventDefault();
        const touch = e.touches[0];
        const deltaX = touch.clientX - this.startX;
        let newWidth = this.startWidth + deltaX;
        
        newWidth = Math.max(this.minWidth, Math.min(this.maxWidth, newWidth));
        this.setSidebarWidth(newWidth);
    }

    onTouchEnd() {
        if (!this.isDragging) return;
        
        this.isDragging = false;
        document.body.classList.remove('sidebar-resizing');
        this.handle.classList.remove('sidebar-resize-handle-active');
        this.saveWidth();
    }

    setSidebarWidth(width) {
        this.sidebar.style.width = `${width}px`;
        
        // Update main content margin
        const appMain = document.querySelector('.app-main');
        if (appMain) {
            appMain.style.marginLeft = `${width}px`;
        }
        
        // Also update CSS variable if used
        document.documentElement.style.setProperty('--sidebar-width', `${width}px`);
    }

    saveWidth() {
        const width = this.sidebar.offsetWidth;
        try {
            localStorage.setItem(this.storageKey, width.toString());
        } catch (e) {
            console.warn('Failed to save sidebar width:', e);
        }
    }

    restoreWidth() {
        try {
            const savedWidth = localStorage.getItem(this.storageKey);
            if (savedWidth) {
                const width = parseInt(savedWidth, 10);
                if (!isNaN(width) && width >= this.minWidth && width <= this.maxWidth) {
                    this.setSidebarWidth(width);
                    return;
                }
            }
        } catch (e) {
            console.warn('Failed to restore sidebar width:', e);
        }
        
        // Set default width if no saved width or error
        this.setSidebarWidth(this.defaultWidth);
    }

    reset() {
        // Reset to default width
        this.setSidebarWidth(this.defaultWidth);
        this.saveWidth();
    }
}

// Initialize sidebar resize
const sidebarResize = new SidebarResize();

// Expose globally for debugging/testing
window.sidebarResize = sidebarResize;
