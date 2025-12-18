"""
Bulk Operations API for Admin Panel
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import csv
import io

from ...core.database import get_db
from ...models.admin import AdminUser
from ...models.user import User
from ...core.admin_auth import require_admin_or_super_admin
from ...services.audit_service import AuditService

router = APIRouter(prefix="/admin/bulk", tags=["admin-bulk-operations"])


class BulkOperationRequest(BaseModel):
    """Bulk operation request"""
    user_ids: List[int]
    action: str  # activate, deactivate, delete, export


class BulkOperationResponse(BaseModel):
    """Bulk operation response"""
    success: bool
    message: str
    processed: int
    failed: int
    errors: List[str] = []


@router.post("/users/activate", response_model=BulkOperationResponse)
async def bulk_activate_users(
    request: BulkOperationRequest,
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """Bulk activate users"""
    processed = 0
    failed = 0
    errors = []
    
    for user_id in request.user_ids:
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.is_active = True
                processed += 1
                
                # Log audit action
                AuditService.log_update(
                    db=db,
                    admin_user_id=current_user.id,
                    resource_type="user",
                    resource_id=str(user_id),
                    old_values={"is_active": False},
                    new_values={"is_active": True},
                    description=f"Bulk activated user: {user.email}"
                )
            else:
                failed += 1
                errors.append(f"User {user_id} not found")
        except Exception as e:
            failed += 1
            errors.append(f"Error processing user {user_id}: {str(e)}")
    
    db.commit()
    
    return BulkOperationResponse(
        success=processed > 0,
        message=f"Activated {processed} user(s)",
        processed=processed,
        failed=failed,
        errors=errors
    )


@router.post("/users/deactivate", response_model=BulkOperationResponse)
async def bulk_deactivate_users(
    request: BulkOperationRequest,
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """Bulk deactivate users"""
    processed = 0
    failed = 0
    errors = []
    
    for user_id in request.user_ids:
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.is_active = False
                processed += 1
                
                # Log audit action
                AuditService.log_update(
                    db=db,
                    admin_user_id=current_user.id,
                    resource_type="user",
                    resource_id=str(user_id),
                    old_values={"is_active": True},
                    new_values={"is_active": False},
                    description=f"Bulk deactivated user: {user.email}"
                )
            else:
                failed += 1
                errors.append(f"User {user_id} not found")
        except Exception as e:
            failed += 1
            errors.append(f"Error processing user {user_id}: {str(e)}")
    
    db.commit()
    
    return BulkOperationResponse(
        success=processed > 0,
        message=f"Deactivated {processed} user(s)",
        processed=processed,
        failed=failed,
        errors=errors
    )


@router.post("/users/export")
async def export_users_csv(
    user_ids: Optional[List[int]] = None,
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """Export users to CSV"""
    from fastapi.responses import Response
    
    query = db.query(User)
    if user_ids:
        query = query.filter(User.id.in_(user_ids))
    
    users = query.all()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        "id", "email", "username", "full_name", "company_name", "user_role",
        "subscription_tier", "is_active", "is_verified", "created_at"
    ])
    writer.writeheader()
    
    for user in users:
        writer.writerow({
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "company_name": user.company_name,
            "user_role": user.user_role.value if hasattr(user.user_role, 'value') else str(user.user_role),
            "subscription_tier": user.subscription_tier.value if hasattr(user.subscription_tier, 'value') else str(user.subscription_tier),
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at.isoformat()
        })
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users_export.csv"}
    )


@router.post("/users/import")
async def import_users_csv(
    file: UploadFile = File(...),
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """Import users from CSV"""
    from ...services.auth_service import auth_service
    
    content = await file.read()
    csv_content = content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(csv_content))
    
    processed = 0
    failed = 0
    errors = []
    
    for row in reader:
        try:
            # Check if user exists
            existing = db.query(User).filter(User.email == row['email']).first()
            if existing:
                errors.append(f"User {row['email']} already exists")
                failed += 1
                continue
            
            # Create user
            user = User(
                email=row['email'],
                username=row.get('username', row['email'].split('@')[0]),
                hashed_password=auth_service.get_password_hash(row.get('password', 'TempPassword123!')),
                full_name=row['full_name'],
                company_name=row.get('company_name', ''),
                user_role=row.get('user_role', 'others'),
                subscription_tier=row.get('subscription_tier', 'free'),
                is_active=row.get('is_active', 'true').lower() == 'true',
                is_verified=row.get('is_verified', 'false').lower() == 'true'
            )
            
            db.add(user)
            processed += 1
            
            # Log audit action
            AuditService.log_create(
                db=db,
                admin_user_id=current_user.id,
                resource_type="user",
                resource_id=str(user.id),
                new_values={"email": user.email, "full_name": user.full_name},
                description=f"Bulk imported user: {user.email}"
            )
        except Exception as e:
            failed += 1
            errors.append(f"Error importing user {row.get('email', 'unknown')}: {str(e)}")
    
    db.commit()
    
    return BulkOperationResponse(
        success=processed > 0,
        message=f"Imported {processed} user(s), {failed} failed",
        processed=processed,
        failed=failed,
        errors=errors[:10]  # Limit errors returned
    )

