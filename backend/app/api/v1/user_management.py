"""
User Management API for Admin Panel
Provides full CRUD operations for user management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from ...core.database import get_db
from ...models.user import User, UserRole, SubscriptionTier
from ...schemas.user_management import (
    UserCreate, UserUpdate, UserResponse, UserListResponse,
    AdminUserCreate, AdminUserUpdate
)
from ...services.user_management_service import user_management_service
from ...services.account_email_service import AccountEmailService
from ...core.auth import get_current_admin_user

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize account email service
account_email_service = AccountEmailService()


@router.get("/admin/users", response_model=UserListResponse)
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get all users with filtering and pagination"""
    try:
        users = await user_management_service.get_users(
            db=db,
            skip=skip,
            limit=limit,
            search=search,
            role=role,
            is_active=is_active
        )
        return users
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch users"
        )


@router.get("/admin/users/{user_id}")  # Removed response_model to allow phone/address in response
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get a specific user by ID - user_management.py endpoint"""
    logger.info(f"user_management.py get_user called for user_id={user_id}")
    try:
        user = await user_management_service.get_user_by_id(db=db, user_id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Try to get additional profile data if stored in notification_preferences JSON
        import json
        phone = None
        address = None
        company_name = user.company_name
        
        if user.notification_preferences:
            try:
                prefs = json.loads(user.notification_preferences)
                phone = prefs.get('phone') or prefs.get('phone_number')
                address = prefs.get('address') or prefs.get('street_address') or prefs.get('full_address')
                # Also check for company_name in preferences if it's "N/A" in the main field
                if (not company_name or company_name == "N/A") and prefs.get('company_name'):
                    company_name = prefs.get('company_name')
                logger.info(f"Extracted from preferences: phone={phone}, address={address}")
            except Exception as e:
                logger.error(f"Error parsing notification_preferences: {e}")
                pass
        
        # Ensure company_name is not None (UserResponse requires it to be a string)
        if not company_name or company_name == "N/A" or company_name is None:
            company_name = "N/A"  # Use "N/A" string instead of None
        
        # Create response with all available data
        # Return as dict to ensure phone/address are included (UserResponse schema might filter them)
        from fastapi.responses import JSONResponse
        
        response_dict = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "company_name": company_name,  # Always a string, never None
            "user_role": user.user_role.value if hasattr(user.user_role, 'value') else str(user.user_role),
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "total_payments": float(user.total_payments) if user.total_payments else 0.0,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "timezone": user.timezone,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "phone": phone,  # Include phone from notification_preferences
            "phone_number": phone,
            "address": address,  # Include address from notification_preferences
            "street_address": address,
            "full_address": address
        }
        
        logger.info(f"user_management.py: Returning user {user_id} with phone={phone}, address={address}, response_dict keys: {list(response_dict.keys())}")
        print(f"=== user_management.py RETURNING with phone={phone}, address={address} ===", flush=True)
        # Use JSONResponse to ensure our dict is returned
        from fastapi.responses import JSONResponse
        return JSONResponse(content=response_dict)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user"
        )


@router.post("/admin/users", response_model=UserResponse)
async def create_user(
    user_data: AdminUserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new user"""
    try:
        # Check if email already exists
        existing_user = await user_management_service.get_user_by_email(db=db, email=user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username already exists
        existing_username = await user_management_service.get_user_by_username(db=db, username=user_data.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        user = await user_management_service.create_user(db=db, user_data=user_data)
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.put("/admin/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: AdminUserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update an existing user"""
    try:
        # Check if user exists
        existing_user = await user_management_service.get_user_by_id(db=db, user_id=user_id)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if email is being changed and if it already exists
        if user_data.email and user_data.email != existing_user.email:
            email_exists = await user_management_service.get_user_by_email(db=db, email=user_data.email)
            if email_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Check if username is being changed and if it already exists
        if user_data.username and user_data.username != existing_user.username:
            username_exists = await user_management_service.get_user_by_username(db=db, username=user_data.username)
            if username_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        old_email = existing_user.email
        old_tier = existing_user.subscription_tier.value if existing_user.subscription_tier else None
        
        user = await user_management_service.update_user(db=db, user_id=user_id, user_data=user_data)
        db.refresh(user)
        
        # Send email notifications for changes
        try:
            # Email change notification
            if user_data.email and user_data.email != old_email:
                import secrets
                verification_token = secrets.token_urlsafe(32)
                account_email_service.send_email_change_request_notification(
                    user_email=old_email,
                    user_name=user.full_name,
                    new_email=user_data.email,
                    verification_token=verification_token
                )
            
            # Subscription change notification
            if user.subscription_tier and user.subscription_tier.value != old_tier:
                account_email_service.send_subscription_changed_notification(
                    user_email=user.email,
                    user_name=user.full_name,
                    subscription_data={
                        "old_tier": old_tier,
                        "new_tier": user.subscription_tier.value
                    }
                )
        except Exception as e:
            logger.error(f"Error sending account update notifications: {e}")
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


@router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete a user (soft delete)"""
    try:
        # Check if user exists
        existing_user = await user_management_service.get_user_by_id(db=db, user_id=user_id)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent admin from deleting themselves
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        # Send account deletion notification before deletion
        try:
            account_email_service.send_account_deleted_notification(
                user_email=existing_user.email,
                user_name=existing_user.full_name
            )
        except Exception as e:
            logger.error(f"Error sending account deletion notification: {e}")
        
        await user_management_service.delete_user(db=db, user_id=user_id)
        return {"message": "User deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )


@router.patch("/admin/users/{user_id}/activate")
async def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Activate a user account"""
    try:
        user = await user_management_service.activate_user(db=db, user_id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return {"message": "User activated successfully", "user": user}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to activate user"
        )


@router.patch("/admin/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Deactivate a user account"""
    try:
        # Prevent admin from deactivating themselves
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate your own account"
            )
        
        user = await user_management_service.deactivate_user(db=db, user_id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return {"message": "User deactivated successfully", "user": user}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate user"
        )


@router.patch("/admin/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    new_password: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Reset a user's password"""
    try:
        user = await user_management_service.reset_password(db=db, user_id=user_id, new_password=new_password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return {"message": "Password reset successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting password for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        )


@router.get("/admin/users/{user_id}/usage")
async def get_user_usage(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get user usage statistics"""
    try:
        usage = await user_management_service.get_user_usage(db=db, user_id=user_id)
        if not usage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return usage
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching usage for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user usage"
        )


# Webapp User Management (for regular users to manage their own profile)
@router.get("/users/profile", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_admin_user)
):
    """Get current user's profile"""
    # Extract phone and address from notification_preferences
    import json
    phone = None
    address = None
    company_name = current_user.company_name
    
    if current_user.notification_preferences:
        try:
            prefs = json.loads(current_user.notification_preferences)
            phone = prefs.get('phone') or prefs.get('phone_number')
            address = prefs.get('address') or prefs.get('street_address') or prefs.get('full_address')
            if (not company_name or company_name == "N/A") and prefs.get('company_name'):
                company_name = prefs.get('company_name')
        except:
            pass
    
    # Return user with phone and address
    user_dict = {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "company_name": company_name if company_name and company_name != "N/A" else None,
        "user_role": current_user.user_role,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "total_payments": current_user.total_payments,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
        "timezone": current_user.timezone,
        "last_login": current_user.last_login,
        "phone": phone,
        "phone_number": phone,
        "address": address,
        "street_address": address,
        "full_address": address
    }
    return user_dict


@router.put("/users/profile", response_model=UserResponse)
async def update_current_user_profile(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update current user's profile"""
    try:
        old_email = current_user.email
        old_tier = current_user.subscription_tier.value if current_user.subscription_tier else None
        
        # Check if email is being changed and if it already exists
        if user_data.email and user_data.email != current_user.email:
            email_exists = await user_management_service.get_user_by_email(db=db, email=user_data.email)
            if email_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Check if username is being changed and if it already exists
        if user_data.username and user_data.username != current_user.username:
            username_exists = await user_management_service.get_user_by_username(db=db, username=user_data.username)
            if username_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        user = await user_management_service.update_user(db=db, user_id=current_user.id, user_data=user_data)
        db.refresh(user)
        
        # Send email notifications for changes
        try:
            # Email change notification
            if user_data.email and user_data.email != old_email:
                import secrets
                verification_token = secrets.token_urlsafe(32)
                account_email_service.send_email_change_request_notification(
                    user_email=old_email,
                    user_name=user.full_name,
                    new_email=user_data.email,
                    verification_token=verification_token
                )
            
            # Subscription change notification
            if user.subscription_tier and user.subscription_tier.value != old_tier:
                account_email_service.send_subscription_changed_notification(
                    user_email=user.email,
                    user_name=user.full_name,
                    subscription_data={
                        "old_tier": old_tier,
                        "new_tier": user.subscription_tier.value
                    }
                )
            
            # Profile update notification (optional - only if significant changes)
            changes = {}
            if user_data.full_name and user_data.full_name != current_user.full_name:
                changes["full_name"] = user_data.full_name
            if user_data.company_name and user_data.company_name != current_user.company_name:
                changes["company_name"] = user_data.company_name
            if changes:
                account_email_service.send_profile_updated_notification(
                    user_email=user.email,
                    user_name=user.full_name,
                    changes=changes
                )
        except Exception as e:
            logger.error(f"Error sending account update notifications: {e}")
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.patch("/users/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Change current user's password"""
    try:
        success = await user_management_service.change_password(
            db=db,
            user_id=current_user.id,
            current_password=current_password,
            new_password=new_password
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Send password changed notification
        try:
            account_email_service.send_password_changed_notification(
                user_email=current_user.email,
                user_name=current_user.full_name
            )
        except Exception as e:
            logger.error(f"Error sending password changed notification: {e}")
        
        return {"message": "Password changed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )
