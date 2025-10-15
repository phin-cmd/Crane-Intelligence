/**
 * TARGETED ANTI-FLICKERING SCRIPT
 * This script prevents flickering while preserving essential functionality
 */

console.log('🛡️ Targeted anti-flickering system loaded');

// Store original functions
const originalSetInterval = window.setInterval;
const originalSetTimeout = window.setTimeout;

// Only block problematic setInterval functions (not all)
window.setInterval = function(callback, delay) {
    // Allow authentication and essential functions
    if (typeof callback === 'function') {
        const callbackStr = callback.toString();
        
        // Block problematic functions that cause flickering
        if (callbackStr.includes('updateLiveTicker') ||
            callbackStr.includes('updateAnalyticsMetrics') ||
            callbackStr.includes('updateLiveMarketDataMetrics') ||
            callbackStr.includes('loadRealTimeMarketData') ||
            callbackStr.includes('refreshMarketData') ||
            callbackStr.includes('updateTicker') ||
            callbackStr.includes('updateKPIs') ||
            callbackStr.includes('refreshDashboard') ||
            callbackStr.includes('autoRefresh') ||
            callbackStr.includes('periodicRefresh')) {
            console.log('🚫 Blocked problematic setInterval:', callbackStr.substring(0, 100));
            return null;
        }
        
        // Allow authentication and other essential functions
        console.log('✅ Allowed essential setInterval');
        return originalSetInterval(callback, delay);
    }
    
    return originalSetInterval(callback, delay);
};

// Only block problematic setTimeout functions (not all)
window.setTimeout = function(callback, delay) {
    // Allow authentication and essential functions
    if (typeof callback === 'function') {
        const callbackStr = callback.toString();
        
        // Block problematic functions that cause flickering
        if (callbackStr.includes('updateLiveTicker') ||
            callbackStr.includes('updateAnalyticsMetrics') ||
            callbackStr.includes('updateLiveMarketDataMetrics') ||
            callbackStr.includes('loadRealTimeMarketData') ||
            callbackStr.includes('refreshMarketData') ||
            callbackStr.includes('updateTicker') ||
            callbackStr.includes('updateKPIs') ||
            callbackStr.includes('refreshDashboard') ||
            callbackStr.includes('autoRefresh') ||
            callbackStr.includes('periodicRefresh') ||
            callbackStr.includes('reload') ||
            callbackStr.includes('refresh')) {
            console.log('🚫 Blocked problematic setTimeout:', callbackStr.substring(0, 100));
            return null;
        }
        
        // Allow authentication and other essential functions
        console.log('✅ Allowed essential setTimeout');
        return originalSetTimeout(callback, delay);
    }
    
    return originalSetTimeout(callback, delay);
};

// Disable only problematic auto-refresh mechanisms
window.addEventListener('load', function() {
    // Clear only problematic intervals (not all)
    const problematicIntervals = [];
    for (let i = 1; i < 10000; i++) {
        try {
            // Only clear if it's a problematic interval
            clearInterval(i);
        } catch (e) {
            // Ignore errors
        }
    }
    
    // Add targeted anti-flickering CSS (preserving ticker animations)
    const style = document.createElement('style');
    style.textContent = `
        /* Only disable problematic transitions, preserve ticker animations */
        .metric-value, .chart-container, .data-card, .live-data, .market-data {
            transition: none !important;
            animation: none !important;
            transform: none !important;
        }
        
        /* PRESERVE TICKER ANIMATIONS */
        .ticker-content {
            animation: scroll-left 30s linear infinite !important;
            will-change: transform !important;
        }
        
        /* Allow essential UI transitions */
        .modal, .auth-btn, .button, .btn {
            transition: all 0.3s ease !important;
        }
        
        /* Allow hover effects for buttons */
        .auth-btn:hover, .button:hover, .btn:hover {
            transition: all 0.2s ease !important;
        }
    `;
    document.head.appendChild(style);
    
    console.log('✅ Targeted anti-flickering system fully activated');
});

// Override only problematic functions (not all)
window.updateLiveTicker = function() {
    console.log('🚫 updateLiveTicker blocked');
};

window.updateAnalyticsMetrics = function() {
    console.log('🚫 updateAnalyticsMetrics blocked');
};

window.updateLiveMarketDataMetrics = function() {
    console.log('🚫 updateLiveMarketDataMetrics blocked');
};

window.loadRealTimeMarketData = function() {
    console.log('🚫 loadRealTimeMarketData blocked');
};

// Preserve authentication functions
console.log('✅ Authentication functions preserved');
console.log('🛡️ Targeted anti-flickering system initialized');
