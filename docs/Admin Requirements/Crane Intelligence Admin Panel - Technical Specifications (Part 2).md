# Crane Intelligence Admin Panel - Technical Specifications (Part 2)

## 📝 **4. Content Management - Technical Specifications**

### **Layout Structure**
```html
<div class="content-management">
  <div class="content-header">
    <h1 class="page-title">Content Management</h1>
  </div>

  <!-- Tab Navigation -->
  <div class="tab-navigation">
    <button class="tab-button active" data-tab="library">Content Library</button>
    <button class="tab-button" data-tab="media">Media Manager</button>
    <button class="tab-button" data-tab="templates">Templates</button>
    <button class="tab-button" data-tab="publishing">Publishing</button>
  </div>

  <!-- Content Library Tab -->
  <div class="tab-content active" id="library-tab">
    <div class="content-layout">
      <!-- Sidebar with folder structure -->
      <div class="content-sidebar">
        <div class="folder-tree">
          <div class="folder-item">
            <span class="folder-icon">📁</span>
            <span class="folder-name">Articles</span>
            <span class="item-count">12</span>
          </div>
          <div class="folder-item">
            <span class="folder-icon">📁</span>
            <span class="folder-name">Blog</span>
            <span class="item-count">12</span>
          </div>
          <div class="folder-item">
            <span class="folder-icon">📁</span>
            <span class="folder-name">News</span>
          </div>
          <div class="folder-item">
            <span class="folder-icon">📁</span>
            <span class="folder-name">Resources</span>
          </div>
          <div class="folder-item">
            <span class="folder-icon">📁</span>
            <span class="folder-name">Whitepapers</span>
          </div>
          <div class="folder-item">
            <span class="folder-icon">📁</span>
            <span class="folder-name">Uncategorized</span>
          </div>
          <div class="folder-item">
            <span class="folder-icon">📁</span>
            <span class="folder-name">Archived</span>
          </div>
        </div>
      </div>

      <!-- Main content area -->
      <div class="content-main">
        <div class="content-toolbar">
          <div class="search-wrapper">
            <input type="text" class="search-input" placeholder="Search" />
            <span class="search-icon">🔍</span>
          </div>
        </div>

        <table class="content-table">
          <thead>
            <tr>
              <th>Title</th>
              <th>Publish Date</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr class="content-row">
              <td class="content-title">Welcome to The Site</td>
              <td class="publish-date">Apr 22, 2024</td>
              <td><span class="status-badge status-published">Published</span></td>
            </tr>
            <tr class="content-row">
              <td class="content-title">New Feature Announcement</td>
              <td class="publish-date">Apr 22, 2024</td>
              <td><span class="status-badge status-published">Published</span></td>
            </tr>
            <tr class="content-row">
              <td class="content-title">Weekly Roundup</td>
              <td class="publish-date">Apr 21, 2024</td>
              <td><span class="status-badge status-published">Published</span></td>
            </tr>
            <tr class="content-row">
              <td class="content-title">Getting Started Guide</td>
              <td class="publish-date">Apr 24, 2024</td>
              <td><span class="status-badge status-published">Published</span></td>
            </tr>
            <tr class="content-row">
              <td class="content-title">Product Update</td>
              <td class="publish-date">Apr 24, 2024</td>
              <td><span class="status-badge status-published">Published</span></td>
            </tr>
            <tr class="content-row">
              <td class="content-title">Case Study: XYZ Corp</td>
              <td class="publish-date">Apr 24, 2024</td>
              <td><span class="status-badge status-published">Published</span></td>
            </tr>
            <tr class="content-row">
              <td class="content-title">Tips & Tricks</td>
              <td class="publish-date">Apr 22, 2024</td>
              <td><span class="status-badge status-published">Published</span></td>
            </tr>
            <tr class="content-row">
              <td class="content-title">Industry Insights</td>
              <td class="publish-date">Apr 12, 2024</td>
              <td><span class="status-badge status-published">Published</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- Media Manager Tab -->
  <div class="tab-content" id="media-tab">
    <div class="media-layout">
      <div class="media-upload">
        <div class="upload-area">
          <div class="upload-content">
            <h3 class="upload-title">Drag & drop files to upload</h3>
            <button class="upload-button">UPLOAD</button>
          </div>
        </div>
      </div>

      <div class="media-grid">
        <div class="media-item">
          <img src="office.jpg" alt="Office" class="media-thumbnail" />
          <div class="media-info">
            <span class="media-name">office.jpg</span>
            <span class="media-size">1920 x 1020</span>
          </div>
        </div>
        <div class="media-item">
          <img src="meeting.jpg" alt="Meeting" class="media-thumbnail" />
          <div class="media-info">
            <span class="media-name">meeting.jpg</span>
            <span class="media-size">1820 x 1880</span>
          </div>
        </div>
        <div class="media-item">
          <img src="business.jpg" alt="Business" class="media-thumbnail" />
          <div class="media-info">
            <span class="media-name">business.jpg</span>
            <span class="media-size">1920 x 1080</span>
          </div>
        </div>
        <div class="media-item">
          <img src="analytics.jpg" alt="Analytics" class="media-thumbnail" />
          <div class="media-info">
            <span class="media-name">analytics.jpg</span>
            <span class="media-size">1920 x 1800</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Templates Tab -->
  <div class="tab-content" id="templates-tab">
    <div class="templates-layout">
      <div class="templates-sidebar">
        <h3 class="sidebar-title">Templates</h3>
        <div class="template-status">
          <div class="status-item">
            <span class="status-indicator status-draft"></span>
            <span class="status-label">Draft</span>
          </div>
          <div class="status-item">
            <span class="status-indicator status-review"></span>
            <span class="status-label">In Review</span>
          </div>
          <div class="status-item">
            <span class="status-indicator status-approved"></span>
            <span class="status-label">Approved</span>
          </div>
        </div>
      </div>

      <div class="templates-main">
        <div class="template-grid">
          <div class="template-card">
            <h4 class="template-title">Blog Post</h4>
            <p class="template-description">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam vitae.</p>
            <div class="template-actions">
              <button class="btn btn-secondary">PREVIEW</button>
              <button class="btn btn-primary">EDIT</button>
            </div>
          </div>
          
          <div class="template-card">
            <h4 class="template-title">Landing Page</h4>
            <p class="template-description">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam vitae.</p>
            <div class="template-actions">
              <button class="btn btn-secondary">PREVIEW</button>
              <button class="btn btn-primary">EDIT</button>
            </div>
          </div>
        </div>
      </div>

      <div class="publishing-panel">
        <h3 class="panel-title">Publishing</h3>
        
        <div class="publishing-section">
          <h4 class="section-title">Approving</h4>
          <div class="approval-item">
            <h5 class="approval-title">Blog Post</h5>
            <p class="approval-description">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam vitae.</p>
          </div>
          <div class="approval-item">
            <h5 class="approval-title">Landing Page</h5>
            <p class="approval-description">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam vitae.</p>
            <button class="btn btn-sm btn-secondary">PREVIEW</button>
            <button class="btn btn-sm btn-primary">EDIT</button>
          </div>
        </div>

        <div class="seo-section">
          <h4 class="section-title">SEO Settings</h4>
          <div class="form-group">
            <label class="form-label">Focus Keyword</label>
            <input type="text" class="form-input" />
          </div>
          <div class="form-group">
            <label class="form-label">SEO Title</label>
            <input type="text" class="form-input" />
          </div>
          <div class="form-group">
            <label class="form-label">Meta Description</label>
            <textarea class="form-textarea"></textarea>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
```

