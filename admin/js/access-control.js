// Role-Based Access Control System for Crane Intelligence Admin Portal

// Define user roles and their permissions
const ROLE_PERMISSIONS = {
    'super-admin': {
        name: 'Super Admin',
        level: 5,
        color: '#FF00FF',
        permissions: {
            // Dashboard
            'dashboard.view': true,
            'dashboard.export': true,
            
            // Users Management
            'users.view': true,
            'users.create': true,
            'users.edit': true,
            'users.delete': true,
            'users.suspend': true,
            'users.export': true,
            
            // Admin Users Management
            'admin-users.view': true,
            'admin-users.create': true,
            'admin-users.edit': true,
            'admin-users.delete': true,
            'admin-users.suspend': true,
            'admin-users.export': true,
            'admin-users.manage-roles': true,
            
            // Content Management
            'content.view': true,
            'content.create': true,
            'content.edit': true,
            'content.delete': true,
            'content.publish': true,
            'content.export': true,
            
            // Analytics
            'analytics.view': true,
            'analytics.export': true,
            'analytics.custom-reports': true,
            
            // Settings
            'settings.view': true,
            'settings.edit': true,
            'settings.system-config': true,
            'settings.email-config': true,
            'settings.integrations': true,
            
            // Security
            'security.view': true,
            'security.audit-logs': true,
            'security.user-sessions': true,
            'security.security-settings': true,
            
            // Data Management
            'data.view': true,
            'data.export': true,
            'data.import': true,
            'data.quality-check': true,
            'data.background-jobs': true,
            
            // Database
            'database.view': true,
            'database.backup': true,
            'database.restore': true,
            'database.optimize': true,
            'database.query': true,
            'database.structure': true
        }
    },
    
    'admin': {
        name: 'Admin',
        level: 4,
        color: '#00FF85',
        permissions: {
            // Dashboard
            'dashboard.view': true,
            'dashboard.export': true,
            
            // Users Management
            'users.view': true,
            'users.create': true,
            'users.edit': true,
            'users.delete': false,
            'users.suspend': true,
            'users.export': true,
            
            // Admin Users Management
            'admin-users.view': true,
            'admin-users.create': false,
            'admin-users.edit': true,
            'admin-users.delete': false,
            'admin-users.suspend': true,
            'admin-users.export': true,
            'admin-users.manage-roles': false,
            
            // Content Management
            'content.view': true,
            'content.create': true,
            'content.edit': true,
            'content.delete': true,
            'content.publish': true,
            'content.export': true,
            
            // Analytics
            'analytics.view': true,
            'analytics.export': true,
            'analytics.custom-reports': true,
            
            // Settings
            'settings.view': true,
            'settings.edit': true,
            'settings.system-config': false,
            'settings.email-config': true,
            'settings.integrations': false,
            
            // Security
            'security.view': true,
            'security.audit-logs': true,
            'security.user-sessions': true,
            'security.security-settings': false,
            
            // Data Management
            'data.view': true,
            'data.export': true,
            'data.import': true,
            'data.quality-check': true,
            'data.background-jobs': true,
            
            // Database
            'database.view': true,
            'database.backup': false,
            'database.restore': false,
            'database.optimize': false,
            'database.query': true,
            'database.structure': true
        }
    },
    
    'manager': {
        name: 'Manager',
        level: 3,
        color: '#FFA500',
        permissions: {
            // Dashboard
            'dashboard.view': true,
            'dashboard.export': true,
            
            // Users Management
            'users.view': true,
            'users.create': true,
            'users.edit': true,
            'users.delete': false,
            'users.suspend': true,
            'users.export': true,
            
            // Admin Users Management
            'admin-users.view': true,
            'admin-users.create': false,
            'admin-users.edit': false,
            'admin-users.delete': false,
            'admin-users.suspend': false,
            'admin-users.export': true,
            'admin-users.manage-roles': false,
            
            // Content Management
            'content.view': true,
            'content.create': true,
            'content.edit': true,
            'content.delete': false,
            'content.publish': true,
            'content.export': true,
            
            // Analytics
            'analytics.view': true,
            'analytics.export': true,
            'analytics.custom-reports': false,
            
            // Settings
            'settings.view': true,
            'settings.edit': false,
            'settings.system-config': false,
            'settings.email-config': false,
            'settings.integrations': false,
            
            // Security
            'security.view': true,
            'security.audit-logs': true,
            'security.user-sessions': false,
            'security.security-settings': false,
            
            // Data Management
            'data.view': true,
            'data.export': true,
            'data.import': false,
            'data.quality-check': true,
            'data.background-jobs': false,
            
            // Database
            'database.view': true,
            'database.backup': false,
            'database.restore': false,
            'database.optimize': false,
            'database.query': false,
            'database.structure': false
        }
    },
    
    'sales': {
        name: 'Sales',
        level: 2,
        color: '#007BFF',
        permissions: {
            // Dashboard
            'dashboard.view': true,
            'dashboard.export': false,
            
            // Users Management
            'users.view': true,
            'users.create': true,
            'users.edit': true,
            'users.delete': false,
            'users.suspend': false,
            'users.export': true,
            
            // Admin Users Management
            'admin-users.view': false,
            'admin-users.create': false,
            'admin-users.edit': false,
            'admin-users.delete': false,
            'admin-users.suspend': false,
            'admin-users.export': false,
            'admin-users.manage-roles': false,
            
            // Content Management
            'content.view': true,
            'content.create': false,
            'content.edit': false,
            'content.delete': false,
            'content.publish': false,
            'content.export': false,
            
            // Analytics
            'analytics.view': true,
            'analytics.export': true,
            'analytics.custom-reports': false,
            
            // Settings
            'settings.view': false,
            'settings.edit': false,
            'settings.system-config': false,
            'settings.email-config': false,
            'settings.integrations': false,
            
            // Security
            'security.view': false,
            'security.audit-logs': false,
            'security.user-sessions': false,
            'security.security-settings': false,
            
            // Data Management
            'data.view': true,
            'data.export': true,
            'data.import': false,
            'data.quality-check': false,
            'data.background-jobs': false,
            
            // Database
            'database.view': false,
            'database.backup': false,
            'database.restore': false,
            'database.optimize': false,
            'database.query': false,
            'database.structure': false
        }
    },
    
    'support': {
        name: 'Support',
        level: 1,
        color: '#800080',
        permissions: {
            // Dashboard
            'dashboard.view': true,
            'dashboard.export': false,
            
            // Users Management
            'users.view': true,
            'users.create': false,
            'users.edit': true,
            'users.delete': false,
            'users.suspend': false,
            'users.export': false,
            
            // Admin Users Management
            'admin-users.view': false,
            'admin-users.create': false,
            'admin-users.edit': false,
            'admin-users.delete': false,
            'admin-users.suspend': false,
            'admin-users.export': false,
            'admin-users.manage-roles': false,
            
            // Content Management
            'content.view': true,
            'content.create': false,
            'content.edit': false,
            'content.delete': false,
            'content.publish': false,
            'content.export': false,
            
            // Analytics
            'analytics.view': false,
            'analytics.export': false,
            'analytics.custom-reports': false,
            
            // Settings
            'settings.view': false,
            'settings.edit': false,
            'settings.system-config': false,
            'settings.email-config': false,
            'settings.integrations': false,
            
            // Security
            'security.view': false,
            'security.audit-logs': false,
            'security.user-sessions': false,
            'security.security-settings': false,
            
            // Data Management
            'data.view': false,
            'data.export': false,
            'data.import': false,
            'data.quality-check': false,
            'data.background-jobs': false,
            
            // Database
            'database.view': false,
            'database.backup': false,
            'database.restore': false,
            'database.optimize': false,
            'database.query': false,
            'database.structure': false
        }
    }
};

