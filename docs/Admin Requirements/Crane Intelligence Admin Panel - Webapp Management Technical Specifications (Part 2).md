# Crane Intelligence Admin Panel - Webapp Management Technical Specifications (Part 2)

## ⚙️ **12. Core Features Management - Technical Specifications**

### **Layout Structure**
```html
<div class="core-features-management">
  <div class="features-header">
    <h1 class="page-title">Core Features Management</h1>
    <div class="header-controls">
      <button class="btn btn-secondary">
        <span class="btn-icon">📋</span>
        Feature Audit
      </button>
      <button class="btn btn-primary">
        <span class="btn-icon">🚀</span>
        Deploy Changes
      </button>
    </div>
  </div>

  <!-- Feature Flags Dashboard -->
  <div class="feature-flags-section">
    <h2 class="section-title">FEATURE FLAGS</h2>
    <div class="flags-table-container">
      <table class="flags-table">
        <thead>
          <tr>
            <th>Feature</th>
            <th>Enabled</th>
            <th>A/B Test</th>
            <th>% Rollout</th>
            <th>Adoption Rate</th>
            <th>Performance</th>
          </tr>
        </thead>
        <tbody>
          <tr class="flag-row">
            <td class="feature-cell">
              <span class="feature-name">Feature 1</span>
            </td>
            <td class="enabled-cell">
              <label class="toggle-switch">
                <input type="checkbox" checked>
                <span class="toggle-slider"></span>
              </label>
            </td>
            <td class="ab-test-cell">
              <label class="toggle-switch toggle-disabled">
                <input type="checkbox">
                <span class="toggle-slider"></span>
              </label>
            </td>
            <td class="rollout-cell">
              <div class="rollout-slider-container">
                <input type="range" class="rollout-slider" min="0" max="100" value="0">
                <span class="rollout-value">0%</span>
              </div>
            </td>
            <td class="adoption-cell">
              <span class="adoption-rate">10.2%</span>
              <span class="adoption-trend trend-positive">+0.6%</span>
            </td>
            <td class="performance-cell">
              <span class="performance-trend trend-positive">+0.6%</span>
            </td>
          </tr>
          
          <tr class="flag-row">
            <td class="feature-cell">
              <span class="feature-name">Feature 2</span>
            </td>
            <td class="enabled-cell">
              <label class="toggle-switch">
                <input type="checkbox" checked>
                <span class="toggle-slider"></span>
              </label>
            </td>
            <td class="ab-test-cell">
              <label class="toggle-switch toggle-disabled">
                <input type="checkbox">
                <span class="toggle-slider"></span>
              </label>
            </td>
            <td class="rollout-cell">
              <div class="rollout-slider-container">
                <input type="range" class="rollout-slider" min="0" max="100" value="2">
                <span class="rollout-value">0.2%</span>
              </div>
            </td>
            <td class="adoption-cell">
              <span class="adoption-rate">15.0%</span>
              <span class="adoption-trend trend-negative">-0.2%</span>
            </td>
            <td class="performance-cell">
              <span class="performance-trend trend-negative">-0.2%</span>
            </td>
          </tr>
          
          <tr class="flag-row">
            <td class="feature-cell">
              <span class="feature-name">Feature 3</span>
            </td>
            <td class="enabled-cell">
              <label class="toggle-switch">
                <input type="checkbox" checked>
                <span class="toggle-slider"></span>
              </label>
            </td>
            <td class="ab-test-cell">
              <label class="toggle-switch toggle-disabled">
                <input type="checkbox">
                <span class="toggle-slider"></span>
              </label>
            </td>
            <td class="rollout-cell">
              <div class="rollout-slider-container">
                <input type="range" class="rollout-slider" min="0" max="100" value="75">
                <span class="rollout-value">75%</span>
              </div>
            </td>
            <td class="adoption-cell">
              <span class="adoption-rate">30.5%</span>
              <span class="adoption-trend trend-positive">+0.4%</span>
            </td>
            <td class="performance-cell">
              <span class="performance-trend trend-positive">+0.4%</span>
            </td>
          </tr>
          
          <tr class="flag-row">
            <td class="feature-cell">
              <span class="feature-name">Feature 4</span>
            </td>
            <td class="enabled-cell">
              <label class="toggle-switch">
                <input type="checkbox" checked>
                <span class="toggle-slider"></span>
              </label>
            </td>
            <td class="ab-test-cell">
              <label class="toggle-switch toggle-disabled">
                <input type="checkbox">
                <span class="toggle-slider"></span>
              </label>
            </td>
            <td class="rollout-cell">
              <div class="rollout-slider-container">
                <input type="range" class="rollout-slider" min="0" max="100" value="50">
                <span class="rollout-value">50%</span>
              </div>
            </td>
            <td class="adoption-cell">
              <span class="adoption-rate">10.0%</span>
              <span class="adoption-trend trend-positive">+0.4%</span>
            </td>
            <td class="performance-cell">
              <span class="performance-trend trend-positive">+0.4%</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- Crane Valuation Configuration -->
  <div class="crane-valuation-section">
    <h2 class="section-title">CRANE VALUATION CONFIGURATION</h2>
    <div class="valuation-grid">
      <div class="valuation-card">
        <h3 class="valuation-title">Crane Valuation Settings</h3>
        <div class="valuation-form">
          <div class="form-group">
            <label class="form-label">Valuation Method</label>
            <select class="form-select">
              <option>Market Comparison</option>
              <option>Cost Approach</option>
              <option>Income Approach</option>
              <option>Hybrid Method</option>
            </select>
          </div>
          
          <div class="form-group">
            <label class="form-label">Risk Premium</label>
            <div class="input-with-suffix">
              <input type="number" class="form-input" value="5.0" step="0.1">
              <span class="input-suffix">%</span>
            </div>
          </div>
          
          <div class="form-group">
            <label class="form-label">Depreciation Model</label>
            <select class="form-select">
              <option>Straight Line</option>
              <option>Declining Balance</option>
              <option>Sum of Years</option>
              <option>Custom</option>
            </select>
          </div>
        </div>
      </div>
      
      <div class="valuation-card">
        <h3 class="valuation-title">Market Data Sources</h3>
        <div class="data-sources-form">
          <div class="form-group">
            <label class="form-label">Primary Provider</label>
            <select class="form-select">
              <option>Provider A</option>
              <option>Equipment Watch</option>
              <option>Ritchie Bros</option>
              <option>IronPlanet</option>
            </select>
          </div>
          
          <div class="form-group">
            <label class="form-label">Update Frequency</label>
            <select class="form-select">
              <option>Real-time</option>
              <option>Hourly</option>
              <option>Daily</option>
              <option>Weekly</option>
            </select>
          </div>
          
          <div class="form-group">
            <label class="form-label">Data Quality Threshold</label>
            <div class="input-with-suffix">
              <input type="number" class="form-input" value="85" min="0" max="100">
              <span class="input-suffix">%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Pricing Models Configuration -->
    <div class="pricing-models-section">
      <div class="models-tabs">
        <button class="tab-btn tab-active">Pricing Models</button>
        <button class="tab-btn">Calculation Parameters</button>
      </div>
      
      <div class="tab-content tab-content-active">
        <div class="pricing-grid">
          <div class="pricing-card">
            <h4 class="pricing-title">Model Type</h4>
            <select class="form-select">
              <option>Black-Scholes</option>
              <option>Monte Carlo</option>
              <option>Binomial Tree</option>
              <option>Custom Model</option>
            </select>
          </div>
          
          <div class="pricing-card">
            <h4 class="pricing-title">Volatility</h4>
            <div class="input-with-suffix">
              <input type="number" class="form-input" value="0.2" step="0.01">
              <span class="input-suffix">σ</span>
            </div>
          </div>
          
          <div class="pricing-card">
            <h4 class="pricing-title">Risk-Free Rate</h4>
            <div class="input-with-suffix">
              <input type="number" class="form-input" value="3.5" step="0.1">
              <span class="input-suffix">%</span>
            </div>
          </div>
          
          <div class="pricing-card">
            <h4 class="pricing-title">Time to Maturity</h4>
            <div class="input-with-suffix">
              <input type="number" class="form-input" value="1.0" step="0.1">
              <span class="input-suffix">years</span>
            </div>
          </div>
        </div>
        
        <div class="adjustments-section">
          <label class="checkbox-label">
            <input type="checkbox" class="checkbox-input" checked>
            <span class="checkbox-custom"></span>
            <span class="checkbox-text">Enable Adjustments</span>
          </label>
        </div>
      </div>
    </div>
  </div>

  <!-- Feature Performance Monitoring -->
  <div class="feature-performance-section">
    <h2 class="section-title">FEATURE PERFORMANCE</h2>
    <div class="performance-grid">
      <div class="performance-card">
        <h3 class="performance-title">Load Time (ms)</h3>
        <div class="performance-chart">
          <canvas id="loadTimeChart"></canvas>
        </div>
        <div class="performance-stats">
          <div class="stat-item">
            <span class="stat-label">Average</span>
            <span class="stat-value">245ms</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">P95</span>
            <span class="stat-value">450ms</span>
          </div>
        </div>
      </div>
      
      <div class="performance-card">
        <h3 class="performance-title">Error Rate (%)</h3>
        <div class="performance-chart">
          <canvas id="errorRateChart"></canvas>
        </div>
        <div class="performance-stats">
          <div class="stat-item">
            <span class="stat-label">Current</span>
            <span class="stat-value">0.12%</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Target</span>
            <span class="stat-value">&lt;0.5%</span>
          </div>
        </div>
      </div>
      
      <div class="performance-card">
        <h3 class="performance-title">User Satisfaction</h3>
        <div class="performance-chart">
          <canvas id="satisfactionChart"></canvas>
        </div>
        <div class="performance-stats">
          <div class="stat-item">
            <span class="stat-label">Score</span>
            <span class="stat-value">4.7/5</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Responses</span>
            <span class="stat-value">1,247</span>
          </div>
        </div>
      </div>
      
      <div class="performance-card">
        <h3 class="performance-title">Feature Health</h3>
        <div class="performance-chart">
          <canvas id="featureHealthChart"></canvas>
        </div>
        <div class="performance-stats">
          <div class="stat-item">
            <span class="stat-label">Overall</span>
            <span class="stat-value health-excellent">Excellent</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Uptime</span>
            <span class="stat-value">99.9%</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Feature Versioning -->
  <div class="feature-versioning-section">
    <h2 class="section-title">FEATURE VERSIONING</h2>
    <div class="versioning-container">
      <div class="version-timeline">
        <div class="version-item version-current">
          <div class="version-marker"></div>
          <div class="version-content">
            <h4 class="version-title">v2.1.0 (Current)</h4>
            <p class="version-description">Enhanced crane valuation algorithms with improved accuracy</p>
            <div class="version-meta">
              <span class="version-date">2024-04-15</span>
              <span class="version-status status-live">Live</span>
            </div>
          </div>
        </div>
        
        <div class="version-item">
          <div class="version-marker"></div>
          <div class="version-content">
            <h4 class="version-title">v2.0.5</h4>
            <p class="version-description">Bug fixes and performance improvements</p>
            <div class="version-meta">
              <span class="version-date">2024-04-01</span>
              <span class="version-status status-archived">Archived</span>
            </div>
          </div>
        </div>
        
        <div class="version-item">
          <div class="version-marker"></div>
          <div class="version-content">
            <h4 class="version-title">v2.0.0</h4>
            <p class="version-description">Major release with new dashboard and analytics</p>
            <div class="version-meta">
              <span class="version-date">2024-03-15</span>
              <span class="version-status status-archived">Archived</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="version-actions">
        <button class="btn btn-secondary">
          <span class="btn-icon">📋</span>
          View Changelog
        </button>
        <button class="btn btn-warning">
          <span class="btn-icon">↩️</span>
          Rollback
        </button>
        <button class="btn btn-primary">
          <span class="btn-icon">🚀</span>
          Deploy New Version
        </button>
      </div>
    </div>
  </div>
</div>
```

