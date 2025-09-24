# Crane Intelligence Admin Panel - Webapp Management JavaScript Specifications

## 🔧 **JavaScript Functionality for Webapp Management**

### **Webapp User Management JavaScript**
```javascript
// Webapp User Management Functionality
class WebappUserManager {
  constructor() {
    this.initializeCharts();
    this.initializeRealTimeUpdates();
    this.initializeSessionRecordings();
    this.initializeFeedbackManagement();
  }

  // Initialize Charts
  initializeCharts() {
    // Session Trend Chart
    const sessionTrendCtx = document.getElementById('sessionTrendChart');
    if (sessionTrendCtx) {
      this.sessionTrendChart = new Chart(sessionTrendCtx.getContext('2d'), {
        type: 'line',
        data: {
          labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
          datasets: [{
            label: 'Session Duration',
            data: [320, 380, 420, 450, 380, 340],
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
            legend: { display: false }
          },
          scales: {
            x: {
              grid: { color: '#404040' },
              ticks: { color: '#B0B0B0', font: { size: 10 } }
            },
            y: {
              grid: { color: '#404040' },
              ticks: { 
                color: '#B0B0B0', 
                font: { size: 10 },
                callback: function(value) {
                  return Math.floor(value / 60) + 'm ' + (value % 60) + 's';
                }
              }
            }
          }
        }
      });
    }

    // Page Views Chart
    const pageViewsCtx = document.getElementById('pageViewsChart');
    if (pageViewsCtx) {
      this.pageViewsChart = new Chart(pageViewsCtx.getContext('2d'), {
        type: 'bar',
        data: {
          labels: ['Dashboard', 'Valuation', 'Reports', 'Settings', 'Profile'],
          datasets: [{
            label: 'Page Views',
            data: [450, 320, 280, 180, 120],
            backgroundColor: '#28A745',
            borderRadius: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            x: {
              grid: { display: false },
              ticks: { color: '#B0B0B0', font: { size: 10 } }
            },
            y: {
              grid: { color: '#404040' },
              ticks: { color: '#B0B0B0', font: { size: 10 } }
            }
          }
        }
      });
    }

    // Feature Adoption Chart
    const featureAdoptionCtx = document.getElementById('featureAdoptionChart');
    if (featureAdoptionCtx) {
      this.featureAdoptionChart = new Chart(featureAdoptionCtx.getContext('2d'), {
        type: 'line',
        data: {
          labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
          datasets: [{
            label: 'Adoption Rate',
            data: [15, 25, 45, 65],
            borderColor: '#FFC107',
            backgroundColor: 'rgba(255, 193, 7, 0.1)',
            borderWidth: 2,
            fill: true,
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            x: {
              grid: { color: '#404040' },
              ticks: { color: '#B0B0B0', font: { size: 10 } }
            },
            y: {
              grid: { color: '#404040' },
              ticks: { 
                color: '#B0B0B0', 
                font: { size: 10 },
                callback: function(value) {
                  return value + '%';
                }
              }
            }
          }
        }
      });
    }

    // Churn Prediction Chart
    const churnPredictionCtx = document.getElementById('churnPredictionChart');
    if (churnPredictionCtx) {
      this.churnPredictionChart = new Chart(churnPredictionCtx.getContext('2d'), {
        type: 'line',
        data: {
          labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
          datasets: [{
            label: 'Churn Risk',
            data: [12, 8, 15, 6, 9],
            borderColor: '#DC3545',
            backgroundColor: 'rgba(220, 53, 69, 0.1)',
            borderWidth: 2,
            fill: true,
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            x: {
              grid: { color: '#404040' },
              ticks: { color: '#B0B0B0', font: { size: 10 } }
            },
            y: {
              grid: { color: '#404040' },
              ticks: { 
                color: '#B0B0B0', 
                font: { size: 10 },
                callback: function(value) {
                  return value + '%';
                }
              }
            }
          }
        }
      });
    }
  }

  // Real-time Updates
  initializeRealTimeUpdates() {
    setInterval(() => {
      this.updateActiveUsers();
      this.updateSessionMetrics();
      this.updateUserJourney();
    }, 30000); // Update every 30 seconds
  }

  updateActiveUsers() {
    // Simulate real-time user updates
    const userRows = document.querySelectorAll('.session-row');
    userRows.forEach(row => {
      const durationCell = row.querySelector('.duration-cell');
      if (durationCell) {
        const currentDuration = durationCell.textContent;
        const [minutes, seconds] = currentDuration.split(':').map(Number);
        const totalSeconds = minutes * 60 + seconds + 1;
        const newMinutes = Math.floor(totalSeconds / 60);
        const newSeconds = totalSeconds % 60;
        durationCell.textContent = `${newMinutes.toString().padStart(2, '0')}:${newSeconds.toString().padStart(2, '0')}`;
      }
    });
  }

  updateSessionMetrics() {
    // Update engagement metrics
    const metricValues = document.querySelectorAll('.metric-value');
    metricValues.forEach(metric => {
      if (metric.textContent.includes('m')) {
        // Update session duration
        const currentValue = parseInt(metric.textContent);
        metric.textContent = `${currentValue}m ${Math.floor(Math.random() * 60)}s`;
      } else if (!metric.textContent.includes('%')) {
        // Update page views
        const currentValue = parseInt(metric.textContent.replace(',', ''));
        metric.textContent = (currentValue + Math.floor(Math.random() * 5)).toLocaleString();
      }
    });
  }

  updateUserJourney() {
    // Update journey heatmap dots
    const heatmapDots = document.querySelectorAll('.heatmap-dot');
    heatmapDots.forEach(dot => {
      const classes = ['hot', 'warm', 'cool'];
      const currentClass = classes.find(cls => dot.classList.contains(cls));
      if (currentClass) {
        dot.classList.remove(currentClass);
        const newClass = classes[Math.floor(Math.random() * classes.length)];
        dot.classList.add(newClass);
      }
    });
  }

  // Session Recordings Management
  initializeSessionRecordings() {
    const recordingButtons = document.querySelectorAll('.recording-btn');
    recordingButtons.forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        this.handleRecordingAction(btn);
      });
    });
  }

  handleRecordingAction(button) {
    const isRecording = button.classList.contains('recording-active');
    
    if (isRecording) {
      // Stop recording
      button.classList.remove('recording-active');
      button.querySelector('.recording-icon').textContent = '📹';
      this.showNotification('Recording stopped', 'success');
    } else {
      // Start recording
      button.classList.add('recording-active');
      button.querySelector('.recording-icon').textContent = '🔴';
      this.showNotification('Recording started', 'info');
    }
  }

  // Feedback Management
  initializeFeedbackManagement() {
    const feedbackActions = document.querySelectorAll('.feedback-actions .btn');
    feedbackActions.forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        this.handleFeedbackAction(btn);
      });
    });
  }

  handleFeedbackAction(button) {
    const action = button.textContent.trim();
    const feedbackItem = button.closest('.feedback-item');
    
    if (action === 'Reply') {
      this.openFeedbackReply(feedbackItem);
    } else if (action === 'Resolve') {
      this.resolveFeedback(feedbackItem);
    }
  }

  openFeedbackReply(feedbackItem) {
    // Create reply modal or inline form
    const replyForm = document.createElement('div');
    replyForm.className = 'feedback-reply-form';
    replyForm.innerHTML = `
      <textarea class="reply-textarea" placeholder="Type your reply..."></textarea>
      <div class="reply-actions">
        <button class="btn btn-secondary btn-sm cancel-reply">Cancel</button>
        <button class="btn btn-primary btn-sm send-reply">Send Reply</button>
      </div>
    `;
    
    feedbackItem.appendChild(replyForm);
    
    // Handle reply actions
    replyForm.querySelector('.cancel-reply').addEventListener('click', () => {
      replyForm.remove();
    });
    
    replyForm.querySelector('.send-reply').addEventListener('click', () => {
      const replyText = replyForm.querySelector('.reply-textarea').value;
      if (replyText.trim()) {
        this.sendFeedbackReply(feedbackItem, replyText);
        replyForm.remove();
      }
    });
  }

  sendFeedbackReply(feedbackItem, replyText) {
    // Simulate sending reply
    this.showNotification('Reply sent successfully', 'success');
    
    // Add reply indicator
    const feedbackHeader = feedbackItem.querySelector('.feedback-header');
    const replyIndicator = document.createElement('span');
    replyIndicator.className = 'reply-indicator';
    replyIndicator.textContent = 'Replied';
    feedbackHeader.appendChild(replyIndicator);
  }

  resolveFeedback(feedbackItem) {
    feedbackItem.style.opacity = '0.6';
    feedbackItem.style.pointerEvents = 'none';
    
    const resolvedIndicator = document.createElement('span');
    resolvedIndicator.className = 'resolved-indicator';
    resolvedIndicator.textContent = 'Resolved';
    feedbackItem.querySelector('.feedback-header').appendChild(resolvedIndicator);
    
    this.showNotification('Feedback resolved', 'success');
  }

  // Utility Functions
  showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.classList.add('notification-show');
    }, 100);
    
    setTimeout(() => {
      notification.classList.remove('notification-show');
      setTimeout(() => {
        notification.remove();
      }, 300);
    }, 3000);
  }
}

// Activities Tracking JavaScript
class ActivitiesTracker {
  constructor() {
    this.initializeCharts();
    this.initializeFilters();
    this.initializeRealTimeUpdates();
    this.initializeHeatmap();
  }

  // Initialize Charts
  initializeCharts() {
    // Peak Usage Chart
    const peakUsageCtx = document.getElementById('peakUsageChart');
    if (peakUsageCtx) {
      this.peakUsageChart = new Chart(peakUsageCtx.getContext('2d'), {
        type: 'line',
        data: {
          labels: ['0', '6', '12', '18', '24'],
          datasets: [{
            label: 'Active Users',
            data: [45, 120, 380, 520, 180],
            borderColor: '#FFC107',
            backgroundColor: 'rgba(255, 193, 7, 0.1)',
            borderWidth: 2,
            fill: true,
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            x: {
              grid: { color: '#404040' },
              ticks: { color: '#B0B0B0', font: { size: 10 } }
            },
            y: {
              grid: { color: '#404040' },
              ticks: { color: '#B0B0B0', font: { size: 10 } }
            }
          }
        }
      });
    }

    // Feature Performance Chart
    const featurePerformanceCtx = document.getElementById('featurePerformanceChart');
    if (featurePerformanceCtx) {
      this.featurePerformanceChart = new Chart(featurePerformanceCtx.getContext('2d'), {
        type: 'bar',
        data: {
          labels: ['00', '11', '12', '06', '36', '05', '38'],
          datasets: [{
            label: 'Performance Score',
            data: [85, 92, 78, 88, 95, 82, 90],
            backgroundColor: [
              '#28A745', '#28A745', '#FFC107', 
              '#28A745', '#28A745', '#FFC107', '#28A745'
            ],
            borderRadius: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            x: {
              grid: { display: false },
              ticks: { color: '#B0B0B0', font: { size: 10 } }
            },
            y: {
              grid: { color: '#404040' },
              ticks: { 
                color: '#B0B0B0', 
                font: { size: 10 },
                callback: function(value) {
                  return value + '%';
                }
              }
            }
          }
        }
      });
    }
  }

  // Initialize Filters
  initializeFilters() {
    const filterSelects = document.querySelectorAll('.filter-select');
    filterSelects.forEach(select => {
      select.addEventListener('change', (e) => {
        this.applyFilter(e.target.name, e.target.value);
      });
    });
  }

  applyFilter(filterType, filterValue) {
    const activityRows = document.querySelectorAll('.activity-row');
    
    activityRows.forEach(row => {
      let shouldShow = true;
      
      if (filterType === 'action-type' && filterValue !== 'Action Type') {
        const actionText = row.querySelector('.action-text').textContent;
        shouldShow = actionText.toLowerCase().includes(filterValue.toLowerCase());
      }
      
      if (filterType === 'filter' && filterValue !== 'Filter') {
        // Apply general filter logic
        const userText = row.querySelector('.user-name').textContent;
        const actionText = row.querySelector('.action-text').textContent;
        const searchText = (userText + ' ' + actionText).toLowerCase();
        shouldShow = searchText.includes(filterValue.toLowerCase());
      }
      
      row.style.display = shouldShow ? '' : 'none';
    });
    
    this.showNotification(`Filter applied: ${filterValue}`, 'info');
  }

  // Real-time Updates
  initializeRealTimeUpdates() {
    setInterval(() => {
      this.addNewActivity();
      this.updateActivityMetrics();
    }, 15000); // Update every 15 seconds
  }

  addNewActivity() {
    const activityTable = document.querySelector('.activity-table tbody');
    if (activityTable) {
      const newActivity = this.generateRandomActivity();
      const newRow = document.createElement('tr');
      newRow.className = 'activity-row';
      newRow.innerHTML = newActivity;
      
      // Add to top of table
      activityTable.insertBefore(newRow, activityTable.firstChild);
      
      // Remove oldest row if more than 20 rows
      const rows = activityTable.querySelectorAll('.activity-row');
      if (rows.length > 20) {
        rows[rows.length - 1].remove();
      }
      
      // Highlight new row
      newRow.style.backgroundColor = 'rgba(0, 123, 255, 0.1)';
      setTimeout(() => {
        newRow.style.backgroundColor = '';
      }, 2000);
    }
  }

  generateRandomActivity() {
    const users = ['Elizabeth', 'James', 'Daniel', 'Olivia', 'Michael'];
    const actions = [
      { text: 'Logged In', indicator: 'action-success' },
      { text: 'API Call', indicator: 'action-info' },
      { text: 'Error', indicator: 'action-error' },
      { text: 'Logged Out', indicator: 'action-warning' },
      { text: 'Database Update', indicator: 'action-info' }
    ];
    
    const user = users[Math.floor(Math.random() * users.length)];
    const action = actions[Math.floor(Math.random() * actions.length)];
    const avatar = user.charAt(0).toUpperCase();
    
    return `
      <td class="time-cell">now</td>
      <td class="user-cell">
        <div class="user-avatar user-avatar-${avatar.toLowerCase()}">${avatar}</div>
        <span class="user-name">${user}</span>
      </td>
      <td class="action-cell">
        <span class="action-indicator ${action.indicator}"></span>
        <span class="action-text">${action.text}</span>
      </td>
      <td class="details-cell">${this.generateActionDetails(action.text)}</td>
    `;
  }

  generateActionDetails(actionType) {
    const details = {
      'Logged In': 'Session started',
      'API Call': `Path: /api/v1/${Math.random().toString(36).substr(2, 5)}`,
      'Error': `Error code ${Math.floor(Math.random() * 9000) + 1000}`,
      'Logged Out': 'Session ended',
      'Database Update': 'Data synchronized'
    };
    
    return details[actionType] || 'Activity completed';
  }

  updateActivityMetrics() {
    // Update feature usage bars
    const featureBars = document.querySelectorAll('.feature-progress');
    featureBars.forEach(bar => {
      const currentWidth = parseInt(bar.style.width);
      const variation = Math.floor(Math.random() * 10) - 5; // -5 to +5
      const newWidth = Math.max(0, Math.min(100, currentWidth + variation));
      bar.style.width = newWidth + '%';
    });
  }

  // Initialize Heatmap
  initializeHeatmap() {
    this.generateHeatmapData();
    setInterval(() => {
      this.updateHeatmap();
    }, 60000); // Update every minute
  }

  generateHeatmapData() {
    const heatmapCells = document.querySelectorAll('.heatmap-cell');
    heatmapCells.forEach(cell => {
      const intensity = Math.random();
      if (intensity < 0.25) {
        cell.className = 'heatmap-cell heatmap-low';
      } else if (intensity < 0.5) {
        cell.className = 'heatmap-cell heatmap-medium';
      } else if (intensity < 0.75) {
        cell.className = 'heatmap-cell heatmap-high';
      } else {
        cell.className = 'heatmap-cell heatmap-very-high';
      }
    });
  }

  updateHeatmap() {
    this.generateHeatmapData();
  }

  // Export Functions
  exportActivityData() {
    const activityData = this.collectActivityData();
    const csvContent = this.convertToCSV(activityData);
    this.downloadCSV(csvContent, 'activity-log.csv');
  }

  collectActivityData() {
    const rows = document.querySelectorAll('.activity-row');
    const data = [];
    
    rows.forEach(row => {
      const time = row.querySelector('.time-cell').textContent;
      const user = row.querySelector('.user-name').textContent;
      const action = row.querySelector('.action-text').textContent;
      const details = row.querySelector('.details-cell').textContent;
      
      data.push({ time, user, action, details });
    });
    
    return data;
  }

  convertToCSV(data) {
    const headers = ['Time', 'User', 'Action', 'Details'];
    const csvRows = [headers.join(',')];
    
    data.forEach(row => {
      const values = [row.time, row.user, row.action, row.details];
      csvRows.push(values.map(value => `"${value}"`).join(','));
    });
    
    return csvRows.join('\n');
  }

  downloadCSV(content, filename) {
    const blob = new Blob([content], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
    
    this.showNotification('Activity data exported successfully', 'success');
  }

  // Utility Functions
  showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.classList.add('notification-show');
    }, 100);
    
    setTimeout(() => {
      notification.classList.remove('notification-show');
      setTimeout(() => {
        notification.remove();
      }, 300);
    }, 3000);
  }
}

// Core Features Management JavaScript
class CoreFeaturesManager {
  constructor() {
    this.initializeFeatureFlags();
    this.initializeValuationConfig();
    this.initializePerformanceCharts();
    this.initializeVersioning();
  }

  // Feature Flags Management
  initializeFeatureFlags() {
    const toggleSwitches = document.querySelectorAll('.toggle-switch input');
    toggleSwitches.forEach(toggle => {
      toggle.addEventListener('change', (e) => {
        this.handleFeatureToggle(e.target);
      });
    });

    const rolloutSliders = document.querySelectorAll('.rollout-slider');
    rolloutSliders.forEach(slider => {
      slider.addEventListener('input', (e) => {
        this.handleRolloutChange(e.target);
      });
    });
  }

  handleFeatureToggle(toggle) {
    const row = toggle.closest('.flag-row');
    const featureName = row.querySelector('.feature-name').textContent;
    const isEnabled = toggle.checked;
    
    if (isEnabled) {
      this.enableFeature(featureName, row);
    } else {
      this.disableFeature(featureName, row);
    }
  }

  enableFeature(featureName, row) {
    // Update UI
    row.classList.add('feature-enabled');
    
    // Update rollout slider
    const rolloutSlider = row.querySelector('.rollout-slider');
    rolloutSlider.disabled = false;
    
    // Show notification
    this.showNotification(`${featureName} enabled`, 'success');
    
    // Log activity
    this.logFeatureActivity(featureName, 'enabled');
  }

  disableFeature(featureName, row) {
    // Update UI
    row.classList.remove('feature-enabled');
    
    // Reset rollout slider
    const rolloutSlider = row.querySelector('.rollout-slider');
    const rolloutValue = row.querySelector('.rollout-value');
    rolloutSlider.value = 0;
    rolloutSlider.disabled = true;
    rolloutValue.textContent = '0%';
    
    // Show notification
    this.showNotification(`${featureName} disabled`, 'warning');
    
    // Log activity
    this.logFeatureActivity(featureName, 'disabled');
  }

  handleRolloutChange(slider) {
    const row = slider.closest('.flag-row');
    const featureName = row.querySelector('.feature-name').textContent;
    const rolloutValue = row.querySelector('.rollout-value');
    const percentage = slider.value;
    
    rolloutValue.textContent = percentage + '%';
    
    // Update adoption rate simulation
    this.updateAdoptionRate(row, percentage);
    
    // Log activity
    this.logFeatureActivity(featureName, `rollout changed to ${percentage}%`);
  }

  updateAdoptionRate(row, rolloutPercentage) {
    const adoptionCell = row.querySelector('.adoption-rate');
    const trendCell = row.querySelector('.adoption-trend');
    
    // Simulate adoption rate based on rollout percentage
    const baseRate = parseFloat(adoptionCell.textContent);
    const newRate = (baseRate * (rolloutPercentage / 100)).toFixed(1);
    
    adoptionCell.textContent = newRate + '%';
    
    // Update trend
    const trend = Math.random() > 0.5 ? '+' : '-';
    const trendValue = (Math.random() * 2).toFixed(1);
    trendCell.textContent = trend + trendValue + '%';
    trendCell.className = `adoption-trend trend-${trend === '+' ? 'positive' : 'negative'}`;
  }

  // Valuation Configuration
  initializeValuationConfig() {
    const configForms = document.querySelectorAll('.valuation-form, .data-sources-form');
    configForms.forEach(form => {
      const inputs = form.querySelectorAll('select, input');
      inputs.forEach(input => {
        input.addEventListener('change', (e) => {
          this.handleConfigChange(e.target);
        });
      });
    });

    // Tab switching
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
      btn.addEventListener('click', (e) => {
        this.switchTab(e.target);
      });
    });
  }

  handleConfigChange(input) {
    const configType = input.closest('.valuation-card, .pricing-card').querySelector('h3, h4').textContent;
    const value = input.value;
    
    // Save configuration
    this.saveConfiguration(configType, input.name || input.className, value);
    
    // Show notification
    this.showNotification(`${configType} updated`, 'success');
    
    // Update dependent calculations
    this.updateCalculations();
  }

  saveConfiguration(section, field, value) {
    // Simulate saving to backend
    const config = JSON.parse(localStorage.getItem('craneValuationConfig') || '{}');
    if (!config[section]) config[section] = {};
    config[section][field] = value;
    localStorage.setItem('craneValuationConfig', JSON.stringify(config));
  }

  updateCalculations() {
    // Simulate recalculating valuation models
    const performanceCards = document.querySelectorAll('.performance-card');
    performanceCards.forEach(card => {
      const statValues = card.querySelectorAll('.stat-value');
      statValues.forEach(stat => {
        if (stat.textContent.includes('ms')) {
          const currentValue = parseInt(stat.textContent);
          const variation = Math.floor(Math.random() * 20) - 10;
          stat.textContent = Math.max(100, currentValue + variation) + 'ms';
        }
      });
    });
  }

  switchTab(button) {
    // Remove active class from all tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.classList.remove('tab-active');
    });
    
    document.querySelectorAll('.tab-content').forEach(content => {
      content.classList.remove('tab-content-active');
    });
    
    // Add active class to clicked tab
    button.classList.add('tab-active');
    
    // Show corresponding content
    const tabIndex = Array.from(button.parentNode.children).indexOf(button);
    const tabContents = document.querySelectorAll('.tab-content');
    if (tabContents[tabIndex]) {
      tabContents[tabIndex].classList.add('tab-content-active');
    }
  }

  // Performance Charts
  initializePerformanceCharts() {
    this.createLoadTimeChart();
    this.createErrorRateChart();
    this.createSatisfactionChart();
    this.createFeatureHealthChart();
  }

  createLoadTimeChart() {
    const ctx = document.getElementById('loadTimeChart');
    if (ctx) {
      new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: {
          labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
          datasets: [{
            label: 'Load Time',
            data: [180, 220, 280, 320, 250, 200],
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
          plugins: { legend: { display: false } },
          scales: {
            x: {
              grid: { color: '#404040' },
              ticks: { color: '#B0B0B0', font: { size: 10 } }
            },
            y: {
              grid: { color: '#404040' },
              ticks: { 
                color: '#B0B0B0', 
                font: { size: 10 },
                callback: function(value) { return value + 'ms'; }
              }
            }
          }
        }
      });
    }
  }

  createErrorRateChart() {
    const ctx = document.getElementById('errorRateChart');
    if (ctx) {
      new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: {
          labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
          datasets: [{
            label: 'Error Rate',
            data: [0.05, 0.12, 0.08, 0.15, 0.09, 0.06],
            borderColor: '#DC3545',
            backgroundColor: 'rgba(220, 53, 69, 0.1)',
            borderWidth: 2,
            fill: true,
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: {
              grid: { color: '#404040' },
              ticks: { color: '#B0B0B0', font: { size: 10 } }
            },
            y: {
              grid: { color: '#404040' },
              ticks: { 
                color: '#B0B0B0', 
                font: { size: 10 },
                callback: function(value) { return value + '%'; }
              }
            }
          }
        }
      });
    }
  }

  createSatisfactionChart() {
    const ctx = document.getElementById('satisfactionChart');
    if (ctx) {
      new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: {
          labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
          datasets: [{
            label: 'Satisfaction',
            data: [4.2, 4.5, 4.7, 4.8],
            borderColor: '#28A745',
            backgroundColor: 'rgba(40, 167, 69, 0.1)',
            borderWidth: 2,
            fill: true,
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: {
              grid: { color: '#404040' },
              ticks: { color: '#B0B0B0', font: { size: 10 } }
            },
            y: {
              min: 0,
              max: 5,
              grid: { color: '#404040' },
              ticks: { 
                color: '#B0B0B0', 
                font: { size: 10 },
                callback: function(value) { return value + '/5'; }
              }
            }
          }
        }
      });
    }
  }

  createFeatureHealthChart() {
    const ctx = document.getElementById('featureHealthChart');
    if (ctx) {
      new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: {
          labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
          datasets: [{
            label: 'Health Score',
            data: [95, 97, 94, 98, 96, 99],
            borderColor: '#28A745',
            backgroundColor: 'rgba(40, 167, 69, 0.1)',
            borderWidth: 2,
            fill: true,
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: {
              grid: { color: '#404040' },
              ticks: { color: '#B0B0B0', font: { size: 10 } }
            },
            y: {
              min: 80,
              max: 100,
              grid: { color: '#404040' },
              ticks: { 
                color: '#B0B0B0', 
                font: { size: 10 },
                callback: function(value) { return value + '%'; }
              }
            }
          }
        }
      });
    }
  }

  // Versioning Management
  initializeVersioning() {
    const versionActions = document.querySelectorAll('.version-actions .btn');
    versionActions.forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        this.handleVersionAction(btn);
      });
    });
  }

  handleVersionAction(button) {
    const action = button.textContent.trim();
    
    switch (action) {
      case 'View Changelog':
        this.showChangelog();
        break;
      case 'Rollback':
        this.confirmRollback();
        break;
      case 'Deploy New Version':
        this.deployNewVersion();
        break;
    }
  }

  showChangelog() {
    // Create and show changelog modal
    const modal = this.createModal('Changelog', this.generateChangelogContent());
    document.body.appendChild(modal);
  }

  confirmRollback() {
    const confirmed = confirm('Are you sure you want to rollback to the previous version? This action cannot be undone.');
    if (confirmed) {
      this.performRollback();
    }
  }

  performRollback() {
    // Simulate rollback process
    this.showNotification('Rollback initiated...', 'warning');
    
    setTimeout(() => {
      this.showNotification('Rollback completed successfully', 'success');
      this.updateVersionTimeline();
    }, 3000);
  }

  deployNewVersion() {
    // Simulate deployment process
    this.showNotification('Deployment started...', 'info');
    
    setTimeout(() => {
      this.showNotification('New version deployed successfully', 'success');
      this.updateVersionTimeline();
    }, 5000);
  }

  updateVersionTimeline() {
    // Update version timeline with new version
    const timeline = document.querySelector('.version-timeline');
    const newVersion = this.createVersionItem('v2.2.0', 'Latest features and improvements', 'Live');
    timeline.insertBefore(newVersion, timeline.firstChild);
  }

  createVersionItem(version, description, status) {
    const item = document.createElement('div');
    item.className = 'version-item version-current';
    item.innerHTML = `
      <div class="version-marker"></div>
      <div class="version-content">
        <h4 class="version-title">${version} (Current)</h4>
        <p class="version-description">${description}</p>
        <div class="version-meta">
          <span class="version-date">${new Date().toISOString().split('T')[0]}</span>
          <span class="version-status status-live">${status}</span>
        </div>
      </div>
    `;
    return item;
  }

  generateChangelogContent() {
    return `
      <div class="changelog-content">
        <h3>Version 2.1.0</h3>
        <ul>
          <li>Enhanced crane valuation algorithms</li>
          <li>Improved performance monitoring</li>
          <li>New user interface components</li>
          <li>Bug fixes and stability improvements</li>
        </ul>
        
        <h3>Version 2.0.5</h3>
        <ul>
          <li>Performance optimizations</li>
          <li>Security updates</li>
          <li>Minor bug fixes</li>
        </ul>
      </div>
    `;
  }

  createModal(title, content) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
      <div class="modal-content">
        <div class="modal-header">
          <h3>${title}</h3>
          <button class="modal-close">&times;</button>
        </div>
        <div class="modal-body">
          ${content}
        </div>
      </div>
    `;
    
    // Close modal functionality
    modal.querySelector('.modal-close').addEventListener('click', () => {
      modal.remove();
    });
    
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.remove();
      }
    });
    
    return modal;
  }

  // Utility Functions
  logFeatureActivity(featureName, action) {
    const timestamp = new Date().toISOString();
    const logEntry = {
      timestamp,
      feature: featureName,
      action,
      user: 'Admin'
    };
    
    // Store in local storage for demo purposes
    const logs = JSON.parse(localStorage.getItem('featureLogs') || '[]');
    logs.unshift(logEntry);
    logs.splice(100); // Keep only last 100 entries
    localStorage.setItem('featureLogs', JSON.stringify(logs));
  }

  showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.classList.add('notification-show');
    }, 100);
    
    setTimeout(() => {
      notification.classList.remove('notification-show');
      setTimeout(() => {
        notification.remove();
      }, 300);
    }, 3000);
  }
}

