"""
Admin Payments/Billing Management API
CRUD operations for payment and billing records
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from ...core.database import get_db
from ...models.user import User
from ...models.fmv_report import FMVReport
from ...core.admin_auth import get_current_admin_user, require_admin_or_super_admin, require_can_view_financial_data
from ...models.admin import AdminUser

router = APIRouter(prefix="/admin/payments", tags=["admin-payments"])


class PaymentResponse(BaseModel):
    user_id: int
    user_email: str
    user_name: str
    total_payments: float
    payment_intent_id: Optional[str]
    amount_paid: Optional[float]
    payment_status: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]


class BillingHistoryResponse(BaseModel):
    id: int
    user_id: int
    user_email: str
    amount: float
    payment_intent_id: Optional[str]
    payment_status: str
    report_id: Optional[int]
    created_at: datetime


@router.get("", response_model=List[PaymentResponse])
async def list_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[int] = None,
    subscription_tier: Optional[str] = None,
    current_user: AdminUser = Depends(require_can_view_financial_data),
    db: Session = Depends(get_db)
):
    """List all payment records"""
    query = db.query(User)
    
    if user_id:
        query = query.filter(User.id == user_id)
    
    users = query.offset(skip).limit(limit).all()
    
    return [
        PaymentResponse(
            user_id=u.id,
            user_email=u.email,
            user_name=u.full_name,
            total_payments=u.total_payments or 0.0,
            subscription_tier=u.subscription_tier.value if hasattr(u.subscription_tier, 'value') else str(u.subscription_tier),
            payment_intent_id=None,  # Would need to track this separately
            amount_paid=u.total_payments,
            payment_status="completed" if u.total_payments > 0 else "pending",
            created_at=u.created_at,
            updated_at=u.updated_at
        )
        for u in users
    ]


@router.get("/billing-history", response_model=List[BillingHistoryResponse])
async def get_billing_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: AdminUser = Depends(require_can_view_financial_data),
    db: Session = Depends(get_db)
):
    """Get billing history from FMV reports (which track payments)"""
    query = db.query(FMVReport).filter(FMVReport.amount_paid.isnot(None))
    
    if user_id:
        query = query.filter(FMVReport.user_id == user_id)
    if start_date:
        query = query.filter(FMVReport.paid_at >= start_date)
    if end_date:
        query = query.filter(FMVReport.paid_at <= end_date)
    
    reports = query.order_by(FMVReport.paid_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for report in reports:
        user = db.query(User).filter(User.id == report.user_id).first()
        result.append(BillingHistoryResponse(
            id=report.id,
            user_id=report.user_id,
            user_email=user.email if user else "Unknown",
            amount=report.amount_paid or 0.0,
            payment_intent_id=report.payment_intent_id,
            payment_status=report.payment_status or "completed",
            subscription_tier=report.subscription_tier,
            report_id=report.id,
            created_at=report.paid_at or report.created_at
        ))
    
    return result


@router.get("/stats/summary")
async def get_payment_stats(
    current_user: AdminUser = Depends(require_can_view_financial_data),
    db: Session = Depends(get_db)
):
    """Get payment statistics summary"""
    # Total revenue
    total_revenue = db.query(User).with_entities(
        db.func.sum(User.total_payments)
    ).scalar() or 0.0
    
    # Revenue by user role (subscription tiers removed)
    users_by_role = db.query(
        User.user_role,
        db.func.count(User.id).label('count'),
        db.func.sum(User.total_payments).label('revenue')
    ).group_by(User.user_role).all()
    
    role_stats = {}
    for role, count, revenue in users_by_role:
        role_name = role.value if hasattr(role, 'value') else str(role)
        role_stats[role_name] = {
            "count": count,
            "revenue": float(revenue or 0.0)
        }
    
    # Today's revenue
    today = datetime.utcnow().date()
    today_revenue_cents = db.query(FMVReport).with_entities(
        db.func.sum(FMVReport.amount_paid)
    ).filter(
        FMVReport.paid_at >= datetime.combine(today, datetime.min.time())
    ).scalar() or 0.0
    # Convert from cents to dollars (amount_paid is stored in cents)
    today_revenue = float(today_revenue_cents) / 100.0 if today_revenue_cents else 0.0
    
    # This month's revenue
    from datetime import date
    first_day_month = date.today().replace(day=1)
    month_revenue_cents = db.query(FMVReport).with_entities(
        db.func.sum(FMVReport.amount_paid)
    ).filter(
        FMVReport.paid_at >= datetime.combine(first_day_month, datetime.min.time())
    ).scalar() or 0.0
    # Convert from cents to dollars (amount_paid is stored in cents)
    month_revenue = float(month_revenue_cents) / 100.0 if month_revenue_cents else 0.0
    
    return {
        "total_revenue": float(total_revenue),
        "today_revenue": today_revenue,
        "month_revenue": month_revenue,
        "by_role": role_stats,
        "total_users": db.query(User).filter(User.total_payments > 0).count()
    }


@router.get("/{user_id}/history")
async def get_user_billing_history(
    user_id: int,
    current_user: AdminUser = Depends(require_can_view_financial_data),
    db: Session = Depends(get_db)
):
    """Get billing history for a specific user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    reports = db.query(FMVReport).filter(
        FMVReport.user_id == user_id,
        FMVReport.amount_paid.isnot(None)
    ).order_by(FMVReport.paid_at.desc()).all()
    
    return [
        {
            "id": r.id,
            "amount": r.amount_paid,
            "payment_intent_id": r.payment_intent_id,
            "payment_status": r.payment_status,
            "report_type": r.report_type.value if hasattr(r.report_type, 'value') else str(r.report_type),
            "paid_at": r.paid_at,
            "created_at": r.created_at
        }
        for r in reports
    ]

