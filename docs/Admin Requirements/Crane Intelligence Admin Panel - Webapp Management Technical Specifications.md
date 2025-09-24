# Crane Intelligence Admin Panel - Webapp Management Technical Specifications

## 🌐 **10. Webapp User Management - Technical Specifications**

### **Layout Structure**
```html
<div class="webapp-user-management">
  <div class="webapp-header">
    <h1 class="page-title">Webapp User Management</h1>
    <div class="header-controls">
      <button class="btn btn-secondary">
        <span class="btn-icon">📊</span>
        Export Report
      </button>
      <button class="btn btn-primary">
        <span class="btn-icon">🔄</span>
        Refresh Data
      </button>
    </div>
  </div>

  <!-- Active User Sessions -->
  <div class="active-sessions-section">
    <div class="section-header">
      <h2 class="section-title">ACTIVE USER SESSIONS</h2>
      <div class="session-stats">
        <span class="stat-item">
          <span class="stat-value">247</span>
          <span class="stat-label">Active</span>
        </span>
        <span class="stat-item">
          <span class="stat-value">1,532</span>
          <span class="stat-label">Total Today</span>
        </span>
      </div>
    </div>

    <div class="sessions-table-container">
      <table class="sessions-table">
        <thead>
          <tr>
            <th>USER</th>
            <th>STATUS</th>
            <th>SESSION DURATION</th>
            <th>USER JOURNEY MAPPING</th>
            <th>SESSION RECORDINGS</th>
            <th>USER FEEDBACK MANAGEMENT</th>
          </tr>
        </thead>
        <tbody>
          <tr class="session-row">
            <td class="user-cell">
              <div class="user-avatar">LLA</div>
              <span class="user-name">LLA</span>
            </td>
            <td class="status-cell">
              <span class="status-indicator status-active"></span>
              <span class="status-text">Active</span>
            </td>
            <td class="duration-cell">00:14:32</td>
            <td class="journey-cell">
              <div class="journey-heatmap">
                <div class="heatmap-dot hot"></div>
                <div class="heatmap-dot warm"></div>
                <div class="heatmap-dot cool"></div>
              </div>
            </td>
            <td class="recording-cell">
              <button class="recording-btn">
                <span class="recording-icon">📹</span>
                <span class="recording-duration">00:14:32</span>
              </button>
            </td>
            <td class="feedback-cell">
              <div class="feedback-item">
                <span class="feedback-date">2024-04-23</span>
                <span class="feedback-text">Improve the performance</span>
              </div>
            </td>
          </tr>
          
          <tr class="session-row">
            <td class="user-cell">
              <div class="user-avatar">EFS</div>
              <span class="user-name">EFS</span>
            </td>
            <td class="status-cell">
              <span class="status-indicator status-idle"></span>
              <span class="status-text">Idle</span>
            </td>
            <td class="duration-cell">00:03:25</td>
            <td class="journey-cell">
              <div class="journey-heatmap">
                <div class="heatmap-dot cool"></div>
                <div class="heatmap-dot cool"></div>
                <div class="heatmap-dot cool"></div>
              </div>
            </td>
            <td class="recording-cell">
              <button class="recording-btn">
                <span class="recording-icon">📹</span>
                <span class="recording-duration">00:03:25</span>
              </button>
            </td>
            <td class="feedback-cell">
              <div class="feedback-item">
                <span class="feedback-date">2024-04-21</span>
                <span class="feedback-text">Great user experience!</span>
              </div>
            </td>
          </tr>
          
          <tr class="session-row">
            <td class="user-cell">
              <div class="user-avatar">JDB</div>
              <span class="user-name">JDB</span>
            </td>
            <td class="status-cell">
              <span class="status-indicator status-active"></span>
              <span class="status-text">Active</span>
            </td>
            <td class="duration-cell">00:08:47</td>
            <td class="journey-cell">
              <div class="journey-heatmap">
                <div class="heatmap-dot warm"></div>
                <div class="heatmap-dot hot"></div>
                <div class="heatmap-dot warm"></div>
              </div>
            </td>
            <td class="recording-cell">
              <button class="recording-btn">
                <span class="recording-icon">📹</span>
                <span class="recording-duration">00:08:47</span>
              </button>
            </td>
            <td class="feedback-cell">
              <div class="feedback-item">
                <span class="feedback-date">2024-04-20</span>
                <span class="feedback-text">Feature requests</span>
              </div>
            </td>
          </tr>
          
          <tr class="session-row">
            <td class="user-cell">
              <div class="user-avatar">SAR</div>
              <span class="user-name">SAR</span>
            </td>
            <td class="status-cell">
              <span class="status-indicator status-recording"></span>
              <span class="status-text">Recording</span>
            </td>
            <td class="duration-cell">00:25:14</td>
            <td class="journey-cell">
              <div class="journey-heatmap">
                <div class="heatmap-dot hot"></div>
                <div class="heatmap-dot hot"></div>
                <div class="heatmap-dot warm"></div>
              </div>
            </td>
            <td class="recording-cell">
              <button class="recording-btn recording-active">
                <span class="recording-icon">🔴</span>
                <span class="recording-duration">00:25:14</span>
              </button>
            </td>
            <td class="feedback-cell">
              <div class="feedback-item">
                <span class="feedback-date">2024-04-18</span>
                <span class="feedback-text">Issue with onboarding</span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- User Engagement Metrics -->
  <div class="engagement-metrics-section">
    <h2 class="section-title">USER ENGAGEMENT METRICS</h2>
    <div class="metrics-grid">
      <div class="metric-card">
        <h3 class="metric-title">AVERAGE SESSION</h3>
        <div class="metric-value">6m 42s</div>
        <div class="metric-trend">
          <canvas id="sessionTrendChart"></canvas>
        </div>
      </div>
      
      <div class="metric-card">
        <h3 class="metric-title">PAGE VIEWS</h3>
        <div class="metric-value">1,532</div>
        <div class="metric-chart">
          <canvas id="pageViewsChart"></canvas>
        </div>
      </div>
      
      <div class="metric-card">
        <h3 class="metric-title">FEATURE USAGE</h3>
        <div class="metric-value">58%</div>
        <div class="metric-gauge">
          <div class="gauge-circle" data-percentage="58">
            <span class="gauge-percentage">58%</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- User Journey Mapping -->
  <div class="journey-mapping-section">
    <div class="journey-header">
      <h2 class="section-title">USER JOURNEY MAPPING</h2>
      <div class="journey-controls">
        <select class="journey-filter">
          <option>All Users</option>
          <option>New Users</option>
          <option>Returning Users</option>
        </select>
      </div>
    </div>
    
    <div class="journey-funnel">
      <div class="funnel-stage">
        <div class="funnel-shape funnel-top">
          <span class="funnel-label">Session 1</span>
          <span class="funnel-percentage">132</span>
        </div>
      </div>
      
      <div class="funnel-stage">
        <div class="funnel-shape funnel-middle">
          <span class="funnel-label">Session 2</span>
          <span class="funnel-percentage">42%</span>
        </div>
      </div>
      
      <div class="funnel-stage">
        <div class="funnel-shape funnel-bottom">
          <span class="funnel-label">Retention</span>
          <span class="funnel-percentage">75%</span>
        </div>
      </div>
    </div>
  </div>

  <!-- User Lifecycle Management -->
  <div class="lifecycle-management-section">
    <h2 class="section-title">USER LIFECYCLE MANAGEMENT</h2>
    <div class="lifecycle-grid">
      <div class="lifecycle-card">
        <h3 class="lifecycle-title">ONBOARDING PROGRESS</h3>
        <div class="progress-bar-container">
          <div class="progress-bar">
            <div class="progress-fill" style="width: 75%;"></div>
          </div>
          <div class="progress-labels">
            <span>25%</span>
            <span>50%</span>
            <span>75%</span>
            <span>100%</span>
          </div>
        </div>
      </div>
      
      <div class="lifecycle-card">
        <h3 class="lifecycle-title">FEATURE ADOPTION RATES</h3>
        <div class="adoption-chart">
          <canvas id="featureAdoptionChart"></canvas>
        </div>
      </div>
      
      <div class="lifecycle-card">
        <h3 class="lifecycle-title">CHURN PREDICTION ANALYTICS</h3>
        <div class="churn-chart">
          <canvas id="churnPredictionChart"></canvas>
        </div>
      </div>
    </div>
  </div>

  <!-- Session Recordings Panel -->
  <div class="session-recordings-panel">
    <h2 class="section-title">SESSION RECORDINGS</h2>
    <div class="recordings-list">
      <div class="recording-item">
        <div class="recording-info">
          <span class="recording-title">Session 1</span>
          <span class="recording-duration">00:14:32</span>
        </div>
        <div class="recording-actions">
          <button class="btn btn-secondary btn-sm">Play</button>
          <button class="btn btn-secondary btn-sm">Download</button>
        </div>
      </div>
      
      <div class="recording-item">
        <div class="recording-info">
          <span class="recording-title">Session 2</span>
          <span class="recording-duration">00:20:19</span>
        </div>
        <div class="recording-actions">
          <button class="btn btn-secondary btn-sm">Play</button>
          <button class="btn btn-secondary btn-sm">Download</button>
        </div>
      </div>
      
      <div class="recording-item">
        <div class="recording-info">
          <span class="recording-title">Session 3</span>
          <span class="recording-duration">00:37:36</span>
        </div>
        <div class="recording-actions">
          <button class="btn btn-secondary btn-sm">Play</button>
          <button class="btn btn-secondary btn-sm">Download</button>
        </div>
      </div>
      
      <div class="recording-item">
        <div class="recording-info">
          <span class="recording-title">Session 4</span>
          <span class="recording-duration">00:23:44</span>
        </div>
        <div class="recording-actions">
          <button class="btn btn-secondary btn-sm">Play</button>
          <button class="btn btn-secondary btn-sm">Download</button>
        </div>
      </div>
    </div>
  </div>

  <!-- User Feedback Management -->
  <div class="feedback-management-section">
    <h2 class="section-title">USER FEEDBACK MANAGEMENT</h2>
    <div class="feedback-list">
      <div class="feedback-item">
        <div class="feedback-header">
          <span class="feedback-date">2024-04-23</span>
          <span class="feedback-type">Performance</span>
        </div>
        <div class="feedback-content">
          <p class="feedback-text">Great user experience!</p>
        </div>
        <div class="feedback-actions">
          <button class="btn btn-secondary btn-sm">Reply</button>
          <button class="btn btn-primary btn-sm">Resolve</button>
        </div>
      </div>
      
      <div class="feedback-item">
        <div class="feedback-header">
          <span class="feedback-date">2024-04-21</span>
          <span class="feedback-type">Feature Request</span>
        </div>
        <div class="feedback-content">
          <p class="feedback-text">Feature requests</p>
        </div>
        <div class="feedback-actions">
          <button class="btn btn-secondary btn-sm">Reply</button>
          <button class="btn btn-primary btn-sm">Resolve</button>
        </div>
      </div>
      
      <div class="feedback-item">
        <div class="feedback-header">
          <span class="feedback-date">2024-04-20</span>
          <span class="feedback-type">Bug Report</span>
        </div>
        <div class="feedback-content">
          <p class="feedback-text">Issue with onboarding</p>
        </div>
        <div class="feedback-actions">
          <button class="btn btn-secondary btn-sm">Reply</button>
          <button class="btn btn-primary btn-sm">Resolve</button>
        </div>
      </div>
    </div>
  </div>
</div>
```

