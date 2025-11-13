/**
 * Cache Buster - Forces browser to load latest version
 * This file ensures users always get the freshest code
 */

(function() {
    'use strict';
    
    // Version from server (updated on each deployment)
    const CACHE_VERSION = Date.now();
    
    // Add version parameter to all dynamic script loads
    function bustCache() {
        // Get all script and link tags
        const scripts = document.querySelectorAll('script[src]');
        const links = document.querySelectorAll('link[rel="stylesheet"]');
        
        // Add version to scripts
        scripts.forEach(script => {
            const src = script.getAttribute('src');
            if (src && !src.includes('?v=') && !src.includes('&v=')) {
                const separator = src.includes('?') ? '&' : '?';
                script.src = src + separator + 'v=' + CACHE_VERSION;
            }
        });
        
        // Add version to stylesheets
        links.forEach(link => {
            const href = link.getAttribute('href');
            if (href && !href.includes('?v=') && !href.includes('&v=')) {
                const separator = href.includes('?') ? '&' : '?';
                link.href = href + separator + 'v=' + CACHE_VERSION;
            }
        });
    }
    
    // Force reload if old version detected
    function checkVersion() {
        const storedVersion = localStorage.getItem('crane_app_version');
        const currentVersion = CACHE_VERSION.toString();
        
        if (storedVersion && storedVersion !== currentVersion) {
            console.log('🔄 New version detected, forcing refresh...');
            localStorage.setItem('crane_app_version', currentVersion);
            // Force hard reload
            // window.// location.reload DISABLED to prevent flickering DISABLED to prevent flickering(true);
            return;
        }
        
        localStorage.setItem('crane_app_version', currentVersion);
    }
    
    // Clear old caches
    function clearOldCaches() {
        if ('caches' in window) {
            caches.keys().then(names => {
                names.forEach(name => {
                    if (!name.includes(CACHE_VERSION)) {
                        caches.delete(name);
                    }
                });
            });
        }
    }
    
    // Run on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            checkVersion();
            bustCache();
            clearOldCaches();
        });
    } else {
        checkVersion();
        bustCache();
        clearOldCaches();
    }
    
    console.log('🔧 Cache Buster loaded - Version:', CACHE_VERSION);
    
})();

