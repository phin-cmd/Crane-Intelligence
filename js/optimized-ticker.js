/**
 * OPTIMIZED TICKER ANIMATION SYSTEM
 * Consolidated JavaScript for consistent ticker behavior
 * Prevents conflicts and ensures smooth animations
 */

class TickerManager {
    constructor() {
        this.tickers = [];
        this.initialized = false;
        this.init();
    }

    init() {
        if (this.initialized) return;
        
        console.log('🎯 Initializing Optimized Ticker System...');
        
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeTickers());
        } else {
            this.initializeTickers();
        }
        
        this.initialized = true;
    }

    initializeTickers() {
        // Find all ticker elements
        const stockTickers = document.querySelectorAll('.stock-ticker .ticker-content');
        const marketTickers = document.querySelectorAll('.market-ticker .ticker-content');
        const boxedTickers = document.querySelectorAll('.live-market-data .ticker-content');
        
        // Initialize stock tickers
        stockTickers.forEach((ticker, index) => {
            this.setupTicker(ticker, 'scroll-left', `stock-ticker-${index}`);
        });
        
        // Initialize market tickers
        marketTickers.forEach((ticker, index) => {
            this.setupTicker(ticker, 'scroll', `market-ticker-${index}`);
        });
        
        // Initialize boxed tickers
        boxedTickers.forEach((ticker, index) => {
            this.setupTicker(ticker, 'scrollBoxed', `boxed-ticker-${index}`);
        });
        
        console.log(`✅ Initialized ${stockTickers.length + marketTickers.length + boxedTickers.length} tickers`);
    }

    setupTicker(element, animationName, id) {
        if (!element) return;
        
        // Force remove any conflicting styles
        element.style.animation = 'none';
        element.style.transform = 'none';
        element.offsetHeight; // Force reflow
        
        // Apply the correct animation
        element.style.animation = `${animationName} 30s linear infinite`;
        element.style.willChange = 'transform';
        
        // Store reference
        this.tickers.push({
            element: element,
            id: id,
            animationName: animationName
        });
        
        console.log(`✅ Ticker ${id} initialized with ${animationName} animation`);
    }

    // Method to restart a specific ticker
    restartTicker(selector) {
        const ticker = document.querySelector(selector);
        if (ticker) {
            this.setupTicker(ticker, 'scroll-left', 'restarted-ticker');
        }
    }

    // Method to restart all tickers
    restartAllTickers() {
        this.tickers.forEach(ticker => {
            this.setupTicker(ticker.element, ticker.animationName, ticker.id);
        });
    }

    // Method to pause all tickers
    pauseAllTickers() {
        this.tickers.forEach(ticker => {
            ticker.element.style.animationPlayState = 'paused';
        });
    }

    // Method to resume all tickers
    resumeAllTickers() {
        this.tickers.forEach(ticker => {
            ticker.element.style.animationPlayState = 'running';
        });
    }
}

// Initialize the ticker manager
const tickerManager = new TickerManager();

// Global functions for backward compatibility
window.startMarketTicker = function() {
    tickerManager.restartAllTickers();
};

window.restartTicker = function(selector) {
    tickerManager.restartTicker(selector);
};

// Auto-restart tickers if they get blocked
setInterval(() => {
    const tickers = document.querySelectorAll('.ticker-content');
    tickers.forEach(ticker => {
        const computedStyle = window.getComputedStyle(ticker);
        if (computedStyle.animation === 'none' || computedStyle.animation === '') {
            console.log('🔄 Restarting blocked ticker...');
            tickerManager.setupTicker(ticker, 'scroll-left', 'auto-restart');
        }
    });
}, 5000); // Check every 5 seconds

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        tickerManager.pauseAllTickers();
    } else {
        tickerManager.resumeAllTickers();
    }
});

console.log('✅ Optimized Ticker System loaded successfully');
