"""
Input Sanitization and Validation
Comprehensive input validation and sanitization system
"""

import re
import html
import json
import logging
import bleach
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from email.utils import parseaddr
from urllib.parse import urlparse
import phonenumbers
from pydantic import BaseModel, ValidationError, validator
from pydantic.types import EmailStr, HttpUrl, constr
import sqlalchemy
from sqlalchemy import text

logger = logging.getLogger(__name__)

class SecurityValidationError(Exception):
    """Custom exception for security validation errors"""
    pass

class InputValidator:
    """Comprehensive input validation and sanitization"""
    
    def __init__(self):
        self.sanitization_rules = {
            "html": {
                "allowed_tags": ["b", "i", "em", "strong", "p", "br"],
                "allowed_attributes": {},
                "strip": True
            },
            "sql": {
                "blocked_keywords": [
                    "DROP", "DELETE", "INSERT", "UPDATE", "SELECT", "UNION",
                    "ALTER", "CREATE", "EXEC", "EXECUTE", "SCRIPT", "TRUNCATE"
                ]
            },
            "xss": {
                "allowed_protocols": ["http", "https", "mailto"],
                "blocked_attributes": ["onclick", "onload", "onerror", "onmouseover"]
            }
        }
        
        # Compiled regex patterns for validation
        self.patterns = {
            "email": re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
            "phone": re.compile(r'^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$'),
            "alphanumeric": re.compile(r'^[a-zA-Z0-9]+$'),
            "alphanumeric_space": re.compile(r'^[a-zA-Z0-9\s]+$'),
            "numeric": re.compile(r'^[0-9]+$'),
            "decimal": re.compile(r'^[0-9]+\.?[0-9]*$'),
            "url": re.compile(r'^https?://[^\s/$.?#].[^\s]*$'),
            "uuid": re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'),
            "sql_injection": re.compile(r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)', re.IGNORECASE),
            "xss_patterns": re.compile(r'<script[^>]*>.*?</script>|<iframe[^>]*>.*?</iframe>|<object[^>]*>.*?</object>', re.IGNORECASE),
            "path_traversal": re.compile(r'\.\./|\.\.\\|%2e%2e%2f|%2e%2e%5c', re.IGNORECASE)
        }
    
    def sanitize_string(self, value: str, max_length: int = 1000, allow_html: bool = False) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            raise SecurityValidationError("Input must be a string")
        
        # Trim whitespace
        value = value.strip()
        
        # Check length
        if len(value) > max_length:
            raise SecurityValidationError(f"Input exceeds maximum length of {max_length}")
        
        # Check for SQL injection patterns
        if self.patterns["sql_injection"].search(value):
            raise SecurityValidationError("Potential SQL injection detected")
        
        # Check for XSS patterns
        if self.patterns["xss_patterns"].search(value):
            raise SecurityValidationError("Potential XSS attack detected")
        
        # Check for path traversal
        if self.patterns["path_traversal"].search(value):
            raise SecurityValidationError("Potential path traversal attack detected")
        
        # HTML sanitization
        if allow_html:
            value = bleach.clean(
                value,
                tags=self.sanitization_rules["html"]["allowed_tags"],
                attributes=self.sanitization_rules["html"]["allowed_attributes"],
                strip=self.sanitization_rules["html"]["strip"]
            )
        else:
            # Escape HTML entities
            value = html.escape(value)
        
        return value
    
    def validate_email(self, email: str) -> str:
        """Validate and sanitize email address"""
        if not email:
            raise SecurityValidationError("Email is required")
        
        # Basic format validation
        if not self.patterns["email"].match(email):
            raise SecurityValidationError("Invalid email format")
        
        # Parse email
        name, addr = parseaddr(email)
        if not addr:
            raise SecurityValidationError("Invalid email address")
        
        # Sanitize the email
        sanitized_email = self.sanitize_string(addr.lower(), max_length=254)
        
        # Additional validation
        if len(sanitized_email.split('@')[0]) > 64:
            raise SecurityValidationError("Email local part too long")
        
        return sanitized_email
    
    def validate_phone(self, phone: str) -> str:
        """Validate and sanitize phone number"""
        if not phone:
            raise SecurityValidationError("Phone number is required")
        
        # Remove all non-digit characters except +
        cleaned_phone = re.sub(r'[^\d+]', '', phone)
        
        try:
            # Parse with phonenumbers library
            parsed_phone = phonenumbers.parse(cleaned_phone, None)
            if not phonenumbers.is_valid_number(parsed_phone):
                raise SecurityValidationError("Invalid phone number")
            
            # Format as international
            formatted_phone = phonenumbers.format_number(parsed_phone, phonenumbers.PhoneNumberFormat.E164)
            return formatted_phone
            
        except phonenumbers.NumberParseException:
            raise SecurityValidationError("Invalid phone number format")
    
    def validate_url(self, url: str) -> str:
        """Validate and sanitize URL"""
        if not url:
            raise SecurityValidationError("URL is required")
        
        # Basic format validation
        if not self.patterns["url"].match(url):
            raise SecurityValidationError("Invalid URL format")
        
        # Parse URL
        parsed = urlparse(url)
        
        # Check protocol
        if parsed.scheme not in self.sanitization_rules["xss"]["allowed_protocols"]:
            raise SecurityValidationError("URL protocol not allowed")
        
        # Check for suspicious patterns
        if self.patterns["xss_patterns"].search(url):
            raise SecurityValidationError("URL contains potentially malicious content")
        
        return url
    
    def validate_numeric(self, value: Union[str, int, float], min_value: Optional[float] = None, 
                        max_value: Optional[float] = None, decimal_places: int = 2) -> float:
        """Validate and sanitize numeric input"""
        if value is None:
            raise SecurityValidationError("Numeric value is required")
        
        try:
            # Convert to float
            if isinstance(value, str):
                numeric_value = float(value)
            else:
                numeric_value = float(value)
            
            # Check range
            if min_value is not None and numeric_value < min_value:
                raise SecurityValidationError(f"Value must be at least {min_value}")
            
            if max_value is not None and numeric_value > max_value:
                raise SecurityValidationError(f"Value must be at most {max_value}")
            
            # Round to specified decimal places
            return round(numeric_value, decimal_places)
            
        except (ValueError, TypeError):
            raise SecurityValidationError("Invalid numeric value")
    
    def validate_integer(self, value: Union[str, int], min_value: Optional[int] = None, 
                        max_value: Optional[int] = None) -> int:
        """Validate and sanitize integer input"""
        if value is None:
            raise SecurityValidationError("Integer value is required")
        
        try:
            if isinstance(value, str):
                int_value = int(value)
            else:
                int_value = int(value)
            
            # Check range
            if min_value is not None and int_value < min_value:
                raise SecurityValidationError(f"Value must be at least {min_value}")
            
            if max_value is not None and int_value > max_value:
                raise SecurityValidationError(f"Value must be at most {max_value}")
            
            return int_value
            
        except (ValueError, TypeError):
            raise SecurityValidationError("Invalid integer value")
    
    def validate_date(self, date_str: str, format: str = "%Y-%m-%d") -> date:
        """Validate and sanitize date input"""
        if not date_str:
            raise SecurityValidationError("Date is required")
        
        try:
            parsed_date = datetime.strptime(date_str, format).date()
            
            # Check if date is reasonable (not too far in past/future)
            today = date.today()
            if parsed_date < date(1900, 1, 1):
                raise SecurityValidationError("Date too far in the past")
            
            if parsed_date > date(2100, 12, 31):
                raise SecurityValidationError("Date too far in the future")
            
            return parsed_date
            
        except ValueError:
            raise SecurityValidationError(f"Invalid date format. Expected: {format}")
    
    def validate_json(self, json_str: str, max_size: int = 10000) -> Dict[str, Any]:
        """Validate and sanitize JSON input"""
        if not json_str:
            raise SecurityValidationError("JSON is required")
        
        # Check size
        if len(json_str) > max_size:
            raise SecurityValidationError(f"JSON exceeds maximum size of {max_size} bytes")
        
        try:
            parsed_json = json.loads(json_str)
            
            # Recursively sanitize string values
            sanitized_json = self._sanitize_json_recursive(parsed_json)
            
            return sanitized_json
            
        except json.JSONDecodeError:
            raise SecurityValidationError("Invalid JSON format")
    
    def _sanitize_json_recursive(self, obj: Any) -> Any:
        """Recursively sanitize JSON object"""
        if isinstance(obj, dict):
            return {key: self._sanitize_json_recursive(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._sanitize_json_recursive(item) for item in obj]
        elif isinstance(obj, str):
            return self.sanitize_string(obj)
        else:
            return obj
    
    def validate_sql_safe(self, query: str, allowed_operations: List[str] = None) -> str:
        """Validate SQL query for safety"""
        if not query:
            raise SecurityValidationError("SQL query is required")
        
        # Check for blocked keywords
        query_upper = query.upper()
        blocked_keywords = self.sanitization_rules["sql"]["blocked_keywords"]
        
        for keyword in blocked_keywords:
            if keyword in query_upper:
                raise SecurityValidationError(f"SQL keyword '{keyword}' not allowed")
        
        # Check for SQL injection patterns
        if self.patterns["sql_injection"].search(query):
            raise SecurityValidationError("Potential SQL injection detected")
        
        # If allowed operations specified, check against them
        if allowed_operations:
            first_word = query.strip().split()[0].upper()
            if first_word not in allowed_operations:
                raise SecurityValidationError(f"SQL operation '{first_word}' not allowed")
        
        return query.strip()
    
    def validate_file_upload(self, filename: str, allowed_extensions: List[str] = None, 
                           max_size: int = 10485760) -> str:
        """Validate file upload parameters"""
        if not filename:
            raise SecurityValidationError("Filename is required")
        
        # Sanitize filename
        sanitized_filename = self.sanitize_string(filename, max_length=255)
        
        # Check for path traversal
        if self.patterns["path_traversal"].search(sanitized_filename):
            raise SecurityValidationError("Filename contains path traversal characters")
        
        # Check extension
        if allowed_extensions:
            file_ext = sanitized_filename.split('.')[-1].lower()
            if file_ext not in allowed_extensions:
                raise SecurityValidationError(f"File extension '.{file_ext}' not allowed")
        
        return sanitized_filename
    
    def validate_password(self, password: str, min_length: int = 8, 
                         require_uppercase: bool = True, require_lowercase: bool = True,
                         require_numbers: bool = True, require_special: bool = True) -> str:
        """Validate password strength"""
        if not password:
            raise SecurityValidationError("Password is required")
        
        if len(password) < min_length:
            raise SecurityValidationError(f"Password must be at least {min_length} characters")
        
        if require_uppercase and not re.search(r'[A-Z]', password):
            raise SecurityValidationError("Password must contain at least one uppercase letter")
        
        if require_lowercase and not re.search(r'[a-z]', password):
            raise SecurityValidationError("Password must contain at least one lowercase letter")
        
        if require_numbers and not re.search(r'[0-9]', password):
            raise SecurityValidationError("Password must contain at least one number")
        
        if require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise SecurityValidationError("Password must contain at least one special character")
        
        # Check for common weak passwords
        weak_passwords = ['password', '123456', 'qwerty', 'abc123', 'password123']
        if password.lower() in weak_passwords:
            raise SecurityValidationError("Password is too common")
        
        return password
    
    def validate_csrf_token(self, token: str, expected_token: str) -> bool:
        """Validate CSRF token"""
        if not token or not expected_token:
            raise SecurityValidationError("CSRF token is required")
        
        if not isinstance(token, str) or not isinstance(expected_token, str):
            raise SecurityValidationError("CSRF token must be a string")
        
        # Use constant-time comparison to prevent timing attacks
        if len(token) != len(expected_token):
            return False
        
        result = 0
        for a, b in zip(token, expected_token):
            result |= ord(a) ^ ord(b)
        
        return result == 0
    
    def get_validation_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get validation summary for data"""
        summary = {
            "total_fields": len(data),
            "validated_fields": 0,
            "errors": [],
            "warnings": []
        }
        
        for field, value in data.items():
            try:
                if isinstance(value, str):
                    self.sanitize_string(value)
                elif isinstance(value, (int, float)):
                    self.validate_numeric(value)
                elif isinstance(value, dict):
                    self.validate_json(json.dumps(value))
                
                summary["validated_fields"] += 1
                
            except SecurityValidationError as e:
                summary["errors"].append({
                    "field": field,
                    "error": str(e)
                })
        
        return summary
