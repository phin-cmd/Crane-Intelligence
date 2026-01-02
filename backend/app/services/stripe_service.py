"""
Stripe Payment Service
Handles payment processing via Stripe API
"""

import stripe
import logging
import os
from typing import Dict, Any, Optional
from ..core.config import settings

logger = logging.getLogger(__name__)


class StripeService:
    """
    Stripe payment service
    Handles payment intents, subscriptions, and webhooks
    """
    
    def __init__(self):
        self.secret_key = settings.stripe_secret_key
        self.publishable_key = settings.stripe_publishable_key
        self.webhook_secret = settings.stripe_webhook_secret
        self.environment = os.getenv("ENVIRONMENT", "prod").lower()
        
        if not self.secret_key:
            logger.warning("Stripe secret key not configured. Payment processing will fail.")
        else:
            stripe.api_key = self.secret_key
            # Validate key types match environment
            self._validate_stripe_keys()
            logger.info("Stripe service initialized")
    
    def _validate_stripe_keys(self):
        """
        Validate that Stripe keys match the environment configuration.
        Production must use live keys, dev/uat must use test keys.
        """
        if not self.secret_key or not self.publishable_key:
            return  # Skip validation if keys are not configured
        
        # Detect key types
        is_test_secret = self.secret_key.startswith("sk_test_")
        is_live_secret = self.secret_key.startswith("sk_live_")
        is_test_publishable = self.publishable_key.startswith("pk_test_")
        is_live_publishable = self.publishable_key.startswith("pk_live_")
        
        # Determine detected mode
        if is_test_secret and is_test_publishable:
            detected_mode = "test"
        elif is_live_secret and is_live_publishable:
            detected_mode = "live"
        else:
            detected_mode = "mixed"  # Mismatched key types
        
        # Log key type detection (without exposing actual keys)
        logger.info(f"Stripe keys detected: {detected_mode} mode (secret: {'test' if is_test_secret else 'live' if is_live_secret else 'unknown'}, publishable: {'test' if is_test_publishable else 'live' if is_live_publishable else 'unknown'})")
        
        # Validate environment-key matching
        if self.environment == "prod":
            if detected_mode == "test":
                logger.error(
                    "CRITICAL: Production environment is using TEST Stripe keys! "
                    "This will prevent real payment processing. "
                    "Production MUST use live keys (pk_live_... and sk_live_...)."
                )
            elif detected_mode == "mixed":
                logger.error(
                    "CRITICAL: Production environment has mismatched Stripe key types! "
                    "Both keys must be live keys (pk_live_... and sk_live_...)."
                )
            elif detected_mode == "live":
                logger.info("✓ Production environment using live Stripe keys (correct)")
        elif self.environment in ["dev", "uat"]:
            if detected_mode == "live":
                logger.warning(
                    f"WARNING: {self.environment.upper()} environment is using LIVE Stripe keys! "
                    "This could result in real charges during testing. "
                    f"{self.environment.upper()} environment should use test keys (pk_test_... and sk_test_...)."
                )
            elif detected_mode == "mixed":
                logger.warning(
                    f"WARNING: {self.environment.upper()} environment has mismatched Stripe key types! "
                    "Both keys should be test keys (pk_test_... and sk_test_...)."
                )
            elif detected_mode == "test":
                logger.info(f"✓ {self.environment.upper()} environment using test Stripe keys (correct)")
        
        # Validate webhook secret
        if not self.webhook_secret:
            logger.warning(
                f"Stripe webhook secret not configured for {self.environment.upper()} environment. "
                "Webhook signature verification will fail. "
                "Configure STRIPE_WEBHOOK_SECRET in environment variables."
            )
        elif not self.webhook_secret.startswith("whsec_"):
            logger.warning(
                f"Stripe webhook secret format may be incorrect. "
                "Expected format: whsec_... (from Stripe dashboard -> Webhooks -> Signing secret)"
            )
    
    def create_payment_intent(
        self,
        amount: int,  # Amount in cents
        currency: str = "usd",
        metadata: Optional[Dict[str, str]] = None,
        customer_id: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a payment intent
        
        Args:
            amount: Amount in cents
            currency: Currency code (default: usd)
            metadata: Additional metadata
            customer_id: Stripe customer ID (optional)
            description: Payment description
        
        Returns:
            Dict with payment intent data
        """
        if not self.secret_key:
            return {
                "success": False,
                "error": "Stripe secret key not configured"
            }
        
        try:
            intent_params = {
                "amount": amount,
                "currency": currency,
            }
            
            if customer_id:
                intent_params["customer"] = customer_id
            
            if description:
                intent_params["description"] = description
            
            if metadata:
                intent_params["metadata"] = metadata
            
            payment_intent = stripe.PaymentIntent.create(**intent_params)
            
            logger.info(f"Payment intent created: {payment_intent.id}")
            return {
                "success": True,
                "client_secret": payment_intent.client_secret,
                "payment_intent_id": payment_intent.id,
                "amount": payment_intent.amount,
                "currency": payment_intent.currency,
                "status": payment_intent.status
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating payment intent: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
        except Exception as e:
            logger.error(f"Unexpected error creating payment intent: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def confirm_payment_intent(self, payment_intent_id: str) -> Dict[str, Any]:
        """
        Confirm a payment intent
        
        Args:
            payment_intent_id: Stripe payment intent ID
        
        Returns:
            Dict with payment intent status
        """
        if not self.secret_key:
            return {
                "success": False,
                "error": "Stripe secret key not configured"
            }
        
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            return {
                "success": True,
                "payment_intent_id": payment_intent.id,
                "status": payment_intent.status,
                "amount": payment_intent.amount,
                "currency": payment_intent.currency
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving payment intent: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a Stripe customer
        
        Args:
            email: Customer email
            name: Customer name (optional)
            metadata: Additional metadata
        
        Returns:
            Dict with customer data
        """
        if not self.secret_key:
            return {
                "success": False,
                "error": "Stripe secret key not configured"
            }
        
        try:
            customer_params = {
                "email": email
            }
            
            if name:
                customer_params["name"] = name
            
            if metadata:
                customer_params["metadata"] = metadata
            
            customer = stripe.Customer.create(**customer_params)
            
            logger.info(f"Stripe customer created: {customer.id}")
            return {
                "success": True,
                "customer_id": customer.id,
                "email": customer.email
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating customer: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """
        Verify Stripe webhook signature
        
        Args:
            payload: Raw webhook payload
            signature: Stripe signature header
        
        Returns:
            Dict with verification result and event data
        """
        if not self.webhook_secret:
            return {
                "success": False,
                "error": "Stripe webhook secret not configured"
            }
        
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            
            return {
                "success": True,
                "event": event
            }
            
        except ValueError as e:
            logger.error(f"Invalid webhook payload: {e}")
            return {
                "success": False,
                "error": "Invalid payload"
            }
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid webhook signature: {e}")
            return {
                "success": False,
                "error": "Invalid signature"
            }

