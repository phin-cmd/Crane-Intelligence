# Crane Intelligence Admin Panel - Technical Design Specifications

## 🎨 **Global Design System**

### **Color Palette (Exact Values)**
```css
:root {
  /* Primary Colors */
  --bg-primary: #1A1A1A;           /* Main background */
  --bg-secondary: #2A2A2A;         /* Card backgrounds */
  --bg-tertiary: #333333;          /* Elevated elements */
  --bg-hover: #404040;             /* Hover states */
  
  /* Accent Colors */
  --accent-blue: #007BFF;          /* Primary actions */
  --accent-green: #28A745;         /* Success states */
  --accent-orange: #FD7E14;        /* Warnings */
  --accent-red: #DC3545;           /* Errors */
  --accent-yellow: #FFC107;        /* Attention */
  
  /* Text Colors */
  --text-primary: #FFFFFF;         /* Primary text */
  --text-secondary: #B0B0B0;       /* Secondary text */
  --text-muted: #6C757D;           /* Muted text */
  --text-inverse: #000000;         /* Inverse text */
  
  /* Border Colors */
  --border-primary: #404040;       /* Primary borders */
  --border-secondary: #555555;     /* Secondary borders */
  --border-accent: #007BFF;        /* Accent borders */
}
```

### **Typography System**
```css
/* Font Families */
--font-primary: 'Roboto Condensed', sans-serif;
--font-secondary: 'Inter', sans-serif;
--font-mono: 'Fira Code', monospace;

/* Font Sizes */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
--text-4xl: 2.25rem;   /* 36px */

/* Font Weights */
--font-light: 300;
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### **Spacing System**
```css
/* Spacing Scale */
--space-1: 0.25rem;    /* 4px */
--space-2: 0.5rem;     /* 8px */
--space-3: 0.75rem;    /* 12px */
--space-4: 1rem;       /* 16px */
--space-5: 1.25rem;    /* 20px */
--space-6: 1.5rem;     /* 24px */
--space-8: 2rem;       /* 32px */
--space-10: 2.5rem;    /* 40px */
--space-12: 3rem;      /* 48px */
--space-16: 4rem;      /* 64px */
```

### **Border Radius System**
```css
--radius-sm: 0.125rem;   /* 2px */
--radius-base: 0.25rem;  /* 4px */
--radius-md: 0.375rem;   /* 6px */
--radius-lg: 0.5rem;     /* 8px */
--radius-xl: 0.75rem;    /* 12px */
--radius-full: 9999px;   /* Full radius */
```

---

## 🔐 **1. Login Screen - Technical Specifications**

### **Layout Structure**
```html
<div class="login-container">
  <div class="login-form-wrapper">
    <div class="logo-section">
      <img src="crane-logo.svg" class="logo" />
      <h1 class="app-title">CRANE INTELLIGENCE</h1>
      <h2 class="page-title">Admin Panel</h2>
    </div>
    
    <form class="login-form">
      <div class="form-group">
        <label class="form-label">Email</label>
        <input type="email" class="form-input" placeholder="Email" />
      </div>
      
      <div class="form-group">
        <label class="form-label">Password</label>
        <div class="password-input-wrapper">
          <input type="password" class="form-input" placeholder="Password" />
          <button type="button" class="password-toggle">👁</button>
        </div>
      </div>
      
      <div class="form-options">
        <label class="checkbox-wrapper">
          <input type="checkbox" class="checkbox" />
          <span class="checkbox-label">Remember Me</span>
        </label>
        <a href="#" class="forgot-password">Forgot Password?</a>
      </div>
      
      <div class="two-factor-section">
        <h3 class="section-title">Two-Factor Authentication</h3>
        <div class="qr-code-placeholder"></div>
      </div>
      
      <button type="submit" class="login-button">Log In</button>
    </form>
    
    <div class="security-footer">
      <span class="security-text">Secured: SSL Encryption | IP Monitoring</span>
    </div>
  </div>
</div>
```

### **CSS Specifications**
```css
.login-container {
  width: 100vw;
  height: 100vh;
  background: var(--bg-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-primary);
}

.login-form-wrapper {
  width: 400px;
  padding: var(--space-8);
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
}

.logo-section {
  text-align: center;
  margin-bottom: var(--space-8);
}

.logo {
  width: 60px;
  height: 60px;
  margin-bottom: var(--space-4);
}

.app-title {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin: 0 0 var(--space-2) 0;
  letter-spacing: 0.05em;
}

