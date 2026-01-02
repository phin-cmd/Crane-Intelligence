#!/usr/bin/env python3
"""
Send welcome emails to all active subscribers
This script sends welcome emails to subscribers who haven't received one yet
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.subscription import EmailSubscription
from app.services.email_service_unified import email_service
from app.services.email_template_service import EmailTemplateService
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send_welcome_emails_to_all_subscribers(send_to_all=False, specific_email=None):
    """
    Send welcome emails to subscribers
    
    Args:
        send_to_all: If True, send to all active subscribers. If False, only send to those who haven't received one
        specific_email: If provided, only send to this specific email
    """
    db: Session = SessionLocal()
    
    try:
        # Build query
        query = db.query(EmailSubscription)
        
        if specific_email:
            query = query.filter(EmailSubscription.email == specific_email)
        else:
            query = query.filter(EmailSubscription.status == "active")
            if not send_to_all:
                # Only send to subscribers who haven't received an email yet
                query = query.filter(
                    (EmailSubscription.last_email_sent == None) | 
                    (EmailSubscription.email_count == None) | 
                    (EmailSubscription.email_count == 0)
                )
        
        subscribers = query.all()
        
        logger.info(f"Found {len(subscribers)} subscriber(s) to process")
        
        if len(subscribers) == 0:
            logger.info("No subscribers found to send emails to")
            return
        
        success_count = 0
        failure_count = 0
        
        for subscriber in subscribers:
            try:
                email = subscriber.email
                first_name = subscriber.first_name
                
                logger.info(f"Processing subscriber: {email}")
                
                # Generate welcome email
                email_html = EmailTemplateService.newsletter_welcome(
                    email=email,
                    first_name=first_name
                )
                
                if not email_html or len(email_html) < 100:
                    logger.error(f"Failed to generate email template for {email}")
                    failure_count += 1
                    continue
                
                # Send email
                email_subject = "Welcome to Crane Intelligence Newsletter"
                email_sent = email_service.send_email(
                    to_emails=[email],
                    subject=email_subject,
                    html_content=email_html
                )
                
                if email_sent:
                    # Update subscriber record
                    subscriber.last_email_sent = datetime.utcnow()
                    subscriber.email_count = (subscriber.email_count or 0) + 1
                    db.commit()
                    
                    logger.info(f"✅ Welcome email sent successfully to {email}")
                    success_count += 1
                else:
                    logger.error(f"❌ Failed to send email to {email}")
                    failure_count += 1
                    
            except Exception as e:
                logger.error(f"❌ Error processing {subscriber.email}: {e}", exc_info=True)
                failure_count += 1
                db.rollback()
        
        logger.info("=" * 60)
        logger.info(f"Email sending complete!")
        logger.info(f"✅ Successfully sent: {success_count}")
        logger.info(f"❌ Failed: {failure_count}")
        logger.info(f"📊 Total processed: {len(subscribers)}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Error in send_welcome_emails_to_all_subscribers: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Send welcome emails to subscribers")
    parser.add_argument("--all", action="store_true", help="Send to all active subscribers (not just those who haven't received one)")
    parser.add_argument("--email", type=str, help="Send to a specific email address")
    
    args = parser.parse_args()
    
    if args.email:
        logger.info(f"Sending welcome email to specific subscriber: {args.email}")
        send_welcome_emails_to_all_subscribers(send_to_all=True, specific_email=args.email)
    elif args.all:
        logger.info("Sending welcome emails to ALL active subscribers")
        send_welcome_emails_to_all_subscribers(send_to_all=True)
    else:
        logger.info("Sending welcome emails to subscribers who haven't received one yet")
        send_welcome_emails_to_all_subscribers(send_to_all=False)

