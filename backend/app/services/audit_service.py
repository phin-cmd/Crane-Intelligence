"""
Audit Logging Service for Admin Actions
"""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, Dict, Any, List
from ..models.admin import AuditLog, AdminUser
import logging

logger = logging.getLogger(__name__)


class AuditService:
    """Service for logging admin actions"""
    
    @staticmethod
    def log_action(
        db: Session,
        admin_user_id: int,
        action: str,
        resource_type: str,
        resource_id: str,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> AuditLog:
        """Log an admin action"""
        try:
            audit_log = AuditLog(
                admin_user_id=admin_user_id,
                action=action,
                resource_type=resource_type,
                resource_id=str(resource_id),
                old_values=old_values,
                new_values=new_values,
                description=description,
                ip_address=ip_address,
                user_agent=user_agent,
                session_id=session_id,
                timestamp=datetime.utcnow()
            )
            db.add(audit_log)
            db.commit()
            db.refresh(audit_log)
            return audit_log
        except Exception as e:
            logger.error(f"Error logging audit action: {e}")
            db.rollback()
            raise
    
    @staticmethod
    def log_create(
        db: Session,
        admin_user_id: int,
        resource_type: str,
        resource_id: str,
        new_values: Dict[str, Any],
        description: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """Log a create action"""
        return AuditService.log_action(
            db=db,
            admin_user_id=admin_user_id,
            action="create",
            resource_type=resource_type,
            resource_id=resource_id,
            new_values=new_values,
            description=description or f"Created {resource_type} {resource_id}",
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_update(
        db: Session,
        admin_user_id: int,
        resource_type: str,
        resource_id: str,
        old_values: Dict[str, Any],
        new_values: Dict[str, Any],
        description: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """Log an update action"""
        return AuditService.log_action(
            db=db,
            admin_user_id=admin_user_id,
            action="update",
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            description=description or f"Updated {resource_type} {resource_id}",
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_delete(
        db: Session,
        admin_user_id: int,
        resource_type: str,
        resource_id: str,
        old_values: Dict[str, Any],
        description: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """Log a delete action"""
        return AuditService.log_action(
            db=db,
            admin_user_id=admin_user_id,
            action="delete",
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values,
            description=description or f"Deleted {resource_type} {resource_id}",
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_view(
        db: Session,
        admin_user_id: int,
        resource_type: str,
        resource_id: str,
        description: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """Log a view action (for sensitive data)"""
        return AuditService.log_action(
            db=db,
            admin_user_id=admin_user_id,
            action="view",
            resource_type=resource_type,
            resource_id=resource_id,
            description=description or f"Viewed {resource_type} {resource_id}",
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_login(
        db: Session,
        admin_user_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> AuditLog:
        """Log a login action"""
        return AuditService.log_action(
            db=db,
            admin_user_id=admin_user_id,
            action="login",
            resource_type="admin_user",
            resource_id=str(admin_user_id),
            description="Admin user logged in",
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id
        )
    
    @staticmethod
    def log_logout(
        db: Session,
        admin_user_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> AuditLog:
        """Log a logout action"""
        return AuditService.log_action(
            db=db,
            admin_user_id=admin_user_id,
            action="logout",
            resource_type="admin_user",
            resource_id=str(admin_user_id),
            description="Admin user logged out",
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id
        )
    
    @staticmethod
    def get_audit_logs(
        db: Session,
        admin_user_id: Optional[int] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """Get audit logs with filters"""
        query = db.query(AuditLog)
        
        if admin_user_id:
            query = query.filter(AuditLog.admin_user_id == admin_user_id)
        if action:
            query = query.filter(AuditLog.action == action)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        if resource_id:
            query = query.filter(AuditLog.resource_id == resource_id)
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
        
        query = query.order_by(AuditLog.timestamp.desc())
        query = query.limit(limit).offset(offset)
        
        return query.all()
    
    @staticmethod
    def get_audit_log_count(
        db: Session,
        admin_user_id: Optional[int] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        """Get count of audit logs with filters"""
        query = db.query(AuditLog)
        
        if admin_user_id:
            query = query.filter(AuditLog.admin_user_id == admin_user_id)
        if action:
            query = query.filter(AuditLog.action == action)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
        
        return query.count()
    
    @staticmethod
    def export_audit_logs(
        db: Session,
        admin_user_id: Optional[int] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Export audit logs as list of dictionaries"""
        logs = AuditService.get_audit_logs(
            db=db,
            admin_user_id=admin_user_id,
            action=action,
            resource_type=resource_type,
            start_date=start_date,
            end_date=end_date,
            limit=10000  # Large limit for export
        )
        
        return [
            {
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "admin_user_id": log.admin_user_id,
                "admin_email": log.admin_user.email if log.admin_user else None,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "description": log.description,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "old_values": log.old_values,
                "new_values": log.new_values
            }
            for log in logs
        ]