.page-title {
  font-size: var(--text-lg);
  font-weight: var(--font-medium);
  color: var(--accent-yellow);
  margin: 0 0 var(--space-6) 0;
}

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

.password-input-wrapper {
  position: relative;
}

.password-toggle {
  position: absolute;
  right: var(--space-3);
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: var(--text-lg);
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-6);
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.checkbox {
  margin-right: var(--space-2);
  accent-color: var(--accent-blue);
}

.checkbox-label {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.forgot-password {
  font-size: var(--text-sm);
  color: var(--accent-blue);
  text-decoration: none;
}

.forgot-password:hover {
  text-decoration: underline;
}

.two-factor-section {
  margin-bottom: var(--space-6);
  text-align: center;
}

.section-title {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
  margin-bottom: var(--space-3);
}

.qr-code-placeholder {
  width: 80px;
  height: 80px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.qr-code-placeholder::before {
  content: "⚏";
  font-size: var(--text-2xl);
  color: var(--text-muted);
}

.login-button {
  width: 100%;
  padding: var(--space-4);
  background: var(--accent-blue);
  color: var(--text-primary);
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  cursor: pointer;
  transition: background-color 0.2s ease;
  margin-bottom: var(--space-6);
}

.login-button:hover {
  background: #0056b3;
}

.security-footer {
  text-align: center;
  padding-top: var(--space-4);
  border-top: 1px solid var(--border-primary);
}

.security-text {
  font-size: var(--text-xs);
  color: var(--text-muted);
}
```

---

## 🎛️ **2. Dashboard Overview - Technical Specifications**

### **Layout Structure**
```html
<div class="admin-layout">
  <!-- Header -->
  <header class="admin-header">
    <div class="header-left">
      <img src="crane-logo.svg" class="header-logo" />
      <span class="header-title">CRANE INTELLIGENCE</span>
    </div>
    
    <div class="header-center">
      <div class="search-wrapper">
        <input type="text" class="search-input" placeholder="Search" />
        <span class="search-icon">🔍</span>
      </div>
    </div>
    
    <div class="header-right">
      <button class="notification-button">
        <span class="notification-icon">🔔</span>
        <span class="notification-badge">3</span>
      </button>
      <div class="admin-profile">
        <span class="admin-name">Admin</span>
        <div class="admin-avatar"></div>
      </div>
    </div>
  </header>

  <!-- Sidebar -->
  <aside class="admin-sidebar">
    <nav class="sidebar-nav">
      <a href="#" class="nav-item active">
        <span class="nav-icon">🏠</span>
        <span class="nav-label">Dashboard</span>
      </a>
      <a href="#" class="nav-item">
        <span class="nav-icon">👥</span>
        <span class="nav-label">Users</span>
      </a>
      <a href="#" class="nav-item">
        <span class="nav-icon">📝</span>
        <span class="nav-label">Content</span>
      </a>
      <a href="#" class="nav-item">
        <span class="nav-icon">📊</span>
        <span class="nav-label">Analytics</span>
      </a>
      <a href="#" class="nav-item">
        <span class="nav-icon">⚙️</span>
        <span class="nav-label">Settings</span>
      </a>
      <a href="#" class="nav-item">
        <span class="nav-icon">🔒</span>
        <span class="nav-label">Security</span>
      </a>
      <a href="#" class="nav-item">
        <span class="nav-icon">🗄️</span>
        <span class="nav-label">Data</span>
      </a>
    </nav>
  </aside>

  <!-- Main Content -->
  <main class="admin-main">
    <!-- Metrics Cards -->
    <div class="metrics-grid">
      <div class="metric-card metric-card--blue">
        <div class="metric-header">
          <h3 class="metric-title">Active Users</h3>
        </div>
        <div class="metric-value">1,247</div>
      </div>
      
      <div class="metric-card metric-card--orange">
        <div class="metric-header">
          <h3 class="metric-title">Revenue</h3>
        </div>
        <div class="metric-value">$45,230</div>
      </div>
      
      <div class="metric-card metric-card--green">
        <div class="metric-header">
          <h3 class="metric-title">System Health</h3>
        </div>
        <div class="metric-value">98%</div>
      </div>
      
      <div class="metric-card metric-card--orange">
        <div class="metric-header">
          <h3 class="metric-title">Storage Used</h3>
        </div>
        <div class="metric-value">67%</div>
      </div>
    </div>

    <!-- Charts Grid -->
    <div class="charts-grid">
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">User Activity</h3>
        </div>
        <div class="chart-container">
          <canvas id="userActivityChart"></canvas>
        </div>
      </div>
      
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">Geographic User Distribution</h3>
        </div>
        <div class="chart-container">
          <div id="worldMap"></div>
        </div>
      </div>
      
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">Revenue</h3>
        </div>
        <div class="chart-container">
          <canvas id="revenueChart"></canvas>
        </div>
      </div>
      
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">System Performance</h3>
        </div>
        <div class="chart-container">
          <div class="performance-gauges">
            <div class="gauge-item">
              <div class="gauge-circle" data-percentage="26">
                <span class="gauge-value">26%</span>
                <span class="gauge-label">CPU Usage</span>
              </div>
            </div>
            <div class="gauge-item">
              <div class="gauge-circle" data-percentage="40">
                <span class="gauge-value">40%</span>
                <span class="gauge-label">Memory Usage</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</div>
```

### **CSS Specifications**
```css
.admin-layout {
  display: grid;
  grid-template-areas: 
    "sidebar header"
    "sidebar main";
  grid-template-columns: 240px 1fr;
  grid-template-rows: 60px 1fr;
  height: 100vh;
  background: var(--bg-primary);
  font-family: var(--font-primary);
}

/* Header Styles */
.admin-header {
  grid-area: header;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-primary);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-6);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.header-logo {
  width: 32px;
  height: 32px;
}

.header-title {
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  letter-spacing: 0.05em;
}

.header-center {
  flex: 1;
  max-width: 400px;
  margin: 0 var(--space-8);
}

.search-wrapper {
  position: relative;
}

.search-input {
  width: 100%;
  padding: var(--space-2) var(--space-4) var(--space-2) var(--space-10);
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: var(--text-sm);
}

.search-input:focus {
  outline: none;
  border-color: var(--accent-blue);
}

.search-icon {
  position: absolute;
  left: var(--space-3);
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  font-size: var(--text-sm);
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.notification-button {
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

.admin-profile {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.admin-name {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-primary);
}

.admin-avatar {
  width: 32px;
  height: 32px;
  background: var(--accent-blue);
  border-radius: var(--radius-full);
}

/* Sidebar Styles */
.admin-sidebar {
  grid-area: sidebar;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-primary);
  padding: var(--space-6) 0;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-6);
  color: var(--text-secondary);
  text-decoration: none;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  transition: all 0.2s ease;
}

.nav-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.nav-item.active {
  background: var(--accent-blue);
  color: var(--text-primary);
  border-right: 3px solid var(--accent-blue);
}

.nav-icon {
  font-size: var(--text-lg);
  width: 20px;
  text-align: center;
}

/* Main Content Styles */
.admin-main {
  grid-area: main;
  padding: var(--space-6);
  overflow-y: auto;
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-6);
  margin-bottom: var(--space-8);
}