### **CSS Specifications for Activities Tracking**
```css
.activities-tracking {
  padding: var(--space-6);
  background: var(--bg-primary);
  min-height: 100vh;
}

.activities-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-8);
}

.page-title {
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin: 0;
  letter-spacing: 0.05em;
}

.header-controls {
  display: flex;
  gap: var(--space-3);
}

/* Activity Feed */
.activity-feed-section {
  margin-bottom: var(--space-8);
}

.feed-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-6);
}

.section-title {
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  color: var(--accent-yellow);
  margin: 0;
  letter-spacing: 0.05em;
}

.feed-filters {
  display: flex;
  gap: var(--space-3);
}

.filter-select {
  padding: var(--space-2) var(--space-3);
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: var(--text-sm);
}

.activity-feed-container {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  overflow: hidden;
}

.activity-table {
  width: 100%;
  border-collapse: collapse;
}

.activity-table th {
  padding: var(--space-3) var(--space-4);
  text-align: left;
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-primary);
}

.activity-table td {
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--border-primary);
  font-size: var(--text-sm);
}

.activity-row:hover {
  background: var(--bg-hover);
}

.time-cell {
  font-family: var(--font-mono);
  color: var(--text-secondary);
  font-size: var(--text-xs);
}

.user-cell {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.user-avatar {
  width: 24px;
  height: 24px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
  color: var(--text-primary);
}

.user-avatar-e { background: var(--accent-green); }
.user-avatar-j { background: var(--accent-blue); }
.user-avatar-d { background: var(--accent-orange); }
.user-avatar-o { background: var(--accent-purple); }

.user-name {
  font-weight: var(--font-medium);
  color: var(--text-primary);
  font-size: var(--text-sm);
}

.action-cell {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.action-indicator {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
}

.action-success { background: var(--accent-green); }
.action-info { background: var(--accent-blue); }
.action-warning { background: var(--accent-orange); }
.action-error { background: var(--accent-red); }

.action-text {
  font-weight: var(--font-medium);
  color: var(--text-primary);
}

.details-cell {
  color: var(--text-secondary);
  font-family: var(--font-mono);
  font-size: var(--text-xs);
}

/* Activity Analytics */
.activity-analytics-section {
  margin-bottom: var(--space-8);
}

.analytics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-6);
}

.analytics-card {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  padding: var(--space-6);
}

.analytics-title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-4) 0;
}

.feature-list,
.interaction-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.feature-item,
.interaction-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-3);
}

.feature-name,
.interaction-name {
  font-size: var(--text-sm);
  color: var(--text-primary);
  min-width: 80px;
}

.feature-bar,
.interaction-bar {
  flex: 1;
  height: 6px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.feature-progress,
.interaction-progress {
  height: 100%;
  background: var(--accent-yellow);
  border-radius: var(--radius-sm);
  transition: width 0.3s ease;
}

.usage-chart,
.performance-chart {
  height: 120px;
}

/* Activity Heatmap */
.activity-heatmap-section {
  margin-bottom: var(--space-8);
}

.heatmap-container {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  padding: var(--space-6);
}

.heatmap-grid {
  display: grid;
  grid-template-columns: auto 1fr;
  grid-template-rows: auto 1fr;
  gap: var(--space-2);
}

.heatmap-labels {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.day-label {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  padding: var(--space-1);
  text-align: center;
}

.heatmap-hours {
  display: flex;
  gap: var(--space-1);
}

.hour-label {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  padding: var(--space-1);
  text-align: center;
  min-width: 20px;
}

.heatmap-cells {
  display: grid;
  grid-template-columns: repeat(11, 1fr);
  grid-template-rows: repeat(5, 1fr);
  gap: 2px;
}

.heatmap-cell {
  width: 20px;
  height: 20px;
  border-radius: var(--radius-sm);
}

.heatmap-low { background: rgba(255, 193, 7, 0.2); }
.heatmap-medium { background: rgba(255, 193, 7, 0.5); }
.heatmap-high { background: rgba(255, 193, 7, 0.7); }
.heatmap-very-high { background: rgba(255, 193, 7, 1); }

/* Audit Trail */
.audit-trail-section {
  margin-bottom: var(--space-8);
}

.audit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-6);
}

.audit-controls {
  display: flex;
  gap: var(--space-2);
}

.audit-table-container {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  overflow: hidden;
  margin-bottom: var(--space-6);
}

.audit-table {
  width: 100%;
  border-collapse: collapse;
}

.audit-table th {
  padding: var(--space-3) var(--space-4);
  text-align: left;
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-primary);
}

.audit-table td {
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--border-primary);
  font-size: var(--text-sm);
}

.audit-row:hover {
  background: var(--bg-hover);
}

.timestamp-cell {
  font-family: var(--font-mono);
  color: var(--text-secondary);
  font-size: var(--text-xs);
}

.event-cell {
  font-weight: var(--font-medium);
  color: var(--text-primary);
}

.status-badge {
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  text-transform: uppercase;
}

.status-completed {
  background: rgba(40, 167, 69, 0.2);
  color: var(--accent-green);
}

.status-warning {
  background: rgba(255, 193, 7, 0.2);
  color: var(--accent-orange);
}

.status-exported {
  background: rgba(0, 123, 255, 0.2);
  color: var(--accent-blue);
}

/* Compliance Section */
.compliance-section {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  padding: var(--space-6);
}

.compliance-title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-4) 0;
}

.compliance-stats {
  display: flex;
  justify-content: space-between;
  gap: var(--space-6);
}

.compliance-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  text-align: center;
}

.compliance-label {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.compliance-status {
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  font-family: var(--font-mono);
}

.status-good {
  color: var(--accent-green);
}

.status-excellent {
  color: var(--accent-blue);
}
```

