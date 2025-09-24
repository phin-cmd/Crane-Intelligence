# Crane Intelligence Admin Panel - Technical Specifications (Part 3)

## ⚙️ **6. Platform Settings - Technical Specifications**

### **Layout Structure**
```html
<div class="settings-management">
  <div class="settings-header">
    <h1 class="page-title">Platform Settings</h1>
  </div>

  <!-- Settings Tab Navigation -->
  <div class="settings-tabs">
    <button class="settings-tab active" data-tab="general">General</button>
    <button class="settings-tab" data-tab="api">API</button>
    <button class="settings-tab" data-tab="email">Email</button>
    <button class="settings-tab" data-tab="billing">Billing</button>
    <button class="settings-tab" data-tab="advanced">Advanced</button>
  </div>

  <!-- General Settings Tab -->
  <div class="settings-content active" id="general-tab">
    <div class="settings-grid">
      <!-- Site Configuration -->
      <div class="settings-card">
        <div class="card-header">
          <h3 class="card-title">Site Configuration</h3>
        </div>
        <div class="card-content">
          <div class="form-group">
            <label class="form-label">Company Name</label>
            <input type="text" class="form-input" value="Crane Intelligence" />
          </div>
          <div class="form-group">
            <label class="form-label">Site Logo</label>
            <div class="file-upload">
              <input type="file" class="file-input" id="logo-upload" />
              <label for="logo-upload" class="file-label">
                <span class="upload-icon">📁</span>
                Choose File
              </label>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Brand Colors</label>
            <div class="color-picker-group">
              <input type="color" class="color-picker" value="#007BFF" />
              <input type="color" class="color-picker" value="#28A745" />
              <input type="color" class="color-picker" value="#FD7E14" />
            </div>
          </div>
        </div>
      </div>

      <!-- Localization -->
      <div class="settings-card">
        <div class="card-header">
          <h3 class="card-title">Localization</h3>
        </div>
        <div class="card-content">
          <div class="form-group">
            <label class="form-label">Timezone</label>
            <select class="form-select">
              <option>UTC-5 (Eastern Time)</option>
              <option>UTC-8 (Pacific Time)</option>
              <option>UTC+0 (GMT)</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Language</label>
            <select class="form-select">
              <option>English (US)</option>
              <option>English (UK)</option>
              <option>Spanish</option>
              <option>French</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Date Format</label>
            <select class="form-select">
              <option>MM/DD/YYYY</option>
              <option>DD/MM/YYYY</option>
              <option>YYYY-MM-DD</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Maintenance Mode -->
      <div class="settings-card">
        <div class="card-header">
          <h3 class="card-title">Maintenance Mode</h3>
        </div>
        <div class="card-content">
          <div class="toggle-group">
            <label class="toggle-label">Enable Maintenance Mode</label>
            <label class="toggle-switch">
              <input type="checkbox" />
              <span class="toggle-slider"></span>
            </label>
          </div>
          <div class="form-group">
            <label class="form-label">Maintenance Message</label>
            <textarea class="form-textarea" placeholder="Site is under maintenance..."></textarea>
          </div>
          <div class="form-group">
            <label class="form-label">Estimated Downtime</label>
            <input type="text" class="form-input" placeholder="2 hours" />
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- API Settings Tab -->
  <div class="settings-content" id="api-tab">
    <div class="settings-grid">
      <!-- Third-party Integrations -->
      <div class="settings-card">
        <div class="card-header">
          <h3 class="card-title">Third-party Integrations</h3>
        </div>
        <div class="card-content">
          <div class="integration-item">
            <div class="integration-info">
              <span class="integration-name">Google Analytics</span>
              <span class="integration-status status-connected">Connected</span>
            </div>
            <button class="btn btn-secondary btn-sm">Configure</button>
          </div>
          <div class="integration-item">
            <div class="integration-info">
              <span class="integration-name">Stripe</span>
              <span class="integration-status status-connected">Connected</span>
            </div>
            <button class="btn btn-secondary btn-sm">Configure</button>
          </div>
          <div class="integration-item">
            <div class="integration-info">
              <span class="integration-name">SendGrid</span>
              <span class="integration-status status-disconnected">Disconnected</span>
            </div>
            <button class="btn btn-primary btn-sm">Connect</button>
          </div>
        </div>
      </div>

      <!-- API Keys -->
      <div class="settings-card">
        <div class="card-header">
          <h3 class="card-title">API Key Management</h3>
        </div>
        <div class="card-content">
          <div class="api-key-item">
            <div class="api-key-info">
              <span class="api-key-name">Production API Key</span>
              <span class="api-key-value">sk_live_••••••••••••••••</span>
            </div>
            <div class="api-key-actions">
              <button class="btn btn-secondary btn-sm">Regenerate</button>
              <button class="btn btn-danger btn-sm">Revoke</button>
            </div>
          </div>
          <div class="api-key-item">
            <div class="api-key-info">
              <span class="api-key-name">Test API Key</span>
              <span class="api-key-value">sk_test_••••••••••••••••</span>
            </div>
            <div class="api-key-actions">
              <button class="btn btn-secondary btn-sm">Regenerate</button>
              <button class="btn btn-danger btn-sm">Revoke</button>
            </div>
          </div>
          <button class="btn btn-primary">Generate New Key</button>
        </div>
      </div>

      <!-- Rate Limiting -->
      <div class="settings-card">
        <div class="card-header">
          <h3 class="card-title">Rate Limiting</h3>
        </div>
        <div class="card-content">
          <div class="form-group">
            <label class="form-label">Requests per Minute</label>
            <input type="number" class="form-input" value="1000" />
          </div>
          <div class="form-group">
            <label class="form-label">Burst Limit</label>
            <input type="number" class="form-input" value="2000" />
          </div>
          <div class="toggle-group">
            <label class="toggle-label">Enable Rate Limiting</label>
            <label class="toggle-switch">
              <input type="checkbox" checked />
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Email Settings Tab -->
  <div class="settings-content" id="email-tab">
    <div class="settings-grid">
      <!-- SMTP Configuration -->
      <div class="settings-card">
        <div class="card-header">
          <h3 class="card-title">SMTP Configuration</h3>
        </div>
        <div class="card-content">
          <div class="form-group">
            <label class="form-label">SMTP Host</label>
            <input type="text" class="form-input" value="smtp.gmail.com" />
          </div>
          <div class="form-group">
            <label class="form-label">SMTP Port</label>
            <input type="number" class="form-input" value="587" />
          </div>
          <div class="form-group">
            <label class="form-label">Username</label>
            <input type="email" class="form-input" value="admin@craneintelligence.com" />
          </div>
          <div class="form-group">
            <label class="form-label">Password</label>
            <input type="password" class="form-input" value="••••••••" />
          </div>
          <div class="toggle-group">
            <label class="toggle-label">Use SSL/TLS</label>
            <label class="toggle-switch">
              <input type="checkbox" checked />
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>
      </div>

      <!-- Email Templates -->
      <div class="settings-card">
        <div class="card-header">
          <h3 class="card-title">Email Templates</h3>
        </div>
        <div class="card-content">
          <div class="template-list">
            <div class="template-item">
              <span class="template-name">Welcome Email</span>
              <button class="btn btn-secondary btn-sm">Edit</button>
            </div>
            <div class="template-item">
              <span class="template-name">Password Reset</span>
              <button class="btn btn-secondary btn-sm">Edit</button>
            </div>
            <div class="template-item">
              <span class="template-name">Account Verification</span>
              <button class="btn btn-secondary btn-sm">Edit</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Delivery Settings -->
      <div class="settings-card">
        <div class="card-header">
          <h3 class="card-title">Delivery Settings</h3>
        </div>
        <div class="card-content">
          <div class="form-group">
            <label class="form-label">From Name</label>
            <input type="text" class="form-input" value="Crane Intelligence" />
          </div>
          <div class="form-group">
            <label class="form-label">From Email</label>
            <input type="email" class="form-input" value="noreply@craneintelligence.com" />
          </div>
          <div class="form-group">
            <label class="form-label">Reply-To Email</label>
            <input type="email" class="form-input" value="support@craneintelligence.com" />
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Save Button -->
  <div class="settings-footer">
    <button class="btn btn-primary btn-large">Save All Settings</button>
  </div>
</div>
```

