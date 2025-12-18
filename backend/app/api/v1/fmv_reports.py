"""
FMV Reports API Endpoints
Handles FMV report submission, retrieval, and status management
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session
from datetime import datetime

from ...core.database import get_db
from ...core.config import settings
from ...api.v1.auth import get_current_user
from ...services.fmv_report_service import FMVReportService
from ...services.fmv_email_service import FMVEmailService
from ...services.fallback_request_service import FallbackRequestService
from ...schemas.fallback_request import FallbackRequestCreate, FallbackRequestResponse, FallbackRequestUpdate
from ...models.fallback_request import FallbackRequest
from ...services.stripe_service import StripeService
from ...services.storage_service import get_storage_service
from ...schemas.fmv_report import (
    FMVReportCreate, FMVReportResponse, StatusTransition, FMVReportUpdate,
    FMVReportTimelineResponse, FMVReportTimelineItem
)
from pydantic import BaseModel
from ...models.fmv_report import FMVReport, FMVReportStatus
from ...models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/fmv-reports", tags=["FMV Reports"])

from fastapi.responses import Response


# Request models
class FleetPricingRequest(BaseModel):
    """Request model for Fleet Valuation pricing calculation"""
    unit_count: int  # Number of cranes (1-50)
class CreatePaymentRequest(BaseModel):
    report_type: str
    amount: int  # Amount in cents
    crane_data: Dict[str, Any] = {}
    cardholder_name: str = ""
    receipt_email: str = ""
    metadata: Optional[Dict[str, Any]] = None  # Optional metadata from frontend


class PaymentReceivedRequest(BaseModel):
    payment_intent_id: str
    amount: float

# Initialize services (lazy initialization to avoid import errors)
_fmv_email_service = None
_stripe_service = None

def get_fmv_email_service():
    """Get or create FMV email service instance"""
    global _fmv_email_service
    if _fmv_email_service is None:
        try:
            _fmv_email_service = FMVEmailService()
        except Exception as e:
            logger.warning(f"Failed to initialize FMV email service: {e}")
            _fmv_email_service = None
    return _fmv_email_service

def get_stripe_service():
    """Get or create Stripe service instance"""
    global _stripe_service
    if _stripe_service is None:
        try:
            _stripe_service = StripeService()
        except Exception as e:
            logger.warning(f"Failed to initialize Stripe service: {e}")
            _stripe_service = None
    return _stripe_service


def convert_report_to_response(report: FMVReport) -> FMVReportResponse:
    """Convert FMVReport model to response schema, handling enum conversions"""
    report_dict = {
        "id": report.id,
        "user_id": report.user_id,
        "report_type": report.report_type.value if hasattr(report.report_type, 'value') else str(report.report_type),
        "status": report.status.value if hasattr(report.status, 'value') else str(report.status),
        "crane_details": report.crane_details,
        "service_records": report.service_records,
        "service_record_files": report.service_record_files if hasattr(report, 'service_record_files') else None,
        "fleet_pricing_tier": report.fleet_pricing_tier.value if report.fleet_pricing_tier and hasattr(report.fleet_pricing_tier, 'value') else (str(report.fleet_pricing_tier) if report.fleet_pricing_tier else None),
        "unit_count": report.unit_count,
        "amount_paid": report.amount_paid,
        "payment_intent_id": report.payment_intent_id,
        "payment_status": report.payment_status,
        "created_at": report.created_at,
        "submitted_at": report.submitted_at,
        "paid_at": report.paid_at,
        "in_progress_at": report.in_progress_at,
        "completed_at": report.completed_at,
        "delivered_at": report.delivered_at,
        "overdue_at": getattr(report, 'overdue_at', None),
        "rejected_at": getattr(report, 'rejected_at', None),
        "cancelled_at": getattr(report, 'cancelled_at', None),
        "turnaround_deadline": getattr(report, 'turnaround_deadline', None),
        "pdf_url": getattr(report, 'pdf_url', None),
        "pdf_uploaded_at": getattr(report, 'pdf_uploaded_at', None),
        "analyst_notes": getattr(report, 'analyst_notes', None),
        "rejection_reason": getattr(report, 'rejection_reason', None),
        "assigned_analyst": getattr(report, 'assigned_analyst', None),
        "metadata": getattr(report, 'report_metadata', None) if hasattr(report, 'report_metadata') else None,  # Use renamed attribute
        "updated_at": getattr(report, 'updated_at', None)
    }
    return FMVReportResponse(**report_dict)


# CRITICAL: These endpoints MUST be defined FIRST, before ANY other routes
# FastAPI matches routes in order, and parameterized routes like /{report_id} will match /create-payment
# if defined before this specific route
# IMPORTANT: /submit MUST be defined before /{report_id} routes to avoid route conflicts

@router.get("/calculate-fleet-price")
async def calculate_fleet_price(
    unit_count: int,
    db: Session = Depends(get_db)
):
    """Calculate Fleet Valuation price based on unit count"""
    try:
        # Note: FMVReportService is already imported at top of file
        service = FMVReportService(db)
        
        if unit_count < 1 or unit_count > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Fleet Valuation supports 1-50 cranes"
            )
        
        price, tier = service.calculate_fleet_price_by_units(unit_count)
        per_crane = service.get_per_crane_cost(unit_count)
        
        return {
            "success": True,
            "unit_count": unit_count,
            "price": price,
            "price_cents": int(price * 100),
            "tier": tier.value if hasattr(tier, 'value') else str(tier),
            "per_crane_cost": per_crane
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error calculating fleet price: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate fleet price: {str(e)}"
        )

@router.post("/payment-by-intent")
async def mark_payment_received_by_intent(
    payment_data: PaymentReceivedRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Mark payment as received by payment intent ID (finds report automatically) - MUST be before /{report_id}/payment"""
    try:
        service = FMVReportService(db)
        
        # First, try to find report by payment_intent_id
        report = service.get_report_by_payment_intent(payment_data.payment_intent_id)
        
        if not report:
            # If not found, try to find the most recent draft report for the user
            # This handles cases where report was created but payment_intent_id wasn't set yet
            try:
                from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
                security = HTTPBearer(auto_error=False)
                credentials = await security(request)
                if credentials:
                    current_user = await get_current_user(credentials)
                    user_id = int(current_user.get("sub"))
                    # Get user's most recent draft report
                    user_reports = service.get_user_reports(user_id, "draft")
                    if user_reports:
                        # Sort by created_at descending and get the most recent
                        user_reports.sort(key=lambda r: r.created_at, reverse=True)
                        report = user_reports[0]
                        logger.info(f"Found draft report {report.id} for user {user_id} to associate with payment")
            except:
                pass
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report not found for payment intent {payment_data.payment_intent_id}"
            )
        
        # Mark payment received (this will upgrade user tier if needed)
        report = service.mark_payment_received(report.id, payment_data.payment_intent_id, payment_data.amount)
        
        # Get user for notification
        user = db.query(User).filter(User.id == report.user_id).first()
        
        logger.info(f"✅ Payment marked as received for report {report.id} via payment intent: ${payment_data.amount}, status updated to {report.status.value}")
        
        # Send SUBMITTED notification (payment successful, report submitted)
        try:
            if user:
                email_service = get_fmv_email_service()
                if email_service:
                    # Send SUBMITTED notification (form filled, payment successful)
                    # NOTE: This email already includes the PDF receipt as an attachment,
                    # so we do NOT send a separate Payment Receipt email.
                    email_service.send_submitted_notification(
                        user_email=user.email,
                        user_name=user.full_name,
                        report_data={
                            "report_id": report.id,
                            "report_type": report.report_type.value if hasattr(report.report_type, 'value') else str(report.report_type),
                            "amount": payment_data.amount,
                            "payment_intent_id": payment_data.payment_intent_id
                        }
                    )
                    
                    # Create user notification (single notification for payment success)
                    try:
                        from ...models.notification import UserNotification
                        user_notification = UserNotification(
                            user_id=user.id,
                            title=f"Payment Successful - Report #{report.id}",
                            message=f"Your payment of ${payment_data.amount:,.2f} for FMV Report #{report.id} has been received. Your report has been submitted successfully.",
                            type="payment_success",
                            read=False
                        )
                        db.add(user_notification)
                        db.commit()
                        logger.info(f"✅ User notification created for successful payment on report {report.id}")
                    except Exception as notif_error:
                        logger.warning(f"Failed to create user notification: {notif_error}")
                        db.rollback()
        except Exception as e:
            logger.error(f"Error sending paid notification: {e}")
        
        # Return report
        response = convert_report_to_response(report)
        return response.dict()
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"ValueError marking payment by intent: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error marking payment by intent: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark payment: {str(e)}"
        )


