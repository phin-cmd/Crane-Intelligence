"""
FMV Report Email Service
Handles all email notifications for FMV report workflow
Enhanced to use Brevo API directly
"""

import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
except ImportError:
    # Fallback for Python < 3.9
    from backports.zoneinfo import ZoneInfo

from .brevo_email_service import BrevoEmailService
from .email_service_unified import UnifiedEmailService
from ..core.config import settings

logger = logging.getLogger(__name__)


class FMVEmailService:
    """Email service for FMV report notifications using Brevo API or SMTP"""
    
    def __init__(self):
        try:
            # Use UnifiedEmailService which respects USE_BREVO_API setting and falls back to SMTP
            self.email_service = UnifiedEmailService()
            self.template_dir = Path(settings.email_templates_dir)
        except Exception as e:
            logger.warning(f"Failed to initialize FMV email service: {e}")
            self.email_service = None
            self.template_dir = None
    
    def _extract_first_name(self, user_name: str) -> str:
        """Extract first name from full name"""
        if not user_name:
            return "User"
        return user_name.split()[0] if user_name.split() else user_name
    
    def _get_user_timezone(self, user_timezone: Optional[str] = None) -> str:
        """Get user timezone, defaulting to UTC if not provided"""
        if user_timezone:
            return user_timezone
        # Default to UTC if no timezone specified
        return 'UTC'
    
    def _format_datetime_with_timezone(self, dt: datetime, user_timezone: Optional[str] = None, include_timezone: bool = True) -> str:
        """Format datetime in user's timezone
        
        Args:
            dt: UTC datetime object
            user_timezone: User's timezone (e.g., 'America/New_York')
            include_timezone: Whether to include timezone abbreviation in output
        
        Returns:
            Formatted datetime string in user's timezone
        """
        if not dt:
            return 'N/A'
        
        try:
            tz = self._get_user_timezone(user_timezone)
            # Convert UTC to user's timezone
            if dt.tzinfo is None:
                # Assume UTC if no timezone info
                dt = dt.replace(tzinfo=ZoneInfo('UTC'))
            
            user_dt = dt.astimezone(ZoneInfo(tz))
            
            # Format with timezone abbreviation
            if include_timezone:
                # Format: "Dec 19, 2024, 3:45 PM EST"
                return user_dt.strftime('%B %d, %Y at %I:%M %p %Z')
            else:
                # Format: "Dec 19, 2024, 3:45 PM"
                return user_dt.strftime('%B %d, %Y at %I:%M %p')
        except Exception as e:
            logger.warning(f"Error formatting datetime with timezone {user_timezone}: {e}")
            # Fallback to UTC formatting
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=ZoneInfo('UTC'))
            return dt.strftime('%B %d, %Y at %I:%M %p UTC')
    
    def _convert_amount_to_dollars(self, amount: Any) -> float:
        """Convert amount from cents to dollars if needed
        
        Args:
            amount: Amount value (could be in cents or dollars)
        
        Returns:
            Amount in dollars
        """
        if not amount:
            return 0.0
        
        # Convert to float
        try:
            amount_float = float(amount)
        except (ValueError, TypeError):
            return 0.0
        
        # If amount is >= 10000, it's definitely in cents (e.g., 149500 = $1495.00)
        # If amount is between 1000-9999, check if it's a round number divisible by 100
        # (common cent values like 25000, 99500, 149500)
        if amount_float >= 10000:
            # Definitely in cents, convert to dollars
            return amount_float / 100.0
        elif amount_float >= 1000:
            # Check if it's a round cent value (divisible by 100 with no remainder when divided by 100)
            # This catches values like 25000, 99500, 149500
            if isinstance(amount, (int, float)) and amount_float % 100 == 0 and amount_float >= 1000:
                return amount_float / 100.0
        
        # Otherwise, assume it's already in dollars
        return amount_float
    
    def send_submitted_notification(self, user_email: str, user_name: str, report_data: Dict[str, Any], user_timezone: Optional[str] = None) -> bool:
        """Send notification when report is submitted with PDF receipt attachment"""
        if not self.email_service:
            return False
        try:
            first_name = self._extract_first_name(user_name)
            # Get submitted_at from report_data or use current time
            submitted_dt = report_data.get('submitted_at')
            if submitted_dt:
                if isinstance(submitted_dt, str):
                    from dateutil import parser
                    submitted_dt = parser.parse(submitted_dt)
                elif not isinstance(submitted_dt, datetime):
                    submitted_dt = None
            if not submitted_dt:
                submitted_dt = datetime.now(ZoneInfo('UTC'))
            
            template_context = {
                "username": user_name.split()[0] if user_name else "User",
                "user_name": user_name,
                "first_name": first_name,
                "user_email": user_email,
                "report_id": report_data.get('report_id'),
                "report_type": report_data.get('report_type', 'N/A').replace('_', ' ').title(),
                "submitted_date": self._format_datetime_with_timezone(submitted_dt, user_timezone),
                "platform_name": settings.app_name,
                "support_email": settings.mail_from_email,
                "dashboard_url": f"{settings.frontend_url}/dashboard.html"
            }
            
            # Generate PDF receipt attachment
            attachments = []
            try:
                from .receipt_pdf_service import ReceiptPDFService
                pdf_service = ReceiptPDFService()
                
                if pdf_service.available:
                    receipt_data = {
                        "receipt_number": f"RPT-{report_data.get('report_id', 'N/A')}",
                        "transaction_id": report_data.get('payment_intent_id', report_data.get('transaction_id', 'N/A')),
                        "payment_date": datetime.now(ZoneInfo('UTC')).isoformat(),
                        "customer_name": user_name,
                        "customer_email": user_email,
                        "report_id": report_data.get('report_id'),
                        "report_type": report_data.get('report_type', 'N/A'),
                        "amount": self._convert_amount_to_dollars(report_data.get('amount', 0)),
                        "currency": "USD",
                        "company_name": settings.app_name
                    }
                    
                    pdf_base64 = pdf_service.generate_receipt_pdf_base64(receipt_data)
                    if pdf_base64:
                        attachments.append({
                            "name": f"Payment_Receipt_Report_{report_data.get('report_id', 'N/A')}.pdf",
                            "content": pdf_base64
                        })
                        logger.info(f"✅ Generated PDF receipt attachment for report {report_data.get('report_id')}")
                    else:
                        logger.warning(f"⚠️ Failed to generate PDF receipt for report {report_data.get('report_id')}")
                else:
                    logger.warning("⚠️ PDF receipt service not available - skipping attachment")
            except Exception as pdf_error:
                logger.error(f"❌ Error generating PDF receipt: {pdf_error}", exc_info=True)
                # Continue without attachment if PDF generation fails
            
            result = self.email_service.send_template_email(
                to_emails=[user_email],
                template_name="fmv_report_submitted.html",
                template_context=template_context,
                subject=f"FMV Report Submitted - Report #{report_data.get('report_id')}",
                tags=["fmv-report", "submitted"],
                attachments=attachments if attachments else None
            )
            
            # Also send admin notification
            self._send_admin_notification("submitted", report_data, user_name, user_email)
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error sending submitted notification: {e}")
            return False
    
    def send_draft_reminder_notification(self, user_email: str, user_name: str, report_data: Dict[str, Any], user_timezone: Optional[str] = None) -> bool:
        """Send reminder notification when report is in DRAFT status (payment not completed)
        Sends periodic reminders at different intervals (1 hour, 6 hours, 24 hours, 48 hours, etc.)"""
        logger.info(f"📧 send_draft_reminder_notification called: user_email={user_email}, report_id={report_data.get('report_id')}")
        if not self.email_service:
            logger.warning("⚠️ Email service not available in send_draft_reminder_notification")
            return False
        try:
            first_name = self._extract_first_name(user_name)
            hours_since = report_data.get('hours_since_creation', 0)
            reminder_interval = report_data.get('reminder_interval', '')
            
            # Build reminder message based on time since creation
            if hours_since < 6:
                urgency_message = "Don't forget to complete your payment to submit your FMV report."
            elif hours_since < 24:
                urgency_message = "Your FMV report is still waiting for payment. Complete your purchase now."
            elif hours_since < 48:
                urgency_message = "Your FMV report has been waiting for payment for over 24 hours. Please complete your purchase."
            else:
                urgency_message = f"Your FMV report has been waiting for payment for {int(hours_since)} hours. Complete your purchase to avoid cancellation."
            
            # Get report type and format it for display
            report_type = report_data.get('report_type', '')
            report_type_display = report_data.get('report_type_display')
            if not report_type_display and report_type:
                # Format report type for display (e.g., "spot_check" -> "Spot Check")
                report_type_display = report_type.replace('_', ' ').title()
            
            # Get amount and convert from cents to dollars if needed
            # CRITICAL: Prioritize calculated bulk price from metadata if available
            amount_raw = report_data.get('amount', 0)
            
            # Check for calculated bulk price in metadata (fleet_price_cents or total_price)
            if report_type == 'fleet_valuation':
                # First check for calculated bulk price in metadata
                metadata = report_data.get('metadata', {})
                if isinstance(metadata, str):
                    import json
                    try:
                        metadata = json.loads(metadata)
                    except:
                        metadata = {}
                
                # Check for fleet_price_cents (in cents) or total_price (could be in cents or dollars)
                fleet_price_cents = metadata.get('fleet_price_cents') or report_data.get('fleet_price_cents')
                total_price = metadata.get('total_price') or report_data.get('total_price')
                
                if fleet_price_cents:
                    amount_raw = int(fleet_price_cents)
                    logger.info(f"💰 Using fleet_price_cents from metadata: {amount_raw} cents")
                elif total_price:
                    # total_price might be in cents (if > 1000) or dollars
                    total_price_val = float(total_price)
                    if total_price_val >= 1000:
                        amount_raw = int(total_price_val)  # Assume cents
                    else:
                        amount_raw = int(total_price_val * 100)  # Convert dollars to cents
                    logger.info(f"💰 Using total_price from metadata: {amount_raw} cents")
                elif report_data.get('crane_details'):
                    # Check crane_details for total_price
                    crane_details = report_data.get('crane_details', {})
                    if isinstance(crane_details, str):
                        import json
                        try:
                            crane_details = json.loads(crane_details)
                        except:
                            crane_details = {}
                    if crane_details.get('total_price'):
                        total_price_val = float(crane_details.get('total_price'))
                        if total_price_val >= 1000:
                            amount_raw = int(total_price_val)
                        else:
                            amount_raw = int(total_price_val * 100)
                        logger.info(f"💰 Using total_price from crane_details: {amount_raw} cents")
            
            # Convert amount from cents to dollars if needed
            # Use the proper conversion function that handles edge cases
            amount_dollars = self._convert_amount_to_dollars(amount_raw)
            
            template_context = {
                "username": user_name.split()[0] if user_name else "User",
                "user_name": user_name,
                "first_name": first_name,
                "user_email": user_email,
                "report_id": report_data.get('report_id'),
                "report_type": report_type,
                "report_type_display": report_type_display or "FMV Report",
                "amount": amount_dollars,
                "payment_url": report_data.get('payment_url', f"{settings.frontend_url}/payment.html?report_id={report_data.get('report_id')}"),
                "platform_name": settings.app_name,
                "support_email": settings.mail_from_email,
                "dashboard_url": f"{settings.frontend_url}/dashboard.html",
                "hours_since_creation": int(hours_since) if hours_since else 0,
                "reminder_interval": reminder_interval,
                "urgency_message": urgency_message
            }
            
            # Build subject - always include "Reminder:" prefix
            # For ALL reminders (including initial), do NOT append "(initial since creation)" in the title
            subject = f"Reminder: Complete Your FMV Report Payment - Report #{report_data.get('report_id')}"
            
            logger.info(f"📧 Sending email via send_template_email: to={user_email}, template=fmv_report_draft_reminder.html")
            result = self.email_service.send_template_email(
                to_emails=[user_email],
                template_name="fmv_report_draft_reminder.html",
                template_context=template_context,
                subject=subject,
                tags=["fmv-report", "draft-reminder", "payment-pending"]
            )
            
            logger.info(f"📧 Email send result: {result}")
            success = result.get("success", False)
            logger.info(f"📧 Email send success: {success}")
            
            # Also send admin notification
            self._send_admin_notification("draft_reminder", report_data, user_name, user_email)
            
            return success
        except Exception as e:
            logger.error(f"❌ Error sending draft reminder notification: {e}", exc_info=True)
            return False
    
    def send_draft_created_notification(self, user_email: str, user_name: str, report_data: Dict[str, Any], user_timezone: Optional[str] = None) -> bool:
        """Send notification when a DRAFT report is first created (payment required)"""
        if not self.email_service:
            return False
        try:
            first_name = self._extract_first_name(user_name)
            
            # Get report type and format it for display
            report_type = report_data.get('report_type', '')
            report_type_display = report_data.get('report_type_display')
            if not report_type_display and report_type:
                # Format report type for display (e.g., "spot_check" -> "Spot Check")
                report_type_display = report_type.replace('_', ' ').title()
            
            # Get amount and convert from cents to dollars if needed
            # CRITICAL: Prioritize calculated bulk price from metadata if available
            amount_raw = report_data.get('amount', 0)
            
            # Check for calculated bulk price in metadata (fleet_price_cents or total_price)
            if report_type == 'fleet_valuation':
                # First check for calculated bulk price in metadata
                metadata = report_data.get('metadata', {})
                if isinstance(metadata, str):
                    import json
                    try:
                        metadata = json.loads(metadata)
                    except:
                        metadata = {}
                
                # Check for fleet_price_cents (in cents) or total_price (could be in cents or dollars)
                fleet_price_cents = metadata.get('fleet_price_cents') or report_data.get('fleet_price_cents')
                total_price = metadata.get('total_price') or report_data.get('total_price')
                
                if fleet_price_cents:
                    amount_raw = int(fleet_price_cents)
                    logger.info(f"💰 Using fleet_price_cents from metadata: {amount_raw} cents")
                elif total_price:
                    # total_price might be in cents (if > 1000) or dollars
                    total_price_val = float(total_price)
                    if total_price_val >= 1000:
                        amount_raw = int(total_price_val)  # Assume cents
                    else:
                        amount_raw = int(total_price_val * 100)  # Convert dollars to cents
                    logger.info(f"💰 Using total_price from metadata: {amount_raw} cents")
                elif report_data.get('crane_details'):
                    # Check crane_details for total_price
                    crane_details = report_data.get('crane_details', {})
                    if isinstance(crane_details, str):
                        import json
                        try:
                            crane_details = json.loads(crane_details)
                        except:
                            crane_details = {}
                    if crane_details.get('total_price'):
                        total_price_val = float(crane_details.get('total_price'))
                        if total_price_val >= 1000:
                            amount_raw = int(total_price_val)
                        else:
                            amount_raw = int(total_price_val * 100)
                        logger.info(f"💰 Using total_price from crane_details: {amount_raw} cents")
            
            amount = self._convert_amount_to_dollars(amount_raw)
            
            if not amount or amount <= 0:
                # Default amounts if not provided (centralized pricing)
                try:
                    from .fmv_pricing_config import get_base_price_dollars
                    if report_type == 'fleet_valuation':
                        amount_cents = get_base_price_dollars(report_type, unit_count=report_data.get('unit_count') or 1)
                        amount = self._convert_amount_to_dollars(amount_cents)
                    else:
                        amount_cents = get_base_price_dollars(report_type)
                        amount = self._convert_amount_to_dollars(amount_cents)
                except Exception:
                    # Fallback to safe legacy defaults if pricing config is unavailable
                    if report_type == 'spot_check':
                        amount = 250.00
                    elif report_type == 'professional':
                        amount = 995.00
                    elif report_type == 'fleet_valuation':
                        amount = 1495.00  # Default to tier 1-5
            
            template_context = {
                "username": user_name.split()[0] if user_name else "User",
                "user_name": user_name,
                "first_name": first_name,
                "user_email": user_email,
                "report_id": report_data.get('report_id'),
                "report_type": report_type,
                "report_type_display": report_type_display or "FMV Report",
                "amount": amount,
                "amount_display": f"${amount:,.2f}",
                "payment_url": report_data.get('payment_url', f"{settings.frontend_url}/report-generation.html?report_id={report_data.get('report_id')}"),
                "platform_name": settings.app_name,
                "support_email": settings.mail_from_email,
                "dashboard_url": f"{settings.frontend_url}/dashboard.html",
                "created_date": self._format_datetime_with_timezone(datetime.now(ZoneInfo('UTC')), user_timezone)
            }
            
            # Try to use draft created template, fallback to draft reminder template
            template_name = "fmv_report_draft_created.html"
            if not (self.template_dir / template_name).exists():
                template_name = "fmv_report_draft_reminder.html"
            
            result = self.email_service.send_template_email(
                to_emails=[user_email],
                template_name=template_name,
                template_context=template_context,
                subject=f"FMV Report Created - Payment Required - Report #{report_data.get('report_id')}",
                tags=["fmv-report", "draft-created", "payment-required"]
            )
            
            # Also send admin notification
            self._send_admin_notification("draft_created", report_data, user_name, user_email)
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error sending draft created notification: {e}", exc_info=True)
            return False
    
    def send_payment_pending_notification(self, user_email: str, user_name: str, report_data: Dict[str, Any]) -> bool:
        """Send notification when payment is pending (deprecated - use send_draft_reminder_notification)"""
        return self.send_draft_reminder_notification(user_email, user_name, report_data)
    
    def send_paid_notification(self, user_email: str, user_name: str, report_data: Dict[str, Any], user_timezone: Optional[str] = None) -> bool:
        """Send notification when payment is received"""
        if not self.email_service:
            return False
        try:
            first_name = self._extract_first_name(user_name)
            template_context = {
                "username": user_name.split()[0] if user_name else "User",
                "user_name": user_name,
                "first_name": first_name,
                "user_email": user_email,
                "report_id": report_data.get('report_id'),
                "amount": report_data.get('amount', 0),
                "payment_intent_id": report_data.get('payment_intent_id', 'N/A'),
                "payment_date": self._format_datetime_with_timezone(datetime.now(ZoneInfo('UTC')), user_timezone),
                "platform_name": settings.app_name,
                "support_email": settings.mail_from_email,
                "dashboard_url": f"{settings.frontend_url}/dashboard.html"
            }
            
            result = self.email_service.send_template_email(
                to_emails=[user_email],
                template_name="fmv_report_paid.html",
                template_context=template_context,
                subject=f"Payment Received - FMV Report #{report_data.get('report_id')}",
                tags=["fmv-report", "payment-success"]
            )
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error sending paid notification: {e}")
            return False
    
    def send_payment_receipt(self, user_email: str, user_name: str, report_data: Dict[str, Any], user_timezone: Optional[str] = None) -> bool:
        """Send payment receipt email"""
        if not self.email_service:
            return False
        try:
            first_name = self._extract_first_name(user_name)
            template_context = {
                "first_name": first_name,
                "user_name": user_name,
                "user_email": user_email,
                "report_id": report_data.get('report_id'),
                "amount": report_data.get('amount', 0),
                "transaction_id": report_data.get('transaction_id') or report_data.get('payment_intent_id', 'N/A'),
                "payment_date": self._format_datetime_with_timezone(datetime.now(ZoneInfo('UTC')), user_timezone),
                "platform_name": settings.app_name,
                "support_email": settings.mail_from_email,
                "dashboard_url": f"{settings.frontend_url}/dashboard.html"
            }
            
            result = self.email_service.send_template_email(
                to_emails=[user_email],
                template_name="payment_receipt.html",
                template_context=template_context,
                subject=f"Payment Receipt - Report #{report_data.get('report_id')}",
                tags=["payment-receipt", "invoice"]
            )
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error sending payment receipt: {e}")
            return False
    
    def send_in_review_notification(self, user_email: str, user_name: str, report_data: Dict[str, Any], user_timezone: Optional[str] = None) -> bool:
        """Send notification when report enters review"""
        if not self.email_service:
            return False
        try:
            first_name = self._extract_first_name(user_name)
            template_context = {
                "username": user_name.split()[0] if user_name else "User",
                "user_name": user_name,
                "first_name": first_name,
                "user_email": user_email,
                "report_id": report_data.get('report_id'),
                "assigned_analyst": report_data.get('assigned_analyst'),
                "review_date": self._format_datetime_with_timezone(datetime.now(ZoneInfo('UTC')), user_timezone),
                "platform_name": settings.app_name,
                "support_email": settings.mail_from_email,
                "dashboard_url": f"{settings.frontend_url}/dashboard.html"
            }
            
            result = self.email_service.send_template_email(
                to_emails=[user_email],
                template_name="fmv_report_in_review.html",
                template_context=template_context,
                subject=f"FMV Report Under Review - Report #{report_data.get('report_id')}",
                tags=["fmv-report", "in-review"]
            )
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error sending in_review notification: {e}")
            return False
    
    def send_in_progress_notification(self, user_email: str, user_name: str, report_data: Dict[str, Any], user_timezone: Optional[str] = None) -> bool:
        """Send notification when report processing starts"""
        if not self.email_service:
            return False
        try:
            first_name = self._extract_first_name(user_name)
            template_context = {
                "username": user_name.split()[0] if user_name else "User",
                "user_name": user_name,
                "first_name": first_name,
                "user_email": user_email,
                "report_id": report_data.get('report_id'),
                "progress_date": self._format_datetime_with_timezone(datetime.now(ZoneInfo('UTC')), user_timezone),
                "platform_name": settings.app_name,
                "support_email": settings.mail_from_email,
                "dashboard_url": f"{settings.frontend_url}/dashboard.html"
            }
            
            result = self.email_service.send_template_email(
                to_emails=[user_email],
                template_name="fmv_report_in_progress.html",
                template_context=template_context,
                subject=f"FMV Report Processing Started - Report #{report_data.get('report_id')}",
                tags=["fmv-report", "in-progress"]
            )
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error sending in_progress notification: {e}")
            return False
    
    def send_completed_notification(self, user_email: str, user_name: str, report_data: Dict[str, Any], user_timezone: Optional[str] = None) -> bool:
        """Send notification when report is completed"""
        if not self.email_service:
            return False
        try:
            first_name = self._extract_first_name(user_name)
            template_context = {
                "username": user_name.split()[0] if user_name else "User",
                "user_name": user_name,
                "first_name": first_name,
                "user_email": user_email,
                "report_id": report_data.get('report_id'),
                "completed_date": self._format_datetime_with_timezone(datetime.now(ZoneInfo('UTC')), user_timezone),
                "platform_name": settings.app_name,
                "support_email": settings.mail_from_email,
                "dashboard_url": f"{settings.frontend_url}/dashboard.html"
            }
            
            result = self.email_service.send_template_email(
                to_emails=[user_email],
                template_name="fmv_report_completed.html",
                template_context=template_context,
                subject=f"FMV Report Completed - Report #{report_data.get('report_id')}",
                tags=["fmv-report", "completed"]
            )
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error sending completed notification: {e}")
            return False
    
    def send_deleted_notification(self, user_email: str, user_name: str, report_data: Dict[str, Any], user_timezone: Optional[str] = None) -> bool:
        """Send notification when report is deleted"""
        if not self.email_service:
            return False
        try:
            first_name = self._extract_first_name(user_name)
            
            # Format report type for display
            report_type = report_data.get('report_type', '')
            report_type_display = report_data.get('report_type_display')
            if not report_type_display and report_type:
                report_type_display = report_type.replace('_', ' ').title()
            
            # Format crane details
            crane_data = report_data.get('crane_data') or report_data.get('crane_details') or {}
            crane_details = f"{crane_data.get('manufacturer', 'N/A')} {crane_data.get('model', 'N/A')}"
            if crane_data.get('year'):
                crane_details += f" ({crane_data.get('year')})"
            
            template_context = {
                "username": user_name.split()[0] if user_name else "User",
                "user_name": user_name,
                "first_name": first_name,
                "user_email": user_email,
                "report_id": report_data.get('report_id'),
                "report_type": report_type,
                "report_type_display": report_type_display or 'N/A',
                "crane_details": crane_details,
                "deleted_date": self._format_datetime_with_timezone(datetime.now(ZoneInfo('UTC')), user_timezone),
                "platform_name": settings.app_name,
                "support_email": settings.mail_from_email,
                "dashboard_url": f"{settings.frontend_url}/dashboard.html"
            }
            
            result = self.email_service.send_template_email(
                to_emails=[user_email],
                template_name="fmv_report_deleted.html",
                template_context=template_context,
                subject=f"FMV Report Deleted - Report #{report_data.get('report_id')}",
                tags=["fmv-report", "deleted"]
            )
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error sending deleted notification: {e}")
            return False
    
    def send_delivered_notification(self, user_email: str, user_name: str, report_data: Dict[str, Any], user_timezone: Optional[str] = None) -> bool:
        """Send notification when report is delivered"""
        if not self.email_service:
            return False
        try:
            first_name = self._extract_first_name(user_name)
            pdf_url = report_data.get('pdf_url', f"{settings.frontend_url}/reports/{report_data.get('report_id')}")
            
            template_context = {
                "username": user_name.split()[0] if user_name else "User",
                "user_name": user_name,
                "first_name": first_name,
                "user_email": user_email,
                "report_id": report_data.get('report_id'),
                "pdf_url": pdf_url,
                "delivered_date": self._format_datetime_with_timezone(datetime.now(ZoneInfo('UTC')), user_timezone),
                "platform_name": settings.app_name,
                "support_email": settings.mail_from_email,
                "dashboard_url": f"{settings.frontend_url}/dashboard.html"
            }
            
            result = self.email_service.send_template_email(
                to_emails=[user_email],
                template_name="fmv_report_delivered.html",
                template_context=template_context,
                subject=f"Your FMV Report is Ready - Report #{report_data.get('report_id')}",
                tags=["fmv-report", "delivered"]
            )
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error sending delivered notification: {e}")
            return False
    
    def send_need_more_info_notification(self, user_email: str, user_name: str, report_data: Dict[str, Any], user_timezone: Optional[str] = None) -> bool:
        """Send notification when admin needs more information"""
        if not self.email_service:
            return False
        try:
            first_name = self._extract_first_name(user_name)
            need_more_info_reason = report_data.get('need_more_info_reason') or report_data.get('rejection_reason', 'Additional information is required to complete your report.')
            
            # Get report type and format it for display
            report_type = report_data.get('report_type', '')
            report_type_display = report_data.get('report_type_display')
            if not report_type_display and report_type:
                # Format report type for display (e.g., "spot_check" -> "Spot Check")
                report_type_display = report_type.replace('_', ' ').title()
            
            # Extract crane details
            crane_details = report_data.get('crane_details') or {}
            if isinstance(crane_details, str):
                try:
                    import json
                    crane_details = json.loads(crane_details)
                except:
                    crane_details = {}
            
            crane_manufacturer = crane_details.get('manufacturer') or ''
            crane_model = crane_details.get('model') or ''
            crane_year = crane_details.get('year') or ''
            
            # Get amount paid (convert from cents to dollars if needed)
            amount_paid = report_data.get('amount_paid')
            if amount_paid:
                amount_paid = self._convert_amount_to_dollars(amount_paid)
            
            template_context = {
                "username": user_name.split()[0] if user_name else "User",
                "user_name": user_name,
                "first_name": first_name,
                "user_email": user_email,
                "report_id": report_data.get('report_id'),
                "report_type": report_type,
                "report_type_display": report_type_display or "FMV Report",
                "need_more_info_reason": need_more_info_reason,
                "request_date": self._format_datetime_with_timezone(datetime.now(ZoneInfo('UTC')), user_timezone),
                "crane_manufacturer": crane_manufacturer,
                "crane_model": crane_model,
                "crane_year": str(crane_year) if crane_year else '',
                "amount_paid": amount_paid,
                "platform_name": settings.app_name,
                "support_email": settings.mail_from_email,
                "dashboard_url": f"{settings.frontend_url}/dashboard.html"
            }
            
            result = self.email_service.send_template_email(
                to_emails=[user_email],
                template_name="fmv_report_need_more_info.html",
                template_context=template_context,
                subject=f"More Information Needed - FMV Report #{report_data.get('report_id')}",
                tags=["fmv-report", "need-more-info"]
            )
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error sending need more info notification: {e}")
            return False
    
    def send_rejected_notification(self, user_email: str, user_name: str, report_data: Dict[str, Any]) -> bool:
        """Send notification when report is rejected (deprecated - use send_need_more_info_notification)"""
        # Map to need_more_info for backward compatibility
        return self.send_need_more_info_notification(user_email, user_name, report_data)
    
    def send_cancelled_notification(self, user_email: str, user_name: str, report_data: Dict[str, Any], user_timezone: Optional[str] = None) -> bool:
        """Send notification when report is cancelled"""
        if not self.email_service:
            return False
        try:
            first_name = self._extract_first_name(user_name)
            template_context = {
                "username": user_name.split()[0] if user_name else "User",
                "user_name": user_name,
                "first_name": first_name,
                "user_email": user_email,
                "report_id": report_data.get('report_id'),
                "cancelled_date": self._format_datetime_with_timezone(datetime.now(ZoneInfo('UTC')), user_timezone),
                "platform_name": settings.app_name,
                "support_email": settings.mail_from_email,
                "dashboard_url": f"{settings.frontend_url}/dashboard.html"
            }
            
            result = self.email_service.send_template_email(
                to_emails=[user_email],
                template_name="fmv_report_cancelled.html",
                template_context=template_context,
                subject=f"FMV Report Cancelled - Report #{report_data.get('report_id')}",
                tags=["fmv-report", "cancelled"]
            )
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error sending cancelled notification: {e}")
            return False
    
    def _send_admin_notification(self, notification_type: str, report_data: Dict[str, Any], user_name: str, user_email: str) -> bool:
        """Send notification to admin users (internal method)"""
        if not self.email_service:
            return False
        try:
            from ...models.admin import AdminUser
            from ...core.database import SessionLocal
            
            db = SessionLocal()
            try:
                admin_users = db.query(AdminUser).filter(
                    AdminUser.is_active == True,
                    AdminUser.is_verified == True
                ).all()
                
                if not admin_users:
                    return False
                
                admin_emails = [admin.email for admin in admin_users]
                
                template_context = {
                    "notification_type": notification_type.replace('_', ' ').title(),
                    "report_id": report_data.get('report_id'),
                    "user_name": user_name,
                    "user_email": user_email,
                    "report_type": report_data.get('report_type', 'N/A').replace('_', ' ').title(),
                    "status": notification_type,
                    "timestamp": self._format_datetime_with_timezone(datetime.now(ZoneInfo('UTC')), None),  # Admin notifications use UTC for now
                    "platform_name": settings.app_name,
                    "admin_dashboard_url": f"{settings.admin_url}/admin/fmv-reports.html"
                }
                
                result = self.email_service.send_template_email(
                    to_emails=admin_emails,
                    template_name="admin_fmv_report_alert.html",
                    template_context=template_context,
                    subject=f"FMV Report Update: {notification_type.replace('_', ' ').title()} - Report #{report_data.get('report_id')}",
                    tags=["admin-notification", "fmv-report", notification_type]
                )
                
                return result.get("success", False)
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error sending admin notification: {e}")
            return False
    
    def send_overdue_notification(self, admin_emails: List[str], report_data: Dict[str, Any], user_name: str, user_email: str) -> bool:
        """Send OVERDUE notification to admin users only (admin didn't complete within 24 hours)"""
        if not self.email_service:
            return False
        try:
            template_context = {
                "notification_type": "Overdue",
                "report_id": report_data.get('report_id'),
                "user_name": user_name,
                "user_email": user_email,
                "report_type": report_data.get('report_type', 'N/A').replace('_', ' ').title(),
                "submitted_at": report_data.get('submitted_at', 'N/A'),
                "deadline": report_data.get('deadline', 'N/A'),
                "hours_overdue": report_data.get('hours_overdue', 0),
                "timestamp": datetime.now().strftime('%B %d, %Y at %I:%M %p'),
                "platform_name": settings.app_name,
                "admin_dashboard_url": f"{settings.admin_url}/admin/fmv-reports.html"
            }
            
            result = self.email_service.send_template_email(
                to_emails=admin_emails,
                template_name="admin_fmv_report_overdue.html",
                template_context=template_context,
                subject=f"⚠️ OVERDUE: FMV Report #{report_data.get('report_id')} Past 24-Hour Deadline",
                tags=["admin-notification", "fmv-report", "overdue", "urgent"]
            )
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error sending overdue notification: {e}")
            return False
    
    def send_admin_notification(self, admin_emails: List[str], notification_type: str, report_data: Dict[str, Any]) -> bool:
        """Send notification to specific admin users (public method)"""
        if not self.email_service:
            return False
        try:
            template_context = {
                "notification_type": notification_type.replace('_', ' ').title(),
                "report_id": report_data.get('report_id'),
                "user_name": report_data.get('user_name', 'N/A'),
                "user_email": report_data.get('user_email', 'N/A'),
                "report_type": report_data.get('report_type', 'N/A').replace('_', ' ').title(),
                "status": notification_type,
                "timestamp": datetime.now().strftime('%B %d, %Y at %I:%M %p'),
                "platform_name": settings.app_name,
                "admin_dashboard_url": f"{settings.admin_url}/admin/fmv-reports.html"
            }
            
            result = self.email_service.send_template_email(
                to_emails=admin_emails,
                template_name="admin_fmv_report_alert.html",
                template_context=template_context,
                subject=f"FMV Report Update: {notification_type.replace('_', ' ').title()} - Report #{report_data.get('report_id')}",
                tags=["admin-notification", "fmv-report", notification_type]
            )
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error sending admin notification: {e}")
            return False

