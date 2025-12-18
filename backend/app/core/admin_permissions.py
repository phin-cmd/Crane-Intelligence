"""
Role-based permission system for admin users
Defines what each admin role can and cannot do
"""
from typing import List, Set
from enum import Enum
from ..models.admin import AdminRole


class Permission(str, Enum):
    """Individual permissions that can be assigned"""
    # User Management
    VIEW_USERS = "view_users"
    CREATE_USERS = "create_users"
    EDIT_USERS = "edit_users"
    DELETE_USERS = "delete_users"
    MANAGE_USER_SUBSCRIPTIONS = "manage_user_subscriptions"
    
    # Admin User Management
    VIEW_ADMIN_USERS = "view_admin_users"
    CREATE_ADMIN_USERS = "create_admin_users"
    EDIT_ADMIN_USERS = "edit_admin_users"
    DELETE_ADMIN_USERS = "delete_admin_users"
    
    # Reports
    VIEW_REPORTS = "view_reports"
    CREATE_REPORTS = "create_reports"
    EDIT_REPORTS = "edit_reports"
    DELETE_REPORTS = "delete_reports"
    EXPORT_REPORTS = "export_reports"
    
    # Analytics
    VIEW_ANALYTICS = "view_analytics"
    VIEW_FINANCIAL_DATA = "view_financial_data"
    
    # System Settings
    VIEW_SETTINGS = "view_settings"
    EDIT_SETTINGS = "edit_settings"
    
    # Content Management
    VIEW_CONTENT = "view_content"
    CREATE_CONTENT = "create_content"
    EDIT_CONTENT = "edit_content"
    DELETE_CONTENT = "delete_content"
    PUBLISH_CONTENT = "publish_content"
    
    # Impersonation
    IMPERSONATE_USERS = "impersonate_users"
    
    # Audit & Logs
    VIEW_AUDIT_LOGS = "view_audit_logs"
    VIEW_SYSTEM_LOGS = "view_system_logs"
    
    # Security
    VIEW_SECURITY_EVENTS = "view_security_events"
    MANAGE_SECURITY = "manage_security"