### **CSS Specifications**
```css
.webapp-user-management {
  padding: var(--space-6);
  background: var(--bg-primary);
  min-height: 100vh;
}

.webapp-header {
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
}

.header-controls {
  display: flex;
  gap: var(--space-3);
}

/* Active Sessions Section */
.active-sessions-section {
  margin-bottom: var(--space-8);
}

.section-header {
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

.session-stats {
  display: flex;
  gap: var(--space-6);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-1);
}

.stat-value {
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  font-family: var(--font-mono);
}

.stat-label {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  text-transform: uppercase;
}

/* Sessions Table */
.sessions-table-container {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  overflow: hidden;
}

.sessions-table {
  width: 100%;
  border-collapse: collapse;
}

.sessions-table th {
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

.sessions-table td {
  padding: var(--space-4);
  border-bottom: 1px solid var(--border-primary);
  font-size: var(--text-sm);
}

.session-row:hover {
  background: var(--bg-hover);
}

.user-cell {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.user-avatar {
  width: 32px;
  height: 32px;
  background: var(--accent-blue);
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
  color: var(--text-primary);
}

.user-name {
  font-weight: var(--font-medium);
  color: var(--text-primary);
}

.status-cell {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
}

.status-active {
  background: var(--accent-green);
}

.status-idle {
  background: var(--accent-orange);
}

.status-recording {
  background: var(--accent-red);
  animation: pulse 2s infinite;
}

.status-text {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.duration-cell {
  font-family: var(--font-mono);
  color: var(--text-primary);
  font-weight: var(--font-medium);
}

/* Journey Heatmap */
.journey-cell {
  padding: var(--space-2);
}

.journey-heatmap {
  display: flex;
  gap: var(--space-1);
}

.heatmap-dot {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
}

.heatmap-dot.hot {
  background: var(--accent-red);
}

.heatmap-dot.warm {
  background: var(--accent-orange);
}

.heatmap-dot.cool {
  background: var(--accent-blue);
}

/* Recording Button */
.recording-btn {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-1) var(--space-2);
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  cursor: pointer;
  font-size: var(--text-xs);
  transition: all 0.2s ease;
}

.recording-btn:hover {
  background: var(--bg-hover);
}

.recording-btn.recording-active {
  background: rgba(220, 53, 69, 0.2);
  border-color: var(--accent-red);
}

.recording-icon {
  font-size: var(--text-sm);
}

.recording-duration {
  font-family: var(--font-mono);
  font-weight: var(--font-medium);
}

/* Feedback Cell */
.feedback-cell {
  max-width: 200px;
}

.feedback-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.feedback-date {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.feedback-text {
  font-size: var(--text-sm);
  color: var(--text-primary);
  line-height: 1.4;
}

/* Engagement Metrics */
.engagement-metrics-section {
  margin-bottom: var(--space-8);
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-6);
}

.metric-card {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  padding: var(--space-6);
}

.metric-title {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
  margin: 0 0 var(--space-3) 0;
  letter-spacing: 0.05em;
}

.metric-value {
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  font-family: var(--font-mono);
  margin-bottom: var(--space-4);
}

.metric-trend,
.metric-chart {
  height: 60px;
}

.metric-gauge {
  display: flex;
  justify-content: center;
  align-items: center;
}

.gauge-circle {
  width: 80px;
  height: 80px;
  border-radius: var(--radius-full);
  background: conic-gradient(
    var(--accent-green) 0deg,
    var(--accent-green) calc(var(--percentage, 0) * 3.6deg),
    var(--bg-tertiary) calc(var(--percentage, 0) * 3.6deg),
    var(--bg-tertiary) 360deg
  );
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.gauge-circle::before {
  content: '';
  position: absolute;
  width: 60px;
  height: 60px;
  background: var(--bg-secondary);
  border-radius: var(--radius-full);
}

.gauge-percentage {
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  z-index: 1;
}

/* Journey Mapping */
.journey-mapping-section {
  margin-bottom: var(--space-8);
}

.journey-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-6);
}

.journey-controls {
  display: flex;
  gap: var(--space-3);
}

.journey-filter {
  padding: var(--space-2) var(--space-3);
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: var(--text-sm);
}

.journey-funnel {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--space-4);
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  padding: var(--space-8);
}

.funnel-stage {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.funnel-shape {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-primary);
  font-weight: var(--font-medium);
  position: relative;
}

.funnel-top {
  width: 120px;
  height: 80px;
  background: var(--accent-blue);
  clip-path: polygon(0 0, 100% 0, 80% 100%, 20% 100%);
}

.funnel-middle {
  width: 100px;
  height: 80px;
  background: var(--accent-green);
  clip-path: polygon(0 0, 100% 0, 75% 100%, 25% 100%);
}

.funnel-bottom {
  width: 80px;
  height: 80px;
  background: var(--accent-orange);
  clip-path: polygon(0 0, 100% 0, 70% 100%, 30% 100%);
}

.funnel-label {
  font-size: var(--text-sm);
  margin-bottom: var(--space-1);
}

.funnel-percentage {
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
}

/* Lifecycle Management */
.lifecycle-management-section {
  margin-bottom: var(--space-8);
}

.lifecycle-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-6);
}

.lifecycle-card {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  padding: var(--space-6);
}

.lifecycle-title {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
  margin: 0 0 var(--space-4) 0;
  letter-spacing: 0.05em;
}

.progress-bar-container {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--accent-green);
  border-radius: var(--radius-sm);
  transition: width 0.3s ease;
}

.progress-labels {
  display: flex;
  justify-content: space-between;
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.adoption-chart,
.churn-chart {
  height: 120px;
}

/* Session Recordings Panel */
.session-recordings-panel {
  margin-bottom: var(--space-8);
}

.recordings-list {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.recording-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3);
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-primary);
}

.recording-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.recording-title {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-primary);
}

.recording-actions {
  display: flex;
  gap: var(--space-2);
}

/* User Feedback Management */
.feedback-management-section {
  margin-bottom: var(--space-8);
}

.feedback-list {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.feedback-item {
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-primary);
  padding: var(--space-4);
}

.feedback-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-2);
}

.feedback-date {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.feedback-type {
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  color: var(--accent-blue);
  background: rgba(0, 123, 255, 0.2);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
}

.feedback-content {
  margin-bottom: var(--space-3);
}

.feedback-text {
  font-size: var(--text-sm);
  color: var(--text-primary);
  line-height: 1.5;
  margin: 0;
}

.feedback-actions {
  display: flex;
  gap: var(--space-2);
}

/* Responsive Design */
@media (max-width: 1024px) {
  .metrics-grid,
  .lifecycle-grid {
    grid-template-columns: 1fr;
  }
  
  .sessions-table {
    font-size: var(--text-xs);
  }
  
  .journey-funnel {
    flex-direction: column;
  }
}

@media (max-width: 768px) {
  .webapp-header {
    flex-direction: column;
    gap: var(--space-4);
    align-items: stretch;
  }
  
  .section-header {
    flex-direction: column;
    gap: var(--space-3);
    align-items: stretch;
  }
  
  .sessions-table-container {
    overflow-x: auto;
  }
  
  .feedback-header {
    flex-direction: column;
    gap: var(--space-2);
    align-items: flex-start;
  }
}
```

