"""
Payment Amount Validation
Server-side payment amount validation to prevent manipulation
"""

import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from fastapi import HTTPException, status

from ..services.fmv_report_service import FMVReportService

logger = logging.getLogger(__name__)


class PaymentAmountValidator:
    """Validates payment amounts server-side to prevent client manipulation"""
    
    def __init__(self):
        self.pricing_service = FMVReportService()
        self.manipulation_attempts = {}  # Track manipulation attempts
    
    def calculate_server_price(
        self, 
        report_type: str, 
        crane_data: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Calculate price server-side (in cents)
        Returns: Price in cents
        """
        try:
            if report_type == "fleet_valuation":
                unit_count = crane_data.get("unit_count", 1) if crane_data else 1
                # Validate unit count
                if not isinstance(unit_count, int) or unit_count < 1 or unit_count > 50:
                    raise ValueError(f"Invalid unit_count: {unit_count}")
                
                price, tier = self.pricing_service.calculate_fleet_price_by_units(unit_count)
                amount_cents = int(price * 100)
            else:
                # Get base price for other report types
                price = self.pricing_service.get_base_price_dollars(report_type)
                amount_cents = int(price * 100)
            
            return amount_cents
            
        except Exception as e:
            logger.error(f"Error calculating server price: {e}")
            raise HTTPException(
                status_code=500,
                detail="Error calculating price. Please try again."
            )
    
    def validate_payment_amount(
        self,
        report_type: str,
        client_amount: int,
        crane_data: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None
    ) -> Tuple[bool, int, str]:
        """
        Validate payment amount against server calculation
        Returns: (is_valid, server_calculated_amount, error_message)
        """
        try:
            # Calculate server-side price
            server_amount = self.calculate_server_price(report_type, crane_data)
            
            # Verify amounts match
            if client_amount != server_amount:
                # Log manipulation attempt
                self._log_manipulation_attempt(
                    user_id=user_id,
                    report_type=report_type,
                    client_amount=client_amount,
                    server_amount=server_amount
                )
                
                return False, server_amount, (
                    f"Payment amount mismatch. "
                    f"Expected: ${server_amount/100:.2f}, "
                    f"Received: ${client_amount/100:.2f}. "
                    f"Prices are calculated server-side and cannot be modified."
                )
            
            return True, server_amount, ""
            
        except Exception as e:
            logger.error(f"Error validating payment amount: {e}")
            return False, 0, f"Error validating payment: {str(e)}"
    
    def _log_manipulation_attempt(
        self,
        user_id: Optional[int],
        report_type: str,
        client_amount: int,
        server_amount: int
    ):
        """Log payment manipulation attempt"""
        attempt_key = f"{user_id}_{report_type}_{datetime.utcnow().isoformat()}"
        
        self.manipulation_attempts[attempt_key] = {
            "user_id": user_id,
            "report_type": report_type,
            "client_amount": client_amount,
            "server_amount": server_amount,
            "difference": abs(client_amount - server_amount),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.warning(
            f"PAYMENT MANIPULATION ATTEMPT DETECTED: "
            f"User ID: {user_id}, "
            f"Report Type: {report_type}, "
            f"Client Amount: ${client_amount/100:.2f}, "
            f"Server Amount: ${server_amount/100:.2f}, "
            f"Difference: ${abs(client_amount - server_amount)/100:.2f}"
        )
        
        # Log to security audit logger
        try:
            from .audit_logger import SecurityAuditLogger
            import asyncio
            
            # Get IP address from request context if available
            ip_address = getattr(self, '_current_ip', 'unknown')
            
            # Run async function
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(SecurityAuditLogger.log_payment_manipulation(
                        user_id=user_id,
                        ip_address=ip_address,
                        client_amount=client_amount,
                        server_amount=server_amount,
                        report_type=report_type,
                        db=None
                    ))
                else:
                    loop.run_until_complete(SecurityAuditLogger.log_payment_manipulation(
                        user_id=user_id,
                        ip_address=ip_address,
                        client_amount=client_amount,
                        server_amount=server_amount,
                        report_type=report_type,
                        db=None
                    ))
            except RuntimeError:
                # No event loop, create new one
                asyncio.run(SecurityAuditLogger.log_payment_manipulation(
                    user_id=user_id,
                    ip_address=ip_address,
                    client_amount=client_amount,
                    server_amount=server_amount,
                    report_type=report_type,
                    db=None
                ))
        except Exception as log_error:
            logger.error(f"Failed to log payment manipulation to audit logger: {log_error}")
    
    def get_manipulation_stats(self) -> Dict[str, Any]:
        """Get statistics on manipulation attempts"""
        return {
            "total_attempts": len(self.manipulation_attempts),
            "recent_attempts": list(self.manipulation_attempts.values())[-10:]
        }


# Global instance
payment_validator = PaymentAmountValidator()

