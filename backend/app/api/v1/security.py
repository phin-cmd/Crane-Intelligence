"""
Security API Endpoints
Comprehensive security management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional, List
import logging
import asyncio
from datetime import datetime, timedelta

from ...security.security_middleware import SecurityMiddleware
from ...security.security_config import get_security_config, SecurityConfig
from ...security.ssl_manager import SSLManager
from ...security.database_security import DatabaseSecurityManager
from ...security.rate_limiter import RateLimiter
from ...security.input_validator import InputValidator
from ...security.sql_injection_prevention import SQLInjectionPrevention
from ...security.xss_protection import XSSProtection
from ...security.csrf_protection import CSRFProtection

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Security Management"])

# Security dependencies
security = HTTPBearer()

async def get_security_middleware() -> SecurityMiddleware:
    """Get security middleware instance"""
    # This would be injected by the main app
    # For now, return a mock instance
    return SecurityMiddleware(None)

async def get_security_config() -> SecurityConfig:
    """Get security configuration"""
    return get_security_config()

@router.get("/security/status", response_model=Dict[str, Any])
async def get_security_status(
    security_middleware: SecurityMiddleware = Depends(get_security_middleware)
):
    """
    Get comprehensive security status
    """
    try:
        status = await security_middleware.get_security_status()
        return {
            "status": "success",
            "security_status": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting security status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting security status: {str(e)}"
        )

@router.get("/security/ssl/status", response_model=Dict[str, Any])
async def get_ssl_status():
    """
    Get SSL/TLS certificate status
    """
    try:
        ssl_manager = SSLManager()
        await ssl_manager.initialize()
        
        cert_info = await ssl_manager.get_certificate_info()
        return {
            "status": "success",
            "ssl_status": cert_info,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting SSL status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting SSL status: {str(e)}"
        )

@router.post("/security/ssl/generate", response_model=Dict[str, Any])
async def generate_ssl_certificate(
    host: str = "localhost",
    cert_dir: str = "certs"
):
    """
    Generate new SSL certificate
    """
    try:
        ssl_manager = SSLManager()
        cert_path, key_path = await ssl_manager.generate_self_signed_cert(host, cert_dir)
        
        return {
            "status": "success",
            "message": "SSL certificate generated successfully",
            "cert_path": cert_path,
            "key_path": key_path,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating SSL certificate: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating SSL certificate: {str(e)}"
        )

@router.get("/security/database/status", response_model=Dict[str, Any])
async def get_database_security_status():
    """
    Get database security status
    """
    try:
        db_security = DatabaseSecurityManager()
        await db_security.initialize()
        
        security_stats = await db_security.get_security_stats()
        return {
            "status": "success",
            "database_security": security_stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting database security status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting database security status: {str(e)}"
        )

@router.get("/security/rate-limiting/status", response_model=Dict[str, Any])
async def get_rate_limiting_status():
    """
    Get rate limiting status
    """
    try:
        rate_limiter = RateLimiter()
        await rate_limiter.initialize()
        
        stats = await rate_limiter.get_rate_limit_stats("system", "default")
        return {
            "status": "success",
            "rate_limiting": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting rate limiting status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting rate limiting status: {str(e)}"
        )

@router.post("/security/rate-limiting/block-ip", response_model=Dict[str, Any])
async def block_ip_address(
    ip_address: str,
    duration: int = 3600
):
    """
    Block IP address for specified duration
    """
    try:
        rate_limiter = RateLimiter()
        await rate_limiter.initialize()
        
        await rate_limiter.block_ip(ip_address, duration)
        
        return {
            "status": "success",
            "message": f"IP address {ip_address} blocked for {duration} seconds",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error blocking IP address: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error blocking IP address: {str(e)}"
        )

@router.post("/security/rate-limiting/unblock-ip", response_model=Dict[str, Any])
async def unblock_ip_address(ip_address: str):
    """
    Unblock IP address
    """
    try:
        rate_limiter = RateLimiter()
        await rate_limiter.initialize()
        
        await rate_limiter.unblock_ip(ip_address)
        
        return {
            "status": "success",
            "message": f"IP address {ip_address} unblocked",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error unblocking IP address: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error unblocking IP address: {str(e)}"
        )

@router.get("/security/xss/status", response_model=Dict[str, Any])
async def get_xss_protection_status():
    """
    Get XSS protection status
    """
    try:
        xss_protection = XSSProtection()
        stats = xss_protection.get_protection_stats()
        
        return {
            "status": "success",
            "xss_protection": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting XSS protection status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting XSS protection status: {str(e)}"
        )

@router.post("/security/xss/scan", response_model=Dict[str, Any])
async def scan_for_xss(
    content: str,
    user_id: Optional[int] = None
):
    """
    Scan content for XSS attacks
    """
    try:
        xss_protection = XSSProtection()
        is_xss, threats = xss_protection.detector.detect_xss(content)
        
        if is_xss:
            # Log the attack attempt
            logger.warning(f"XSS attack detected: {threats}")
            
            # Log to database if user_id provided
            if user_id:
                # This would be logged to the database
                pass
        
        return {
            "status": "success",
            "is_xss": is_xss,
            "threats": threats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error scanning for XSS: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scanning for XSS: {str(e)}"
        )

@router.get("/security/csrf/status", response_model=Dict[str, Any])
async def get_csrf_protection_status():
    """
    Get CSRF protection status
    """
    try:
        csrf_protection = CSRFProtection()
        stats = csrf_protection.get_csrf_stats()
        
        return {
            "status": "success",
            "csrf_protection": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting CSRF protection status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting CSRF protection status: {str(e)}"
        )

@router.post("/security/csrf/generate-token", response_model=Dict[str, Any])
async def generate_csrf_token(
    user_id: Optional[int] = None,
    expiry: Optional[int] = None
):
    """
    Generate CSRF token
    """
    try:
        csrf_protection = CSRFProtection()
        token = csrf_protection.generate_token(user_id, expiry)
        
        return {
            "status": "success",
            "csrf_token": token,
            "expiry": expiry or 3600,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating CSRF token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating CSRF token: {str(e)}"
        )

@router.post("/security/csrf/validate-token", response_model=Dict[str, Any])
async def validate_csrf_token(
    token: str,
    user_id: Optional[int] = None
):
    """
    Validate CSRF token
    """
    try:
        csrf_protection = CSRFProtection()
        is_valid, message = csrf_protection.validate_token(token, user_id)
        
        return {
            "status": "success",
            "is_valid": is_valid,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error validating CSRF token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating CSRF token: {str(e)}"
        )

@router.get("/security/input-validation/status", response_model=Dict[str, Any])
async def get_input_validation_status():
    """
    Get input validation status
    """
    try:
        input_validator = InputValidator()
        stats = input_validator.get_validation_stats()
        
        return {
            "status": "success",
            "input_validation": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting input validation status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting input validation status: {str(e)}"
        )

@router.post("/security/input-validation/validate", response_model=Dict[str, Any])
async def validate_input(
    input_data: str,
    validation_type: str = "general"
):
    """
    Validate input data
    """
    try:
        input_validator = InputValidator()
        
        if validation_type == "email":
            is_valid = input_validator.validate_email(input_data)
        elif validation_type == "password":
            is_valid = input_validator.validate_password_strength(input_data)
        elif validation_type == "alphanumeric":
            is_valid = input_validator.validate_alphanumeric(input_data)
        elif validation_type == "uuid":
            is_valid = input_validator.validate_uuid(input_data)
        else:
            # General validation
            sanitized = input_validator.sanitize_string(input_data)
            is_valid = sanitized is not None
        
        return {
            "status": "success",
            "is_valid": is_valid,
            "validation_type": validation_type,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error validating input: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating input: {str(e)}"
        )

@router.get("/security/sql-injection/status", response_model=Dict[str, Any])
async def get_sql_injection_prevention_status():
    """
    Get SQL injection prevention status
    """
    try:
        sql_prevention = SQLInjectionPrevention()
        stats = sql_prevention.get_prevention_stats()
        
        return {
            "status": "success",
            "sql_injection_prevention": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting SQL injection prevention status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting SQL injection prevention status: {str(e)}"
        )

@router.post("/security/sql-injection/scan-query", response_model=Dict[str, Any])
async def scan_sql_query(
    query: str,
    user_id: Optional[int] = None
):
    """
    Scan SQL query for injection attempts
    """
    try:
        sql_prevention = SQLInjectionPrevention()
        is_safe, threats = sql_prevention.scan_query(query)
        
        if not is_safe:
            # Log the attack attempt
            logger.warning(f"SQL injection attempt detected: {threats}")
            
            # Log to database if user_id provided
            if user_id:
                # This would be logged to the database
                pass
        
        return {
            "status": "success",
            "is_safe": is_safe,
            "threats": threats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error scanning SQL query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scanning SQL query: {str(e)}"
        )

@router.get("/security/audit-logs", response_model=Dict[str, Any])
async def get_audit_logs(
    user_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100
):
    """
    Get security audit logs
    """
    try:
        # This would query the database for audit logs
        # For now, return mock data
        audit_logs = [
            {
                "id": 1,
                "user_id": user_id,
                "action": "LOGIN",
                "ip_address": "192.168.1.1",
                "user_agent": "Mozilla/5.0...",
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        return {
            "status": "success",
            "audit_logs": audit_logs,
            "total": len(audit_logs),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting audit logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting audit logs: {str(e)}"
        )

@router.get("/security/configuration", response_model=Dict[str, Any])
async def get_security_configuration(
    config: SecurityConfig = Depends(get_security_config)
):
    """
    Get security configuration
    """
    try:
        return {
            "status": "success",
            "configuration": {
                "environment": config.environment,
                "ssl_enabled": config.ssl_enabled,
                "rate_limiting_enabled": config.rate_limiting_enabled,
                "xss_protection_enabled": config.xss_protection_enabled,
                "csrf_protection_enabled": config.csrf_protection_enabled,
                "input_validation_enabled": config.input_validation_enabled,
                "sql_injection_prevention_enabled": config.sql_injection_prevention_enabled,
                "database_security_enabled": config.db_audit_logging,
                "security_headers_enabled": config.security_headers_enabled,
                "cors_origins": config.cors_origins,
                "max_request_size": config.max_request_size,
                "session_max_age": config.session_max_age
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting security configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting security configuration: {str(e)}"
        )
