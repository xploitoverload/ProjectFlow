/**
 * ProjectFlow UI Style Engine
 * Controls live switching between Bento Glass OLED, Minimalism, Neo-Brutalism, Neumorphism, and Flat.
 */

class UIStyleEngine {
    constructor() {
        this.styles = [
            { id: 'bento-glass', name: 'Bento Glass OLED', badge: 'Flagship' },
            { id: 'minimalism', name: 'Minimalism', badge: 'Clean' },
            { id: 'neo-brutalism', name: 'Neo-Brutalism', badge: 'Bold' },
            { id: 'neumorphism', name: 'Neumorphism', badge: 'Soft UI' },
            { id: 'flat', name: 'Flat Design', badge: '2D' }
        ];
        this.currentStyle = this.loadStyle();
        this.applyStyle(this.currentStyle);
        this.setupEventListeners();
    }

    loadStyle() {
        return localStorage.getItem('projectflow_ui_style') || 'bento-glass';
    }

    saveStyle(style) {
        localStorage.setItem('projectflow_ui_style', style);
    }

    applyStyle(style) {
        const valid = this.styles.find(s => s.id === style);
        const activeId = valid ? valid.id : 'bento-glass';
        document.body.setAttribute('data-ui-style', activeId);
        this.currentStyle = activeId;
        this.saveStyle(activeId);
        this.updateUI();
        console.log(`UI Style applied: ${activeId}`);
    }

    updateUI() {
        // Update label on switcher button
        const labelEl = document.getElementById('currentStyleLabel');
        const active = this.styles.find(s => s.id === this.currentStyle);
        if (labelEl && active) {
            labelEl.textContent = active.name;
        }

        // Update active class on options
        document.querySelectorAll('.style-option-item').forEach(el => {
            if (el.dataset.style === this.currentStyle) {
                el.classList.add('active');
            } else {
                el.classList.remove('active');
            }
        });
    }

    setupEventListeners() {
        // Toggle menu
        document.addEventListener('click', (e) => {
            const btn = e.target.closest('#styleSwitcherBtn');
            const menu = document.getElementById('styleSwitcherMenu');
            if (btn && menu) {
                e.stopPropagation();
                menu.classList.toggle('show');
            } else if (menu && !e.target.closest('#styleSwitcherMenu')) {
                menu.classList.remove('show');
            }
        });

        // Delegate style option click
        document.addEventListener('click', (e) => {
            const item = e.target.closest('.style-option-item');
            if (item && item.dataset.style) {
                e.preventDefault();
                this.applyStyle(item.dataset.style);
                document.getElementById('styleSwitcherMenu')?.classList.remove('show');
            }
        });
    }
}

// Global helper
window.setUIStyle = function(style) {
    if (window.uiStyleEngine) {
        window.uiStyleEngine.applyStyle(style);
        document.getElementById('styleSwitcherMenu')?.classList.remove('show');
    }
};

// Initialize immediately and on DOMContentLoaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.uiStyleEngine = new UIStyleEngine();
    });
} else {
    window.uiStyleEngine = new UIStyleEngine();
}
