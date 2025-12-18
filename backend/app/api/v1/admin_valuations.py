"""
Admin Valuations Management API
CRUD operations for valuation records
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from ...core.database import get_db
from ...models.user import UsageLog
from ...models.equipment import ValuationRecord
from ...core.admin_auth import get_current_admin_user, require_admin_or_super_admin
from ...models.admin import AdminUser

router = APIRouter(prefix="/admin/valuations", tags=["admin-valuations"])


class ValuationResponse(BaseModel):
    id: int
    user_id: int
    action_type: str
    endpoint: str
    timestamp: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]
    success: bool
    error_message: Optional[str]
    crane_manufacturer: Optional[str]
    crane_model: Optional[str]
    crane_capacity: Optional[float]

    class Config:
        from_attributes = True


@router.get("", response_model=List[ValuationResponse])
async def list_valuations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[int] = None,
    action_type: Optional[str] = None,
    success: Optional[bool] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """List all valuation records with optional filters"""
    query = db.query(UsageLog).filter(UsageLog.action_type == 'valuation')
    
    if user_id:
        query = query.filter(UsageLog.user_id == user_id)
    if action_type:
        query = query.filter(UsageLog.action_type == action_type)
    if success is not None:
        query = query.filter(UsageLog.success == success)
    if start_date:
        query = query.filter(UsageLog.timestamp >= start_date)
    if end_date:
        query = query.filter(UsageLog.timestamp <= end_date)
    
    valuations = query.order_by(UsageLog.timestamp.desc()).offset(skip).limit(limit).all()
    return valuations


@router.get("/{valuation_id}", response_model=ValuationResponse)
async def get_valuation(
    valuation_id: int,
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """Get a specific valuation by ID"""
    valuation = db.query(UsageLog).filter(
        UsageLog.id == valuation_id,
        UsageLog.action_type == 'valuation'
    ).first()
    if not valuation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Valuation not found"
        )
    return valuation


@router.delete("/{valuation_id}")
async def delete_valuation(
    valuation_id: int,
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """Delete a valuation record"""
    valuation = db.query(UsageLog).filter(
        UsageLog.id == valuation_id,
        UsageLog.action_type == 'valuation'
    ).first()
    if not valuation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Valuation not found"
        )
    
    db.delete(valuation)
    db.commit()
    
    return {"message": "Valuation deleted successfully"}


@router.get("/stats/summary")
async def get_valuation_stats(
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """Get valuation statistics summary"""
    total_valuations = db.query(UsageLog).filter(UsageLog.action_type == 'valuation').count()
    successful_valuations = db.query(UsageLog).filter(
        UsageLog.action_type == 'valuation',
        UsageLog.success == True
    ).count()
    failed_valuations = total_valuations - successful_valuations
    
    # Get valuations by date range
    today = datetime.utcnow().date()
    today_valuations = db.query(UsageLog).filter(
        UsageLog.action_type == 'valuation',
        UsageLog.timestamp >= datetime.combine(today, datetime.min.time())
    ).count()
    
    # Get this month's valuations
    from datetime import date
    first_day_month = date.today().replace(day=1)
    month_valuations = db.query(UsageLog).filter(
        UsageLog.action_type == 'valuation',
        UsageLog.timestamp >= datetime.combine(first_day_month, datetime.min.time())
    ).count()
    
    return {
        "total": total_valuations,
        "successful": successful_valuations,
        "failed": failed_valuations,
        "today": today_valuations,
        "this_month": month_valuations,
        "success_rate": (successful_valuations / total_valuations * 100) if total_valuations > 0 else 0
    }

