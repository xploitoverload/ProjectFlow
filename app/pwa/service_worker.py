"""Service Worker management for PWA."""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class CacheStrategy:
    """Cache strategy configuration."""
    name: str
    strategy_type: str  # 'cache-first', 'network-first', 'stale-while-revalidate'
    max_age: int = 3600  # seconds
    max_entries: int = 50
    patterns: List[str] = None
    
    def __post_init__(self):
        if self.patterns is None:
            self.patterns = []


@dataclass
class PushNotification:
    """Push notification configuration."""
    id: str
    title: str
    body: str
    icon: str
    badge: str
    tag: str = None
    require_interaction: bool = False
    data: Dict = None
    actions: List[Dict] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}
        if self.actions is None:
            self.actions = []


class ServiceWorkerManager:
    """Manages service worker functionality for PWA."""
    
    def __init__(self):
        """Initialize service worker manager."""
        self.cache_strategies: Dict[str, CacheStrategy] = {}
        self.supported_endpoints: List[str] = []
        self.sw_version = "1.0.0"
        self.sw_enabled = True
        self._setup_default_strategies()
    
    def _setup_default_strategies(self):
        """Setup default cache strategies."""
        # API endpoints - network first
        self.register_cache_strategy(
            CacheStrategy(
                name='api-cache',
                strategy_type='network-first',
                max_age=1800,
                patterns=['/api/*']
            )
        )
        
        # Static assets - cache first
        self.register_cache_strategy(
            CacheStrategy(
                name='static-cache',
                strategy_type='cache-first',
                max_age=86400,
                patterns=['/static/*', '*.js', '*.css']
            )
        )
        
        # Images - stale while revalidate
        self.register_cache_strategy(
            CacheStrategy(
                name='image-cache',
                strategy_type='stale-while-revalidate',
                max_age=604800,
                patterns=['*.png', '*.jpg', '*.jpeg', '*.gif', '*.svg']
            )
        )
    
    def register_cache_strategy(self, strategy: CacheStrategy) -> None:
        """
        Register a new cache strategy.
        
        Args:
            strategy: CacheStrategy instance
        """
        self.cache_strategies[strategy.name] = strategy
        logger.info(f"Registered cache strategy: {strategy.name}")
    
    def get_service_worker_code(self) -> str:
        """
        Generate service worker JavaScript code.
        
        Returns:
            Service worker code as string
        """
        strategies = []
        for name, strategy in self.cache_strategies.items():
            strategies.append({
                'name': name,
                'type': strategy.strategy_type,
                'patterns': strategy.patterns,
                'maxAge': strategy.max_age,
                'maxEntries': strategy.max_entries
            })
        
        sw_code = f"""
// Service Worker v{self.sw_version}
// Generated: {datetime.now().isoformat()}

const CACHE_NAME = 'pwa-cache-v{self.sw_version}';
const STRATEGIES = {json.dumps(strategies)};

// Install event
self.addEventListener('install', (event) => {{
    console.log('[SW] Installing service worker');
    event.waitUntil(self.skipWaiting());
}});

// Activate event
self.addEventListener('activate', (event) => {{
    console.log('[SW] Activating service worker');
    event.waitUntil(
        caches.keys().then((cacheNames) => {{
            return Promise.all(
                cacheNames.map((cacheName) => {{
                    if (cacheName !== CACHE_NAME) {{
                        console.log('[SW] Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }}
                }})
            );
        }}).then(() => self.clients.claim())
    );
}});

// Fetch event
self.addEventListener('fetch', (event) => {{
    const url = new URL(event.request.url);
    
    // Skip non-GET requests
    if (event.request.method !== 'GET') {{
        return;
    }}
    
    // Skip third-party requests
    if (url.origin !== location.origin) {{
        return;
    }}
    
    // Apply matching strategy
    const strategy = STRATEGIES.find((s) =>
        s.patterns.some((pattern) => matchPattern(url.pathname, pattern))
    );
    
    if (strategy) {{
        if (strategy.type === 'cache-first') {{
            event.respondWith(cacheFirst(event.request));
        }} else if (strategy.type === 'network-first') {{
            event.respondWith(networkFirst(event.request));
        }} else if (strategy.type === 'stale-while-revalidate') {{
            event.respondWith(staleWhileRevalidate(event.request));
        }}
    }} else {{
        event.respondWith(fetch(event.request));
    }}
}});

// Message event
self.addEventListener('message', (event) => {{
    console.log('[SW] Received message:', event.data);
    
    if (event.data.type === 'SKIP_WAITING') {{
        self.skipWaiting();
    }} else if (event.data.type === 'CLEAR_CACHE') {{
        caches.delete(CACHE_NAME).then(() => {{
            console.log('[SW] Cache cleared');
        }});
    }}
}});

// Push event
self.addEventListener('push', (event) => {{
    const data = event.data?.json() || {{}};
    const options = {{
        body: data.body,
        icon: data.icon,
        badge: data.badge,
        tag: data.tag,
        requireInteraction: data.require_interaction,
        data: data.data || {{}},
        actions: data.actions || []
    }};
    
    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
}});

// Notification click
self.addEventListener('notificationclick', (event) => {{
    event.notification.close();
    
    const urlToOpen = event.notification.data.url || '/';
    
    event.waitUntil(
        clients.matchAll({{type: 'window', includeUncontrolled: true}}).then((windowClients) => {{
            for (let i = 0; i < windowClients.length; i++) {{
                if (windowClients[i].url === urlToOpen) {{
                    return windowClients[i].focus();
                }}
            }}
            return clients.openWindow(urlToOpen);
        }})
    );
}});

// Periodic background sync
self.addEventListener('periodicsync', (event) => {{
    if (event.tag === 'sync-data') {{
        event.waitUntil(syncData());
    }}
}});

// Cache first strategy
async function cacheFirst(request) {{
    const cache = await caches.open(CACHE_NAME);
    const cached = await cache.match(request);
    
    if (cached) {{
        return cached;
    }}
    
    try {{
        const response = await fetch(request);
        if (response.ok) {{
            cache.put(request, response.clone());
        }}
        return response;
    }} catch (error) {{
        console.error('[SW] Fetch error:', error);
        return new Response('Offline', {{status: 503}});
    }}
}}

// Network first strategy
async function networkFirst(request) {{
    try {{
        const response = await fetch(request);
        if (response.ok) {{
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, response.clone());
        }}
        return response;
    }} catch (error) {{
        const cached = await caches.match(request);
        if (cached) {{
            return cached;
        }}
        return new Response('Offline', {{status: 503}});
    }}
}}

// Stale while revalidate
async function staleWhileRevalidate(request) {{
    const cache = await caches.open(CACHE_NAME);
    const cached = await cache.match(request);
    
    const fetchPromise = fetch(request).then((response) => {{
        if (response.ok) {{
            cache.put(request, response.clone());
        }}
        return response;
    }});
    
    return cached || fetchPromise;
}}

// Sync data with server
async function syncData() {{
    try {{
        const response = await fetch('/api/v1/pwa/sync', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{timestamp: new Date().toISOString()}})
        }});
        console.log('[SW] Data synced:', response.status);
        return response;
    }} catch (error) {{
        console.error('[SW] Sync error:', error);
        throw error;
    }}
}}

// Pattern matching helper
function matchPattern(url, pattern) {{
    if (pattern === '/*') return true;
    if (pattern.endsWith('*')) {{
        return url.startsWith(pattern.slice(0, -1));
    }}
    return url === pattern;
}}

console.log('[SW] Service worker loaded');
"""
        return sw_code
    
    def get_install_prompt_script(self) -> str:
        """
        Generate install prompt JavaScript.
        
        Returns:
            JavaScript code for install prompts
        """
        return """
// Install prompt handling
let deferredPrompt = null;
let installPromptShown = false;

window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    
    // Show install button if not shown before
    if (!installPromptShown && localStorage.getItem('install-dismissed') !== 'true') {
        const installBtn = document.getElementById('install-btn');
        if (installBtn) {
            installBtn.style.display = 'block';
        }
    }
});

// Handle install button click
function installApp() {
    if (!deferredPrompt) return;
    
    deferredPrompt.prompt();
    deferredPrompt.userChoice.then((choice) => {
        if (choice.outcome === 'accepted') {
            console.log('[PWA] App installed');
            localStorage.setItem('app-installed', 'true');
        } else {
            console.log('[PWA] Install dismissed');
            localStorage.setItem('install-dismissed', 'true');
        }
        deferredPrompt = null;
    });
}

// App installed detection
window.addEventListener('appinstalled', () => {
    console.log('[PWA] App installed');
    localStorage.setItem('app-installed', 'true');
});

// Online/offline detection
window.addEventListener('online', () => {
    console.log('[PWA] App is online');
    notifyOnlineStatus(true);
});

window.addEventListener('offline', () => {
    console.log('[PWA] App is offline');
    notifyOnlineStatus(false);
});

// Check initial online status
function checkOnlineStatus() {
    const isOnline = navigator.onLine;
    notifyOnlineStatus(isOnline);
    return isOnline;
}

function notifyOnlineStatus(isOnline) {
    const statusEl = document.getElementById('online-status');
    if (statusEl) {
        statusEl.textContent = isOnline ? 'Online' : 'Offline';
        statusEl.className = isOnline ? 'online' : 'offline';
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkOnlineStatus();
    registerServiceWorker();
});

async function registerServiceWorker() {
    if (!('serviceWorker' in navigator)) {
        console.log('[PWA] Service workers not supported');
        return;
    }
    
    try {
        const registration = await navigator.serviceWorker.register('/static/js/service-worker.js');
        console.log('[PWA] Service worker registered:', registration);
        
        // Check for updates periodically
        setInterval(() => {
            registration.update();
        }, 60000);
        
        // Listen for controller change
        let refreshing = false;
        navigator.serviceWorker.addEventListener('controllerchange', () => {
            if (!refreshing) {
                console.log('[PWA] Service worker updated, reloading');
                window.location.reload();
                refreshing = true;
            }
        });
    } catch (error) {
        console.error('[PWA] Service worker registration failed:', error);
    }
}
"""
    
    def enable_service_worker(self) -> None:
        """Enable service worker."""
        self.sw_enabled = True
        logger.info("Service worker enabled")
    
    def disable_service_worker(self) -> None:
        """Disable service worker."""
        self.sw_enabled = False
        logger.info("Service worker disabled")
    
    def update_service_worker_version(self, version: str) -> None:
        """
        Update service worker version.
        
        Args:
            version: New version string
        """
        self.sw_version = version
        logger.info(f"Service worker version updated to {version}")
    
    def get_stats(self) -> Dict:
        """
        Get service worker statistics.
        
        Returns:
            Dictionary with stats
        """
        return {
            'version': self.sw_version,
            'enabled': self.sw_enabled,
            'cache_strategies': len(self.cache_strategies),
            'strategies': [
                {
                    'name': s.name,
                    'type': s.strategy_type,
                    'patterns': s.patterns
                }
                for s in self.cache_strategies.values()
            ]
        }
