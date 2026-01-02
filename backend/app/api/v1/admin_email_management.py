"""
Email Template and Management API
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from ...core.database import get_db
from ...models.admin import AdminUser, EmailTemplate
from ...models.subscription import EmailSubscription
from ...core.admin_auth import require_admin_or_super_admin
from ...services.subscription_service import SubscriptionService

router = APIRouter(prefix="/admin/emails", tags=["admin-email-management"])


class EmailTemplateResponse(BaseModel):
    """Email template response"""
    id: int
    name: str
    subject: str
    body_html: str
    body_text: Optional[str]
    template_type: str
    variables: Optional[List[str]]
    is_active: bool
    usage_count: int
    last_used: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class EmailTemplateCreate(BaseModel):
    """Create email template request"""
    name: str
    subject: str
    body_html: str
    body_text: Optional[str] = None
    template_type: str
    variables: Optional[List[str]] = None


class EmailTemplateUpdate(BaseModel):
    """Update email template request"""
    subject: Optional[str] = None
    body_html: Optional[str] = None
    body_text: Optional[str] = None
    template_type: Optional[str] = None
    variables: Optional[List[str]] = None
    is_active: Optional[bool] = None


class EmailLogResponse(BaseModel):
    """Email log response"""
    id: int
    recipient: str
    subject: str
    template_name: Optional[str]
    status: str
    sent_at: datetime
    error_message: Optional[str]


class SubscriberResponse(BaseModel):
    """Subscriber response model"""
    id: int
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    company: Optional[str]
    subscription_type: str
    status: str  # active, unsubscribed, bounced
    source: Optional[str]
    subscribed_at: datetime
    unsubscribed_at: Optional[datetime]
    last_email_sent: Optional[datetime]
    email_count: int
    preferences: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/templates", response_model=List[EmailTemplateResponse])
async def list_email_templates(
    template_type: Optional[str] = Query(None),
    active_only: bool = Query(False),
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """List all email templates"""
    try:
        # Check if EmailTemplate model exists
        try:
            query = db.query(EmailTemplate)
        except Exception as e:
            # If EmailTemplate table doesn't exist, return empty list
            return []
        
        if template_type:
            query = query.filter(EmailTemplate.template_type == template_type)
        if active_only:
            query = query.filter(EmailTemplate.is_active == True)
        
        templates = query.order_by(EmailTemplate.name).all()
        
        result = []
        import json
        for t in templates:
            # Parse variables if it's a string (JSON column might return string)
            variables = t.variables
            
            # Handle different types of variables field
            if variables is None:
                variables = []
            elif isinstance(variables, str):
                # Strip whitespace and check if it's empty
                variables_str = variables.strip()
                if not variables_str or variables_str == '':
                    variables = []
                else:
                    try:
                        # Try to parse as JSON
                        variables = json.loads(variables_str)
                        # Ensure it's a list after parsing
                        if not isinstance(variables, list):
                            variables = []
                    except (json.JSONDecodeError, ValueError, TypeError):
                        # If parsing fails, default to empty list
                        variables = []
            elif not isinstance(variables, list):
                # If it's not a string, None, or list, default to empty list
                variables = []
            
            result.append(
                EmailTemplateResponse(
                    id=t.id,
                    name=t.name,
                    subject=t.subject,
                    body_html=t.body_html,
                    body_text=t.body_text,
                    template_type=t.template_type,
                    variables=variables,
                    is_active=t.is_active,
                    usage_count=t.usage_count or 0,
                    last_used=t.last_used,
                    created_at=t.created_at,
                    updated_at=t.updated_at
                )
            )
        
        return result
    except Exception as e:
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error loading email templates: {str(e)}", exc_info=True)
        # Return empty list if there's any error (table doesn't exist, etc.)
        return []


@router.post("/templates", response_model=EmailTemplateResponse)
async def create_email_template(
    template_data: EmailTemplateCreate,
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """Create a new email template"""
    # Check if template name already exists
    existing = db.query(EmailTemplate).filter(EmailTemplate.name == template_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Template name already exists"
        )
    
    template = EmailTemplate(
        name=template_data.name,
        subject=template_data.subject,
        body_html=template_data.body_html,
        body_text=template_data.body_text,
        template_type=template_data.template_type,
        variables=template_data.variables or []
    )
    
    db.add(template)
    db.commit()
    db.refresh(template)
    
    return EmailTemplateResponse(
        id=template.id,
        name=template.name,
        subject=template.subject,
        body_html=template.body_html,
        body_text=template.body_text,
        template_type=template.template_type,
        variables=template.variables,
        is_active=template.is_active,
        usage_count=template.usage_count,
        last_used=template.last_used,
        created_at=template.created_at,
        updated_at=template.updated_at
    )


@router.put("/templates/{template_id}", response_model=EmailTemplateResponse)
async def update_email_template(
    template_id: int,
    template_data: EmailTemplateUpdate,
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """Update an email template"""
    template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    if template_data.subject is not None:
        template.subject = template_data.subject
    if template_data.body_html is not None:
        template.body_html = template_data.body_html
    if template_data.body_text is not None:
        template.body_text = template_data.body_text
    if template_data.template_type is not None:
        template.template_type = template_data.template_type
    if template_data.variables is not None:
        template.variables = template_data.variables
    if template_data.is_active is not None:
        template.is_active = template_data.is_active
    
    template.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(template)
    
    # Parse variables if it's a string
    variables = template.variables
    if isinstance(variables, str):
        try:
            import json
            variables = json.loads(variables) if variables else []
        except (json.JSONDecodeError, ValueError):
            variables = []
    elif variables is None:
        variables = []
    if not isinstance(variables, list):
        variables = []
    
    return EmailTemplateResponse(
        id=template.id,
        name=template.name,
        subject=template.subject,
        body_html=template.body_html,
        body_text=template.body_text,
        template_type=template.template_type,
        variables=variables,
        is_active=template.is_active,
        usage_count=template.usage_count or 0,
        last_used=template.last_used,
        created_at=template.created_at,
        updated_at=template.updated_at
    )


@router.delete("/templates/{template_id}")
async def delete_email_template(
    template_id: int,
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """Delete an email template"""
    template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    db.delete(template)
    db.commit()
    
    return {"message": "Template deleted successfully"}


@router.get("/logs", response_model=List[EmailLogResponse])
async def get_email_logs(
    recipient: Optional[str] = Query(None),
    template_name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """Get email sending logs"""
    # In a real implementation, you'd have an EmailLog model
    # This is a placeholder structure
    return []


@router.get("/stats/summary")
async def get_email_stats(
    days: int = Query(30, ge=1, le=365),
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """Get email statistics"""
    # Placeholder - in production, aggregate from email logs
    return {
        "total_sent": 0,
        "total_delivered": 0,
        "total_bounced": 0,
        "total_failed": 0,
        "delivery_rate": 0.0,
        "by_template": {}
    }


@router.get("/subscribers", response_model=List[SubscriberResponse])
async def list_subscribers(
    request: Request,
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status: active, unsubscribed, bounced"),
    subscription_type: Optional[str] = Query(None, description="Filter by subscription type: newsletter, blog, updates, etc."),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum number of subscribers to return"),
    offset: int = Query(0, ge=0, description="Number of subscribers to skip"),
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """
    List all email subscribers with their opt-in/opt-out details.
    Available to authenticated admin users.
    """
    
    try:
        subscription_service = SubscriptionService(db)
        
        # Get all subscriptions with optional filtering
        subscriptions = subscription_service.get_all_subscriptions(
            status=status_filter,
            subscription_type=subscription_type,
            limit=limit,
            offset=offset
        )
        
        result = []
        import json
        for sub in subscriptions:
            # Parse preferences if it's a JSON string
            preferences = sub.preferences
            if preferences:
                if isinstance(preferences, str):
                    try:
                        preferences = json.loads(preferences)
                    except (json.JSONDecodeError, ValueError):
                        preferences = {}
                elif not isinstance(preferences, dict):
                    preferences = {}
            else:
                preferences = None
            
            result.append(
                SubscriberResponse(
                    id=sub.id,
                    email=sub.email,
                    first_name=sub.first_name,
                    last_name=sub.last_name,
                    company=sub.company,
                    subscription_type=sub.subscription_type,
                    status=sub.status,
                    source=sub.source,
                    subscribed_at=sub.subscribed_at,
                    unsubscribed_at=sub.unsubscribed_at,
                    last_email_sent=sub.last_email_sent,
                    email_count=sub.email_count or 0,
                    preferences=preferences,
                    created_at=sub.created_at,
                    updated_at=sub.updated_at
                )
            )
        
        return result
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error loading subscribers: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load subscribers: {str(e)}"
        )


@router.get("/subscribers/{subscriber_id}", response_model=SubscriberResponse)
async def get_subscriber(
    subscriber_id: int,
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """
    Get a single subscriber by ID.
    """
    try:
        subscription = db.query(EmailSubscription).filter(
            EmailSubscription.id == subscriber_id
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscriber not found"
            )
        
        import json
        preferences = subscription.preferences
        if preferences:
            if isinstance(preferences, str):
                try:
                    preferences = json.loads(preferences)
                except (json.JSONDecodeError, ValueError):
                    preferences = {}
            elif not isinstance(preferences, dict):
                preferences = {}
        else:
            preferences = None
        
        return SubscriberResponse(
            id=subscription.id,
            email=subscription.email,
            first_name=subscription.first_name,
            last_name=subscription.last_name,
            company=subscription.company,
            subscription_type=subscription.subscription_type,
            status=subscription.status,
            source=subscription.source,
            subscribed_at=subscription.subscribed_at,
            unsubscribed_at=subscription.unsubscribed_at,
            last_email_sent=subscription.last_email_sent,
            email_count=subscription.email_count or 0,
            preferences=preferences,
            created_at=subscription.created_at,
            updated_at=subscription.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error loading subscriber: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load subscriber: {str(e)}"
        )


class SubscriberUpdateRequest(BaseModel):
    """Update subscriber status request"""
    email: str
    status: Optional[str] = None  # active, unsubscribed, bounced


@router.put("/subscribers/{subscriber_id}/status", response_model=dict)
async def update_subscriber_status(
    subscriber_id: int,
    request_data: SubscriberUpdateRequest,
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """
    Update subscriber status (unsubscribe/resubscribe) by admin.
    """
    try:
        subscription_service = SubscriptionService(db)
        
        # Get the subscription
        subscription = db.query(EmailSubscription).filter(
            EmailSubscription.id == subscriber_id
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscriber not found"
            )
        
        # Update status
        if request_data.status == "unsubscribed":
            result = subscription_service.unsubscribe_email(email=subscription.email)
        elif request_data.status == "active":
            # Resubscribe
            subscription.status = "active"
            subscription.unsubscribed_at = None
            subscription.updated_at = datetime.now(timezone.utc)
            db.commit()
            result = {
                "success": True,
                "message": "Subscriber resubscribed successfully"
            }
        else:
            # Update status directly
            subscription.status = request_data.status
            subscription.updated_at = datetime.now(timezone.utc)
            if request_data.status == "unsubscribed":
                subscription.unsubscribed_at = datetime.now(timezone.utc)
            elif request_data.status == "active":
                subscription.unsubscribed_at = None
            db.commit()
            result = {
                "success": True,
                "message": f"Subscriber status updated to {request_data.status}"
            }
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("message", "Failed to update subscriber status")
            )
        
        return {
            "success": True,
            "message": result.get("message", "Subscriber status updated successfully"),
            "subscriber_id": subscriber_id,
            "email": subscription.email,
            "status": subscription.status
        }
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error updating subscriber status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update subscriber status: {str(e)}"
        )


@router.delete("/subscribers/{subscriber_id}", response_model=dict)
async def delete_subscriber(
    subscriber_id: int,
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a subscriber from the database.
    """
    try:
        subscription = db.query(EmailSubscription).filter(
            EmailSubscription.id == subscriber_id
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscriber not found"
            )
        
        email = subscription.email
        db.delete(subscription)
        db.commit()
        
        return {
            "success": True,
            "message": f"Subscriber {email} deleted successfully",
            "subscriber_id": subscriber_id,
            "email": email
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error deleting subscriber: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete subscriber: {str(e)}"
        )