### **CSS Specifications**
```css
.content-management {
  padding: var(--space-6);
  background: var(--bg-primary);
  min-height: 100vh;
}

.content-header {
  margin-bottom: var(--space-8);
}

/* Tab Navigation */
.tab-navigation {
  display: flex;
  border-bottom: 1px solid var(--border-primary);
  margin-bottom: var(--space-6);
}

.tab-button {
  padding: var(--space-4) var(--space-6);
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s ease;
}

.tab-button:hover {
  color: var(--text-primary);
}

.tab-button.active {
  color: var(--accent-blue);
  border-bottom-color: var(--accent-blue);
}

/* Tab Content */
.tab-content {
  display: none;
}

.tab-content.active {
  display: block;
}

/* Content Library Layout */
.content-layout {
  display: grid;
  grid-template-columns: 250px 1fr;
  gap: var(--space-6);
}

.content-sidebar {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  padding: var(--space-6);
}

.folder-tree {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.folder-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.folder-item:hover {
  background: var(--bg-hover);
}

.folder-icon {
  font-size: var(--text-base);
}

.folder-name {
  flex: 1;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-primary);
}

.item-count {
  font-size: var(--text-xs);
  color: var(--text-muted);
  background: var(--bg-tertiary);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
}

.content-main {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  overflow: hidden;
}

.content-toolbar {
  padding: var(--space-4) var(--space-6);
  border-bottom: 1px solid var(--border-primary);
  background: var(--bg-tertiary);
}

.search-wrapper {
  position: relative;
  max-width: 300px;
}

.search-input {
  width: 100%;
  padding: var(--space-2) var(--space-4) var(--space-2) var(--space-10);
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: var(--text-sm);
}

.search-icon {
  position: absolute;
  left: var(--space-3);
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
}

/* Content Table */
.content-table {
  width: 100%;
  border-collapse: collapse;
}

.content-table th {
  padding: var(--space-3) var(--space-6);
  text-align: left;
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-primary);
}

.content-table td {
  padding: var(--space-3) var(--space-6);
  border-bottom: 1px solid var(--border-primary);
  font-size: var(--text-sm);
}

.content-row:hover {
  background: var(--bg-hover);
}

.content-title {
  font-weight: var(--font-medium);
  color: var(--text-primary);
}

.publish-date {
  color: var(--text-secondary);
}

.status-published {
  background: rgba(40, 167, 69, 0.2);
  color: var(--accent-green);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  text-transform: uppercase;
}

/* Media Manager */
.media-layout {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: var(--space-6);
}

.media-upload {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  padding: var(--space-6);
}

.upload-area {
  border: 2px dashed var(--border-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-8);
  text-align: center;
  transition: border-color 0.2s ease;
}

.upload-area:hover {
  border-color: var(--accent-blue);
}

.upload-title {
  font-size: var(--text-lg);
  font-weight: var(--font-medium);
  color: var(--text-primary);
  margin: 0 0 var(--space-4) 0;
}

.upload-button {
  background: var(--accent-blue);
  color: var(--text-primary);
  border: none;
  padding: var(--space-3) var(--space-6);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.upload-button:hover {
  background: #0056b3;
}

.media-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: var(--space-4);
}

.media-item {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  overflow: hidden;
  transition: transform 0.2s ease;
}

.media-item:hover {
  transform: translateY(-2px);
}

.media-thumbnail {
  width: 100%;
  height: 120px;
  object-fit: cover;
}

.media-info {
  padding: var(--space-3);
}

.media-name {
  display: block;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-primary);
  margin-bottom: var(--space-1);
}

.media-size {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

/* Templates Layout */
.templates-layout {
  display: grid;
  grid-template-columns: 200px 1fr 300px;
  gap: var(--space-6);
}

.templates-sidebar {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  padding: var(--space-6);
}

.sidebar-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-4) 0;
}

.template-status {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.status-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: var(--radius-full);
}

.status-draft {
  background: var(--text-muted);
}

.status-review {
  background: var(--accent-orange);
}

.status-approved {
  background: var(--accent-green);
}

.status-label {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.templates-main {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  padding: var(--space-6);
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--space-6);
}

.template-card {
  background: var(--bg-tertiary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  padding: var(--space-6);
}

.template-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-3) 0;
}

.template-description {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0 0 var(--space-4) 0;
  line-height: 1.5;
}

.template-actions {
  display: flex;
  gap: var(--space-2);
}

.publishing-panel {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  padding: var(--space-6);
}

.panel-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-6) 0;
}

.publishing-section {
  margin-bottom: var(--space-6);
  padding-bottom: var(--space-6);
  border-bottom: 1px solid var(--border-primary);
}

.section-title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-4) 0;
}

.approval-item {
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  margin-bottom: var(--space-3);
}

.approval-title {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-2) 0;
}

.approval-description {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  margin: 0 0 var(--space-3) 0;
  line-height: 1.4;
}

.seo-section {
  margin-bottom: var(--space-6);
}

.form-group {
  margin-bottom: var(--space-4);
}

.form-label {
  display: block;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
  margin-bottom: var(--space-2);
}

.form-input {
  width: 100%;
  padding: var(--space-2) var(--space-3);
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: var(--text-sm);
}

.form-input:focus {
  outline: none;
  border-color: var(--accent-blue);
}

.form-textarea {
  width: 100%;
  min-height: 80px;
  padding: var(--space-2) var(--space-3);
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: var(--text-sm);
  resize: vertical;
}

.form-textarea:focus {
  outline: none;
  border-color: var(--accent-blue);
}

/* Responsive Design */
@media (max-width: 1024px) {
  .content-layout {
    grid-template-columns: 1fr;
  }
  
  .templates-layout {
    grid-template-columns: 1fr;
  }
  
  .media-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .tab-navigation {
    overflow-x: auto;
  }
  
  .template-grid {
    grid-template-columns: 1fr;
  }
  
  .media-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  }
}
```