@router.post("/create-payment", status_code=status.HTTP_200_OK)
async def create_fmv_payment(
    request_data: CreatePaymentRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a payment intent for FMV report purchase (authentication optional)
    Also creates a DRAFT report if one doesn't exist (identified by draft_report_id in metadata)"""
    logger.info(f"Received payment creation request: report_type={request_data.report_type}, amount={request_data.amount}")
    try:
        # Try to get current_user from token if provided
        current_user = None
        try:
            from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
            security = HTTPBearer(auto_error=False)
            credentials = await security(request)
            if credentials:
                current_user = await get_current_user(credentials)
        except:
            pass
        
        report_type = request_data.report_type
        amount = request_data.amount  # Amount in cents
        crane_data = request_data.crane_data or {}
        cardholder_name = request_data.cardholder_name or ""
        receipt_email = request_data.receipt_email or ""
        
        if not report_type or not amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="report_type and amount are required"
            )
        
        # Check if a draft_report_id is provided in metadata
        frontend_metadata = request_data.metadata or {}
        draft_report_id = frontend_metadata.get('draft_report_id') or frontend_metadata.get('report_id')
        
        # Initialize draft_report_id to None if not provided
        if draft_report_id:
            try:
                draft_report_id = int(draft_report_id)
            except (ValueError, TypeError):
                draft_report_id = None
        
        # If no draft report exists, create one now
        if not draft_report_id:
            try:
                # Get user_id from authenticated user or find by email
                user_id = None
                user_email = receipt_email or (current_user.get("email") if current_user else None)
                
                # Also check metadata for user_email (from frontend)
                if not user_email and frontend_metadata:
                    user_email = frontend_metadata.get('user_email') or frontend_metadata.get('receipt_email')
                
                if current_user:
                    try:
                        user_id = int(current_user.get("sub"))
                        if not user_email:
                            user_email = current_user.get("email")
                        logger.info(f"✅ Got user_id from token: {user_id}, email: {user_email}")
                    except:
                        pass
                
                # Try to find user by email (case-insensitive)
                if not user_id and user_email:
                    # Try exact match first
                    user = db.query(User).filter(User.email == user_email).first()
                    if not user:
                        # Try case-insensitive match
                        user = db.query(User).filter(User.email.ilike(user_email)).first()
                    if user:
                        user_id = user.id
                        logger.info(f"✅ Found user {user_id} by email {user_email}")
                    else:
                        logger.warning(f"⚠️ User not found by email: {user_email}")
                
                # CRITICAL: If user_id is still not found, log detailed error but continue
                # The draft will be created with user_email in metadata, and can be linked later
                if not user_id:
                    logger.error(f"❌ Cannot create DRAFT report: user_id not found. current_user={current_user}, user_email={user_email}, receipt_email={receipt_email}, metadata={frontend_metadata}")
                    # Still try to create draft if we have user_email - will need to link user later
                    if not user_email:
                        logger.error(f"❌ Cannot create DRAFT report: no user_email available")
                        # Don't fail - payment intent can still be created, but log the error
                    else:
                        # Try one more time to find user - maybe email format issue
                        # Try with trimmed and lowercased email
                        email_variants = [
                            user_email.strip(),
                            user_email.strip().lower(),
                            user_email.strip().upper(),
                        ]
                        for email_variant in email_variants:
                            user = db.query(User).filter(User.email.ilike(email_variant)).first()
                            if user:
                                user_id = user.id
                                logger.info(f"✅ Found user {user_id} by email variant: {email_variant}")
                                break
                
                if user_id:
                    # Create DRAFT report
                    # Note: FMVReportService is already imported at top of file
                    from ...schemas.fmv_report import FMVReportCreate, CraneDetails
                    service = FMVReportService(db)
                    
                    # Build crane_details from crane_data
                    crane_details = CraneDetails(
                        manufacturer=crane_data.get("manufacturer", ""),
                        model=crane_data.get("model", ""),
                        year=crane_data.get("year"),
                        capacity=crane_data.get("capacity"),
                        operatingHours=crane_data.get("operatingHours", crane_data.get("hours", 0)),
                        region=crane_data.get("region", ""),
                        craneType=crane_data.get("craneType", crane_data.get("crane_type", ""))
                    )
                    
                    # Create report data
                    report_create = FMVReportCreate(
                        report_type=report_type,
                        crane_details=crane_details,
                        metadata={
                            "user_email": user_email,
                            "cardholder_name": cardholder_name,
                            "receipt_email": receipt_email
                        }
                    )
                    
                    # Create the DRAFT report
                    logger.info(f"🔄 Creating DRAFT report for user {user_id} in /create-payment endpoint...")
                    draft_report = service.create_report(user_id, report_create)
                    draft_report_id = draft_report.id
                    
                    # CRITICAL: Ensure the report is committed to database
                    db.commit()
                    db.refresh(draft_report)
                    
                    logger.info(f"✅ Created DRAFT report {draft_report_id} before payment intent creation for user {user_id}. Status: {draft_report.status.value}")
                elif user_email:
                    # CRITICAL: Even without user_id, try to create draft with email in metadata
                    # This ensures draft exists even if user lookup fails
                    logger.warning(f"⚠️ Creating DRAFT report without user_id (user lookup failed), using email: {user_email}")
                    try:
                        from ...schemas.fmv_report import FMVReportCreate, CraneDetails
                        service = FMVReportService(db)
                        
                        # Build crane_details from crane_data
                        crane_details = CraneDetails(
                            manufacturer=crane_data.get("manufacturer", ""),
                            model=crane_data.get("model", ""),
                            year=crane_data.get("year"),
                            capacity=crane_data.get("capacity"),
                            operatingHours=crane_data.get("operatingHours", crane_data.get("hours", 0)),
                            region=crane_data.get("region", ""),
                            craneType=crane_data.get("craneType", crane_data.get("crane_type", ""))
                        )
                        
                        # Create report data with user_email in metadata
                        report_create = FMVReportCreate(
                            report_type=report_type,
                            crane_details=crane_details,
                            metadata={
                                "user_email": user_email,
                                "cardholder_name": cardholder_name,
                                "receipt_email": receipt_email,
                                "user_id_missing": True,  # Flag to indicate user needs to be linked later
                                "created_via": "create-payment-endpoint"
                            }
                        )
                        
                        # Try to find user one more time before creating
                        # If still not found, we'll need to handle this differently
                        # For now, we'll skip creating the draft if user_id is absolutely required
                        logger.error(f"❌ Cannot create DRAFT report without user_id. User email {user_email} not found in database. Please ensure user exists before creating report.")
                        # Note: We're not creating the draft here because create_report requires user_id
                        # This is a limitation we need to address
                    except Exception as draft_error:
                        logger.error(f"❌ Failed to prepare DRAFT report creation: {draft_error}", exc_info=True)
                else:
                    logger.error(f"❌ Cannot create DRAFT report: user_id not found and no user_email available. current_user={current_user}, receipt_email={receipt_email}")
                    # Don't fail - payment intent can still be created, but log the error
            except Exception as create_error:
                logger.error(f"❌ Failed to create DRAFT report before payment: {create_error}", exc_info=True)
                # Continue anyway - payment intent can still be created
        
        # Create metadata for payment intent - use frontend metadata if provided, otherwise build from crane_data
        frontend_metadata = request_data.metadata or {}
        if frontend_metadata:
            # Use metadata from frontend if provided
            metadata = {str(k): str(v) if v is not None else "" for k, v in frontend_metadata.items()}
        else:
            # Build metadata from crane_data
            metadata = {
                "report_type": report_type,
                "crane_manufacturer": crane_data.get("manufacturer", ""),
                "crane_model": crane_data.get("model", ""),
                "crane_year": str(crane_data.get("year", "")),
                "crane_capacity": str(crane_data.get("capacity", "")),
                "crane_hours": str(crane_data.get("operatingHours", crane_data.get("hours", ""))),
                "crane_region": crane_data.get("region", ""),
                "crane_type": crane_data.get("craneType", crane_data.get("crane_type", "")),
                "user_email": receipt_email or (current_user.get("email") if current_user else ""),
                "cardholder_name": cardholder_name
            }
            # Ensure all metadata values are strings (Stripe requirement)
            metadata = {k: str(v) if v is not None else "" for k, v in metadata.items()}
        
        # CRITICAL: Add report_id to metadata if we have a draft_report_id
        # This ensures the payment can be linked to the correct report
        if draft_report_id:
            metadata["report_id"] = str(draft_report_id)
            metadata["draft_report_id"] = str(draft_report_id)
            logger.info(f"✅ Added report_id {draft_report_id} to payment intent metadata")
        
        # Create payment intent using Stripe service
        stripe = get_stripe_service()
        if not stripe:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Payment service unavailable"
            )
        result = stripe.create_payment_intent(
            amount=amount,
            currency="usd",
            metadata=metadata,
            description=f"FMV Report - {report_type} - {crane_data.get('manufacturer', '')} {crane_data.get('model', '')}"
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to create payment intent")
            )
        
        # Link payment_intent_id to DRAFT report if we created one
        payment_intent_id = result.get("payment_intent_id")
        if draft_report_id and payment_intent_id:
            try:
                # Note: FMVReportService is already imported at top of file
                service = FMVReportService(db)
                report = db.query(FMVReport).filter(FMVReport.id == draft_report_id).first()
                if report:
                    report.payment_intent_id = payment_intent_id
                    db.commit()
                    db.refresh(report)
                    logger.info(f"✅ Linked payment_intent_id {payment_intent_id} to DRAFT report {draft_report_id}")
            except Exception as link_error:
                logger.warning(f"⚠️ Failed to link payment_intent_id to report: {link_error}")
                # Continue anyway - payment can still proceed
        
        # Generate a transaction ID (can be improved with proper transaction tracking)
        import uuid
        transaction_id = str(uuid.uuid4())[:8].upper()
        
        logger.info(f"Payment intent created successfully: payment_intent_id={payment_intent_id}, transaction_id={transaction_id}, draft_report_id={draft_report_id}")
        
        response_data = {
            "success": True,
            "client_secret": result.get("client_secret"),
            "payment_intent_id": payment_intent_id,
            "transaction_id": transaction_id,
            "amount": result.get("amount"),
            "currency": result.get("currency")
        }
        
        # Include draft_report_id in response if we created one
        if draft_report_id:
            response_data["draft_report_id"] = draft_report_id
        
        return response_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating payment intent: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create payment intent: {str(e)}"
        )


