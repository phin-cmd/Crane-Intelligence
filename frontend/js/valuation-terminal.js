/**
 * Bloomberg-style Valuation Terminal JavaScript
 * Professional terminal interface for crane valuations
 */

class ValuationTerminal {
    constructor() {
        this.currentTab = 'valuation';
        this.valuationData = {};
        this.marketData = {};
        this.charts = {};
        this.alerts = [];
        this.watchlist = [];
        this.recentValuations = [];
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.updateTime();
        this.loadInitialData();
        this.setupCharts();
        this.startDataRefresh();
        
        // Update time every second
        setInterval(() => this.updateTime(), 1000);
        
        // Refresh market data every 30 seconds
        setInterval(() => this.refreshMarketData(), 30000);
    }

    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.switchTab(e.target.closest('.tab').dataset.tab);
            });
        });

        // Valuation form
        document.getElementById('valuation-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.calculateValuation();
        });

        // Alert form
        document.getElementById('alert-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.createAlert();
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });
    }

    updateTime() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-US', { 
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        
        document.getElementById('current-time').textContent = timeString;
        document.getElementById('last-update').textContent = timeString;
    }

    loadInitialData() {
        // Load market data
        this.loadMarketData();
        
        // Load watchlist
        this.loadWatchlist();
        
        // Load recent valuations
        this.loadRecentValuations();
        
        // Load alerts
        this.loadAlerts();
    }

    async loadMarketData() {
        try {
            const response = await fetch('/api/v1/analytics/market-analysis');
            if (response.ok) {
                const data = await response.json();
                this.marketData = data.data;
                this.updateMarketOverview();
            }
        } catch (error) {
            console.error('Error loading market data:', error);
        }
    }

    updateMarketOverview() {
        const overview = document.getElementById('market-overview');
        if (!overview) return;

        const marketItems = [
            { label: 'Crane Index', value: '+2.4%', positive: true },
            { label: 'Heavy Equipment', value: '+1.8%', positive: true },
            { label: 'Construction', value: '-0.5%', positive: false },
            { label: 'Oil & Gas', value: '+3.2%', positive: true }
        ];

        overview.innerHTML = marketItems.map(item => `
            <div class="market-item">
                <span class="label">${item.label}</span>
                <span class="value ${item.positive ? 'positive' : 'negative'}">${item.value}</span>
            </div>
        `).join('');
    }

    loadWatchlist() {
        this.watchlist = [
            { symbol: 'GROVE GMK5250L', price: 1250000, change: 2.1, positive: true },
            { symbol: 'LIEBHERR LTM1120', price: 2100000, change: -1.2, positive: false },
            { symbol: 'MANITOWOC 2250', price: 850000, change: 0.8, positive: true }
        ];

        this.updateWatchlist();
    }

    updateWatchlist() {
        const watchlist = document.getElementById('watchlist');
        if (!watchlist) return;

        watchlist.innerHTML = this.watchlist.map(item => `
            <div class="watchlist-item" onclick="terminal.showValuationDetails('${item.symbol}')">
                <span class="symbol">${item.symbol}</span>
                <span class="price">$${this.formatNumber(item.price)}</span>
                <span class="change ${item.positive ? 'positive' : 'negative'}">${item.positive ? '+' : ''}${item.change}%</span>
            </div>
        `).join('');
    }

    loadRecentValuations() {
        this.recentValuations = [
            { title: 'Grove GMK5250L', time: '2 hours ago', price: 1250000 },
            { title: 'Liebherr LTM1120', time: '4 hours ago', price: 2100000 },
            { title: 'Manitowoc 2250', time: '6 hours ago', price: 850000 }
        ];

        this.updateRecentValuations();
    }

    updateRecentValuations() {
        const container = document.getElementById('recent-valuations');
        if (!container) return;

        container.innerHTML = this.recentValuations.map(item => `
            <div class="valuation-item" onclick="terminal.showValuationDetails('${item.title}')">
                <div class="valuation-info">
                    <div class="valuation-title">${item.title}</div>
                    <div class="valuation-time">${item.time}</div>
                </div>
                <div class="valuation-price">$${this.formatNumber(item.price)}</div>
            </div>
        `).join('');
    }

    loadAlerts() {
        this.alerts = [
            { type: 'high', title: 'Market Volatility Alert', time: '2 min ago', icon: 'fas fa-exclamation-triangle' },
            { type: 'medium', title: 'New Valuation Available', time: '5 min ago', icon: 'fas fa-info-circle' }
        ];

        this.updateAlerts();
    }

    updateAlerts() {
        const container = document.getElementById('alerts-list');
        if (!container) return;

        container.innerHTML = this.alerts.map(alert => `
            <div class="alert-item ${alert.type}">
                <div class="alert-icon">
                    <i class="${alert.icon}"></i>
                </div>
                <div class="alert-content">
                    <div class="alert-title">${alert.title}</div>
                    <div class="alert-time">${alert.time}</div>
                </div>
            </div>
        `).join('');
    }

    switchTab(tabName) {
        // Update tab appearance
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update tab content
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');

        this.currentTab = tabName;

        // Load tab-specific data
        if (tabName === 'market-data') {
            this.loadMarketDataTab();
        } else if (tabName === 'analytics') {
            this.loadAnalyticsTab();
        } else if (tabName === 'reports') {
            this.loadReportsTab();
        }
    }

    async calculateValuation() {
        const form = document.getElementById('valuation-form');
        const formData = new FormData(form);
        
        const valuationData = {
            manufacturer: formData.get('manufacturer'),
            model: formData.get('model'),
            year: parseInt(formData.get('year')),
            hours: parseInt(formData.get('hours')),
            capacity_tons: parseFloat(formData.get('capacity')),
            condition_score: parseFloat(formData.get('condition')),
            location: formData.get('location'),
            boom_length_ft: parseFloat(formData.get('boom_length')) || 0
        };

        try {
            // Show loading state
            this.showLoading('Calculating valuation...');

            const response = await fetch('/api/v1/enhanced-valuation/value-crane', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(valuationData)
            });

            if (response.ok) {
                const result = await response.json();
                this.displayValuationResults(result);
                this.addToRecentValuations(valuationData, result);
            } else {
                throw new Error('Valuation calculation failed');
            }
        } catch (error) {
            console.error('Error calculating valuation:', error);
            this.showError('Failed to calculate valuation. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    displayValuationResults(result) {
        const resultsContainer = document.getElementById('valuation-results');
        const detailsContainer = document.getElementById('valuation-details');

        // Update main results
        document.getElementById('fair-market-value').textContent = this.formatCurrency(result.fair_market_value);
        document.getElementById('wholesale-value').textContent = this.formatCurrency(result.wholesale_value);
        document.getElementById('retail-value').textContent = this.formatCurrency(result.retail_value);
        document.getElementById('confidence-score').textContent = `${Math.round(result.confidence_score * 100)}%`;

        // Update detailed results
        detailsContainer.innerHTML = `
            <div class="valuation-details-content">
                <h4>Detailed Analysis</h4>
                <div class="details-grid">
                    <div class="detail-item">
                        <span class="detail-label">Market Position:</span>
                        <span class="detail-value">${result.market_position}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Deal Score:</span>
                        <span class="detail-value">${result.deal_score}/10</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Comparable Sales:</span>
                        <span class="detail-value">${result.comparable_count}</span>
                    </div>
                </div>
                
                <h4>Market Trends</h4>
                <div class="trends-grid">
                    <div class="trend-item">
                        <span class="trend-label">Price Trend:</span>
                        <span class="trend-value">${result.market_trends.price_trend}</span>
                    </div>
                    <div class="trend-item">
                        <span class="trend-label">Demand Level:</span>
                        <span class="trend-value">${result.market_trends.demand_level}</span>
                    </div>
                    <div class="trend-item">
                        <span class="trend-label">Market Activity:</span>
                        <span class="trend-value">${result.market_trends.market_activity}</span>
                    </div>
                </div>

                <h4>Financing Scenarios</h4>
                <div class="financing-scenarios">
                    ${result.financing_scenarios.map(scenario => `
                        <div class="scenario-item">
                            <div class="scenario-title">${scenario.scenario}</div>
                            <div class="scenario-details">
                                <span>Down Payment: ${this.formatCurrency(scenario.down_payment)}</span>
                                <span>Monthly Payment: ${this.formatCurrency(scenario.monthly_payment)}</span>
                                <span>Total Cost: ${this.formatCurrency(scenario.total_cost)}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>

                <h4>Risk Factors</h4>
                <div class="risk-factors">
                    ${result.risk_factors.length > 0 ? 
                        result.risk_factors.map(risk => `<div class="risk-item">• ${risk}</div>`).join('') :
                        '<div class="no-risks">No significant risk factors identified</div>'
                    }
                </div>

                <h4>Recommendations</h4>
                <div class="recommendations">
                    ${result.recommendations.map(rec => `<div class="recommendation-item">• ${rec}</div>`).join('')}
                </div>
            </div>
        `;

        resultsContainer.style.display = 'block';
        resultsContainer.scrollIntoView({ behavior: 'smooth' });
    }

    addToRecentValuations(valuationData, result) {
        const newValuation = {
            title: `${valuationData.manufacturer} ${valuationData.model}`,
            time: 'Just now',
            price: result.fair_market_value
        };

        this.recentValuations.unshift(newValuation);
        this.recentValuations = this.recentValuations.slice(0, 5); // Keep only last 5
        this.updateRecentValuations();
    }

    async loadMarketDataTab() {
        try {
            const response = await fetch('/api/v1/analytics/market-analysis');
            if (response.ok) {
                const data = await response.json();
                this.updateMarketCharts(data.data);
            }
        } catch (error) {
            console.error('Error loading market data:', error);
        }
    }

    updateMarketCharts(data) {
        // Update price chart
        this.updatePriceChart();
        
        // Update volume chart
        this.updateVolumeChart();
        
        // Update market data table
        this.updateMarketDataTable();
    }

    updatePriceChart() {
        const ctx = document.getElementById('price-chart');
        if (!ctx) return;

        if (this.charts.priceChart) {
            this.charts.priceChart.destroy();
        }

        this.charts.priceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Crane Index',
                    data: [100, 102, 105, 108, 110, 115],
                    borderColor: '#00ff85',
                    backgroundColor: 'rgba(0, 255, 133, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#fff'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: '#ccc'
                        },
                        grid: {
                            color: '#333'
                        }
                    },
                    y: {
                        ticks: {
                            color: '#ccc'
                        },
                        grid: {
                            color: '#333'
                        }
                    }
                }
            }
        });
    }

    updateVolumeChart() {
        const ctx = document.getElementById('volume-chart');
        if (!ctx) return;

        if (this.charts.volumeChart) {
            this.charts.volumeChart.destroy();
        }

        this.charts.volumeChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
                datasets: [{
                    label: 'Volume',
                    data: [120, 150, 180, 200, 160],
                    backgroundColor: '#00ff85',
                    borderColor: '#00cc6a'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#fff'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: '#ccc'
                        },
                        grid: {
                            color: '#333'
                        }
                    },
                    y: {
                        ticks: {
                            color: '#ccc'
                        },
                        grid: {
                            color: '#333'
                        }
                    }
                }
            }
        });
    }

    updateMarketDataTable() {
        const tbody = document.getElementById('market-data-body');
        if (!tbody) return;

        const marketData = [
            { symbol: 'GROVE GMK5250L', price: 1250000, change: 2.1, volume: 15, time: '14:32' },
            { symbol: 'LIEBHERR LTM1120', price: 2100000, change: -1.2, volume: 8, time: '14:30' },
            { symbol: 'MANITOWOC 2250', price: 850000, change: 0.8, volume: 22, time: '14:28' }
        ];

        tbody.innerHTML = marketData.map(item => `
            <tr>
                <td>${item.symbol}</td>
                <td>${this.formatCurrency(item.price)}</td>
                <td class="${item.change > 0 ? 'positive' : 'negative'}">${item.change > 0 ? '+' : ''}${item.change}%</td>
                <td>${item.volume}</td>
                <td>${item.time}</td>
            </tr>
        `).join('');
    }

    async loadAnalyticsTab() {
        try {
            const response = await fetch('/api/v1/analytics/dashboard');
            if (response.ok) {
                const data = await response.json();
                this.updateAnalyticsCharts(data.data);
            }
        } catch (error) {
            console.error('Error loading analytics:', error);
        }
    }

    updateAnalyticsCharts(data) {
        // Update market trends chart
        this.updateMarketTrendsChart();
        
        // Update regional analysis chart
        this.updateRegionalAnalysisChart();
        
        // Update price distribution chart
        this.updatePriceDistributionChart();
        
        // Update performance metrics chart
        this.updatePerformanceMetricsChart();
    }

    updateMarketTrendsChart() {
        const container = document.getElementById('market-trends-chart');
        if (!container) return;

        const trace = {
            x: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            y: [100, 102, 105, 108, 110, 115],
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Market Index',
            line: { color: '#00ff85' }
        };

        const layout = {
            title: 'Market Trends',
            paper_bgcolor: '#1a1a1a',
            plot_bgcolor: '#1a1a1a',
            font: { color: '#fff' },
            xaxis: { color: '#ccc' },
            yaxis: { color: '#ccc' }
        };

        Plotly.newPlot(container, [trace], layout, { responsive: true });
    }

    updateRegionalAnalysisChart() {
        const container = document.getElementById('regional-analysis-chart');
        if (!container) return;

        const trace = {
            x: ['Texas', 'California', 'Florida', 'New York'],
            y: [1200000, 1500000, 1100000, 1300000],
            type: 'bar',
            marker: { color: '#00ff85' }
        };

        const layout = {
            title: 'Regional Price Analysis',
            paper_bgcolor: '#1a1a1a',
            plot_bgcolor: '#1a1a1a',
            font: { color: '#fff' },
            xaxis: { color: '#ccc' },
            yaxis: { color: '#ccc' }
        };

        Plotly.newPlot(container, [trace], layout, { responsive: true });
    }

    updatePriceDistributionChart() {
        const container = document.getElementById('price-distribution-chart');
        if (!container) return;

        // Generate random data for price distribution
        const data = [];
        for (let i = 0; i < 1000; i++) {
            data.push(Math.random() * 2000000 + 500000);
        }

        const trace = {
            x: data,
            type: 'histogram',
            marker: { color: '#00ff85' },
            nbinsx: 30
        };

        const layout = {
            title: 'Price Distribution',
            paper_bgcolor: '#1a1a1a',
            plot_bgcolor: '#1a1a1a',
            font: { color: '#fff' },
            xaxis: { color: '#ccc' },
            yaxis: { color: '#ccc' }
        };

        Plotly.newPlot(container, [trace], layout, { responsive: true });
    }

    updatePerformanceMetricsChart() {
        const container = document.getElementById('performance-metrics-chart');
        if (!container) return;

        const trace = {
            values: [99.8, 0.2],
            labels: ['Uptime', 'Downtime'],
            type: 'pie',
            marker: {
                colors: ['#00ff85', '#ff4444']
            }
        };

        const layout = {
            title: 'System Performance',
            paper_bgcolor: '#1a1a1a',
            font: { color: '#fff' }
        };

        Plotly.newPlot(container, [trace], layout, { responsive: true });
    }

    async loadReportsTab() {
        // Load existing reports
        this.loadReportsList();
    }

    loadReportsList() {
        const container = document.getElementById('reports-list');
        if (!container) return;

        const reports = [
            { name: 'Executive Summary - Q3 2024', date: '2024-09-28', type: 'executive' },
            { name: 'Market Analysis Report', date: '2024-09-27', type: 'market' },
            { name: 'Detailed Valuation Report', date: '2024-09-26', type: 'detailed' }
        ];

        container.innerHTML = reports.map(report => `
            <div class="report-item">
                <div class="report-info">
                    <div class="report-name">${report.name}</div>
                    <div class="report-date">${report.date}</div>
                </div>
                <div class="report-actions">
                    <button class="btn-secondary" onclick="terminal.downloadReport('${report.type}')">
                        <i class="fas fa-download"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }

    async generateReport(type) {
        try {
            this.showLoading('Generating report...');

            const response = await fetch(`/api/v1/analytics/reports/${type}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
                    end_date: new Date().toISOString(),
                    report_format: 'json',
                    report_type: type
                })
            });

            if (response.ok) {
                const data = await response.json();
                this.showSuccess('Report generated successfully!');
                this.loadReportsList();
            } else {
                throw new Error('Report generation failed');
            }
        } catch (error) {
            console.error('Error generating report:', error);
            this.showError('Failed to generate report. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    setupCharts() {
        // Initialize charts when tab is first loaded
        this.setupChartStyles();
    }

    setupChartStyles() {
        // Configure Chart.js defaults
        Chart.defaults.color = '#fff';
        Chart.defaults.borderColor = '#333';
        Chart.defaults.backgroundColor = 'rgba(0, 255, 133, 0.1)';
    }

    startDataRefresh() {
        // Refresh data every 5 minutes
        setInterval(() => {
            this.refreshMarketData();
        }, 300000);
    }

    async refreshMarketData() {
        try {
            await this.loadMarketData();
            this.updateMarketOverview();
            this.updateWatchlist();
        } catch (error) {
            console.error('Error refreshing market data:', error);
        }
    }

    handleKeyboardShortcuts(e) {
        // Ctrl + number keys for tab switching
        if (e.ctrlKey && e.key >= '1' && e.key <= '4') {
            const tabs = ['valuation', 'market-data', 'analytics', 'reports'];
            const tabIndex = parseInt(e.key) - 1;
            if (tabs[tabIndex]) {
                this.switchTab(tabs[tabIndex]);
            }
        }

        // F5 to refresh data
        if (e.key === 'F5') {
            e.preventDefault();
            this.refreshMarketData();
        }

        // Escape to close modals
        if (e.key === 'Escape') {
            this.closeAllModals();
        }
    }

    showValuationDetails(symbol) {
        // Show detailed valuation for selected symbol
        console.log('Showing valuation details for:', symbol);
        // Implementation would show detailed valuation popup
    }

    createAlert() {
        const modal = document.getElementById('alert-modal');
        modal.style.display = 'block';
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        modal.style.display = 'none';
    }

    closeAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.style.display = 'none';
        });
    }

    showLoading(message) {
        // Show loading indicator
        console.log('Loading:', message);
    }

    hideLoading() {
        // Hide loading indicator
        console.log('Loading complete');
    }

    showSuccess(message) {
        // Show success notification
        console.log('Success:', message);
    }

    showError(message) {
        // Show error notification
        console.log('Error:', message);
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount);
    }

    formatNumber(number) {
        return new Intl.NumberFormat('en-US').format(number);
    }

    // Quick tool functions
    openCalculator() {
        console.log('Opening calculator');
    }

    openConverter() {
        console.log('Opening unit converter');
    }

    openCalendar() {
        console.log('Opening calendar');
    }

    openNotes() {
        console.log('Opening notes');
    }

    downloadReport(type) {
        console.log('Downloading report:', type);
    }
}

// Global functions for HTML onclick handlers
function refreshMarketData() {
    terminal.refreshMarketData();
}

function addToWatchlist() {
    console.log('Adding to watchlist');
}

function createAlert() {
    terminal.createAlert();
}

function clearForm() {
    document.getElementById('valuation-form').reset();
}

function openCalculator() {
    terminal.openCalculator();
}

function openConverter() {
    terminal.openConverter();
}

function openCalendar() {
    terminal.openCalendar();
}

function openNotes() {
    terminal.openNotes();
}

function generateReport(type) {
    terminal.generateReport(type);
}

function closeModal(modalId) {
    terminal.closeModal(modalId);
}

// Initialize terminal when page loads
let terminal;
document.addEventListener('DOMContentLoaded', () => {
    terminal = new ValuationTerminal();
});
