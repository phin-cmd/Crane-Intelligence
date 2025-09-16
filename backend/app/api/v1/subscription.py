from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from ...services.subscription_service import SubscriptionService
from ...schemas.subscription import (
    EmailSubscriptionCreate, 
    EmailSubscriptionResponse,
    UnsubscribeRequest,
    SubscriptionStatusResponse,
    BulkUnsubscribeRequest,
    EmailPreferencesUpdate
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/subscribe", response_model=dict)
async def subscribe_email(
    subscription_data: EmailSubscriptionCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Subscribe an email to the newsletter/blog updates
    """
    try:
        # Get client IP and User Agent
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "")
        
        # If behind a proxy, get real IP
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        subscription_service = SubscriptionService(db)
        result = subscription_service.subscribe_email(
            subscription_data=subscription_data,
            ip_address=client_ip,
            user_agent=user_agent
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "data": {
                    "email": subscription_data.email,
                    "subscription_type": subscription_data.subscription_type,
                    "already_subscribed": result.get("already_subscribed", False)
                }
            }
        else:
            return {
                "success": False,
                "message": result["message"],
                "error": result.get("error", "subscription_failed")
            }
            
    except Exception as e:
        logger.error(f"Error in subscribe_email endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred"
        )


@router.post("/unsubscribe", response_model=dict)
async def unsubscribe_email(
    unsubscribe_data: UnsubscribeRequest,
    db: Session = Depends(get_db)
):
    """
    Unsubscribe an email from the newsletter
    """
    try:
        subscription_service = SubscriptionService(db)
        result = subscription_service.unsubscribe_email(
            email=unsubscribe_data.email,
            token=unsubscribe_data.token
        )
        
        return {
            "success": result["success"],
            "message": result["message"],
            "already_unsubscribed": result.get("already_unsubscribed", False)
        }
        
    except Exception as e:
        logger.error(f"Error in unsubscribe_email endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred"
        )


@router.get("/status/{email}", response_model=SubscriptionStatusResponse)
async def get_subscription_status(
    email: str,
    db: Session = Depends(get_db)
):
    """
    Check subscription status for an email
    """
    try:
        subscription_service = SubscriptionService(db)
        result = subscription_service.get_subscription_status(email)
        
        return SubscriptionStatusResponse(
            email=email,
            is_subscribed=result["is_subscribed"],
            subscription_type=result.get("subscription_type"),
            subscribed_at=result.get("subscribed_at"),
            status=result.get("status", "unknown")
        )
        
    except Exception as e:
        logger.error(f"Error in get_subscription_status endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred"
        )


@router.get("/generate-unsubscribe-token/{email}", response_model=dict)
async def generate_unsubscribe_token(
    email: str,
    db: Session = Depends(get_db)
):
    """
    Generate an unsubscribe token for an email (for email links)
    """
    try:
        subscription_service = SubscriptionService(db)
        
        # Check if email is subscribed
        status_result = subscription_service.get_subscription_status(email)
        if not status_result["is_subscribed"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not found in subscription list"
            )
        
        token = subscription_service.generate_unsubscribe_token(email)
        
        return {
            "success": True,
            "email": email,
            "unsubscribe_token": token,
            "unsubscribe_url": f"/api/v1/subscription/unsubscribe?email={email}&token={token}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in generate_unsubscribe_token endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred"
        )


@router.get("/unsubscribe", response_model=dict)
async def unsubscribe_with_token(
    email: str,
    token: str,
    db: Session = Depends(get_db)
):
    """
    Unsubscribe using email and token (for email links)
    """
    try:
        subscription_service = SubscriptionService(db)
        result = subscription_service.unsubscribe_email(email=email, token=token)
        
        return {
            "success": result["success"],
            "message": result["message"]
        }
        
    except Exception as e:
        logger.error(f"Error in unsubscribe_with_token endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred"
        )


@router.put("/preferences/{email}", response_model=dict)
async def update_subscription_preferences(
    email: str,
    preferences_data: EmailPreferencesUpdate,
    db: Session = Depends(get_db)
):
    """
    Update subscription preferences for an email
    """
    try:
        subscription_service = SubscriptionService(db)
        result = subscription_service.update_subscription_preferences(
            email=email,
            preferences=preferences_data.preferences
        )
        
        return {
            "success": result["success"],
            "message": result["message"]
        }
        
    except Exception as e:
        logger.error(f"Error in update_subscription_preferences endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred"
        )


@router.get("/stats", response_model=dict)
async def get_subscription_stats(
    db: Session = Depends(get_db)
):
    """
    Get subscription statistics (admin endpoint)
    """
    try:
        subscription_service = SubscriptionService(db)
        stats = subscription_service.get_subscription_stats()
        
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error in get_subscription_stats endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred"
        )


@router.get("/list", response_model=List[EmailSubscriptionResponse])
async def list_subscriptions(
    status: str = None,
    subscription_type: str = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    List all subscriptions with optional filtering (admin endpoint)
    """
    try:
        subscription_service = SubscriptionService(db)
        subscriptions = subscription_service.get_all_subscriptions(
            status=status,
            subscription_type=subscription_type,
            limit=limit,
            offset=offset
        )
        
        return subscriptions
        
    except Exception as e:
        logger.error(f"Error in list_subscriptions endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred"
        )


@router.post("/bulk-unsubscribe", response_model=dict)
async def bulk_unsubscribe(
    bulk_data: BulkUnsubscribeRequest,
    db: Session = Depends(get_db)
):
    """
    Bulk unsubscribe multiple emails (admin endpoint)
    """
    try:
        subscription_service = SubscriptionService(db)
        results = []
        
        for email in bulk_data.emails:
            result = subscription_service.unsubscribe_email(email=email)
            results.append({
                "email": email,
                "success": result["success"],
                "message": result["message"]
            })
        
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful
        
        return {
            "success": True,
            "message": f"Processed {len(results)} emails. {successful} successful, {failed} failed.",
            "results": results,
            "summary": {
                "total": len(results),
                "successful": successful,
                "failed": failed
            }
        }
        
    except Exception as e:
        logger.error(f"Error in bulk_unsubscribe endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred"
        )
