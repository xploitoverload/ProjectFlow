/**
 * Jira Features Loader
 * Loads and initializes all Jira feature modules
 */

(function() {
    'use strict';

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeFeatures);
    } else {
        initializeFeatures();
    }

    function initializeFeatures() {
        console.log('Initializing Jira Features...');

        // Initialize global instances
        try {
            // Global Navigation
            if (typeof GlobalNavigation !== 'undefined') {
                window.globalNav = new GlobalNavigation();
                console.log('✓ Global Navigation initialized');
            }

            // Issue Navigator
            if (typeof IssueNavigator !== 'undefined' && document.getElementById('issueNavigator')) {
                window.issueNavigator = new IssueNavigator();
                console.log('✓ Issue Navigator initialized');
            }

            // Project Tabs
            if (typeof ProjectTabs !== 'undefined' && document.getElementById('projectTabs')) {
                window.projectTabs = new ProjectTabs();
                console.log('✓ Project Tabs initialized');
            }

            // Collaboration Features
            if (typeof CollaborationFeatures !== 'undefined') {
                window.collaboration = new CollaborationFeatures();
                console.log('✓ Collaboration Features initialized');
            }

            // Service Desk
            if (typeof ServiceDesk !== 'undefined' && document.getElementById('serviceDesk')) {
                window.serviceDesk = new ServiceDesk();
                console.log('✓ Service Desk initialized');
            }

            // Reporting System
            if (typeof ReportingSystem !== 'undefined' && document.getElementById('reportingContainer')) {
                window.reportingSystem = new ReportingSystem();
                console.log('✓ Reporting System initialized');
            }

            // Forms Builder
            if (typeof FormsBuilder !== 'undefined' && document.getElementById('formsBuilder')) {
                window.formsBuilder = new FormsBuilder();
                console.log('✓ Forms Builder initialized');
            }

            // Advanced Fields System
            if (typeof AdvancedFieldsSystem !== 'undefined') {
                window.advancedFields = new AdvancedFieldsSystem();
                console.log('✓ Advanced Fields System initialized');
            }

            // Filter Management
            if (typeof FilterManagement !== 'undefined' && document.getElementById('filterManagement')) {
                window.filterManagement = new FilterManagement();
                console.log('✓ Filter Management initialized');
            }

            // Modals System
            if (typeof ModalsSystem !== 'undefined') {
                window.modalsSystem = new ModalsSystem();
                console.log('✓ Modals System initialized');
            }

            // AI Features
            if (typeof AtlassianIntelligence !== 'undefined') {
                window.atlassianAI = new AtlassianIntelligence();
                console.log('✓ Atlassian Intelligence initialized');
            }

            // Development Integration
            if (typeof DevelopmentIntegration !== 'undefined' && document.getElementById('devIntegration')) {
                window.devIntegration = new DevelopmentIntegration();
                console.log('✓ Development Integration initialized');
            }

            // Jira Ops
            if (typeof JiraOpsSystem !== 'undefined' && document.getElementById('jiraOps')) {
                window.jiraOps = new JiraOpsSystem();
                console.log('✓ Jira Ops System initialized');
            }

            // Home Dashboard
            if (typeof HomeDashboard !== 'undefined' && document.getElementById('homeDashboard')) {
                window.homeDashboard = new HomeDashboard();
                console.log('✓ Home Dashboard initialized');
            }

            // Settings System
            if (typeof SettingsSystem !== 'undefined' && document.getElementById('settingsSystem')) {
                window.settingsSystem = new SettingsSystem();
                console.log('✓ Settings System initialized');
            }

            // Initialize Lucide icons
            if (typeof lucide !== 'undefined' && lucide.createIcons) {
                lucide.createIcons();
                console.log('✓ Lucide icons initialized');
            }

            console.log('All Jira features loaded successfully!');

        } catch (error) {
            console.error('Error initializing features:', error);
        }
    }

    // Global helper functions
    window.showToast = function(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: ${type === 'success' ? '#36b37e' : type === 'error' ? '#ff5630' : '#0052cc'};
            color: white;
            padding: 12px 20px;
            border-radius: 6px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            z-index: 10000;
            animation: slideIn 0.3s ease-out;
        `;
        document.body.appendChild(toast);
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    };

    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);

})();
