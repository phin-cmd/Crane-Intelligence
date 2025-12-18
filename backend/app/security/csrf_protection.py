"""
CSRF (Cross-Site Request Forgery) Protection
Comprehensive CSRF protection system
"""

import secrets
import hashlib
import hmac
import time
import logging
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timedelta
import redis
import json
from cryptography.fernet import Fernet
import base64

logger = logging.getLogger(__name__)

class CSRFProtection:
    """CSRF Protection System"""
    
    def __init__(self, secret_key: Optional[str] = None, redis_client: Optional[redis.Redis] = None):
        self.secret_key = secret_key or self._generate_secret_key()
        self.redis_client = redis_client
        self.token_expiry = 3600  # 1 hour
        self.max_tokens_per_user = 10
        self.token_length = 32
        
        # Initialize encryption
        self.fernet = Fernet(self._get_encryption_key())
    
    def _generate_secret_key(self) -> str:
        """Generate a secure secret key"""
        return secrets.token_urlsafe(32)
    
    def _get_encryption_key(self) -> bytes:
        """Get encryption key from secret"""
        key = hashlib.sha256(self.secret_key.encode()).digest()
        return base64.urlsafe_b64encode(key)
    
    async def initialize(self):
        """Initialize CSRF protection"""
        try:
            if not self.redis_client:
                self.redis_client = redis.Redis(
                    host='localhost',
                    port=6379,
                    db=5,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
            
            await self.redis_client.ping()
            logger.info("CSRF protection initialized with Redis backend")
            
        except Exception as e:
            logger.warning(f"Redis not available for CSRF protection: {e}")
            self.redis_client = None
    
    def generate_token(self, user_id: Optional[int] = None, session_id: Optional[str] = None) -> str:
        """Generate CSRF token"""
        try:
            # Create token data
            token_data = {
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": time.time(),
                "nonce": secrets.token_urlsafe(16)
            }
            
            # Create token
            token = secrets.token_urlsafe(self.token_length)
            
            # Create signature
            signature = self._create_signature(token, token_data)
            
            # Encrypt token data
            encrypted_data = self.fernet.encrypt(json.dumps(token_data).encode())
            
            # Store token
            if self.redis_client:
                token_key = f"csrf_token:{token}"
                self.redis_client.setex(
                    token_key,
                    self.token_expiry,
                    json.dumps({
                        "signature": signature,
                        "data": base64.b64encode(encrypted_data).decode()
                    })
                )
            
            return token
            
        except Exception as e:
            logger.error(f"Error generating CSRF token: {e}")
            raise
    
    def _create_signature(self, token: str, token_data: Dict[str, Any]) -> str:
        """Create HMAC signature for token"""
        message = f"{token}:{json.dumps(token_data, sort_keys=True)}"
        signature = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _verify_signature(self, token: str, token_data: Dict[str, Any], signature: str) -> bool:
        """Verify HMAC signature for token"""
        expected_signature = self._create_signature(token, token_data)
        return hmac.compare_digest(signature, expected_signature)
    
    def validate_token(self, token: str, user_id: Optional[int] = None, 
                     session_id: Optional[str] = None) -> Tuple[bool, str]:
        """Validate CSRF token"""
        if not token:
            return False, "No token provided"
        
        try:
            if self.redis_client:
                # Get token from Redis
                token_key = f"csrf_token:{token}"
                token_data_str = self.redis_client.get(token_key)
                
                if not token_data_str:
                    return False, "Token not found or expired"
                
                token_info = json.loads(token_data_str)
                signature = token_info["signature"]
                encrypted_data = base64.b64decode(token_info["data"])
                
                # Decrypt token data
                decrypted_data = self.fernet.decrypt(encrypted_data)
                token_data = json.loads(decrypted_data.decode())
                
                # Verify signature
                if not self._verify_signature(token, token_data, signature):
                    return False, "Invalid token signature"
                
                # Check expiry
                if time.time() - token_data["timestamp"] > self.token_expiry:
                    return False, "Token expired"
                
                # Check user/session match
                if user_id and token_data.get("user_id") != user_id:
                    return False, "Token user mismatch"
                
                if session_id and token_data.get("session_id") != session_id:
                    return False, "Token session mismatch"
                
                return True, "Token is valid"
            
            else:
                # Fallback validation without Redis
                return False, "Token validation not available"
                
        except Exception as e:
            logger.error(f"Error validating CSRF token: {e}")
            return False, f"Token validation error: {str(e)}"
    
    def revoke_token(self, token: str) -> bool:
        """Revoke CSRF token"""
        try:
            if self.redis_client:
                token_key = f"csrf_token:{token}"
                return self.redis_client.delete(token_key) > 0
            return False
            
        except Exception as e:
            logger.error(f"Error revoking CSRF token: {e}")
            return False
    
    def revoke_user_tokens(self, user_id: int) -> int:
        """Revoke all tokens for a user"""
        try:
            if not self.redis_client:
                return 0
            
            # Get all tokens for user
            pattern = f"csrf_token:*"
            keys = self.redis_client.keys(pattern)
            
            revoked_count = 0
            for key in keys:
                try:
                    token_data_str = self.redis_client.get(key)
                    if token_data_str:
                        token_info = json.loads(token_data_str)
                        encrypted_data = base64.b64decode(token_info["data"])
                        decrypted_data = self.fernet.decrypt(encrypted_data)
                        token_data = json.loads(decrypted_data.decode())
                        
                        if token_data.get("user_id") == user_id:
                            self.redis_client.delete(key)
                            revoked_count += 1
                            
                except Exception:
                    # Skip invalid tokens
                    continue
            
            logger.info(f"Revoked {revoked_count} tokens for user {user_id}")
            return revoked_count
            
        except Exception as e:
            logger.error(f"Error revoking user tokens: {e}")
            return 0
    
    def cleanup_expired_tokens(self) -> int:
        """Clean up expired tokens"""
        try:
            if not self.redis_client:
                return 0
            
            current_time = time.time()
            pattern = f"csrf_token:*"
            keys = self.redis_client.keys(pattern)
            
            cleaned_count = 0
            for key in keys:
                try:
                    token_data_str = self.redis_client.get(key)
                    if token_data_str:
                        token_info = json.loads(token_data_str)
                        encrypted_data = base64.b64decode(token_info["data"])
                        decrypted_data = self.fernet.decrypt(encrypted_data)
                        token_data = json.loads(decrypted_data.decode())
                        
                        if current_time - token_data["timestamp"] > self.token_expiry:
                            self.redis_client.delete(key)
                            cleaned_count += 1
                            
                except Exception:
                    # Skip invalid tokens
                    continue
            
            logger.info(f"Cleaned up {cleaned_count} expired tokens")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired tokens: {e}")
            return 0
    
    def get_token_info(self, token: str) -> Optional[Dict[str, Any]]:
        """Get information about a token"""
        try:
            if not self.redis_client:
                return None
            
            token_key = f"csrf_token:{token}"
            token_data_str = self.redis_client.get(token_key)
            
            if not token_data_str:
                return None
            
            token_info = json.loads(token_data_str)
            encrypted_data = base64.b64decode(token_info["data"])
            decrypted_data = self.fernet.decrypt(encrypted_data)
            token_data = json.loads(decrypted_data.decode())
            
            return {
                "token": token,
                "user_id": token_data.get("user_id"),
                "session_id": token_data.get("session_id"),
                "created_at": datetime.fromtimestamp(token_data["timestamp"]).isoformat(),
                "expires_at": datetime.fromtimestamp(token_data["timestamp"] + self.token_expiry).isoformat(),
                "is_expired": time.time() - token_data["timestamp"] > self.token_expiry
            }
            
        except Exception as e:
            logger.error(f"Error getting token info: {e}")
            return None
    
    def get_user_tokens(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all tokens for a user"""
        try:
            if not self.redis_client:
                return []
            
            pattern = f"csrf_token:*"
            keys = self.redis_client.keys(pattern)
            
            user_tokens = []
            for key in keys:
                try:
                    token_data_str = self.redis_client.get(key)
                    if token_data_str:
                        token_info = json.loads(token_data_str)
                        encrypted_data = base64.b64decode(token_info["data"])
                        decrypted_data = self.fernet.decrypt(encrypted_data)
                        token_data = json.loads(decrypted_data.decode())
                        
                        if token_data.get("user_id") == user_id:
                            token = key.replace("csrf_token:", "")
                            user_tokens.append({
                                "token": token,
                                "session_id": token_data.get("session_id"),
                                "created_at": datetime.fromtimestamp(token_data["timestamp"]).isoformat(),
                                "expires_at": datetime.fromtimestamp(token_data["timestamp"] + self.token_expiry).isoformat(),
                                "is_expired": time.time() - token_data["timestamp"] > self.token_expiry
                            })
                            
                except Exception:
                    # Skip invalid tokens
                    continue
            
            return user_tokens
            
        except Exception as e:
            logger.error(f"Error getting user tokens: {e}")
            return []
    
    def create_csrf_middleware(self):
        """Create CSRF middleware for FastAPI"""
        from fastapi import Request, HTTPException
        from fastapi.responses import JSONResponse
        
        async def csrf_middleware(request: Request, call_next):
            # Skip CSRF check for GET requests and safe methods
            if request.method in ["GET", "HEAD", "OPTIONS"]:
                response = await call_next(request)
                return response
            
            # Get token from header or form data
            token = None
            if "X-CSRF-Token" in request.headers:
                token = request.headers["X-CSRF-Token"]
            elif "csrf_token" in request.form:
                token = request.form["csrf_token"]
            
            # Get user ID from request (implement based on your auth system)
            user_id = None  # Extract from JWT or session
            
            # Validate token
            is_valid, message = self.validate_token(token, user_id)
            if not is_valid:
                return JSONResponse(
                    status_code=403,
                    content={"error": "CSRF token validation failed", "message": message}
                )
            
            response = await call_next(request)
            return response
        
        return csrf_middleware
    
    def get_csrf_stats(self) -> Dict[str, Any]:
        """Get CSRF protection statistics"""
        try:
            if not self.redis_client:
                return {"error": "Redis not available"}
            
            pattern = f"csrf_token:*"
            keys = self.redis_client.keys(pattern)
            
            total_tokens = len(keys)
            expired_tokens = 0
            active_tokens = 0
            
            current_time = time.time()
            for key in keys:
                try:
                    token_data_str = self.redis_client.get(key)
                    if token_data_str:
                        token_info = json.loads(token_data_str)
                        encrypted_data = base64.b64decode(token_info["data"])
                        decrypted_data = self.fernet.decrypt(encrypted_data)
                        token_data = json.loads(decrypted_data.decode())
                        
                        if current_time - token_data["timestamp"] > self.token_expiry:
                            expired_tokens += 1
                        else:
                            active_tokens += 1
                            
                except Exception:
                    # Skip invalid tokens
                    continue
            
            return {
                "total_tokens": total_tokens,
                "active_tokens": active_tokens,
                "expired_tokens": expired_tokens,
                "token_expiry": self.token_expiry,
                "max_tokens_per_user": self.max_tokens_per_user
            }
            
        except Exception as e:
            logger.error(f"Error getting CSRF stats: {e}")
            return {"error": str(e)}
