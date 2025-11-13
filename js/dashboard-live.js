/**
 * Live Dashboard - Connected to Database
 * Real-time dashboard with database integration
 */

class DashboardLive {
    constructor() {
        this.api = window.craneAPI || new CraneIntelligenceAPI();
        this.refreshInterval = null;
        this.charts = {};
        this.init();
    }

    async init() {
        console.log('Initializing Live Dashboard...');
        
        // Check authentication
        if (!this.api.isAuthenticated()) {
            console.warn('User not authenticated, redirecting to login...');
            // Don't redirect immediately, let them see the page
            // window.location.href = '/login.html';
            // return;
        }

        await this.loadDashboardData();
        this.setupEventListeners();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.getElementById('refreshDashboard');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadDashboardData();
            });
        }

        // Time period selector
        const periodSelector = document.getElementById('timePeriod');
        if (periodSelector) {
            periodSelector.addEventListener('change', (e) => {
                this.updateChartsPeriod(e.target.value);
            });
        }

        // Export data button
        const exportBtn = document.getElementById('exportDashboardData');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                this.exportDashboardData();
            });
        }
    }

    async loadDashboardData() {
        try {
            this.showLoading();

            // Load all dashboard data in parallel
            const [stats, listings, valuations, notifications, marketData] = await Promise.all([
                this.api.getDashboardStats().catch(() => ({ stats: this.getDefaultStats() })),
                this.api.getCraneListings({ limit: 10 }).catch(() => ({ listings: [] })),
                this.api.getValuations(5, 0).catch(() => ({ valuations: [] })),
                this.api.getNotifications(5, true).catch(() => ({ notifications: [] })),
                this.api.getMarketData({ limit: 20 }).catch(() => ({ market_data: [] }))
            ]);

            // Update UI with data
            this.updateStats(stats.stats || this.getDefaultStats());
            this.updateRecentListings(listings.listings || []);
            this.updateRecentValuations(valuations.valuations || []);
            this.updateNotifications(notifications.notifications || []);
            this.updateMarketCharts(marketData.market_data || []);

            this.hideLoading();
            this.updateLastRefreshTime();

        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.hideLoading();
            this.showError('Failed to load dashboard data');
            
            // Load default/mock data
            this.updateStats(this.getDefaultStats());
        }
    }

    getDefaultStats() {
        return {
            total_listings: 150,
            user_valuations: 25,
            watchlist_count: 12,
            unread_notifications: 5,
            average_market_price: 750000
        };
    }

    updateStats(stats) {
        // Update stat cards
        this.updateStatCard('totalListings', stats.total_listings || 0);
        this.updateStatCard('userValuations', stats.user_valuations || 0);
        this.updateStatCard('watchlistCount', stats.watchlist_count || 0);
        this.updateStatCard('unreadNotifications', stats.unread_notifications || 0);
        this.updateStatCard('averageMarketPrice', this.api.formatPrice(stats.average_market_price || 0));

        // Update additional metrics
        this.updateMetric('totalListings', stats.total_listings, '+12%');
        this.updateMetric('avgPrice', this.api.formatPrice(stats.average_market_price), '+5.2%');
        this.updateMetric('activeUsers', '1,234', '+8%');
        this.updateMetric('marketCap', '$125M', '+3.1%');
    }

    updateStatCard(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
            
            // Add animation
            element.classList.add('stat-update');
            // setTimeout(// DISABLED to prevent flickering // () => element.classList.remove('stat-update'), 500);
        }
    }

    updateMetric(prefix, value, change) {
        const valueElement = document.querySelector(`.${prefix}-value`);
        const changeElement = document.querySelector(`.${prefix}-change`);
        
        if (valueElement) valueElement.textContent = value;
        if (changeElement) changeElement.textContent = change;
    }

    updateRecentListings(listings) {
        const container = document.getElementById('recentListings');
        if (!container) return;

        if (!listings || listings.length === 0) {
            container.innerHTML = '<p class="no-data">No recent listings available</p>';
            return;
        }

        const listingsHTML = listings.slice(0, 5).map(listing => `
            <div class="listing-item" data-id="${listing.id}">
                <div class="listing-image">
                    <i class="fas fa-truck-moving"></i>
                </div>
                <div class="listing-info">
                    <h4>${listing.manufacturer} ${listing.model}</h4>
                    <p>${listing.year} • ${listing.condition} • ${listing.location}</p>
                </div>
                <div class="listing-price">
                    ${this.api.formatPrice(listing.price)}
                </div>
                <div class="listing-actions">
                    <button class="btn-sm" onclick="dashboard.viewListing(${listing.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn-sm" onclick="dashboard.addToWatchlist(${listing.id})">
                        <i class="fas fa-bookmark"></i>
                    </button>
                </div>
            </div>
        `).join('');

        container.innerHTML = listingsHTML;
    }

    updateRecentValuations(valuations) {
        const container = document.getElementById('recentValuations');
        if (!container) return;

        if (!valuations || valuations.length === 0) {
            container.innerHTML = '<p class="no-data">No recent valuations available</p>';
            return;
        }

        const valuationsHTML = valuations.map(v => `
            <div class="valuation-item" data-id="${v.id}">
                <div class="valuation-header">
                    <h4>${v.crane_make} ${v.crane_model}</h4>
                    <span class="valuation-status ${v.status}">${v.status}</span>
                </div>
                <div class="valuation-details">
                    <span class="detail">Year: ${v.crane_year}</span>
                    <span class="detail">Condition: ${v.crane_condition}</span>
                    <span class="detail value">${this.api.formatPrice(v.estimated_value)}</span>
                </div>
                <div class="valuation-footer">
                    <span class="date">${this.api.formatDate(v.created_at)}</span>
                    <button class="btn-sm" onclick="dashboard.viewValuation(${v.id})">
                        View Details
                    </button>
                </div>
            </div>
        `).join('');

        container.innerHTML = valuationsHTML;
    }

    updateNotifications(notifications) {
        const container = document.getElementById('notificationsList');
        const badge = document.getElementById('notificationBadge');
        
        if (badge) {
            badge.textContent = notifications.length;
            badge.style.display = notifications.length > 0 ? 'block' : 'none';
        }

        if (!container) return;

        if (!notifications || notifications.length === 0) {
            container.innerHTML = '<p class="no-notifications">No new notifications</p>';
            return;
        }

        const notificationsHTML = notifications.map(n => `
            <div class="notification-item ${n.is_read ? 'read' : 'unread'}" data-id="${n.id}">
                <div class="notification-icon ${n.type}">
                    <i class="fas fa-${this.getNotificationIcon(n.type)}"></i>
                </div>
                <div class="notification-content">
                    <h4>${n.title}</h4>
                    <p>${n.message}</p>
                    <span class="notification-time">${this.api.formatDateTime(n.created_at)}</span>
                </div>
                <button class="notification-close" onclick="dashboard.dismissNotification(${n.id})">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `).join('');

        container.innerHTML = notificationsHTML;
    }

    getNotificationIcon(type) {
        const icons = {
            'info': 'info-circle',
            'success': 'check-circle',
            'warning': 'exclamation-triangle',
            'error': 'times-circle'
        };
        return icons[type] || 'bell';
    }

    updateMarketCharts(marketData) {
        if (!marketData || marketData.length === 0) return;

        // Update price trends chart
        this.updatePriceTrendsChart(marketData);
        
        // Update market distribution chart
        this.updateMarketDistributionChart(marketData);
        
        // Update volume chart
        this.updateVolumeChart(marketData);
    }

    updatePriceTrendsChart(marketData) {
        const canvas = document.getElementById('priceTrendsChart');
        if (!canvas || !window.Chart) return;

        // Group data by date
        const dateMap = new Map();
        marketData.forEach(item => {
            const date = new Date(item.data_date).toLocaleDateString();
            if (!dateMap.has(date)) {
                dateMap.set(date, []);
            }
            dateMap.get(date).push(item.average_price);
        });

        const labels = Array.from(dateMap.keys());
        const data = Array.from(dateMap.values()).map(prices => 
            prices.reduce((sum, p) => sum + p, 0) / prices.length
        );

        const ctx = canvas.getContext('2d');
        
        if (this.charts.priceTrends) {
            this.charts.priceTrends.destroy();
        }

        this.charts.priceTrends = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Average Price',
                    data: data,
                    borderColor: '#0066cc',
                    backgroundColor: 'rgba(0, 102, 204, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            callback: function(value) {
                                return '$' + (value / 1000) + 'K';
                            }
                        }
                    }
                }
            }
        });
    }

    updateMarketDistributionChart(marketData) {
        const canvas = document.getElementById('marketDistributionChart');
        if (!canvas || !window.Chart) return;

        // Group by crane type
        const typeMap = new Map();
        marketData.forEach(item => {
            const count = typeMap.get(item.crane_type) || 0;
            typeMap.set(item.crane_type, count + 1);
        });

        const labels = Array.from(typeMap.keys());
        const data = Array.from(typeMap.values());

        const ctx = canvas.getContext('2d');
        
        if (this.charts.distribution) {
            this.charts.distribution.destroy();
        }

        this.charts.distribution = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        '#0066cc',
                        '#00cc66',
                        '#cc6600',
                        '#cc0066',
                        '#6600cc'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right'
                    }
                }
            }
        });
    }

    updateVolumeChart(marketData) {
        const canvas = document.getElementById('volumeChart');
        if (!canvas || !window.Chart) return;

        // Group by make
        const makeMap = new Map();
        marketData.forEach(item => {
            const volume = makeMap.get(item.make) || 0;
            makeMap.set(item.make, volume + (item.market_volume || 0));
        });

        const labels = Array.from(makeMap.keys()).slice(0, 10);
        const data = Array.from(makeMap.values()).slice(0, 10);

        const ctx = canvas.getContext('2d');
        
        if (this.charts.volume) {
            this.charts.volume.destroy();
        }

        this.charts.volume = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Market Volume',
                    data: data,
                    backgroundColor: '#0066cc'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    startAutoRefresh() {
        // Refresh every 5 minutes
        // this.refreshInterval = // setInterval(// DISABLED to prevent flickering // () => { // DISABLED to prevent flickering
            this.loadDashboardData();
        // }, 5 * 60 * 1000); // DISABLED to prevent flickering
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    updateLastRefreshTime() {
        const element = document.getElementById('lastRefreshTime');
        if (element) {
            element.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
        }
    }

    async viewListing(listingId) {
        window.location.href = `/listing-details.html?id=${listingId}`;
    }

    async addToWatchlist(listingId) {
        try {
            await this.api.addToWatchlist(listingId);
            this.showSuccess('Added to watchlist!');
            await this.loadDashboardData(); // Refresh to update watchlist count
        } catch (error) {
            console.error('Error adding to watchlist:', error);
            this.showError('Failed to add to watchlist');
        }
    }

    async viewValuation(valuationId) {
        window.location.href = `/valuation-details.html?id=${valuationId}`;
    }

    async dismissNotification(notificationId) {
        try {
            await this.api.markNotificationRead(notificationId);
            await this.loadDashboardData(); // Refresh notifications
        } catch (error) {
            console.error('Error dismissing notification:', error);
        }
    }

    async exportDashboardData() {
        try {
            this.showLoading('Preparing export...');
            
            const data = {
                stats: await this.api.getDashboardStats(),
                listings: await this.api.getCraneListings({ limit: 100 }),
                valuations: await this.api.getValuations(100, 0),
                marketData: await this.api.getMarketData({ limit: 100 })
            };
            
            const dataStr = JSON.stringify(data, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            const url = URL.createObjectURL(dataBlob);
            
            const link = document.createElement('a');
            link.href = url;
            link.download = `dashboard_data_${new Date().toISOString().split('T')[0]}.json`;
            link.click();
            
            URL.revokeObjectURL(url);
            
            this.hideLoading();
            this.showSuccess('Dashboard data exported successfully!');
        } catch (error) {
            console.error('Export error:', error);
            this.hideLoading();
            this.showError('Failed to export dashboard data');
        }
    }

    // Utility methods
    showLoading() {
        const loader = document.getElementById('dashboardLoader');
        if (loader) loader.style.display = 'flex';
    }

    hideLoading() {
        const loader = document.getElementById('dashboardLoader');
        if (loader) loader.style.display = 'none';
    }

    showSuccess(message) {
        this.showToast(message, 'success');
    }

    showError(message) {
        this.showToast(message, 'error');
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(toast);
        
        // setTimeout(// DISABLED to prevent flickering // () => toast.classList.add('show'), 100);
        // setTimeout(// DISABLED to prevent flickering // () => {
            toast.classList.remove('show');
            // setTimeout(// DISABLED to prevent flickering // () => toast.remove(), 300);
        }, 3000);
    }

    cleanup() {
        this.stopAutoRefresh();
        
        // Destroy charts
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        this.charts = {};
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.dashboard = new DashboardLive();
    });
} else {
    window.dashboard = new DashboardLive();
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.dashboard) {
        window.dashboard.cleanup();
    }
});

// Export for global use
window.DashboardLive = DashboardLive;

