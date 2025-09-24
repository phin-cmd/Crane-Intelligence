# Crane Intelligence Admin Panel - Technical Specifications (Final)

## 🗄️ **8. Data Management - Technical Specifications**

### **Layout Structure**
```html
<div class="data-management">
  <div class="data-header">
    <h1 class="page-title">DATA MANAGEMENT</h1>
  </div>

  <!-- External Data Sources -->
  <div class="data-sources-section">
    <h2 class="section-title">External Data Sources</h2>
    <div class="sources-grid">
      <div class="source-card source-connected">
        <div class="source-header">
          <h3 class="source-name">Equipment Watch</h3>
          <div class="source-status">
            <span class="status-indicator status-connected"></span>
            <span class="status-text">Connected</span>
          </div>
        </div>
        <div class="source-details">
          <div class="detail-item">
            <span class="detail-label">Last Sync</span>
            <span class="detail-value">2 minutes ago</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Records</span>
            <span class="detail-value">45,230</span>
          </div>
        </div>
        <div class="source-actions">
          <button class="btn btn-secondary btn-sm">Configure</button>
          <button class="btn btn-primary btn-sm">Sync Now</button>
        </div>
      </div>

      <div class="source-card source-active">
        <div class="source-header">
          <h3 class="source-name">Ritchie Bros</h3>
          <div class="source-status">
            <span class="status-indicator status-active"></span>
            <span class="status-text">Active</span>
          </div>
        </div>
        <div class="source-details">
          <div class="detail-item">
            <span class="detail-label">Last Sync</span>
            <span class="detail-value">15 minutes ago</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Records</span>
            <span class="detail-value">32,150</span>
          </div>
        </div>
        <div class="source-actions">
          <button class="btn btn-secondary btn-sm">Configure</button>
          <button class="btn btn-primary btn-sm">Sync Now</button>
        </div>
      </div>

      <div class="source-card source-syncing">
        <div class="source-header">
          <h3 class="source-name">IronPlanet</h3>
          <div class="source-status">
            <span class="status-indicator status-syncing"></span>
            <span class="status-text">Syncing</span>
          </div>
        </div>
        <div class="source-details">
          <div class="detail-item">
            <span class="detail-label">Progress</span>
            <span class="detail-value">67%</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">ETA</span>
            <span class="detail-value">5 minutes</span>
          </div>
        </div>
        <div class="source-actions">
          <button class="btn btn-secondary btn-sm">Configure</button>
          <button class="btn btn-danger btn-sm">Cancel</button>
        </div>
      </div>

      <div class="source-card source-error">
        <div class="source-header">
          <h3 class="source-name">MachineryTrader</h3>
          <div class="source-status">
            <span class="status-indicator status-error"></span>
            <span class="status-text">Error</span>
          </div>
        </div>
        <div class="source-details">
          <div class="detail-item">
            <span class="detail-label">Last Attempt</span>
            <span class="detail-value">1 hour ago</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Error</span>
            <span class="detail-value">API Timeout</span>
          </div>
        </div>
        <div class="source-actions">
          <button class="btn btn-secondary btn-sm">Configure</button>
          <button class="btn btn-warning btn-sm">Retry</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Data Quality Monitoring -->
  <div class="data-quality-section">
    <h2 class="section-title">DATA QUALITY</h2>
    <div class="quality-grid">
      <div class="quality-metric">
        <div class="metric-header">
          <h3 class="metric-name">Data Accuracy</h3>
          <span class="metric-value">94%</span>
        </div>
        <div class="metric-bar">
          <div class="metric-progress" style="width: 94%; background: var(--accent-green);"></div>
        </div>
      </div>

      <div class="quality-metric">
        <div class="metric-header">
          <h3 class="metric-name">Completeness</h3>
          <span class="metric-value">87%</span>
        </div>
        <div class="metric-bar">
          <div class="metric-progress" style="width: 87%; background: var(--accent-orange);"></div>
        </div>
      </div>

      <div class="quality-metric">
        <div class="metric-header">
          <h3 class="metric-name">Freshness</h3>
          <span class="metric-value">92%</span>
        </div>
        <div class="metric-bar">
          <div class="metric-progress" style="width: 92%; background: var(--accent-green);"></div>
        </div>
      </div>

      <div class="quality-metric">
        <div class="metric-header">
          <h3 class="metric-name">Consistency</h3>
          <span class="metric-value">89%</span>
        </div>
        <div class="metric-bar">
          <div class="metric-progress" style="width: 89%; background: var(--accent-orange);"></div>
        </div>
      </div>
    </div>
  </div>

  <!-- Background Jobs and Database Administration -->
  <div class="data-operations">
    <div class="background-jobs">
      <h2 class="section-title">BACKGROUND JOBS</h2>
      
      <div class="jobs-section">
        <div class="jobs-column">
          <h3 class="column-title">Active Tasks</h3>
          <div class="job-list">
            <div class="job-item">
              <div class="job-icon">📄</div>
              <div class="job-details">
                <span class="job-name">Data Import</span>
                <div class="job-progress">
                  <div class="progress-bar">
                    <div class="progress-fill" style="width: 65%;"></div>
                  </div>
                  <span class="progress-text">65%</span>
                </div>
              </div>
            </div>

            <div class="job-item">
              <div class="job-icon">🔄</div>
              <div class="job-details">
                <span class="job-name">Sync Operation</span>
                <div class="job-progress">
                  <div class="progress-bar">
                    <div class="progress-fill" style="width: 32%;"></div>
                  </div>
                  <span class="progress-text">32%</span>
                </div>
              </div>
            </div>
          </div>

          <div class="queue-status">
            <h4 class="queue-title">Queue Status</h4>
            <p class="queue-info">85 jobs pending</p>
          </div>
        </div>

        <div class="jobs-column">
          <h3 class="column-title">Scheduled</h3>
          <div class="scheduled-list">
            <div class="scheduled-item">
              <span class="scheduled-name">Data Export</span>
              <span class="scheduled-time">Daily at 2:00 AM</span>
            </div>
            <div class="scheduled-item">
              <span class="scheduled-name">Cleanup Operation</span>
              <span class="scheduled-time">Weekly on Sunday</span>
            </div>
            <div class="scheduled-item">
              <span class="scheduled-name">Queue pending</span>
              <span class="scheduled-time">Every 15 minutes</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="database-admin">
      <h2 class="section-title">DATABASE ADMINISTRATION</h2>
      
      <div class="db-grid">
        <div class="db-card">
          <h3 class="db-title">Performance Metrics</h3>
          <div class="db-metrics">
            <div class="db-metric">
              <span class="db-metric-label">Query Response Time</span>
              <span class="db-metric-value">45ms</span>
            </div>
            <div class="db-metric">
              <span class="db-metric-label">Active Connections</span>
              <span class="db-metric-value">23/100</span>
            </div>
            <div class="db-metric">
              <span class="db-metric-label">Cache Hit Ratio</span>
              <span class="db-metric-value">94.2%</span>
            </div>
          </div>
        </div>

        <div class="db-card">
          <h3 class="db-title">Query Optimization</h3>
          <div class="optimization-status">
            <span class="optimization-label">Optimization Enabled</span>
            <div class="optimization-progress">
              <div class="progress-bar">
                <div class="progress-fill" style="width: 100%; background: var(--accent-green);"></div>
              </div>
            </div>
          </div>
        </div>

        <div class="db-card">
          <h3 class="db-title">Backup Status</h3>
          <div class="backup-info">
            <div class="backup-item">
              <span class="backup-label">Last Backup</span>
              <span class="backup-value">2 hours ago</span>
            </div>
            <div class="backup-item">
              <span class="backup-label">Progress</span>
              <span class="backup-value">62%</span>
            </div>
            <div class="backup-progress">
              <div class="progress-bar">
                <div class="progress-fill" style="width: 62%; background: var(--accent-blue);"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
```