### **JavaScript for Tab Functionality**
```javascript
// Tab switching functionality
document.addEventListener('DOMContentLoaded', function() {
  const tabButtons = document.querySelectorAll('.tab-button');
  const tabContents = document.querySelectorAll('.tab-content');

  tabButtons.forEach(button => {
    button.addEventListener('click', () => {
      const targetTab = button.dataset.tab;
      
      // Remove active class from all buttons and contents
      tabButtons.forEach(btn => btn.classList.remove('active'));
      tabContents.forEach(content => content.classList.remove('active'));
      
      // Add active class to clicked button and corresponding content
      button.classList.add('active');
      document.getElementById(`${targetTab}-tab`).classList.add('active');
    });
  });

  // Drag and drop functionality for media upload
  const uploadArea = document.querySelector('.upload-area');
  
  uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = 'var(--accent-blue)';
  });
  
  uploadArea.addEventListener('dragleave', () => {
    uploadArea.style.borderColor = 'var(--border-primary)';
  });
  
  uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = 'var(--border-primary)';
    
    const files = e.dataTransfer.files;
    handleFileUpload(files);
  });

  function handleFileUpload(files) {
    // Handle file upload logic here
    console.log('Files to upload:', files);
  }
});
```

---

## 📊 **5. Analytics & Reporting - Technical Specifications**