// Access Control Functions
class AccessControl {
    constructor() {
        this.currentUser = this.getCurrentUser();
        this.currentRole = this.currentUser?.role || 'support';
    }

    // Get current user from localStorage
    getCurrentUser() {
        try {
            const userData = localStorage.getItem('userData');
            return userData ? JSON.parse(userData) : null;
        } catch (error) {
            console.error('Error parsing user data:', error);
            return null;
        }
    }

    // Check if user has specific permission
    hasPermission(permission) {
        const rolePermissions = ROLE_PERMISSIONS[this.currentRole];
        if (!rolePermissions) {
            console.warn(`Unknown role: ${this.currentRole}`);
            return false;
        }
        return rolePermissions.permissions[permission] === true;
    }

    // Check if user has any of the specified permissions
    hasAnyPermission(permissions) {
        return permissions.some(permission => this.hasPermission(permission));
    }

    // Check if user has all of the specified permissions
    hasAllPermissions(permissions) {
        return permissions.every(permission => this.hasPermission(permission));
    }

    // Get user's role level
    getRoleLevel() {
        const rolePermissions = ROLE_PERMISSIONS[this.currentRole];
        return rolePermissions ? rolePermissions.level : 0;
    }

    // Check if user can manage another user
    canManageUser(targetUserRole) {
        const targetRolePermissions = ROLE_PERMISSIONS[targetUserRole];
        if (!targetRolePermissions) return false;
        
        return this.getRoleLevel() > targetRolePermissions.level;
    }