# Role-based permission mappings
ROLE_PERMISSIONS: dict[AdminRole, Set[Permission]] = {
    AdminRole.SUPER_ADMIN: {
        # Super Admin has ALL permissions
        Permission.VIEW_USERS,
        Permission.CREATE_USERS,
        Permission.EDIT_USERS,
        Permission.DELETE_USERS,
        Permission.MANAGE_USER_SUBSCRIPTIONS,
        Permission.VIEW_ADMIN_USERS,
        Permission.CREATE_ADMIN_USERS,
        Permission.EDIT_ADMIN_USERS,
        Permission.DELETE_ADMIN_USERS,
        Permission.VIEW_REPORTS,
        Permission.CREATE_REPORTS,
        Permission.EDIT_REPORTS,
        Permission.DELETE_REPORTS,
        Permission.EXPORT_REPORTS,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_FINANCIAL_DATA,
        Permission.VIEW_SETTINGS,
        Permission.EDIT_SETTINGS,
        Permission.VIEW_CONTENT,
        Permission.CREATE_CONTENT,
        Permission.EDIT_CONTENT,
        Permission.DELETE_CONTENT,
        Permission.PUBLISH_CONTENT,
        Permission.IMPERSONATE_USERS,
        Permission.VIEW_AUDIT_LOGS,
        Permission.VIEW_SYSTEM_LOGS,
        Permission.VIEW_SECURITY_EVENTS,
        Permission.MANAGE_SECURITY,
    },
    
    AdminRole.ADMIN: {
        # Admin: Full access except managing admin users
        Permission.VIEW_USERS,
        Permission.CREATE_USERS,
        Permission.EDIT_USERS,
        Permission.DELETE_USERS,
        Permission.MANAGE_USER_SUBSCRIPTIONS,
        # No admin user management
        Permission.VIEW_REPORTS,
        Permission.CREATE_REPORTS,
        Permission.EDIT_REPORTS,
        Permission.DELETE_REPORTS,
        Permission.EXPORT_REPORTS,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_FINANCIAL_DATA,
        Permission.VIEW_SETTINGS,
        Permission.EDIT_SETTINGS,
        Permission.VIEW_CONTENT,
        Permission.CREATE_CONTENT,
        Permission.EDIT_CONTENT,
        Permission.DELETE_CONTENT,
        Permission.PUBLISH_CONTENT,
        Permission.IMPERSONATE_USERS,
        Permission.VIEW_AUDIT_LOGS,
        Permission.VIEW_SYSTEM_LOGS,
        Permission.VIEW_SECURITY_EVENTS,
        Permission.MANAGE_SECURITY,
    },
    
    AdminRole.MANAGER: {
        # Manager: All pages except delete access
        Permission.VIEW_USERS,
        Permission.CREATE_USERS,
        Permission.EDIT_USERS,
        # No DELETE_USERS
        Permission.MANAGE_USER_SUBSCRIPTIONS,
        Permission.VIEW_REPORTS,
        Permission.CREATE_REPORTS,
        Permission.EDIT_REPORTS,
        # No DELETE_REPORTS
        Permission.EXPORT_REPORTS,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_FINANCIAL_DATA,
        Permission.VIEW_SETTINGS,
        Permission.EDIT_SETTINGS,
        Permission.VIEW_CONTENT,
        Permission.CREATE_CONTENT,
        Permission.EDIT_CONTENT,
        # No DELETE_CONTENT
        Permission.PUBLISH_CONTENT,
        Permission.VIEW_AUDIT_LOGS,
        Permission.VIEW_SYSTEM_LOGS,
        Permission.VIEW_SECURITY_EVENTS,
        # No MANAGE_SECURITY
    },
    
    AdminRole.SUPPORT: {
        # Support: Read only and minimal managing access
        Permission.VIEW_USERS,
        Permission.EDIT_USERS,  # Limited editing (e.g., reset password, activate/deactivate)
        # No CREATE_USERS, DELETE_USERS
        Permission.VIEW_REPORTS,
        # No CREATE_REPORTS, EDIT_REPORTS, DELETE_REPORTS
        Permission.EXPORT_REPORTS,
        Permission.VIEW_ANALYTICS,
        # No VIEW_FINANCIAL_DATA
        Permission.VIEW_SETTINGS,
        # No EDIT_SETTINGS
        Permission.VIEW_CONTENT,
        # No CREATE_CONTENT, EDIT_CONTENT, DELETE_CONTENT, PUBLISH_CONTENT
        Permission.VIEW_AUDIT_LOGS,
        Permission.VIEW_SYSTEM_LOGS,
        Permission.VIEW_SECURITY_EVENTS,
    },
    
    AdminRole.IMPERSONATOR: {
        # Impersonator: Only impersonation access
        Permission.VIEW_USERS,
        Permission.IMPERSONATE_USERS,
        Permission.VIEW_REPORTS,  # Can view reports of impersonated users
    },
}


def get_permissions_for_role(role: AdminRole) -> Set[Permission]:
    """Get all permissions for a given admin role"""
    return ROLE_PERMISSIONS.get(role, set())


def has_permission(role: AdminRole, permission: Permission) -> bool:
    """Check if a role has a specific permission"""
    return permission in ROLE_PERMISSIONS.get(role, set())


def can_delete(role: AdminRole) -> bool:
    """Check if role can delete resources"""
    return role in [AdminRole.SUPER_ADMIN, AdminRole.ADMIN]


def can_manage_admin_users(role: AdminRole) -> bool:
    """Check if role can manage admin users"""
    return role == AdminRole.SUPER_ADMIN


def can_impersonate(role: AdminRole) -> bool:
    """Check if role can impersonate users"""
    return role in [AdminRole.SUPER_ADMIN, AdminRole.ADMIN, AdminRole.IMPERSONATOR]


def can_view_financial_data(role: AdminRole) -> bool:
    """Check if role can view financial data"""
    return role in [AdminRole.SUPER_ADMIN, AdminRole.ADMIN, AdminRole.MANAGER]


def can_edit_settings(role: AdminRole) -> bool:
    """Check if role can edit system settings"""
    return role in [AdminRole.SUPER_ADMIN, AdminRole.ADMIN, AdminRole.MANAGER]