### **CSS Specifications**
```css
.data-management {
  padding: var(--space-6);
  background: var(--bg-primary);
  min-height: 100vh;
}

.data-header {
  margin-bottom: var(--space-8);
}

.page-title {
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  color: var(--accent-yellow);
  margin: 0;
  letter-spacing: 0.05em;
}

.section-title {
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  color: var(--accent-yellow);
  margin: 0 0 var(--space-6) 0;
  letter-spacing: 0.05em;
}

/* Data Sources Section */
.data-sources-section {
  margin-bottom: var(--space-8);
}

.sources-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-6);
}

.source-card {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  padding: var(--space-6);
  transition: transform 0.2s ease;
}

.source-card:hover {
  transform: translateY(-2px);
}

.source-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.source-name {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0;
}

.source-status {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: var(--radius-full);
}

.status-connected {
  background: var(--accent-green);
}

.status-active {
  background: var(--accent-green);
}

.status-syncing {
  background: var(--accent-blue);
  animation: pulse 2s infinite;
}

.status-error {
  background: var(--accent-red);
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.status-text {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
  text-transform: uppercase;
}

.source-details {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  margin-bottom: var(--space-4);
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-label {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.detail-value {
  font-size: var(--text-sm);
  color: var(--text-primary);
  font-weight: var(--font-medium);
}

.source-actions {
  display: flex;
  gap: var(--space-2);
}

/* Data Quality Section */
.data-quality-section {
  margin-bottom: var(--space-8);
}

.quality-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-6);
}

.quality-metric {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  padding: var(--space-6);
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.metric-name {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0;
}

.metric-value {
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  font-family: var(--font-mono);
}

.metric-bar {
  width: 100%;
  height: 8px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.metric-progress {
  height: 100%;
  border-radius: var(--radius-sm);
  transition: width 0.3s ease;
}

/* Data Operations */
.data-operations {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-8);
}

/* Background Jobs */
.background-jobs {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  padding: var(--space-6);
}

.jobs-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-6);
}

.jobs-column {
  display: flex;
  flex-direction: column;
}

.column-title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-4) 0;
}

.job-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  margin-bottom: var(--space-6);
}

.job-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
}

.job-icon {
  font-size: var(--text-lg);
}

.job-details {
  flex: 1;
}

.job-name {
  display: block;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-primary);
  margin-bottom: var(--space-2);
}

.job-progress {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: var(--bg-primary);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--accent-blue);
  border-radius: var(--radius-sm);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  font-weight: var(--font-medium);
  min-width: 30px;
}

.queue-status {
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  padding: var(--space-4);
}

.queue-title {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-2) 0;
}

.queue-info {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
}

.scheduled-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.scheduled-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  padding: var(--space-3);
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
}

.scheduled-name {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-primary);
}

.scheduled-time {
  font-size: var(--text-xs);
  color: var(--text-secondary);
}

/* Database Administration */
.database-admin {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  padding: var(--space-6);
}

.db-grid {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.db-card {
  background: var(--bg-tertiary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  padding: var(--space-5);
}

.db-title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-4) 0;
}

.db-metrics {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.db-metric {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.db-metric-label {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.db-metric-value {
  font-size: var(--text-sm);
  color: var(--text-primary);
  font-weight: var(--font-medium);
  font-family: var(--font-mono);
}

.optimization-status {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.optimization-label {
  font-size: var(--text-sm);
  color: var(--text-primary);
  font-weight: var(--font-medium);
}

.optimization-progress {
  display: flex;
  align-items: center;
}

.backup-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.backup-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.backup-label {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.backup-value {
  font-size: var(--text-sm);
  color: var(--text-primary);
  font-weight: var(--font-medium);
}

.backup-progress {
  margin-top: var(--space-2);
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
}

.btn-primary {
  background: var(--accent-blue);
  color: var(--text-primary);
}

.btn-primary:hover {
  background: #0056b3;
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  border: 1px solid var(--border-primary);
}

.btn-secondary:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.btn-danger {
  background: var(--accent-red);
  color: var(--text-primary);
}

.btn-danger:hover {
  background: #c82333;
}

.btn-warning {
  background: var(--accent-orange);
  color: var(--text-primary);
}

.btn-warning:hover {
  background: #e0a800;
}

.btn-sm {
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-xs);
}

/* Responsive Design */
@media (max-width: 1024px) {
  .sources-grid {
    grid-template-columns: 1fr;
  }
  
  .quality-grid {
    grid-template-columns: 1fr;
  }
  
  .data-operations {
    grid-template-columns: 1fr;
  }
  
  .jobs-section {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .source-header {
    flex-direction: column;
    gap: var(--space-2);
    align-items: flex-start;
  }
  
  .source-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .metric-header {
    flex-direction: column;
    gap: var(--space-2);
    align-items: flex-start;
  }
}
```