    // Apply access restrictions to UI elements
    applyAccessRestrictions() {
        // Hide navigation items based on permissions
        this.hideNavigationItems();
        
        // Hide action buttons based on permissions
        this.hideActionButtons();
        
        // Disable form elements based on permissions
        this.disableFormElements();
        
        // Show/hide sections based on permissions
        this.toggleSections();
    }

    // Hide navigation items user doesn't have access to
    hideNavigationItems() {
        const navItems = {
            'users': 'users.view',
            'content': 'content.view',
            'analytics': 'analytics.view',
            'settings': 'settings.view',
            'security': 'security.view',
            'data': 'data.view',
            'database': 'database.view',
            'admin-users': 'admin-users.view'
        };

        Object.entries(navItems).forEach(([navId, permission]) => {
            const navElement = document.querySelector(`a[href*="${navId}"]`);
            if (navElement && !this.hasPermission(permission)) {
                navElement.style.display = 'none';
            }
        });
    }

    // Hide action buttons user doesn't have permission for
    hideActionButtons() {
        const actionButtons = {
            '.add-admin-btn': 'admin-users.create',
            '.btn-edit': 'admin-users.edit',
            '.btn-delete': 'admin-users.delete',
            '.btn-suspend': 'admin-users.suspend',
            '.btn-export': 'admin-users.export'
        };

        Object.entries(actionButtons).forEach(([selector, permission]) => {
            const buttons = document.querySelectorAll(selector);
            buttons.forEach(button => {
                if (!this.hasPermission(permission)) {
                    button.style.display = 'none';
                }
            });
        });
    }

    // Disable form elements user can't modify
    disableFormElements() {
        const formElements = {
            'input[type="text"]': 'admin-users.edit',
            'input[type="email"]': 'admin-users.edit',
            'select': 'admin-users.edit',
            'textarea': 'admin-users.edit'
        };

        Object.entries(formElements).forEach(([selector, permission]) => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                if (!this.hasPermission(permission)) {
                    element.disabled = true;
                    element.style.opacity = '0.5';
                }
            });
        });
    }

    // Toggle sections based on permissions
    toggleSections() {
        const sections = {
            '.admin-users-section': 'admin-users.view',
            '.user-management-section': 'users.view',
            '.content-management-section': 'content.view',
            '.analytics-section': 'analytics.view',
            '.settings-section': 'settings.view',
            '.security-section': 'security.view',
            '.data-section': 'data.view',
            '.database-section': 'database.view'
        };

        Object.entries(sections).forEach(([selector, permission]) => {
            const section = document.querySelector(selector);
            if (section && !this.hasPermission(permission)) {
                section.style.display = 'none';
            }
        });
    }

    // Get role display information
    getRoleInfo(role) {
        return ROLE_PERMISSIONS[role] || {
            name: 'Unknown',
            level: 0,
            color: '#666666',
            permissions: {}
        };
    }

    // Check if user can access a specific page
    canAccessPage(pageName) {
        const pagePermissions = {
            'dashboard': 'dashboard.view',
            'users': 'users.view',
            'admin-users': 'admin-users.view',
            'content': 'content.view',
            'analytics': 'analytics.view',
            'settings': 'settings.view',
            'security': 'security.view',
            'data': 'data.view',
            'database': 'database.view'
        };

        const permission = pagePermissions[pageName];
        return permission ? this.hasPermission(permission) : false;
    }

    // Redirect user if they don't have access
    redirectIfNoAccess(pageName) {
        if (!this.canAccessPage(pageName)) {
            alert('You do not have permission to access this page.');
            window.location.href = 'dashboard.html';
        }
    }

    // Get user's accessible pages
    getAccessiblePages() {
        const pages = [
            { name: 'dashboard', permission: 'dashboard.view', url: 'dashboard.html' },
            { name: 'users', permission: 'users.view', url: 'users.html' },
            { name: 'admin-users', permission: 'admin-users.view', url: 'admin-users.html' },
            { name: 'content', permission: 'content.view', url: 'content.html' },
            { name: 'analytics', permission: 'analytics.view', url: 'analytics.html' },
            { name: 'settings', permission: 'settings.view', url: 'settings.html' },
            { name: 'security', permission: 'security.view', url: 'security.html' },
            { name: 'data', permission: 'data.view', url: 'data.html' },
            { name: 'database', permission: 'database.view', url: 'database.html' }
        ];

        return pages.filter(page => this.hasPermission(page.permission));
    }
}

// Initialize access control when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const accessControl = new AccessControl();
    
    // Apply access restrictions
    accessControl.applyAccessRestrictions();
    
    // Make access control available globally
    window.accessControl = accessControl;
    
    // Log current user role for debugging
    console.log('Current user role:', accessControl.currentRole);
    console.log('Accessible pages:', accessControl.getAccessiblePages());
});

// Export for use in other scripts
// Browser environment - no module exports needed
