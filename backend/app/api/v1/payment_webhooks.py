"""
Stripe Payment Webhook Handler
Handles Stripe webhook events and sends email notifications
"""

import logging
from fastapi import APIRouter, Request, HTTPException, status
from typing import Dict, Any
import stripe

from ...services.stripe_service import StripeService
from ...services.payment_email_service import PaymentEmailService
from ...models.user import User
from ...core.database import get_db, SessionLocal

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payment-webhooks", tags=["Payment Webhooks"])

stripe_service = StripeService()
payment_email_service = PaymentEmailService()


@router.get("/stripe")
async def stripe_webhook_health():
    """
    Health check endpoint for Stripe webhook
    Allows Stripe to verify the endpoint is accessible
    """
    webhook_secret_configured = bool(stripe_service.webhook_secret)
    return {
        "status": "ok",
        "endpoint": "/api/v1/payment-webhooks/stripe",
        "webhook_secret_configured": webhook_secret_configured,
        "message": "Stripe webhook endpoint is active"
    }


@router.post("/stripe")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhook events
    Sends email notifications for payment events
    
    CRITICAL: Always returns 200-299 status codes to Stripe, even on errors.
    Stripe requires successful HTTP status codes (200-299) to consider webhooks delivered.
    """
    try:
        payload = await request.body()
        signature = request.headers.get("stripe-signature")
        
        if not signature:
            logger.error("❌ Stripe webhook: Missing stripe-signature header")
            # Return 200 to Stripe but log the error
            return {"status": "error", "message": "Missing stripe-signature header"}
        
        # Verify webhook signature
        verification_result = stripe_service.verify_webhook_signature(payload, signature)
        
        if not verification_result.get("success"):
            error_msg = verification_result.get("error", "Invalid webhook signature")
            logger.error(f"❌ Stripe webhook signature verification failed: {error_msg}")
            # Return 200 to Stripe but log the error
            return {"status": "error", "message": error_msg}
        
        event = verification_result.get("event")
        if not event:
            logger.error("❌ Stripe webhook: No event data after verification")
            return {"status": "error", "message": "No event data"}
        
        event_type = event.get("type")
        event_data = event.get("data", {}).get("object", {})
        
        logger.info(f"✅ Received Stripe webhook: {event_type} (ID: {event.get('id', 'unknown')})")
        
        # Handle different event types
        db = SessionLocal()
        try:
            if event_type == "payment_intent.created":
                await _handle_payment_intent_created(event_data, db)
            elif event_type == "payment_intent.succeeded":
                await _handle_payment_intent_succeeded(event_data, db)
            elif event_type == "payment_intent.payment_failed":
                await _handle_payment_intent_failed(event_data, db)
            elif event_type == "payment_intent.canceled":
                await _handle_payment_intent_cancelled(event_data, db)
            elif event_type == "charge.refunded":
                await _handle_charge_refunded(event_data, db)
            elif event_type == "invoice.payment_succeeded":
                await _handle_invoice_payment_succeeded(event_data, db)
            elif event_type == "invoice.payment_failed":
                await _handle_invoice_payment_failed(event_data, db)
            else:
                logger.info(f"ℹ️ Unhandled webhook event type: {event_type}")
            
            logger.info(f"✅ Successfully processed Stripe webhook: {event_type}")
            return {"status": "success", "event_type": event_type}
        except Exception as handler_error:
            # Log the error but still return 200 to Stripe
            logger.error(f"❌ Error handling webhook event {event_type}: {handler_error}", exc_info=True)
            return {"status": "error", "message": f"Error processing {event_type}: {str(handler_error)}"}
        finally:
            db.close()
            
    except Exception as e:
        # CRITICAL: Always return 200 status to Stripe, even on unexpected errors
        # This prevents Stripe from disabling the webhook endpoint
        logger.error(f"❌ Unexpected error processing Stripe webhook: {e}", exc_info=True)
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}


async def _handle_payment_intent_created(event_data: Dict[str, Any], db):
    """Handle payment_intent.created event"""
    try:
        user_email = event_data.get("receipt_email") or event_data.get("metadata", {}).get("user_email")
        if not user_email:
            return
        
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            return
        
        payment_email_service.send_payment_initiated_notification(
            user_email=user.email,
            user_name=user.full_name,
            payment_data={
                "amount": event_data.get("amount"),
                "payment_intent_id": event_data.get("id"),
                "description": event_data.get("description", "Payment")
            }
        )
    except Exception as e:
        logger.error(f"Error handling payment_intent.created: {e}")


async def _handle_payment_intent_succeeded(event_data: Dict[str, Any], db):
    """Handle payment_intent.succeeded event - Update FMV report status and send notifications"""
    try:
        payment_intent_id = event_data.get("id")
        if not payment_intent_id:
            logger.warning("Payment intent ID not found in webhook event")
            return
        
        # Get amount from payment intent (Stripe returns in cents)
        amount_cents = event_data.get("amount") or event_data.get("amount_received", 0)
        amount_dollars = amount_cents / 100.0
        
        # Find the FMV report associated with this payment intent
        from ...models.fmv_report import FMVReport
        from ...services.fmv_report_service import FMVReportService
        from ...services.fmv_email_service import FMVEmailService
        
        report = db.query(FMVReport).filter(FMVReport.payment_intent_id == payment_intent_id).first()
        
        if report:
            # Report found - update status and send notifications
            logger.info(f"✅ Found report {report.id} for payment intent {payment_intent_id}")
            
            service = FMVReportService(db)
            
            # Mark payment as received (this updates status from DRAFT to SUBMITTED)
            try:
                updated_report = service.mark_payment_received(report.id, payment_intent_id, amount_dollars)
                logger.info(f"✅ Payment marked as received for report {updated_report.id}, status: {updated_report.status.value}")
                
                # Get user for notifications
                user = db.query(User).filter(User.id == updated_report.user_id).first()
                
                if user:
                    # Send FMV report-specific notifications
                    email_service = FMVEmailService()
                    
                    # Send SUBMITTED notification (report submitted successfully)
                    # NOTE: This email already includes the PDF receipt attachment; we do NOT send a separate Payment Receipt email.
                    try:
                        email_service.send_submitted_notification(
                            user_email=user.email,
                            user_name=user.full_name,
                            report_data={
                                "report_id": updated_report.id,
                                "report_type": updated_report.report_type.value if hasattr(updated_report.report_type, 'value') else str(updated_report.report_type),
                                "amount": amount_dollars,
                                "payment_intent_id": payment_intent_id
                            }
                        )
                        logger.info(f"✅ Sent submission notification for report {updated_report.id}")
                    except Exception as email_error:
                        logger.error(f"❌ Failed to send submission notification: {email_error}")
                    
                    # Create user notification in database
                    try:
                        from ...models.notification import UserNotification
                        user_notification = UserNotification(
                            user_id=user.id,
                            title=f"FMV Report #{updated_report.id} Submitted",
                            message=f"Your FMV Report #{updated_report.id} has been submitted successfully. Payment received: ${amount_dollars:,.2f}",
                            type="fmv_report_submitted",
                            read=False
                        )
                        db.add(user_notification)
                        db.commit()
                        logger.info(f"✅ Created user notification for report {updated_report.id}")
                    except Exception as notif_error:
                        logger.warning(f"⚠️ Failed to create user notification: {notif_error}")
                        db.rollback()
                else:
                    logger.warning(f"⚠️ User not found for report {updated_report.id}")
                    
            except Exception as update_error:
                logger.error(f"❌ Failed to mark payment received for report {report.id}: {update_error}", exc_info=True)
        else:
            # No report found - might be a subscription payment or other payment type
            # Send generic payment success notification
            logger.info(f"ℹ️ No FMV report found for payment intent {payment_intent_id}, sending generic payment notification")
            
            user_email = event_data.get("receipt_email") or event_data.get("metadata", {}).get("user_email")
            if user_email:
                user = db.query(User).filter(User.email == user_email).first()
                if user:
                    payment_email_service.send_payment_success_notification(
                        user_email=user.email,
                        user_name=user.full_name,
                        payment_data={
                            "amount": amount_cents,
                            "payment_intent_id": payment_intent_id,
                            "charge_id": event_data.get("charges", {}).get("data", [{}])[0].get("id") if event_data.get("charges") else None,
                            "description": event_data.get("description", "Payment")
                        }
                    )
    except Exception as e:
        logger.error(f"Error handling payment_intent.succeeded: {e}", exc_info=True)


async def _handle_payment_intent_failed(event_data: Dict[str, Any], db):
    """Handle payment_intent.payment_failed event"""
    try:
        user_email = event_data.get("receipt_email") or event_data.get("metadata", {}).get("user_email")
        if not user_email:
            return
        
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            return
        
        last_payment_error = event_data.get("last_payment_error", {})
        payment_email_service.send_payment_failed_notification(
            user_email=user.email,
            user_name=user.full_name,
            payment_data={
                "amount": event_data.get("amount"),
                "payment_intent_id": event_data.get("id"),
                "error_message": last_payment_error.get("message", "Payment could not be processed")
            }
        )
    except Exception as e:
        logger.error(f"Error handling payment_intent.payment_failed: {e}")


async def _handle_payment_intent_cancelled(event_data: Dict[str, Any], db):
    """Handle payment_intent.canceled event"""
    try:
        user_email = event_data.get("receipt_email") or event_data.get("metadata", {}).get("user_email")
        if not user_email:
            return
        
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            return
        
        payment_email_service.send_payment_cancelled_notification(
            user_email=user.email,
            user_name=user.full_name,
            payment_data={
                "amount": event_data.get("amount"),
                "payment_intent_id": event_data.get("id")
            }
        )
    except Exception as e:
        logger.error(f"Error handling payment_intent.canceled: {e}")


async def _handle_charge_refunded(event_data: Dict[str, Any], db):
    """Handle charge.refunded event"""
    try:
        user_email = event_data.get("receipt_email") or event_data.get("metadata", {}).get("user_email")
        if not user_email:
            return
        
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            return
        
        refunds = event_data.get("refunds", {}).get("data", [])
        latest_refund = refunds[0] if refunds else {}
        
        payment_email_service.send_payment_refunded_notification(
            user_email=user.email,
            user_name=user.full_name,
            payment_data={
                "amount": event_data.get("amount"),
                "refund_amount": latest_refund.get("amount"),
                "charge_id": event_data.get("id"),
                "refund_id": latest_refund.get("id")
            }
        )
    except Exception as e:
        logger.error(f"Error handling charge.refunded: {e}")


async def _handle_invoice_payment_succeeded(event_data: Dict[str, Any], db):
    """Handle invoice.payment_succeeded event"""
    try:
        customer_email = event_data.get("customer_email")
        if not customer_email:
            return
        
        user = db.query(User).filter(User.email == customer_email).first()
        if not user:
            return
        
        payment_email_service.send_subscription_payment_success_notification(
            user_email=user.email,
            user_name=user.full_name,
            payment_data={
                "amount": event_data.get("amount_paid"),
                "invoice_id": event_data.get("id"),
                "subscription_id": event_data.get("subscription"),
                "billing_period": "Monthly",  # Could be extracted from subscription
                "next_billing_date": event_data.get("lines", {}).get("data", [{}])[0].get("period", {}).get("end")
            }
        )
    except Exception as e:
        logger.error(f"Error handling invoice.payment_succeeded: {e}")


async def _handle_invoice_payment_failed(event_data: Dict[str, Any], db):
    """Handle invoice.payment_failed event"""
    try:
        customer_email = event_data.get("customer_email")
        if not customer_email:
            return
        
        user = db.query(User).filter(User.email == customer_email).first()
        if not user:
            return
        
        payment_email_service.send_subscription_payment_failed_notification(
            user_email=user.email,
            user_name=user.full_name,
            payment_data={
                "amount": event_data.get("amount_due"),
                "invoice_id": event_data.get("id"),
                "subscription_id": event_data.get("subscription"),
                "error_message": event_data.get("last_payment_error", {}).get("message", "Payment could not be processed")
            }
        )
    except Exception as e:
        logger.error(f"Error handling invoice.payment_failed: {e}")

