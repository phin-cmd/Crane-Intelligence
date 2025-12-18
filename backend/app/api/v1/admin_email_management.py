"""
Email Template and Management API
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from ...core.database import get_db
from ...models.admin import AdminUser, EmailTemplate
from ...core.admin_auth import require_admin_or_super_admin

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


@router.get("/templates", response_model=List[EmailTemplateResponse])
async def list_email_templates(
    template_type: Optional[str] = Query(None),
    active_only: bool = Query(False),
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """List all email templates"""
    query = db.query(EmailTemplate)
    
    if template_type:
        query = query.filter(EmailTemplate.template_type == template_type)
    if active_only:
        query = query.filter(EmailTemplate.is_active == True)
    
    templates = query.order_by(EmailTemplate.name).all()
    
    return [
        EmailTemplateResponse(
            id=t.id,
            name=t.name,
            subject=t.subject,
            body_html=t.body_html,
            body_text=t.body_text,
            template_type=t.template_type,
            variables=t.variables,
            is_active=t.is_active,
            usage_count=t.usage_count,
            last_used=t.last_used,
            created_at=t.created_at,
            updated_at=t.updated_at
        )
        for t in templates
    ]


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

