/**
 * Theme Manager - Handles dark/light mode toggle with localStorage persistence
 */

class ThemeManager {
    constructor() {
        this.currentTheme = this.loadTheme();
        this.applyTheme(this.currentTheme);
        console.log(`ThemeManager initialized with theme: ${this.currentTheme}`);
    }
    
    loadTheme() {
        const savedTheme = localStorage.getItem('theme');
        return savedTheme || 'dark'; // Default to dark
    }
    
    saveTheme(theme) {
        localStorage.setItem('theme', theme);
        console.log(`Theme saved: ${theme}`);
    }
    
    applyTheme(theme) {
        // Simply set the data-theme attribute on body
        // CSS file handles all the color variables
        document.body.setAttribute('data-theme', theme);
        this.currentTheme = theme;
        this.saveTheme(theme);
        
        console.log(`Theme applied: ${theme}`);
        
        // Update toggle button icons
        this.updateToggleButtons();
    }
    
    toggleTheme() {
        const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        console.log(`Toggling theme from ${this.currentTheme} to ${newTheme}`);
        this.applyTheme(newTheme);
    }
    
    updateToggleButtons() {
        const buttons = document.querySelectorAll('.theme-toggle-btn');
        console.log(`Updating ${buttons.length} theme toggle buttons`);
        buttons.forEach(btn => {
            const icon = btn.querySelector('[data-lucide]');
            if (icon) {
                const iconName = this.currentTheme === 'dark' ? 'sun' : 'moon';
                icon.setAttribute('data-lucide', iconName);
                console.log(`Icon updated to: ${iconName}`);
                if (typeof lucide !== 'undefined') {
                    lucide.createIcons();
                }
            }
        });
    }
    
    getTheme() {
        return this.currentTheme;
    }
}

// Initialize theme manager when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.themeManager = new ThemeManager();
        console.log('ThemeManager loaded on DOMContentLoaded');
    });
} else {
    window.themeManager = new ThemeManager();
    console.log('ThemeManager loaded immediately');
}