.metric-card {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  border-left: 4px solid transparent;
  transition: transform 0.2s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
}

.metric-card--blue {
  border-left-color: var(--accent-blue);
}

.metric-card--orange {
  border-left-color: var(--accent-orange);
}

.metric-card--green {
  border-left-color: var(--accent-green);
}

.metric-title {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
  margin: 0 0 var(--space-2) 0;
}

.metric-value {
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  font-family: var(--font-mono);
}

/* Charts Grid */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-6);
}

.chart-card {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  overflow: hidden;
}

.chart-header {
  padding: var(--space-4) var(--space-6);
  border-bottom: 1px solid var(--border-primary);
}

.chart-title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0;
}

.chart-container {
  padding: var(--space-6);
  height: 300px;
}

/* Performance Gauges */
.performance-gauges {
  display: flex;
  justify-content: space-around;
  align-items: center;
  height: 100%;
}

.gauge-item {
  text-align: center;
}

.gauge-circle {
  width: 120px;
  height: 120px;
  border-radius: var(--radius-full);
  background: conic-gradient(
    var(--accent-green) 0deg,
    var(--accent-green) calc(var(--percentage, 0) * 3.6deg),
    var(--bg-tertiary) calc(var(--percentage, 0) * 3.6deg),
    var(--bg-tertiary) 360deg
  );
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  margin-bottom: var(--space-3);
}

.gauge-circle::before {
  content: '';
  position: absolute;
  width: 80px;
  height: 80px;
  background: var(--bg-secondary);
  border-radius: var(--radius-full);
}

.gauge-value {
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  z-index: 1;
}

