"""
Initialize default admin users
Creates super admin and other default admin users if they don't exist
"""
from sqlalchemy.orm import Session
from ..models.admin import AdminUser, AdminRole
from ..services.auth_service import auth_service
import logging

logger = logging.getLogger(__name__)


def init_default_admin_users(db: Session):
    """Initialize default admin users"""
    try:
        # Check if any admin users exist
        existing_count = db.query(AdminUser).count()
        if existing_count > 0:
            logger.info(f"Admin users already exist ({existing_count} users)")
            return
        
        # Create Super Admin
        super_admin = AdminUser(
            email="superadmin@craneintelligence.com",
            username="superadmin",
            hashed_password=auth_service.get_password_hash("SuperAdmin123!"),
            full_name="Super Administrator",
            admin_role=AdminRole.SUPER_ADMIN.value,
            is_active=True,
            is_verified=True,
            permissions=None  # Uses role-based permissions
        )
        db.add(super_admin)
        
        # Create Admin
        admin = AdminUser(
            email="admin@craneintelligence.com",
            username="admin",
            hashed_password=auth_service.get_password_hash("Admin123!"),
            full_name="Administrator",
            admin_role=AdminRole.ADMIN.value,
            is_active=True,
            is_verified=True,
            permissions=None
        )
        db.add(admin)
        
        # Create Manager
        manager = AdminUser(
            email="manager@craneintelligence.com",
            username="manager",
            hashed_password=auth_service.get_password_hash("Manager123!"),
            full_name="Manager",
            admin_role=AdminRole.MANAGER.value,
            is_active=True,
            is_verified=True,
            permissions=None
        )
        db.add(manager)
        
        # Create Support
        support = AdminUser(
            email="support@craneintelligence.com",
            username="support",
            hashed_password=auth_service.get_password_hash("Support123!"),
            full_name="Support Staff",
            admin_role=AdminRole.SUPPORT.value,
            is_active=True,
            is_verified=True,
            permissions=None
        )
        db.add(support)
        
        # Create Impersonator
        impersonator = AdminUser(
            email="impersonator@craneintelligence.com",
            username="impersonator",
            hashed_password=auth_service.get_password_hash("Impersonator123!"),
            full_name="Impersonator",
            admin_role=AdminRole.IMPERSONATOR.value,
            is_active=True,
            is_verified=True,
            permissions=None
        )
        db.add(impersonator)
        
        db.commit()
        logger.info("Default admin users created successfully")
        logger.info("Super Admin: superadmin@craneintelligence.com / SuperAdmin123!")
        logger.info("Admin: admin@craneintelligence.com / Admin123!")
        logger.info("Manager: manager@craneintelligence.com / Manager123!")
        logger.info("Support: support@craneintelligence.com / Support123!")
        logger.info("Impersonator: impersonator@craneintelligence.com / Impersonator123!")
        
    except Exception as e:
        logger.error(f"Error initializing admin users: {e}")
        db.rollback()
        raise

