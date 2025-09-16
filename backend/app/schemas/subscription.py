from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime


class EmailSubscriptionCreate(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company: Optional[str] = None
    subscription_type: str = "newsletter"
    source: Optional[str] = None
    preferences: Optional[dict] = None

    @validator('subscription_type')
    def validate_subscription_type(cls, v):
        allowed_types = ['newsletter', 'blog', 'updates', 'marketing', 'all']
        if v not in allowed_types:
            raise ValueError(f'Subscription type must be one of: {", ".join(allowed_types)}')
        return v


class EmailSubscriptionResponse(BaseModel):
    id: int
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    company: Optional[str]
    subscription_type: str
    status: str
    source: Optional[str]
    subscribed_at: datetime
    preferences: Optional[dict]

    class Config:
        from_attributes = True


class UnsubscribeRequest(BaseModel):
    email: EmailStr
    token: Optional[str] = None


class SubscriptionStatusResponse(BaseModel):
    email: str
    is_subscribed: bool
    subscription_type: Optional[str]
    subscribed_at: Optional[datetime]
    status: str


class BulkUnsubscribeRequest(BaseModel):
    emails: list[EmailStr]
    reason: Optional[str] = None


class EmailPreferencesUpdate(BaseModel):
    preferences: dict
    subscription_type: Optional[str] = None