.gauge-label {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  font-weight: var(--font-medium);
}

/* Responsive Design */
@media (max-width: 1024px) {
  .admin-layout {
    grid-template-columns: 200px 1fr;
  }
  
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .admin-layout {
    grid-template-areas: 
      "header"
      "main";
    grid-template-columns: 1fr;
    grid-template-rows: 60px 1fr;
  }
  
  .admin-sidebar {
    display: none;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
}
```

### **JavaScript for Charts**
```javascript
// User Activity Chart
const userActivityCtx = document.getElementById('userActivityChart').getContext('2d');
new Chart(userActivityCtx, {
  type: 'line',
  data: {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [{
      label: 'User Activity',
      data: [800, 950, 1100, 1300, 1450, 1200, 1500],
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
          color: '#B0B0B0'
        }
      },
      y: {
        grid: {
          color: '#404040'
        },
        ticks: {
          color: '#B0B0B0'
        }
      }
    }
  }
});

// Revenue Chart
const revenueCtx = document.getElementById('revenueChart').getContext('2d');
new Chart(revenueCtx, {
  type: 'bar',
  data: {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
    datasets: [{
      label: 'Revenue',
      data: [5000, 7000, 8500, 9200, 11000, 8800, 10500],
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
          color: '#B0B0B0'
        }
      },
      y: {
        grid: {
          color: '#404040'
        },
        ticks: {
          color: '#B0B0B0',
          callback: function(value) {
            return '$' + value.toLocaleString();
          }
        }
      }
    }
  }
});

// Update gauge percentages
document.querySelectorAll('.gauge-circle').forEach(gauge => {
  const percentage = gauge.dataset.percentage;
  gauge.style.setProperty('--percentage', percentage);
});

// Real-time updates
setInterval(() => {
  // Update metrics with new data
  updateMetrics();
  updateCharts();
}, 30000);

