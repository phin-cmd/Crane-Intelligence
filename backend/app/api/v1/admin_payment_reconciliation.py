"""
Payment Reconciliation and Refund Management API
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import stripe

from ...core.database import get_db
from ...models.admin import AdminUser
from ...models.payment import Payment, Refund, PaymentStatus, RefundStatus
from ...models.user import User
from ...core.admin_auth import require_can_view_financial_data, get_current_admin_user
from ...core.config import settings

router = APIRouter(prefix="/admin/payments", tags=["admin-payment-reconciliation"])

# Initialize Stripe (if API key is available)
try:
    stripe.api_key = settings.stripe_secret_key if hasattr(settings, 'stripe_secret_key') else None
except:
    stripe.api_key = None


class ReconciliationResponse(BaseModel):
    """Response for payment reconciliation"""
    payment_id: int
    stripe_payment_intent_id: Optional[str]
    user_id: int
    user_email: str
    amount: float
    status: str
    is_reconciled: bool
    matched: bool
    match_reason: Optional[str] = None


class RefundRequest(BaseModel):
    """Request to create a refund"""
    payment_id: int
    amount: Optional[float] = None  # If None, full refund
    reason: str = "requested_by_customer"
    admin_notes: Optional[str] = None


class RefundResponse(BaseModel):
    """Response for refund"""
    id: int
    payment_id: int
    amount: float
    status: str
    reason: Optional[str]
    stripe_refund_id: Optional[str]
    created_at: datetime


@router.get("/reconcile", response_model=List[ReconciliationResponse])
async def reconcile_payments(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    unreconciled_only: bool = Query(True),
    current_user: AdminUser = Depends(require_can_view_financial_data),
    db: Session = Depends(get_db)
):
    """Reconcile payments with Stripe"""
    query = db.query(Payment)
    
    if unreconciled_only:
        query = query.filter(Payment.is_reconciled == False)
    
    if start_date:
        query = query.filter(Payment.created_at >= start_date)
    if end_date:
        query = query.filter(Payment.created_at <= end_date)
    
    payments = query.order_by(Payment.created_at.desc()).limit(100).all()
    
    results = []
    for payment in payments:
        user = db.query(User).filter(User.id == payment.user_id).first()
        
        matched = False
        match_reason = None
        
        # Try to match with Stripe if payment intent ID exists
        if payment.stripe_payment_intent_id and stripe.api_key:
            try:
                stripe_payment = stripe.PaymentIntent.retrieve(payment.stripe_payment_intent_id)
                if stripe_payment.status == "succeeded" and abs(stripe_payment.amount / 100 - payment.amount) < 0.01:
                    matched = True
                    match_reason = "Stripe payment intent matched"
            except Exception as e:
                match_reason = f"Stripe error: {str(e)}"
        
        results.append(ReconciliationResponse(
            payment_id=payment.id,
            stripe_payment_intent_id=payment.stripe_payment_intent_id,
            user_id=payment.user_id,
            user_email=user.email if user else "Unknown",
            amount=payment.amount,
            status=payment.status,
            is_reconciled=payment.is_reconciled,
            matched=matched,
            match_reason=match_reason
        ))
    
    return results


@router.post("/reconcile/{payment_id}")
async def mark_payment_reconciled(
    payment_id: int,
    current_user: AdminUser = Depends(require_can_view_financial_data),
    db: Session = Depends(get_db)
):
    """Mark a payment as reconciled"""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    payment.is_reconciled = True
    payment.reconciled_at = datetime.utcnow()
    payment.reconciled_by = current_user.id
    db.commit()
    
    return {"message": "Payment marked as reconciled"}


@router.post("/reconcile/batch")
async def batch_reconcile_payments(
    payment_ids: List[int],
    current_user: AdminUser = Depends(require_can_view_financial_data),
    db: Session = Depends(get_db)
):
    """Batch mark payments as reconciled"""
    payments = db.query(Payment).filter(Payment.id.in_(payment_ids)).all()
    
    for payment in payments:
        payment.is_reconciled = True
        payment.reconciled_at = datetime.utcnow()
        payment.reconciled_by = current_user.id
    
    db.commit()
    
    return {"message": f"Marked {len(payments)} payments as reconciled"}


@router.post("/refund", response_model=RefundResponse)
async def create_refund(
    refund_request: RefundRequest,
    current_user: AdminUser = Depends(require_can_view_financial_data),
    db: Session = Depends(get_db)
):
    """Create a refund for a payment"""
    payment = db.query(Payment).filter(Payment.id == refund_request.payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Determine refund amount
    refund_amount = refund_request.amount if refund_request.amount else payment.amount
    
    # Check if refund amount is valid
    if refund_amount > payment.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refund amount cannot exceed payment amount"
        )
    
    # Check existing refunds
    existing_refunds = db.query(Refund).filter(
        Refund.payment_id == payment.id,
        Refund.status.in_([RefundStatus.COMPLETED.value, RefundStatus.PROCESSING.value])
    ).all()
    
    total_refunded = sum(r.amount for r in existing_refunds)
    if total_refunded + refund_amount > payment.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Total refund amount cannot exceed payment amount"
        )
    
    # Create refund record
    refund = Refund(
        payment_id=payment.id,
        user_id=payment.user_id,
        amount=refund_amount,
        reason=refund_request.reason,
        admin_notes=refund_request.admin_notes,
        processed_by=current_user.id,
        status=RefundStatus.PENDING.value
    )
    
    db.add(refund)
    db.commit()
    
    # Process refund with Stripe if payment intent exists
    stripe_refund_id = None
    if payment.stripe_payment_intent_id and stripe.api_key:
        try:
            # Create refund in Stripe
            stripe_refund = stripe.Refund.create(
                payment_intent=payment.stripe_payment_intent_id,
                amount=int(refund_amount * 100),  # Convert to cents
                reason=refund_request.reason
            )
            stripe_refund_id = stripe_refund.id
            refund.stripe_refund_id = stripe_refund_id
            refund.status = RefundStatus.COMPLETED.value
            refund.processed_at = datetime.utcnow()
        except Exception as e:
            refund.status = RefundStatus.FAILED.value
            refund.admin_notes = f"Stripe refund failed: {str(e)}"
    
    # Update payment status
    if refund.status == RefundStatus.COMPLETED.value:
        if refund_amount == payment.amount:
            payment.status = PaymentStatus.REFUNDED.value
        else:
            payment.status = PaymentStatus.PARTIALLY_REFUNDED.value
    
    db.commit()
    db.refresh(refund)
    
    return RefundResponse(
        id=refund.id,
        payment_id=refund.payment_id,
        amount=refund.amount,
        status=refund.status,
        reason=refund.reason,
        stripe_refund_id=refund.stripe_refund_id,
        created_at=refund.created_at
    )


@router.get("/refunds", response_model=List[RefundResponse])
async def list_refunds(
    payment_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: AdminUser = Depends(require_can_view_financial_data),
    db: Session = Depends(get_db)
):
    """List all refunds"""
    query = db.query(Refund)
    
    if payment_id:
        query = query.filter(Refund.payment_id == payment_id)
    if user_id:
        query = query.filter(Refund.user_id == user_id)
    if status:
        query = query.filter(Refund.status == status)
    if start_date:
        query = query.filter(Refund.created_at >= start_date)
    if end_date:
        query = query.filter(Refund.created_at <= end_date)
    
    refunds = query.order_by(Refund.created_at.desc()).limit(100).all()
    
    return [
        RefundResponse(
            id=r.id,
            payment_id=r.payment_id,
            amount=r.amount,
            status=r.status,
            reason=r.reason,
            stripe_refund_id=r.stripe_refund_id,
            created_at=r.created_at
        )
        for r in refunds
    ]


@router.get("/refunds/{refund_id}", response_model=RefundResponse)
async def get_refund(
    refund_id: int,
    current_user: AdminUser = Depends(require_can_view_financial_data),
    db: Session = Depends(get_db)
):
    """Get a specific refund"""
    refund = db.query(Refund).filter(Refund.id == refund_id).first()
    if not refund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Refund not found"
        )
    
    return RefundResponse(
        id=refund.id,
        payment_id=refund.payment_id,
        amount=refund.amount,
        status=refund.status,
        reason=refund.reason,
        stripe_refund_id=refund.stripe_refund_id,
        created_at=refund.created_at
    )