---

## 📱 **9. Mobile Responsive Design - Technical Specifications**

### **Layout Structure**
```html
<div class="mobile-admin">
  <!-- Mobile Header -->
  <header class="mobile-header">
    <button class="mobile-menu-toggle">
      <span class="hamburger-line"></span>
      <span class="hamburger-line"></span>
      <span class="hamburger-line"></span>
    </button>
    <div class="mobile-logo">
      <img src="crane-logo.svg" alt="Crane Intelligence" />
    </div>
    <button class="mobile-notifications">
      <span class="notification-icon">🔔</span>
      <span class="notification-badge">3</span>
    </button>
  </header>

  <!-- Mobile Navigation Overlay -->
  <nav class="mobile-nav-overlay">
    <div class="mobile-nav-content">
      <div class="mobile-nav-header">
        <div class="mobile-user-info">
          <div class="mobile-avatar"></div>
          <span class="mobile-username">Admin</span>
        </div>
        <button class="mobile-nav-close">✕</button>
      </div>
      
      <div class="mobile-nav-menu">
        <a href="#" class="mobile-nav-item active">
          <span class="mobile-nav-icon">🏠</span>
          <span class="mobile-nav-label">Dashboard</span>
        </a>
        <a href="#" class="mobile-nav-item">
          <span class="mobile-nav-icon">👥</span>
          <span class="mobile-nav-label">Users</span>
        </a>
        <a href="#" class="mobile-nav-item">
          <span class="mobile-nav-icon">📝</span>
          <span class="mobile-nav-label">Content</span>
        </a>
        <a href="#" class="mobile-nav-item">
          <span class="mobile-nav-icon">📊</span>
          <span class="mobile-nav-label">Analytics</span>
        </a>
        <a href="#" class="mobile-nav-item">
          <span class="mobile-nav-icon">⚙️</span>
          <span class="mobile-nav-label">Settings</span>
        </a>
        <a href="#" class="mobile-nav-item">
          <span class="mobile-nav-icon">🔒</span>
          <span class="mobile-nav-label">Security</span>
        </a>
        <a href="#" class="mobile-nav-item">
          <span class="mobile-nav-icon">🗄️</span>
          <span class="mobile-nav-label">Data</span>
        </a>
      </div>
    </div>
  </nav>

  <!-- Mobile Main Content -->
  <main class="mobile-main">
    <!-- Mobile Dashboard -->
    <div class="mobile-dashboard">
      <!-- Mobile Metrics -->
      <div class="mobile-metrics">
        <div class="mobile-metric-card">
          <h3 class="mobile-metric-title">ACTIVE USERS</h3>
          <div class="mobile-metric-value">1,572</div>
        </div>
        
        <div class="mobile-metric-card">
          <h3 class="mobile-metric-title">REVENUE</h3>
          <div class="mobile-metric-value">$28,430</div>
        </div>
        
        <div class="mobile-metric-card">
          <h3 class="mobile-metric-title">SYSTEM HEALTH</h3>
          <div class="mobile-metric-status">
            <div class="mobile-health-indicator"></div>
            <span class="mobile-health-text">Excellent</span>
          </div>
        </div>
      </div>

      <!-- Mobile Charts -->
      <div class="mobile-charts">
        <div class="mobile-chart-card">
          <h3 class="mobile-chart-title">User Activity</h3>
          <div class="mobile-chart-container">
            <canvas id="mobileUserActivityChart"></canvas>
          </div>
        </div>
        
        <div class="mobile-chart-card">
          <h3 class="mobile-chart-title">Revenue</h3>
          <div class="mobile-chart-container">
            <canvas id="mobileRevenueChart"></canvas>
          </div>
        </div>
      </div>

      <!-- Mobile Quick Actions -->
      <div class="mobile-quick-actions">
        <h3 class="mobile-section-title">Quick Actions</h3>
        <div class="mobile-actions-grid">
          <button class="mobile-action-btn">
            <span class="mobile-action-icon">👥</span>
            <span class="mobile-action-label">Add User</span>
          </button>
          <button class="mobile-action-btn">
            <span class="mobile-action-icon">📝</span>
            <span class="mobile-action-label">New Post</span>
          </button>
          <button class="mobile-action-btn">
            <span class="mobile-action-icon">📊</span>
            <span class="mobile-action-label">Reports</span>
          </button>
          <button class="mobile-action-btn">
            <span class="mobile-action-icon">⚙️</span>
            <span class="mobile-action-label">Settings</span>
          </button>
        </div>
      </div>
    </div>
  </main>

  <!-- Mobile Bottom Navigation -->
  <nav class="mobile-bottom-nav">
    <a href="#" class="mobile-bottom-item active">
      <span class="mobile-bottom-icon">🏠</span>
      <span class="mobile-bottom-label">Home</span>
    </a>
    <a href="#" class="mobile-bottom-item">
      <span class="mobile-bottom-icon">👥</span>
      <span class="mobile-bottom-label">Users</span>
    </a>
    <a href="#" class="mobile-bottom-item">
      <span class="mobile-bottom-icon">📊</span>
      <span class="mobile-bottom-label">Analytics</span>
    </a>
    <a href="#" class="mobile-bottom-item">
      <span class="mobile-bottom-icon">⚙️</span>
      <span class="mobile-bottom-label">Settings</span>
    </a>
  </nav>
</div>
```

