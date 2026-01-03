"""
Secure Exception Handling
Prevents information disclosure through error messages
"""

from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


class SecureHTTPException(HTTPException):
    """Secure HTTP exception that doesn't leak internal information"""
    
    def __init__(self, status_code: int, detail: str = None, internal_error: str = None):
        # Log internal error for debugging
        if internal_error:
            logger.error(f"Internal error: {internal_error}")
        
        # Return generic error to client
        super().__init__(
            status_code=status_code,
            detail=detail or "An error occurred. Please try again later."
        )