### **CSS Specifications**
```css
.settings-management {
  padding: var(--space-6);
  background: var(--bg-primary);
  min-height: 100vh;
}

.settings-header {
  margin-bottom: var(--space-8);
}

/* Settings Tabs */
.settings-tabs {
  display: flex;
  border-bottom: 1px solid var(--border-primary);
  margin-bottom: var(--space-8);
}

.settings-tab {
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

.settings-tab:hover {
  color: var(--text-primary);
}

.settings-tab.active {
  color: var(--accent-blue);
  border-bottom-color: var(--accent-blue);
}

/* Settings Content */
.settings-content {
  display: none;
}

.settings-content.active {
  display: block;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: var(--space-6);
  margin-bottom: var(--space-8);
}

/* Settings Cards */
.settings-card {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  overflow: hidden;
}

.card-header {
  padding: var(--space-4) var(--space-6);
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-primary);
}

.card-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0;
}

.card-content {
  padding: var(--space-6);
}

/* Form Elements */
.form-group {
  margin-bottom: var(--space-5);
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
  padding: var(--space-3) var(--space-4);
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: var(--text-base);
  transition: border-color 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--accent-blue);
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.form-select {
  width: 100%;
  padding: var(--space-3) var(--space-4);
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: var(--text-base);
  cursor: pointer;
}

.form-textarea {
  width: 100%;
  min-height: 100px;
  padding: var(--space-3) var(--space-4);
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: var(--text-base);
  resize: vertical;
  font-family: inherit;
}

.form-textarea:focus {
  outline: none;
  border-color: var(--accent-blue);
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

/* File Upload */
.file-upload {
  position: relative;
}

.file-input {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.file-label {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.file-label:hover {
  background: var(--bg-hover);
}

.upload-icon {
  font-size: var(--text-base);
}

/* Color Picker Group */
.color-picker-group {
  display: flex;
  gap: var(--space-3);
}

.color-picker {
  width: 50px;
  height: 40px;
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  cursor: pointer;
  background: none;
}

/* Toggle Switch */
.toggle-group {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.toggle-label {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-primary);
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 28px;
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
  background-color: var(--bg-tertiary);
  transition: 0.3s;
  border-radius: 28px;
  border: 1px solid var(--border-primary);
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 20px;
  width: 20px;
  left: 3px;
  bottom: 3px;
  background-color: var(--text-primary);
  transition: 0.3s;
  border-radius: 50%;
}

input:checked + .toggle-slider {
  background-color: var(--accent-blue);
  border-color: var(--accent-blue);
}

input:checked + .toggle-slider:before {
  transform: translateX(22px);
}

/* Integration Items */
.integration-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4);
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-primary);
  margin-bottom: var(--space-3);
}

.integration-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.integration-name {
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  color: var(--text-primary);
}

.integration-status {
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  text-transform: uppercase;
  padding: 2px 6px;
  border-radius: var(--radius-sm);
}

.status-connected {
  background: rgba(40, 167, 69, 0.2);
  color: var(--accent-green);
}

.status-disconnected {
  background: rgba(220, 53, 69, 0.2);
  color: var(--accent-red);
}

/* API Key Items */
.api-key-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4);
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-primary);
  margin-bottom: var(--space-3);
}

.api-key-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.api-key-name {
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  color: var(--text-primary);
}

.api-key-value {
  font-size: var(--text-sm);
  color: var(--text-muted);
  font-family: var(--font-mono);
}

.api-key-actions {
  display: flex;
  gap: var(--space-2);
}

/* Template List */
.template-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.template-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3);
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-primary);
}

.template-name {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-primary);
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

.btn-sm {
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-xs);
}

.btn-large {
  padding: var(--space-4) var(--space-8);
  font-size: var(--text-lg);
}

/* Settings Footer */
.settings-footer {
  display: flex;
  justify-content: center;
  padding: var(--space-8) 0;
  border-top: 1px solid var(--border-primary);
}

/* Responsive Design */
@media (max-width: 768px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }
  
  .settings-tabs {
    overflow-x: auto;
  }
  
  .integration-item,
  .api-key-item,
  .template-item {
    flex-direction: column;
    gap: var(--space-3);
    align-items: stretch;
  }
  
  .api-key-actions {
    justify-content: center;
  }
}
```

