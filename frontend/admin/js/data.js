/**
 * Data Management JavaScript
 * Handles data sources, quality monitoring, and database administration
 */

class DataManager {
    constructor() {
        this.currentTab = 'sources';
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadDataOverview();
    }

    bindEvents() {
        // Tab navigation
        document.querySelectorAll('.data-tab').forEach(tab => {
            tab.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });
        
        // Data source management
        document.getElementById('addDataSourceBtn').addEventListener('click', () => this.showDataSourceModal());
        
        // Quality checks
        document.getElementById('runQualityCheck').addEventListener('click', () => this.runQualityCheck());
        
        // Background jobs
        document.getElementById('createJobBtn').addEventListener('click', () => this.showJobModal());
        
        // Database management
        document.getElementById('backupDbBtn').addEventListener('click', () => this.backupDatabase());
        document.getElementById('optimizeDbBtn').addEventListener('click', () => this.optimizeDatabase());
        
        // Pipeline management
        document.getElementById('runPipelineBtn').addEventListener('click', () => this.runPipeline());
    }

    switchTab(tabName) {
        // Hide all panels
        document.querySelectorAll('.data-panel').forEach(panel => {
            panel.classList.remove('active');
        });
        
        // Remove active class from all tabs
        document.querySelectorAll('.data-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        
        // Show selected panel
        document.getElementById(`${tabName}-panel`).classList.add('active');
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        this.currentTab = tabName;
        
        // Load data for the selected tab
        switch(tabName) {
            case 'sources':
                this.loadDataSources();
                break;
            case 'quality':
                this.loadQualityMetrics();
                break;
            case 'jobs':
                this.loadBackgroundJobs();
                break;
            case 'database':
                this.loadDatabaseInfo();
                break;
            case 'pipeline':
                this.loadPipelineStatus();
                break;
        }
    }

    async loadDataOverview() {
        try {
            const api = new AdminAPI();
            const data = await api.getDataOverview();
            this.updateDataStats(data);
        } catch (error) {
            console.error('Error loading data overview:', error);
            this.showError('Failed to load data overview');
        }
    }

    updateDataStats(data) {
        document.getElementById('totalRecords').textContent = (data.total_records || 0).toLocaleString();
        document.getElementById('dataSources').textContent = data.data_sources || 0;
        document.getElementById('dataQuality').textContent = `${data.data_quality || 0}%`;
        document.getElementById('lastSync').textContent = data.last_sync || 'Never';
    }

    async loadDataSources() {
        try {
            const api = new AdminAPI();
            const sources = await api.getDataSources();
            this.renderDataSources(sources);
        } catch (error) {
            console.error('Error loading data sources:', error);
            this.showError('Failed to load data sources');
        }
    }

    renderDataSources(sources) {
        const container = document.querySelector('.sources-grid');
        container.innerHTML = '';

        if (sources.length === 0) {
            container.innerHTML = '<div class="no-data">No data sources configured</div>';
            return;
        }

        sources.forEach(source => {
            const card = document.createElement('div');
            card.className = 'source-card';
            card.innerHTML = `
                <div class="source-header">
                    <h4>${source.name}</h4>
                    <span class="status-badge ${source.is_active ? 'active' : 'inactive'}">${source.is_active ? 'Active' : 'Inactive'}</span>
                </div>
                <div class="source-details">
                    <div class="detail-item">
                        <span class="label">Type:</span>
                        <span class="value">${source.source_type}</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">Endpoint:</span>
                        <span class="value">${source.endpoint_url || 'N/A'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">Last Sync:</span>
                        <span class="value">${source.last_sync ? this.formatDate(source.last_sync) : 'Never'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">Records:</span>
                        <span class="value">${source.record_count || 0}</span>
                    </div>
                </div>
                <div class="source-actions">
                    <button class="btn btn-sm btn-secondary" onclick="dataManager.editDataSource(${source.id})">Edit</button>
                    <button class="btn btn-sm btn-primary" onclick="dataManager.syncDataSource(${source.id})">Sync Now</button>
                    <button class="btn btn-sm btn-danger" onclick="dataManager.removeDataSource(${source.id})">Remove</button>
                </div>
            `;
            container.appendChild(card);
        });
    }

    async loadQualityMetrics() {
        try {
            const api = new AdminAPI();
            const metrics = await api.getDataQualityMetrics();
            this.renderQualityMetrics(metrics);
        } catch (error) {
            console.error('Error loading quality metrics:', error);
            this.showError('Failed to load quality metrics');
        }
    }

    renderQualityMetrics(metrics) {
        // Update overall quality score
        const overallScore = document.querySelector('.metric-score');
        if (overallScore) {
            overallScore.textContent = `${metrics.overall_score || 0}%`;
            overallScore.className = `metric-score ${this.getQualityClass(metrics.overall_score)}`;
        }

        // Update individual metrics
        const metricCards = document.querySelectorAll('.metric-card');
        metricCards.forEach(card => {
            const header = card.querySelector('.metric-header h4');
            const score = card.querySelector('.metric-score');
            const progressFill = card.querySelector('.progress-fill');
            
            if (header && score && progressFill) {
                const metricName = header.textContent.toLowerCase();
                let value = 0;
                
                switch(metricName) {
                    case 'accuracy':
                        value = metrics.accuracy || 0;
                        break;
                    case 'completeness':
                        value = metrics.completeness || 0;
                        break;
                    case 'freshness':
                        value = metrics.freshness || 0;
                        break;
                }
                
                score.textContent = `${value}%`;
                score.className = `metric-score ${this.getQualityClass(value)}`;
                progressFill.style.width = `${value}%`;
            }
        });
    }

    async loadBackgroundJobs() {
        try {
            const api = new AdminAPI();
            const jobs = await api.getBackgroundJobs();
            this.renderBackgroundJobs(jobs);
        } catch (error) {
            console.error('Error loading background jobs:', error);
            this.showError('Failed to load background jobs');
        }
    }

    renderBackgroundJobs(jobs) {
        const tbody = document.getElementById('jobsTableBody');
        tbody.innerHTML = '';

        if (jobs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center">No background jobs found</td></tr>';
            return;
        }

        jobs.forEach(job => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${job.job_name}</td>
                <td><span class="type-badge ${job.job_type}">${job.job_type}</span></td>
                <td><span class="status-badge ${job.status}">${job.status}</span></td>
                <td>
                    <div class="progress-container">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${job.progress}%"></div>
                        </div>
                        <span class="progress-text">${job.progress}%</span>
                    </div>
                </td>
                <td>${job.started_at ? this.formatDate(job.started_at) : 'N/A'}</td>
                <td>${job.duration || 'N/A'}</td>
                <td>
                    <div class="action-buttons">
                        ${job.status === 'running' ? `<button class="btn btn-sm btn-warning" onclick="dataManager.cancelJob(${job.id})">Cancel</button>` : ''}
                        <button class="btn btn-sm btn-secondary" onclick="dataManager.viewJobDetails(${job.id})">Details</button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    async loadDatabaseInfo() {
        try {
            const api = new AdminAPI();
            const dbInfo = await api.getDatabaseInfo();
            this.renderDatabaseInfo(dbInfo);
        } catch (error) {
            console.error('Error loading database info:', error);
            this.showError('Failed to load database information');
        }
    }

    renderDatabaseInfo(dbInfo) {
        // Update database stats
        const stats = document.querySelectorAll('.db-stat');
        stats.forEach(stat => {
            const label = stat.querySelector('.label').textContent;
            const value = stat.querySelector('.value');
            
            switch(label) {
                case 'Database Size:':
                    value.textContent = dbInfo.database_size || 'N/A';
                    break;
                case 'Tables:':
                    value.textContent = dbInfo.table_count || 0;
                    break;
                case 'Indexes:':
                    value.textContent = dbInfo.index_count || 0;
                    break;
                case 'Connections:':
                    value.textContent = `${dbInfo.active_connections || 0}/${dbInfo.max_connections || 100}`;
                    break;
            }
        });

        // Update table information
        const tbody = document.getElementById('dbTablesTableBody');
        tbody.innerHTML = '';

        if (dbInfo.tables && dbInfo.tables.length > 0) {
            dbInfo.tables.forEach(table => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${table.name}</td>
                    <td>${table.row_count || 0}</td>
                    <td>${table.size || 'N/A'}</td>
                    <td>${table.last_updated ? this.formatDate(table.last_updated) : 'N/A'}</td>
                `;
                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center">No table information available</td></tr>';
        }
    }

    async loadPipelineStatus() {
        try {
            const api = new AdminAPI();
            const status = await api.getPipelineStatus();
            this.renderPipelineStatus(status);
        } catch (error) {
            console.error('Error loading pipeline status:', error);
            this.showError('Failed to load pipeline status');
        }
    }

    renderPipelineStatus(status) {
        const steps = document.querySelectorAll('.pipeline-step');
        steps.forEach((step, index) => {
            const statusElement = step.querySelector('.step-status');
            if (statusElement && status.steps && status.steps[index]) {
                const stepStatus = status.steps[index];
                statusElement.textContent = stepStatus.status;
                statusElement.className = `step-status ${stepStatus.status.toLowerCase()}`;
            }
        });
    }

    showDataSourceModal() {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Add Data Source</h3>
                    <button class="modal-close" onclick="this.closest('.modal').remove()">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="dataSourceForm">
                        <div class="form-group">
                            <label for="sourceName">Source Name</label>
                            <input type="text" id="sourceName" name="name" required>
                        </div>
                        <div class="form-group">
                            <label for="sourceType">Source Type</label>
                            <select id="sourceType" name="source_type" required>
                                <option value="api">REST API</option>
                                <option value="database">Database</option>
                                <option value="file">File Feed</option>
                                <option value="webhook">Webhook</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="endpointUrl">Endpoint URL</label>
                            <input type="url" id="endpointUrl" name="endpoint_url">
                        </div>
                        <div class="form-group">
                            <label for="apiKey">API Key</label>
                            <input type="password" id="apiKey" name="api_key">
                        </div>
                        <div class="form-group">
                            <label for="syncFrequency">Sync Frequency (seconds)</label>
                            <input type="number" id="syncFrequency" name="sync_frequency" value="3600">
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="this.closest('.modal').remove()">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="dataManager.createDataSource()">Create Source</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    async createDataSource() {
        try {
            const form = document.getElementById('dataSourceForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            
            const api = new AdminAPI();
            await api.createDataSource(data);
            this.showSuccess('Data source created successfully');
            document.querySelector('.modal').remove();
            this.loadDataSources();
        } catch (error) {
            console.error('Error creating data source:', error);
            this.showError('Failed to create data source');
        }
    }

    async editDataSource(id) {
        try {
            const api = new AdminAPI();
            const source = await api.getDataSource(id);
            // Show edit modal with pre-filled data
            this.showDataSourceModal(source);
        } catch (error) {
            console.error('Error loading data source:', error);
            this.showError('Failed to load data source');
        }
    }

    async syncDataSource(id) {
        try {
            const api = new AdminAPI();
            await api.syncDataSource(id);
            this.showSuccess('Data source sync started');
            this.loadDataSources();
        } catch (error) {
            console.error('Error syncing data source:', error);
            this.showError('Failed to sync data source');
        }
    }

    async removeDataSource(id) {
        if (!confirm('Are you sure you want to remove this data source?')) {
            return;
        }
        
        try {
            const api = new AdminAPI();
            await api.removeDataSource(id);
            this.showSuccess('Data source removed');
            this.loadDataSources();
        } catch (error) {
            console.error('Error removing data source:', error);
            this.showError('Failed to remove data source');
        }
    }

    async runQualityCheck() {
        try {
            const api = new AdminAPI();
            await api.runQualityCheck();
            this.showSuccess('Quality check started');
            this.loadQualityMetrics();
        } catch (error) {
            console.error('Error running quality check:', error);
            this.showError('Failed to run quality check');
        }
    }

    async backupDatabase() {
        try {
            const api = new AdminAPI();
            const response = await api.backupDatabase();
            this.showSuccess('Database backup started');
            
            if (response.download_url) {
                window.open(response.download_url, '_blank');
            }
        } catch (error) {
            console.error('Error backing up database:', error);
            this.showError('Failed to backup database');
        }
    }

    async optimizeDatabase() {
        if (!confirm('Are you sure you want to optimize the database? This may take some time.')) {
            return;
        }
        
        try {
            const api = new AdminAPI();
            await api.optimizeDatabase();
            this.showSuccess('Database optimization started');
        } catch (error) {
            console.error('Error optimizing database:', error);
            this.showError('Failed to optimize database');
        }
    }

    async runPipeline() {
        try {
            const api = new AdminAPI();
            await api.runPipeline();
            this.showSuccess('Data pipeline started');
            this.loadPipelineStatus();
        } catch (error) {
            console.error('Error running pipeline:', error);
            this.showError('Failed to run data pipeline');
        }
    }

    getQualityClass(score) {
        if (score >= 90) return 'good';
        if (score >= 70) return 'warning';
        return 'error';
    }

    formatDate(dateString) {
        return new Date(dateString).toLocaleString();
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

// Initialize data manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dataManager = new DataManager();
});