### **CSS Specifications**
```css
/* Mobile-First Responsive Design */
.mobile-admin {
  display: none;
  background: var(--bg-primary);
  min-height: 100vh;
  font-family: var(--font-primary);
}

/* Mobile Header */
.mobile-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-primary);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-4);
  z-index: 1000;
}

.mobile-menu-toggle {
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--space-2);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.hamburger-line {
  width: 24px;
  height: 3px;
  background: var(--text-primary);
  border-radius: var(--radius-sm);
  transition: all 0.3s ease;
}

.mobile-menu-toggle.active .hamburger-line:nth-child(1) {
  transform: rotate(45deg) translate(6px, 6px);
}

.mobile-menu-toggle.active .hamburger-line:nth-child(2) {
  opacity: 0;
}

.mobile-menu-toggle.active .hamburger-line:nth-child(3) {
  transform: rotate(-45deg) translate(6px, -6px);
}

.mobile-logo img {
  height: 32px;
  width: auto;
}

.mobile-notifications {
  position: relative;
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: var(--text-lg);
  padding: var(--space-2);
}

.notification-badge {
  position: absolute;
  top: 0;
  right: 0;
  background: var(--accent-red);
  color: var(--text-primary);
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
  padding: 2px 6px;
  border-radius: var(--radius-full);
  min-width: 18px;
  text-align: center;
}

/* Mobile Navigation Overlay */
.mobile-nav-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  z-index: 2000;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
}

.mobile-nav-overlay.active {
  opacity: 1;
  visibility: visible;
}

.mobile-nav-content {
  position: absolute;
  top: 0;
  left: 0;
  width: 280px;
  height: 100%;
  background: var(--bg-secondary);
  transform: translateX(-100%);
  transition: transform 0.3s ease;
}

.mobile-nav-overlay.active .mobile-nav-content {
  transform: translateX(0);
}

.mobile-nav-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-6) var(--space-4);
  border-bottom: 1px solid var(--border-primary);
}

.mobile-user-info {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.mobile-avatar {
  width: 40px;
  height: 40px;
  background: var(--accent-blue);
  border-radius: var(--radius-full);
}

.mobile-username {
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  color: var(--text-primary);
}

.mobile-nav-close {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: var(--text-xl);
  padding: var(--space-2);
}

.mobile-nav-menu {
  padding: var(--space-4) 0;
}

.mobile-nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-4) var(--space-6);
  color: var(--text-secondary);
  text-decoration: none;
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  transition: all 0.2s ease;
}

.mobile-nav-item:hover,
.mobile-nav-item.active {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.mobile-nav-icon {
  font-size: var(--text-xl);
  width: 24px;
  text-align: center;
}

/* Mobile Main Content */
.mobile-main {
  padding-top: 60px;
  padding-bottom: 80px;
  padding-left: var(--space-4);
  padding-right: var(--space-4);
}

.mobile-dashboard {
  padding: var(--space-6) 0;
}

/* Mobile Metrics */
.mobile-metrics {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  margin-bottom: var(--space-8);
}

.mobile-metric-card {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  padding: var(--space-6);
  text-align: center;
}

.mobile-metric-title {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
  margin: 0 0 var(--space-3) 0;
  letter-spacing: 0.05em;
}

.mobile-metric-value {
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  font-family: var(--font-mono);
}

.mobile-metric-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
}

.mobile-health-indicator {
  width: 12px;
  height: 12px;
  background: var(--accent-green);
  border-radius: var(--radius-full);
}

.mobile-health-text {
  font-size: var(--text-lg);
  font-weight: var(--font-medium);
  color: var(--accent-green);
}

/* Mobile Charts */
.mobile-charts {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
  margin-bottom: var(--space-8);
}

.mobile-chart-card {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  overflow: hidden;
}

.mobile-chart-title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0;
  padding: var(--space-4) var(--space-6);
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-primary);
}

.mobile-chart-container {
  padding: var(--space-4);
  height: 200px;
}

/* Mobile Quick Actions */
.mobile-quick-actions {
  margin-bottom: var(--space-8);
}

.mobile-section-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-4) 0;
}

.mobile-actions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-4);
}

.mobile-action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-6);
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.mobile-action-btn:hover {
  background: var(--bg-hover);
  transform: translateY(-2px);
}

.mobile-action-icon {
  font-size: var(--text-2xl);
}

.mobile-action-label {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
}

/* Mobile Bottom Navigation */
.mobile-bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 80px;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-primary);
  display: flex;
  z-index: 1000;
}

.mobile-bottom-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-1);
  color: var(--text-secondary);
  text-decoration: none;
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  transition: all 0.2s ease;
}

.mobile-bottom-item:hover,
.mobile-bottom-item.active {
  color: var(--accent-blue);
  background: rgba(0, 123, 255, 0.1);
}

.mobile-bottom-icon {
  font-size: var(--text-lg);
}

.mobile-bottom-label {
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Touch Interactions */
.mobile-action-btn,
.mobile-nav-item,
.mobile-bottom-item {
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}

/* Swipe Gestures */
.mobile-chart-container {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

/* Pull to Refresh */
.mobile-main {
  overscroll-behavior-y: contain;
}

/* Responsive Breakpoints */
@media (max-width: 768px) {
  .admin-layout {
    display: none;
  }
  
  .mobile-admin {
    display: block;
  }
}

@media (max-width: 480px) {
  .mobile-actions-grid {
    grid-template-columns: 1fr;
  }
  
  .mobile-nav-content {
    width: 100%;
  }
  
  .mobile-metric-card {
    padding: var(--space-4);
  }
  
  .mobile-metric-value {
    font-size: var(--text-2xl);
  }
}

/* Landscape Orientation */
@media (max-width: 768px) and (orientation: landscape) {
  .mobile-header {
    height: 50px;
  }
  
  .mobile-main {
    padding-top: 50px;
    padding-bottom: 60px;
  }
  
  .mobile-bottom-nav {
    height: 60px;
  }
  
  .mobile-metrics {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--space-3);
  }
  
  .mobile-charts {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-4);
  }
}

/* Dark Mode Support */
@media (prefers-color-scheme: dark) {
  .mobile-admin {
    color-scheme: dark;
  }
}

/* Reduced Motion */
@media (prefers-reduced-motion: reduce) {
  .mobile-nav-overlay,
  .mobile-nav-content,
  .hamburger-line,
  .mobile-action-btn {
    transition: none;
  }
}

/* High Contrast Mode */
@media (prefers-contrast: high) {
  .mobile-metric-card,
  .mobile-chart-card,
  .mobile-action-btn {
    border-width: 2px;
  }
}
```