---

## 📊 **11. Activities Tracking - Technical Specifications**

### **Layout Structure**
```html
<div class="activities-tracking">
  <div class="activities-header">
    <h1 class="page-title">ACTIVITY TRACKING</h1>
    <div class="header-controls">
      <button class="btn btn-secondary">
        <span class="btn-icon">📤</span>
        Export Logs
      </button>
      <button class="btn btn-primary">
        <span class="btn-icon">🔄</span>
        Refresh
      </button>
    </div>
  </div>

  <!-- Activity Feed -->
  <div class="activity-feed-section">
    <div class="feed-header">
      <h2 class="section-title">ACTIVITY FEED</h2>
      <div class="feed-filters">
        <select class="filter-select">
          <option>Filter</option>
          <option>User Actions</option>
          <option>System Events</option>
          <option>API Calls</option>
          <option>Errors</option>
        </select>
        <select class="filter-select">
          <option>Action Type</option>
          <option>Login</option>
          <option>Logout</option>
          <option>API Call</option>
          <option>Database Update</option>
          <option>Error</option>
        </select>
      </div>
    </div>

    <div class="activity-feed-container">
      <table class="activity-table">
        <thead>
          <tr>
            <th>Time</th>
            <th>User</th>
            <th>Action</th>
            <th>Details</th>
          </tr>
        </thead>
        <tbody>
          <tr class="activity-row">
            <td class="time-cell">1 ago</td>
            <td class="user-cell">
              <div class="user-avatar user-avatar-e">E</div>
              <span class="user-name">Elizabeth</span>
            </td>
            <td class="action-cell">
              <span class="action-indicator action-success"></span>
              <span class="action-text">Logged In</span>
            </td>
            <td class="details-cell">Logged In</td>
          </tr>
          
          <tr class="activity-row">
            <td class="time-cell">1 ago</td>
            <td class="user-cell">
              <div class="user-avatar user-avatar-j">J</div>
              <span class="user-name">James</span>
            </td>
            <td class="action-cell">
              <span class="action-indicator action-info"></span>
              <span class="action-text">API Call</span>
            </td>
            <td class="details-cell">Path: /API/call</td>
          </tr>
          
          <tr class="activity-row">
            <td class="time-cell">8 ago</td>
            <td class="user-cell">
              <div class="user-avatar user-avatar-d">D</div>
              <span class="user-name">Daniel</span>
            </td>
            <td class="action-cell">
              <span class="action-indicator action-error"></span>
              <span class="action-text">Error</span>
            </td>
            <td class="details-cell">Error code 1331</td>
          </tr>
          
          <tr class="activity-row">
            <td class="time-cell">10 ago</td>
            <td class="user-cell">
              <div class="user-avatar user-avatar-o">O</div>
              <span class="user-name">Olivia</span>
            </td>
            <td class="action-cell">
              <span class="action-indicator action-warning"></span>
              <span class="action-text">Logged Out</span>
            </td>
            <td class="details-cell">Logged out 0980</td>
          </tr>
          
          <tr class="activity-row">
            <td class="time-cell">0 ago</td>
            <td class="user-cell">
              <div class="user-avatar user-avatar-j">J</div>
              <span class="user-name">James</span>
            </td>
            <td class="action-cell">
              <span class="action-indicator action-info"></span>
              <span class="action-text">Database Update</span>
            </td>
            <td class="details-cell">Data updated</td>
          </tr>
          
          <tr class="activity-row">
            <td class="time-cell">16 ago</td>
            <td class="user-cell">
              <div class="user-avatar user-avatar-e">E</div>
              <span class="user-name">Elisari</span>
            </td>
            <td class="action-cell">
              <span class="action-indicator action-warning"></span>
              <span class="action-text">Logged Out</span>
            </td>
            <td class="details-cell">Logged Out</td>
          </tr>
          
          <tr class="activity-row">
            <td class="time-cell">32 ago</td>
            <td class="user-cell">
              <div class="user-avatar user-avatar-j">J</div>
              <span class="user-name">James</span>
            </td>
            <td class="action-cell">
              <span class="action-indicator action-info"></span>
              <span class="action-text">Database Update</span>
            </td>
            <td class="details-cell">Update - Error 1908</td>
          </tr>
          
          <tr class="activity-row">
            <td class="time-cell">28 ago</td>
            <td class="user-cell">
              <div class="user-avatar user-avatar-d">D</div>
              <span class="user-name">James</span>
            </td>
            <td class="action-cell">
              <span class="action-indicator action-success"></span>
              <span class="action-text">Logged In</span>
            </td>
            <td class="details-cell">System update</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- Activity Analytics -->
  <div class="activity-analytics-section">
    <h2 class="section-title">ACTIVITY ANALYTICS</h2>
    <div class="analytics-grid">
      <div class="analytics-card">
        <h3 class="analytics-title">Most Used Features</h3>
        <div class="feature-list">
          <div class="feature-item">
            <span class="feature-name">Dashboard</span>
            <div class="feature-bar">
              <div class="feature-progress" style="width: 85%;"></div>
            </div>
          </div>
          <div class="feature-item">
            <span class="feature-name">Reports</span>
            <div class="feature-bar">
              <div class="feature-progress" style="width: 70%;"></div>
            </div>
          </div>
          <div class="feature-item">
            <span class="feature-name">Notifications</span>
            <div class="feature-bar">
              <div class="feature-progress" style="width: 60%;"></div>
            </div>
          </div>
          <div class="feature-item">
            <span class="feature-name">Settings</span>
            <div class="feature-bar">
              <div class="feature-progress" style="width: 45%;"></div>
            </div>
          </div>
          <div class="feature-item">
            <span class="feature-name">Profile</span>
            <div class="feature-bar">
              <div class="feature-progress" style="width: 30%;"></div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="analytics-card">
        <h3 class="analytics-title">Peak Usage Times</h3>
        <div class="usage-chart">
          <canvas id="peakUsageChart"></canvas>
        </div>
      </div>
      
      <div class="analytics-card">
        <h3 class="analytics-title">User Interaction Patterns</h3>
        <div class="interaction-list">
          <div class="interaction-item">
            <span class="interaction-name">Navigation</span>
            <div class="interaction-bar">
              <div class="interaction-progress" style="width: 90%;"></div>
            </div>
          </div>
          <div class="interaction-item">
            <span class="interaction-name">Search</span>
            <div class="interaction-bar">
              <div class="interaction-progress" style="width: 75%;"></div>
            </div>
          </div>
          <div class="interaction-item">
            <span class="interaction-name">Interaction</span>
            <div class="interaction-bar">
              <div class="interaction-progress" style="width: 65%;"></div>
            </div>
          </div>
          <div class="interaction-item">
            <span class="interaction-name">Settings</span>
            <div class="interaction-bar">
              <div class="interaction-progress" style="width: 55%;"></div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="analytics-card">
        <h3 class="analytics-title">Feature Performance Metrics</h3>
        <div class="performance-chart">
          <canvas id="featurePerformanceChart"></canvas>
        </div>
      </div>
    </div>
  </div>

  <!-- Activity Heatmap -->
  <div class="activity-heatmap-section">
    <h2 class="section-title">Activity Heatmap</h2>
    <div class="heatmap-container">
      <div class="heatmap-grid">
        <div class="heatmap-labels">
          <div class="day-label">Mon</div>
          <div class="day-label">Tue</div>
          <div class="day-label">Wed</div>
          <div class="day-label">Sun</div>
          <div class="day-label">Mon</div>
        </div>
        <div class="heatmap-hours">
          <div class="hour-label">0</div>
          <div class="hour-label">2</div>
          <div class="hour-label">9</div>
          <div class="hour-label">0</div>
          <div class="hour-label">6</div>
          <div class="hour-label">10</div>
          <div class="hour-label">12</div>
          <div class="hour-label">14</div>
          <div class="hour-label">18</div>
          <div class="hour-label">20</div>
          <div class="hour-label">23</div>
        </div>
        <div class="heatmap-cells">
          <!-- Heatmap cells would be generated dynamically -->
          <div class="heatmap-cell heatmap-low"></div>
          <div class="heatmap-cell heatmap-medium"></div>
          <div class="heatmap-cell heatmap-high"></div>
          <div class="heatmap-cell heatmap-very-high"></div>
          <div class="heatmap-cell heatmap-medium"></div>
          <!-- More cells... -->
        </div>
      </div>
    </div>
  </div>

  <!-- Audit Trail -->
  <div class="audit-trail-section">
    <div class="audit-header">
      <h2 class="section-title">AUDIT TRAIL</h2>
      <div class="audit-controls">
        <button class="btn btn-secondary">
          <span class="btn-icon">📊</span>
          DATA EXPORT
        </button>
        <button class="btn btn-secondary">
          <span class="btn-icon">🔍</span>
          FILTER
        </button>
        <button class="btn btn-secondary">
          <span class="btn-icon">↕️</span>
        </button>
      </div>
    </div>

    <div class="audit-table-container">
      <table class="audit-table">
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Event</th>
            <th>User</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr class="audit-row">
            <td class="timestamp-cell">10:13 AM 17:11</td>
            <td class="event-cell">File Download</td>
            <td class="user-cell">Alejandra</td>
            <td class="status-cell">
              <span class="status-badge status-completed">Completed</span>
            </td>
          </tr>
          
          <tr class="audit-row">
            <td class="timestamp-cell">4:52 AM 16:10</td>
            <td class="event-cell">Policy Violation</td>
            <td class="user-cell">Elisabeth</td>
            <td class="status-cell">
              <span class="status-badge status-warning">Warning</span>
            </td>
          </tr>
          
          <tr class="audit-row">
            <td class="timestamp-cell">8:14 AM 11:30</td>
            <td class="event-cell">Settings Change</td>
            <td class="user-cell">Daniel</td>
            <td class="status-cell">
              <span class="status-badge status-exported">Exported</span>
            </td>
          </tr>
          
          <tr class="audit-row">
            <td class="timestamp-cell">16:31 AM 12:51</td>
            <td class="event-cell">Report Export</td>
            <td class="user-cell">Olivia</td>
            <td class="status-cell">
              <span class="status-badge status-exported">Exported</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="compliance-section">
      <h3 class="compliance-title">COMPLIANCE TRACKING</h3>
      <div class="compliance-stats">
        <div class="compliance-item">
          <span class="compliance-label">GDPR Compliance</span>
          <span class="compliance-status status-good">98%</span>
        </div>
        <div class="compliance-item">
          <span class="compliance-label">Data Retention</span>
          <span class="compliance-status status-good">95%</span>
        </div>
        <div class="compliance-item">
          <span class="compliance-label">Access Control</span>
          <span class="compliance-status status-excellent">100%</span>
        </div>
      </div>
    </div>
  </div>
</div>
```

This completes the first part of the webapp management specifications. Would you like me to continue with the Core Features Management section and complete the technical documentation?
