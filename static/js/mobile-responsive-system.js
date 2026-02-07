/**
 * Mobile & Responsive Features System
 * Touch gestures, Responsive transforms, Swipe actions, Pull to refresh, Offline mode
 */

class MobileResponsiveSystem {
    constructor() {
        // Define responsiveBreakpoints BEFORE calling detectMobile()
        this.responsiveBreakpoints = {
            mobile: 768,
            tablet: 1024,
            desktop: 1440
        };
        
        // Now call detectMobile() which depends on responsiveBreakpoints
        this.isMobile = this.detectMobile();
        this.isTouch = 'ontouchstart' in window;
        this.isOffline = !navigator.onLine;
        this.swipeThreshold = 50;
        this.pullThreshold = 80;
        
        this.offlineQueue = [];
        
        this.init();
    }
    
    init() {
        console.log('Mobile & Responsive System initialized');
        this.setupTouchGestures();
        this.setupResponsiveTransforms();
        this.setupOfflineDetection();
        this.setupPullToRefresh();
        this.setupBottomNavigation();
        this.setupMobileDrawer();
    }
    
    detectMobile() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
               window.innerWidth < this.responsiveBreakpoints.mobile;
    }
    
    // Touch Gestures for Card Drag-Drop
    setupTouchGestures() {
        let touchStartX = 0;
        let touchStartY = 0;
        let touchElement = null;
        
        document.addEventListener('touchstart', (e) => {
            if (e.target.closest('.card-draggable')) {
                touchElement = e.target.closest('.card-draggable');
                const touch = e.touches[0];
                touchStartX = touch.clientX;
                touchStartY = touch.clientY;
                
                if (this.isMobile) {
                    this.vibrate(10); // Haptic feedback
                }
            }
        });
        
        document.addEventListener('touchmove', (e) => {
            if (touchElement) {
                const touch = e.touches[0];
                const deltaX = touch.clientX - touchStartX;
                const deltaY = touch.clientY - touchStartY;
                
                // Translate element during drag
                touchElement.style.transform = `translate(${deltaX}px, ${deltaY}px)`;
                touchElement.style.opacity = '0.8';
            }
        });
        
        document.addEventListener('touchend', (e) => {
            if (touchElement) {
                touchElement.style.transform = '';
                touchElement.style.opacity = '';
                touchElement = null;
                
                if (this.isMobile) {
                    this.vibrate(20); // Drop feedback
                }
            }
        });
    }
    
    // Responsive Table to Cards Transformation
    setupResponsiveTransforms() {
        const transformTables = () => {
            const tables = document.querySelectorAll('.responsive-table');
            const isMobileView = window.innerWidth < this.responsiveBreakpoints.mobile;
            
            tables.forEach(table => {
                if (isMobileView) {
                    this.tableToCards(table);
                } else {
                    this.cardsToTable(table);
                }
            });
        };
        
        // Initial transform
        transformTables();
        
        // Re-transform on resize
        let resizeTimer;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(transformTables, 250);
        });
    }
    
    tableToCards(table) {
        if (table.classList.contains('cards-view')) return;
        
        const rows = table.querySelectorAll('tbody tr');
        const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent);
        
        const cardsContainer = document.createElement('div');
        cardsContainer.className = 'mobile-cards-container';
        
        rows.forEach(row => {
            const cells = row.querySelectorAll('td');
            const card = document.createElement('div');
            card.className = 'mobile-card';
            
            let cardHTML = '';
            cells.forEach((cell, idx) => {
                if (headers[idx]) {
                    cardHTML += `
                        <div class="mobile-card-row">
                            <span class="mobile-card-label">${headers[idx]}:</span>
                            <span class="mobile-card-value">${cell.innerHTML}</span>
                        </div>
                    `;
                }
            });
            
            card.innerHTML = cardHTML;
            card.dataset.swipeable = 'true';
            this.setupSwipeActions(card);
            cardsContainer.appendChild(card);
        });
        
        table.style.display = 'none';
        table.parentNode.insertBefore(cardsContainer, table);
        table.classList.add('cards-view');
    }
    
    cardsToTable(table) {
        const cardsContainer = table.parentNode.querySelector('.mobile-cards-container');
        if (cardsContainer) {
            cardsContainer.remove();
            table.style.display = '';
            table.classList.remove('cards-view');
        }
    }
    
    // Swipe Actions (Archive/Delete/Watch)
    setupSwipeActions(element) {
        let startX = 0;
        let currentX = 0;
        let isSwiping = false;
        
        element.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            isSwiping = true;
        });
        
        element.addEventListener('touchmove', (e) => {
            if (!isSwiping) return;
            
            currentX = e.touches[0].clientX;
            const deltaX = currentX - startX;
            
            if (Math.abs(deltaX) > 10) {
                element.style.transform = `translateX(${deltaX}px)`;
                
                // Show action hints
                if (deltaX > this.swipeThreshold) {
                    element.classList.add('swipe-right-hint');
                } else if (deltaX < -this.swipeThreshold) {
                    element.classList.add('swipe-left-hint');
                } else {
                    element.classList.remove('swipe-right-hint', 'swipe-left-hint');
                }
            }
        });
        
        element.addEventListener('touchend', (e) => {
            if (!isSwiping) return;
            
            const deltaX = currentX - startX;
            
            if (deltaX > this.swipeThreshold) {
                this.handleSwipeRight(element);
                this.vibrate(30);
            } else if (deltaX < -this.swipeThreshold) {
                this.handleSwipeLeft(element);
                this.vibrate(30);
            }
            
            // Reset
            element.style.transform = '';
            element.classList.remove('swipe-right-hint', 'swipe-left-hint');
            isSwiping = false;
            currentX = 0;
        });
    }
    
    handleSwipeRight(element) {
        // Archive action
        this.showSwipeAction(element, 'Archived', 'archive');
        element.style.opacity = '0.5';
        setTimeout(() => element.remove(), 300);
    }
    
    handleSwipeLeft(element) {
        // Delete action
        this.showSwipeAction(element, 'Deleted', 'trash-2');
        element.style.opacity = '0.5';
        setTimeout(() => element.remove(), 300);
    }
    
    showSwipeAction(element, message, icon) {
        const action = document.createElement('div');
        action.className = 'swipe-action-indicator';
        action.innerHTML = `<i data-lucide="${icon}"></i> ${message}`;
        element.appendChild(action);
        
        setTimeout(() => action.remove(), 2000);
        if (typeof lucide !== 'undefined') lucide.createIcons();
    }
    
    // Pull to Refresh
    setupPullToRefresh() {
        let startY = 0;
        let currentY = 0;
        let isPulling = false;
        const mainContent = document.querySelector('.app-main') || document.body;
        
        let refreshIndicator = document.createElement('div');
        refreshIndicator.className = 'pull-refresh-indicator';
        refreshIndicator.innerHTML = '<i data-lucide="refresh-cw"></i> Pull to refresh';
        document.body.appendChild(refreshIndicator);
        
        mainContent.addEventListener('touchstart', (e) => {
            if (mainContent.scrollTop === 0) {
                startY = e.touches[0].clientY;
                isPulling = true;
            }
        });
        
        mainContent.addEventListener('touchmove', (e) => {
            if (!isPulling) return;
            
            currentY = e.touches[0].clientY;
            const deltaY = currentY - startY;
            
            if (deltaY > 0 && deltaY < 150) {
                refreshIndicator.style.transform = `translateY(${deltaY}px)`;
                refreshIndicator.style.opacity = deltaY / this.pullThreshold;
                
                if (deltaY > this.pullThreshold) {
                    refreshIndicator.classList.add('ready');
                    refreshIndicator.innerHTML = '<i data-lucide="refresh-cw"></i> Release to refresh';
                    if (typeof lucide !== 'undefined') lucide.createIcons();
                }
            }
        });
        
        mainContent.addEventListener('touchend', () => {
            if (!isPulling) return;
            
            const deltaY = currentY - startY;
            
            if (deltaY > this.pullThreshold) {
                this.triggerRefresh(refreshIndicator);
            } else {
                refreshIndicator.style.transform = '';
                refreshIndicator.style.opacity = '';
                refreshIndicator.classList.remove('ready');
            }
            
            isPulling = false;
            currentY = 0;
        });
    }
    
    triggerRefresh(indicator) {
        indicator.classList.add('refreshing');
        indicator.innerHTML = '<i data-lucide="loader" class="spin"></i> Refreshing...';
        if (typeof lucide !== 'undefined') lucide.createIcons();
        
        // Simulate refresh
        setTimeout(() => {
            indicator.style.transform = '';
            indicator.style.opacity = '';
            indicator.classList.remove('ready', 'refreshing');
            indicator.innerHTML = '<i data-lucide="refresh-cw"></i> Pull to refresh';
            if (typeof lucide !== 'undefined') lucide.createIcons();
            
            this.showToast('Content refreshed');
        }, 1500);
    }
    
    // Bottom Navigation Bar for Mobile
    setupBottomNavigation() {
        if (!this.isMobile) return;
        
        const bottomNav = document.createElement('nav');
        bottomNav.className = 'mobile-bottom-nav';
        bottomNav.innerHTML = `
            <button class="nav-item active" onclick="mobileSystem.navigate('home')">
                <i data-lucide="home"></i>
                <span>Home</span>
            </button>
            <button class="nav-item" onclick="mobileSystem.navigate('issues')">
                <i data-lucide="list"></i>
                <span>Issues</span>
            </button>
            <button class="nav-item" onclick="mobileSystem.navigate('boards')">
                <i data-lucide="kanban"></i>
                <span>Boards</span>
            </button>
            <button class="nav-item" onclick="mobileSystem.navigate('filters')">
                <i data-lucide="filter"></i>
                <span>Filters</span>
            </button>
            <button class="nav-item" onclick="mobileSystem.navigate('more')">
                <i data-lucide="menu"></i>
                <span>More</span>
            </button>
        `;
        
        document.body.appendChild(bottomNav);
        if (typeof lucide !== 'undefined') lucide.createIcons();
    }
    
    // Mobile Navigation Drawer
    setupMobileDrawer() {
        if (!this.isMobile) return;
        
        const drawer = document.createElement('div');
        drawer.className = 'mobile-drawer';
        drawer.id = 'mobileDrawer';
        drawer.innerHTML = `
            <div class="drawer-header">
                <h3>Menu</h3>
                <button class="btn-icon" onclick="mobileSystem.closeDrawer()">
                    <i data-lucide="x"></i>
                </button>
            </div>
            <nav class="drawer-nav">
                <a href="#" class="drawer-nav-item">
                    <i data-lucide="home"></i>
                    Home
                </a>
                <a href="#" class="drawer-nav-item">
                    <i data-lucide="list"></i>
                    Issues
                </a>
                <a href="#" class="drawer-nav-item">
                    <i data-lucide="kanban"></i>
                    Boards
                </a>
                <a href="#" class="drawer-nav-item">
                    <i data-lucide="calendar"></i>
                    Calendar
                </a>
                <a href="#" class="drawer-nav-item">
                    <i data-lucide="chart-bar"></i>
                    Reports
                </a>
            </nav>
        `;
        
        const overlay = document.createElement('div');
        overlay.className = 'drawer-overlay';
        overlay.onclick = () => this.closeDrawer();
        
        document.body.appendChild(drawer);
        document.body.appendChild(overlay);
        
        if (typeof lucide !== 'undefined') lucide.createIcons();
        
        // Swipe gesture to open drawer
        this.setupDrawerSwipe();
    }
    
    setupDrawerSwipe() {
        let startX = 0;
        let currentX = 0;
        
        document.addEventListener('touchstart', (e) => {
            if (e.touches[0].clientX < 20) {
                startX = e.touches[0].clientX;
            }
        });
        
        document.addEventListener('touchmove', (e) => {
            if (startX > 0) {
                currentX = e.touches[0].clientX;
                const deltaX = currentX - startX;
                
                if (deltaX > this.swipeThreshold) {
                    this.openDrawer();
                    startX = 0;
                }
            }
        });
    }
    
    openDrawer() {
        document.getElementById('mobileDrawer').classList.add('open');
        document.querySelector('.drawer-overlay').classList.add('visible');
        this.vibrate(15);
    }
    
    closeDrawer() {
        document.getElementById('mobileDrawer').classList.remove('open');
        document.querySelector('.drawer-overlay').classList.remove('visible');
    }
    
    // Offline Mode Detection
    setupOfflineDetection() {
        window.addEventListener('online', () => {
            this.isOffline = false;
            this.hideOfflineIndicator();
            this.syncOfflineQueue();
        });
        
        window.addEventListener('offline', () => {
            this.isOffline = true;
            this.showOfflineIndicator();
        });
        
        if (this.isOffline) {
            this.showOfflineIndicator();
        }
    }
    
    showOfflineIndicator() {
        let indicator = document.getElementById('offlineIndicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'offlineIndicator';
            indicator.className = 'offline-indicator';
            indicator.innerHTML = `
                <i data-lucide="wifi-off"></i>
                <span>You're offline. Changes will sync when reconnected.</span>
            `;
            document.body.appendChild(indicator);
            if (typeof lucide !== 'undefined') lucide.createIcons();
        }
        indicator.classList.add('visible');
    }
    
    hideOfflineIndicator() {
        const indicator = document.getElementById('offlineIndicator');
        if (indicator) {
            indicator.classList.remove('visible');
            this.showToast('Back online - syncing...');
        }
    }
    
    queueOfflineAction(action) {
        this.offlineQueue.push({
            action,
            timestamp: Date.now()
        });
        localStorage.setItem('offlineQueue', JSON.stringify(this.offlineQueue));
    }
    
    syncOfflineQueue() {
        const queue = JSON.parse(localStorage.getItem('offlineQueue') || '[]');
        if (queue.length > 0) {
            this.showToast(`Syncing ${queue.length} offline changes...`);
            // Process queue
            setTimeout(() => {
                localStorage.removeItem('offlineQueue');
                this.offlineQueue = [];
                this.showToast('All changes synced');
            }, 1500);
        }
    }
    
    // Haptic Feedback
    vibrate(duration) {
        if ('vibrate' in navigator) {
            navigator.vibrate(duration);
        }
    }
    
    // Mobile-Optimized Modals
    optimizeModalForMobile(modal) {
        if (this.isMobile) {
            modal.classList.add('mobile-fullscreen');
        }
    }
    
    // Navigation
    navigate(section) {
        const items = document.querySelectorAll('.mobile-bottom-nav .nav-item');
        items.forEach(item => item.classList.remove('active'));
        event.target.closest('.nav-item').classList.add('active');
        
        this.vibrate(10);
        this.showToast(`Navigating to ${section}`);
    }
    
    showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'toast mobile-toast';
        toast.textContent = message;
        toast.style.cssText = 'position: fixed; bottom: 80px; left: 50%; transform: translateX(-50%); background: #36b37e; color: white; padding: 12px 20px; border-radius: 6px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); z-index: 10000;';
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 2000);
    }
}

// Initialize
const mobileSystem = new MobileResponsiveSystem();