### **Layout Structure**
```html
<div class="analytics-dashboard">
  <div class="analytics-header">
    <h1 class="page-title">Admin panel</h1>
    <div class="header-controls">
      <div class="date-range">
        <span class="date-text">Apr 24, 2023 — Apr 24, 2024</span>
        <button class="date-button">📅</button>
      </div>
      <div class="format-selector">
        <label class="format-label">Format</label>
        <select class="format-select">
          <option>PDF</option>
          <option>Excel</option>
          <option>CSV</option>
        </select>
      </div>
      <button class="export-button">
        <span class="export-icon">📤</span>
        Export
      </button>
    </div>
  </div>

  <!-- Tab Navigation -->
  <div class="analytics-tabs">
    <button class="analytics-tab active" data-tab="overview">OVERVIEW</button>
    <button class="analytics-tab" data-tab="users">USERS</button>
    <button class="analytics-tab" data-tab="financial">FINANCIAL</button>
    <button class="analytics-tab" data-tab="technical">TECHNICAL</button>
  </div>

  <!-- Overview Tab Content -->
  <div class="tab-panel active" id="overview-panel">
    <!-- Key Metrics -->
    <div class="metrics-row">
      <div class="metric-card metric-large">
        <h3 class="metric-title">Total Revenue</h3>
        <div class="metric-value metric-green">$1,250,300</div>
      </div>
      <div class="metric-card">
        <h3 class="metric-title">User Growth</h3>
        <div class="metric-value metric-green">8.5%</div>
      </div>
      <div class="metric-card">
        <h3 class="metric-title">Conversion Rate</h3>
        <div class="metric-value metric-blue">3.2%</div>
      </div>
    </div>

    <!-- Charts Grid -->
    <div class="charts-grid">
      <!-- User Engagement Chart -->
      <div class="chart-container">
        <div class="chart-header">
          <h3 class="chart-title">User Engagement</h3>
          <div class="chart-controls">
            <button class="time-filter active">1W</button>
            <button class="time-filter">Year</button>
          </div>
        </div>
        <div class="chart-wrapper">
          <canvas id="userEngagementChart"></canvas>
        </div>
      </div>

      <!-- Revenue Trends Chart -->
      <div class="chart-container">
        <div class="chart-header">
          <h3 class="chart-title">Revenue Trends</h3>
        </div>
        <div class="chart-wrapper">
          <canvas id="revenueTrendsChart"></canvas>
        </div>
      </div>

      <!-- Traffic Sources Chart -->
      <div class="chart-container">
        <div class="chart-header">
          <h3 class="chart-title">Traffic Sources</h3>
        </div>
        <div class="chart-wrapper">
          <div class="pie-chart-container">
            <canvas id="trafficSourcesChart"></canvas>
            <div class="chart-legend">
              <div class="legend-item">
                <span class="legend-color" style="background: #007BFF;"></span>
                <span class="legend-label">Direct</span>
                <span class="legend-value">56.2%</span>
              </div>
              <div class="legend-item">
                <span class="legend-color" style="background: #28A745;"></span>
                <span class="legend-label">Referral</span>
                <span class="legend-value">24.5%</span>
              </div>
              <div class="legend-item">
                <span class="legend-color" style="background: #FFC107;"></span>
                <span class="legend-label">Organic</span>
                <span class="legend-value">19.3%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- User Behavior Chart -->
      <div class="chart-container">
        <div class="chart-header">
          <h3 class="chart-title">User Behavior</h3>
        </div>
        <div class="chart-wrapper">
          <canvas id="userBehaviorChart"></canvas>
        </div>
      </div>
    </div>

    <!-- Scheduled Reports Section -->
    <div class="scheduled-reports">
      <div class="reports-header">
        <h3 class="reports-title">Scheduled Reports</h3>
        <span class="reports-status">🟢</span>
      </div>
      <div class="report-item">
        <span class="report-date">Apr 24, 2023</span>
        <span class="report-format">CSV</span>
        <button class="report-action">☰</button>
      </div>
    </div>

    <!-- User Behavior Heatmap -->
    <div class="heatmap-section">
      <h3 class="section-title">User Behavior</h3>
      <div class="heatmap-grid">
        <!-- Heatmap visualization would go here -->
        <div class="heatmap-placeholder"></div>
      </div>
    </div>
  </div>
</div>
```

