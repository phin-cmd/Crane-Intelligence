// Common Admin Header Component
function renderAdminHeader(pageTitle = 'Admin Dashboard') {
    const adminUser = JSON.parse(localStorage.getItem('admin_user') || '{}');
    const adminName = adminUser.full_name || adminUser.email || 'Admin User';
    const adminRole = adminUser.role || adminUser.admin_role || 'Administrator';
    
    return `
        <header class="admin-header">
            <div class="header-left">
                <div class="logo">
                    <a href="dashboard.html" style="display: flex; align-items: center; text-decoration: none;">
                        <img src="../images/logos/crane-intelligence-logo.svg" alt="Crane Intelligence" class="logo-img" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                        <div class="logo-text-fallback" style="display: none; flex-direction: column; margin-left: 12px;">
                            <span style="color: #00FF85; font-size: 20px; font-weight: 700;">CRANE</span>
                            <span style="color: #FFFFFF; font-size: 12px;">INTELLIGENCE</span>
                        </div>
                    </a>
                </div>
                <h1 class="page-title">${pageTitle}</h1>
            </div>
            <div class="header-right">
                <!-- Notification Bell -->
                <div class="notification-bell-container">
                    <button class="notification-bell" id="adminNotificationBell" aria-label="Notifications">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                            <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
                        </svg>
                        <span class="notification-badge" id="adminNotificationBadge" style="display: none;">0</span>
                    </button>
                    <!-- Notification Dropdown -->
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
                        <div class="avatar-initials">${adminName.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2)}</div>
                    </div>
                    <div class="profile-info">
                        <div class="profile-name">${adminName}</div>
                        <div class="profile-role">${adminRole}</div>
                    </div>
                    <div class="profile-dropdown-btn">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="6,9 12,15 18,9"></polyline>
                        </svg>
                    </div>
                    <!-- Profile Dropdown Menu -->
                    <div class="profile-dropdown" id="profileDropdown">
                        <a href="profile.html" class="dropdown-item">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                                <circle cx="12" cy="7" r="4"></circle>
                            </svg>
                            My Profile
                        </a>
                        <a href="security-2fa.html" class="dropdown-item">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                            </svg>
                            Security Settings
                        </a>
                        <a href="sessions.html" class="dropdown-item">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                                <circle cx="12" cy="7" r="4"></circle>
                            </svg>
                            Active Sessions
                        </a>
                        <button class="dropdown-item logout" onclick="adminLogout()">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                                <polyline points="16,17 21,12 16,7"></polyline>
                                <line x1="21" y1="12" x2="9" y2="12"></line>
                            </svg>
                            Logout
                        </button>
                    </div>
                </div>
            </div>
        </header>
    `;
}

