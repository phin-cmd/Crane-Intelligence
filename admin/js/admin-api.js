/**
 * Crane Intelligence Admin API Client
 * Handles all API communication for the admin panel
 */

// Prevent duplicate declaration
if (typeof AdminAPI === 'undefined') {
    class AdminAPI {
    constructor() {
        // Use production URL or detect from window location
        const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
        this.baseUrl = isLocalhost 
            ? 'http://localhost:8004/api/v1'
            : 'https://craneintelligence.tech/api/v1';
        this.authToken = localStorage.getItem('admin_token') || localStorage.getItem('admin_access_token');
        this.refreshToken = localStorage.getItem('admin_refresh_token');
        this.isRefreshing = false;
        this.failedQueue = [];
        
        this.setupInterceptors();
    }

    setupInterceptors() {
        // Add request interceptor to include auth token
        this.interceptRequest = (config) => {
            if (this.authToken) {
                config.headers = {
                    ...config.headers,
                    'Authorization': `Bearer ${this.authToken}`,
                    'Content-Type': 'application/json'
                };
            }
            return config;
        };

        // Add response interceptor to handle token refresh
        this.interceptResponse = async (response) => {
            if (response.status === 401 && this.refreshToken) {
                return this.handleTokenRefresh(response);
            }
            return response;
        };
    }

    async handleTokenRefresh(originalResponse) {
        if (this.isRefreshing) {
            // If already refreshing, queue the request
            return new Promise((resolve, reject) => {
                this.failedQueue.push({ resolve, reject });
            });
        }

        this.isRefreshing = true;

        try {
            const response = await fetch(`${this.baseUrl}/admin/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    refresh_token: this.refreshToken
                })
            });

            if (response.ok) {
                const data = await response.json();
                this.authToken = data.access_token;
                this.refreshToken = data.refresh_token;
                
                localStorage.setItem('admin_token', this.authToken);
                localStorage.setItem('admin_refresh_token', this.refreshToken);

                // Process queued requests
                this.processQueue(null);
                
                // Retry original request
                return this.retryRequest(originalResponse);
            } else {
                throw new Error('Token refresh failed');
            }
        } catch (error) {
            this.processQueue(error);
            this.logout();
            throw error;
        } finally {
            this.isRefreshing = false;
        }
    }

    processQueue(error) {
        this.failedQueue.forEach(({ resolve, reject }) => {
            if (error) {
                reject(error);
            } else {
                resolve();
            }
        });
        
        this.failedQueue = [];
    }

    async retryRequest(originalResponse) {
        // Retry the original request with new token
        const originalRequest = originalResponse.config;
        originalRequest.headers.Authorization = `Bearer ${this.authToken}`;
        
        return fetch(originalRequest.url, {
            method: originalRequest.method,
            headers: originalRequest.headers,
            body: originalRequest.body
        });
    }

    async request(endpoint, options = {}) {
        console.log('AdminAPI.request called:', endpoint, options);
        const config = {
            method: 'GET',
            headers: {},
            ...options
        };

        // Apply request interceptor
        const interceptedConfig = this.interceptRequest(config);
        console.log('Intercepted config:', interceptedConfig);

        try {
            const fullUrl = `${this.baseUrl}${endpoint}`;
            console.log('Making request to:', fullUrl);
            const response = await fetch(fullUrl, interceptedConfig);
            console.log('Response status:', response.status);
            
            // Apply response interceptor
            const interceptedResponse = await this.interceptResponse(response);
            
            if (!interceptedResponse.ok) {
                throw new Error(`HTTP error! status: ${interceptedResponse.status}`);
            }
            
            const data = await interceptedResponse.json();
            console.log('Response data:', data);
            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Convenience methods that return Response-like objects for compatibility
    async get(endpoint, options = {}) {
        const data = await this.request(endpoint, { ...options, method: 'GET' });
        // Return a Response-like object
        return {
            ok: true,
            status: 200,
            json: async () => data,
            data: data
        };
    }

    async post(endpoint, body, options = {}) {
        const data = await this.request(endpoint, {
            ...options,
            method: 'POST',
            body: typeof body === 'object' ? JSON.stringify(body) : body
        });
        return {
            ok: true,
            status: 200,
            json: async () => data,
            data: data
        };
    }

    async patch(endpoint, body, options = {}) {
        const data = await this.request(endpoint, {
            ...options,
            method: 'PATCH',
            body: typeof body === 'object' ? JSON.stringify(body) : body
        });
        return {
            ok: true,
            status: 200,
            json: async () => data,
            data: data
        };
    }

    async put(endpoint, body, options = {}) {
        const data = await this.request(endpoint, {
            ...options,
            method: 'PUT',
            body: typeof body === 'object' ? JSON.stringify(body) : body
        });
        return {
            ok: true,
            status: 200,
            json: async () => data,
            data: data
        };
    }

    async delete(endpoint, options = {}) {
        const data = await this.request(endpoint, { ...options, method: 'DELETE' });
        return {
            ok: true,
            status: 200,
            json: async () => data,
            data: data
        };
    }

    // Authentication methods
    async login(email, password) {
        const response = await this.request('/admin/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        
        this.authToken = response.access_token;
        this.refreshToken = response.refresh_token;
        
        localStorage.setItem('admin_token', this.authToken);
        localStorage.setItem('admin_refresh_token', this.refreshToken);
        
        return response;
    }

    async logout() {
        try {
            await this.request('/admin/auth/logout', {
                method: 'POST'
            });
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            this.authToken = null;
            this.refreshToken = null;
        localStorage.removeItem('admin_token');
            localStorage.removeItem('admin_refresh_token');
            window.location.href = 'login.html';
        }
    }

    async getProfile() {
        return this.request('/admin/auth/me');
    }

    // Dashboard methods
    async getDashboardData() {
        return this.request('/admin/dashboard/data');
    }

    async getDashboardMetrics() {
        return this.request('/admin/dashboard/data');
    }

    async getRecentActivity(limit = 10) {
        return this.request(`/admin/dashboard/activity?limit=${limit}`);
    }

    // Analytics methods
    async getAnalyticsData() {
        return this.request('/admin/analytics');
    }

    // Content methods
    async getContent(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request(`/admin/content?${queryString}`);
    }

    async getContentById(id) {
        return this.request(`/admin/content/${id}`);
    }

    async createContent(data) {
        return this.request('/admin/content', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async updateContent(id, data) {
        return this.request(`/admin/content/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async deleteContent(id) {
        return this.request(`/admin/content/${id}`, {
            method: 'DELETE'
        });
    }

    async getContentStats() {
        return this.request('/admin/content/stats');
    }

    // Security methods
    async getSecurityData() {
        return this.request('/admin/security/overview');
    }

    async getSecurityEvents(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request(`/admin/security/events?${queryString}`);
    }

    async getSecurityEvent(eventId) {
        return this.request(`/admin/security/events/${eventId}`);
    }

    async resolveSecurityEvent(eventId) {
        return this.request(`/admin/security/events/${eventId}/resolve`, {
            method: 'POST'
        });
    }

    async getActiveSessions() {
        return this.request('/admin/security/sessions');
    }

    async terminateSession(sessionId) {
        return this.request(`/admin/security/sessions/${sessionId}/terminate`, {
            method: 'POST'
        });
    }

    async terminateAllSessions() {
        return this.request('/admin/security/sessions/terminate-all', {
            method: 'POST'
        });
    }

    async createRole(roleData) {
        return this.request('/admin/security/roles', {
            method: 'POST',
            body: JSON.stringify(roleData)
        });
    }

    async getRoles() {
        return this.request('/admin/security/roles');
    }

    async updateRole(roleId, roleData) {
        return this.request(`/admin/security/roles/${roleId}`, {
            method: 'PUT',
            body: JSON.stringify(roleData)
        });
    }

    async deleteRole(roleId) {
        return this.request(`/admin/security/roles/${roleId}`, {
            method: 'DELETE'
        });
    }

    // Data management methods
    async getDataOverview() {
        return this.request('/admin/data/overview');
    }

    // Settings methods
    async getSettings() {
        return this.request('/admin/settings');
    }

    async updateSettings(data) {
        return this.request('/admin/settings', {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async resetSettings() {
        return this.request('/admin/settings/reset', {
            method: 'POST'
        });
    }

    // User management methods
    async getUsers(params = {}) {
        console.log('AdminAPI.getUsers called with params:', params);
        const queryString = new URLSearchParams(params).toString();
        const url = `/admin/users?${queryString}`;
        console.log('Requesting URL:', url);
        return this.request(url);
    }

    async getUser(userId) {
        return this.request(`/admin/users/${userId}`);
    }

    async createUser(userData) {
        return this.request('/admin/users', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }

    async updateUser(userId, userData) {
        return this.request(`/admin/users/${userId}`, {
            method: 'PUT',
            body: JSON.stringify(userData)
        });
    }

    async deleteUser(userId) {
        return this.request(`/admin/users/${userId}`, {
            method: 'DELETE'
        });
    }

    async activateUser(userId) {
        return this.request(`/admin/users/${userId}/activate`, {
            method: 'PATCH'
        });
    }

    async deactivateUser(userId) {
        return this.request(`/admin/users/${userId}/deactivate`, {
            method: 'PATCH'
        });
    }

    async resetUserPassword(userId, newPassword) {
        return this.request(`/admin/users/${userId}/reset-password`, {
            method: 'PATCH',
            body: JSON.stringify({ new_password: newPassword })
        });
    }

    async getUserUsage(userId) {
        return this.request(`/admin/users/${userId}/usage`);
    }

    // Content management methods
    async getContentItems(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request(`/admin/content?${queryString}`);
    }

    async getContentItem(itemId) {
        return this.request(`/admin/content/${itemId}`);
    }

    async createContentItem(contentData) {
        return this.request('/admin/content', {
            method: 'POST',
            body: JSON.stringify(contentData)
        });
    }

    async updateContentItem(itemId, contentData) {
        return this.request(`/admin/content/${itemId}`, {
            method: 'PUT',
            body: JSON.stringify(contentData)
        });
    }

    async deleteContentItem(itemId) {
        return this.request(`/admin/content/${itemId}`, {
            method: 'DELETE'
        });
    }

    // Media management methods
    async uploadMediaFile(file, folderPath = '/', metadata = {}) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('folder_path', folderPath);
        formData.append('alt_text', metadata.alt_text || '');
        formData.append('caption', metadata.caption || '');
        formData.append('tags', JSON.stringify(metadata.tags || []));

        return this.request('/admin/media/upload', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.authToken}`
                // Don't set Content-Type, let browser set it for FormData
            },
            body: formData
        });
    }

    async getMediaFiles(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request(`/admin/media?${queryString}`);
    }

    async deleteMediaFile(fileId) {
        return this.request(`/admin/media/${fileId}`, {
            method: 'DELETE'
        });
    }

    // Analytics methods
    async getAnalyticsOverview() {
        return this.request('/admin/analytics/overview');
    }

    async getUserAnalytics(period = '30d') {
        return this.request(`/admin/analytics/users?period=${period}`);
    }

    async getFinancialAnalytics(period = '30d') {
        return this.request(`/admin/analytics/financial?period=${period}`);
    }

    async getTechnicalAnalytics(period = '24h') {
        return this.request(`/admin/analytics/technical?period=${period}`);
    }

    // System settings methods
    async getSystemSettings() {
        return this.request('/admin/settings');
    }

    async updateSystemSetting(settingId, settingData) {
        return this.request(`/admin/settings/${settingId}`, {
            method: 'PUT',
            body: JSON.stringify(settingData)
        });
    }

    // Logging methods
    async getSystemLogs(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request(`/admin/logs/system?${queryString}`);
    }

    async getAuditLogs(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request(`/admin/logs/audit?${queryString}`);
    }

    // Notification methods
    async getNotifications(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request(`/admin/notifications?${queryString}`);
    }

    async createNotification(notificationData) {
        return this.request('/admin/notifications', {
            method: 'POST',
            body: JSON.stringify(notificationData)
        });
    }

    async markNotificationRead(notificationId) {
        return this.request(`/admin/notifications/${notificationId}/read`, {
            method: 'PATCH'
        });
    }

    // Data management methods
    async getDataSources() {
        return this.request('/admin/data/sources');
    }

    async createDataSource(sourceData) {
        return this.request('/admin/data/sources', {
            method: 'POST',
            body: JSON.stringify(sourceData)
        });
    }

    async getDataQualityMetrics() {
        return this.request('/admin/data/quality');
    }

    // Background job methods
    async getBackgroundJobs(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request(`/admin/jobs?${queryString}`);
    }

    async cancelBackgroundJob(jobId) {
        return this.request(`/admin/jobs/${jobId}/cancel`, {
            method: 'POST'
        });
    }

    // Security methods
    async getSecurityDashboard() {
        return this.request('/admin/security/dashboard');
    }

    async getSecurityEvents(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request(`/admin/security/events?${queryString}`);
    }

    // Email template methods
    async getEmailTemplates(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request(`/admin/email/templates?${queryString}`);
    }

    async createEmailTemplate(templateData) {
        return this.request('/admin/email/templates', {
            method: 'POST',
            body: JSON.stringify(templateData)
        });
    }

    // Bulk operations methods
    async bulkUserOperation(operationData) {
        return this.request('/admin/bulk/users', {
            method: 'POST',
            body: JSON.stringify(operationData)
        });
    }

    async bulkContentOperation(operationData) {
        return this.request('/admin/bulk/content', {
            method: 'POST',
            body: JSON.stringify(operationData)
        });
    }

    // Data export/import methods
    async exportData(exportRequest) {
        return this.request('/admin/data/export', {
            method: 'POST',
            body: JSON.stringify(exportRequest)
        });
    }

    async importData(importRequest) {
        return this.request('/admin/data/import', {
            method: 'POST',
            body: JSON.stringify(importRequest)
        });
    }

    // Utility methods
    async healthCheck() {
        return this.request('/admin/health');
    }

    isAuthenticated() {
        return !!this.authToken;
    }

    getAuthToken() {
        return this.authToken;
    }

    setAuthToken(token) {
        this.authToken = token;
        localStorage.setItem('admin_token', token);
    }

    // Error handling
    handleError(error) {
        console.error('API Error:', error);
        
        if (error.status === 401) {
            this.logout();
        } else if (error.status === 403) {
            this.showError('Access denied. You do not have permission to perform this action.');
        } else if (error.status === 404) {
            this.showError('Resource not found.');
        } else if (error.status >= 500) {
            this.showError('Server error. Please try again later.');
        } else {
            this.showError('An unexpected error occurred. Please try again.');
        }
    }

    showError(message) {
        // Create error notification
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-notification';
        errorDiv.textContent = message;
        
        // Add to page
        document.body.appendChild(errorDiv);
        
        // Remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.parentNode.removeChild(errorDiv);
            }
        }, 5000);
    }
    }

    // Create global API instance
    window.adminAPI = new AdminAPI();
} else {
    // AdminAPI already exists, use existing instance
    if (!window.adminAPI) {
        window.adminAPI = new AdminAPI();
    }
}

// Export for use in other modules
// Browser environment - no module exports needed