function updateMetrics() {
  // Simulate real-time data updates
  const activeUsers = document.querySelector('.metric-card--blue .metric-value');
  const currentValue = parseInt(activeUsers.textContent.replace(',', ''));
  const newValue = currentValue + Math.floor(Math.random() * 20) - 10;
  activeUsers.textContent = newValue.toLocaleString();
}
```

---

## 👥 **3. User Management - Technical Specifications**

### **Layout Structure**
```html
<div class="user-management">
  <div class="page-header">
    <h1 class="page-title">User Management</h1>
    <div class="page-actions">
      <button class="btn btn-secondary">
        <span class="btn-icon">⏰</span>
        Export
      </button>
      <button class="btn btn-primary">
        <span class="btn-icon">➕</span>
        Add User
      </button>
    </div>
  </div>

  <div class="user-content">
    <!-- Filters Section -->
    <div class="filters-section">
      <div class="search-filter">
        <input type="text" class="filter-input" placeholder="Search users..." />
        <span class="search-icon">🔍</span>
      </div>
      
      <select class="filter-select">
        <option>Role: Admin, Manager, User</option>
        <option>Admin</option>
        <option>Manager</option>
        <option>User</option>
      </select>
      
      <div class="date-filter">
        <input type="text" class="filter-input" placeholder="434/3033 - 04/24/2024" />
        <span class="calendar-icon">📅</span>
      </div>
      
      <select class="filter-select">
        <option>Status: Active, Suspended, Pending</option>
        <option>Active</option>
        <option>Suspended</option>
        <option>Pending</option>
      </select>
      
      <button class="filter-button">
        <span class="filter-icon">🔧</span>
        Filter
      </button>
    </div>

    <!-- Bulk Actions -->
    <div class="bulk-actions">
      <div class="bulk-controls">
        <button class="btn btn-danger btn-sm">Delete</button>
        <button class="btn btn-warning btn-sm">Suspend</button>
        <label class="bulk-select">
          <input type="checkbox" class="bulk-checkbox" />
          Bulk Action
        </label>
        <button class="btn btn-secondary btn-sm">Export</button>
      </div>
      
      <div class="table-actions">
        <button class="action-btn">⭐</button>
        <button class="action-btn">📋</button>
        <button class="action-btn">↕️</button>
        <button class="action-btn">📊</button>
        <button class="action-btn">📤</button>
      </div>
    </div>

    <div class="content-layout">
      <!-- User Table -->
      <div class="user-table-section">
        <table class="user-table">
          <thead>
            <tr>
              <th><input type="checkbox" class="select-all" /></th>
              <th>Avatar</th>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Status</th>
              <th>Last Login</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr class="user-row">
              <td><input type="checkbox" class="row-select" /></td>
              <td>
                <div class="user-avatar">
                  <img src="avatar1.jpg" alt="Alice Martin" />
                </div>
              </td>
              <td class="user-name">Alice Martin</td>
              <td class="user-email">alice@martin.com</td>
              <td><span class="role-badge role-admin">Admin</span></td>
              <td><span class="status-badge status-active">Active</span></td>
              <td class="last-login">22 min. ago</td>
              <td>
                <button class="action-btn">✏️</button>
                <button class="action-btn">👁️</button>
              </td>
            </tr>
            <!-- More user rows... -->
          </tbody>
        </table>
      </div>

      <!-- User Details Panel -->
      <div class="user-details-panel">
        <div class="panel-header">
          <h3 class="panel-title">User Details</h3>
        </div>
        
        <div class="user-profile">
          <div class="profile-avatar">
            <img src="avatar-selected.jpg" alt="Carol White" />
          </div>
          <div class="profile-info">
            <h4 class="profile-name">Carol White</h4>
            <p class="profile-email">carol.white@example.com</p>
          </div>
        </div>

        <div class="role-section">
          <h4 class="section-title">Role</h4>
          <div class="role-options">
            <label class="radio-option">
              <input type="radio" name="role" value="admin" />
              <span class="radio-label">Admin</span>
            </label>
            <label class="radio-option">
              <input type="radio" name="role" value="manager" />
              <span class="radio-label">Manager</span>
            </label>
            <label class="radio-option">
              <input type="radio" name="role" value="user" checked />
              <span class="radio-label">User</span>
            </label>
          </div>
        </div>

        <div class="permissions-section">
          <h4 class="section-title">Permissions</h4>
          <table class="permissions-table">
            <thead>
              <tr>
                <th></th>
                <th>Read</th>
                <th>Write</th>
                <th>Delete</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Dashboard</td>
                <td><span class="permission-check">✓</span></td>
                <td><span class="permission-check">✓</span></td>
                <td><span class="permission-cross">—</span></td>
              </tr>
              <tr>
                <td>Projects</td>
                <td><span class="permission-check">✓</span></td>
                <td><span class="permission-check">✓</span></td>
                <td><span class="permission-cross">—</span></td>
              </tr>
              <tr>
                <td>Tasks</td>
                <td><span class="permission-check">✓</span></td>
                <td><span class="permission-cross">—</span></td>
                <td><span class="permission-cross">—</span></td>
              </tr>
              <tr>
                <td>Reports</td>
                <td><span class="permission-check">✓</span></td>
                <td><span class="permission-cross">—</span></td>
                <td><span class="permission-cross">—</span></td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="account-settings">
          <h4 class="section-title">Account Settings</h4>
          <div class="setting-item">
            <span class="setting-label">Enabled</span>
            <label class="toggle-switch">
              <input type="checkbox" checked />
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>

        <button class="btn btn-primary btn-full">Save</button>
      </div>
    </div>
  </div>
</div>
```

### **CSS Specifications**
```css
.user-management {
  padding: var(--space-6);
  background: var(--bg-primary);
  min-height: 100vh;
}

.page-header {
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

.page-actions {
  display: flex;
  gap: var(--space-3);
}

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

.btn-warning {
  background: var(--accent-orange);
  color: var(--text-primary);
}

.btn-sm {
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-xs);
}

.btn-full {
  width: 100%;
}

/* Filters Section */
.filters-section {
  display: flex;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
  flex-wrap: wrap;
}

.search-filter {
  position: relative;
  flex: 1;
  min-width: 200px;
}

.filter-input {
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

.filter-select {
  padding: var(--space-2) var(--space-4);
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: var(--text-sm);
  min-width: 180px;
}

.date-filter {
  position: relative;
}

.calendar-icon {
  position: absolute;
  right: var(--space-3);
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
}

.filter-button {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  background: var(--accent-blue);
  color: var(--text-primary);
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  cursor: pointer;
}

/* Bulk Actions */
.bulk-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
  padding: var(--space-3);
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-primary);
}

.bulk-controls {
  display: flex;
  gap: var(--space-2);
  align-items: center;
}

.bulk-select {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  cursor: pointer;
}

.table-actions {
  display: flex;
  gap: var(--space-1);
}

.action-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: var(--space-1);
  border-radius: var(--radius-sm);
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

