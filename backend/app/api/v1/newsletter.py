"""
Newsletter API endpoints for Crane Intelligence Platform
Handles email newsletter subscriptions from the footer
"""

from fastapi import APIRouter, HTTPException, Depends, status, Request
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime, timezone
import logging

from ...core.database import get_db
from ...services.subscription_service import SubscriptionService
from ...services.email_service_unified import email_service
from ...services.email_template_service import EmailTemplateService
from ...schemas.subscription import EmailSubscriptionCreate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/newsletter", tags=["Newsletter"])


class NewsletterSubscribeRequest(BaseModel):
    email: EmailStr


class NewsletterSubscribeResponse(BaseModel):
    success: bool
    message: str
    error: Optional[str] = None


@router.post("/subscribe", response_model=NewsletterSubscribeResponse)
async def subscribe_to_newsletter(
    request_data: NewsletterSubscribeRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Subscribe an email to the newsletter
    Called from the footer subscription form
    """
    try:
        # Get client IP and user agent
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # Create subscription data
        subscription_data = EmailSubscriptionCreate(
            email=request_data.email,
            subscription_type="newsletter",
            source="footer"
        )
        
        # Subscribe email
        subscription_service = SubscriptionService(db)
        result = subscription_service.subscribe_email(
            subscription_data=subscription_data,
            ip_address=client_ip,
            user_agent=user_agent
        )
        
        # Send welcome email if subscription was successful (new or reactivated)
        # Also send if user was already subscribed (they might not have received the email)
        should_send_email = result.get("success") or result.get("already_subscribed", False)
        
        # Check if user already received an email (to avoid sending duplicates)
        if should_send_email:
            subscription = result.get("subscription")
            if subscription:
                # Check if they've already received an email
                if hasattr(subscription, 'last_email_sent') and subscription.last_email_sent:
                    logger.info(f"User {request_data.email} already received welcome email, skipping")
                    should_send_email = False
        
        if should_send_email:
            # Send welcome email using standardized template
            try:
                email_subject = "Welcome to Crane Intelligence Newsletter"
                
                # Get first name from subscription data if available
                first_name = None
                if hasattr(subscription_data, 'first_name') and subscription_data.first_name:
                    first_name = subscription_data.first_name
                elif hasattr(request_data, 'first_name') and request_data.first_name:
                    first_name = request_data.first_name
                else:
                    # Try to get from existing subscription
                    subscription = result.get("subscription")
                    if subscription and hasattr(subscription, 'first_name'):
                        first_name = subscription.first_name
                
                # Generate email using standardized template service
                email_html = EmailTemplateService.newsletter_welcome(
                    email=request_data.email,
                    first_name=first_name
                )
                
                # Verify template was generated correctly
                if not email_html or len(email_html) < 100:
                    logger.error(f"Generated email template is too short or empty: {len(email_html) if email_html else 0} characters")
                    raise ValueError("Email template generation failed")
                
                # Verify logo is in template
                if 'crane-intelligence-logo' not in email_html:
                    logger.error("Logo missing from generated email template")
                    raise ValueError("Email template missing required brand elements")
                
                logger.info(f"Generated email template with {len(email_html)} characters, logo present: {'crane-intelligence-logo' in email_html}")
                
                email_sent = email_service.send_email(
                    to_emails=[request_data.email],
                    subject=email_subject,
                    html_content=email_html
                )
                
                if email_sent:
                    logger.info(f"Welcome email sent to {request_data.email} using standardized template")
                    # Update last_email_sent and email_count in database
                    try:
                        subscription_service = SubscriptionService(db)
                        subscription = subscription_service.db.query(EmailSubscription).filter(
                            EmailSubscription.email == request_data.email
                        ).first()
                        if subscription:
                            from datetime import datetime, timezone
                            subscription.last_email_sent = datetime.now(timezone.utc)
                            subscription.email_count = (subscription.email_count or 0) + 1
                            subscription_service.db.commit()
                    except Exception as db_error:
                        logger.warning(f"Failed to update email tracking in database: {db_error}")
                else:
                    logger.warning(f"Failed to send welcome email to {request_data.email}")
                    
            except Exception as e:
                logger.error(f"Error sending welcome email: {e}", exc_info=True)
                # Don't fail the subscription if email fails
        
        return NewsletterSubscribeResponse(
            success=result.get("success", False),
            message=result.get("message", "Subscription processed"),
            error=result.get("error")
        )
        
    except Exception as e:
        logger.error(f"Error processing newsletter subscription: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process subscription request"
        )


@router.post("/unsubscribe", response_model=NewsletterSubscribeResponse)
async def unsubscribe_from_newsletter(
    request_data: NewsletterSubscribeRequest,
    db: Session = Depends(get_db)
):
    """
    Unsubscribe an email from the newsletter
    """
    try:
        subscription_service = SubscriptionService(db)
        result = subscription_service.unsubscribe_email(email=request_data.email)
        
        return NewsletterSubscribeResponse(
            success=result.get("success", False),
            message=result.get("message", "Unsubscription processed"),
            error=result.get("error")
        )
        
    except Exception as e:
        logger.error(f"Error processing newsletter unsubscription: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process unsubscription request"
        )

