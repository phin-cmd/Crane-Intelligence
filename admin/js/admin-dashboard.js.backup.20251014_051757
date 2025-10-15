/**
 * Crane Intelligence Admin Dashboard JavaScript
 * Bloomberg Terminal Style Interface
 */

class AdminDashboard {
    constructor() {
        this.charts = {};
        this.refreshInterval = null;
        this.isRefreshing = false;
        this.api = new AdminAPI();
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDashboardData();
        this.initializeCharts();
        this.startAutoRefresh();
        this.loadRecentActivity();
        this.loadNotifications();
    }

    setupEventListeners() {
        // Refresh button
        document.getElementById('refresh-btn')?.addEventListener('click', () => {
            this.refreshDashboard();
        });

        // Export button
        document.getElementById('export-btn')?.addEventListener('click', () => {
            this.exportDashboard();
        });

        // Profile dropdown
        const profileDropdownBtn = document.getElementById('profile-dropdown-btn');
        const profileDropdown = document.getElementById('profile-dropdown');
        
        profileDropdownBtn?.addEventListener('click', (e) => {
            e.stopPropagation();
            profileDropdown.classList.toggle('show');
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!profileDropdown.contains(e.target) && !profileDropdownBtn.contains(e.target)) {
                profileDropdown.classList.remove('show');
            }
        });

        // Notification panel
        const notificationBtn = document.getElementById('notification-btn');
        const notificationPanel = document.getElementById('notification-panel');
        const notificationClose = document.getElementById('notification-close');
        
        notificationBtn?.addEventListener('click', () => {
            notificationPanel.classList.toggle('show');
        });

        notificationClose?.addEventListener('click', () => {
            notificationPanel.classList.remove('show');
        });

        // Chart period controls
        document.getElementById('user-activity-period')?.addEventListener('change', (e) => {
            this.updateUserActivityChart(e.target.value);
        });

        document.getElementById('revenue-period')?.addEventListener('change', (e) => {
            this.updateRevenueChart(e.target.value);
        });

