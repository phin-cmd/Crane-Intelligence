/**
 * NON-FLICKERING CACHE BUSTER
 * This cache buster does NOT cause any flickering or auto-refresh
 */

console.log('🔧 Non-flickering cache buster loaded');

// Store version without causing any refreshes
const currentVersion = Date.now().toString();
const storedVersion = localStorage.getItem('cacheVersion');

if (storedVersion && storedVersion !== currentVersion) {
    console.log('🔄 Version update detected - stored for reference only (no refresh)');
    localStorage.setItem('cacheVersion', currentVersion);
} else if (!storedVersion) {
    localStorage.setItem('cacheVersion', currentVersion);
}

// Manual refresh function (only when explicitly called by user)
window.manualRefresh = function() {
    console.log('Manual refresh requested by user');
    window.location.reload(true);
};

// Disable any automatic refresh mechanisms
window.addEventListener('beforeunload', function() {
    console.log('Page unloading - no auto-refresh');
});

// Override any problematic refresh functions
window.autoRefresh = function() {
    console.log('🚫 autoRefresh blocked to prevent flickering');
};

window.periodicRefresh = function() {
    console.log('🚫 periodicRefresh blocked to prevent flickering');
};

console.log('✅ Non-flickering cache buster initialized');
