/**
 * Admin Layout Component
 * Provides consistent header, sidebar, and authorization for all admin pages
 */

class AdminLayout {
    constructor() {
        this.adminUser = null;
        this.isAuthorized = false;
        this.serverStatusAuthFailures = 0;
        this.serverStatusInterval = null;
        this.init();
    }

    async init() {
        // Check for admin token first - if no token, redirect immediately
        const adminToken = localStorage.getItem('admin_token') || localStorage.getItem('admin_access_token') || localStorage.getItem('access_token');
        const adminUser = JSON.parse(localStorage.getItem('admin_user') || '{}');
        
        if (!adminToken && (!adminUser || Object.keys(adminUser).length === 0)) {
            console.log('No admin token found, redirecting to login');
            this.redirectToLogin();
            return;
        }
        
        // If we have cached admin user, use it immediately for rendering
        if (adminUser && Object.keys(adminUser).length > 0) {
            this.adminUser = adminUser;
            this.isAuthorized = true;
        }
        
        // Render layout components immediately (don't wait for API check)
        this.renderHeader();
        this.renderSidebar();
        this.setupEventListeners();
        
        // Store instance globally for modal access
        window.adminLayout = this;
        
        // Dispatch event to notify that layout is ready
        window.dispatchEvent(new CustomEvent('adminLayoutReady'));
        
        // Check authorization in background (non-blocking)
        this.checkAuthorization().catch(error => {
            console.warn('Background auth check failed:', error);
            // Don't redirect if we already rendered - user might have valid cached session
        });
    }

    async checkAuthorization() {
        try {
            // Check for admin token
            const adminToken = localStorage.getItem('admin_token') || localStorage.getItem('admin_access_token') || localStorage.getItem('access_token');
            const adminUser = JSON.parse(localStorage.getItem('admin_user') || '{}');
            
            if (!adminToken) {
                console.log('No admin token found');
                this.isAuthorized = false;
                this.redirectToLogin();
                return;
            }

            // If we have admin user in localStorage, use it as fallback
            if (adminUser && Object.keys(adminUser).length > 0) {
                this.adminUser = adminUser;
                console.log('Using admin user from localStorage (fallback)');
                // Still try to verify, but don't block rendering if API fails
            }

            // Verify token with API - try multiple endpoints
            let apiSuccess = false;
            
            // Try /admin/auth/profile first (admin auth endpoint)
            try {
                // Determine API base URL based on current environment
                const hostname = window.location.hostname;
                let apiBase;
                if (hostname === 'dev.craneintelligence.tech') {
                    apiBase = 'https://dev.craneintelligence.tech/api/v1';
                } else if (hostname === 'uat.craneintelligence.tech') {
                    apiBase = 'https://uat.craneintelligence.tech/api/v1';
                } else if (hostname === 'localhost' || hostname === '127.0.0.1') {
                    apiBase = '/api/v1';
                } else {
                    apiBase = 'https://craneintelligence.tech/api/v1';
                }
                
                const response = await fetch(`${apiBase}/admin/auth/profile`, {
                    headers: {
                        'Authorization': `Bearer ${adminToken}`,
                        'Content-Type': 'application/json'
                    }
                });
                
                if (response.ok) {
                    const data = await response.json();
                    this.adminUser = data || adminUser;
                    this.isAuthorized = true;
                    localStorage.setItem('admin_user', JSON.stringify(this.adminUser));
                    apiSuccess = true;
                    console.log('Admin profile loaded from API');
                } else if (response.status === 401 || response.status === 403) {
                    // Token is invalid or expired
                    console.log('Token is invalid or expired, clearing tokens and redirecting to login');
                    localStorage.removeItem('admin_token');
                    localStorage.removeItem('admin_access_token');
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('admin_refresh_token');
                    localStorage.removeItem('admin_user');
                    this.isAuthorized = false;
                    this.redirectToLogin();
                    return;
                } else if (response.status === 404) {
                    // Endpoint doesn't exist, try dashboard stats
                    console.log('Admin profile endpoint not found, trying dashboard stats');
                    const statsResponse = await fetch(`${apiBase}/admin/dashboard/stats`, {
                        headers: {
                            'Authorization': `Bearer ${adminToken}`,
                            'Content-Type': 'application/json'
                        }
                    });
                    
                    if (statsResponse.ok) {
                        apiSuccess = true;
                        // Use admin user from localStorage
                        if (adminUser && Object.keys(adminUser).length > 0) {
                            this.adminUser = adminUser;
                            this.isAuthorized = true;
                            console.log('Using admin user from localStorage (dashboard stats OK)');
                        }
                    } else if (statsResponse.status === 401 || statsResponse.status === 403) {
                        // Token is invalid
                        console.log('Token is invalid, clearing tokens');
                        localStorage.removeItem('admin_token');
                        localStorage.removeItem('access_token');
                        localStorage.removeItem('admin_refresh_token');
                        this.isAuthorized = false;
                        return;
                    }
                }
            } catch (e) {
                console.log('API check failed, using localStorage fallback:', e);
                // Don't fail authorization on network errors - use localStorage fallback
            }
            
            // If API check failed, try to get user from localStorage
            if (!apiSuccess) {
                // Check if admin_user exists in localStorage with valid role
                if (adminUser && Object.keys(adminUser).length > 0) {
                    const hasAdminRole = adminUser.role === 'admin' || 
                                       adminUser.admin_role || 
                                       adminUser.user_role === 'admin';
                    if (hasAdminRole) {
                        this.adminUser = adminUser;
                        this.isAuthorized = true;
                        console.log('Using admin user from localStorage (fallback)');
                    } else {
                        this.isAuthorized = false;
                        console.log('No valid admin role found in localStorage');
                    }
                } else {
                    this.isAuthorized = false;
                    console.log('No admin user found in localStorage');
                }
            }
        } catch (error) {
            console.error('Authorization check failed:', error);
            // Fallback: check if admin_user exists in localStorage
            const adminUser = JSON.parse(localStorage.getItem('admin_user') || '{}');
            if (adminUser && (adminUser.role === 'admin' || adminUser.admin_role)) {
                this.adminUser = adminUser;
                this.isAuthorized = true;
            } else {
                this.isAuthorized = false;
            }
        }
    }

