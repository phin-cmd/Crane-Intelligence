"""
Consultation API endpoints for Crane Intelligence Platform
Handles consultation requests from the homepage
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime, timezone
import logging

from ...core.database import get_db
from ...models.consultation import ConsultationRequest, ConsultationStatus
from ...models.admin import AdminUser
from ...core.admin_auth import get_current_admin_user
from ...services.email_service_unified import email_service
from ...services.email_template_service import EmailTemplateService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/consultation", tags=["Consultation"])


# Pydantic models
class ConsultationSubmitRequest(BaseModel):
    name: str
    email: EmailStr
    company: Optional[str] = None
    subject: Optional[str] = None  # Optional subject for contact form
    message: str
    type: Optional[str] = "consultation_request"


class ConsultationResponse(BaseModel):
    id: int
    name: str
    email: str
    company: Optional[str]
    subject: Optional[str]
    message: str
    status: str
    created_at: datetime
    email_sent: bool
    
    class Config:
        from_attributes = True


class ConsultationListResponse(BaseModel):
    success: bool
    message: str
    data: List[ConsultationResponse]
    total: int
    error: Optional[str] = None


class ConsultationUpdateRequest(BaseModel):
    status: Optional[str] = None
    admin_notes: Optional[str] = None


@router.post("/submit", response_model=ConsultationResponse)
async def submit_consultation(
    request: ConsultationSubmitRequest,
    db: Session = Depends(get_db)
):
    """
    Submit a consultation request from the homepage
    Saves to database and sends email notification to all admin users
    """
    try:
        logger.info(f"Received consultation request from {request.name} ({request.email})")
        
        # Create consultation request
        consultation = ConsultationRequest(
            name=request.name,
            email=request.email,
            company=request.company,
            subject=request.subject,
            message=request.message,
            status=ConsultationStatus.NEW.value
        )
        
        logger.info("Adding consultation request to database...")
        db.add(consultation)
        db.commit()
        db.refresh(consultation)
        logger.info(f"Consultation request {consultation.id} created successfully")
        
        # Get all active admin users
        # Use a more resilient query that handles missing columns
        try:
            admin_users = db.query(AdminUser).filter(
                AdminUser.is_active == True,
                AdminUser.is_verified == True
            ).all()
            admin_emails = [admin.email for admin in admin_users]
        except Exception as e:
            # Fallback: Query admin emails directly using raw SQL if model columns don't match DB schema
            logger.warning(f"Could not query AdminUser model: {e}. Using direct email query.")
            try:
                from sqlalchemy import text
                result = db.execute(text("""
                    SELECT email 
                    FROM admin_users 
                    WHERE is_active = true AND is_verified = true
                """))
                admin_emails = [row[0] for row in result.fetchall()]
            except Exception as sql_error:
                logger.error(f"Could not query admin emails directly: {sql_error}")
                admin_emails = []
        
        if admin_emails:
            # Send email notification to all admin users using standard email template and brand guide
            try:
                # Determine if this is a consultation or contact request for subject line
                is_contact_request = request.subject is not None or request.type == 'contact_request'
                if is_contact_request:
                    email_subject = f"New Contact Form Submission from {request.name}"
                else:
                    email_subject = f"New Consultation Request from {request.name}"
                
                # Generate email using standard template and brand guide
                email_html = EmailTemplateService.consultation_admin_notification(
                    name=request.name,
                    email=request.email,
                    company=request.company,
                    subject=request.subject,
                    message=request.message,
                    consultation_id=consultation.id,
                    created_at=consultation.created_at.strftime('%B %d, %Y at %I:%M %p')
                )
                
                # Verify template was generated correctly with logo
                if not email_html or len(email_html) < 100:
                    logger.error(f"Generated admin notification email template is too short or empty: {len(email_html) if email_html else 0} characters")
                    raise ValueError("Email template generation failed")
                
                # Verify logo is in template
                if 'crane-intelligence-logo' not in email_html:
                    logger.error("Logo missing from generated admin notification email template")
                    raise ValueError("Email template missing required brand elements")
                
                logger.info(f"Generated admin notification email template with {len(email_html)} characters, logo present: {'crane-intelligence-logo' in email_html}")
                
                email_sent = email_service.send_email(
                    to_emails=admin_emails,
                    subject=email_subject,
                    html_content=email_html
                )
                
                if email_sent:
                    consultation.email_sent = True
                    consultation.email_sent_at = datetime.now(timezone.utc)
                    db.commit()
                    logger.info(f"Consultation request {consultation.id} - Email sent to {len(admin_emails)} admin users")
                else:
                    logger.warning(f"Consultation request {consultation.id} - Failed to send email notification")
                    
            except Exception as e:
                logger.error(f"Error sending consultation email notification: {e}", exc_info=True)
                # Don't fail the request if email fails
        else:
            logger.warning("No active admin users found to send consultation notification")
        
        # Send confirmation email to the user using standardized template
        try:
            # Determine if this is a consultation or contact request
            is_contact_request = request.subject is not None or request.type == 'contact_request'
            
            if is_contact_request:
                # Contact form confirmation email
                user_email_subject = "Thank You for Contacting Crane Intelligence"
                user_email_html = EmailTemplateService.consultation_user_confirmation(
                    name=request.name,
                    email=request.email,
                    company=request.company,
                    subject=request.subject,
                    message=request.message,
                    consultation_id=consultation.id,
                    created_at=consultation.created_at.strftime('%B %d, %Y at %I:%M %p'),
                    is_contact_request=True
                )
            else:
                # Consultation form confirmation email
                user_email_subject = "Thank You for Your Consultation Request"
                user_email_html = EmailTemplateService.consultation_user_confirmation(
                    name=request.name,
                    email=request.email,
                    company=request.company,
                    subject=request.subject,
                    message=request.message,
                    consultation_id=consultation.id,
                    created_at=consultation.created_at.strftime('%B %d, %Y at %I:%M %p'),
                    is_contact_request=False
                )
            
            # Verify template was generated correctly
            if not user_email_html or len(user_email_html) < 100:
                logger.error(f"Generated consultation email template is too short or empty: {len(user_email_html) if user_email_html else 0} characters")
                raise ValueError("Email template generation failed")
            
            # Verify logo is in template
            if 'crane-intelligence-logo' not in user_email_html:
                logger.error("Logo missing from generated consultation email template")
                raise ValueError("Email template missing required brand elements")
            
            logger.info(f"Generated consultation email template with {len(user_email_html)} characters, logo present: {'crane-intelligence-logo' in user_email_html}")
            
            user_email_sent = email_service.send_email(
                to_emails=[request.email],
                subject=user_email_subject,
                html_content=user_email_html
            )
            
            if user_email_sent:
                logger.info(f"Confirmation email sent to user {request.email} for consultation request {consultation.id} using standardized template")
            else:
                logger.warning(f"Failed to send confirmation email to user {request.email} for consultation request {consultation.id}")
                
        except Exception as e:
            logger.error(f"Error sending user confirmation email: {e}", exc_info=True)
            # Don't fail the request if user email fails
        
        return ConsultationResponse(
            id=consultation.id,
            name=consultation.name,
            email=consultation.email,
            company=consultation.company,
            subject=consultation.subject,
            message=consultation.message,
            status=consultation.status,
            created_at=consultation.created_at,
            email_sent=consultation.email_sent
        )
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Error submitting consultation request: {e}")
        logger.error(f"Full traceback: {error_details}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit consultation request: {str(e)}"
        )


@router.get("", response_model=ConsultationListResponse)
async def get_consultations(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all consultation requests (admin only)
    """
    try:
        query = db.query(ConsultationRequest)
        
        if status_filter:
            query = query.filter(ConsultationRequest.status == status_filter)
        
        total = query.count()
        consultations = query.order_by(ConsultationRequest.created_at.desc()).offset(skip).limit(limit).all()
        
        return ConsultationListResponse(
            success=True,
            message="Consultations retrieved successfully",
            data=[
                ConsultationResponse(
                    id=c.id,
                    name=c.name,
                    email=c.email,
                    company=c.company,
                    subject=c.subject,
                    message=c.message,
                    status=c.status,
                    created_at=c.created_at,
                    email_sent=c.email_sent
                ) for c in consultations
            ],
            total=total
        )
    except Exception as e:
        logger.error(f"Error fetching consultations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch consultations"
        )