### **CSS Specifications**
```css
.analytics-dashboard {
  padding: var(--space-6);
  background: var(--bg-primary);
  min-height: 100vh;
}

.analytics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-8);
}

.header-controls {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.date-range {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
}

.date-text {
  font-size: var(--text-sm);
  color: var(--text-primary);
  font-weight: var(--font-medium);
}

.date-button {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: var(--text-base);
}

.format-selector {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.format-label {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  font-weight: var(--font-medium);
}

.format-select {
  padding: var(--space-2) var(--space-3);
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: var(--text-sm);
}

.export-button {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  background: var(--accent-blue);
  color: var(--text-primary);
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.export-button:hover {
  background: #0056b3;
}

/* Analytics Tabs */
.analytics-tabs {
  display: flex;
  border-bottom: 1px solid var(--border-primary);
  margin-bottom: var(--space-8);
}

.analytics-tab {
  padding: var(--space-4) var(--space-6);
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  letter-spacing: 0.05em;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s ease;
}

.analytics-tab:hover {
  color: var(--text-primary);
}

.analytics-tab.active {
  color: var(--accent-blue);
  border-bottom-color: var(--accent-blue);
}

/* Tab Panels */
.tab-panel {
  display: none;
}

.tab-panel.active {
  display: block;
}

/* Metrics Row */
.metrics-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: var(--space-6);
  margin-bottom: var(--space-8);
}

.metric-card {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  padding: var(--space-6);
}

.metric-large {
  padding: var(--space-8);
}

.metric-title {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
  margin: 0 0 var(--space-3) 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.metric-value {
  font-size: var(--text-4xl);
  font-weight: var(--font-bold);
  font-family: var(--font-mono);
  margin: 0;
}

.metric-green {
  color: var(--accent-green);
}

.metric-blue {
  color: var(--accent-blue);
}

/* Charts Grid */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-6);
  margin-bottom: var(--space-8);
}

.chart-container {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  overflow: hidden;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4) var(--space-6);
  border-bottom: 1px solid var(--border-primary);
  background: var(--bg-tertiary);
}

.chart-title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0;
}

.chart-controls {
  display: flex;
  gap: var(--space-2);
}

.time-filter {
  padding: var(--space-1) var(--space-3);
  background: none;
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: all 0.2s ease;
}

.time-filter:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.time-filter.active {
  background: var(--accent-blue);
  color: var(--text-primary);
  border-color: var(--accent-blue);
}

.chart-wrapper {
  padding: var(--space-6);
  height: 300px;
}

/* Pie Chart Container */
.pie-chart-container {
  display: flex;
  align-items: center;
  gap: var(--space-6);
  height: 100%;
}

.chart-legend {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: var(--radius-sm);
}

.legend-label {
  font-size: var(--text-sm);
  color: var(--text-primary);
  font-weight: var(--font-medium);
  min-width: 60px;
}

.legend-value {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  font-weight: var(--font-medium);
}

/* Scheduled Reports */
.scheduled-reports {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  padding: var(--space-6);
  margin-bottom: var(--space-8);
}

.reports-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.reports-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0;
}

.reports-status {
  font-size: var(--text-sm);
}

.report-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3);
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-primary);
}

.report-date {
  font-size: var(--text-sm);
  color: var(--text-primary);
  font-weight: var(--font-medium);
}

.report-format {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  background: var(--bg-primary);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
}

.report-action {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: var(--text-base);
}

/* Heatmap Section */
.heatmap-section {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  padding: var(--space-6);
}

.section-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-6) 0;
}

.heatmap-grid {
  height: 200px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
}

.heatmap-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    var(--bg-tertiary) 0%,
    var(--accent-green) 25%,
    var(--accent-yellow) 50%,
    var(--accent-orange) 75%,
    var(--accent-red) 100%
  );
  opacity: 0.3;
  border-radius: var(--radius-md);
}

/* Responsive Design */
@media (max-width: 1024px) {
  .metrics-row {
    grid-template-columns: 1fr;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .pie-chart-container {
    flex-direction: column;
    gap: var(--space-4);
  }
}

@media (max-width: 768px) {
  .analytics-header {
    flex-direction: column;
    gap: var(--space-4);
    align-items: stretch;
  }
  
  .header-controls {
    flex-wrap: wrap;
  }
  
  .analytics-tabs {
    overflow-x: auto;
  }
}
```

