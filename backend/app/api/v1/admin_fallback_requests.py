"""
Admin Fallback Requests API Endpoints
Handles admin-specific fallback request management
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.admin_auth import get_current_admin_user
from ...services.fallback_request_service import FallbackRequestService
from ...schemas.fallback_request import FallbackRequestResponse, FallbackRequestUpdate
from ...models.fallback_request import FallbackRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/fallback-requests", tags=["Admin Fallback Requests"])


def convert_fallback_to_response(request: FallbackRequest) -> FallbackRequestResponse:
    """Convert FallbackRequest model to response schema"""
    return FallbackRequestResponse(
        id=request.id,
        user_id=request.user_id,
        user_email=request.user_email,
        manufacturer=request.manufacturer,
        model=request.model,
        year=request.year,
        serial_number=request.serial_number,
        capacity_tons=request.capacity_tons,
        crane_type=request.crane_type,
        operating_hours=request.operating_hours,
        mileage=request.mileage,
        boom_length=request.boom_length,
        jib_length=request.jib_length,
        max_hook_height=request.max_hook_height,
        max_radius=request.max_radius,
        region=request.region,
        condition=request.condition,
        additional_specs=request.additional_specs,
        special_features=request.special_features,
        usage_history=request.usage_history,
        status=request.status,
        assigned_analyst=request.assigned_analyst,
        analyst_notes=request.analyst_notes,
        rejection_reason=request.rejection_reason,
        linked_fmv_report_id=request.linked_fmv_report_id,
        created_at=request.created_at,
        in_review_at=request.in_review_at,
        valuation_started_at=request.valuation_started_at,
        completed_at=request.completed_at,
        rejected_at=request.rejected_at,
        cancelled_at=request.cancelled_at,
        updated_at=request.updated_at
    )


@router.get("", response_model=Dict[str, Any])
async def get_admin_fallback_requests(
    status_filter: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all fallback requests for admin (with filters)"""
    try:
        service = FallbackRequestService(db)
        requests = service.get_all_requests(status_filter)
        
        # Apply pagination
        total = len(requests)
        paginated_requests = requests[offset:offset + limit]
        
        return {
            "success": True,
            "requests": [convert_fallback_to_response(req).dict() for req in paginated_requests],
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting admin fallback requests: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve fallback requests")


@router.get("/{request_id}", response_model=FallbackRequestResponse)
async def get_fallback_request(
    request_id: int,
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get a specific fallback request by ID"""
    try:
        service = FallbackRequestService(db)
        request = service.get_request(request_id)
        
        if not request:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fallback request not found")
        
        return convert_fallback_to_response(request)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting fallback request: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve fallback request")


@router.put("/{request_id}", response_model=FallbackRequestResponse)
async def update_fallback_request(
    request_id: int,
    update_data: FallbackRequestUpdate,
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update a fallback request (admin only)"""
    try:
        service = FallbackRequestService(db)
        request = service.update_request(request_id, update_data)
        
        return convert_fallback_to_response(request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating fallback request: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update fallback request")


@router.get("/stats/summary", response_model=Dict[str, Any])
async def get_fallback_stats(
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get statistics for fallback requests"""
    try:
        service = FallbackRequestService(db)
        all_requests = service.get_all_requests()
        
        stats = {
            "total": len(all_requests),
            "pending": len([r for r in all_requests if r.status == "pending"]),
            "in_review": len([r for r in all_requests if r.status == "in_review"]),
            "valuation_in_progress": len([r for r in all_requests if r.status == "valuation_in_progress"]),
            "completed": len([r for r in all_requests if r.status == "completed"]),
            "rejected": len([r for r in all_requests if r.status == "rejected"])
        }
        
        return {"success": True, "stats": stats}
    except Exception as e:
        logger.error(f"Error getting fallback stats: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve stats")

