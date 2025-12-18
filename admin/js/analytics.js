/**
 * Analytics & Reporting JavaScript
 * Handles analytics data visualization and report generation
 */

class AnalyticsManager {
    constructor() {
        this.charts = {};
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadAnalyticsData();
        this.initializeCharts();
    }

    bindEvents() {
        // Period selectors
        document.getElementById('userGrowthPeriod').addEventListener('change', () => this.updateUserGrowthChart());
        document.getElementById('revenuePeriod').addEventListener('change', () => this.updateRevenueChart());
        
        // Report generation
        document.getElementById('generateReportBtn').addEventListener('click', () => this.showReportModal());
        
        // Export functionality
        document.getElementById('exportDataBtn').addEventListener('click', () => this.exportData());
        
        // Window resize handler
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => this.resizeCharts(), 250);
        });
    }

    async loadAnalyticsData() {
        try {
            const api = new AdminAPI();
            const data = await api.getAnalyticsData();
            this.updateOverviewStats(data.overview);
            this.updateCharts(data);
        } catch (error) {
            console.error('Error loading analytics data:', error);
            this.showError('Failed to load analytics data');
        }
    }

    updateOverviewStats(overview) {
        document.getElementById('totalUsers').textContent = overview.total_users || 0;
        document.getElementById('totalRevenue').textContent = `$${(overview.total_revenue || 0).toLocaleString()}`;
        document.getElementById('reportsGenerated').textContent = overview.reports_generated || 0;
        document.getElementById('apiCalls').textContent = (overview.api_calls || 0).toLocaleString();
    }

    initializeCharts() {
        this.initializeUserGrowthChart();
        this.initializeRevenueChart();
        this.initializeSubscriptionChart();
        this.initializeGeographicChart();
    }

    initializeUserGrowthChart() {
        const ctx = document.getElementById('userGrowthChart').getContext('2d');
        this.charts.userGrowth = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'New Users',
                    data: [],
                    borderColor: '#00d4aa',
                    backgroundColor: 'rgba(0, 212, 170, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#ffffff'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: '#ffffff' },
                        grid: { color: '#333333' }
                    },
                    y: {
                        ticks: { color: '#ffffff' },
                        grid: { color: '#333333' }
                    }
                }
            }
        });
    }

    initializeRevenueChart() {
        const ctx = document.getElementById('revenueChart').getContext('2d');
        this.charts.revenue = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Revenue',
                    data: [],
                    backgroundColor: '#ff6b35',
                    borderColor: '#ff6b35'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#ffffff'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: '#ffffff' },
                        grid: { color: '#333333' }
                    },
                    y: {
                        ticks: { color: '#ffffff' },
                        grid: { color: '#333333' }
                    }
                }
            }
        });
    }

    initializeSubscriptionChart() {
        const ctx = document.getElementById('subscriptionChart').getContext('2d');
        this.charts.subscription = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: [], // Will be populated from API data
                datasets: [{
                    data: [],
                    backgroundColor: ['#ff6b35', '#00d4aa', '#4a90e2', '#FFD600', '#00FF85'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#ffffff'
                        }
                    }
                }
            }
        });
    }

    initializeGeographicChart() {
        const ctx = document.getElementById('geographicChart').getContext('2d');
        this.charts.geographic = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Users by Country',
                    data: [],
                    backgroundColor: '#4a90e2',
                    borderColor: '#4a90e2'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#ffffff'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: '#ffffff' },
                        grid: { color: '#333333' }
                    },
                    y: {
                        ticks: { color: '#ffffff' },
                        grid: { color: '#333333' }
                    }
                }
            }
        });
    }

    updateCharts(data) {
        this.updateUserGrowthChart(data.user_analytics?.registration_trends);
        this.updateRevenueChart(data.financial_analytics?.revenue_trends);
        this.updateSubscriptionChart(data.user_analytics?.subscription_distribution);
        this.updateGeographicChart(data.user_analytics?.geographic_distribution);
    }

    resizeCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart) {
                chart.resize();
            }
        });
    }

    updateUserGrowthChart(trends) {
        if (!trends) return;
        
        const labels = trends.map(item => item.date);
        const data = trends.map(item => item.count);
        
        this.charts.userGrowth.data.labels = labels;
        this.charts.userGrowth.data.datasets[0].data = data;
        this.charts.userGrowth.update();
    }

    updateRevenueChart(trends) {
        if (!trends) return;
        
        const labels = trends.map(item => item.date);
        const data = trends.map(item => item.revenue);
        
        this.charts.revenue.data.labels = labels;
        this.charts.revenue.data.datasets[0].data = data;
        this.charts.revenue.update();
    }

    updateSubscriptionChart(distribution) {
        if (!distribution) {
            // Show empty chart if no data
            this.charts.subscription.data.labels = [];
            this.charts.subscription.data.datasets[0].data = [];
            this.charts.subscription.update();
            return;
        }
        
        // Handle both object format {basic: 10, pro: 5} and array format [{label: 'Basic', count: 10}]
        if (Array.isArray(distribution)) {
            this.charts.subscription.data.labels = distribution.map(item => item.label || item.name || 'Unknown');
            this.charts.subscription.data.datasets[0].data = distribution.map(item => item.count || item.value || 0);
        } else {
            // Object format - extract keys as labels and values as data
            const labels = Object.keys(distribution);
            const data = labels.map(key => distribution[key] || 0);
            this.charts.subscription.data.labels = labels.map(key => key.charAt(0).toUpperCase() + key.slice(1));
            this.charts.subscription.data.datasets[0].data = data;
        }
        this.charts.subscription.update();
    }

    updateGeographicChart(distribution) {
        if (!distribution) return;
        
        const labels = distribution.map(item => item.country);
        const data = distribution.map(item => item.users);
        
        this.charts.geographic.data.labels = labels;
        this.charts.geographic.data.datasets[0].data = data;
        this.charts.geographic.update();
    }

    showReportModal() {
        // Create report generation modal
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Generate Custom Report</h3>
                    <button class="modal-close" onclick="this.closest('.modal').remove()">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="reportForm">
                        <div class="form-group">
                            <label for="reportType">Report Type</label>
                            <select id="reportType" required>
                                <option value="user_analytics">User Analytics</option>
                                <option value="financial">Financial Report</option>
                                <option value="technical">Technical Report</option>
                                <option value="growth">Growth Report</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="reportPeriod">Period</label>
                            <select id="reportPeriod" required>
                                <option value="7d">Last 7 Days</option>
                                <option value="30d">Last 30 Days</option>
                                <option value="90d">Last 90 Days</option>
                                <option value="1y">Last Year</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="reportFormat">Format</label>
                            <select id="reportFormat" required>
                                <option value="pdf">PDF</option>
                                <option value="excel">Excel</option>
                                <option value="csv">CSV</option>
                            </select>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="this.closest('.modal').remove()">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="analyticsManager.generateReport()">Generate Report</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    async generateReport() {
        try {
            const form = document.getElementById('reportForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            
            const api = new AdminAPI();
            const response = await api.generateReport(data);
            this.showSuccess('Report generated successfully');
            
            // Close modal
            document.querySelector('.modal').remove();
            
            // Download report if URL provided
            if (response.download_url) {
                window.open(response.download_url, '_blank');
            }
        } catch (error) {
            console.error('Error generating report:', error);
            this.showError('Failed to generate report');
        }
    }

    async exportData() {
        try {
            const dataType = document.getElementById('exportDataType').value;
            const format = document.getElementById('exportFormat').value;
            const dateRange = document.getElementById('exportDateRange').value;
            
            const api = new AdminAPI();
            const response = await api.exportData({
                data_type: dataType,
                format: format,
                date_range: dateRange
            });
            
            this.showSuccess('Data export started');
            
            if (response.download_url) {
                window.open(response.download_url, '_blank');
            }
        } catch (error) {
            console.error('Error exporting data:', error);
            this.showError('Failed to export data');
        }
    }

    showSuccess(message) {
        const notification = document.createElement('div');
        notification.className = 'notification success';
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 3000);
    }

    showError(message) {
        const notification = document.createElement('div');
        notification.className = 'notification error';
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 5000);
    }
}

// Initialize analytics manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.analyticsManager = new AnalyticsManager();
});
