/**
 * Comprehensive API Client for Crane Intelligence Platform
 * Handles all backend API communications
 */

class CraneIntelligenceAPI {
    constructor() {
        this.baseUrl = '/api/v1';
        this.authToken = null;
        this.init();
    }

    init() {
        // Load auth token from localStorage
        this.authToken = localStorage.getItem('crane_auth_token') || 
                        localStorage.getItem('auth_token') || 
                        sessionStorage.getItem('auth_token');
    }

    /**
     * Set authentication token
     */
    setAuthToken(token) {
        this.authToken = token;
        localStorage.setItem('crane_auth_token', token);
        localStorage.setItem('auth_token', token);
    }

    /**
     * Clear authentication token
     */
    clearAuthToken() {
        this.authToken = null;
        localStorage.removeItem('crane_auth_token');
        localStorage.removeItem('auth_token');
        localStorage.removeItem('crane_user_data');
        sessionStorage.removeItem('auth_token');
    }

    /**
     * Get headers for API requests
     */
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (this.authToken) {
            headers['Authorization'] = `Bearer ${this.authToken}`;
        }
        
        return headers;
    }

    /**
     * Make API request
     */
    async request(endpoint, options = {}) {
        try {
            const url = `${this.baseUrl}${endpoint}`;
            const config = {
                ...options,
                headers: {
                    ...this.getHeaders(),
                    ...options.headers
                }
            };

            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || data.message || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error(`API request failed: ${endpoint}`, error);
            throw error;
        }
    }

    // ==================== AUTHENTICATION ====================

    async login(email, password) {
        const data = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        
        if (data.access_token) {
            this.setAuthToken(data.access_token);
        }
        
        return data;
    }

    async register(email, password, fullName, companyName = null) {
        const data = await this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify({
                email,
                password,
                full_name: fullName,
                company_name: companyName,
                username: email.split('@')[0]
            })
        });
        
        if (data.access_token) {
            this.setAuthToken(data.access_token);
        }
        
        return data;
    }

    async logout() {
        this.clearAuthToken();
        return { success: true };
    }

    // ==================== USER PROFILE ====================

    async getUserProfile() {
        return await this.request('/users/me');
    }

    async updateUserProfile(profileData) {
        return await this.request('/users/me', {
            method: 'PUT',
            body: JSON.stringify(profileData)
        });
    }

    // ==================== CRANE LISTINGS ====================

    async getCraneListings(filters = {}) {
        const params = new URLSearchParams();
        
        if (filters.limit) params.append('limit', filters.limit);
        if (filters.offset) params.append('offset', filters.offset);
        if (filters.manufacturer) params.append('manufacturer', filters.manufacturer);
        if (filters.min_price) params.append('min_price', filters.min_price);
        if (filters.max_price) params.append('max_price', filters.max_price);
        if (filters.condition) params.append('condition', filters.condition);
        
        const queryString = params.toString();
        const endpoint = queryString ? `/crane-listings?${queryString}` : '/crane-listings';
        
        return await this.request(endpoint);
    }

    async getCraneListing(listingId) {
        return await this.request(`/crane-listings/${listingId}`);
    }

    async createCraneListing(listingData) {
        return await this.request('/crane-listings', {
            method: 'POST',
            body: JSON.stringify(listingData)
        });
    }

    async updateCraneListing(listingId, listingData) {
        return await this.request(`/crane-listings/${listingId}`, {
            method: 'PUT',
            body: JSON.stringify(listingData)
        });
    }

    async deleteCraneListing(listingId) {
        return await this.request(`/crane-listings/${listingId}`, {
            method: 'DELETE'
        });
    }

    // ==================== VALUATIONS ====================

    async getValuations(limit = 50, offset = 0) {
        return await this.request(`/valuations?limit=${limit}&offset=${offset}`);
    }

    async createValuation(valuationData) {
        return await this.request('/valuations', {
            method: 'POST',
            body: JSON.stringify(valuationData)
        });
    }

    async getValuation(valuationId) {
        const valuations = await this.getValuations();
        return valuations.valuations.find(v => v.id === valuationId);
    }

    // ==================== MARKET DATA ====================

    async getMarketData(filters = {}) {
        const params = new URLSearchParams();
        
        if (filters.crane_type) params.append('crane_type', filters.crane_type);
        if (filters.make) params.append('make', filters.make);
        if (filters.region) params.append('region', filters.region);
        if (filters.limit) params.append('limit', filters.limit);
        
        const queryString = params.toString();
        const endpoint = queryString ? `/market-data?${queryString}` : '/market-data';
        
        return await this.request(endpoint);
    }

    async getMarketAnalysis() {
        return await this.request('/analytics/market-analysis');
    }

    // ==================== NOTIFICATIONS ====================

    async getNotifications(limit = 20, unreadOnly = false) {
        const params = new URLSearchParams({ limit });
        if (unreadOnly) params.append('unread_only', 'true');
        
        return await this.request(`/notifications?${params.toString()}`);
    }

    async markNotificationRead(notificationId) {
        return await this.request(`/notifications/${notificationId}/read`, {
            method: 'POST'
        });
    }

    async markAllNotificationsRead() {
        const notifications = await this.getNotifications();
        const unread = notifications.notifications.filter(n => !n.is_read);
        
        const promises = unread.map(n => this.markNotificationRead(n.id));
        return await Promise.all(promises);
    }

    // ==================== WATCHLIST ====================

    async getWatchlist() {
        return await this.request('/watchlist');
    }

    async addToWatchlist(craneListingId) {
        return await this.request('/watchlist', {
            method: 'POST',
            body: JSON.stringify({ crane_listing_id: craneListingId })
        });
    }

    async removeFromWatchlist(watchlistId) {
        return await this.request(`/watchlist/${watchlistId}`, {
            method: 'DELETE'
        });
    }

    // ==================== PRICE ALERTS ====================

    async getPriceAlerts() {
        return await this.request('/price-alerts');
    }

    async createPriceAlert(alertData) {
        return await this.request('/price-alerts', {
            method: 'POST',
            body: JSON.stringify(alertData)
        });
    }

    async deletePriceAlert(alertId) {
        return await this.request(`/price-alerts/${alertId}`, {
            method: 'DELETE'
        });
    }

    // ==================== ACTIVITY LOGS ====================

    async getActivityLogs(limit = 50) {
        return await this.request(`/activity-logs?limit=${limit}`);
    }

    // ==================== DASHBOARD ====================

    async getDashboardStats() {
        return await this.request('/dashboard/stats');
    }

    async getDashboardData() {
        try {
            const [stats, listings, valuations, notifications, watchlist] = await Promise.all([
                this.getDashboardStats(),
                this.getCraneListings({ limit: 10 }),
                this.getValuations(5, 0),
                this.getNotifications(5, true),
                this.getWatchlist()
            ]);

            return {
                success: true,
                stats: stats.stats,
                recent_listings: listings.listings,
                recent_valuations: valuations.valuations,
                unread_notifications: notifications.notifications,
                watchlist: watchlist.watchlist
            };
        } catch (error) {
            console.error('Error fetching dashboard data:', error);
            throw error;
        }
    }

    // ==================== CONSULTATIONS ====================

    async submitConsultation(consultationData) {
        return await this.request('/consultations', {
            method: 'POST',
            body: JSON.stringify(consultationData)
        });
    }

    // ==================== ADVANCED SEARCH ====================

    async searchCranes(searchParams) {
        const filters = {
            manufacturer: searchParams.manufacturer,
            min_price: searchParams.minPrice,
            max_price: searchParams.maxPrice,
            condition: searchParams.condition,
            limit: searchParams.limit || 50
        };
        
        return await this.getCraneListings(filters);
    }

    async searchMarketData(searchParams) {
        return await this.getMarketData({
            crane_type: searchParams.craneType,
            make: searchParams.make,
            region: searchParams.region,
            limit: searchParams.limit || 50
        });
    }

    // ==================== REPORTS ====================

    async generateReport(reportType, reportParams) {
        // Generate different types of reports
        switch (reportType) {
            case 'market_analysis':
                return await this.getMarketAnalysis();
            
            case 'valuation_history':
                return await this.getValuations(100, 0);
            
            case 'watchlist_summary':
                return await this.getWatchlist();
            
            case 'activity_report':
                return await this.getActivityLogs(100);
            
            default:
                throw new Error('Unknown report type');
        }
    }

    // ==================== EXPORT DATA ====================

    async exportData(dataType, format = 'json') {
        let data;
        
        switch (dataType) {
            case 'crane_listings':
                data = await this.getCraneListings({ limit: 1000 });
                break;
            
            case 'valuations':
                data = await this.getValuations(1000, 0);
                break;
            
            case 'market_data':
                data = await this.getMarketData({ limit: 1000 });
                break;
            
            case 'watchlist':
                data = await this.getWatchlist();
                break;
            
            default:
                throw new Error('Unknown data type');
        }

        if (format === 'csv') {
            return this.convertToCSV(data);
        }
        
        return data;
    }

    convertToCSV(data) {
        // Simple CSV conversion
        if (!data || !data.length) return '';
        
        const headers = Object.keys(data[0]);
        const rows = data.map(row => 
            headers.map(header => JSON.stringify(row[header] || '')).join(',')
        );
        
        return [headers.join(','), ...rows].join('\n');
    }

    // ==================== HEALTH CHECK ====================

    async healthCheck() {
        try {
            const response = await fetch(`${this.baseUrl}/health`);
            return await response.json();
        } catch (error) {
            return { status: 'unhealthy', error: error.message };
        }
    }

    // ==================== UTILITY METHODS ====================

    isAuthenticated() {
        return !!this.authToken;
    }

    formatPrice(price) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(price);
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        }).format(date);
    }

    formatDateTime(dateString) {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    }

    // ==================== MOCK DATA (for development) ====================

    getMockData(dataType) {
        const mockData = {
            dashboard: {
                stats: {
                    total_listings: 150,
                    user_valuations: 25,
                    watchlist_count: 12,
                    unread_notifications: 5,
                    average_market_price: 750000
                }
            },
            listings: [
                {
                    id: 1,
                    manufacturer: 'Liebherr',
                    model: 'LTM 1200-5.1',
                    year: 2018,
                    capacity: 200,
                    condition: 'excellent',
                    location: 'Houston, TX',
                    price: 850000,
                    mileage: 5000,
                    description: 'Excellent condition mobile crane'
                }
            ]
        };
        
        return mockData[dataType] || null;
    }
}

// Export for use in other modules
window.CraneIntelligenceAPI = CraneIntelligenceAPI;

// Create global instance
if (!window.craneAPI) {
    window.craneAPI = new CraneIntelligenceAPI();
}

// Export default instance
window.api = window.craneAPI;

console.log('Crane Intelligence API Client loaded successfully');