### **JavaScript for Charts**
```javascript
// User Engagement Chart
const userEngagementCtx = document.getElementById('userEngagementChart').getContext('2d');
new Chart(userEngagementCtx, {
  type: 'line',
  data: {
    labels: ['Jan', 'Feb', 'Apr', 'Apr', 'May', 'Jun', 'Jul', 'Sep'],
    datasets: [{
      label: 'User Engagement',
      data: [1000, 1200, 1100, 1400, 1600, 1800, 2000, 2500],
      borderColor: '#007BFF',
      backgroundColor: 'rgba(0, 123, 255, 0.1)',
      borderWidth: 3,
      fill: true,
      tension: 0.4,
      pointBackgroundColor: '#007BFF',
      pointBorderColor: '#FFFFFF',
      pointBorderWidth: 2,
      pointRadius: 6
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
            size: 12
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
            size: 12
          },
          callback: function(value) {
            return value.toLocaleString();
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

// Revenue Trends Chart
const revenueTrendsCtx = document.getElementById('revenueTrendsChart').getContext('2d');
new Chart(revenueTrendsCtx, {
  type: 'bar',
  data: {
    labels: ['Mar', 'May', 'Jun', 'Sep', 'Sep'],
    datasets: [{
      label: 'Revenue',
      data: [8000, 12000, 15000, 18000, 22000],
      backgroundColor: '#28A745',
      borderRadius: 6,
      borderSkipped: false
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
            size: 12
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
            size: 12
          },
          callback: function(value) {
            return '$' + (value / 1000) + 'k';
          }
        }
      }
    }
  }
});

// Traffic Sources Pie Chart
const trafficSourcesCtx = document.getElementById('trafficSourcesChart').getContext('2d');
new Chart(trafficSourcesCtx, {
  type: 'doughnut',
  data: {
    labels: ['Direct', 'Referral', 'Organic'],
    datasets: [{
      data: [56.2, 24.5, 19.3],
      backgroundColor: ['#007BFF', '#28A745', '#FFC107'],
      borderWidth: 0,
      cutout: '60%'
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      }
    }
  }
});

// User Behavior Chart
const userBehaviorCtx = document.getElementById('userBehaviorChart').getContext('2d');
new Chart(userBehaviorCtx, {
  type: 'line',
  data: {
    labels: ['Jan', 'Feb', 'Apr', 'Apr'],
    datasets: [{
      label: 'User Behavior',
      data: [300, 450, 600, 750],
      borderColor: '#28A745',
      backgroundColor: 'rgba(40, 167, 69, 0.1)',
      borderWidth: 3,
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
            size: 12
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
            size: 12
          }
        }
      }
    }
  }
});

// Tab switching functionality
document.addEventListener('DOMContentLoaded', function() {
  const tabs = document.querySelectorAll('.analytics-tab');
  const panels = document.querySelectorAll('.tab-panel');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const targetPanel = tab.dataset.tab;
      
      // Remove active class from all tabs and panels
      tabs.forEach(t => t.classList.remove('active'));
      panels.forEach(p => p.classList.remove('active'));
      
      // Add active class to clicked tab and corresponding panel
      tab.classList.add('active');
      document.getElementById(`${targetPanel}-panel`).classList.add('active');
    });
  });
});
```

This completes the detailed technical specifications for the Content Management and Analytics sections. Would you like me to continue with the remaining sections (Settings, Security, Data Management, and Mobile Responsive)?