@router.get("/{consultation_id}", response_model=ConsultationResponse)
async def get_consultation(
    consultation_id: int,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific consultation request (admin only)
    """
    try:
        consultation = db.query(ConsultationRequest).filter(
            ConsultationRequest.id == consultation_id
        ).first()
        
        if not consultation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consultation request not found"
            )
        
        return ConsultationResponse(
            id=consultation.id,
            name=consultation.name,
            email=consultation.email,
            company=consultation.company,
            subject=consultation.subject,
            message=consultation.message,
            status=consultation.status,
            created_at=consultation.created_at,
            email_sent=consultation.email_sent
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching consultation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch consultation"
        )


@router.patch("/{consultation_id}", response_model=ConsultationResponse)
async def update_consultation(
    consultation_id: int,
    update_data: ConsultationUpdateRequest,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update a consultation request (admin only)
    """
    try:
        consultation = db.query(ConsultationRequest).filter(
            ConsultationRequest.id == consultation_id
        ).first()
        
        if not consultation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consultation request not found"
            )
        
        if update_data.status:
            consultation.status = update_data.status
            # Update status-specific timestamps
            now = datetime.now(timezone.utc)
            if update_data.status == ConsultationStatus.CONTACTED.value:
                consultation.contacted_at = now
            elif update_data.status == ConsultationStatus.SCHEDULED.value:
                consultation.scheduled_at = now
            elif update_data.status == ConsultationStatus.COMPLETED.value:
                consultation.completed_at = now
        
        if update_data.admin_notes is not None:
            consultation.admin_notes = update_data.admin_notes
        
        db.commit()
        db.refresh(consultation)
        
        return ConsultationResponse(
            id=consultation.id,
            name=consultation.name,
            email=consultation.email,
            company=consultation.company,
            subject=consultation.subject,
            message=consultation.message,
            status=consultation.status,
            created_at=consultation.created_at,
            email_sent=consultation.email_sent
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating consultation: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update consultation"
        )

