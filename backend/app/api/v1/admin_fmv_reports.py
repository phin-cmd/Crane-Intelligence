"""
Admin FMV Reports API Endpoints
Handles admin-specific FMV report management endpoints
Matches frontend expectations: /api/v1/admin/fmv-reports
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form, Response
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.admin_auth import get_current_admin_user
from ...services.fmv_report_service import FMVReportService
from ...services.fmv_email_service import FMVEmailService
from ...schemas.fmv_report import FMVReportResponse, StatusTransition, FMVReportUpdate
from ...models.fmv_report import FMVReportStatus
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class StatusUpdateRequest(BaseModel):
    status: str
    notes: Optional[str] = None

router = APIRouter(prefix="/admin/fmv-reports", tags=["Admin FMV Reports"])


def convert_report_to_response(report) -> FMVReportResponse:
    """Convert FMVReport model to response schema, handling enum conversions"""
    report_dict = {
        "id": report.id,
        "user_id": report.user_id,
        "report_type": report.report_type.value if hasattr(report.report_type, 'value') else str(report.report_type),
        "status": report.status.value if hasattr(report.status, 'value') else str(report.status),
        "crane_details": report.crane_details if report.crane_details else {},
        "service_records": report.service_records if report.service_records else None,
        "service_record_files": report.service_record_files if hasattr(report, 'service_record_files') and report.service_record_files else None,
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
        "pdf_url": getattr(report, 'pdf_url', None),
        "pdf_uploaded_at": getattr(report, 'pdf_uploaded_at', None),
        "analyst_notes": getattr(report, 'analyst_notes', None),
        "rejection_reason": getattr(report, 'rejection_reason', None),
        "assigned_analyst": getattr(report, 'assigned_analyst', None),
        "metadata": getattr(report, 'report_metadata', None) if hasattr(report, 'report_metadata') else None,  # Use renamed attribute
        "updated_at": getattr(report, 'updated_at', None),
        "turnaround_deadline": getattr(report, 'turnaround_deadline', None)
    }
    return FMVReportResponse(**report_dict)


@router.get("/{report_id}/receipt", response_class=Response)
async def get_admin_payment_receipt_pdf(
    report_id: int,
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Admin-only endpoint to download PDF receipt for a paid FMV report.
    Uses the same receipt PDF generation as the user endpoint, but relies
    solely on admin authentication (no user ownership check).
    """
    try:
        service = FMVReportService(db)
        report = service.get_report(report_id)
        
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
        
        # Ensure report has payment information
        if not report.payment_intent_id or not report.amount_paid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Report has no payment information")
        
        # Get user who owns the report
        from ...models.user import User
        user = db.query(User).filter(User.id == report.user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        # Generate PDF receipt
        from ...services.receipt_pdf_service import ReceiptPDFService
        pdf_service = ReceiptPDFService()
        
        if not pdf_service.available:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="PDF generation service not available")
        
        from ...core.config import settings
        from datetime import datetime
        
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
        
        return Response(
            content=pdf_buffer.getvalue(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename=\"Payment_Receipt_Report_{report.id}.pdf\"'
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating admin receipt PDF: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate receipt")


# Initialize services (lazy initialization)
_fmv_email_service = None

def get_fmv_email_service():
    """Get or create FMV email service instance"""
    global _fmv_email_service
    if _fmv_email_service is None:
        try:
            from ...services.fmv_email_service import FMVEmailService
            _fmv_email_service = FMVEmailService()
        except Exception as e:
            logger.warning(f"Could not initialize FMV email service: {e}")
            _fmv_email_service = None
    return _fmv_email_service


@router.get("", response_model=Dict[str, Any])
async def get_admin_reports(
    status_filter: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all FMV reports for admin (with filters) - matches frontend expectation"""
    try:
        # Admin access is already verified by get_current_admin_user dependency
        
        logger.info(f"Admin reports query started: status_filter={status_filter}, limit={limit}, offset={offset}")
        
        service = FMVReportService(db)
        
        # Get all reports (admin can see all) - include drafts, paid, DELETED, etc.
        # Pass None for user_id to get all reports
        # include_deleted=True to show DELETED reports in admin panel
        try:
            reports = service.get_user_reports(None, status_filter, include_deleted=True)
            # Log DRAFT and DELETED reports count for debugging
            draft_count = sum(1 for r in reports if r.status == FMVReportStatus.DRAFT)
            deleted_count = sum(1 for r in reports if r.status == FMVReportStatus.DELETED)
            logger.info(f"Admin reports query: status_filter={status_filter}, total_reports={len(reports)}, draft_reports={draft_count}, deleted_reports={deleted_count}")
        except Exception as query_error:
            logger.error(f"Error querying reports from database: {query_error}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Database query failed: {str(query_error)}"
            )
        
        # Apply pagination
        total = len(reports)
        paginated_reports = reports[offset:offset + limit]
        
        logger.info(f"Returning {len(paginated_reports)} reports (offset={offset}, limit={limit})")
        
        # Convert reports and add frontend-compatible fields
        reports_list = []
        fixed_count = 0
        for report in paginated_reports:
            # Fix status mismatch: If payment succeeded but status is still DRAFT, update it
            # Also fetch amount from Stripe if missing
            # Check if payment_intent_id exists (even if payment_status is not set)
            if report.payment_intent_id:
                # Fetch amount from Stripe if missing or zero
                if not report.amount_paid or report.amount_paid == 0:
                    try:
                        from ...services.stripe_service import StripeService
                        stripe_service = StripeService()
                        payment_intent = stripe_service.get_payment_intent(report.payment_intent_id)
                        if payment_intent:
                            # Stripe returns amount in cents, but amount_paid is stored in dollars
                            # Check if payment_intent is a dict or object
                            if isinstance(payment_intent, dict):
                                amount_cents = payment_intent.get('amount') or payment_intent.get('amount_received')
                                payment_status = payment_intent.get('status')
                            else:
                                amount_cents = getattr(payment_intent, 'amount', None) or getattr(payment_intent, 'amount_received', None)
                                payment_status = getattr(payment_intent, 'status', None)
                            
                            if amount_cents:
                                # CRITICAL: Store amount_paid in CENTS (not dollars) for consistency
                                # The amount_paid field should always be in cents to match Stripe's format
                                report.amount_paid = float(amount_cents)
                                # Also update payment_status if it's missing or incorrect
                                if payment_status == 'succeeded' and (not report.payment_status or report.payment_status != 'succeeded'):
                                    report.payment_status = 'succeeded'
                                logger.info(f"✅ Fetched amount from Stripe for report {report.id}: ${report.amount_paid}, status: {payment_status}")
                                # CRITICAL: Commit the amount update
                                try:
                                    db.commit()
                                    db.refresh(report)
                                except Exception as commit_error:
                                    logger.error(f"❌ Failed to commit amount update for report {report.id}: {commit_error}")
                                    db.rollback()
                    except Exception as stripe_error:
                        logger.warning(f"Could not fetch amount from Stripe for report {report.id}: {stripe_error}")
                
                # Auto-fix status if payment succeeded but status is still DRAFT
                if report.payment_status == 'succeeded' and report.status == FMVReportStatus.DRAFT:
                    logger.warning(f"⚠️  Report {report.id} has successful payment but status is DRAFT - auto-fixing to SUBMITTED")
                    report.status = FMVReportStatus.SUBMITTED
                    if not report.submitted_at:
                        from datetime import datetime
                        report.submitted_at = datetime.utcnow()
                    # Legacy: also set paid_at for backward compatibility
                    if not report.paid_at:
                        from datetime import datetime
                        report.paid_at = datetime.utcnow()
                    # CRITICAL: Commit the status fix to database
                    try:
                        db.commit()
                    except Exception as commit_error:
                        logger.error(f"❌ Failed to commit status fix for report {report.id}: {commit_error}")
                        db.rollback()
                
                # Auto-fix status if still DRAFT (legacy check for amount_paid)
                if (report.status == FMVReportStatus.DRAFT and 
                    report.amount_paid and 
                    report.amount_paid > 0):
                    logger.warning(f"⚠️  Report {report.id} has successful payment but status is DRAFT - auto-fixing to SUBMITTED")
                    report.status = FMVReportStatus.SUBMITTED
                    if not report.submitted_at:
                        from datetime import datetime
                        report.submitted_at = datetime.utcnow()
                    # Legacy: also set paid_at for backward compatibility
                    if not report.paid_at:
                        from datetime import datetime
                        report.paid_at = datetime.utcnow()
                    # CRITICAL: Commit the status fix to database
                    try:
                        db.commit()
                        db.refresh(report)
                        logger.info(f"✅ Fixed and committed status for report {report.id}: DRAFT -> SUBMITTED")
                        fixed_count += 1
                    except Exception as commit_error:
                        logger.error(f"❌ Failed to commit status fix for report {report.id}: {commit_error}")
                        db.rollback()
            
            try:
                report_response = convert_report_to_response(report)
                report_dict = report_response.dict()
            except Exception as convert_error:
                logger.error(f"Error converting report {report.id} to response: {convert_error}", exc_info=True)
                # Skip this report and continue with others
                continue
            
            # Get user info for customer_name and customer_email
            try:
                from ...models.user import User
                user = db.query(User).filter(User.id == report.user_id).first()
                if user:
                    report_dict["customer_name"] = user.full_name or user.username or f"User {report.user_id}"
                    report_dict["customer_email"] = user.email
                else:
                    # Try to get email from report metadata
                    if hasattr(report, 'report_metadata') and report.report_metadata and isinstance(report.report_metadata, dict):
                        report_dict["customer_email"] = report.report_metadata.get("user_email") or report.report_metadata.get("receipt_email") or "Unknown"
                        report_dict["customer_name"] = "Unknown User"
                    else:
                        report_dict["customer_name"] = "Unknown User"
                        report_dict["customer_email"] = "Unknown"
            except Exception as user_error:
                logger.warning(f"Error getting user info for report {report.id}: {user_error}")
                report_dict["customer_name"] = "Unknown User"
                report_dict["customer_email"] = "Unknown"
            
            # Map crane_details to crane_data for frontend compatibility
            report_dict["crane_data"] = report_dict.get("crane_details", {})
            
            # Map amount_paid to amount for frontend compatibility (convert to cents)
            # If amount_paid is not available, calculate from report type
            if report_dict.get("amount_paid"):
                report_dict["amount"] = int(report_dict.get("amount_paid") * 100)
            else:
                # Calculate expected price based on report type for unpaid reports
                try:
                    from ...services.fmv_pricing_config import get_base_price_cents
                    report_type = report_dict.get("report_type")
                    unit_count = report_dict.get("unit_count", 1)
                    expected_price_cents = get_base_price_cents(report_type, unit_count)
                    report_dict["amount"] = expected_price_cents
                except Exception as price_error:
                    logger.warning(f"Could not calculate price for report {report.id}: {price_error}")
                    report_dict["amount"] = 0
            
            # Calculate time remaining until deadline if turnaround_deadline exists
            if report_dict.get("turnaround_deadline"):
                try:
                    from ...services.turnaround_tracker import TurnaroundTracker
                    tracker = TurnaroundTracker(db)
                    time_info = tracker.get_time_remaining(report)
                    if time_info:
                        report_dict["time_remaining"] = time_info
                except Exception as time_error:
                    logger.warning(f"Could not calculate time remaining for report {report.id}: {time_error}")
                    report_dict["time_remaining"] = None
            
            # Calculate 24-hour deadline from submitted_at if available
            if report.submitted_at:
                try:
                    from datetime import timedelta
                    deadline_24h = report.submitted_at + timedelta(hours=24)
                    report_dict["deadline_24h"] = deadline_24h.isoformat() if hasattr(deadline_24h, 'isoformat') else str(deadline_24h)
                except Exception as e:
                    logger.warning(f"Could not calculate 24h deadline for report {report.id}: {e}")
            elif report.paid_at:
                # Fallback to paid_at if submitted_at is not available
                try:
                    from datetime import timedelta
                    deadline_24h = report.paid_at + timedelta(hours=24)
                    report_dict["deadline_24h"] = deadline_24h.isoformat() if hasattr(deadline_24h, 'isoformat') else str(deadline_24h)
                except Exception as e:
                    logger.warning(f"Could not calculate 24h deadline from paid_at for report {report.id}: {e}")
            
            reports_list.append(report_dict)
        
        # Commit any status fixes
        if fixed_count > 0:
            db.commit()
            logger.info(f"✅ Auto-fixed {fixed_count} report(s) with status mismatch in admin query")
        
        return {
            "success": True,
            "reports": reports_list,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting admin reports: {e}", exc_info=True)
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Full traceback: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to retrieve reports: {str(e)}"
        )


@router.put("/{report_id}", response_model=Dict[str, Any])
async def update_report_status(
    report_id: int,
    status_update: StatusUpdateRequest,
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update FMV report status (admin only) - matches frontend expectation"""
    try:
        # Admin access is already verified by get_current_admin_user dependency
        
        service = FMVReportService(db)
        
        # Convert string to enum
        try:
            status_enum = FMVReportStatus(status_update.status)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status: {status_update.status}")
        
        # Update status using StatusTransition
        from ...schemas.fmv_report import StatusTransition
        status_transition = StatusTransition(
            status=status_enum,
            analyst_notes=status_update.notes,
            need_more_info_reason=status_update.notes if status_enum == FMVReportStatus.NEED_MORE_INFO else None
        )
        # Get admin user ID - handle both dict and object types
        admin_user_id = None
        if current_user:
            if isinstance(current_user, dict):
                admin_user_id = current_user.get("sub")
            elif hasattr(current_user, 'id'):
                admin_user_id = current_user.id
            elif hasattr(current_user, 'sub'):
                admin_user_id = current_user.sub
        
        report = service.update_status(
            report_id=report_id,
            status_transition=status_transition,
            admin_user_id=admin_user_id
        )
        
        # Send email notification if status changed
        try:
            from ...models.user import User
            user = db.query(User).filter(User.id == report.user_id).first()
            if user:
                email_service = get_fmv_email_service()
                if email_service:
                    report_data = {
                        "report_id": report.id,
                        "report_type": report.report_type.value if hasattr(report.report_type, 'value') else str(report.report_type),
                        "assigned_analyst": getattr(report, 'assigned_analyst', None),
                        "need_more_info_reason": getattr(report, 'need_more_info_reason', None) or getattr(report, 'rejection_reason', None),  # Use new field, fallback to old
                        "rejection_reason": getattr(report, 'need_more_info_reason', None) or getattr(report, 'rejection_reason', None),  # Backward compatibility
                        "pdf_url": report.pdf_url,
                        "amount": report.amount_paid
                    }
                    
                    # Send user notification based on status
                    if status_enum == FMVReportStatus.IN_PROGRESS:
                        email_service.send_in_progress_notification(
                            user_email=user.email,
                            user_name=user.full_name,
                            report_data=report_data
                        )
                    elif status_enum == FMVReportStatus.COMPLETED:
                        email_service.send_completed_notification(
                            user_email=user.email,
                            user_name=user.full_name,
                            report_data=report_data
                        )
                    elif status_enum == FMVReportStatus.DELIVERED:
                        email_service.send_delivered_notification(
                            user_email=user.email,
                            user_name=user.full_name,
                            report_data=report_data
                        )
                    elif status_enum == FMVReportStatus.NEED_MORE_INFO:
                        # Include all necessary data for need more info email
                        need_more_info_data = {
                            "report_id": report.id,
                            "report_type": report.report_type.value if hasattr(report.report_type, 'value') else str(report.report_type),
                            "report_type_display": report.report_type.value.replace('_', ' ').title() if hasattr(report.report_type, 'value') else str(report.report_type).replace('_', ' ').title(),
                            "crane_details": report.crane_details,
                            "amount_paid": report.amount_paid,
                            "need_more_info_reason": getattr(report, 'need_more_info_reason', None) or status_update.notes or "Additional information is required to complete your report."
                        }
                        email_service.send_need_more_info_notification(
                            user_email=user.email,
                            user_name=user.full_name,
                            report_data=need_more_info_data
                        )
                    
                    # Send admin notification for ALL status changes
                    email_service._send_admin_notification(
                        notification_type=status_enum.value,
                        report_data=report_data,
                        user_name=user.full_name,
                        user_email=user.email
                    )
                    
                    # Create user notification record
                    try:
                        from ...models.notification import UserNotification
                        # Build user-facing bell notification messages
                        status_messages = {
                            FMVReportStatus.IN_PROGRESS: f"Your FMV Report #{report.id} is now being processed",
                            FMVReportStatus.COMPLETED: f"Your FMV Report #{report.id} has been completed",
                            FMVReportStatus.DELIVERED: f"Your FMV Report #{report.id} has been delivered",
                            FMVReportStatus.NEED_MORE_INFO: None
                        }
                        
                        # For NEED_MORE_INFO, include the admin's reason in the notification message
                        if status_enum == FMVReportStatus.NEED_MORE_INFO:
                            reason = report_data.get("need_more_info_reason") or status_update.notes or "Additional information is required to complete your report."
                            # Keep notification concise but include the key reason text
                            trimmed_reason = (reason[:180] + "…") if len(reason) > 180 else reason
                            status_messages[FMVReportStatus.NEED_MORE_INFO] = (
                                f"More information is needed for your FMV Report #{report.id}: {trimmed_reason}"
                            )
                        
                        if status_enum in status_messages:
                            user_notification = UserNotification(
                                user_id=user.id,
                                title=f"FMV Report #{report.id} Status Update",
                                message=status_messages[status_enum],
                                type="fmv_report_status_update",
                                read=False
                            )
                            db.add(user_notification)
                    except Exception as user_notif_error:
                        logger.warning(f"Failed to create user notification record: {user_notif_error}")
                    
                    # Create admin notification records
                    try:
                        from ...models.admin import Notification
                        from sqlalchemy import text
                        
                        # Use raw SQL to avoid schema mismatch issues with AdminUser model
                        try:
                            admin_users_result = db.execute(text("""
                                SELECT id, email, full_name, username 
                                FROM admin_users 
                                WHERE is_active = true AND is_verified = true
                            """))
                            admin_users_data = admin_users_result.fetchall()
                            admin_users = []
                            for row in admin_users_data:
                                admin_obj = type('AdminUser', (), {
                                    'id': row[0],
                                    'email': row[1],
                                    'full_name': row[2] if len(row) > 2 and row[2] else None,
                                    'username': row[3] if len(row) > 3 and row[3] else None
                                })()
                                admin_users.append(admin_obj)
                        except Exception as sql_error:
                            logger.warning(f"Failed to query admin users with raw SQL, trying ORM: {sql_error}")
                            from ...models.admin import AdminUser
                            admin_users = db.query(AdminUser).filter(
                                AdminUser.is_active == True,
                                AdminUser.is_verified == True
                            ).all()
                        
                        for admin in admin_users:
                            admin_notification = Notification(
                                admin_user_id=admin.id,
                                notification_type="fmv_report_status_update",
                                title=f"Report #{report.id} Status Updated",
                                message=f"Report #{report.id} status changed to {status_enum.value}. User: {user.full_name or user.email}",
                                action_url=f"/admin/fmv-reports.html#report-{report.id}",
                                action_text="View Report",
                                is_read=False
                            )
                            db.add(admin_notification)
                        db.commit()
                    except Exception as notif_error:
                        logger.warning(f"Failed to create admin notification records: {notif_error}")
        except Exception as e:
            logger.error(f"Error sending status notification: {e}")
        
        return {
            "success": True,
            "report": convert_report_to_response(report)
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating report status: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update report status")


@router.post("/upload-pdf", response_model=Dict[str, Any])
async def upload_pdf(
    pdf: Optional[UploadFile] = File(None),
    report_id: Optional[int] = Form(None),
    pdf_url: Optional[str] = Form(None),
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Upload PDF for a completed report (admin only) - matches frontend expectation"""
    try:
        # Admin access is already verified by get_current_admin_user dependency
        
        # Get report_id from form or use default
        if not report_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="report_id is required")
        
        # Handle file upload or URL
        final_pdf_url = pdf_url
        if pdf and pdf.filename:
            # Upload to DigitalOcean Spaces
            from ...services.storage_service import get_storage_service
            
            content = await pdf.read()
            storage_service = get_storage_service()
            
            # Upload to Spaces
            final_pdf_url = storage_service.upload_file(
                file_content=content,
                filename=pdf.filename,
                folder="fmv-reports",
                content_type=pdf.content_type or "application/pdf"
            )
        
        if not final_pdf_url:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Either pdf file or pdf_url is required")
        
        service = FMVReportService(db)
        report = service.upload_pdf(report_id, final_pdf_url)
        
        # Auto-update status to DELIVERED when PDF is uploaded
        if report.status != FMVReportStatus.DELIVERED:
            from ...schemas.fmv_report import StatusTransition
            # Get admin user ID for status transition
            admin_user_id = None
            if current_user:
                if isinstance(current_user, dict):
                    admin_user_id = current_user.get("sub")
                elif hasattr(current_user, 'id'):
                    admin_user_id = current_user.id
                elif hasattr(current_user, 'sub'):
                    admin_user_id = current_user.sub
            
            status_transition = StatusTransition(status=FMVReportStatus.DELIVERED)
            try:
                report = service.update_status(report_id, status_transition, admin_user_id=admin_user_id)
            except ValueError as status_error:
                # If status transition fails, log but continue (PDF is still uploaded)
                logger.warning(f"Could not update status to DELIVERED for report {report_id}: {status_error}. PDF uploaded successfully.")
                # Refresh report to get latest state
                db.refresh(report)
        
        # Send DELIVERED notification (form filled, payment successful, PDF uploaded)
        try:
            from ...models.user import User
            user = db.query(User).filter(User.id == report.user_id).first()
            if user:
                email_service = get_fmv_email_service()
                if email_service:
                    report_data = {
                        "report_id": report.id,
                        "report_type": report.report_type.value if hasattr(report.report_type, 'value') else str(report.report_type),
                        "pdf_url": final_pdf_url
                    }
                    
                    # Send user notification
                    email_service.send_delivered_notification(
                        user_email=user.email,
                        user_name=user.full_name,
                        report_data=report_data
                    )
                    
                    # Send admin notification
                    email_service._send_admin_notification(
                        notification_type="delivered",
                        report_data=report_data,
                        user_name=user.full_name,
                        user_email=user.email
                    )
                    
                    # Create user notification record
                    try:
                        from ...models.notification import UserNotification
                        user_notification = UserNotification(
                            user_id=user.id,
                            title=f"FMV Report #{report.id} Delivered",
                            message=f"Your FMV Report #{report.id} has been delivered. You can download it from your dashboard.",
                            type="fmv_report_delivered",
                            read=False
                        )
                        db.add(user_notification)
                    except Exception as notif_error:
                        logger.warning(f"Failed to create user notification: {notif_error}")
                    
                    # Create admin notification records
                    try:
                        from ...models.admin import Notification
                        from sqlalchemy import text
                        
                        # Use raw SQL to avoid schema mismatch issues with AdminUser model
                        try:
                            admin_users_result = db.execute(text("""
                                SELECT id, email, full_name, username 
                                FROM admin_users 
                                WHERE is_active = true AND is_verified = true
                            """))
                            admin_users_data = admin_users_result.fetchall()
                            admin_users = []
                            for row in admin_users_data:
                                admin_obj = type('AdminUser', (), {
                                    'id': row[0],
                                    'email': row[1],
                                    'full_name': row[2] if len(row) > 2 and row[2] else None,
                                    'username': row[3] if len(row) > 3 and row[3] else None
                                })()
                                admin_users.append(admin_obj)
                        except Exception as sql_error:
                            logger.warning(f"Failed to query admin users with raw SQL, trying ORM: {sql_error}")
                            from ...models.admin import AdminUser
                            admin_users = db.query(AdminUser).filter(
                                AdminUser.is_active == True,
                                AdminUser.is_verified == True
                            ).all()
                        
                        for admin in admin_users:
                            admin_notification = Notification(
                                admin_user_id=admin.id,
                                notification_type="fmv_report_delivered",
                                title=f"Report #{report.id} Delivered",
                                message=f"Report #{report.id} has been delivered to {user.email} ({user.full_name or 'User'})",
                                action_url=f"/admin/fmv-reports.html#report-{report.id}",
                                action_text="View Report",
                                is_read=False
                            )
                            db.add(admin_notification)
                        db.commit()
                    except Exception as admin_notif_error:
                        logger.warning(f"Failed to create admin notification records: {admin_notif_error}")
        except Exception as e:
            logger.error(f"Error sending delivered notification: {e}")
        
        return {
            "success": True,
            "report": convert_report_to_response(report)
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading PDF: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upload PDF")


@router.post("/check-draft-reminders", response_model=Dict[str, Any])
async def check_draft_reminders(
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Check for DRAFT reports and send periodic reminder emails (admin only)
    Sends reminders at different intervals: 1 hour, 6 hours, 24 hours, 48 hours"""
    try:
        from datetime import datetime, timedelta
        from ...models.fmv_report import FMVReport, FMVReportStatus
        from ...models.user import User
        from ...models.admin import AdminUser, Notification
        
        now = datetime.utcnow()
        
        # Find DRAFT reports that need reminders
        # Send reminders at: 1 hour, 6 hours, 24 hours, 48 hours
        draft_reports = db.query(FMVReport).filter(
            FMVReport.status == FMVReportStatus.DRAFT
        ).all()
        
        email_service = get_fmv_email_service()
        reminders_sent = 0
        
        for report in draft_reports:
            user = db.query(User).filter(User.id == report.user_id).first()
            if not user or not email_service:
                continue
            
            # Calculate hours since report creation
            hours_since_creation = (now - report.created_at).total_seconds() / 3600
            
            # Determine if reminder should be sent based on time intervals
            should_send_reminder = False
            reminder_interval = None
            
            if 1 <= hours_since_creation < 2:
                # First reminder: 1 hour
                should_send_reminder = True
                reminder_interval = "1 hour"
            elif 6 <= hours_since_creation < 7:
                # Second reminder: 6 hours
                should_send_reminder = True
                reminder_interval = "6 hours"
            elif 24 <= hours_since_creation < 25:
                # Third reminder: 24 hours
                should_send_reminder = True
                reminder_interval = "24 hours"
            elif 48 <= hours_since_creation < 49:
                # Fourth reminder: 48 hours
                should_send_reminder = True
                reminder_interval = "48 hours"
            elif hours_since_creation >= 72:
                # Final reminder: 72+ hours (every 24 hours after that)
                if int(hours_since_creation) % 24 < 1:
                    should_send_reminder = True
                    reminder_interval = f"{int(hours_since_creation)} hours"
            
            if should_send_reminder:
                try:
                    # Send DRAFT reminder email
                    email_service.send_draft_reminder_notification(
                        user_email=user.email,
                        user_name=user.full_name,
                        report_data={
                            "report_id": report.id,
                            "amount": report.amount_paid or 0,
                            "payment_url": f"{settings.frontend_url}/payment.html?report_id={report.id}",
                            "hours_since_creation": int(hours_since_creation),
                            "reminder_interval": reminder_interval
                        }
                    )
                    
                    # Create user notification
                    from ...models.notification import UserNotification
                    user_notification = UserNotification(
                        user_id=user.id,
                        title=f"Complete Your FMV Report Payment",
                        message=f"Your FMV Report #{report.id} is waiting for payment. Complete your purchase to submit the report.",
                        type="fmv_report_draft_reminder",
                        read=False
                    )
                    db.add(user_notification)
                    
                    # Create admin notifications
                    admin_users = db.query(AdminUser).filter(
                        AdminUser.is_active == True,
                        AdminUser.is_verified == True
                    ).all()
                    
                    for admin in admin_users:
                        admin_notification = Notification(
                            admin_user_id=admin.id,
                            notification_type="fmv_report_draft_reminder",
                            title=f"⚠️ DRAFT Report Reminder: #{report.id}",
                            message=f"User {user.email}'s FMV Report #{report.id} is still in DRAFT status ({reminder_interval} since creation). Payment pending.",
                            action_url=f"/admin/fmv-reports.html?report_id={report.id}",
                            action_text="View Report"
                        )
                        db.add(admin_notification)
                    
                    reminders_sent += 1
                    logger.info(f"✅ Sent DRAFT reminder for report {report.id} ({reminder_interval} since creation)")
                except Exception as e:
                    logger.error(f"Error sending draft reminder for report {report.id}: {e}")
        
        db.commit()
        
        return {
            "success": True,
            "reminders_sent": reminders_sent,
            "total_draft_reports": len(draft_reports)
        }
    except Exception as e:
        logger.error(f"Error checking draft reminders: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to check draft reminders")


@router.post("/check-overdue-reports", response_model=Dict[str, Any])
async def check_overdue_reports(
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Check for OVERDUE reports and send admin-only emails (admin only)"""
    try:
        from datetime import datetime, timedelta
        from ...models.fmv_report import FMVReport, FMVReportStatus
        from ...models.user import User
        from ...models.admin import AdminUser
        
        # Find SUBMITTED reports past 24-hour deadline
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        overdue_reports = db.query(FMVReport).filter(
            FMVReport.status == FMVReportStatus.SUBMITTED,
            FMVReport.submitted_at.isnot(None),
            FMVReport.submitted_at < twenty_four_hours_ago
        ).all()
        
        email_service = get_fmv_email_service()
        overdue_emails_sent = 0
        
        # Get all active admin users
        admin_users = db.query(AdminUser).filter(
            AdminUser.is_active == True,
            AdminUser.is_verified == True
        ).all()
        
        admin_emails = [admin.email for admin in admin_users]
        
        for report in overdue_reports:
            user = db.query(User).filter(User.id == report.user_id).first()
            if user and email_service and admin_emails:
                try:
                    # Calculate hours overdue
                    hours_overdue = (datetime.utcnow() - report.submitted_at).total_seconds() / 3600
                    
                    # Send OVERDUE notification to admins only
                    email_service.send_overdue_notification(
                        admin_emails=admin_emails,
                        report_data={
                            "report_id": report.id,
                            "report_type": report.report_type.value if hasattr(report.report_type, 'value') else str(report.report_type),
                            "submitted_at": report.submitted_at.isoformat() if report.submitted_at else None,
                            "deadline": (report.submitted_at + timedelta(hours=24)).isoformat() if report.submitted_at else None,
                            "hours_overdue": int(hours_overdue)
                        },
                        user_name=user.full_name,
                        user_email=user.email
                    )
                    
                    # Mark report as overdue (update status)
                    if report.status != FMVReportStatus.OVERDUE:
                        from ...schemas.fmv_report import StatusTransition
                        status_transition = StatusTransition(status=FMVReportStatus.OVERDUE)
                        service = FMVReportService(db)
                        report = service.update_status(report.id, status_transition, admin_user_id=None)
                    
                    # Create admin notification records
                    for admin in admin_users:
                        from ...models.admin import Notification
                        admin_notification = Notification(
                            admin_user_id=admin.id,
                            notification_type="fmv_report_overdue",
                            title=f"⚠️ OVERDUE: Report #{report.id} Past Deadline",
                            message=f"Report #{report.id} submitted by {user.email} is {int(hours_overdue)} hours overdue",
                            data={
                                "report_id": report.id,
                                "status": "overdue",
                                "user_email": user.email,
                                "user_name": user.full_name,
                                "hours_overdue": int(hours_overdue)
                            },
                            is_read=False
                        )
                        db.add(admin_notification)
                    
                    overdue_emails_sent += 1
                except Exception as e:
                    logger.error(f"Error sending overdue notification for report {report.id}: {e}")
        
        db.commit()
        
        return {
            "success": True,
            "overdue_emails_sent": overdue_emails_sent,
            "total_overdue_reports": len(overdue_reports)
        }
    except Exception as e:
        logger.error(f"Error checking overdue reports: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to check overdue reports")


@router.get("/stats", response_model=Dict[str, Any])
async def get_admin_stats(
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get FMV report statistics for admin dashboard"""
    try:
        # Admin access is already verified by get_current_admin_user dependency
        
        service = FMVReportService(db)
        stats = service.get_admin_stats()
        
        return {
            "success": True,
            **stats
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting admin stats: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve stats")

