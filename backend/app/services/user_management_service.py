"""
User Management Service
Business logic for user management operations
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import hashlib
import secrets

from ..models.user import User, UserRole
from ..schemas.user_management import (
    UserCreate, UserUpdate, AdminUserCreate, AdminUserUpdate,
    UserListResponse, UserUsageResponse, UserStatsResponse
)
from ..core.auth import get_password_hash, verify_password

logger = logging.getLogger(__name__)


class UserManagementService:
    """Service class for user management operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def get_users(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> UserListResponse:
        """Get users with filtering and pagination"""
        try:
            query = db.query(User)
            
            # Apply filters
            if search:
                search_filter = or_(
                    User.full_name.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%"),
                    User.username.ilike(f"%{search}%"),
                    User.company_name.ilike(f"%{search}%")
                )
                query = query.filter(search_filter)
            
            if role:
                query = query.filter(User.user_role == role)
            
            if is_active is not None:
                query = query.filter(User.is_active == is_active)
            
            # Get total count
            total = query.count()
            
            # Apply pagination and ordering
            users = query.order_by(desc(User.created_at)).offset(skip).limit(limit).all()
            
            # Calculate pagination info
            total_pages = (total + limit - 1) // limit
            current_page = (skip // limit) + 1
            
            return UserListResponse(
                users=users,
                total=total,
                page=current_page,
                per_page=limit,
                total_pages=total_pages
            )
        except Exception as e:
            self.logger.error(f"Error fetching users: {e}")
            raise
    
    async def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            return db.query(User).filter(User.id == user_id).first()
        except Exception as e:
            self.logger.error(f"Error fetching user {user_id}: {e}")
            raise
    
    async def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            return db.query(User).filter(User.email == email).first()
        except Exception as e:
            self.logger.error(f"Error fetching user by email {email}: {e}")
            raise
    
    async def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            return db.query(User).filter(User.username == username).first()
        except Exception as e:
            self.logger.error(f"Error fetching user by username {username}: {e}")
            raise
    
    async def create_user(self, db: Session, user_data: AdminUserCreate) -> User:
        """Create a new user"""
        try:
            # Hash the password
            hashed_password = get_password_hash(user_data.password)
            
            # Create user object
            db_user = User(
                email=user_data.email,
                username=user_data.username,
                hashed_password=hashed_password,
                full_name=user_data.full_name,
                company_name=user_data.company_name,
                user_role=user_data.user_role,
                is_active=user_data.is_active,
                is_verified=user_data.is_verified
            )
            
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            self.logger.info(f"Created user: {db_user.email}")
            return db_user
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error creating user: {e}")
            raise
    
    async def update_user(
        self,
        db: Session,
        user_id: int,
        user_data: AdminUserUpdate
    ) -> Optional[User]:
        """Update an existing user"""
        try:
            db_user = await self.get_user_by_id(db=db, user_id=user_id)
            if not db_user:
                return None
            
            # Update fields
            update_data = user_data.dict(exclude_unset=True)
            
            # Hash password if provided
            if 'password' in update_data:
                update_data['hashed_password'] = get_password_hash(update_data.pop('password'))
            
            # Handle phone and address - store in notification_preferences JSON
            import json
            phone = update_data.pop('phone', None)
            address = update_data.pop('address', None)
            
            if phone is not None or address is not None:
                # Load existing preferences or create new dict
                prefs = {}
                if db_user.notification_preferences:
                    try:
                        prefs = json.loads(db_user.notification_preferences)
                    except:
                        prefs = {}
                
                # Update phone and address in preferences
                if phone is not None:
                    prefs['phone'] = phone
                    prefs['phone_number'] = phone
                if address is not None:
                    prefs['address'] = address
                    prefs['street_address'] = address
                    prefs['full_address'] = address
                
                # Save back to notification_preferences
                db_user.notification_preferences = json.dumps(prefs)
            
            # Update standard fields
            for field, value in update_data.items():
                if hasattr(db_user, field):
                    setattr(db_user, field, value)
            
            db_user.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(db_user)
            
            self.logger.info(f"Updated user: {db_user.email}")
            return db_user
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error updating user {user_id}: {e}")
            raise
    
    async def delete_user(self, db: Session, user_id: int) -> bool:
        """Delete a user (soft delete)"""
        try:
            db_user = await self.get_user_by_id(db=db, user_id=user_id)
            if not db_user:
                return False
            
            # Soft delete by setting is_active to False
            db_user.is_active = False
            db_user.updated_at = datetime.utcnow()
            
            db.commit()
            
            self.logger.info(f"Deleted user: {db_user.email}")
            return True
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error deleting user {user_id}: {e}")
            raise
    
    async def activate_user(self, db: Session, user_id: int) -> Optional[User]:
        """Activate a user account"""
        try:
            db_user = await self.get_user_by_id(db=db, user_id=user_id)
            if not db_user:
                return None
            
            db_user.is_active = True
            db_user.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(db_user)
            
            self.logger.info(f"Activated user: {db_user.email}")
            return db_user
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error activating user {user_id}: {e}")
            raise
    
    async def deactivate_user(self, db: Session, user_id: int) -> Optional[User]:
        """Deactivate a user account"""
        try:
            db_user = await self.get_user_by_id(db=db, user_id=user_id)
            if not db_user:
                return None
            
            db_user.is_active = False
            db_user.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(db_user)
            
            self.logger.info(f"Deactivated user: {db_user.email}")
            return db_user
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error deactivating user {user_id}: {e}")
            raise
    
    async def reset_password(self, db: Session, user_id: int, new_password: str) -> Optional[User]:
        """Reset a user's password"""
        try:
            db_user = await self.get_user_by_id(db=db, user_id=user_id)
            if not db_user:
                return None
            
            db_user.hashed_password = get_password_hash(new_password)
            db_user.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(db_user)
            
            self.logger.info(f"Reset password for user: {db_user.email}")
            return db_user
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error resetting password for user {user_id}: {e}")
            raise
    
    async def change_password(
        self,
        db: Session,
        user_id: int,
        current_password: str,
        new_password: str
    ) -> bool:
        """Change a user's password"""
        try:
            db_user = await self.get_user_by_id(db=db, user_id=user_id)
            if not db_user:
                return False
            
            # Verify current password
            if not verify_password(current_password, db_user.hashed_password):
                return False
            
            # Update password
            db_user.hashed_password = get_password_hash(new_password)
            db_user.updated_at = datetime.utcnow()
            
            db.commit()
            
            self.logger.info(f"Changed password for user: {db_user.email}")
            return True
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error changing password for user {user_id}: {e}")
            raise
    
    async def get_user_usage(self, db: Session, user_id: int) -> Optional[UserUsageResponse]:
        """Get user usage statistics"""
        try:
            db_user = await self.get_user_by_id(db=db, user_id=user_id)
            if not db_user:
                return None
            
            # Define subscription limits
            subscription_limits = {
                SubscriptionTier.BASIC: {
                    "valuations": 100,
                    "api_calls": 1000
                },
                SubscriptionTier.PRO: {
                    "valuations": 500,
                    "api_calls": 10000
                },
            }
            
            limits = subscription_limits.get(db_user.subscription_tier, subscription_limits[SubscriptionTier.BASIC])
            
            # Calculate usage percentage
            usage_percentage = {}
            if limits["valuations"] > 0:
                usage_percentage["valuations"] = (db_user.monthly_valuations_used / limits["valuations"]) * 100
            else:
                usage_percentage["valuations"] = 0
            
            if limits["api_calls"] > 0:
                usage_percentage["api_calls"] = (db_user.monthly_api_calls_used / limits["api_calls"]) * 100
            else:
                usage_percentage["api_calls"] = 0
            
            return UserUsageResponse(
                user_id=db_user.id,
                monthly_valuations_used=db_user.monthly_valuations_used,
                monthly_api_calls_used=db_user.monthly_api_calls_used,
                subscription_tier=db_user.subscription_tier,
                subscription_limits=limits,
                usage_percentage=usage_percentage,
                last_activity=db_user.updated_at
            )
        except Exception as e:
            self.logger.error(f"Error fetching usage for user {user_id}: {e}")
            raise
    
    async def get_user_stats(self, db: Session) -> UserStatsResponse:
        """Get user statistics"""
        try:
            # Total users
            total_users = db.query(User).count()
            
            # Active users
            active_users = db.query(User).filter(User.is_active == True).count()
            
            # Verified users
            verified_users = db.query(User).filter(User.is_verified == True).count()
            
            # Users by role
            users_by_role = {}
            for role in UserRole:
                count = db.query(User).filter(User.user_role == role).count()
                users_by_role[role.value] = count
            
            # Users by subscription - removed (subscription logic removed)
            users_by_subscription = {}
            
            # New users this month
            month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            new_users_this_month = db.query(User).filter(User.created_at >= month_start).count()
            
            # New users this week
            week_start = datetime.utcnow() - timedelta(days=7)
            new_users_this_week = db.query(User).filter(User.created_at >= week_start).count()
            
            return UserStatsResponse(
                total_users=total_users,
                active_users=active_users,
                verified_users=verified_users,
                users_by_role=users_by_role,
                users_by_subscription=users_by_subscription,
                new_users_this_month=new_users_this_month,
                new_users_this_week=new_users_this_week
            )
        except Exception as e:
            self.logger.error(f"Error fetching user stats: {e}")
            raise


# Create service instance
user_management_service = UserManagementService()