function renderAdminSidebar(currentPage = '') {
    const menuCategories = [
        {
            title: 'Overview',
            items: [
                { href: 'dashboard.html', icon: 'rect', label: 'Dashboard', key: 'dashboard' }
            ]
        },
        {
            title: 'User Management',
            items: [
                { href: 'users.html', icon: 'users', label: 'Users', key: 'users' },
                { href: 'admin-users.html', icon: 'user-plus', label: 'Admin Users', key: 'admin-users' },
                { href: 'bulk-operations.html', icon: 'users', label: 'Bulk Operations', key: 'bulk-operations' }
            ]
        },
        {
            title: 'Data Management',
            items: [
                { href: 'cranes.html', icon: 'crane', label: 'Cranes', key: 'cranes' },
                { href: 'valuations.html', icon: 'chart', label: 'Valuations', key: 'valuations' },
                { href: 'fmv-reports.html', icon: 'file', label: 'FMV Reports', key: 'fmv-reports' }
            ]
        },
        {
            title: 'Financial',
            items: [
                { href: 'payments.html', icon: 'card', label: 'Payments', key: 'payments' },
                { href: 'payment-reconciliation.html', icon: 'card', label: 'Payment Reconciliation', key: 'payment-reconciliation' },
                { href: 'refunds.html', icon: 'card', label: 'Refunds', key: 'refunds' },
                { href: 'subscriptions.html', icon: 'package', label: 'Subscriptions', key: 'subscriptions' }
            ]
        },
        {
            title: 'Security & Access',
            items: [
                { href: 'security-2fa.html', icon: 'shield', label: 'Security & 2FA', key: 'security-2fa' },
                { href: 'sessions.html', icon: 'users', label: 'Sessions', key: 'sessions' },
                { href: 'audit-logs.html', icon: 'file', label: 'Audit Logs', key: 'audit-logs' },
                { href: 'roles.html', icon: 'shield', label: 'Role Settings', key: 'roles' }
            ]
        },
        {
            title: 'System',
            items: [
                { href: 'algorithm.html', icon: 'settings', label: 'Algorithm', key: 'algorithm' },
                { href: 'system-health.html', icon: 'settings', label: 'System Health', key: 'system-health' },
                { href: 'email-management.html', icon: 'file', label: 'Email Management', key: 'email-management' },
                { href: 'gdpr-compliance.html', icon: 'shield', label: 'GDPR Compliance', key: 'gdpr-compliance' }
            ]
        }
    ];

    const icons = {
        rect: '<rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect>',
        users: '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle>',
        crane: '<path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>',
        chart: '<path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>',
        file: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14,2 14,8 20,8"></polyline>',
        card: '<line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>',
        package: '<rect x="3" y="8" width="18" height="4" rx="1"></rect><path d="M12 8v13"></path><path d="M19 12v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-7"></path><path d="M7.5 8a2.5 2.5 0 0 1 0-5A4.8 8 0 0 1 12 8a4.8 8 0 0 1 4.5-5 2.5 2.5 0 0 1 0 5"></path>',
        shield: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>',
        settings: '<circle cx="12" cy="12" r="3"></circle><path d="M12 1v6m0 6v6m11-7h-6m-6 0H1"></path>',
        'user-plus': '<path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="8.5" cy="7" r="4"></circle><line x1="20" y1="8" x2="20" y2="14"></line><line x1="23" y1="11" x2="17" y2="11"></line>'
    };

    return `
        <nav class="admin-sidebar">
            ${menuCategories.map(category => `
                <div class="sidebar-category">
                    <div class="sidebar-category-title">${category.title}</div>
                    <ul class="sidebar-menu">
                        ${category.items.map(item => `
                            <li class="${currentPage === item.key ? 'active' : ''}">
                                <a href="${item.href}">
                                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        ${icons[item.icon]}
                                    </svg>
                                    ${item.label}
                                </a>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            `).join('')}
        </nav>
    `;
}

function renderAdminFooter() {
    return `
        <footer class="admin-footer">
            <div class="footer-content">
                <div class="footer-section">
                    <p>&copy; ${new Date().getFullYear()} Crane Intelligence. All rights reserved.</p>
                </div>
                <div class="footer-section">
                    <a href="/" style="color: #B0B0B0; text-decoration: none; margin-right: 20px;">Main Website</a>
                    <a href="/admin/dashboard.html" style="color: #B0B0B0; text-decoration: none;">Admin Dashboard</a>
                </div>
            </div>
        </footer>
    `;
}

// Initialize header dropdown and notifications
function initAdminHeader() {
    // Profile dropdown
    const profileElement = document.getElementById('adminProfile');
    if (profileElement) {
        profileElement.addEventListener('click', function(e) {
            e.stopPropagation();
            const dropdown = document.getElementById('profileDropdown');
            if (dropdown) {
                dropdown.classList.toggle('show');
            }
        });

        document.addEventListener('click', function(e) {
            const dropdown = document.getElementById('profileDropdown');
            if (dropdown && !profileElement.contains(e.target)) {
                dropdown.classList.remove('show');
            }
        });
    }

    // Notification bell
    setupAdminNotificationBell();
}

// Setup notification bell functionality
function setupAdminNotificationBell() {
    const notificationBell = document.getElementById('adminNotificationBell');
    const notificationDropdown = document.getElementById('adminNotificationDropdown');
    const markAllReadBtn = document.getElementById('adminMarkAllReadBtn');
    
    if (!notificationBell || !notificationDropdown) return;
    
    let isNotificationDropdownOpen = false;
    
    notificationBell.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        if (isNotificationDropdownOpen) {
            notificationDropdown.classList.remove('show');
            isNotificationDropdownOpen = false;
        } else {
            notificationDropdown.classList.add('show');
            isNotificationDropdownOpen = true;
            loadAdminNotifications();
        }
    });
    
    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            markAllAdminNotificationsAsRead();
        });
    }
    
    // Close on outside click
    document.addEventListener('click', function(e) {
        if (notificationDropdown && !notificationBell.contains(e.target) && !notificationDropdown.contains(e.target)) {
            notificationDropdown.classList.remove('show');
            isNotificationDropdownOpen = false;
        }
    });
    
    // Load notifications periodically
    loadAdminNotifications();
    setInterval(loadAdminNotifications, 30000);
}

// Load admin notifications
function loadAdminNotifications() {
    const token = localStorage.getItem('admin_token') || localStorage.getItem('admin_access_token');
    if (!token) return;
    
    const apiBaseUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:8004'
        : 'https://craneintelligence.tech';
    
    fetch(`${apiBaseUrl}/api/v1/notifications/admin/notifications`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (response.status === 404) {
            // Notifications endpoint doesn't exist yet - this is okay
            console.log('Notifications API endpoint not available yet');
            return null;
        }
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data && data.success && data.data) {
            updateAdminNotificationUI(data.data);
        }
    })
    .catch(error => {
        // Silently handle errors - notifications are not critical
        if (error.message && !error.message.includes('404')) {
            console.error('Error loading admin notifications:', error);
        }
    });
}

// Update notification UI
function updateAdminNotificationUI(notifications) {
    const notificationList = document.getElementById('adminNotificationList');
    const notificationBadge = document.getElementById('adminNotificationBadge');
    
    if (!notificationList) return;
    
    const unreadCount = notifications.filter(n => !n.read).length;
    
    if (notificationBadge) {
        if (unreadCount > 0) {
            notificationBadge.textContent = unreadCount > 99 ? '99+' : unreadCount;
            notificationBadge.style.display = 'block';
        } else {
            notificationBadge.style.display = 'none';
        }
    }
    
    if (notifications.length === 0) {
        notificationList.innerHTML = '<div class="notification-empty">No notifications</div>';
        return;
    }
    
    notificationList.innerHTML = notifications.slice(0, 10).map(notification => {
        const timeAgo = formatTimeAgo(notification.created_at);
        const icon = getNotificationIcon(notification.type);
        const unreadClass = notification.read ? '' : 'unread';
        
        return `
            <div class="notification-item ${unreadClass}" data-id="${notification.id}">
                <div class="notification-icon">${icon}</div>
                <div class="notification-content">
                    <div class="notification-title">${escapeHtml(notification.title)}</div>
                    <div class="notification-message">${escapeHtml(notification.message)}</div>
                    <div class="notification-time">${timeAgo}</div>
                </div>
            </div>
        `;
    }).join('');
    
    notificationList.querySelectorAll('.notification-item').forEach(item => {
        item.addEventListener('click', function() {
            const notificationId = this.dataset.id;
            markAdminNotificationAsRead(notificationId);
        });
    });
}

// Mark notification as read
function markAdminNotificationAsRead(notificationId) {
    const token = localStorage.getItem('admin_token') || localStorage.getItem('admin_access_token');
    if (!token) return;
    
    const apiBaseUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:8004'
        : 'https://craneintelligence.tech';
    
    fetch(`${apiBaseUrl}/api/v1/notifications/admin/notifications/${notificationId}/read`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(() => {
        loadAdminNotifications();
    })
    .catch(error => {
        console.error('Error marking notification as read:', error);
    });
}

// Mark all notifications as read
function markAllAdminNotificationsAsRead() {
    const token = localStorage.getItem('admin_token') || localStorage.getItem('admin_access_token');
    if (!token) return;
    
    const apiBaseUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:8004'
        : 'https://craneintelligence.tech';
    
    fetch(`${apiBaseUrl}/api/v1/notifications/admin/notifications/read-all`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(() => {
        loadAdminNotifications();
    })
    .catch(error => {
        console.error('Error marking all notifications as read:', error);
    });
}

// Helper functions
function formatTimeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
}

function getNotificationIcon(type) {
    const icons = {
        'info': 'ℹ️',
        'warning': '⚠️',
        'error': '❌',
        'success': '✅',
        'default': '🔔'
    };
    return icons[type] || icons['default'];
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Logout function
function adminLogout() {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_access_token');
    localStorage.removeItem('admin_refresh_token');
    localStorage.removeItem('admin_user');
    window.location.href = '/admin/login.html';
}