// Initialize all managers when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  // Initialize based on current page
  if (document.querySelector('.webapp-user-management')) {
    new WebappUserManager();
  }
  
  if (document.querySelector('.activities-tracking')) {
    new ActivitiesTracker();
  }
  
  if (document.querySelector('.core-features-management')) {
    new CoreFeaturesManager();
  }
});

// CSS for notifications and modals
const additionalCSS = `
.notification {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 12px 20px;
  border-radius: 6px;
  color: white;
  font-weight: 500;
  z-index: 10000;
  transform: translateX(100%);
  transition: transform 0.3s ease;
}

.notification-show {
  transform: translateX(0);
}

.notification-success {
  background: #28a745;
}

.notification-error {
  background: #dc3545;
}

.notification-warning {
  background: #ffc107;
  color: #212529;
}

.notification-info {
  background: #007bff;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
}

.modal-content {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4) var(--space-6);
  border-bottom: 1px solid var(--border-primary);
}

.modal-header h3 {
  margin: 0;
  color: var(--text-primary);
}

.modal-close {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: var(--text-xl);
  cursor: pointer;
  padding: var(--space-2);
}

.modal-body {
  padding: var(--space-6);
}

.changelog-content h3 {
  color: var(--text-primary);
  margin-bottom: var(--space-3);
}

.changelog-content ul {
  color: var(--text-secondary);
  margin-bottom: var(--space-4);
}

.feedback-reply-form {
  margin-top: var(--space-4);
  padding: var(--space-4);
  background: var(--bg-primary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-primary);
}

.reply-textarea {
  width: 100%;
  min-height: 80px;
  padding: var(--space-3);
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  resize: vertical;
  margin-bottom: var(--space-3);
}

.reply-actions {
  display: flex;
  gap: var(--space-2);
  justify-content: flex-end;
}

.reply-indicator,
.resolved-indicator {
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  color: var(--accent-green);
  background: rgba(40, 167, 69, 0.2);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  margin-left: var(--space-2);
}

.resolved-indicator {
  color: var(--text-muted);
  background: rgba(108, 117, 125, 0.2);
}
`;

// Inject additional CSS
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalCSS;
document.head.appendChild(styleSheet);
```

This comprehensive JavaScript specification provides complete functionality for all webapp management features including real-time updates, interactive charts, user session management, activity tracking, feature flag controls, and performance monitoring.