---

## 🔒 **7. Security & Access Control - Technical Specifications**

### **Layout Structure**
```html
<div class="security-dashboard">
  <div class="security-header">
    <h1 class="page-title">Security & Access Control</h1>
  </div>

  <!-- Security Overview -->
  <div class="security-overview">
    <div class="security-score-card">
      <div class="score-container">
        <div class="score-circle">
          <div class="score-value">92</div>
          <div class="score-label">Security Score</div>
        </div>
      </div>
      <div class="score-details">
        <div class="score-item">
          <span class="score-metric">Authentication</span>
          <span class="score-status status-excellent">Excellent</span>
        </div>
        <div class="score-item">
          <span class="score-metric">Access Control</span>
          <span class="score-status status-good">Good</span>
        </div>
        <div class="score-item">
          <span class="score-metric">Data Protection</span>
          <span class="score-status status-excellent">Excellent</span>
        </div>
      </div>
    </div>

    <div class="recent-events">
      <h3 class="events-title">Recent Security Events</h3>
      <div class="event-list">
        <div class="event-item">
          <div class="event-icon event-success">✓</div>
          <div class="event-details">
            <span class="event-description">Successful login from 192.168.1.100</span>
            <span class="event-time">2 minutes ago</span>
          </div>
        </div>
        <div class="event-item">
          <div class="event-icon event-warning">⚠</div>
          <div class="event-details">
            <span class="event-description">Failed login attempt from 203.0.113.1</span>
            <span class="event-time">15 minutes ago</span>
          </div>
        </div>
        <div class="event-item">
          <div class="event-icon event-info">ℹ</div>
          <div class="event-details">
            <span class="event-description">Password changed for user@example.com</span>
            <span class="event-time">1 hour ago</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Security Sections -->
  <div class="security-sections">
    <!-- Role Management -->
    <div class="security-section">
      <div class="section-header">
        <h3 class="section-title">Role Management</h3>
        <button class="btn btn-primary btn-sm">Add Role</button>
      </div>
      
      <div class="permissions-matrix">
        <table class="permissions-table">
          <thead>
            <tr>
              <th>Permission</th>
              <th>Admin</th>
              <th>Manager</th>
              <th>User</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="permission-name">Dashboard Access</td>
              <td class="permission-cell">
                <span class="permission-granted">✓</span>
              </td>
              <td class="permission-cell">
                <span class="permission-granted">✓</span>
              </td>
              <td class="permission-cell">
                <span class="permission-granted">✓</span>
              </td>
            </tr>
            <tr>
              <td class="permission-name">User Management</td>
              <td class="permission-cell">
                <span class="permission-granted">✓</span>
              </td>
              <td class="permission-cell">
                <span class="permission-limited">◐</span>
              </td>
              <td class="permission-cell">
                <span class="permission-denied">✗</span>
              </td>
            </tr>
            <tr>
              <td class="permission-name">Content Management</td>
              <td class="permission-cell">
                <span class="permission-granted">✓</span>
              </td>
              <td class="permission-cell">
                <span class="permission-granted">✓</span>
              </td>
              <td class="permission-cell">
                <span class="permission-limited">◐</span>
              </td>
            </tr>
            <tr>
              <td class="permission-name">Analytics</td>
              <td class="permission-cell">
                <span class="permission-granted">✓</span>
              </td>
              <td class="permission-cell">
                <span class="permission-granted">✓</span>
              </td>
              <td class="permission-cell">
                <span class="permission-denied">✗</span>
              </td>
            </tr>
            <tr>
              <td class="permission-name">System Settings</td>
              <td class="permission-cell">
                <span class="permission-granted">✓</span>
              </td>
              <td class="permission-cell">
                <span class="permission-denied">✗</span>
              </td>
              <td class="permission-cell">
                <span class="permission-denied">✗</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Access Control -->
    <div class="security-section">
      <div class="section-header">
        <h3 class="section-title">Access Control</h3>
      </div>
      
      <div class="access-control-grid">
        <div class="access-card">
          <h4 class="access-title">IP Whitelist</h4>
          <div class="ip-list">
            <div class="ip-item">
              <span class="ip-address">192.168.1.0/24</span>
              <button class="ip-remove">✗</button>
            </div>
            <div class="ip-item">
              <span class="ip-address">10.0.0.0/8</span>
              <button class="ip-remove">✗</button>
            </div>
          </div>
          <div class="ip-add">
            <input type="text" class="ip-input" placeholder="Add IP address" />
            <button class="btn btn-primary btn-sm">Add</button>
          </div>
        </div>

        <div class="access-card">
          <h4 class="access-title">IP Blacklist</h4>
          <div class="ip-list">
            <div class="ip-item">
              <span class="ip-address">203.0.113.1</span>
              <button class="ip-remove">✗</button>
            </div>
            <div class="ip-item">
              <span class="ip-address">198.51.100.0/24</span>
              <button class="ip-remove">✗</button>
            </div>
          </div>
          <div class="ip-add">
            <input type="text" class="ip-input" placeholder="Add IP address" />
            <button class="btn btn-primary btn-sm">Add</button>
          </div>
        </div>

        <div class="access-card">
          <h4 class="access-title">Geographic Restrictions</h4>
          <div class="geo-list">
            <div class="geo-item">
              <span class="geo-country">China</span>
              <span class="geo-status status-blocked">Blocked</span>
            </div>
            <div class="geo-item">
              <span class="geo-country">Russia</span>
              <span class="geo-status status-blocked">Blocked</span>
            </div>
            <div class="geo-item">
              <span class="geo-country">North Korea</span>
              <span class="geo-status status-blocked">Blocked</span>
            </div>
          </div>
        </div>

        <div class="access-card">
          <h4 class="access-title">Session Management</h4>
          <div class="session-settings">
            <div class="setting-item">
              <span class="setting-label">Session Timeout</span>
              <select class="setting-select">
                <option>30 minutes</option>
                <option>1 hour</option>
                <option>2 hours</option>
                <option>4 hours</option>
              </select>
            </div>
            <div class="setting-item">
              <span class="setting-label">Max Concurrent Sessions</span>
              <input type="number" class="setting-input" value="3" />
            </div>
            <div class="setting-item">
              <span class="setting-label">Force Logout on IP Change</span>
              <label class="toggle-switch">
                <input type="checkbox" checked />
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- GDPR Compliance -->
    <div class="security-section">
      <div class="section-header">
        <h3 class="section-title">GDPR Compliance</h3>
      </div>
      
      <div class="gdpr-grid">
        <div class="gdpr-card">
          <h4 class="gdpr-title">Data Export Requests</h4>
          <div class="gdpr-stats">
            <div class="stat-item">
              <span class="stat-value">12</span>
              <span class="stat-label">Pending</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">45</span>
              <span class="stat-label">Completed</span>
            </div>
          </div>
          <button class="btn btn-secondary">View Requests</button>
        </div>

        <div class="gdpr-card">
          <h4 class="gdpr-title">Data Deletion Requests</h4>
          <div class="gdpr-stats">
            <div class="stat-item">
              <span class="stat-value">3</span>
              <span class="stat-label">Pending</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">18</span>
              <span class="stat-label">Completed</span>
            </div>
          </div>
          <button class="btn btn-secondary">View Requests</button>
        </div>

        <div class="gdpr-card">
          <h4 class="gdpr-title">Consent Management</h4>
          <div class="consent-stats">
            <div class="consent-item">
              <span class="consent-type">Marketing</span>
              <span class="consent-percentage">78%</span>
            </div>
            <div class="consent-item">
              <span class="consent-type">Analytics</span>
              <span class="consent-percentage">92%</span>
            </div>
            <div class="consent-item">
              <span class="consent-type">Functional</span>
              <span class="consent-percentage">95%</span>
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
.security-dashboard {
  padding: var(--space-6);
  background: var(--bg-primary);
  min-height: 100vh;
}

.security-header {
  margin-bottom: var(--space-8);
}

/* Security Overview */
.security-overview {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-6);
  margin-bottom: var(--space-8);
}

.security-score-card {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  padding: var(--space-6);
  display: flex;
  gap: var(--space-6);
}

.score-container {
  display: flex;
  align-items: center;
  justify-content: center;
}

.score-circle {
  width: 120px;
  height: 120px;
  border-radius: var(--radius-full);
  background: conic-gradient(
    var(--accent-green) 0deg,
    var(--accent-green) 331.2deg,
    var(--bg-tertiary) 331.2deg,
    var(--bg-tertiary) 360deg
  );
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
}

.score-circle::before {
  content: '';
  position: absolute;
  width: 80px;
  height: 80px;
  background: var(--bg-secondary);
  border-radius: var(--radius-full);
}

.score-value {
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  z-index: 1;
}

.score-label {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  font-weight: var(--font-medium);
  z-index: 1;
}

.score-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.score-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.score-metric {
  font-size: var(--text-sm);
  color: var(--text-primary);
  font-weight: var(--font-medium);
}

.score-status {
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  text-transform: uppercase;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
}

.status-excellent {
  background: rgba(40, 167, 69, 0.2);
  color: var(--accent-green);
}

.status-good {
  background: rgba(253, 126, 20, 0.2);
  color: var(--accent-orange);
}

/* Recent Events */
.recent-events {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  padding: var(--space-6);
}

.events-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-4) 0;
}

.event-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.event-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
}

.event-icon {
  width: 24px;
  height: 24px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
}

.event-success {
  background: var(--accent-green);
  color: var(--text-primary);
}

.event-warning {
  background: var(--accent-orange);
  color: var(--text-primary);
}

.event-info {
  background: var(--accent-blue);
  color: var(--text-primary);
}

.event-details {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.event-description {
  font-size: var(--text-sm);
  color: var(--text-primary);
  font-weight: var(--font-medium);
}

.event-time {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

/* Security Sections */
.security-sections {
  display: flex;
  flex-direction: column;
  gap: var(--space-8);
}

.security-section {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  padding: var(--space-6);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-6);
}

.section-title {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0;
}

/* Permissions Matrix */
.permissions-matrix {
  overflow-x: auto;
}

.permissions-table {
  width: 100%;
  border-collapse: collapse;
}

.permissions-table th {
  padding: var(--space-3) var(--space-4);
  text-align: left;
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-secondary);
  text-transform: uppercase;
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-primary);
}

.permissions-table th:first-child {
  text-align: left;
}

.permissions-table th:not(:first-child) {
  text-align: center;
}

.permissions-table td {
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--border-primary);
}

.permission-name {
  font-size: var(--text-sm);
  color: var(--text-primary);
  font-weight: var(--font-medium);
}

.permission-cell {
  text-align: center;
}

.permission-granted {
  color: var(--accent-green);
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
}

.permission-limited {
  color: var(--accent-orange);
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
}

.permission-denied {
  color: var(--accent-red);
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
}

/* Access Control Grid */
.access-control-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-6);
}

.access-card {
  background: var(--bg-tertiary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  padding: var(--space-5);
}

.access-title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-4) 0;
}

/* IP Lists */
.ip-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  margin-bottom: var(--space-4);
}

.ip-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-2) var(--space-3);
  background: var(--bg-primary);
  border-radius: var(--radius-md);
}

.ip-address {
  font-size: var(--text-sm);
  color: var(--text-primary);
  font-family: var(--font-mono);
}

.ip-remove {
  background: none;
  border: none;
  color: var(--accent-red);
  cursor: pointer;
  font-size: var(--text-sm);
  padding: var(--space-1);
}

.ip-add {
  display: flex;
  gap: var(--space-2);
}

.ip-input {
  flex: 1;
  padding: var(--space-2) var(--space-3);
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: var(--text-sm);
  font-family: var(--font-mono);
}

/* Geographic Restrictions */
.geo-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.geo-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-2) var(--space-3);
  background: var(--bg-primary);
  border-radius: var(--radius-md);
}

.geo-country {
  font-size: var(--text-sm);
  color: var(--text-primary);
  font-weight: var(--font-medium);
}

.geo-status {
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  text-transform: uppercase;
  padding: 2px 6px;
  border-radius: var(--radius-sm);
}

.status-blocked {
  background: rgba(220, 53, 69, 0.2);
  color: var(--accent-red);
}

/* Session Settings */
.session-settings {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.setting-label {
  font-size: var(--text-sm);
  color: var(--text-primary);
  font-weight: var(--font-medium);
}

.setting-select {
  padding: var(--space-1) var(--space-2);
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: var(--text-sm);
}

.setting-input {
  width: 80px;
  padding: var(--space-1) var(--space-2);
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: var(--text-sm);
  text-align: center;
}

/* GDPR Grid */
.gdpr-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-6);
}

.gdpr-card {
  background: var(--bg-tertiary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  padding: var(--space-5);
  text-align: center;
}

.gdpr-title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-4) 0;
}

.gdpr-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: var(--space-4);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-1);
}

.stat-value {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--accent-blue);
}

.stat-label {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  text-transform: uppercase;
}

.consent-stats {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

.consent-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.consent-type {
  font-size: var(--text-sm);
  color: var(--text-primary);
  font-weight: var(--font-medium);
}

.consent-percentage {
  font-size: var(--text-sm);
  color: var(--accent-green);
  font-weight: var(--font-bold);
}

/* Responsive Design */
@media (max-width: 1024px) {
  .security-overview {
    grid-template-columns: 1fr;
  }
  
  .access-control-grid {
    grid-template-columns: 1fr;
  }
  
  .gdpr-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .security-score-card {
    flex-direction: column;
    text-align: center;
  }
  
  .permissions-matrix {
    font-size: var(--text-xs);
  }
  
  .permissions-table th,
  .permissions-table td {
    padding: var(--space-2);
  }
}
```

This completes the comprehensive technical specifications for the Platform Settings and Security & Access Control sections. The specifications include exact measurements, colors, typography, layout structures, and responsive design considerations that developers can use to build the admin panel exactly as designed.

Would you like me to continue with the final sections (Data Management and Mobile Responsive design) to complete the full technical documentation?
