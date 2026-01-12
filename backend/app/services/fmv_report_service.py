"""
FMV Report Service
Business logic for FMV report operations
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, cast, String
from datetime import datetime
import logging

from ..models.fmv_report import FMVReport, FMVReportStatus, FMVReportType, FleetPricingTier
from ..models.status_history import StatusHistory
from ..models.user import User
from ..schemas.fmv_report import (
    FMVReportCreate, StatusTransition, FMVReportUpdate, FleetPricingRequest
)
from ..core.config import settings
# Optional import - fallback if module doesn't exist
try:
    from ..services.fmv_pricing_config import get_base_price_dollars
except ImportError:
    # Fallback pricing function if pricing config module doesn't exist
    def get_base_price_dollars(report_type: str, unit_count: int = 1) -> int:
        """Fallback pricing function"""
        pricing = {
            "spot_check": 25000,  # $250
            "professional": 99500,  # $995
            "fleet_valuation": 149500  # $1,495 base
        }
        base = pricing.get(report_type, 99500)
        if report_type == "fleet_valuation" and unit_count > 1:
            # Simple tiered pricing fallback
            if unit_count <= 5:
                return 149500
            elif unit_count <= 10:
                return 249500
            elif unit_count <= 25:
                return 499500
            else:
                return 799500
        return base

logger = logging.getLogger(__name__)


class FMVReportService:
    """Service for managing FMV reports"""
    
    # Fleet pricing tiers - Tiered pricing model
    FLEET_PRICING = {
        FleetPricingTier.TIER_1_5: 1495.00,   # 1-5 cranes: $1,495 ($299 per crane)
        FleetPricingTier.TIER_6_10: 2495.00,  # 6-10 cranes: $2,495 ($249 per crane)
        FleetPricingTier.TIER_11_25: 4995.00, # 11-25 cranes: $4,995 ($199 per crane)
        FleetPricingTier.TIER_26_50: 7995.00  # 26-50 cranes: $7,995 (~$159 per crane)
    }
    
    @staticmethod
    def calculate_fleet_price_by_units(unit_count: int) -> tuple[float, FleetPricingTier]:
        """
        Calculate Fleet Valuation price based on number of cranes
        
        Args:
            unit_count: Number of cranes (1-50)
            
        Returns:
            Tuple of (price, tier)
        """
        if unit_count <= 0 or unit_count > 50:
            raise ValueError("Fleet Valuation supports 1-50 cranes")
        
        if unit_count <= 5:
            return (1495.00, FleetPricingTier.TIER_1_5)
        elif unit_count <= 10:
            return (2495.00, FleetPricingTier.TIER_6_10)
        elif unit_count <= 25:
            return (4995.00, FleetPricingTier.TIER_11_25)
        else:  # 26-50
            return (7995.00, FleetPricingTier.TIER_26_50)
    
    @staticmethod
    def get_per_crane_cost(unit_count: int) -> float:
        """Get per-crane cost for a given unit count"""
        price, _ = FMVReportService.calculate_fleet_price_by_units(unit_count)
        return round(price / unit_count, 2)
    
    # Valid status transitions
    # DRAFT: Form filled, purchase clicked but payment not completed
    # SUBMITTED: Form filled, payment successful
    # IN_PROGRESS: Admin views report and changes status to in_progress
    # COMPLETED: Admin completes the FMV report
    # DELIVERED: Admin uploads PDF and clicks "Upload and send to customer"
    # NEED_MORE_INFO: Admin needs more information to complete report
    # OVERDUE: Admin didn't complete within 24 hours (calculated status, admin only)
    VALID_TRANSITIONS = {
        FMVReportStatus.DRAFT: [FMVReportStatus.SUBMITTED],  # Payment received moves to SUBMITTED
        FMVReportStatus.SUBMITTED: [
            FMVReportStatus.IN_PROGRESS, 
            FMVReportStatus.NEED_MORE_INFO,
            FMVReportStatus.COMPLETED,  # Allow admin to skip directly to completed
            FMVReportStatus.DELIVERED  # Allow admin to skip directly to delivered
        ],
        FMVReportStatus.IN_PROGRESS: [
            FMVReportStatus.COMPLETED, 
            FMVReportStatus.NEED_MORE_INFO,
            FMVReportStatus.DELIVERED  # Allow admin to skip to delivered
        ],
        FMVReportStatus.COMPLETED: [FMVReportStatus.DELIVERED],  # PDF ready, can deliver
        FMVReportStatus.DELIVERED: [],  # Final state - Email sent
        FMVReportStatus.NEED_MORE_INFO: [
            FMVReportStatus.IN_PROGRESS, 
            FMVReportStatus.SUBMITTED,
            FMVReportStatus.COMPLETED,  # Allow admin to move forward after info received
            FMVReportStatus.DELIVERED  # Allow admin to move forward after info received
        ],
        FMVReportStatus.OVERDUE: [
            FMVReportStatus.IN_PROGRESS, 
            FMVReportStatus.COMPLETED,
            FMVReportStatus.DELIVERED  # Allow admin to deliver overdue reports
        ]
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def can_submit_fmv_request(self, user: User) -> tuple:
        """
        Check if user can submit FMV request - Pay-per-use model
        For Fleet Valuation tier: Users get 5 valuations per payment, then must pay again
        For Spot Check and Professional: Pay-per-use (no limits, payment required each time)
        """
        # Pay-per-use model: All reports require payment
        # The payment check happens during report creation/payment processing
        # This method is mainly for validation, not limit enforcement
        return True, ""
    
    def calculate_fleet_price(self, tier: FleetPricingTier) -> float:
        """Calculate price for fleet valuation tier"""
        return self.FLEET_PRICING.get(tier, 0.0)
    
    def create_report(self, user_id: int, report_data: FMVReportCreate) -> FMVReport:
        """Create a new FMV report"""
        # Get user
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Check if user can submit - BUT allow if payment is successful (payment_intent_id in metadata)
        # This allows free tier users and users at limit to create reports after successful payment
        payment_intent_id = None
        payment_succeeded = False
        if report_data.metadata and isinstance(report_data.metadata, dict):
            payment_intent_id = report_data.metadata.get('payment_intent_id')
            payment_succeeded = report_data.metadata.get('payment_succeeded', False)
        
        # Pay-per-use model: Payment is required for all reports
        # If no payment intent or payment not succeeded, allow creation but report will be in payment_pending status
        # Users must complete payment to proceed
        
        # For Fleet Valuation: Check if user has remaining valuations from payment
        report_type_value = report_data.report_type.value if hasattr(report_data.report_type, 'value') else str(report_data.report_type)
        if report_type_value == "fleet_valuation" and payment_intent_id and payment_succeeded:
            from .fleet_usage_tracker import FleetUsageTracker
            tracker = FleetUsageTracker(self.db)
            can_create, message, usage_info = tracker.can_create_fleet_report(user_id, payment_intent_id)
            if not can_create:
                raise ValueError(message)
        
        # Prepare crane details - Pydantic aliases will convert camelCase to snake_case
        # Store both formats for maximum compatibility with frontend and admin panel
        crane_details_dict = report_data.crane_details.dict(exclude_none=True)
        
        # Create a dict with both snake_case (from Pydantic) and camelCase (from original input)
        # This ensures compatibility with both frontend (camelCase) and admin panel (checks both)
        crane_details = crane_details_dict.copy()
        
        # Add camelCase versions for fields that were converted by Pydantic aliases
        # This ensures the admin panel can find the data regardless of format
        field_mappings = {
            'crane_type': 'craneType',
            'operating_hours': 'operatingHours',
            'boom_length': 'boomLength',
            'jib_length': 'jibLength',
            'max_hook_height': 'maxHookHeight',
            'max_radius': 'maxRadius',
            'serial_number': 'serialNumber',
            'additional_specs': 'additionalSpecs',
            'special_features': 'specialFeatures',
            'usage_history': 'usageHistory'
        }
        
        # Add camelCase versions if snake_case exists
        for snake_key, camel_key in field_mappings.items():
            if snake_key in crane_details and camel_key not in crane_details:
                crane_details[camel_key] = crane_details[snake_key]
            # Also add snake_case if camelCase exists (for backward compatibility)
            elif camel_key in crane_details and snake_key not in crane_details:
                crane_details[snake_key] = crane_details[camel_key]
        
        service_records = [record.dict() for record in report_data.service_records] if report_data.service_records else None
        service_record_files = report_data.service_record_files if report_data.service_record_files else None
        
        # CRITICAL: If service_record_files is None/empty, check metadata for backup
        # This handles cases where files were uploaded but not passed correctly (manual entry, auto, etc.)
        if not service_record_files and report_data.metadata and isinstance(report_data.metadata, dict):
            # Check for service_record_file_urls in metadata (comma-separated or array)
            metadata_files = report_data.metadata.get('service_record_file_urls') or report_data.metadata.get('service_record_files')
            if metadata_files:
                if isinstance(metadata_files, str):
                    # Comma-separated string
                    service_record_files = [url.strip() for url in metadata_files.split(',') if url.strip()]
                elif isinstance(metadata_files, list):
                    service_record_files = metadata_files
                logger.info(f"📎 Found service_record_files in metadata: {len(service_record_files) if isinstance(service_record_files, list) else 1} files")
        
        # CRITICAL: Also check if service_record_files is empty but we have files in metadata
        # This ensures manual entry and auto-generated reports include their files
        if (not service_record_files or len(service_record_files) == 0) and report_data.metadata and isinstance(report_data.metadata, dict):
            # Try alternative metadata keys
            for key in ['service_record_file_urls', 'service_record_files', 'manual_entry_service_record_urls', 'uploaded_files']:
                metadata_files = report_data.metadata.get(key)
                if metadata_files:
                    if isinstance(metadata_files, str):
                        # Comma-separated string
                        parsed_files = [url.strip() for url in metadata_files.split(',') if url.strip()]
                        if parsed_files:
                            service_record_files = parsed_files
                            logger.info(f"📎 Found service_record_files in metadata.{key} (comma-separated): {len(parsed_files)} files")
                            break
                    elif isinstance(metadata_files, list):
                        if metadata_files:
                            service_record_files = metadata_files
                            logger.info(f"📎 Found service_record_files in metadata.{key} (array): {len(metadata_files)} files")
                            break
        
        # CRITICAL: For bulk processing, ensure bulk_file_url from crane_details is in service_record_files
        bulk_file_url = None
        crane_details_dict = report_data.crane_details.dict(exclude_none=True) if hasattr(report_data.crane_details, 'dict') else (report_data.crane_details if isinstance(report_data.crane_details, dict) else {})
        if crane_details_dict.get('bulk_file_url'):
            bulk_file_url = crane_details_dict.get('bulk_file_url')
        elif report_data.metadata and isinstance(report_data.metadata, dict) and report_data.metadata.get('bulk_file_url'):
            bulk_file_url = report_data.metadata.get('bulk_file_url')
        
        if bulk_file_url:
            # Ensure service_record_files is a list
            if not service_record_files:
                service_record_files = []
            elif not isinstance(service_record_files, list):
                service_record_files = [service_record_files] if service_record_files else []
            
            # Add bulk_file_url if not already in the list
            if bulk_file_url not in service_record_files:
                service_record_files.append(bulk_file_url)
                logger.info(f"✅ Added bulk_file_url to service_record_files: {bulk_file_url}")
        
        # Log service record files for debugging
        logger.info(f"📎 Service record files received: {service_record_files}")
        logger.info(f"📎 Service record files type: {type(service_record_files)}")
        if service_record_files:
            logger.info(f"📎 Service record files count: {len(service_record_files) if isinstance(service_record_files, list) else 1}")
            logger.info(f"📎 Service record files content: {service_record_files[:3] if isinstance(service_record_files, list) else service_record_files}")  # Log first 3 URLs
        else:
            logger.warning(f"⚠️ No service_record_files provided - report will be created without attachments")
        
        # Determine initial status
        initial_status = FMVReportStatus.DRAFT
        
        # Convert report_type to Enum if needed (FMVReportType is already imported at top)
        try:
            if isinstance(report_data.report_type, FMVReportType):
                report_type_enum = report_data.report_type
            elif hasattr(report_data.report_type, 'value'):
                # It's a Pydantic enum, get the value and convert to SQLAlchemy enum
                report_type_value = report_data.report_type.value
                logger.info(f"Converting Pydantic enum value '{report_type_value}' to FMVReportType enum")
                report_type_enum = FMVReportType(report_type_value)
            else:
                # It's a string, convert to enum
                report_type_str = str(report_data.report_type)
                logger.info(f"Converting string '{report_type_str}' to FMVReportType enum")
                report_type_enum = FMVReportType(report_type_str)
            logger.info(f"✅ Report type enum: {report_type_enum}, value: {report_type_enum.value}")
        except Exception as enum_error:
            logger.error(f"❌ Error converting report_type to enum: {enum_error}", exc_info=True)
            raise ValueError(f"Invalid report_type: {report_data.report_type}. Error: {str(enum_error)}")
        
        # Convert fleet_pricing_tier to Enum if needed (FleetPricingTier is already imported at top)
        fleet_tier_enum = None
        if report_data.fleet_pricing_tier:
            try:
                if isinstance(report_data.fleet_pricing_tier, FleetPricingTier):
                    fleet_tier_enum = report_data.fleet_pricing_tier
                elif hasattr(report_data.fleet_pricing_tier, 'value'):
                    fleet_tier_enum = FleetPricingTier(report_data.fleet_pricing_tier.value)
                else:
                    fleet_tier_enum = FleetPricingTier(str(report_data.fleet_pricing_tier))
                logger.info(f"✅ Fleet tier enum: {fleet_tier_enum}, value: {fleet_tier_enum.value if fleet_tier_enum else None}")
            except Exception as tier_error:
                logger.warning(f"⚠️ Error converting fleet_pricing_tier to enum: {tier_error}, using None")
                fleet_tier_enum = None
        
        # Create report
        logger.info(f"Creating FMVReport with: user_id={user_id}, report_type={report_type_enum}, status={initial_status}")
        logger.info(f"📎 Setting service_record_files on report: {service_record_files}")
        logger.info(f"📎 Service_record_files type: {type(service_record_files)}, is list: {isinstance(service_record_files, list)}")
        
        # CRITICAL: Ensure service_record_files is a list (not empty string)
        # IMPORTANT: Preserve empty arrays as empty arrays (not None) to ensure field is set in database
        if service_record_files is not None:
            if isinstance(service_record_files, str):
                # If it's a string, try to parse as JSON or treat as single URL
                try:
                    import json
                    service_record_files = json.loads(service_record_files)
                    # If parsed result is a list, filter it
                    if isinstance(service_record_files, list):
                        service_record_files = [f for f in service_record_files if f and str(f).strip()]
                except:
                    # Treat as single URL string
                    service_record_files = [service_record_files] if service_record_files.strip() else []
            elif isinstance(service_record_files, list):
                # Filter out empty/null URLs but preserve the list structure
                service_record_files = [f for f in service_record_files if f and str(f).strip()]
                # CRITICAL: Keep as empty array (not None) to ensure field is set in database
                # This allows frontend to distinguish between "not provided" (None) and "no files" ([])
            else:
                # Convert single value to list
                service_record_files = [service_record_files] if service_record_files else []
        
        logger.info(f"📎 Final service_record_files after processing: {service_record_files}")
        
        # CRITICAL: Store metadata from report_data if provided (for bulk processing pricing, etc.)
        report_metadata = None
        if report_data.metadata and isinstance(report_data.metadata, dict):
            report_metadata = report_data.metadata.copy()
            # CRITICAL: Remove empty bulk_file_url from metadata if it exists (empty string means it wasn't properly set)
            # The bulk_file_url should be in service_record_files instead
            if report_metadata.get('bulk_file_url') == '' or (report_metadata.get('bulk_file_url') and not str(report_metadata.get('bulk_file_url')).strip()):
                logger.warning(f"⚠️ Empty bulk_file_url in metadata, removing it. bulk_file_url should be in service_record_files instead.")
                # Don't remove the key, but log it - the URL should be in service_record_files
            logger.info(f"📋 Storing metadata in report: {list(report_metadata.keys())}")
        
        try:
            report = FMVReport(
                user_id=user_id,
                report_type=report_type_enum,
                status=initial_status,
                crane_details=crane_details,
                service_records=service_records,
                service_record_files=service_record_files,  # This should now be a list or None
                fleet_pricing_tier=fleet_tier_enum,
                unit_count=report_data.unit_count,
                payment_intent_id=payment_intent_id if payment_intent_id else None,  # Set payment_intent_id if provided in metadata
                report_metadata=report_metadata  # Store metadata for email service and other uses
            )
            logger.info(f"✅ FMVReport object created successfully")
            logger.info(f"📎 Report.service_record_files after creation: {report.service_record_files}")
            logger.info(f"📎 Report.service_record_files type after creation: {type(report.service_record_files)}")
        except Exception as create_error:
            logger.error(f"❌ Error creating FMVReport object: {create_error}", exc_info=True)
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise
        
        # If payment already succeeded, set payment status
        if payment_succeeded and payment_intent_id:
            report.payment_status = "succeeded"
            # Don't set amount_paid here - it will be set when mark_payment_received is called
        
        self.db.add(report)
        try:
            self.db.commit()
            self.db.refresh(report)
            logger.info(f"✅ DRAFT report {report.id} committed to database. Status: {report.status.value}, User: {user_id}")
            logger.info(f"📎 Report.service_record_files after commit and refresh: {report.service_record_files}")
        except Exception as commit_error:
            logger.error(f"❌ Failed to commit DRAFT report to database: {commit_error}", exc_info=True)
            self.db.rollback()
            raise
        
        # NOTE: Notifications are now created in the API endpoint (submit_fmv_report) 
        # to ensure consistent notification titles and messages across the application.
        # This prevents duplicate notifications and ensures all notifications use
        # the standardized format: "Complete Your FMV Report Payment - Report #{id}"
        logger.info(f"📧 Notifications will be created by API endpoint for DRAFT report {report.id}")
        
        # Send email notification for DRAFT report creation
        # IMPORTANT: Only send the REMINDER email (so user receives a single email)
        try:
            from ..services.fmv_email_service import FMVEmailService
            email_service = FMVEmailService()
            
                        # Get report type and amount (centralized pricing)
            report_type = report.report_type.value if hasattr(report.report_type, 'value') else str(report.report_type)
            try:
                if report_type == 'fleet_valuation':
                    amount = get_base_price_dollars(report_type, unit_count=report.unit_count or 1)
                else:
                    amount = get_base_price_dollars(report_type)
            except Exception:
                # Fallback to legacy defaults if pricing config is unavailable
                if report_type == 'spot_check':
                    amount = 250.00
                elif report_type == 'professional':
                    amount = 995.00
                elif report_type == 'fleet_valuation':
                    # Fall back to lowest fleet tier
                    amount = 1495.00
            
            # NOTE: Draft reminder email is now sent in the /submit endpoint, not here
            # This prevents duplicate emails. The service method only creates the report,
            # and the endpoint handles email sending to ensure emails are sent only once.
            logger.info(f"📧 Draft reminder email will be sent by /submit endpoint for report {report.id} (preventing duplicates)")
        except Exception as email_error:
            logger.error(f"❌ Failed to send DRAFT reminder email for report {report.id}: {email_error}", exc_info=True)
            # Don't fail report creation if email fails
        
        logger.info(f"Created FMV report {report.id} for user {user_id} with payment_intent_id: {payment_intent_id}")
        return report
    
    def submit_report(self, report_id: int, user_id: int) -> FMVReport:
        """Submit a draft report for processing"""
        report = self.db.query(FMVReport).filter(
            and_(FMVReport.id == report_id, FMVReport.user_id == user_id)
        ).first()
        
        if not report:
            raise ValueError("Report not found")
        
        if report.status != FMVReportStatus.DRAFT:
            raise ValueError(f"Cannot submit report in status: {report.status.value}")
        
        # Pay-per-use model: No monthly limits
        # Payment is required for each report submission
        # For Fleet Valuation: Check if user has remaining valuations from payment
        if report.payment_status == "succeeded" and report.amount_paid and report.amount_paid > 0:
            logger.info(f"Report {report_id} is already paid, allowing submission")
            
            # For Fleet Valuation: Verify remaining usage
            report_type_value = report.report_type.value if hasattr(report.report_type, 'value') else str(report.report_type)
            if report_type_value == "fleet_valuation" and report.payment_intent_id:
                from .fleet_usage_tracker import FleetUsageTracker
                tracker = FleetUsageTracker(self.db)
                can_create, message, usage_info = tracker.can_create_fleet_report(report.user_id, report.payment_intent_id)
                if not can_create:
                    raise ValueError(message)
        
        # Update status based on payment
        # If payment is received, move to SUBMITTED (Order Received)
        # If not paid, keep as DRAFT (Report Submitted but Not Paid)
        if report.payment_status == "succeeded" and report.amount_paid and report.amount_paid > 0:
            report.status = FMVReportStatus.SUBMITTED
            report.submitted_at = datetime.utcnow()
        else:
            # Keep as DRAFT - Report Submitted but Not Paid
            # submitted_at is not set until payment is received
            pass
        
        self.db.commit()
        self.db.refresh(report)
        
        logger.info(f"Submitted FMV report {report_id} by user {user_id}")
        return report
    
    def update_status(self, report_id: int, status_transition: StatusTransition, admin_user_id: Optional[int] = None) -> FMVReport:
        """Update report status with validation"""
        report = self.db.query(FMVReport).filter(FMVReport.id == report_id).first()
        
        if not report:
            raise ValueError("Report not found")
        
        # Normalize statuses to enums for consistent comparison/validation
        current_status = report.status
        new_status = status_transition.status

        # Convert string statuses to FMVReportStatus enums if needed
        if isinstance(current_status, str):
            try:
                current_status = FMVReportStatus(current_status)
            except ValueError:
                logger.warning(f"Unknown current_status string '{current_status}' for report {report_id}")
        if isinstance(new_status, str):
            try:
                new_status = FMVReportStatus(new_status)
            except ValueError:
                logger.warning(f"Unknown new_status string '{new_status}' for report {report_id}")
        
        # If status is the same, allow it (no-op)
        if current_status == new_status:
            logger.info(f"Report {report_id} already in status {new_status.value}, no change needed")
            return report
        
        # Validate transition - allow admin users more flexibility
        valid_transitions = self.VALID_TRANSITIONS.get(current_status, [])
        if new_status not in valid_transitions:
            # For admin users, allow more flexible transitions (except backwards from DELIVERED)
            if admin_user_id and new_status != FMVReportStatus.DRAFT:
                # Allow admin to transition to any forward status except DRAFT
                forward_statuses = [
                    FMVReportStatus.SUBMITTED,
                    FMVReportStatus.IN_PROGRESS,
                    FMVReportStatus.COMPLETED,
                    FMVReportStatus.DELIVERED,
                    FMVReportStatus.NEED_MORE_INFO
                ]
                if new_status in forward_statuses:
                    logger.info(f"Admin {admin_user_id} transitioning report {report_id} from {current_status.value} to {new_status.value} (admin override)")
                else:
                    raise ValueError(f"Invalid status transition from {current_status.value} to {new_status.value}")
            else:
                raise ValueError(f"Invalid status transition from {current_status.value} to {new_status.value}")
        
        # If transitioning to NEED_MORE_INFO, ensure the database enum supports this value
        if new_status == FMVReportStatus.NEED_MORE_INFO:
            try:
                from sqlalchemy import text
                from ..core.database import engine
                # Add enum value need_more_info to fmvreportstatus type if it doesn't exist
                with engine.begin() as conn:
                    conn.execute(text("""
                        DO $$
                        BEGIN
                            IF NOT EXISTS (
                                SELECT 1
                                FROM pg_type t
                                JOIN pg_enum e ON t.oid = e.enumtypid
                                WHERE t.typname = 'fmvreportstatus'
                                  AND e.enumlabel = 'need_more_info'
                            ) THEN
                                ALTER TYPE fmvreportstatus ADD VALUE 'need_more_info';
                            END IF;
                        END
                        $$;
                    """))
                logger.info("Ensured enum fmvreportstatus has value 'need_more_info'")
            except Exception as enum_error:
                logger.warning(f"Could not ensure enum value 'need_more_info' exists: {enum_error}")
        
        # Update status
        report.status = new_status
        now = datetime.utcnow()
        
        # Update timestamps based on status
        if new_status == FMVReportStatus.SUBMITTED:
            # SUBMITTED = Payment received
            report.submitted_at = now
            # Legacy: also set paid_at for backward compatibility
            if not report.paid_at:
                report.paid_at = now
            # Set turnaround deadline (24 hours from submission)
            from datetime import timedelta
            report.turnaround_deadline = now + timedelta(hours=24)
        elif new_status == FMVReportStatus.IN_PROGRESS:
            report.in_progress_at = now
            if status_transition.assigned_analyst:
                report.assigned_analyst = status_transition.assigned_analyst
        elif new_status == FMVReportStatus.COMPLETED:
            report.completed_at = now
        elif new_status == FMVReportStatus.DELIVERED:
            report.delivered_at = now
        elif new_status == FMVReportStatus.NEED_MORE_INFO:
            report.need_more_info_at = now
            # Store reason in need_more_info_reason field
            if hasattr(status_transition, 'rejection_reason') and status_transition.rejection_reason:
                report.need_more_info_reason = status_transition.rejection_reason
            elif hasattr(status_transition, 'analyst_notes') and status_transition.analyst_notes:
                report.need_more_info_reason = status_transition.analyst_notes
        elif new_status == FMVReportStatus.OVERDUE:
            report.overdue_at = now
        
        # Update analyst notes if provided
        if status_transition.analyst_notes:
            report.analyst_notes = status_transition.analyst_notes
        
        # First commit the report status change so it is not blocked by optional history table
        self.db.commit()
        self.db.refresh(report)
        
        # Try to create a status history entry; if the table does not exist, log and continue
        try:
            status_history = StatusHistory(
                report_id=report_id,
                old_status=current_status.value if hasattr(current_status, 'value') else str(current_status),
                new_status=new_status.value if hasattr(new_status, 'value') else str(new_status),
                changed_by=status_transition.changed_by if hasattr(status_transition, 'changed_by') else None,
                change_reason=status_transition.rejection_reason if hasattr(status_transition, 'rejection_reason') else None,
                notes=status_transition.analyst_notes if hasattr(status_transition, 'analyst_notes') else None
            )
            self.db.add(status_history)
            self.db.commit()
        except Exception as history_error:
            # Roll back only the history insert; the report status is already committed
            self.db.rollback()
            logger.warning(f"Status history logging failed for report {report_id}: {history_error}")
        
        logger.info(f"Updated FMV report {report_id} status from {current_status.value} to {new_status.value}")
        return report
    
    def update_report(self, report_id: int, update_data: FMVReportUpdate) -> FMVReport:
        """Update report fields"""
        report = self.db.query(FMVReport).filter(FMVReport.id == report_id).first()
        
        if not report:
            raise ValueError("Report not found")
        
        if update_data.analyst_notes is not None:
            report.analyst_notes = update_data.analyst_notes
        # Handle need_more_info_reason (can come from rejection_reason field for backward compatibility)
        if hasattr(update_data, 'need_more_info_reason') and update_data.need_more_info_reason is not None:
            report.need_more_info_reason = update_data.need_more_info_reason
        elif update_data.rejection_reason is not None:
            # Backward compatibility: rejection_reason maps to need_more_info_reason
            report.need_more_info_reason = update_data.rejection_reason
            report.rejection_reason = update_data.rejection_reason  # Keep for backward compatibility
        if update_data.assigned_analyst is not None:
            report.assigned_analyst = update_data.assigned_analyst
        if update_data.metadata is not None:
            report.report_metadata = update_data.metadata  # Use renamed attribute
        
        self.db.commit()
        self.db.refresh(report)
        
        return report
    
    def update_draft_report(self, report_id: int, user_id: int, update_data) -> FMVReport:
        """Update draft report fields (user-facing) - only allows updating DRAFT reports"""
        from ...schemas.fmv_report import FMVReportDraftUpdate
        import json
        
        report = self.db.query(FMVReport).filter(FMVReport.id == report_id).first()
        
        if not report:
            raise ValueError("Report not found")
        
        # Verify report belongs to user
        if report.user_id != user_id:
            raise ValueError("Report does not belong to user")
        
        # Only allow updating DRAFT reports
        if report.status != FMVReportStatus.DRAFT:
            raise ValueError("Can only update DRAFT reports")
        
        # Update report type if provided
        if update_data.report_type is not None:
            report.report_type = update_data.report_type
        
        # Update crane details if provided
        if update_data.crane_details is not None:
            if isinstance(update_data.crane_details, dict):
                report.crane_details = update_data.crane_details
            else:
                report.crane_details = update_data.crane_details.dict() if hasattr(update_data.crane_details, 'dict') else update_data.crane_details
        
        # Update service record files if provided
        if update_data.service_record_files is not None:
            # Merge with existing files, removing duplicates
            existing_files = report.service_record_files if report.service_record_files else []
            if isinstance(existing_files, str):
                try:
                    existing_files = json.loads(existing_files)
                except:
                    existing_files = [existing_files] if existing_files else []
            elif not isinstance(existing_files, list):
                existing_files = [existing_files] if existing_files else []
            
            new_files = update_data.service_record_files if isinstance(update_data.service_record_files, list) else [update_data.service_record_files]
            # Merge and deduplicate
            all_files = list(set(existing_files + new_files))
            report.service_record_files = all_files
            logger.info(f"✅ Updated draft report {report_id} service_record_files: {len(all_files)} total files")
        
        # Update metadata if provided
        if update_data.metadata is not None:
            existing_metadata = report.report_metadata if report.report_metadata else {}
            if isinstance(existing_metadata, str):
                try:
                    existing_metadata = json.loads(existing_metadata)
                except:
                    existing_metadata = {}
            existing_metadata.update(update_data.metadata)
            report.report_metadata = existing_metadata
        
        self.db.commit()
        self.db.refresh(report)
        
        logger.info(f"✅ Updated draft report {report_id} for user {user_id}")
        return report
    
    def get_user_reports(self, user_id: Optional[int] = None, status_filter: Optional[str] = None, exclude_cancelled: bool = True, include_deleted: bool = False) -> List[FMVReport]:
        """Get all reports for a user (or all reports if user_id is None - admin only)
        
        Args:
            user_id: User ID to filter by (None for admin/all reports)
            status_filter: Optional status filter
            exclude_cancelled: Whether to exclude cancelled/duplicate reports
            include_deleted: Whether to include DELETED reports (False for users, True for admin)
        """
        query = self.db.query(FMVReport)
        
        if user_id is not None:
            query = query.filter(FMVReport.user_id == user_id)
        
        if status_filter:
            # Handle status filter - convert string to enum if needed
            status_filter_lower = status_filter.lower()
            # Map invalid statuses (CANCELLED doesn't exist in enum)
            invalid_statuses = ["cancelled", "canceled"]
            
            if status_filter_lower in invalid_statuses:
                # Invalid status - return empty result
                return []
            
            try:
                # Try to match enum value
                status_enum = FMVReportStatus(status_filter)
                query = query.filter(FMVReport.status == status_enum)
            except ValueError:
                # If not a valid enum, try string comparison (case-insensitive)
                # Also try matching against enum value string
                query = query.filter(
                    or_(
                        FMVReport.status == status_filter,
                        cast(FMVReport.status, String).ilike(f"%{status_filter_lower}%")
                    )
                )
        
        # Get all matching reports
        all_reports = query.order_by(FMVReport.created_at.desc()).all()
        
        # Exclude DELETED reports only if include_deleted is False (for user queries)
        if not include_deleted:
            all_reports = [r for r in all_reports if r.status != FMVReportStatus.DELETED]
        
        # Exclude duplicate reports marked as need_more_info with duplicate reason
        if exclude_cancelled:
            all_reports = [r for r in all_reports if not (
                r.status == FMVReportStatus.NEED_MORE_INFO and 
                r.need_more_info_reason and 
                "Duplicate report" in r.need_more_info_reason
            )]
        
        # For user queries (user_id is not None), filter out draft reports if there's a SUBMITTED+ report with same payment_intent_id
        # This allows DRAFT reports (unpaid) to be shown separately from SUBMITTED reports (paid)
        # For admin queries (user_id is None), return ALL reports including DRAFT - no filtering
        if user_id is not None:
            # Group by payment_intent_id (only for reports that have one)
            payment_groups = {}
            for report in all_reports:
                if report.payment_intent_id:
                    if report.payment_intent_id not in payment_groups:
                        payment_groups[report.payment_intent_id] = []
                    payment_groups[report.payment_intent_id].append(report)
            
            # Only filter out draft reports if there's a SUBMITTED (or later) report with same payment_intent_id
            # This means: if user created a report, clicked purchase but didn't pay (DRAFT), then later paid (SUBMITTED),
            # we only show the SUBMITTED one. But if there's only a DRAFT (no payment), we show it.
            filtered_reports = []
            for report in all_reports:
                # If report has payment_intent_id, check if there's a SUBMITTED+ version
                if report.payment_intent_id and report.payment_intent_id in payment_groups:
                    group = payment_groups[report.payment_intent_id]
                    # Check if there's a SUBMITTED or later status report in this group
                    has_submitted_or_later = any(
                        r.status in [FMVReportStatus.SUBMITTED, FMVReportStatus.IN_PROGRESS, 
                                    FMVReportStatus.COMPLETED, FMVReportStatus.DELIVERED] 
                        for r in group
                    )
                    # Only exclude DRAFT if there's a SUBMITTED+ report with same payment_intent_id
                    if has_submitted_or_later and report.status == FMVReportStatus.DRAFT:
                        continue  # Skip this draft report (it was replaced by a paid version)
                # Include all other reports (DRAFT without payment_intent_id, or DRAFT with unique payment_intent_id)
                filtered_reports.append(report)
            
            return filtered_reports
        
        # Admin query (user_id is None): Return ALL reports including DRAFT - no filtering
        # This ensures admins can see all DRAFT reports in the admin panel
        return all_reports
    
    def get_report(self, report_id: int, user_id: Optional[int] = None) -> Optional[FMVReport]:
        """Get a specific report"""
        query = self.db.query(FMVReport).filter(FMVReport.id == report_id)
        
        if user_id:
            query = query.filter(FMVReport.user_id == user_id)
        
        return query.first()
    
    def get_report_timeline(self, report_id: int) -> List[Dict[str, Any]]:
        """Get timeline for a report"""
        report = self.get_report(report_id)
        if not report:
            raise ValueError("Report not found")
        
        return report.get_status_timeline()
    
    def get_report_by_payment_intent(self, payment_intent_id: str) -> Optional[FMVReport]:
        """Get report by payment intent ID"""
        return self.db.query(FMVReport).filter(FMVReport.payment_intent_id == payment_intent_id).first()
    
    def mark_payment_received(self, report_id: int, payment_intent_id: str, amount: float) -> FMVReport:
        """Mark payment as received and upgrade user subscription tier if needed"""
        # CRITICAL: First check if a report with this payment_intent_id already exists
        # This prevents duplicate reports when payment is received
        existing_report = self.get_report_by_payment_intent(payment_intent_id)
        if existing_report:
            if existing_report.id != report_id:
                logger.warning(f"⚠️ Payment intent {payment_intent_id} already associated with report {existing_report.id}. Using existing report instead of {report_id}")
                report = existing_report
                # Mark the duplicate report as DELETED (soft delete)
                duplicate_report = self.get_report(report_id)
                if duplicate_report:
                    duplicate_report.status = FMVReportStatus.DELETED
                    # deleted_at column doesn't exist in database, skip it
                    # duplicate_report.deleted_at = datetime.utcnow()
                    logger.info(f"✅ Marked duplicate report {report_id} as DELETED (replaced by report {existing_report.id} with same payment)")
                    self.db.commit()
            else:
                report = existing_report
        else:
            # No existing report with this payment_intent_id, use the provided report_id
            report = self.get_report(report_id)
            if not report:
                raise ValueError(f"Report {report_id} not found")
        
        report.payment_intent_id = payment_intent_id
        report.amount_paid = amount
        report.payment_status = "succeeded"
        # Payment received = Order Received = SUBMITTED status
        report.status = FMVReportStatus.SUBMITTED
        report.submitted_at = datetime.utcnow()
        # Legacy: also set paid_at for backward compatibility
        report.paid_at = datetime.utcnow()
        
        # Set turnaround deadline
        from .turnaround_tracker import TurnaroundTracker
        tracker = TurnaroundTracker(self.db)
        tracker.set_turnaround_deadline(report)
        
        # Pay-per-use model: Track payments and Fleet Valuation usage
        user = self.db.query(User).filter(User.id == report.user_id).first()
        if user:
            # Update total payments
            user.total_payments = (user.total_payments or 0) + amount
            
            # For Fleet Valuation: Track usage per payment (5 valuations per payment)
            # Store payment info in report metadata for tracking
            if not report.report_metadata:
                report.report_metadata = {}
            
            report_type_value = report.report_type.value if hasattr(report.report_type, 'value') else str(report.report_type)
            if report_type_value == "fleet_valuation":
                # Fleet Valuation: 5 valuations per payment
                report.report_metadata["valuations_included"] = 5
                report.report_metadata["valuations_used"] = 1
                report.report_metadata["payment_date"] = datetime.utcnow().isoformat()
                logger.info(f"✅ Fleet Valuation payment received: 5 valuations included, 1 used")
            else:
                # Spot Check and Professional: Single use per payment
                report.report_metadata["valuations_included"] = 1
                report.report_metadata["valuations_used"] = 1
                report.report_metadata["payment_date"] = datetime.utcnow().isoformat()
            
            logger.info(f"✅ Payment received for FMV report {report.id}: ${amount}")
        
        self.db.commit()
        self.db.refresh(report)
        if user:
            self.db.refresh(user)
        
        logger.info(f"✅ Payment received for FMV report {report.id}: ${amount}, status updated to {report.status.value}")
        return report
    
    def upload_pdf(self, report_id: int, pdf_url: str) -> FMVReport:
        """Upload PDF for a report"""
        report = self.get_report(report_id)
        if not report:
            raise ValueError("Report not found")
        
        report.pdf_url = pdf_url
        report.pdf_uploaded_at = datetime.utcnow()
        
        # If not already delivered, update status
        if report.status == FMVReportStatus.COMPLETED:
            report.status = FMVReportStatus.DELIVERED
            report.delivered_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(report)
        
        logger.info(f"PDF uploaded for FMV report {report_id}")
        return report
    
    def get_admin_stats(self) -> Dict[str, Any]:
        """Get statistics for admin dashboard"""
        total = self.db.query(FMVReport).count()
        # DRAFT = Form filled, purchase clicked but payment not completed
        draft = self.db.query(FMVReport).filter(FMVReport.status == FMVReportStatus.DRAFT).count()
        # SUBMITTED = Form filled, payment successful
        submitted = self.db.query(FMVReport).filter(FMVReport.status == FMVReportStatus.SUBMITTED).count()
        in_progress = self.db.query(FMVReport).filter(FMVReport.status == FMVReportStatus.IN_PROGRESS).count()
        completed = self.db.query(FMVReport).filter(FMVReport.status == FMVReportStatus.COMPLETED).count()
        delivered = self.db.query(FMVReport).filter(FMVReport.status == FMVReportStatus.DELIVERED).count()
        need_more_info = self.db.query(FMVReport).filter(FMVReport.status == FMVReportStatus.NEED_MORE_INFO).count()
        # OVERDUE = Calculated status (reports past 24-hour deadline)
        from datetime import datetime, timedelta
        overdue_count = self.db.query(FMVReport).filter(
            FMVReport.status == FMVReportStatus.SUBMITTED,
            FMVReport.submitted_at.isnot(None),
            FMVReport.submitted_at < datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        # Calculate total revenue
        total_revenue = self.db.query(FMVReport.amount_paid).filter(
            FMVReport.amount_paid.isnot(None)
        ).all()
        revenue_sum_cents = sum([r[0] for r in total_revenue if r[0]])
        # Convert from cents to dollars (amount_paid is stored in cents)
        revenue_sum = revenue_sum_cents / 100.0 if revenue_sum_cents else 0.0
        
        return {
            "total": total,
            "draft": draft,  # Form filled, purchase clicked but payment not completed
            "submitted": submitted,  # Form filled, payment successful
            "in_progress": in_progress,  # Admin views report and changes status to in_progress
            "completed": completed,  # Admin completes the FMV report
            "delivered": delivered,  # Admin uploads PDF and clicks "Upload and send to customer"
            "need_more_info": need_more_info,  # Admin needs more information to complete report
            "overdue": overdue_count,  # Admin didn't complete within 24 hours
            "total_revenue": revenue_sum
        }