# CRITICAL: /submit endpoint MUST be defined here, before any parameterized routes like /{report_id}
# FastAPI matches routes in order, so this specific route must come before parameterized ones
@router.post("/submit", response_model=FMVReportResponse, status_code=status.HTTP_201_CREATED)
async def submit_fmv_report(
    report_data: FMVReportCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Submit a new FMV report request - Creates DRAFT report immediately when purchase button is clicked"""
    logger.info(f"📥 Received /submit request: report_type={report_data.report_type if hasattr(report_data, 'report_type') else 'unknown'}")
    try:
        # Try to get current_user from token if provided
        current_user = None
        try:
            from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
            security = HTTPBearer(auto_error=False)
            credentials = await security(request)
            if credentials:
                current_user = await get_current_user(credentials)
                logger.info(f"✅ User authenticated: {current_user.get('email') if current_user else 'None'}")
        except Exception as auth_error:
            logger.warning(f"⚠️ Authentication check failed: {auth_error}")
            pass
        
        # Try to get user_id from authenticated user, or from email in report_data
        user_id = None
        user_email = None
        
        if current_user:
            try:
                user_id = int(current_user.get("sub"))
                user_email = current_user.get("email")
                logger.info(f"✅ Got user_id from token: {user_id}, email: {user_email}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to extract user_id from token: {e}")
                pass
        
        if not user_id:
            # If not authenticated, try to find user by email from metadata
            # This allows unauthenticated users to submit reports after payment
            if report_data.metadata and isinstance(report_data.metadata, dict):
                user_email = report_data.metadata.get('user_email') or report_data.metadata.get('receipt_email')
                logger.info(f"🔍 Looking up user by email from metadata: {user_email}")
            if user_email:
                # Try exact match first
                user = db.query(User).filter(User.email == user_email).first()
                if not user:
                    # Try case-insensitive match
                    user = db.query(User).filter(User.email.ilike(user_email)).first()
                if user:
                    user_id = user.id
                    logger.info(f"✅ Found user by email: {user_id}")
                else:
                    logger.warning(f"⚠️ User not found by email: {user_email}")
                    # Try email variants
                    email_variants = [
                        user_email.strip(),
                        user_email.strip().lower(),
                        user_email.strip().upper(),
                    ]
                    for email_variant in email_variants:
                        user = db.query(User).filter(User.email.ilike(email_variant)).first()
                        if user:
                            user_id = user.id
                            logger.info(f"✅ Found user by email variant: {email_variant}, user_id: {user_id}")
                            break
        
        if not user_id:
            # LAST RESORT: Try to get user_email from metadata even if it wasn't found earlier
            if not user_email and report_data.metadata and isinstance(report_data.metadata, dict):
                user_email = report_data.metadata.get('user_email') or report_data.metadata.get('receipt_email')
                if user_email:
                    user = db.query(User).filter(User.email == user_email).first()
                    if user:
                        user_id = user.id
                        logger.info(f"✅ Found user by email (last resort): {user_id}")
            
            if not user_id:
                # FINAL ATTEMPT: If we have current_user but couldn't extract user_id, try to query by email from current_user
                if current_user and current_user.get("email"):
                    user_email_from_token = current_user.get("email")
                    user = db.query(User).filter(User.email == user_email_from_token).first()
                    if user:
                        user_id = user.id
                        logger.info(f"✅ Found user by email from token (final attempt): {user_id}")
            
            if not user_id:
                # Final attempt: Check if user_email exists and try one more lookup with all variants
                if user_email:
                    # Try all possible email formats
                    email_variants = [
                        user_email.strip(),
                        user_email.strip().lower(),
                        user_email.strip().upper(),
                        user_email.strip().replace(' ', ''),
                    ]
                    for email_variant in email_variants:
                        if email_variant:
                            user = db.query(User).filter(User.email.ilike(email_variant)).first()
                            if user:
                                user_id = user.id
                                logger.info(f"✅ Found user {user_id} by email variant (final attempt): {email_variant}")
                                break
                
                if not user_id:
                    # Log detailed error for debugging
                    logger.error(f"❌ Cannot create DRAFT report: user_id not found after all attempts.")
                    logger.error(f"   current_user: {current_user}")
                    logger.error(f"   user_email: {user_email}")
                    logger.error(f"   metadata: {report_data.metadata if hasattr(report_data, 'metadata') else 'N/A'}")
                    
                    # If we have user_email but user doesn't exist, this is a data integrity issue
                    if user_email:
                        # Check if any user exists with similar email
                        similar_users = db.query(User).filter(User.email.ilike(f'%{user_email.split("@")[0]}%')).limit(5).all()
                        if similar_users:
                            logger.error(f"   Found {len(similar_users)} users with similar email pattern:")
                            for u in similar_users:
                                logger.error(f"     - ID={u.id}, Email={u.email}")
                        else:
                            logger.error(f"   No users found with similar email pattern")
                    
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"User authentication required. User with email '{user_email}' not found in database. Please ensure you are logged in with a valid account."
                    )
        
        # Create service instance (FMVReportService is imported at top of file)
        service = FMVReportService(db)
        
        # Create report (will be created as DRAFT status)
        logger.info(f"🔄 Creating DRAFT report for user {user_id}...")
        try:
            report = service.create_report(user_id, report_data)
            logger.info(f"✅ Created DRAFT report {report.id} for user {user_id} via /submit endpoint. Status: {report.status.value}")
            
            # CRITICAL: Ensure the report is committed to database
            db.commit()
            db.refresh(report)
            
            logger.info(f"✅ DRAFT report {report.id} committed to database successfully")
        except Exception as db_error:
            # Rollback on error
            db.rollback()
            logger.error(f"❌ Database error creating DRAFT report: {db_error}", exc_info=True)
            # Re-raise to return proper error to client
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Database connection failed. Please try again in a moment. Error: {str(db_error)}"
            )
        
        # Convert to response
        response = convert_report_to_response(report)
        
        # CRITICAL: Only send DRAFT reminder email, NOT submitted notification
        # DRAFT reports should only receive draft reminder emails asking to complete payment
        # Submitted notification should only be sent when payment is received (status = SUBMITTED)
        try:
            # Ensure we have user_email - get from user object if not already set
            if not user_email:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    user_email = user.email
                    logger.info(f"✅ Retrieved user_email from database: {user_email}")
            
            email_service = get_fmv_email_service()
            if email_service and user_email and report.status == FMVReportStatus.DRAFT:
                # Get user for name
                user = db.query(User).filter(User.id == user_id).first()
                user_name = user.full_name if user and user.full_name else (current_user.get("full_name", "User") if current_user else "User")
                
                # Determine report price based on type
                report_type_value = report.report_type.value if hasattr(report.report_type, 'value') else str(report.report_type)
                if report_type_value == 'spot_check':
                    amount = 495.00
                elif report_type_value == 'professional':
                    amount = 995.00
                elif report_type_value == 'fleet_valuation':
                    # Use fleet pricing if available
                    # Note: FMVReportService is already imported at top of file
                    fleet_service = FMVReportService(db)
                    if report.fleet_pricing_tier:
                        amount = fleet_service.calculate_fleet_price(report.fleet_pricing_tier)
                    else:
                        amount = 1495.00  # Default tier 1-5
                else:
                    amount = 995.00  # Default (professional)
                
                # Send DRAFT reminder email
                email_result = email_service.send_draft_reminder_notification(
                    user_email=user_email,
                    user_name=user_name,
                    report_data={
                        "report_id": report.id,
                        "report_type": report_type_value,
                        "amount": amount,
                        "hours_since_creation": 0,
                        "reminder_interval": "initial",
                        "payment_url": f"{settings.frontend_url}/report-generation.html",
                        "report_type_display": report_type_value.replace('_', ' ').title()
                    }
                )
                if email_result:
                    logger.info(f"✅ Sent DRAFT reminder email for report {report.id} to {user_email}")
                else:
                    logger.warning(f"⚠️ DRAFT reminder email returned False for report {report.id}")
                
                # Create user notification for DRAFT report
                try:
                    from ...models.notification import UserNotification
                    user_notification = UserNotification(
                        user_id=user_id,
                        title=f"Complete Your FMV Report Payment - Report #{report.id}",
                        message=f"Your FMV Report #{report.id} is waiting for payment. Complete your purchase to submit the report.",
                        type="fmv_report_draft_reminder",
                        read=False
                    )
                    db.add(user_notification)
                    db.commit()
                    logger.info(f"✅ Created user notification for DRAFT report {report.id}")
                except Exception as notif_error:
                    logger.warning(f"⚠️ Failed to create user notification for DRAFT report: {notif_error}", exc_info=True)
                
                # Create admin notifications for DRAFT report
                try:
                    from ...models.admin import AdminUser, Notification
                    admin_users = db.query(AdminUser).filter(
                        AdminUser.is_active == True,
                        AdminUser.is_verified == True
                    ).all()
                    
                    for admin in admin_users:
                        admin_notification = Notification(
                            admin_user_id=admin.id,
                            notification_type="fmv_report_draft_created",
                            title=f"📝 New DRAFT Report: #{report.id}",
                            message=f"User {user_email} created a DRAFT FMV Report #{report.id}. Payment pending.",
                            data={
                                "report_id": report.id,
                                "status": "draft",
                                "user_email": user_email,
                                "user_name": user_name,
                                "report_type": report_type_value,
                                "amount": amount
                            },
                            is_read=False
                        )
                        db.add(admin_notification)
                    db.commit()
                    logger.info(f"✅ Created admin notifications for DRAFT report {report.id}")
                except Exception as admin_notif_error:
                    logger.warning(f"⚠️ Failed to create admin notifications for DRAFT report: {admin_notif_error}", exc_info=True)
        except Exception as e:
            logger.error(f"Error sending draft reminder notification: {e}", exc_info=True)
        
        return response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting FMV report: {e}", exc_info=True)
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to submit report: {str(e)}")


@router.post("/upload-service-records", status_code=status.HTTP_200_OK)
async def upload_service_records(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Upload service record files (PDF, JPG, PNG) to DigitalOcean Spaces - max 20MB per file"""
    from pathlib import Path
    
    MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
    ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png'}
    
    uploaded_files = []
    storage_service = get_storage_service()
    
    try:
        for file in files:
            # Validate file size
            content = await file.read()
            file_size = len(content)
            
            if file_size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File {file.filename} exceeds 20MB limit"
                )
            
            # Validate file extension
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File {file.filename} has invalid extension. Only PDF, JPG, PNG allowed."
                )
            
            # Upload to DigitalOcean Spaces
            cdn_url = storage_service.upload_file(
                file_content=content,
                filename=file.filename,
                folder="service-records",
                content_type=file.content_type
            )
            
            uploaded_files.append({
                "filename": file.filename,
                "url": cdn_url,
                "size": file_size,
                "type": file.content_type
            })
        
        return {
            "success": True,
            "files": [f["url"] for f in uploaded_files],  # Return CDN URLs as array for service_record_files
            "file_urls": [f["url"] for f in uploaded_files],  # Keep for backward compatibility
            "file_details": uploaded_files  # Full file details
        }
    except HTTPException:
        raise
    except RuntimeError as e:
        logger.error(f"Storage service error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload service records: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error uploading service records: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload service records: {str(e)}"
        )