    redirectToLogin() {
        window.location.href = '/admin/login.html';
    }

    renderHeader() {
        const pageTitle = document.title.replace(' - Crane Intelligence Admin', '') || 'Admin Dashboard';
        const adminName = this.adminUser?.full_name || this.adminUser?.email || 'Admin User';
        const adminRole = this.adminUser?.admin_role || this.adminUser?.role || 'Administrator';
        const initials = adminName.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);

        const headerHTML = `
            <header class="admin-header">
                <div class="header-left">
                    <div class="logo">
                        <a href="dashboard.html" style="display: flex; align-items: center; text-decoration: none;">
                            <img src="../images/logos/crane-intelligence-logo.svg" alt="Crane Intelligence" class="logo-img" 
                                 onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                            <div class="logo-text-fallback" style="display: none; flex-direction: column; margin-left: 12px;">
                                <span style="color: #00FF85; font-size: 20px; font-weight: 700;">CRANE</span>
                                <span style="color: #FFFFFF; font-size: 12px;">INTELLIGENCE</span>
                            </div>
                        </a>
                    </div>
                    <h1 class="page-title">${pageTitle}</h1>
                </div>
                <div class="header-right">
                    <!-- Server Status Indicator -->
                    <div class="server-status-container" id="serverStatusContainer" style="display: flex; align-items: center; gap: 8px; margin-right: 15px; padding: 8px 12px; background: rgba(255, 255, 255, 0.05); border-radius: 8px; cursor: pointer;" onclick="window.showServerStatusDetails && window.showServerStatusDetails()">
                        <div class="server-status-indicator" id="serverStatusIndicator" style="width: 10px; height: 10px; border-radius: 50%; background: #00FF85; animation: pulse 2s infinite;"></div>
                        <span class="server-status-text" id="serverStatusText" style="font-size: 12px; color: #B0B0B0;">Checking...</span>
                    </div>
                    <!-- Notification Bell -->
                    <div class="notification-bell-container">
                        <button class="notification-bell" id="adminNotificationBell" aria-label="Notifications">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                                <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
                            </svg>
                            <span class="notification-badge" id="adminNotificationBadge" style="display: none;">0</span>
                        </button>
                        <div class="notification-dropdown" id="adminNotificationDropdown">
                            <div class="notification-header">
                                <h3>Notifications</h3>
                                <button class="mark-all-read" id="adminMarkAllReadBtn">Mark all as read</button>
                            </div>
                            <div class="notification-list" id="adminNotificationList">
                                <div class="notification-empty">No notifications</div>
                            </div>
                            <div class="notification-footer">
                                <a href="notifications.html" class="view-all-link">View all notifications</a>
                            </div>
                        </div>
                    </div>
                    <!-- Profile Dropdown -->
                    <div class="admin-profile" id="adminProfile">
                        <div class="profile-avatar">
                            <div class="avatar-initials">${initials}</div>
                        </div>
                        <div class="profile-info">
                            <div class="profile-name">${adminName}</div>
                            <div class="profile-role">${adminRole}</div>
                        </div>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M6 9l6 6 6-6"></path>
                        </svg>
                        <div class="profile-dropdown" id="adminProfileDropdown">
                            <a href="profile.html" class="dropdown-item">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                                    <circle cx="12" cy="7" r="4"></circle>
                                </svg>
                                Profile
                            </a>
                            <a href="settings.html" class="dropdown-item">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <circle cx="12" cy="12" r="3"></circle>
                                    <path d="M12 1v6m0 6v6M5.64 5.64l4.24 4.24m4.24 4.24l4.24 4.24M1 12h6m6 0h6M5.64 18.36l4.24-4.24m4.24-4.24l4.24-4.24"></path>
                                </svg>
                                Settings
                            </a>
                            <div class="dropdown-divider"></div>
                            <a href="#" class="dropdown-item" id="adminLogoutBtn">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                                    <polyline points="16 17 21 12 16 7"></polyline>
                                    <line x1="21" y1="12" x2="9" y2="12"></line>
                                </svg>
                                Logout
                            </a>
                        </div>
                    </div>
                </div>
            </header>
        `;

        // Insert header into container or at beginning of body
        let headerContainer = document.getElementById('admin-header-container');
        if (!headerContainer) {
            // Create container if it doesn't exist
            headerContainer = document.createElement('div');
            headerContainer.id = 'admin-header-container';
            document.body.insertBefore(headerContainer, document.body.firstChild);
        }
        headerContainer.innerHTML = headerHTML;
        
