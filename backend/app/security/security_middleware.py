"""
Security Middleware Integration
Comprehensive security middleware for FastAPI
"""

import time
import logging
import asyncio
from typing import Dict, Any, Optional, List
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.types import ASGIApp
import uvicorn
import ssl

from .ssl_manager import SSLManager
from .database_security import DatabaseSecurityManager
from .rate_limiter import RateLimiter, RateLimitConfig, RateLimitStrategy
from .input_validator import InputValidator, SecurityValidationError
from .sql_injection_prevention import SQLInjectionPrevention
from .xss_protection import XSSProtection
from .csrf_protection import CSRFProtection

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    """Comprehensive Security Middleware"""
    
    def __init__(self, app: ASGIApp, 
                 database_url: Optional[str] = None,
                 redis_client: Optional[Any] = None,
                 secret_key: Optional[str] = None):
        super().__init__(app)
        
        # Initialize security components
        self.ssl_manager = SSLManager()
        self.db_security = DatabaseSecurityManager(database_url) if database_url else None
        self.rate_limiter = RateLimiter(redis_client)
        self.input_validator = InputValidator()
        self.sql_injection_prevention = SQLInjectionPrevention()
        self.xss_protection = XSSProtection()
        self.csrf_protection = CSRFProtection(secret_key, redis_client)
        
        # Security configuration
        self.security_config = {
            "enable_ssl": True,
            "enable_rate_limiting": True,
            "enable_input_validation": True,
            "enable_sql_injection_prevention": True,
            "enable_xss_protection": True,
            "enable_csrf_protection": True,
            "enable_database_security": True,
            "enable_audit_logging": True,
            "max_request_size": 10 * 1024 * 1024,  # 10MB
            "request_timeout": 30,  # seconds
        }
        
        # Rate limiting configuration
        self.rate_limit_configs = {
            "/api/v1/auth/login": RateLimitConfig(
                requests_per_minute=5,
                requests_per_hour=20,
                strategy=RateLimitStrategy.SLIDING_WINDOW
            ),
            "/api/v1/auth/register": RateLimitConfig(
                requests_per_minute=3,
                requests_per_hour=10,
                strategy=RateLimitStrategy.SLIDING_WINDOW
            ),
            "/api/v1/valuation": RateLimitConfig(
                requests_per_minute=30,
                requests_per_hour=200,
                strategy=RateLimitStrategy.TOKEN_BUCKET
            ),
            "default": RateLimitConfig(
                requests_per_minute=60,
                requests_per_hour=1000,
                strategy=RateLimitStrategy.SLIDING_WINDOW
            )
        }
    
    async def initialize(self):
        """Initialize all security components"""
        try:
            # Initialize SSL manager
            if self.security_config["enable_ssl"]:
                await self.ssl_manager.initialize()
            
            # Initialize database security
            if self.security_config["enable_database_security"] and self.db_security:
                await self.db_security.initialize()
            
            # Initialize rate limiter
            if self.security_config["enable_rate_limiting"]:
                await self.rate_limiter.initialize()
            
            # Initialize CSRF protection
            if self.security_config["enable_csrf_protection"]:
                await self.csrf_protection.initialize()
            
            # Configure rate limiting
            for endpoint, config in self.rate_limit_configs.items():
                self.rate_limiter.set_rate_limit_config(endpoint, config)
            
            logger.info("Security middleware initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing security middleware: {e}")
            raise
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process request through security middleware"""
        start_time = time.time()
        
        try:
            # Get client information
            client_ip = self._get_client_ip(request)
            user_agent = request.headers.get("user-agent", "")
            user_id = self._get_user_id(request)
            
            # Security checks
            await self._check_request_size(request)
            await self._check_rate_limits(request, client_ip)
            await self._validate_input(request)
            await self._check_csrf_protection(request, user_id)
            
            # Process request
            response = await call_next(request)
            
            # Post-processing
            await self._log_security_event(request, response, client_ip, user_id, start_time)
            
            # Add security headers
            self._add_security_headers(response)
            
            return response
            
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"error": e.detail}
            )
        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": "Internal security error"}
            )
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _get_user_id(self, request: Request) -> Optional[int]:
        """Extract user ID from request"""
        # Implement based on your authentication system
        # This could be from JWT token, session, etc.
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # Extract user ID from JWT token
            # Implementation depends on your JWT setup
            pass
        
        return None
    
    async def _check_request_size(self, request: Request):
        """Check request size limits"""
        content_length = request.headers.get("content-length")
        if content_length:
            size = int(content_length)
            if size > self.security_config["max_request_size"]:
                raise HTTPException(
                    status_code=413,
                    detail="Request too large"
                )
    
    async def _check_rate_limits(self, request: Request, client_ip: str):
        """Check rate limits"""
        if not self.security_config["enable_rate_limiting"]:
            return
        
        endpoint = request.url.path
        identifier = f"{client_ip}:{endpoint}"
        
        # Get rate limit config for endpoint
        config = self.rate_limit_configs.get(endpoint, self.rate_limit_configs["default"])
        
        # Check rate limit
        is_limited, details = await self.rate_limiter.is_rate_limited(
            identifier, endpoint, client_ip
        )
        
        if is_limited:
            # Check if IP should be blocked
            if details.get("blocked"):
                await self.rate_limiter.block_ip(client_ip, 3600)  # Block for 1 hour
            
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "retry_after": details.get("retry_after", 60)
                }
            )
    
    async def _validate_input(self, request: Request):
        """Validate and sanitize input"""
        if not self.security_config["enable_input_validation"]:
            return
        
        # Validate request body
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
            if body:
                try:
                    # Validate JSON if present
                    content_type = request.headers.get("content-type", "")
                    if "application/json" in content_type:
                        json_data = json.loads(body.decode())
                        self.input_validator.validate_json(json.dumps(json_data))
                    
                    # Check for XSS
                    if self.security_config["enable_xss_protection"]:
                        body_str = body.decode()
                        is_xss, threats = self.xss_protection.detector.detect_xss(body_str)
                        if is_xss:
                            raise HTTPException(
                                status_code=400,
                                detail=f"XSS attack detected: {', '.join(threats)}"
                            )
                
                except json.JSONDecodeError:
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid JSON format"
                    )
                except SecurityValidationError as e:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Input validation error: {str(e)}"
                    )
        
        # Validate query parameters
        for param_name, param_value in request.query_params.items():
            if isinstance(param_value, str):
                try:
                    self.input_validator.sanitize_string(param_value)
                except SecurityValidationError as e:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid query parameter '{param_name}': {str(e)}"
                    )
    
    async def _check_csrf_protection(self, request: Request, user_id: Optional[int]):
        """Check CSRF protection"""
        if not self.security_config["enable_csrf_protection"]:
            return
        
        # Skip CSRF check for safe methods
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return
        
        # Get CSRF token
        token = request.headers.get("x-csrf-token")
        if not token:
            raise HTTPException(
                status_code=403,
                detail="CSRF token required"
            )
        
        # Validate token
        is_valid, message = self.csrf_protection.validate_token(token, user_id)
        if not is_valid:
            raise HTTPException(
                status_code=403,
                detail=f"CSRF token validation failed: {message}"
            )
    
    async def _log_security_event(self, request: Request, response: Response, 
                                client_ip: str, user_id: Optional[int], start_time: float):
        """Log security events"""
        if not self.security_config["enable_audit_logging"]:
            return
        
        try:
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000
            
            # Log to database security if available
            if self.db_security:
                await self.db_security.log_audit_event(
                    user_id=user_id,
                    action=f"{request.method} {request.url.path}",
                    ip_address=client_ip,
                    user_agent=request.headers.get("user-agent", ""),
                    success=response.status_code < 400,
                    error_message=None if response.status_code < 400 else f"HTTP {response.status_code}"
                )
            
            # Log rate limiting stats
            if self.security_config["enable_rate_limiting"]:
                endpoint = request.url.path
                identifier = f"{client_ip}:{endpoint}"
                stats = await self.rate_limiter.get_rate_limit_stats(identifier, endpoint)
                logger.info(f"Rate limit stats for {identifier}: {stats}")
            
        except Exception as e:
            logger.error(f"Error logging security event: {e}")
    
    def _add_security_headers(self, response: Response):
        """Add security headers to response"""
        # Content Security Policy
        csp_header = self.xss_protection.create_csp_header()
        response.headers["Content-Security-Policy"] = csp_header
        
        # X-Frame-Options
        response.headers["X-Frame-Options"] = "DENY"
        
        # X-Content-Type-Options
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # X-XSS-Protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer-Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions-Policy
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Strict-Transport-Security (if HTTPS)
        if self.security_config["enable_ssl"]:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    async def get_security_status(self) -> Dict[str, Any]:
        """Get comprehensive security status"""
        try:
            status = {
                "ssl_status": await self.ssl_manager.get_certificate_info() if self.security_config["enable_ssl"] else None,
                "rate_limiting_status": await self.rate_limiter.get_rate_limit_stats("system", "default") if self.security_config["enable_rate_limiting"] else None,
                "csrf_status": self.csrf_protection.get_csrf_stats() if self.security_config["enable_csrf_protection"] else None,
                "xss_protection_status": self.xss_protection.get_protection_stats() if self.security_config["enable_xss_protection"] else None,
                "database_security_status": await self.db_security.get_security_stats() if self.db_security else None,
                "security_config": self.security_config
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting security status: {e}")
            return {"error": str(e)}
    
    async def cleanup(self):
        """Cleanup security resources"""
        try:
            if self.db_security:
                await self.db_security.close()
            
            if self.rate_limiter.redis_client:
                await self.rate_limiter.redis_client.close()
            
            if self.csrf_protection.redis_client:
                await self.csrf_protection.redis_client.close()
            
            logger.info("Security middleware cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during security cleanup: {e}")

def create_secure_server(app, host: str = "0.0.0.0", port: int = 8003, 
                        ssl_cert: Optional[str] = None, ssl_key: Optional[str] = None):
    """Create a secure server with SSL/TLS"""
    try:
        ssl_context = None
        if ssl_cert and ssl_key:
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(ssl_cert, ssl_key)
            ssl_context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
        
        return uvicorn.Server(
            uvicorn.Config(
                app,
                host=host,
                port=port,
                ssl_context=ssl_context,
                log_level="info"
            )
        )
        
    except Exception as e:
        logger.error(f"Error creating secure server: {e}")
        raise