/* Content Layout */
.content-layout {
  display: grid;
  grid-template-columns: 1fr 350px;
  gap: var(--space-6);
}

/* User Table */
.user-table-section {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  overflow: hidden;
}

.user-table {
  width: 100%;
  border-collapse: collapse;
}

.user-table th {
  background: var(--bg-tertiary);
  padding: var(--space-3) var(--space-4);
  text-align: left;
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--border-primary);
}

.user-table td {
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--border-primary);
  font-size: var(--text-sm);
}

.user-row:hover {
  background: var(--bg-hover);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-full);
  overflow: hidden;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-name {
  font-weight: var(--font-medium);
  color: var(--text-primary);
}

.user-email {
  color: var(--text-secondary);
}

.role-badge {
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  text-transform: uppercase;
}

.role-admin {
  background: rgba(220, 53, 69, 0.2);
  color: var(--accent-red);
}

.role-manager {
  background: rgba(253, 126, 20, 0.2);
  color: var(--accent-orange);
}

.role-user {
  background: rgba(40, 167, 69, 0.2);
  color: var(--accent-green);
}

.status-badge {
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  text-transform: uppercase;
}

.status-active {
  background: rgba(40, 167, 69, 0.2);
  color: var(--accent-green);
}

.status-suspended {
  background: rgba(220, 53, 69, 0.2);
  color: var(--accent-red);
}

.status-pending {
  background: rgba(253, 126, 20, 0.2);
  color: var(--accent-orange);
}

.last-login {
  color: var(--text-secondary);
}

/* User Details Panel */
.user-details-panel {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  padding: var(--space-6);
  height: fit-content;
}

.panel-header {
  margin-bottom: var(--space-6);
}

.panel-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
  padding-bottom: var(--space-6);
  border-bottom: 1px solid var(--border-primary);
}

.profile-avatar {
  width: 60px;
  height: 60px;
  border-radius: var(--radius-full);
  overflow: hidden;
}

.profile-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-name {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-1) 0;
}

.profile-email {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
}

.section-title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-4) 0;
}

.role-section {
  margin-bottom: var(--space-6);
}

.role-options {
  display: flex;
  gap: var(--space-4);
}

.radio-option {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  cursor: pointer;
}

.radio-option input[type="radio"] {
  accent-color: var(--accent-blue);
}

.radio-label {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

/* Permissions Table */
.permissions-section {
  margin-bottom: var(--space-6);
}

.permissions-table {
  width: 100%;
  border-collapse: collapse;
}

.permissions-table th {
  padding: var(--space-2) var(--space-3);
  text-align: center;
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--text-secondary);
  text-transform: uppercase;
  border-bottom: 1px solid var(--border-primary);
}

.permissions-table th:first-child {
  text-align: left;
}

.permissions-table td {
  padding: var(--space-2) var(--space-3);
  text-align: center;
  font-size: var(--text-sm);
  border-bottom: 1px solid var(--border-primary);
}

.permissions-table td:first-child {
  text-align: left;
  color: var(--text-primary);
  font-weight: var(--font-medium);
}

.permission-check {
  color: var(--accent-green);
  font-weight: var(--font-bold);
}

.permission-cross {
  color: var(--text-muted);
}

/* Account Settings */
.account-settings {
  margin-bottom: var(--space-6);
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) 0;
}

.setting-label {
  font-size: var(--text-sm);
  color: var(--text-primary);
  font-weight: var(--font-medium);
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
  background-color: var(--bg-tertiary);
  transition: 0.3s;
  border-radius: 24px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: var(--text-primary);
  transition: 0.3s;
  border-radius: 50%;
}

input:checked + .toggle-slider {
  background-color: var(--accent-blue);
}

input:checked + .toggle-slider:before {
  transform: translateX(20px);
}

/* Responsive Design */
@media (max-width: 1024px) {
  .content-layout {
    grid-template-columns: 1fr;
  }
  
  .user-details-panel {
    order: -1;
  }
}

@media (max-width: 768px) {
  .filters-section {
    flex-direction: column;
  }
  
  .bulk-actions {
    flex-direction: column;
    gap: var(--space-3);
  }
  
  .user-table {
    font-size: var(--text-xs);
  }
  
  .user-table th,
  .user-table td {
    padding: var(--space-2);
  }
}
```

This detailed specification continues for all remaining pages. Would you like me to continue with the complete technical specifications for the remaining pages (Content Management, Analytics, Settings, Security, Data Management, and Mobile Responsive)?
