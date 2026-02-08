// static/js/dark-mode.js
/**
 * Dark Mode Toggle Functionality
 */

class DarkModeManager {
    constructor() {
        this.theme = this.getTheme();
        this.init();
    }
    
    /**
     * Initialize dark mode manager
     */
    init() {
        // Apply saved theme
        this.applyTheme(this.theme);
        
        // Create toggle button
        this.createToggleButton();
        
        // Listen for system theme preference changes
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addListener((e) => {
                if (this.theme === 'auto') {
                    this.applyTheme('auto');
                }
            });
        }
    }
    
    /**
     * Get current theme from localStorage or system preference
     */
    getTheme() {
        const saved = localStorage.getItem('theme-preference');
        
        if (saved) {
            return saved;
        }
        
        // Check system preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        
        return 'light';
    }
    
    /**
     * Apply theme to document
     */
    applyTheme(theme) {
        const html = document.documentElement;
        
        let effectiveTheme = theme;
        
        if (theme === 'auto') {
            if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                effectiveTheme = 'dark';
            } else {
                effectiveTheme = 'light';
            }
        }
        
        // Set data-theme attribute
        if (effectiveTheme === 'dark') {
            html.setAttribute('data-theme', 'dark');
            document.body.classList.add('dark-mode');
            document.body.classList.remove('light-mode');
        } else {
            html.removeAttribute('data-theme');
            document.body.classList.remove('dark-mode');
            document.body.classList.add('light-mode');
        }
        
        // Update toggle button icon
        this.updateToggleButtonIcon(effectiveTheme);
        
        // Save preference
        this.theme = theme;
        localStorage.setItem('theme-preference', theme);
    }
    
    /**
     * Toggle between light and dark modes
     */
    toggle() {
        if (this.theme === 'dark') {
            this.applyTheme('light');
        } else if (this.theme === 'light') {
            this.applyTheme('auto');
        } else {
            this.applyTheme('dark');
        }
    }
    
    /**
     * Create toggle button
     */
    createToggleButton() {
        const button = document.createElement('button');
        button.className = 'theme-toggle';
        button.setAttribute('aria-label', 'Toggle dark mode');
        button.title = 'Toggle dark mode';
        button.innerHTML = this.getToggleIcon();
        
        button.addEventListener('click', () => this.toggle());
        
        document.body.appendChild(button);
    }
    
    /**
     * Get appropriate icon for current theme
     */
    getToggleIcon() {
        const currentTheme = this.getEffectiveTheme();
        return currentTheme === 'dark' ? '☀️' : '🌙';
    }
    
    /**
     * Update toggle button icon
     */
    updateToggleButtonIcon(effectiveTheme) {
        const button = document.querySelector('.theme-toggle');
        if (button) {
            button.innerHTML = effectiveTheme === 'dark' ? '☀️' : '🌙';
        }
    }
    
    /**
     * Get effective theme (accounting for auto)
     */
    getEffectiveTheme() {
        if (this.theme === 'auto') {
            return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
                ? 'dark'
                : 'light';
        }
        return this.theme;
    }
    
    /**
     * Set theme programmatically
     */
    setTheme(theme) {
        if (['light', 'dark', 'auto'].includes(theme)) {
            this.applyTheme(theme);
        }
    }
}

// Initialize dark mode manager when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.darkMode = new DarkModeManager();
    });
} else {
    window.darkMode = new DarkModeManager();
}

/**
 * Expose API for external use
 */
window.darkModeAPI = {
    toggle: () => window.darkMode.toggle(),
    setTheme: (theme) => window.darkMode.setTheme(theme),
    getTheme: () => window.darkMode.theme,
    getEffectiveTheme: () => window.darkMode.getEffectiveTheme()
};
