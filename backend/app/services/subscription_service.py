import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..models.subscription import EmailSubscription, UnsubscribeToken
from ..schemas.subscription import EmailSubscriptionCreate, UnsubscribeRequest
import logging

logger = logging.getLogger(__name__)


class SubscriptionService:
    def __init__(self, db: Session):
        self.db = db

    def subscribe_email(self, subscription_data: EmailSubscriptionCreate, 
                       ip_address: Optional[str] = None, 
                       user_agent: Optional[str] = None) -> dict:
        """
        Subscribe an email to the newsletter/blog updates
        """
        try:
            # Check if email already exists
            existing_subscription = self.db.query(EmailSubscription).filter(
                EmailSubscription.email == subscription_data.email
            ).first()

            if existing_subscription:
                if existing_subscription.status == "active":
                    return {
                        "success": False,
                        "message": "This email is already subscribed to our newsletter.",
                        "already_subscribed": True
                    }
                else:
                    # Reactivate subscription
                    existing_subscription.status = "active"
                    existing_subscription.subscription_type = subscription_data.subscription_type
                    existing_subscription.source = subscription_data.source
                    existing_subscription.first_name = subscription_data.first_name
                    existing_subscription.last_name = subscription_data.last_name
                    existing_subscription.company = subscription_data.company
                    existing_subscription.unsubscribed_at = None
                    existing_subscription.updated_at = datetime.now(timezone.utc)
                    
                    if subscription_data.preferences:
                        import json
                        existing_subscription.preferences = json.dumps(subscription_data.preferences)
                    
                    self.db.commit()
                    
                    return {
                        "success": True,
                        "message": "Welcome back! Your subscription has been reactivated.",
                        "subscription": existing_subscription
                    }

            # Create new subscription
            new_subscription = EmailSubscription(
                email=subscription_data.email,
                first_name=subscription_data.first_name,
                last_name=subscription_data.last_name,
                company=subscription_data.company,
                subscription_type=subscription_data.subscription_type,
                source=subscription_data.source,
                ip_address=ip_address,
                user_agent=user_agent,
                status="active"
            )
            
            if subscription_data.preferences:
                import json
                new_subscription.preferences = json.dumps(subscription_data.preferences)

            self.db.add(new_subscription)
            self.db.commit()
            self.db.refresh(new_subscription)

            return {
                "success": True,
                "message": "Thank you for subscribing! You'll receive our latest updates.",
                "subscription": new_subscription
            }

        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Database integrity error during subscription: {e}")
            return {
                "success": False,
                "message": "An error occurred while processing your subscription. Please try again.",
                "error": "database_error"
            }
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error during subscription: {e}")
            return {
                "success": False,
                "message": "An unexpected error occurred. Please try again later.",
                "error": "server_error"
            }

    def unsubscribe_email(self, email: str, token: Optional[str] = None) -> dict:
        """
        Unsubscribe an email from the newsletter
        """
        try:
            subscription = self.db.query(EmailSubscription).filter(
                EmailSubscription.email == email
            ).first()

            if not subscription:
                return {
                    "success": False,
                    "message": "Email address not found in our subscription list."
                }

            if subscription.status == "unsubscribed":
                return {
                    "success": True,
                    "message": "This email is already unsubscribed.",
                    "already_unsubscribed": True
                }

            # Update subscription status
            subscription.status = "unsubscribed"
            subscription.unsubscribed_at = datetime.now(timezone.utc)
            subscription.updated_at = datetime.now(timezone.utc)
            
            # If token provided, mark it as used
            if token:
                unsubscribe_token = self.db.query(UnsubscribeToken).filter(
                    UnsubscribeToken.token == token,
                    UnsubscribeToken.email == email,
                    UnsubscribeToken.is_used == False
                ).first()
                
                if unsubscribe_token:
                    unsubscribe_token.is_used = True
                    unsubscribe_token.used_at = datetime.now(timezone.utc)

            self.db.commit()

            return {
                "success": True,
                "message": "You have been successfully unsubscribed from our newsletter."
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error during unsubscription: {e}")
            return {
                "success": False,
                "message": "An error occurred while processing your unsubscription. Please try again."
            }

    def generate_unsubscribe_token(self, email: str) -> str:
        """
        Generate a secure unsubscribe token for an email
        """
        # Create a secure random token
        token = secrets.token_urlsafe(32)
        
        # Create token record
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)  # Token expires in 30 days
        
        unsubscribe_token = UnsubscribeToken(
            email=email,
            token=token,
            expires_at=expires_at
        )
        
        self.db.add(unsubscribe_token)
        self.db.commit()
        
        return token

    def get_subscription_status(self, email: str) -> dict:
        """
        Check if an email is subscribed and get subscription details
        """
        subscription = self.db.query(EmailSubscription).filter(
            EmailSubscription.email == email
        ).first()

        if not subscription:
            return {
                "is_subscribed": False,
                "message": "Email not found in subscription list"
            }

        return {
            "is_subscribed": subscription.status == "active",
            "subscription_type": subscription.subscription_type,
            "subscribed_at": subscription.subscribed_at,
            "status": subscription.status,
            "subscription": subscription
        }

    def get_all_subscriptions(self, status: Optional[str] = None, 
                            subscription_type: Optional[str] = None,
                            limit: int = 100, offset: int = 0) -> List[EmailSubscription]:
        """
        Get all subscriptions with optional filtering
        """
        query = self.db.query(EmailSubscription)
        
        if status:
            query = query.filter(EmailSubscription.status == status)
        
        if subscription_type:
            query = query.filter(EmailSubscription.subscription_type == subscription_type)
        
        return query.offset(offset).limit(limit).all()

    def update_subscription_preferences(self, email: str, preferences: dict) -> dict:
        """
        Update subscription preferences for an email
        """
        try:
            subscription = self.db.query(EmailSubscription).filter(
                EmailSubscription.email == email
            ).first()

            if not subscription:
                return {
                    "success": False,
                    "message": "Email not found in subscription list"
                }

            import json
            subscription.preferences = json.dumps(preferences)
            subscription.updated_at = datetime.now(timezone.utc)
            
            self.db.commit()

            return {
                "success": True,
                "message": "Subscription preferences updated successfully"
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating subscription preferences: {e}")
            return {
                "success": False,
                "message": "An error occurred while updating preferences"
            }

    def get_subscription_stats(self) -> dict:
        """
        Get subscription statistics
        """
        total_subscriptions = self.db.query(EmailSubscription).count()
        active_subscriptions = self.db.query(EmailSubscription).filter(
            EmailSubscription.status == "active"
        ).count()
        unsubscribed = self.db.query(EmailSubscription).filter(
            EmailSubscription.status == "unsubscribed"
        ).count()
        
        # Get subscriptions by type
        newsletter_count = self.db.query(EmailSubscription).filter(
            EmailSubscription.subscription_type == "newsletter",
            EmailSubscription.status == "active"
        ).count()
        
        blog_count = self.db.query(EmailSubscription).filter(
            EmailSubscription.subscription_type == "blog",
            EmailSubscription.status == "active"
        ).count()

        return {
            "total_subscriptions": total_subscriptions,
            "active_subscriptions": active_subscriptions,
            "unsubscribed": unsubscribed,
            "newsletter_subscriptions": newsletter_count,
            "blog_subscriptions": blog_count
        }
