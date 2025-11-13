/**
 * Live Data Framework for Crane Intelligence
 * Handles real-time data integration, WebSocket connections, and data processing
 */

class LiveDataFramework {
    constructor() {
        this.wsConnection = null;
        this.dataCache = new Map();
        this.subscribers = new Map();
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.isConnected = false;
        this.heartbeatInterval = null;
        
        // Configuration
        this.config = {
            wsUrl: 'wss://craneintelligence.tech/ws',
            apiBaseUrl: 'https://craneintelligence.tech/api/v1',
            refreshInterval: 5000,
            cacheTimeout: 30000,
            maxCacheSize: 1000
        };
        
        this.init();
    }

    /**
     * Initialize the live data framework
     */
    init() {
        this.setupEventListeners();
        this.startDataRefresh();
        this.initializeWebSocket();
    }

    /**
     * Setup event listeners for page visibility and connectivity
     */
    setupEventListeners() {
        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseDataRefresh();
            } else {
                this.resumeDataRefresh();
            }
        });

        // Handle online/offline events
        window.addEventListener('online', () => {
            this.handleConnectionRestored();
        });

        window.addEventListener('offline', () => {
            this.handleConnectionLost();
        });

        // Handle beforeunload to cleanup
        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });
    }

    /**
     * Initialize WebSocket connection
     */
    initializeWebSocket() {
        try {
            // Get authentication token
            const token = this.getAuthToken();
            // Add token to WebSocket URL if available
            const wsUrl = token ? `${this.config.wsUrl}?token=${token}` : this.config.wsUrl;
            this.wsConnection = new WebSocket(wsUrl);
            
            this.wsConnection.onopen = () => {
                console.log('WebSocket connected');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.startHeartbeat();
                this.notifySubscribers('connection', { status: 'connected' });
            };

            this.wsConnection.onmessage = (event) => {
                this.handleWebSocketMessage(event);
            };

            this.wsConnection.onclose = () => {
                console.log('WebSocket disconnected');
                this.isConnected = false;
                this.stopHeartbeat();
                this.notifySubscribers('connection', { status: 'disconnected' });
                this.attemptReconnect();
            };

            this.wsConnection.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.notifySubscribers('error', { message: 'WebSocket connection error' });
            };

        } catch (error) {
            console.error('Failed to initialize WebSocket:', error);
            this.fallbackToPolling();
        }
    }

    /**
     * Handle WebSocket messages
     */
    handleWebSocketMessage(event) {
        try {
            const data = JSON.parse(event.data);
            const { type, payload, timestamp } = data;

            // Cache the data
            this.cacheData(type, payload, timestamp);

            // Notify subscribers
            this.notifySubscribers(type, payload);

        } catch (error) {
            console.error('Error parsing WebSocket message:', error);
        }
    }

    /**
     * Start heartbeat to keep connection alive
     */
    startHeartbeat() {
        this.heartbeatInterval = setInterval(() => {
            if (this.wsConnection && this.wsConnection.readyState === WebSocket.OPEN) {
                this.wsConnection.send(JSON.stringify({ type: 'ping' }));
            }
        }, 30000); // Send ping every 30 seconds
    }

    /**
     * Stop heartbeat
     */
    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }

    /**
     * Attempt to reconnect WebSocket
     */
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            
            setTimeout(() => {
                this.initializeWebSocket();
            }, this.reconnectDelay * this.reconnectAttempts);
        } else {
            console.log('Max reconnection attempts reached, falling back to polling');
            this.fallbackToPolling();
        }
    }

    /**
     * Fallback to HTTP polling when WebSocket fails
     */
    fallbackToPolling() {
        console.log('Falling back to HTTP polling');
        this.startDataRefresh();
    }

    /**
     * Start data refresh interval
     */
    startDataRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }

        this.refreshInterval = setInterval(() => {
            this.fetchAllData();
        }, this.config.refreshInterval);
    }

    /**
     * Pause data refresh
     */
    pauseDataRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    /**
     * Resume data refresh
     */
    resumeDataRefresh() {
        if (!this.refreshInterval) {
            this.startDataRefresh();
        }
    }

    /**
     * Fetch all data from API
     */
    async fetchAllData() {
        const endpoints = [
            'dashboard/data',
            'market/trends',
            'equipment/live',
            'analytics/overview',
            'notifications'
        ];

        for (const endpoint of endpoints) {
            try {
                await this.fetchData(endpoint);
            } catch (error) {
                console.error(`Error fetching ${endpoint}:`, error);
            }
        }
    }

    /**
     * Fetch data from specific endpoint
     */
    async fetchData(endpoint) {
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/${endpoint}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.cacheData(endpoint, data, Date.now());
            this.notifySubscribers(endpoint, data);

        } catch (error) {
            console.error(`Error fetching ${endpoint}:`, error);
            this.notifySubscribers('error', { 
                endpoint, 
                message: error.message 
            });
        }
    }

    /**
     * Cache data with timestamp
     */
    cacheData(key, data, timestamp) {
        this.dataCache.set(key, {
            data,
            timestamp,
            ttl: this.config.cacheTimeout
        });

        // Clean up old cache entries
        this.cleanupCache();
    }

    /**
     * Get cached data
     */
    getCachedData(key) {
        const cached = this.dataCache.get(key);
        if (cached && Date.now() - cached.timestamp < cached.ttl) {
            return cached.data;
        }
        return null;
    }

    /**
     * Clean up expired cache entries
     */
    cleanupCache() {
        const now = Date.now();
        for (const [key, value] of this.dataCache.entries()) {
            if (now - value.timestamp > value.ttl) {
                this.dataCache.delete(key);
            }
        }

        // Limit cache size
        if (this.dataCache.size > this.config.maxCacheSize) {
            const entries = Array.from(this.dataCache.entries());
            entries.sort((a, b) => a[1].timestamp - b[1].timestamp);
            
            const toDelete = entries.slice(0, entries.length - this.config.maxCacheSize);
            toDelete.forEach(([key]) => this.dataCache.delete(key));
        }
    }

    /**
     * Subscribe to data updates
     */
    subscribe(dataType, callback) {
        if (!this.subscribers.has(dataType)) {
            this.subscribers.set(dataType, new Set());
        }
        this.subscribers.get(dataType).add(callback);

        // Return unsubscribe function
        return () => {
            const subscribers = this.subscribers.get(dataType);
            if (subscribers) {
                subscribers.delete(callback);
                if (subscribers.size === 0) {
                    this.subscribers.delete(dataType);
                }
            }
        };
    }

    /**
     * Notify subscribers of data updates
     */
    notifySubscribers(dataType, data) {
        const subscribers = this.subscribers.get(dataType);
        if (subscribers) {
            subscribers.forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error('Error in subscriber callback:', error);
                }
            });
        }
    }

    /**
     * Get authentication token
     */
    getAuthToken() {
        return localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
    }

    /**
     * Handle connection restored
     */
    handleConnectionRestored() {
        console.log('Connection restored');
        this.reconnectAttempts = 0;
        this.initializeWebSocket();
        this.startDataRefresh();
    }

    /**
     * Handle connection lost
     */
    handleConnectionLost() {
        console.log('Connection lost');
        this.pauseDataRefresh();
        this.notifySubscribers('connection', { status: 'offline' });
    }

    /**
     * Send data via WebSocket
     */
    sendData(type, payload) {
        if (this.wsConnection && this.wsConnection.readyState === WebSocket.OPEN) {
            this.wsConnection.send(JSON.stringify({
                type,
                payload,
                timestamp: Date.now()
            }));
        } else {
            console.warn('WebSocket not connected, cannot send data');
        }
    }

    /**
     * Get real-time data for specific type
     */
    async getRealTimeData(dataType) {
        // Try to get from cache first
        const cached = this.getCachedData(dataType);
        if (cached) {
            return cached;
        }

        // Fetch fresh data
        await this.fetchData(dataType);
        return this.getCachedData(dataType);
    }

    /**
     * Create live ticker data
     */
    createLiveTickerData() {
        const tickerData = [];
        const dataTypes = [
            'total_cranes',
            'avg_value',
            'market_cap',
            'active_users',
            'api_calls',
            'response_time',
            'uptime',
            'data_points'
        ];

        dataTypes.forEach(type => {
            const cached = this.getCachedData(type);
            if (cached) {
                tickerData.push({
                    type,
                    value: cached.value,
                    change: cached.change,
                    positive: cached.positive
                });
            }
        });

        return tickerData;
    }

    /**
     * Generate mock data for development
     */
    generateMockData(dataType) {
        const mockData = {
            'dashboard/data': {
                total_users: Math.floor(Math.random() * 1000) + 1000,
                active_users: Math.floor(Math.random() * 500) + 500,
                total_revenue: Math.floor(Math.random() * 100000) + 50000,
                monthly_revenue: Math.floor(Math.random() * 20000) + 10000,
                system_health: 'excellent',
                uptime: '99.9%',
                response_time: `${Math.floor(Math.random() * 100) + 50}ms`
            },
            'market/trends': {
                labels: Array.from({ length: 24 }, (_, i) => {
                    const date = new Date();
                    date.setHours(date.getHours() - 23 + i);
                    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
                }),
                datasets: [{
                    label: 'Crane Values',
                    data: Array.from({ length: 24 }, () => Math.floor(Math.random() * 1000000) + 1000000)
                }]
            },
            'equipment/live': Array.from({ length: 20 }, (_, i) => ({
                id: `CRN-${String(i + 1).padStart(4, '0')}`,
                type: ['Mobile Crane', 'Tower Crane', 'Crawler Crane'][Math.floor(Math.random() * 3)],
                model: ['GMK5250L', 'LTM1120', 'AC500-2'][Math.floor(Math.random() * 3)],
                location: ['North America', 'Europe', 'Asia'][Math.floor(Math.random() * 3)],
                value: Math.floor(Math.random() * 5000000) + 500000,
                status: ['Active', 'Maintenance', 'Idle'][Math.floor(Math.random() * 3)],
                lastUpdate: new Date().toLocaleString()
            }))
        };

        return mockData[dataType] || {};
    }

    /**
     * Cleanup resources
     */
    cleanup() {
        this.pauseDataRefresh();
        this.stopHeartbeat();
        
        if (this.wsConnection) {
            this.wsConnection.close();
            this.wsConnection = null;
        }

        this.dataCache.clear();
        this.subscribers.clear();
    }

    /**
     * Get connection status
     */
    getConnectionStatus() {
        return {
            isConnected: this.isConnected,
            wsReady: this.wsConnection ? this.wsConnection.readyState === WebSocket.OPEN : false,
            cacheSize: this.dataCache.size,
            subscribers: Array.from(this.subscribers.keys())
        };
    }
}

// Export for use in other modules
window.LiveDataFramework = LiveDataFramework;

// Auto-initialize if not already done
if (!window.liveDataFramework) {
    window.liveDataFramework = new LiveDataFramework();
}