@router.get("/service-records/{filename:path}")
async def get_service_record_file(
    filename: str,
    db: Session = Depends(get_db)
):
    """Redirect to CDN URL for service record files (backward compatibility)"""
    from fastapi.responses import RedirectResponse
    from pathlib import Path
    
    try:
        # Security: Prevent directory traversal
        safe_filename = Path(filename).name
        
        # Construct CDN URL for the file
        storage_service = get_storage_service()
        file_key = f"service-records/{safe_filename}"
        cdn_url = storage_service.get_file_url(file_key, use_cdn=True)
        
        # Redirect to CDN URL
        return RedirectResponse(url=cdn_url, status_code=302)
    except Exception as e:
        logger.error(f"Error redirecting service record file {filename}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to serve file: {str(e)}"
        )


@router.post("/{report_id}/submit", response_model=FMVReportResponse)
async def submit_draft_report(
    report_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a draft report for processing"""
    try:
        user_id = int(current_user.get("sub"))
        service = FMVReportService(db)
        
        report = service.submit_report(report_id, user_id)
        
        # Send submitted notification
        try:
            email_service = get_fmv_email_service()
            if email_service:
                email_service.send_submitted_notification(
                user_email=current_user.get("email"),
                user_name=current_user.get("full_name", "User"),
                report_data={
                    "report_id": report.id,
                    "report_type": report.report_type
                }
            )
        except Exception as e:
            logger.error(f"Error sending submitted notification: {e}")
        
        return convert_report_to_response(report)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting draft report: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to submit report")


@router.get("/user/{user_id}", response_model=List[FMVReportResponse])
async def get_user_reports(
    user_id: str,  # Accept both int and email
    status_filter: Optional[str] = None,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Get all FMV reports for a user (accepts user_id as integer or email)"""
    try:
        # Try to get current_user if token provided (optional authentication)
        current_user = None
        try:
            from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
            security = HTTPBearer(auto_error=False)
            if request:
                credentials = await security(request)
                if credentials:
                    current_user = await get_current_user(credentials)
        except:
            pass
        
        # Determine if user_id is an email or integer
        actual_user_id = None
        try:
            # Try to parse as integer first
            actual_user_id = int(user_id)
        except ValueError:
            # If not an integer, treat as email and look up user
            user = db.query(User).filter(User.email == user_id).first()
            if user:
                actual_user_id = user.id
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        # Verify user can access these reports (if authenticated)
        if current_user:
            current_user_id = int(current_user.get("sub"))
            if current_user_id != actual_user_id and current_user.get("role") != "admin":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        service = FMVReportService(db)
        reports = service.get_user_reports(actual_user_id, status_filter)
        
        # Fix status mismatch: If payment succeeded but status is still DRAFT, update it
        fixed_count = 0
        for report in reports:
            # Check if payment succeeded (payment_status='succeeded' is sufficient, even if amount_paid is null)
            if (report.status == FMVReportStatus.DRAFT and 
                report.payment_status == 'succeeded' and 
                report.payment_intent_id):
                logger.warning(f"⚠️  Report {report.id} for user {actual_user_id} has successful payment but status is DRAFT - auto-fixing to SUBMITTED")
                report.status = FMVReportStatus.SUBMITTED
                if not report.submitted_at:
                    from datetime import datetime
                    report.submitted_at = datetime.utcnow()
                # Legacy: also set paid_at for backward compatibility
                if not report.paid_at:
                    from datetime import datetime
                    report.paid_at = datetime.utcnow()
                # If amount_paid is null but payment succeeded, try to get amount from payment intent
                if not report.amount_paid and report.payment_intent_id:
                    try:
                        stripe_service = get_stripe_service()
                        if stripe_service:
                            payment_intent = stripe_service.get_payment_intent(report.payment_intent_id)
                            if payment_intent and payment_intent.get('amount'):
                                report.amount_paid = payment_intent['amount']  # Amount in cents
                                logger.info(f"✅ Set amount_paid to {report.amount_paid} from payment intent")
                    except Exception as e:
                        logger.warning(f"Could not fetch amount from payment intent: {e}")
                fixed_count += 1
        
        if fixed_count > 0:
            db.commit()
            logger.info(f"✅ Auto-fixed {fixed_count} report(s) with status mismatch")
            # Refresh reports after commit
            reports = service.get_user_reports(actual_user_id, status_filter)
        
        return [convert_report_to_response(report) for report in reports]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user reports: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve reports")


@router.get("/{report_id}", response_model=FMVReportResponse)
async def get_report(
    report_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific FMV report"""
    try:
        user_id = int(current_user.get("sub"))
        is_admin = current_user.get("role") == "admin"
        
        service = FMVReportService(db)
        report = service.get_report(report_id, user_id if not is_admin else None)
        
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
        
        # Verify access
        if not is_admin and report.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        return convert_report_to_response(report)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting report: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve report")


@router.get("/{report_id}/timeline", response_model=FMVReportTimelineResponse)
async def get_report_timeline(
    report_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get timeline for a specific FMV report"""
    try:
        user_id = int(current_user.get("sub"))
        is_admin = current_user.get("role") == "admin"
        
        service = FMVReportService(db)
        report = service.get_report(report_id, user_id if not is_admin else None)
        
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
        
        # Verify access
        if not is_admin and report.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        timeline_data = service.get_report_timeline(report_id)
        timeline_items = [
            FMVReportTimelineItem(
                status=item["status"],
                timestamp=item["timestamp"],
                details=item["details"]
            )
            for item in timeline_data
        ]
        
        return FMVReportTimelineResponse(
            report_id=report_id,
            timeline=timeline_items
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting report timeline: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve timeline")


@router.put("/{report_id}/status", response_model=FMVReportResponse)
async def update_report_status(
    report_id: int,
    status_transition: StatusTransition,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update FMV report status (admin only)"""
    try:
        # Check admin access
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
        
        service = FMVReportService(db)
        report = service.update_status(report_id, status_transition)
        
        # Send appropriate email notification
        try:
            user = db.query(User).filter(User.id == report.user_id).first()
            if user:
                report_data = {
                    "report_id": report.id,
                    "report_type": report.report_type,
                    "assigned_analyst": report.assigned_analyst,
                    "rejection_reason": report.rejection_reason,
                    "pdf_url": report.pdf_url,
                    "amount": report.amount_paid
                }
                
                if status_transition.status == FMVReportStatus.IN_PROGRESS:
                    email_service = get_fmv_email_service()
                    if email_service:
                        email_service.send_in_progress_notification(
                        user_email=user.email,
                        user_name=user.full_name,
                        report_data=report_data
                    )
                elif status_transition.status == FMVReportStatus.COMPLETED:
                    email_service = get_fmv_email_service()
                    if email_service:
                        email_service.send_completed_notification(
                        user_email=user.email,
                        user_name=user.full_name,
                        report_data=report_data
                    )
                elif status_transition.status == FMVReportStatus.DELIVERED:
                    email_service = get_fmv_email_service()
                    if email_service:
                        email_service.send_delivered_notification(
                        user_email=user.email,
                        user_name=user.full_name,
                        report_data=report_data
                    )
                elif status_transition.status == FMVReportStatus.REJECTED:
                    email_service = get_fmv_email_service()
                    if email_service:
                        email_service.send_rejected_notification(
                        user_email=user.email,
                        user_name=user.full_name,
                        report_data=report_data
                    )
        except Exception as e:
            logger.error(f"Error sending status notification: {e}")
        
        return convert_report_to_response(report)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating report status: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update status")


@router.put("/{report_id}", response_model=FMVReportResponse)
async def update_report(
    report_id: int,
    update_data: FMVReportUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update FMV report fields (admin only)"""
    try:
        # Check admin access
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
        
        service = FMVReportService(db)
        report = service.update_report(report_id, update_data)
        
        return convert_report_to_response(report)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating report: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update report")


@router.post("/{report_id}/payment", response_model=FMVReportResponse)
async def mark_payment_received(
    report_id: int,
    payment_data: PaymentReceivedRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Mark payment as received for a report (authentication optional - payment webhook can call this)"""
    try:
        # Try to get current_user from token if provided (optional for payment webhooks)
        current_user = None
        try:
            from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
            security = HTTPBearer(auto_error=False)
            credentials = await security(request)
            if credentials:
                current_user = await get_current_user(credentials)
        except:
            pass
        
        service = FMVReportService(db)
        report = service.mark_payment_received(report_id, payment_data.payment_intent_id, payment_data.amount)
        
        # Get user for notification
        user = db.query(User).filter(User.id == report.user_id).first()
        
        logger.info(f"✅ Payment marked as received for report {report_id}: ${payment_data.amount}, status updated to {report.status.value}")
        
        # Send SUBMITTED notification (payment successful, report submitted)
        # NOTE: This email already includes the PDF receipt attachment; we do NOT send a separate Payment Receipt email.
        try:
            if user:
                email_service = get_fmv_email_service()
                if email_service:
                    # Send SUBMITTED notification (form filled, payment successful)
                    email_service.send_submitted_notification(
                        user_email=user.email,
                        user_name=user.full_name,
                        report_data={
                            "report_id": report.id,
                            "report_type": report.report_type.value if hasattr(report.report_type, 'value') else str(report.report_type),
                            "amount": payment_data.amount,
                            "payment_intent_id": payment_data.payment_intent_id
                        }
                    )
                    
                    # Create user notification
                    try:
                        from ...models.notification import UserNotification
                        user_notification = UserNotification(
                            user_id=user.id,
                            title=f"FMV Report #{report.id} Submitted",
                            message=f"Your FMV Report #{report.id} has been submitted successfully. Payment received: ${payment_data.amount:,.2f}",
                            type="fmv_report_submitted",
                            read=False
                        )
                        db.add(user_notification)
                        db.commit()
                    except Exception as notif_error:
                        logger.warning(f"Failed to create user notification: {notif_error}")
        except Exception as e:
            logger.error(f"Error sending paid notification: {e}")
        
        # Return report
        response = convert_report_to_response(report)
        return response.dict()
    except ValueError as e:
        logger.error(f"ValueError marking payment: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error marking payment: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to mark payment: {str(e)}")


@router.post("/{report_id}/upload-pdf", response_model=FMVReportResponse)
async def upload_pdf(
    report_id: int,
    pdf_url: str = Form(...),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload PDF for a completed report (admin only)"""
    try:
        # Check admin access
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
        
        service = FMVReportService(db)
        report = service.upload_pdf(report_id, pdf_url)
        
        # Send delivered notification if status changed to delivered
        if report.status == FMVReportStatus.DELIVERED:
            try:
                user = db.query(User).filter(User.id == report.user_id).first()
                if user:
                    email_service = get_fmv_email_service()
                    if email_service:
                        email_service.send_delivered_notification(
                        user_email=user.email,
                        user_name=user.full_name,
                        report_data={
                            "report_id": report.id,
                            "pdf_url": pdf_url
                        }
                    )
            except Exception as e:
                logger.error(f"Error sending delivered notification: {e}")
        
        return convert_report_to_response(report)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading PDF: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upload PDF")


@router.post("/fallback-request", response_model=FallbackRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_fallback_request(
    request_data: FallbackRequestCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a fallback request for manual valuation (authentication optional)"""
    try:
        # Try to get current_user from token if provided
        user_id = None
        try:
            from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
            security = HTTPBearer(auto_error=False)
            credentials = await security(request)
            if credentials:
                current_user = await get_current_user(credentials)
                user_id = int(current_user.get("sub"))
        except:
            pass
        
        # Use email from request if no authenticated user
        if not user_id and not request_data.user_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User email is required for unauthenticated requests"
            )
        
        service = FallbackRequestService(db)
        fallback_request = service.create_request(request_data, user_id)
        
        # Convert to response
        return FallbackRequestResponse(
            id=fallback_request.id,
            user_id=fallback_request.user_id,
            user_email=fallback_request.user_email,
            manufacturer=fallback_request.manufacturer,
            model=fallback_request.model,
            year=fallback_request.year,
            serial_number=fallback_request.serial_number,
            capacity_tons=fallback_request.capacity_tons,
            crane_type=fallback_request.crane_type,
            operating_hours=fallback_request.operating_hours,
            mileage=fallback_request.mileage,
            boom_length=fallback_request.boom_length,
            jib_length=fallback_request.jib_length,
            max_hook_height=fallback_request.max_hook_height,
            max_radius=fallback_request.max_radius,
            region=fallback_request.region,
            condition=fallback_request.condition,
            additional_specs=fallback_request.additional_specs,
            special_features=fallback_request.special_features,
            usage_history=fallback_request.usage_history,
            status=fallback_request.status,
            assigned_analyst=fallback_request.assigned_analyst,
            analyst_notes=fallback_request.analyst_notes,
            rejection_reason=fallback_request.rejection_reason,
            linked_fmv_report_id=fallback_request.linked_fmv_report_id,
            created_at=fallback_request.created_at,
            in_review_at=fallback_request.in_review_at,
            valuation_started_at=fallback_request.valuation_started_at,
            completed_at=fallback_request.completed_at,
            rejected_at=fallback_request.rejected_at,
            cancelled_at=fallback_request.cancelled_at,
            updated_at=fallback_request.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating fallback request: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create fallback request")


@router.get("/admin/list", response_model=List[FMVReportResponse])
async def get_admin_reports(
    status_filter: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all FMV reports for admin (with filters)"""
    try:
        # Check admin access
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
        
        service = FMVReportService(db)
        
        # Get all reports (admin can see all)
        reports = service.get_user_reports(None, status_filter)
        
        # Apply pagination
        reports = reports[offset:offset + limit]
        
        return [convert_report_to_response(report) for report in reports]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting admin reports: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve reports")


@router.get("/admin/stats", response_model=Dict[str, Any])
async def get_admin_stats(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get FMV report statistics for admin dashboard"""
    try:
        # Check admin access
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
        
        service = FMVReportService(db)
        stats = service.get_admin_stats()
        
        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting admin stats: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve stats")


@router.delete("/{report_id}/delete", status_code=status.HTTP_200_OK)
async def delete_fmv_report(
    report_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete (soft delete) an FMV report by marking it as DELETED status"""
    try:
        user_id = int(current_user.get("sub"))
        is_admin = current_user.get("role") == "admin"
        
        service = FMVReportService(db)
        report = service.get_report(report_id, user_id if not is_admin else None)
        
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
        
        # Verify access
        if not is_admin and report.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        # Only allow deletion of DRAFT reports (or admin can delete any)
        # FMVReportStatus is already imported at the top of the file
        if not is_admin and report.status != FMVReportStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only DRAFT reports can be deleted by users. Contact support for other reports."
            )
        
        # Mark as DELETED (soft delete)
        report.status = FMVReportStatus.DELETED
        db.commit()
        db.refresh(report)
        
        logger.info(f"✅ Marked report {report_id} as DELETED by user {user_id}")
        
        # Get user details for email and notification
        from ..models.user import User
        user = db.query(User).filter(User.id == user_id).first()
        
        if user:
            # Send deletion email notification
            try:
                from ..services.fmv_email_service import FMVEmailService
                email_service = FMVEmailService()
                crane_data = report.crane_details or {}
                report_data = {
                    'report_id': report_id,
                    'report_type': report.report_type.value if hasattr(report.report_type, 'value') else str(report.report_type) if report.report_type else 'N/A',
                    'crane_data': crane_data,
                    'crane_details': crane_data
                }
                email_service.send_deleted_notification(
                    user_email=user.email,
                    user_name=user.full_name or user.email,
                    report_data=report_data
                )
                logger.info(f"✅ Deletion email sent to {user.email}")
            except Exception as email_error:
                logger.warning(f"Failed to send deletion email: {email_error}")
            
            # Create user notification in bell icon
            try:
                from ..models.notification import UserNotification
                user_notification = UserNotification(
                    user_id=user_id,
                    type="report_deleted",
                    title="Report Deleted",
                    message=f"Your FMV report #{report_id} has been deleted successfully.",
                    read=False
                )
                db.add(user_notification)
                db.commit()
                logger.info(f"✅ User notification created for deleted report {report_id}")
            except Exception as notif_error:
                logger.warning(f"Failed to create user notification: {notif_error}")
                db.rollback()
        
        return {"success": True, "message": "Report deleted successfully", "report_id": report_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting report: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete report: {str(e)}")


@router.get("/{report_id}/receipt", response_class=Response)
async def get_payment_receipt_pdf(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate and download PDF receipt for a paid FMV report
    """
    try:
        # Get report
        service = FMVReportService(db)
        report = service.get_report(report_id)
        
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
        
        # Check if user owns the report or is admin
        user_id = int(current_user.get("sub"))
        if report.user_id != user_id:
            # Check if user is admin - some deployments may not have a user_id FK on AdminUser,
            # so we fall back to checking by primary key (id).
            try:
                from ...models.admin import AdminUser
                admin = db.query(AdminUser).filter(AdminUser.id == user_id).first()
            except Exception:
                admin = None
            if not admin or not admin.is_active:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this receipt")
        
        # Check if report has payment
        if not report.payment_intent_id or not report.amount_paid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Report has no payment information")
        
        # Get user
        user = db.query(User).filter(User.id == report.user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        # Generate PDF receipt
        from ...services.receipt_pdf_service import ReceiptPDFService
        pdf_service = ReceiptPDFService()
        
        if not pdf_service.available:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="PDF generation service not available")
        
        receipt_data = {
            "receipt_number": f"RPT-{report.id}",
            "transaction_id": report.payment_intent_id,
            "payment_date": report.paid_at.isoformat() if report.paid_at else report.submitted_at.isoformat() if report.submitted_at else datetime.utcnow().isoformat(),
            "customer_name": user.full_name or user.email,
            "customer_email": user.email,
            "report_id": report.id,
            "report_type": report.report_type.value if hasattr(report.report_type, 'value') else str(report.report_type),
            "amount": float(report.amount_paid) if report.amount_paid else 0,
            "currency": "USD",
            "company_name": settings.app_name
        }
        
        pdf_buffer = pdf_service.generate_receipt_pdf(receipt_data)
        if not pdf_buffer:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate PDF receipt")
        
        # Return PDF as response
        return Response(
            content=pdf_buffer.getvalue(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="Payment_Receipt_Report_{report.id}.pdf"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating receipt PDF: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate receipt: {str(e)}")

