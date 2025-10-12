from fastapi import Request, HTTPException
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware
import time
import redis

# Rate limiting
def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    # Implement rate limiting logic here
    response = call_next(request)
    return response

# Security headers
def add_security_headers(request: Request, call_next):
    response = call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
