"""
Security Audit Logger
Logs all security events for monitoring and incident response
"""

from datetime import datetime
from typing import Dict, Any, Optional
import json
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)


class SecurityAuditLogger:
    """Log all security events"""
    
    @staticmethod
    async def log_security_event(
        event_type: str,
        user_id: Optional[int],
        ip_address: str,
        details: Dict[str, Any],
        severity: str = "medium",
        db: Optional[Session] = None
    ):
        """
        Log security event
        
        Args:
            event_type: Type of security event (e.g., "payment_manipulation", "sql_injection_attempt")
            user_id: User ID if available
            ip_address: IP address of the request
            details: Additional event details
            severity: Event severity (low, medium, high, critical)
            db: Database session (optional)
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": ip_address,
            "details": details,
            "severity": severity
        }
        
        # Log to database if available
        if db:
            try:
                # Try to insert into security_events table if it exists
                db.execute(
                    text("""
                        INSERT INTO security_events (event_data, created_at)
                        VALUES (:data, NOW())
                        ON CONFLICT DO NOTHING
                    """),
                    {"data": json.dumps(event)}
                )
                db.commit()
            except Exception as e:
                # Table might not exist, just log to application logs
                logger.debug(f"Could not log to security_events table: {e}")
        
        # Always log to application logs
        log_message = f"SECURITY EVENT [{severity.upper()}]: {event_type}"
        if user_id:
            log_message += f" | User: {user_id}"
        log_message += f" | IP: {ip_address} | Details: {json.dumps(details)}"
        
        if severity == "critical":
            logger.critical(log_message)
        elif severity == "high":
            logger.error(log_message)
        elif severity == "medium":
            logger.warning(log_message)
        else:
            logger.info(log_message)
        
        # Alert on high severity events
        if severity in ["high", "critical"]:
            # TODO: Integrate with alerting system (email, Slack, PagerDuty, etc.)
            logger.critical(f"CRITICAL SECURITY EVENT REQUIRES IMMEDIATE ATTENTION: {event_type}")
    
    @staticmethod
    async def log_payment_manipulation(
        user_id: Optional[int],
        ip_address: str,
        client_amount: int,
        server_amount: int,
        report_type: str,
        db: Optional[Session] = None
    ):
        """Log payment manipulation attempt"""
        await SecurityAuditLogger.log_security_event(
            event_type="payment_manipulation_attempt",
            user_id=user_id,
            ip_address=ip_address,
            details={
                "client_amount": client_amount,
                "server_amount": server_amount,
                "difference": abs(client_amount - server_amount),
                "report_type": report_type
            },
            severity="high",
            db=db
        )
    
    @staticmethod
    async def log_sql_injection_attempt(
        user_id: Optional[int],
        ip_address: str,
        query: str,
        threats: list,
        db: Optional[Session] = None
    ):
        """Log SQL injection attempt"""
        await SecurityAuditLogger.log_security_event(
            event_type="sql_injection_attempt",
            user_id=user_id,
            ip_address=ip_address,
            details={
                "query_preview": query[:200] if len(query) > 200 else query,
                "threats": threats
            },
            severity="critical",
            db=db
        )
    
    @staticmethod
    async def log_bot_detection(
        ip_address: str,
        user_agent: str,
        reason: str,
        request_path: str,
        db: Optional[Session] = None
    ):
        """Log bot detection"""
        await SecurityAuditLogger.log_security_event(
            event_type="bot_detected",
            user_id=None,
            ip_address=ip_address,
            details={
                "user_agent": user_agent,
                "reason": reason,
                "request_path": request_path
            },
            severity="low",
            db=db
        )

