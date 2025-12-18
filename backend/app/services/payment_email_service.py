"""
Payment Email Service
Handles all email notifications for payment events using Brevo
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .brevo_email_service import BrevoEmailService
from ..core.config import settings

logger = logging.getLogger(__name__)


class PaymentEmailService:
    """Email service for payment notifications using Brevo"""
    
    def __init__(self):
        try:
            self.email_service = BrevoEmailService()
        except Exception as e:
            logger.warning(f"Failed to initialize payment email service: {e}")
            self.email_service = None
    
    def _extract_first_name(self, user_name: str) -> str:
        """Extract first name from full name"""
        if not user_name:
            return "User"
        return user_name.split()[0] if user_name.split() else user_name
    
    def send_payment_initiated_notification(
        self, 
        user_email: str, 
        user_name: str, 
        payment_data: Dict[str, Any]
    ) -> bool:
        """Send notification when payment is initiated"""
        if not self.email_service:
            return False
        try:
            first_name = self._extract_first_name(user_name)
            template_context = {
                "username": user_name.split()[0] if user_name else "User",
                "user_name": user_name,
                "first_name": first_name,
                "user_email": user_email,
                "amount": payment_data.get('amount', 0) / 100 if payment_data.get('amount') else 0,  # Convert cents to dollars
                "payment_intent_id": payment_data.get('payment_intent_id'),
                "description": payment_data.get('description', 'Payment'),
                "initiated_date": datetime.now().strftime('%B %d, %Y at %I:%M %p'),
                "platform_name": settings.app_name,
                "support_email": settings.mail_from_email
            }
            
            result = self.email_service.send_template_email(
                to_emails=[user_email],
                template_name="payment_initiated.html",
                template_context=template_context,
                subject=f"Payment Initiated - {settings.app_name}",
                tags=["payment", "initiated"]
            )
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error sending payment initiated notification: {e}")
            return False
    
    def send_payment_success_notification(
        self, 
        user_email: str, 
        user_name: str, 
        payment_data: Dict[str, Any]
    ) -> bool:
        """Send notification when payment succeeds"""
        if not self.email_service:
            return False
        try:
            first_name = self._extract_first_name(user_name)
            template_context = {
                "username": user_name.split()[0] if user_name else "User",
                "user_name": user_name,
                "first_name": first_name,
                "user_email": user_email,
                "amount": payment_data.get('amount', 0) / 100 if payment_data.get('amount') else 0,
                "payment_intent_id": payment_data.get('payment_intent_id'),
                "charge_id": payment_data.get('charge_id'),
                "description": payment_data.get('description', 'Payment'),
                "payment_date": datetime.now().strftime('%B %d, %Y at %I:%M %p'),
                "platform_name": settings.app_name,
                "support_email": settings.mail_from_email,
                "dashboard_url": f"{settings.frontend_url}/dashboard.html"
            }
            
            result = self.email_service.send_template_email(
                to_emails=[user_email],
                template_name="payment_success.html",
                template_context=template_context,
                subject=f"Payment Successful - {settings.app_name}",
                tags=["payment", "success"]
            )
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error sending payment success notification: {e}")
            return False
    
    def send_payment_failed_notification(
        self, 
        user_email: str, 
        user_name: str, 
        payment_data: Dict[str, Any]
    ) -> bool:
        """Send notification when payment fails"""
        if not self.email_service:
            return False
        try:
            template_context = {
                "username": user_name,
                "user_email": user_email,
                "amount": payment_data.get('amount', 0) / 100 if payment_data.get('amount') else 0,
                "payment_intent_id": payment_data.get('payment_intent_id'),
                "error_message": payment_data.get('error_message', 'Payment could not be processed'),
                "failed_date": datetime.now().strftime('%B %d, %Y at %I:%M %p'),
                "platform_name": settings.app_name,
                "support_email": settings.mail_from_email,
                "payment_url": payment_data.get('payment_url', f"{settings.frontend_url}/payment.html")
            }
            
            result = self.email_service.send_template_email(
                to_emails=[user_email],
                template_name="payment_failed.html",
                template_context=template_context,
                subject=f"Payment Failed - {settings.app_name}",
                tags=["payment", "failed"]
            )
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error sending payment failed notification: {e}")
            return False
    
    def send_payment_cancelled_notification(
        self, 
        user_email: str, 
        user_name: str, 
        payment_data: Dict[str, Any]
    ) -> bool:
        """Send notification when payment is cancelled"""
        if not self.email_service:
            return False
        try:
            first_name = self._extract_first_name(user_name)
            template_context = {
                "username": user_name.split()[0] if user_name else "User",
                "user_name": user_name,
                "first_name": first_name,
                "user_email": user_email,
                "amount": payment_data.get('amount', 0) / 100 if payment_data.get('amount') else 0,
                "payment_intent_id": payment_data.get('payment_intent_id'),
                "cancelled_date": datetime.now().strftime('%B %d, %Y at %I:%M %p'),
                "platform_name": settings.app_name,
                "support_email": settings.mail_from_email
            }
            
            result = self.email_service.send_template_email(
                to_emails=[user_email],
                template_name="payment_cancelled.html",
                template_context=template_context,
                subject=f"Payment Cancelled - {settings.app_name}",
                tags=["payment", "cancelled"]
            )
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error sending payment cancelled notification: {e}")
            return False
    
    def send_payment_refunded_notification(
        self, 
        user_email: str, 
        user_name: str, 
        payment_data: Dict[str, Any]
    ) -> bool:
        """Send notification when payment is refunded"""
        if not self.email_service:
            return False
        try:
            first_name = self._extract_first_name(user_name)
            template_context = {
                "username": user_name.split()[0] if user_name else "User",
                "user_name": user_name,
                "first_name": first_name,
                "user_email": user_email,
                "amount": payment_data.get('amount', 0) / 100 if payment_data.get('amount') else 0,
                "refund_amount": payment_data.get('refund_amount', 0) / 100 if payment_data.get('refund_amount') else 0,
                "charge_id": payment_data.get('charge_id'),
                "refund_id": payment_data.get('refund_id'),
                "refund_date": datetime.now().strftime('%B %d, %Y at %I:%M %p'),
                "platform_name": settings.app_name,
                "support_email": settings.mail_from_email
            }
            
            result = self.email_service.send_template_email(
                to_emails=[user_email],
                template_name="payment_refunded.html",
                template_context=template_context,
                subject=f"Payment Refunded - {settings.app_name}",
                tags=["payment", "refund"]
            )
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error sending payment refunded notification: {e}")
            return False
    
    def send_subscription_payment_success_notification(
        self, 
        user_email: str, 
        user_name: str, 
        payment_data: Dict[str, Any]
    ) -> bool:
        """Send notification when subscription payment succeeds"""
        if not self.email_service:
            return False
        try:
            template_context = {
                "username": user_name,
                "user_email": user_email,
                "amount": payment_data.get('amount', 0) / 100 if payment_data.get('amount') else 0,
                "invoice_id": payment_data.get('invoice_id'),
                "subscription_id": payment_data.get('subscription_id'),
                "billing_period": payment_data.get('billing_period', 'Monthly'),
                "payment_date": datetime.now().strftime('%B %d, %Y at %I:%M %p'),
                "next_billing_date": payment_data.get('next_billing_date'),
                "platform_name": settings.app_name,
                "support_email": settings.mail_from_email,
                "dashboard_url": f"{settings.frontend_url}/dashboard.html"
            }
            
            result = self.email_service.send_template_email(
                to_emails=[user_email],
                template_name="subscription_payment_success.html",
                template_context=template_context,
                subject=f"Subscription Payment Successful - {settings.app_name}",
                tags=["payment", "subscription", "success"]
            )
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error sending subscription payment success notification: {e}")
            return False
    
    def send_subscription_payment_failed_notification(
        self, 
        user_email: str, 
        user_name: str, 
        payment_data: Dict[str, Any]
    ) -> bool:
        """Send notification when subscription payment fails"""
        if not self.email_service:
            return False
        try:
            template_context = {
                "username": user_name,
                "user_email": user_email,
                "amount": payment_data.get('amount', 0) / 100 if payment_data.get('amount') else 0,
                "invoice_id": payment_data.get('invoice_id'),
                "subscription_id": payment_data.get('subscription_id'),
                "error_message": payment_data.get('error_message', 'Payment could not be processed'),
                "failed_date": datetime.now().strftime('%B %d, %Y at %I:%M %p'),
                "platform_name": settings.app_name,
                "support_email": settings.mail_from_email,
                "payment_url": payment_data.get('payment_url', f"{settings.frontend_url}/payment.html")
            }
            
            result = self.email_service.send_template_email(
                to_emails=[user_email],
                template_name="subscription_payment_failed.html",
                template_context=template_context,
                subject=f"Subscription Payment Failed - {settings.app_name}",
                tags=["payment", "subscription", "failed"]
            )
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error sending subscription payment failed notification: {e}")
            return False

