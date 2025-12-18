"""
Draft Report Reminder API
Handles scheduled reminders for draft reports
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any

from ...core.database import get_db
from ...services.draft_reminder_scheduler import send_draft_reminders

router = APIRouter(prefix="/draft-reminders", tags=["Draft Reminders"])


class ReminderResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any]
    error: str = None


@router.post("/send", response_model=ReminderResponse)
async def send_reminders(db: Session = Depends(get_db)):
    """
    Manually trigger draft report reminder emails
    This endpoint sends reminders for all draft reports that are due
    (every 8 hours after creation)
    """
    try:
        result = send_draft_reminders(db)
        
        return ReminderResponse(
            success=True,
            message=f"Reminder emails processed: {result.get('sent', 0)} sent, {result.get('skipped', 0)} skipped, {result.get('errors', 0)} errors",
            data=result
        )
    except Exception as e:
        return ReminderResponse(
            success=False,
            message="Failed to send reminder emails",
            error=str(e),
            data={}
        )

