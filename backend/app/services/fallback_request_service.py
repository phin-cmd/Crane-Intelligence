"""
Fallback Request Service
Business logic for fallback request operations
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
import logging

from ..models.fallback_request import FallbackRequest, FallbackRequestStatus
from ..models.user import User
from ..schemas.fallback_request import FallbackRequestCreate, FallbackRequestUpdate

logger = logging.getLogger(__name__)


class FallbackRequestService:
    """Service for managing fallback requests"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_request(self, request_data: FallbackRequestCreate, user_id: Optional[int] = None) -> FallbackRequest:
        """Create a new fallback request"""
        # Get user email
        user_email = request_data.user_email
        if user_id:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                user_email = user.email
        
        if not user_email:
            raise ValueError("User email is required")
        
        # Create request
        request = FallbackRequest(
            user_id=user_id,
            user_email=user_email,
            manufacturer=request_data.manufacturer,
            model=request_data.model,
            year=request_data.year,
            serial_number=request_data.serial_number,
            capacity_tons=request_data.capacity_tons,
            crane_type=request_data.crane_type,
            operating_hours=request_data.operating_hours,
            mileage=request_data.mileage,
            boom_length=request_data.boom_length,
            jib_length=request_data.jib_length,
            max_hook_height=request_data.max_hook_height,
            max_radius=request_data.max_radius,
            region=request_data.region,
            condition=request_data.condition,
            additional_specs=request_data.additional_specs,
            special_features=request_data.special_features,
            usage_history=request_data.usage_history,
            status=FallbackRequestStatus.PENDING.value
        )
        
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        
        logger.info(f"Created fallback request {request.id} for user {user_email}")
        return request
    
    def get_request(self, request_id: int) -> Optional[FallbackRequest]:
        """Get a fallback request by ID"""
        return self.db.query(FallbackRequest).filter(FallbackRequest.id == request_id).first()
    
    def get_user_requests(self, user_id: Optional[int] = None, user_email: Optional[str] = None) -> List[FallbackRequest]:
        """Get all fallback requests for a user"""
        query = self.db.query(FallbackRequest)
        
        if user_id:
            query = query.filter(FallbackRequest.user_id == user_id)
        elif user_email:
            query = query.filter(FallbackRequest.user_email == user_email)
        else:
            # Admin: get all requests
            pass
        
        return query.order_by(FallbackRequest.created_at.desc()).all()
    
    def get_all_requests(self, status_filter: Optional[str] = None) -> List[FallbackRequest]:
        """Get all fallback requests (admin only)"""
        query = self.db.query(FallbackRequest)
        
        if status_filter:
            query = query.filter(FallbackRequest.status == status_filter)
        
        return query.order_by(FallbackRequest.created_at.desc()).all()
    
    def update_request(self, request_id: int, update_data: FallbackRequestUpdate) -> FallbackRequest:
        """Update a fallback request (admin only)"""
        request = self.get_request(request_id)
        if not request:
            raise ValueError("Fallback request not found")
        
        # Update status and timestamps
        if update_data.status:
            old_status = request.status
            request.status = update_data.status
            
            # Update timestamps based on status
            now = datetime.utcnow()
            if update_data.status == FallbackRequestStatus.IN_REVIEW.value and not request.in_review_at:
                request.in_review_at = now
            elif update_data.status == FallbackRequestStatus.VALUATION_IN_PROGRESS.value and not request.valuation_started_at:
                request.valuation_started_at = now
            elif update_data.status == FallbackRequestStatus.COMPLETED.value and not request.completed_at:
                request.completed_at = now
            elif update_data.status == FallbackRequestStatus.REJECTED.value and not request.rejected_at:
                request.rejected_at = now
            elif update_data.status == FallbackRequestStatus.CANCELLED.value and not request.cancelled_at:
                request.cancelled_at = now
        
        if update_data.assigned_analyst is not None:
            request.assigned_analyst = update_data.assigned_analyst
        
        if update_data.analyst_notes is not None:
            request.analyst_notes = update_data.analyst_notes
        
        if update_data.rejection_reason is not None:
            request.rejection_reason = update_data.rejection_reason
        
        if update_data.linked_fmv_report_id is not None:
            request.linked_fmv_report_id = update_data.linked_fmv_report_id
        
        self.db.commit()
        self.db.refresh(request)
        
        logger.info(f"Updated fallback request {request_id}")
        return request

