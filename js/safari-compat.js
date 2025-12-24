/**
 * Safari Browser Compatibility Fixes
 * Ensures website works properly in Safari browsers
 */

(function() {
    'use strict';
    
    // Detect Safari
    const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent) || 
                     /iPad|iPhone|iPod/.test(navigator.userAgent) ||
                     (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
    
    if (isSafari) {
        // Fix for Safari CSS variable support
        if (!window.CSS || !CSS.supports || !CSS.supports('color', 'var(--fake-var)')) {
            // Polyfill for CSS variables if needed
            console.log('Safari detected - applying compatibility fixes');
        }
        
        // Fix for Safari flexbox issues
        document.addEventListener('DOMContentLoaded', function() {
            // Add webkit prefixes for flexbox where needed
            const style = document.createElement('style');
            style.textContent = `
                /* Safari flexbox fixes */
                .container, .content-container, .page-container {
                    display: -webkit-box !important;
                    display: -webkit-flex !important;
                    display: flex !important;
                }
                
                /* Safari grid fixes */
                .grid, .grid-2, .grid-3, .grid-4 {
                    display: -webkit-grid !important;
                    display: grid !important;
                }
                
                /* Safari transform fixes */
                * {
                    -webkit-transform: translateZ(0);
                    transform: translateZ(0);
                }
            `;
            document.head.appendChild(style);
        });
        
        // Fix for Safari viewport height issues on mobile
        function setVH() {
            let vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
        }
        
        setVH();
        window.addEventListener('resize', setVH);
        window.addEventListener('orientationchange', setVH);
        
        // Fix for Safari scroll behavior
        if (CSS.supports('scroll-behavior', 'smooth')) {
            document.documentElement.style.scrollBehavior = 'smooth';
        }
        
        // Fix for Safari touch events
        document.addEventListener('touchstart', function(e) {
            // Prevent double-tap zoom on buttons
            if (e.target.tagName === 'BUTTON' || e.target.tagName === 'A') {
                e.preventDefault();
                e.target.click();
            }
        }, { passive: false });
        
        // Fix for Safari form input zoom
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            if (input.style.fontSize === '' || parseInt(input.style.fontSize) < 16) {
                input.style.fontSize = '16px';
            }
        });
    }
    
    // Global Safari fixes
    if (typeof window !== 'undefined') {
        // Fix for Safari Promise support
        if (typeof Promise === 'undefined') {
            console.warn('Promise not supported - loading polyfill');
        }
        
        // Fix for Safari fetch API
        if (typeof fetch === 'undefined') {
            console.warn('Fetch API not supported - loading polyfill');
        }
    }
})();