### **CSS Specifications for Core Features Management**
```css
.core-features-management {
  padding: var(--space-6);
  background: var(--bg-primary);
  min-height: 100vh;
}

.features-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-8);
}

/* Feature Flags */
.feature-flags-section {
  margin-bottom: var(--space-8);
}

.flags-table-container {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  overflow: hidden;
}

.flags-table {
  width: 100%;
  border-collapse: collapse;
}

.flags-table th {
  padding: var(--space-3) var(--space-4);
  text-align: left;
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-primary);
}

.flags-table td {
  padding: var(--space-4);
  border-bottom: 1px solid var(--border-primary);
  font-size: var(--text-sm);
}

.flag-row:hover {
  background: var(--bg-hover);
}

.feature-name {
  font-weight: var(--font-medium);
  color: var(--text-primary);
}

/* Toggle Switch */
.toggle-switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: 24px;
  transition: 0.3s;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 2px;
  bottom: 2px;
  background: var(--text-secondary);
  border-radius: 50%;
  transition: 0.3s;
}

input:checked + .toggle-slider {
  background: var(--accent-green);
  border-color: var(--accent-green);
}

input:checked + .toggle-slider:before {
  transform: translateX(20px);
  background: var(--text-primary);
}

.toggle-disabled {
  opacity: 0.5;
  pointer-events: none;
}

/* Rollout Slider */
.rollout-slider-container {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.rollout-slider {
  flex: 1;
  height: 4px;
  border-radius: var(--radius-sm);
  background: var(--bg-tertiary);
  outline: none;
  -webkit-appearance: none;
}

.rollout-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--accent-blue);
  cursor: pointer;
}

.rollout-slider::-moz-range-thumb {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--accent-blue);
  cursor: pointer;
  border: none;
}

.rollout-value {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  font-family: var(--font-mono);
  min-width: 30px;
}

/* Adoption and Performance */
.adoption-rate {
  font-weight: var(--font-medium);
  color: var(--text-primary);
  font-family: var(--font-mono);
}

.adoption-trend,
.performance-trend {
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  margin-left: var(--space-2);
}

.trend-positive {
  color: var(--accent-green);
}

.trend-negative {
  color: var(--accent-red);
}

/* Crane Valuation Configuration */
.crane-valuation-section {
  margin-bottom: var(--space-8);
}

.valuation-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-6);
  margin-bottom: var(--space-6);
}

.valuation-card {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  padding: var(--space-6);
}

.valuation-title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-4) 0;
}

.valuation-form,
.data-sources-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.form-label {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
}

.form-select,
.form-input {
  padding: var(--space-2) var(--space-3);
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: var(--text-sm);
}

.form-select:focus,
.form-input:focus {
  outline: none;
  border-color: var(--accent-blue);
}

.input-with-suffix {
  position: relative;
  display: flex;
  align-items: center;
}

.input-suffix {
  position: absolute;
  right: var(--space-3);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  pointer-events: none;
}

/* Pricing Models */
.pricing-models-section {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  overflow: hidden;
}

.models-tabs {
  display: flex;
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-primary);
}

.tab-btn {
  padding: var(--space-3) var(--space-6);
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn:hover,
.tab-btn.tab-active {
  color: var(--text-primary);
  background: var(--bg-secondary);
}

.tab-content {
  padding: var(--space-6);
  display: none;
}

.tab-content.tab-content-active {
  display: block;
}

.pricing-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.pricing-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.pricing-title {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
  margin: 0;
}

.adjustments-section {
  padding-top: var(--space-4);
  border-top: 1px solid var(--border-primary);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  cursor: pointer;
}

.checkbox-input {
  display: none;
}

.checkbox-custom {
  width: 16px;
  height: 16px;
  border: 2px solid var(--border-primary);
  border-radius: var(--radius-sm);
  background: var(--bg-tertiary);
  position: relative;
  transition: all 0.2s ease;
}

.checkbox-input:checked + .checkbox-custom {
  background: var(--accent-blue);
  border-color: var(--accent-blue);
}

.checkbox-input:checked + .checkbox-custom::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: var(--text-primary);
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
}

.checkbox-text {
  font-size: var(--text-sm);
  color: var(--text-primary);
}

/* Feature Performance */
.feature-performance-section {
  margin-bottom: var(--space-8);
}

.performance-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-6);
}

.performance-card {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  padding: var(--space-6);
}

.performance-title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-4) 0;
}

.performance-chart {
  height: 120px;
  margin-bottom: var(--space-4);
}

.performance-stats {
  display: flex;
  justify-content: space-between;
  gap: var(--space-4);
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.stat-label {
  font-size: var(--text-xs);
  color: var(--text-secondary);
}

.stat-value {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-primary);
  font-family: var(--font-mono);
}

.health-excellent {
  color: var(--accent-green);
}

/* Feature Versioning */
.feature-versioning-section {
  margin-bottom: var(--space-8);
}

.versioning-container {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  padding: var(--space-6);
}

.version-timeline {
  margin-bottom: var(--space-6);
}

.version-item {
  display: flex;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
  position: relative;
}

.version-item:not(:last-child)::after {
  content: '';
  position: absolute;
  left: 8px;
  top: 24px;
  bottom: -24px;
  width: 2px;
  background: var(--border-primary);
}

.version-marker {
  width: 16px;
  height: 16px;
  border-radius: var(--radius-full);
  background: var(--bg-tertiary);
  border: 2px solid var(--border-primary);
  margin-top: 4px;
  flex-shrink: 0;
}

.version-current .version-marker {
  background: var(--accent-blue);
  border-color: var(--accent-blue);
}

.version-content {
  flex: 1;
}

.version-title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-2) 0;
}

.version-description {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0 0 var(--space-2) 0;
  line-height: 1.5;
}

.version-meta {
  display: flex;
  gap: var(--space-3);
  align-items: center;
}

.version-date {
  font-size: var(--text-xs);
  color: var(--text-muted);
  font-family: var(--font-mono);
}

.version-status {
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  text-transform: uppercase;
}

.status-live {
  background: rgba(40, 167, 69, 0.2);
  color: var(--accent-green);
}

.status-archived {
  background: rgba(108, 117, 125, 0.2);
  color: var(--text-muted);
}

.version-actions {
  display: flex;
  gap: var(--space-3);
  justify-content: flex-end;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .valuation-grid,
  .performance-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .pricing-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .analytics-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .features-header,
  .activities-header {
    flex-direction: column;
    gap: var(--space-4);
    align-items: stretch;
  }
  
  .feed-header,
  .audit-header {
    flex-direction: column;
    gap: var(--space-3);
    align-items: stretch;
  }
  
  .valuation-grid,
  .performance-grid,
  .pricing-grid {
    grid-template-columns: 1fr;
  }
  
  .flags-table-container,
  .activity-feed-container,
  .audit-table-container {
    overflow-x: auto;
  }
  
  .compliance-stats {
    flex-direction: column;
    gap: var(--space-4);
  }
  
  .version-actions {
    flex-direction: column;
  }
}
```

This completes the comprehensive technical specifications for the webapp management sections of the Crane Intelligence Admin Panel, including detailed HTML structures, CSS styling, and responsive design considerations for all components.