        // Geographic chart controls
        document.querySelectorAll('.chart-btn[data-metric]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.chart-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.updateGeographicChart(e.target.dataset.metric);
            });
        });

        // View all activity
        document.getElementById('view-all-activity')?.addEventListener('click', () => {
            window.location.href = 'activity.html';
        });

        // Global search
        document.getElementById('global-search')?.addEventListener('input', (e) => {
                this.handleGlobalSearch(e.target.value);
            });
        }

    async loadDashboardData() {
        try {
            this.showLoadingState();
            
            const data = await this.api.getDashboardData();
            
            // Handle different response formats
            if (data.metrics) {
                this.updateDashboardMetrics(data.metrics);
            } else if (data.active_users !== undefined) {
                // Direct metrics in response
                this.updateDashboardMetrics(data);
            }
            
            if (data.charts) {
                this.updateCharts(data.charts);
            } else {
                this.updateCharts(data);
            }
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.showErrorState('Failed to load dashboard data. Using mock data.');
            // Load mock data as fallback
            this.loadMockData();
        } finally {
            this.hideLoadingState();
        }
    }

    loadMockData() {
        // Load mock data when API fails
        const mockMetrics = {
            active_users: 1247,
            total_revenue: 45230,
            system_health: 98,
            storage_used: 67
        };
        
        this.updateDashboardMetrics(mockMetrics);
        
        // Load mock chart data
        const mockCharts = {
            user_activity: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    data: [1200, 1350, 1100, 1400, 1600, 1800, 1500]
                }]
            },
            revenue_trends: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    data: [35000, 38000, 42000, 40000, 45000, 48000]
                }]
            },
            geographic_distribution: [
                { country: 'United States', users: 1250, percentage: 85 },
                { country: 'Canada', users: 320, percentage: 65 },
                { country: 'United Kingdom', users: 180, percentage: 45 },
                { country: 'Germany', users: 150, percentage: 35 },
                { country: 'Australia', users: 90, percentage: 25 }
            ]
        };
        
        this.updateCharts(mockCharts);
    }

    updateDashboardMetrics(metrics) {
        // Update metric cards
        this.updateMetricValue('active-users', metrics.active_users || metrics.total_users);
        this.updateMetricValue('total-revenue', `$${this.formatNumber(metrics.total_revenue || metrics.monthly_revenue)}`);
        this.updateMetricValue('system-health', `${metrics.system_health === 'excellent' ? 98 : metrics.system_health === 'good' ? 85 : 75}%`);
        this.updateMetricValue('storage-used', `${Math.floor(Math.random() * 30) + 60}%`); // Mock storage data
    }

    updateMetricValue(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
            element.classList.add('fade-in');
        }
    }

    initializeCharts() {
        try {
            this.initializeUserActivityChart();
            this.initializeRevenueChart();
            this.initializeGeographicChart();
            this.initializePerformanceChart();
        } catch (error) {
            console.error('Error initializing charts:', error);
            this.showErrorState('Failed to initialize charts');
        }
    }

    initializeUserActivityChart() {
        const ctx = document.getElementById('user-activity-chart');
        if (!ctx) {
            console.warn('User activity chart canvas not found');
                return;
            }

        try {
            this.charts.userActivity = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Active Users',
                        data: [],
                        borderColor: '#007BFF',
                        backgroundColor: 'rgba(0, 123, 255, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
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
                        x: {
                            grid: {
                                color: '#404040',
                                drawBorder: false
                            },
                            ticks: {
                                color: '#B0B0B0',
                                font: {
                                    family: 'Inter',
                                    size: 11
                                }
                            }
                        },
                        y: {
                            grid: {
                                color: '#404040',
                                drawBorder: false
                            },
                            ticks: {
                                color: '#B0B0B0',
                                font: {
                                    family: 'Inter',
                                    size: 11
                                }
                            }
                        }
                    },
                    elements: {
                        point: {
                            radius: 4,
                            hoverRadius: 6
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Error initializing user activity chart:', error);
        }
    }

    initializeRevenueChart() {
        const ctx = document.getElementById('revenue-chart');
        if (!ctx) {
            console.warn('Revenue chart canvas not found');
            return;
        }

        try {
            this.charts.revenue = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Revenue',
                    data: [],
                    backgroundColor: 'rgba(40, 167, 69, 0.8)',
                    borderColor: '#28A745',
                    borderWidth: 1
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
                    x: {
                        grid: {
                            color: '#404040',
                            drawBorder: false
                        },
                        ticks: {
                            color: '#B0B0B0',
                            font: {
                                family: 'Inter',
                                size: 11
                            }
                        }
                    },
                    y: {
                        grid: {
                            color: '#404040',
                            drawBorder: false
                        },
                        ticks: {
                            color: '#B0B0B0',
                            font: {
                                family: 'Inter',
                                size: 11
                            },
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
        } catch (error) {
            console.error('Error initializing revenue chart:', error);
        }
    }

    initializeGeographicChart() {
        // Geographic chart is implemented with CSS, no Chart.js needed
        this.updateGeographicChart('users');
    }

    initializePerformanceChart() {
        // Performance chart is implemented with CSS, no Chart.js needed
    }

    updateCharts(data) {
        if (data.user_activity) {
            this.updateUserActivityChartData(data.user_activity);
        }
        if (data.revenue_trends) {
            this.updateRevenueChartData(data.revenue_trends);
        }
        if (data.geographic_distribution) {
            this.updateGeographicChartData(data.geographic_distribution);
        }
    }

    updateUserActivityChartData(data) {
        if (this.charts.userActivity) {
            this.charts.userActivity.data.labels = data.labels;
            this.charts.userActivity.data.datasets[0].data = data.datasets[0].data;
            this.charts.userActivity.update();
        }
    }

    updateRevenueChartData(data) {
        if (this.charts.revenue) {
            this.charts.revenue.data.labels = data.labels;
            this.charts.revenue.data.datasets[0].data = data.datasets[0].data;
            this.charts.revenue.update();
        }
    }

    updateGeographicChartData(data) {
        const container = document.getElementById('geographic-chart');
        if (!container) return;

        container.innerHTML = data.map(item => `
            <div class="geo-item">
                <div class="geo-country">${item.country}</div>
                <div class="geo-bar">
                    <div class="geo-fill" style="width: ${item.percentage}%"></div>
                </div>
                <div class="geo-value">${item.users.toLocaleString()}</div>
            </div>
        `).join('');
    }

    async updateUserActivityChart(period) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/admin/analytics/users?period=${period}`, {
                headers: {
                    'Authorization': `Bearer ${this.authToken}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.updateUserActivityChartData(data.registration_trends);
            }
        } catch (error) {
            console.error('Error updating user activity chart:', error);
        }
    }

    async updateRevenueChart(period) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/admin/analytics/financial?period=${period}`, {
                headers: {
                    'Authorization': `Bearer ${this.authToken}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.updateRevenueChartData(data.revenue_trends);
            }
        } catch (error) {
            console.error('Error updating revenue chart:', error);
        }
    }

    updateGeographicChart(metric) {
        // Toggle between users and revenue data
        const items = document.querySelectorAll('.geo-item');
        items.forEach(item => {
            const valueElement = item.querySelector('.geo-value');
            const barElement = item.querySelector('.geo-fill');
            
            if (metric === 'revenue') {
                // Show revenue data (mock)
                const users = parseInt(valueElement.textContent.replace(/,/g, ''));
                const revenue = users * 50; // Mock calculation
                valueElement.textContent = `$${revenue.toLocaleString()}`;
                barElement.style.width = `${Math.min(100, (revenue / 1000) * 10)}%`;
            } else {
                // Show user data (original)
                const users = parseInt(valueElement.textContent.replace(/[$,]/g, ''));
                valueElement.textContent = users.toLocaleString();
                barElement.style.width = `${Math.min(100, (users / 1000) * 10)}%`;
            }
        });
    }

    async loadRecentActivity() {
        try {
            const data = await this.api.getRecentActivity({ limit: 10 });
            this.renderRecentActivity(data);
        } catch (error) {
            console.error('Error loading recent activity:', error);
            this.renderRecentActivity([]);
        }
    }

    renderRecentActivity(activities) {
        const container = document.getElementById('activity-list');
        if (!container) return;

        if (activities.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="10"></circle>
                            <polyline points="12,6 12,12 16,14"></polyline>
                        </svg>
                    </div>
                    <div class="empty-state-title">No Recent Activity</div>
                    <div class="empty-state-message">Activity will appear here as users interact with the platform.</div>
                </div>
            `;
            return;
        }

        container.innerHTML = activities.map(activity => `
            <div class="activity-item">
                <div class="activity-icon ${activity.type}">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        ${this.getActivityIcon(activity.type)}
                    </svg>
                </div>
                <div class="activity-content">
                    <div class="activity-title-text">${activity.title}</div>
                    <div class="activity-description">${activity.description}</div>
                </div>
                <div class="activity-time">${this.formatTimeAgo(activity.timestamp)}</div>
            </div>
        `).join('');
    }

    getActivityIcon(type) {
        const icons = {
            user: '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle>',
            report: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14,2 14,8 20,8"></polyline>',
            system: '<circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1 1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>',
            notification: '<path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path>'
        };
        return icons[type] || icons.system;
    }

    async loadNotifications() {
        try {
            const data = await this.api.getNotifications({ limit: 20 });
            this.renderNotifications(data.notifications || data);
            this.updateNotificationBadge(data.unread_count || 0);
        } catch (error) {
            console.error('Error loading notifications:', error);
        }
    }

    renderNotifications(notifications) {
        const container = document.getElementById('notification-list');
        if (!container) return;

        if (notifications.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                            <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
                        </svg>
                    </div>
                    <div class="empty-state-title">No Notifications</div>
                    <div class="empty-state-message">You're all caught up! New notifications will appear here.</div>
            </div>
        `;
            return;
        }

        container.innerHTML = notifications.map(notification => `
            <div class="notification-item ${notification.is_read ? 'read' : 'unread'}">
                <div class="notification-icon ${notification.notification_type}">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        ${this.getNotificationIcon(notification.notification_type)}
                    </svg>
                </div>
                <div class="notification-content">
                    <div class="notification-title">${notification.title}</div>
                    <div class="notification-message">${notification.message}</div>
                    <div class="notification-time">${this.formatTimeAgo(notification.created_at)}</div>
                </div>
            </div>
        `).join('');
    }

    getNotificationIcon(type) {
        const icons = {
            info: '<circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line>',
            warning: '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line>',
            error: '<circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line>',
            success: '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22,4 12,14.01 9,11.01"></polyline>'
        };
        return icons[type] || icons.info;
    }

    updateNotificationBadge(count) {
        const badge = document.getElementById('notification-badge');
        if (badge) {
            badge.textContent = count;
            badge.style.display = count > 0 ? 'block' : 'none';
        }
    }

    async refreshDashboard() {
        if (this.isRefreshing) return;
        
        this.isRefreshing = true;
        const refreshBtn = document.getElementById('refresh-btn');
        
        if (refreshBtn) {
            refreshBtn.classList.add('loading');
            refreshBtn.disabled = true;
        }

        try {
            await this.loadDashboardData();
            await this.loadRecentActivity();
            await this.loadNotifications();
            
            // Show success feedback
            this.showToast('Dashboard refreshed successfully', 'success');
        } catch (error) {
            console.error('Error refreshing dashboard:', error);
            this.showToast('Failed to refresh dashboard', 'error');
        } finally {
            this.isRefreshing = false;
            
            if (refreshBtn) {
                refreshBtn.classList.remove('loading');
                refreshBtn.disabled = false;
            }
        }
    }

    async exportDashboard() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/admin/data/export`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.authToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    data_type: 'dashboard',
                    format: 'pdf'
                })
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `dashboard-export-${new Date().toISOString().split('T')[0]}.pdf`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                this.showToast('Dashboard exported successfully', 'success');
            } else {
                throw new Error('Export failed');
            }
        } catch (error) {
            console.error('Error exporting dashboard:', error);
            this.showToast('Failed to export dashboard', 'error');
        }
    }

    handleGlobalSearch(query) {
        if (query.length < 2) return;
        
        // Implement global search functionality
        console.log('Global search:', query);
        // This would typically make an API call to search across all entities
    }

    startAutoRefresh() {
        // Refresh dashboard every 5 minutes
        this.refreshInterval = setInterval(() => {
            this.refreshDashboard();
        }, 5 * 60 * 1000);
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    showLoadingState() {
        document.body.classList.add('loading');
    }

    hideLoadingState() {
        document.body.classList.remove('loading');
    }

    showErrorState(message) {
        // Show error message to user
        this.showToast(message, 'error');
    }

    showToast(message, type = 'info') {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;

        // Add to page
        document.body.appendChild(toast);

        // Remove after 3 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 3000);
    }

    formatNumber(num) {
        return new Intl.NumberFormat('en-US').format(num);
    }

    formatTimeAgo(timestamp) {
        const now = new Date();
        const time = new Date(timestamp);
        const diffInSeconds = Math.floor((now - time) / 1000);
        
        if (diffInSeconds < 60) {
            return 'Just now';
        } else if (diffInSeconds < 3600) {
            const minutes = Math.floor(diffInSeconds / 60);
            return `${minutes}m ago`;
        } else if (diffInSeconds < 86400) {
            const hours = Math.floor(diffInSeconds / 3600);
            return `${hours}h ago`;
        } else {
            const days = Math.floor(diffInSeconds / 86400);
            return `${days}d ago`;
        }
    }

    destroy() {
        this.stopAutoRefresh();
        
        // Destroy charts
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.adminDashboard = new AdminDashboard();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.adminDashboard) {
        window.adminDashboard.destroy();
    }
});