        // Initialize server status monitoring
        this.initServerStatusMonitoring();
    }
    
    initServerStatusMonitoring() {
        // Fetch server status immediately
        this.updateServerStatus();
        
        // Update every 30 seconds, but stop if we get too many auth errors
        this.serverStatusInterval = setInterval(() => {
            this.updateServerStatus();
        }, 30000);
    }
    
    async updateServerStatus() {
        // Stop retrying if we've had auth failures
        if (this.serverStatusAuthFailures >= 1) {
            if (this.serverStatusInterval) {
                clearInterval(this.serverStatusInterval);
                this.serverStatusInterval = null;
            }
            return;
        }
        
        try {
            const API_BASE = window.API_BASE || '/api/v1';
            const token = localStorage.getItem('admin_token') || localStorage.getItem('admin_access_token') || localStorage.getItem('access_token');
            
            if (!token) {
                // No token, stop monitoring
                if (this.serverStatusInterval) {
                    clearInterval(this.serverStatusInterval);
                    this.serverStatusInterval = null;
                }
                return;
            }
            
            // Server-status endpoint doesn't require auth
            // Don't send Authorization header to avoid validation errors
            const response = await fetch(`${API_BASE}/admin/server-status`, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.status === 401 || response.status === 403 || response.status === 422) {
                // Authentication failed, stop monitoring immediately (don't retry auth errors)
                if (this.serverStatusInterval) {
                    clearInterval(this.serverStatusInterval);
                    this.serverStatusInterval = null;
                }
                // Only log once to avoid spam
                if (!this.serverStatusAuthFailures) {
                    console.warn('Stopping server status monitoring due to authentication failure');
                }
                this.serverStatusAuthFailures = 1;
                return;
            }
            
            // Reset failure counter on success
            this.serverStatusAuthFailures = 0;
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            this.renderServerStatus(data);
        } catch (error) {
            // Only log non-auth errors to avoid spam
            if (!error.message.includes('401') && !error.message.includes('403')) {
                console.error('Error fetching server status:', error);
            }
            // Don't render error status on auth failures to avoid UI spam
            if (this.serverStatusAuthFailures < 3) {
                this.renderServerStatus({
                    overall: 'unknown',
                    servers: [],
                    error: 'Unable to fetch server status'
                });
            }
        }
    }
    
    renderServerStatus(data) {
        const indicator = document.getElementById('serverStatusIndicator');
        const text = document.getElementById('serverStatusText');
        const container = document.getElementById('serverStatusContainer');
        
        if (!indicator || !text || !container) return;
        
        let status = data.overall || 'unknown';
        let statusColor = '#00FF85'; // Green
        let statusText = 'All Systems Operational';
        
        // Count issues
        const downServers = (data.servers || []).filter(s => s.status === 'down').length;
        const degradedServers = (data.servers || []).filter(s => s.status === 'degraded').length;
        
        if (downServers > 0) {
            status = 'down';
            statusColor = '#FF4444'; // Red
            statusText = `${downServers} Server${downServers > 1 ? 's' : ''} Down`;
            container.style.background = 'rgba(255, 68, 68, 0.2)';
            container.style.border = '1px solid rgba(255, 68, 68, 0.5)';
        } else if (degradedServers > 0) {
            status = 'degraded';
            statusColor = '#FFD600'; // Yellow
            statusText = `${degradedServers} Server${degradedServers > 1 ? 's' : ''} Degraded`;
            container.style.background = 'rgba(255, 214, 0, 0.2)';
            container.style.border = '1px solid rgba(255, 214, 0, 0.5)';
        } else if (status === 'healthy') {
            statusColor = '#00FF85'; // Green
            statusText = 'All Systems Operational';
            container.style.background = 'rgba(0, 255, 133, 0.1)';
            container.style.border = '1px solid rgba(0, 255, 133, 0.3)';
        } else {
            statusColor = '#B0B0B0'; // Gray
            statusText = 'Status Unknown';
            container.style.background = 'rgba(255, 255, 255, 0.05)';
            container.style.border = 'none';
        }
        
        indicator.style.background = statusColor;
        text.textContent = statusText;
        text.style.color = statusColor;
        
        // Store data for details modal
        window.serverStatusData = data;
    }
    
    // Server status details modal function
    showServerStatusDetails() {
        const data = window.serverStatusData || { servers: [] };
        
        // Create modal
        const modal = document.createElement('div');
        modal.id = 'serverStatusModal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        `;
        
        const modalContent = document.createElement('div');
        modalContent.style.cssText = `
            background: #1A1A1A;
            border: 1px solid #333333;
            border-radius: 12px;
            padding: 30px;
            max-width: 800px;
            width: 100%;
            max-height: 90vh;
            overflow-y: auto;
            color: #FFFFFF;
        `;
        
        let serversHTML = '';
        if (data.servers && data.servers.length > 0) {
            serversHTML = data.servers.map(server => {
                let statusColor = '#00FF85';
                let statusIcon = '✓';
                if (server.status === 'down') {
                    statusColor = '#FF4444';
                    statusIcon = '✗';
                } else if (server.status === 'degraded') {
                    statusColor = '#FFD600';
                    statusIcon = '⚠';
                }
                
                return `
                    <div style="padding: 20px; background: #2A2A2A; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid ${statusColor};">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                            <h3 style="color: #FFFFFF; margin: 0; font-size: 18px;">${server.name || server.server}</h3>
                            <span style="color: ${statusColor}; font-weight: 600; font-size: 14px;">
                                ${statusIcon} ${server.status ? server.status.toUpperCase() : 'UNKNOWN'}
                            </span>
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px;">
                            <div>
                                <div style="color: #B0B0B0; font-size: 12px; margin-bottom: 5px;">API Status</div>
                                <div style="color: ${server.api_status === 'healthy' ? '#00FF85' : server.api_status === 'down' ? '#FF4444' : '#FFD600'}; font-weight: 600;">
                                    ${server.api_status ? server.api_status.toUpperCase() : 'UNKNOWN'}
                                </div>
                                ${server.api_error ? `<div style="color: #FF4444; font-size: 11px; margin-top: 5px;">${server.api_error}</div>` : ''}
                                ${server.api_response_time ? `<div style="color: #888; font-size: 11px; margin-top: 5px;">Response: ${server.api_response_time}ms</div>` : ''}
                            </div>
                            <div>
                                <div style="color: #B0B0B0; font-size: 12px; margin-bottom: 5px;">Website Status</div>
                                <div style="color: ${server.website_status === 'healthy' ? '#00FF85' : server.website_status === 'down' ? '#FF4444' : '#FFD600'}; font-weight: 600;">
                                    ${server.website_status ? server.website_status.toUpperCase() : 'UNKNOWN'}
                                </div>
                                ${server.website_error ? `<div style="color: #FF4444; font-size: 11px; margin-top: 5px;">${server.website_error}</div>` : ''}
                                ${server.website_response_time ? `<div style="color: #888; font-size: 11px; margin-top: 5px;">Response: ${server.website_response_time}ms</div>` : ''}
                            </div>
                        </div>
                        ${server.timestamp ? `<div style="color: #666; font-size: 11px; margin-top: 10px;">Last checked: ${new Date(server.timestamp).toLocaleString()}</div>` : ''}
                    </div>
                `;
            }).join('');
        } else {
            serversHTML = '<div style="text-align: center; padding: 40px; color: #B0B0B0;">No server data available</div>';
        }
        
        modalContent.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px;">
                <h2 style="color: #00FF85; margin: 0; font-size: 24px;">Server Status</h2>
                <button onclick="document.getElementById('serverStatusModal').remove()" style="
                    background: transparent;
                    border: none;
                    color: #B0B0B0;
                    font-size: 24px;
                    cursor: pointer;
                    padding: 0;
                    width: 30px;
                    height: 30px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                ">×</button>
            </div>
            <div style="margin-bottom: 20px;">
                ${serversHTML}
            </div>
            <div style="text-align: center; margin-top: 20px;">
                <button onclick="document.getElementById('serverStatusModal').remove()" style="
                    background: #00FF85;
                    color: #1A1A1A;
                    border: none;
                    padding: 12px 32px;
                    border-radius: 8px;
                    cursor: pointer;
                    font-weight: 600;
                    font-size: 14px;
                ">Close</button>
            </div>
        `;
        
        modal.appendChild(modalContent);
        document.body.appendChild(modal);
        
        // Close on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    renderSidebar() {
        const currentPage = window.location.pathname.split('/').pop() || 'dashboard.html';
        
        // Define which pages belong to which categories for auto-expansion
        const categoryPages = {
            'user-management': ['users.html', 'admin-users.html', 'consultations.html'],
            'reports-analytics': ['analytics.html', 'fmv-reports.html', 'valuations.html'],
            'financial': ['payments.html', 'payment-reconciliation.html', 'refunds.html'],
            'system-management': ['cranes.html', 'algorithm.html', 'system-health.html'],
            'security-compliance': ['security-2fa.html', 'sessions.html', 'audit-logs.html', 'gdpr-compliance.html'],
            'settings': ['roles.html', 'email-management.html', 'bulk-operations.html']
        };
        
        // Find which category contains the current page
        const getActiveCategory = () => {
            for (const [category, pages] of Object.entries(categoryPages)) {
                if (pages.includes(currentPage)) {
                    return category;
                }
            }
            return null;
        };
        
        const activeCategory = getActiveCategory();
        
        const sidebarHTML = `
            <aside class="admin-sidebar">
                <nav class="sidebar-nav">
                    <ul class="sidebar-menu" style="list-style: none; padding: 0; margin: 0;">
                        <!-- Dashboard -->
                        <li style="margin: 0;">
                            <a href="dashboard.html" class="${currentPage === 'dashboard.html' ? 'active' : ''}" style="display: flex; align-items: center; gap: 12px; padding: 12px 24px; color: #B0B0B0; text-decoration: none; transition: all 0.2s ease; border-left: 3px solid transparent;">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                                    <polyline points="9 22 9 12 15 12 15 22"></polyline>
                                </svg>
                                Dashboard
                            </a>
                        </li>
                        
                        <!-- Category Separator -->
                        <li style="margin: 16px 0 8px 0; padding: 0 24px;">
                            <div style="height: 1px; background: #333333; margin: 0;"></div>
                        </li>
                        
                        <!-- User Management Category -->
                        <li class="sidebar-category expanded" style="margin: 0;">
                            <div class="category-header" style="display: flex; align-items: center; justify-content: space-between; padding: 8px 24px; color: #808080; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; cursor: pointer;" onclick="this.parentElement.classList.toggle('expanded')">
                                <span>👥 User Management</span>
                                <svg class="category-arrow" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="transition: transform 0.2s;">
                                    <polyline points="6 9 12 15 18 9"></polyline>
                                </svg>
                            </div>
                            <ul class="category-items" style="list-style: none; padding: 0; margin: 0;">
                                <li style="margin: 0;">
                                    <a href="users.html" class="${currentPage === 'users.html' ? 'active' : ''}" style="display: flex; align-items: center; gap: 12px; padding: 10px 24px 10px 48px; color: #B0B0B0; text-decoration: none; transition: all 0.2s ease; border-left: 3px solid transparent;">
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                                            <circle cx="9" cy="7" r="4"></circle>
                                            <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                                            <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                                        </svg>
                                        Users
                                    </a>
                                </li>
                                <li style="margin: 0;">
                                    <a href="admin-users.html" class="${currentPage === 'admin-users.html' ? 'active' : ''}" style="display: flex; align-items: center; gap: 12px; padding: 10px 24px 10px 48px; color: #B0B0B0; text-decoration: none; transition: all 0.2s ease; border-left: 3px solid transparent;">
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                                            <circle cx="12" cy="7" r="4"></circle>
                                        </svg>
                                        Admin Users
                                    </a>
                                </li>
                                <li style="margin: 0;">
                                    <a href="consultations.html" class="${currentPage === 'consultations.html' ? 'active' : ''}" style="display: flex; align-items: center; gap: 12px; padding: 10px 24px 10px 48px; color: #B0B0B0; text-decoration: none; transition: all 0.2s ease; border-left: 3px solid transparent;">
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                                        </svg>
                                        Consultations
                                    </a>
                                </li>
                            </ul>
                        </li>
                        
                        <!-- Reports & Analytics Category -->
                        <li class="sidebar-category expanded" style="margin: 0;">
                            <div class="category-header" style="display: flex; align-items: center; justify-content: space-between; padding: 8px 24px; color: #808080; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; cursor: pointer;" onclick="this.parentElement.classList.toggle('expanded')">
                                <span>📊 Reports & Analytics</span>
                                <svg class="category-arrow" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="transition: transform 0.2s;">
                                    <polyline points="6 9 12 15 18 9"></polyline>
                                </svg>
                            </div>
                            <ul class="category-items" style="list-style: none; padding: 0; margin: 0;">
                                <li style="margin: 0;">
                                    <a href="analytics.html" class="${currentPage === 'analytics.html' ? 'active' : ''}" style="display: flex; align-items: center; gap: 12px; padding: 10px 24px 10px 48px; color: #B0B0B0; text-decoration: none; transition: all 0.2s ease; border-left: 3px solid transparent;">
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <line x1="18" y1="20" x2="18" y2="10"></line>
                                            <line x1="12" y1="20" x2="12" y2="4"></line>
                                            <line x1="6" y1="20" x2="6" y2="14"></line>
                                        </svg>
                                        Analytics
                                    </a>
                                </li>
                                <li style="margin: 0;">
                                    <a href="fmv-reports.html" class="${currentPage === 'fmv-reports.html' ? 'active' : ''}" style="display: flex; align-items: center; gap: 12px; padding: 10px 24px 10px 48px; color: #B0B0B0; text-decoration: none; transition: all 0.2s ease; border-left: 3px solid transparent;">
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                                            <polyline points="14 2 14 8 20 8"></polyline>
                                            <line x1="16" y1="13" x2="8" y2="13"></line>
                                            <line x1="16" y1="17" x2="8" y2="17"></line>
                                        </svg>
                                        FMV Reports
                                    </a>
                                </li>
                                <li style="margin: 0;">
                                    <a href="valuations.html" class="${currentPage === 'valuations.html' ? 'active' : ''}" style="display: flex; align-items: center; gap: 12px; padding: 10px 24px 10px 48px; color: #B0B0B0; text-decoration: none; transition: all 0.2s ease; border-left: 3px solid transparent;">
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                                        </svg>
                                        Valuations
                                    </a>
                                </li>
                            </ul>
                        </li>
                        
                        <!-- Financial Management Category -->
                        <li class="sidebar-category expanded" style="margin: 0;">
                            <div class="category-header" style="display: flex; align-items: center; justify-content: space-between; padding: 8px 24px; color: #808080; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; cursor: pointer;" onclick="this.parentElement.classList.toggle('expanded')">
                                <span>💳 Financial Management</span>
                                <svg class="category-arrow" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="transition: transform 0.2s;">
                                    <polyline points="6 9 12 15 18 9"></polyline>
                                </svg>
                            </div>
                            <ul class="category-items" style="list-style: none; padding: 0; margin: 0;">
                                <li style="margin: 0;">
                                    <a href="payments.html" class="${currentPage === 'payments.html' ? 'active' : ''}" style="display: flex; align-items: center; gap: 12px; padding: 10px 24px 10px 48px; color: #B0B0B0; text-decoration: none; transition: all 0.2s ease; border-left: 3px solid transparent;">
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <line x1="12" y1="1" x2="12" y2="23"></line>
                                            <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                                        </svg>
                                        Payments
                                    </a>
                                </li>
                                <li style="margin: 0;">
                                    <a href="payment-reconciliation.html" class="${currentPage === 'payment-reconciliation.html' ? 'active' : ''}" style="display: flex; align-items: center; gap: 12px; padding: 10px 24px 10px 48px; color: #B0B0B0; text-decoration: none; transition: all 0.2s ease; border-left: 3px solid transparent;">
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <line x1="12" y1="1" x2="12" y2="23"></line>
                                            <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                                        </svg>
                                        Payment Reconciliation
                                    </a>
                                </li>
                                <li style="margin: 0;">
                                    <a href="refunds.html" class="${currentPage === 'refunds.html' ? 'active' : ''}" style="display: flex; align-items: center; gap: 12px; padding: 10px 24px 10px 48px; color: #B0B0B0; text-decoration: none; transition: all 0.2s ease; border-left: 3px solid transparent;">
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <polyline points="23 4 23 10 17 10"></polyline>
                                            <polyline points="1 20 1 14 7 14"></polyline>
                                            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
                                        </svg>
                                        Refunds
                                    </a>
                                </li>
                            </ul>
                        </li>
                        
                        <!-- System Management Category -->
                        <li class="sidebar-category expanded" style="margin: 0;">
                            <div class="category-header" style="display: flex; align-items: center; justify-content: space-between; padding: 8px 24px; color: #808080; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; cursor: pointer;" onclick="this.parentElement.classList.toggle('expanded')">
                                <span>⚙️ System Management</span>
                                <svg class="category-arrow" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="transition: transform 0.2s;">
                                    <polyline points="6 9 12 15 18 9"></polyline>
                                </svg>
                            </div>
                            <ul class="category-items" style="list-style: none; padding: 0; margin: 0;">
                                <li style="margin: 0;">
                                    <a href="cranes.html" class="${currentPage === 'cranes.html' ? 'active' : ''}" style="display: flex; align-items: center; gap: 12px; padding: 10px 24px 10px 48px; color: #B0B0B0; text-decoration: none; transition: all 0.2s ease; border-left: 3px solid transparent;">
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <path d="M20 7h-4V4a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v3H2a1 1 0 0 0-1 1v11a2 2 0 0 0 2 2h18a2 2 0 0 0 2-2V8a1 1 0 0 0-1-1z"></path>
                                        </svg>
                                        Cranes
                                    </a>
                                </li>
                                <li style="margin: 0;">
                                    <a href="algorithm.html" class="${currentPage === 'algorithm.html' ? 'active' : ''}" style="display: flex; align-items: center; gap: 12px; padding: 10px 24px 10px 48px; color: #B0B0B0; text-decoration: none; transition: all 0.2s ease; border-left: 3px solid transparent;">
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <circle cx="12" cy="12" r="10"></circle>
                                            <polyline points="12 6 12 12 16 14"></polyline>
                                        </svg>
                                        Algorithm
                                    </a>
                                </li>
                                <li style="margin: 0;">
                                    <a href="system-health.html" class="${currentPage === 'system-health.html' ? 'active' : ''}" style="display: flex; align-items: center; gap: 12px; padding: 10px 24px 10px 48px; color: #B0B0B0; text-decoration: none; transition: all 0.2s ease; border-left: 3px solid transparent;">
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                                            <polyline points="22 4 12 14.01 9 11.01"></polyline>
                                        </svg>
                                        System Health
                                    </a>
                                </li>
                            </ul>
                        </li>
                        
                        <!-- Security & Compliance Category -->
                        <li class="sidebar-category expanded" style="margin: 0;">
                            <div class="category-header" style="display: flex; align-items: center; justify-content: space-between; padding: 8px 24px; color: #808080; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; cursor: pointer;" onclick="this.parentElement.classList.toggle('expanded')">
                                <span>🔒 Security & Compliance</span>
                                <svg class="category-arrow" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="transition: transform 0.2s;">
                                    <polyline points="6 9 12 15 18 9"></polyline>
                                </svg>
                            </div>
                            <ul class="category-items" style="list-style: none; padding: 0; margin: 0;">
                                <li style="margin: 0;">
                                    <a href="security-2fa.html" class="${currentPage === 'security-2fa.html' ? 'active' : ''}" style="display: flex; align-items: center; gap: 12px; padding: 10px 24px 10px 48px; color: #B0B0B0; text-decoration: none; transition: all 0.2s ease; border-left: 3px solid transparent;">
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                                            <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                                        </svg>
                                        Security & 2FA
                                    </a>
                                </li>
                                <li style="margin: 0;">
                                    <a href="sessions.html" class="${currentPage === 'sessions.html' ? 'active' : ''}" style="display: flex; align-items: center; gap: 12px; padding: 10px 24px 10px 48px; color: #B0B0B0; text-decoration: none; transition: all 0.2s ease; border-left: 3px solid transparent;">
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                                            <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                                        </svg>
                                        Sessions
                                    </a>
                                </li>
                                <li style="margin: 0;">
                                    <a href="audit-logs.html" class="${currentPage === 'audit-logs.html' ? 'active' : ''}" style="display: flex; align-items: center; gap: 12px; padding: 10px 24px 10px 48px; color: #B0B0B0; text-decoration: none; transition: all 0.2s ease; border-left: 3px solid transparent;">
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                                            <polyline points="14 2 14 8 20 8"></polyline>
                                            <line x1="16" y1="13" x2="8" y2="13"></line>
                                            <line x1="16" y1="17" x2="8" y2="17"></line>
                                        </svg>
                                        Audit Logs
                                    </a>
                                </li>
                                <li style="margin: 0;">
                                    <a href="gdpr-compliance.html" class="${currentPage === 'gdpr-compliance.html' ? 'active' : ''}" style="display: flex; align-items: center; gap: 12px; padding: 10px 24px 10px 48px; color: #B0B0B0; text-decoration: none; transition: all 0.2s ease; border-left: 3px solid transparent;">
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                                        </svg>
                                        GDPR Compliance
                                    </a>
                                </li>
                            </ul>
                        </li>
                        
                        <!-- Settings Category -->
                        <li class="sidebar-category expanded" style="margin: 0;">
                            <div class="category-header" style="display: flex; align-items: center; justify-content: space-between; padding: 8px 24px; color: #808080; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; cursor: pointer;" onclick="this.parentElement.classList.toggle('expanded')">
                                <span>⚙️ Settings</span>
                                <svg class="category-arrow" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="transition: transform 0.2s;">
                                    <polyline points="6 9 12 15 18 9"></polyline>
                                </svg>
                            </div>
                            <ul class="category-items" style="list-style: none; padding: 0; margin: 0;">
                                <li style="margin: 0;">
                                    <a href="roles.html" class="${currentPage === 'roles.html' ? 'active' : ''}" style="display: flex; align-items: center; gap: 12px; padding: 10px 24px 10px 48px; color: #B0B0B0; text-decoration: none; transition: all 0.2s ease; border-left: 3px solid transparent;">
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                                            <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                                        </svg>
                                        Role Settings
                                    </a>
                                </li>
                                <li style="margin: 0;">
                                    <a href="email-management.html" class="${currentPage === 'email-management.html' ? 'active' : ''}" style="display: flex; align-items: center; gap: 12px; padding: 10px 24px 10px 48px; color: #B0B0B0; text-decoration: none; transition: all 0.2s ease; border-left: 3px solid transparent;">
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                                            <polyline points="22,6 12,13 2,6"></polyline>
                                        </svg>
                                        Email Management
                                    </a>
                                </li>
                                <li style="margin: 0;">
                                    <a href="bulk-operations.html" class="${currentPage === 'bulk-operations.html' ? 'active' : ''}" style="display: flex; align-items: center; gap: 12px; padding: 10px 24px 10px 48px; color: #B0B0B0; text-decoration: none; transition: all 0.2s ease; border-left: 3px solid transparent;">
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <polyline points="16 18 22 12 16 6"></polyline>
                                            <polyline points="8 6 2 12 8 18"></polyline>
                                        </svg>
                                        Bulk Operations
                                    </a>
                                </li>
                            </ul>
                        </li>
                    </ul>
                </nav>
            </aside>
        `;

        // Add sidebar and layout CSS if not already present
        if (!document.getElementById('admin-layout-styles')) {
            const layoutStyle = document.createElement('style');
            layoutStyle.id = 'admin-layout-styles';
            layoutStyle.textContent = `
                .admin-main {
                    display: flex;
                    min-height: 100vh;
                    padding-top: 70px;
                    margin: 0;
                }
                .admin-sidebar {
                    width: 250px;
                    background: #0F0F0F;
                    border-right: 1px solid #333333;
                    padding: 20px 0;
                    position: fixed;
                    height: calc(100vh - 70px);
                    overflow-y: auto;
                    z-index: 100;
                    top: 70px;
                    left: 0;
                }
                .admin-content {
                    flex: 1;
                    margin-left: 250px;
                    padding: 20px;
                    background: #0F0F0F;
                    min-height: calc(100vh - 70px);
                }
                .sidebar-menu {
                    list-style: none;
                    padding: 0;
                    margin: 0;
                }
                .sidebar-menu li {
                    margin: 0;
                }
                .sidebar-menu a {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    padding: 12px 24px;
                    color: #B0B0B0;
                    text-decoration: none;
                    transition: all 0.2s ease;
                    border-left: 3px solid transparent;
                }
                .sidebar-menu a.active {
                    background: rgba(0, 255, 133, 0.1);
                    color: #00FF85;
                    border-left-color: #00FF85;
                }
                .sidebar-menu a:hover {
                    background: rgba(255, 255, 255, 0.05);
                    color: #FFFFFF;
                }
                .profile-dropdown, .notification-dropdown {
                    display: none;
                    position: absolute;
                    top: 100%;
                    right: 0;
                    background: #1A1A1A;
                    border: 1px solid #333333;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                    z-index: 1000;
                    min-width: 250px;
                    margin-top: 8px;
                }
                .profile-dropdown.show, .notification-dropdown.show {
                    display: block;
                }
                .sidebar-category .category-items {
                    max-height: 0;
                    overflow: hidden;
                    transition: max-height 0.3s ease;
                }
                .sidebar-category.expanded .category-items {
                    max-height: 500px;
                }
                .sidebar-category .category-arrow {
                    transition: transform 0.2s ease;
                }
                .sidebar-category.expanded .category-arrow {
                    transform: rotate(180deg);
                }
            `;
            document.head.appendChild(layoutStyle);
        }

        // Insert sidebar into container or create admin-main structure
        let sidebarContainer = document.getElementById('admin-sidebar-container');
        if (!sidebarContainer) {
            // Create sidebar container
            sidebarContainer = document.createElement('div');
            sidebarContainer.id = 'admin-sidebar-container';
            
            // Check if admin-main exists
            let adminMain = document.querySelector('.admin-main');
            if (!adminMain) {
                // Create admin-main structure
                adminMain = document.createElement('div');
                adminMain.className = 'admin-main';
                
                // Insert after header container
                const headerContainer = document.getElementById('admin-header-container');
                if (headerContainer && headerContainer.nextSibling) {
                    headerContainer.parentNode.insertBefore(adminMain, headerContainer.nextSibling);
                } else {
                    document.body.appendChild(adminMain);
                }
            }
            
            // Insert sidebar into admin-main
            adminMain.insertBefore(sidebarContainer, adminMain.firstChild);
            
            // Wrap existing content in admin-content if needed
            const existingContent = Array.from(document.body.children).filter(
                el => el.id !== 'admin-header-container' && 
                     el.id !== 'admin-sidebar-container' && 
                     !el.classList.contains('admin-main') &&
                     !el.classList.contains('admin-content') &&
                     el.tagName !== 'SCRIPT' &&
                     el.tagName !== 'STYLE'
            );
            
            if (existingContent.length > 0) {
                let adminContent = document.querySelector('.admin-content');
                if (!adminContent) {
                    adminContent = document.createElement('div');
                    adminContent.className = 'admin-content';
                    adminMain.appendChild(adminContent);
                }
                existingContent.forEach(el => {
                    if (el.parentNode === document.body) {
                        adminContent.appendChild(el);
                    }
                });
            } else if (!document.querySelector('.admin-content')) {
                // Create admin-content even if no existing content
                const adminContent = document.createElement('div');
                adminContent.className = 'admin-content';
                adminMain.appendChild(adminContent);
            }
        }
        sidebarContainer.innerHTML = sidebarHTML;
    }

    setupEventListeners() {
        // Profile dropdown
        const profileBtn = document.getElementById('adminProfile');
        const profileDropdown = document.getElementById('adminProfileDropdown');
        
        if (profileBtn && profileDropdown) {
            profileBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                profileDropdown.classList.toggle('show');
            });

            document.addEventListener('click', () => {
                profileDropdown.classList.remove('show');
            });
        }

        // Notification bell
        const notificationBell = document.getElementById('adminNotificationBell');
        const notificationDropdown = document.getElementById('adminNotificationDropdown');
        
        if (notificationBell && notificationDropdown) {
            notificationBell.addEventListener('click', (e) => {
                e.stopPropagation();
                notificationDropdown.classList.toggle('show');
                if (notificationDropdown.classList.contains('show')) {
                    this.loadNotifications();
                }
            });

            document.addEventListener('click', (e) => {
                if (!notificationDropdown.contains(e.target) && !notificationBell.contains(e.target)) {
                    notificationDropdown.classList.remove('show');
                }
            });
            
            // Mark all as read button
            const markAllReadBtn = document.getElementById('adminMarkAllReadBtn');
            if (markAllReadBtn) {
                markAllReadBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.markAllAsRead();
                });
            }
            
            // Load notifications on page load
            this.loadNotifications();
            // Refresh notifications every 30 seconds
            setInterval(() => {
                if (notificationDropdown.classList.contains('show')) {
                    this.loadNotifications();
                }
            }, 30000);
        }

        // Logout
        const logoutBtn = document.getElementById('adminLogoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.logout();
            });
        }
    }

    async loadNotifications() {
        try {
            const adminToken = localStorage.getItem('admin_token') || localStorage.getItem('admin_access_token') || localStorage.getItem('access_token');
            
            if (!adminToken) {
                // No token, don't try to load notifications
                return;
            }
            
            // Determine API base URL
            const hostname = window.location.hostname;
            let apiBase;
            if (hostname === 'dev.craneintelligence.tech') {
                apiBase = 'https://dev.craneintelligence.tech/api/v1';
            } else if (hostname === 'uat.craneintelligence.tech') {
                apiBase = 'https://uat.craneintelligence.tech/api/v1';
            } else if (hostname === 'localhost' || hostname === '127.0.0.1') {
                apiBase = '/api/v1';
            } else {
                apiBase = 'https://craneintelligence.tech/api/v1';
            }
            
            const response = await fetch(`${apiBase}/notifications/admin/notifications`, {
                headers: {
                    'Authorization': `Bearer ${adminToken}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.status === 401 || response.status === 403) {
                // Authentication failed - don't log error, just skip notifications
                // The checkAuthorization will handle redirect
                return;
            }

            if (response.ok) {
                const data = await response.json();
                console.log('[ADMIN NOTIFICATIONS] API response:', data);
                // Handle both response formats: {success, data, ...} and direct array
                const notifications = data.data || data.notifications || data || [];
                console.log('[ADMIN NOTIFICATIONS] Parsed notifications:', notifications.length);
                this.renderNotifications(notifications);
            } else {
                // Only log non-auth errors
                console.error('Failed to load notifications:', response.status, response.statusText);
                const errorData = await response.json().catch(() => ({}));
                console.error('Error details:', errorData);
            }
        } catch (error) {
            // Only log if it's not an auth-related error
            if (!error.message.includes('401') && !error.message.includes('403')) {
                console.error('Failed to load notifications:', error);
            }
        }
    }

    renderNotifications(notifications) {
        const list = document.getElementById('adminNotificationList');
        const badge = document.getElementById('adminNotificationBadge');
        
        if (!list) {
            console.warn('[ADMIN NOTIFICATIONS] Notification list element not found');
            return;
        }

        console.log('[ADMIN NOTIFICATIONS] Rendering', notifications.length, 'notifications');
        
        // API returns 'read' field, not 'is_read' - handle both formats
        const isRead = (n) => n.read !== undefined ? n.read : (n.is_read !== undefined ? n.is_read : false);
        const unreadCount = notifications.filter(n => !isRead(n)).length;
        console.log('[ADMIN NOTIFICATIONS] Unread count:', unreadCount);
        
        if (badge) {
            if (unreadCount > 0) {
                badge.textContent = unreadCount;
                badge.style.display = 'block';
            } else {
                badge.style.display = 'none';
            }
        }

        if (notifications.length === 0) {
            list.innerHTML = '<div class="notification-empty">No notifications</div>';
            return;
        }
        
        list.innerHTML = notifications.slice(0, 5).map(notif => {
            const read = isRead(notif);
            return `
            <div class="notification-item ${read ? '' : 'unread'}" data-notification-id="${notif.id}">
                <div class="notification-content">
                    <div class="notification-title">${notif.title || 'Notification'}</div>
                    <div class="notification-message">${notif.message || ''}</div>
                    <div class="notification-time">${this.formatTime(notif.created_at)}</div>
                </div>
            </div>
        `;
        }).join('');
        
        // Add click handlers to mark as read
        list.querySelectorAll('.notification-item').forEach(item => {
            item.addEventListener('click', async () => {
                const notificationId = item.dataset.notificationId;
                if (notificationId && !item.classList.contains('read')) {
                    await this.markAsRead(notificationId);
                    item.classList.add('read');
                    item.classList.remove('unread');
                    // Update badge count
                    const newUnreadCount = notifications.filter(n => !isRead(n) && n.id != notificationId).length;
                    if (badge) {
                        if (newUnreadCount > 0) {
                            badge.textContent = newUnreadCount;
                        } else {
                            badge.style.display = 'none';
                        }
                    }
                }
            });
        });
    }
    
    async markAsRead(notificationId) {
        try {
            const adminToken = localStorage.getItem('admin_token') || localStorage.getItem('access_token');
            // Determine API base URL
            const hostname = window.location.hostname;
            let apiBase;
            if (hostname === 'dev.craneintelligence.tech') {
                apiBase = 'https://dev.craneintelligence.tech/api/v1';
            } else if (hostname === 'uat.craneintelligence.tech') {
                apiBase = 'https://uat.craneintelligence.tech/api/v1';
            } else if (hostname === 'localhost' || hostname === '127.0.0.1') {
                apiBase = '/api/v1';
            } else {
                apiBase = 'https://craneintelligence.tech/api/v1';
            }
            
            const response = await fetch(`${apiBase}/notifications/admin/notifications/${notificationId}/read`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${adminToken}`,
                    'Content-Type': 'application/json'
                }
            });
            if (response.ok) {
                // Reload notifications to update UI
                this.loadNotifications();
            }
        } catch (error) {
            console.error('Failed to mark notification as read:', error);
        }
    }
    
    async markAllAsRead() {
        try {
            const adminToken = localStorage.getItem('admin_token') || localStorage.getItem('access_token');
            // Determine API base URL
            const hostname = window.location.hostname;
            let apiBase;
            if (hostname === 'dev.craneintelligence.tech') {
                apiBase = 'https://dev.craneintelligence.tech/api/v1';
            } else if (hostname === 'uat.craneintelligence.tech') {
                apiBase = 'https://uat.craneintelligence.tech/api/v1';
            } else if (hostname === 'localhost' || hostname === '127.0.0.1') {
                apiBase = '/api/v1';
            } else {
                apiBase = 'https://craneintelligence.tech/api/v1';
            }
            
            const response = await fetch(`${apiBase}/notifications/admin/notifications/read-all`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${adminToken}`,
                    'Content-Type': 'application/json'
                }
            });
            if (response.ok) {
                // Reload notifications to update UI
                this.loadNotifications();
            }
        } catch (error) {
            console.error('Failed to mark all notifications as read:', error);
        }
    }

    formatTime(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);

        if (minutes < 1) return 'Just now';
        if (minutes < 60) return `${minutes}m ago`;
        if (hours < 24) return `${hours}h ago`;
        if (days < 7) return `${days}d ago`;
        return date.toLocaleDateString();
    }

    logout() {
        localStorage.removeItem('admin_token');
        localStorage.removeItem('access_token');
        localStorage.removeItem('admin_user');
        window.location.href = '/admin/login.html';
    }
}

// Make function globally available
if (typeof window !== 'undefined') {
    window.showServerStatusDetails = function() {
        if (window.adminLayout && window.adminLayout.showServerStatusDetails) {
            window.adminLayout.showServerStatusDetails();
        }
    };
}

// Initialize admin layout when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.adminLayout = new AdminLayout();
    });
} else {
    window.adminLayout = new AdminLayout();
}

