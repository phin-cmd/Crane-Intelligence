/**
 * Auto-Initialize Unified Authentication
 * This script automatically initializes authentication on all pages
 * Place this at the end of body tag on every page
 */

(function() {
    'use strict';
    
    // Wait for DOM to be fully loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAuth);
    } else {
        // DOM is already loaded
        initAuth();
    }
    
    async function initAuth() {
        // Check if unified auth is available
        if (!window.unifiedAuth) {
            console.warn('Unified auth not loaded, waiting...');
            // Wait a bit for the script to load
            await new Promise(resolve => setTimeout(resolve, 100));
            
            if (!window.unifiedAuth) {
                console.error('Unified auth failed to load');
                return;
            }
        }
        
        try {
            // Initialize authentication (will return current status if already initialized)
            const isLoggedIn = await window.unifiedAuth.initialize();
            console.log('Auth initialized:', isLoggedIn ? 'User logged in' : 'Guest');
            
            // Update header UI only if not already properly set
            // Don't override if user is already showing as logged in
            if (isLoggedIn !== undefined) {
                window.unifiedAuth.updateHeaderUI(isLoggedIn);
            }
            
        } catch (error) {
            console.error('Auth initialization error:', error);
        }
    }
    
    // Global logout function
    window.logout = async function() {
        if (window.unifiedAuth) {
            await window.unifiedAuth.logout();
        }
    };
    
    // Global toggle dropdown function
    window.toggleDropdown = function() {
        const dropdown = document.getElementById('userDropdown');
        if (dropdown) {
            dropdown.classList.toggle('show');
        }
    };
    
})();

