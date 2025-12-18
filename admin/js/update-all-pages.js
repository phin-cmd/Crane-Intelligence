/**
 * This script helps ensure all admin pages use the common header, sidebar, and footer components
 * Run this in the browser console on each page to check if it's using the shared components
 */

function checkPageComponents() {
    const hasHeader = document.getElementById('admin-header-container') !== null;
    const hasSidebar = document.getElementById('admin-sidebar-container') !== null;
    const hasFooter = document.getElementById('admin-footer-container') !== null;
    const hasHeaderScript = Array.from(document.querySelectorAll('script[src]')).some(s => s.src.includes('admin-header.js'));
    
    return {
        hasHeader,
        hasSidebar,
        hasFooter,
        hasHeaderScript,
        allGood: hasHeader && hasSidebar && hasFooter && hasHeaderScript
    };
}

// Log the status
console.log('Page Component Check:', checkPageComponents());