### **JavaScript for Mobile Interactions**
```javascript
// Mobile Navigation Toggle
document.addEventListener('DOMContentLoaded', function() {
  const menuToggle = document.querySelector('.mobile-menu-toggle');
  const navOverlay = document.querySelector('.mobile-nav-overlay');
  const navClose = document.querySelector('.mobile-nav-close');

  function openNav() {
    navOverlay.classList.add('active');
    menuToggle.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeNav() {
    navOverlay.classList.remove('active');
    menuToggle.classList.remove('active');
    document.body.style.overflow = '';
  }

  menuToggle.addEventListener('click', openNav);
  navClose.addEventListener('click', closeNav);
  
  // Close nav when clicking overlay
  navOverlay.addEventListener('click', function(e) {
    if (e.target === navOverlay) {
      closeNav();
    }
  });

  // Touch gestures for navigation
  let startX = 0;
  let currentX = 0;
  let isDragging = false;

  document.addEventListener('touchstart', function(e) {
    startX = e.touches[0].clientX;
    isDragging = true;
  });

  document.addEventListener('touchmove', function(e) {
    if (!isDragging) return;
    currentX = e.touches[0].clientX;
  });

  document.addEventListener('touchend', function() {
    if (!isDragging) return;
    isDragging = false;
    
    const deltaX = currentX - startX;
    
    // Swipe right to open nav (from left edge)
    if (deltaX > 50 && startX < 50) {
      openNav();
    }
    
    // Swipe left to close nav
    if (deltaX < -50 && navOverlay.classList.contains('active')) {
      closeNav();
    }
  });

  // Mobile Charts
  const mobileUserActivityCtx = document.getElementById('mobileUserActivityChart');
  if (mobileUserActivityCtx) {
    new Chart(mobileUserActivityCtx.getContext('2d'), {
      type: 'line',
      data: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
        datasets: [{
          label: 'User Activity',
          data: [800, 950, 1100, 1300, 1450],
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
              color: '#404040'
            },
            ticks: {
              color: '#B0B0B0',
              font: {
                size: 10
              }
            }
          },
          y: {
            grid: {
              color: '#404040'
            },
            ticks: {
              color: '#B0B0B0',
              font: {
                size: 10
              }
            }
          }
        },
        interaction: {
          intersect: false,
          mode: 'index'
        }
      }
    });
  }

  const mobileRevenueCtx = document.getElementById('mobileRevenueChart');
  if (mobileRevenueCtx) {
    new Chart(mobileRevenueCtx.getContext('2d'), {
      type: 'bar',
      data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
        datasets: [{
          label: 'Revenue',
          data: [5000, 7000, 8500, 9200, 11000],
          backgroundColor: '#28A745',
          borderRadius: 4
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
              display: false
            },
            ticks: {
              color: '#B0B0B0',
              font: {
                size: 10
              }
            }
          },
          y: {
            grid: {
              color: '#404040'
            },
            ticks: {
              color: '#B0B0B0',
              font: {
                size: 10
              },
              callback: function(value) {
                return '$' + (value / 1000) + 'k';
              }
            }
          }
        }
      }
    });
  }

  // Pull to refresh functionality
  let startY = 0;
  let pullDistance = 0;
  const pullThreshold = 100;
  
  document.addEventListener('touchstart', function(e) {
    if (window.scrollY === 0) {
      startY = e.touches[0].clientY;
    }
  });
  
  document.addEventListener('touchmove', function(e) {
    if (window.scrollY === 0 && startY > 0) {
      pullDistance = e.touches[0].clientY - startY;
      if (pullDistance > 0) {
        e.preventDefault();
        // Add visual feedback for pull to refresh
        if (pullDistance > pullThreshold) {
          // Trigger refresh
          console.log('Refreshing...');
        }
      }
    }
  });
  
  document.addEventListener('touchend', function() {
    startY = 0;
    pullDistance = 0;
  });
});
```

This completes the comprehensive technical specifications for all sections of the Crane Intelligence Admin Panel. The documentation includes exact measurements, colors, typography, layout structures, responsive design considerations, and interactive functionality that developers can use to build the admin panel exactly as designed.

## 📋 **Implementation Summary**

The complete technical specifications cover:

1. **Global Design System** - Colors, typography, spacing, and border radius
2. **Login Screen** - Authentication interface with security features
3. **Dashboard Overview** - Real-time metrics and interactive charts
4. **User Management** - Comprehensive user directory and permissions
5. **Content Management** - Multi-tab content system with media management
6. **Analytics & Reporting** - Professional analytics with export capabilities
7. **Platform Settings** - Configuration system with multiple categories
8. **Security & Access Control** - Enterprise-grade security features
9. **Data Management** - External integrations and quality monitoring
10. **Mobile Responsive** - Touch-optimized mobile interface

Each section includes complete HTML structure, CSS styling, and JavaScript functionality with exact specifications for colors, measurements, typography, and interactions.
