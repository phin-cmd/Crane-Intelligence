"""
Security Configuration
Centralized security configuration for the application
"""

import os
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Security levels for different environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class SecurityConfig:
    """Security configuration class"""
    
    # Environment
    environment: str = "development"
    debug: bool = False
    
    # SSL/TLS Configuration
    ssl_enabled: bool = True
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    ssl_ca_path: Optional[str] = None
    ssl_ciphers: str = "ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS"
    ssl_protocols: List[str] = None
    
    # Database Security
    db_encryption_key: Optional[str] = None
    db_connection_encrypted: bool = True
    db_audit_logging: bool = True
    db_query_logging: bool = False
    
    # Rate Limiting
    rate_limiting_enabled: bool = True
    rate_limiting_redis_url: Optional[str] = None
    rate_limiting_redis_db: int = 1
    rate_limiting_redis_password: Optional[str] = None
    
    # Input Validation
    input_validation_enabled: bool = True
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    max_json_depth: int = 10
    max_json_size: int = 1024 * 1024  # 1MB
    
    # XSS Protection
    xss_protection_enabled: bool = True
    xss_csp_enabled: bool = True
    xss_sanitization_enabled: bool = True
    
    # CSRF Protection
    csrf_protection_enabled: bool = True
    csrf_secret_key: Optional[str] = None
    csrf_token_expiry: int = 3600  # 1 hour
    csrf_redis_url: Optional[str] = None
    
    # SQL Injection Prevention
    sql_injection_prevention_enabled: bool = True
    sql_parameterized_queries_only: bool = True
    sql_query_whitelist: List[str] = None
    
    # Authentication & Authorization
    auth_jwt_secret: Optional[str] = None
    auth_jwt_algorithm: str = "HS256"
    auth_jwt_expiry: int = 3600  # 1 hour
    auth_password_min_length: int = 8
    auth_password_require_special: bool = True
    auth_password_require_uppercase: bool = True
    auth_password_require_lowercase: bool = True
    auth_password_require_numbers: bool = True
    
    # Session Security
    session_secure: bool = True
    session_httponly: bool = True
    session_samesite: str = "Strict"
    session_max_age: int = 3600  # 1 hour
    
    # CORS Configuration
    cors_origins: List[str] = None
    cors_methods: List[str] = None
    cors_headers: List[str] = None
    cors_credentials: bool = True
    
    # Security Headers
    security_headers_enabled: bool = True
    hsts_enabled: bool = True
    hsts_max_age: int = 31536000  # 1 year
    hsts_include_subdomains: bool = True
    hsts_preload: bool = True
    
    # Logging & Monitoring
    security_logging_enabled: bool = True
    security_log_level: str = "INFO"
    security_audit_logging: bool = True
    security_metrics_enabled: bool = True
    
    # IP Whitelisting/Blacklisting
    ip_whitelist: List[str] = None
    ip_blacklist: List[str] = None
    ip_geolocation_check: bool = False
    
    # File Upload Security
    file_upload_enabled: bool = True
    file_upload_max_size: int = 5 * 1024 * 1024  # 5MB
    file_upload_allowed_types: List[str] = None
    file_upload_scan_viruses: bool = False
    
    # API Security
    api_versioning_enabled: bool = True
    api_documentation_enabled: bool = True
    api_rate_limiting_per_endpoint: Dict[str, Dict[str, int]] = None
    
    def __post_init__(self):
        """Post-initialization setup"""
        if self.ssl_protocols is None:
            self.ssl_protocols = ["TLSv1.2", "TLSv1.3"]
        
        if self.sql_query_whitelist is None:
            self.sql_query_whitelist = [
                "SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER"
            ]
        
        if self.cors_origins is None:
            self.cors_origins = ["http://localhost:3000", "https://craneintelligence.tech"]
        
        if self.cors_methods is None:
            self.cors_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        
        if self.cors_headers is None:
            self.cors_headers = ["*"]
        
        if self.file_upload_allowed_types is None:
            self.file_upload_allowed_types = [
                "image/jpeg", "image/png", "image/gif", "application/pdf",
                "text/plain", "application/json", "text/csv"
            ]
        
        if self.api_rate_limiting_per_endpoint is None:
            self.api_rate_limiting_per_endpoint = {
                "/api/v1/auth/login": {"requests_per_minute": 5, "requests_per_hour": 20},
                "/api/v1/auth/register": {"requests_per_minute": 3, "requests_per_hour": 10},
                "/api/v1/valuation": {"requests_per_minute": 30, "requests_per_hour": 200},
                "default": {"requests_per_minute": 60, "requests_per_hour": 1000}
            }

def load_security_config() -> SecurityConfig:
    """Load security configuration from environment variables"""
    try:
        config = SecurityConfig()
        
        # Environment
        config.environment = os.getenv("ENVIRONMENT", "development")
        config.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # SSL/TLS Configuration
        config.ssl_enabled = os.getenv("SSL_ENABLED", "true").lower() == "true"
        config.ssl_cert_path = os.getenv("SSL_CERT_PATH")
        config.ssl_key_path = os.getenv("SSL_KEY_PATH")
        config.ssl_ca_path = os.getenv("SSL_CA_PATH")
        config.ssl_ciphers = os.getenv("SSL_CIPHERS", config.ssl_ciphers)
        
        # Database Security
        config.db_encryption_key = os.getenv("DB_ENCRYPTION_KEY")
        config.db_connection_encrypted = os.getenv("DB_CONNECTION_ENCRYPTED", "true").lower() == "true"
        config.db_audit_logging = os.getenv("DB_AUDIT_LOGGING", "true").lower() == "true"
        config.db_query_logging = os.getenv("DB_QUERY_LOGGING", "false").lower() == "true"
        
        # Rate Limiting
        config.rate_limiting_enabled = os.getenv("RATE_LIMITING_ENABLED", "true").lower() == "true"
        config.rate_limiting_redis_url = os.getenv("REDIS_URL")
        config.rate_limiting_redis_db = int(os.getenv("REDIS_DB", "1"))
        config.rate_limiting_redis_password = os.getenv("REDIS_PASSWORD")
        
        # Input Validation
        config.input_validation_enabled = os.getenv("INPUT_VALIDATION_ENABLED", "true").lower() == "true"
        config.max_request_size = int(os.getenv("MAX_REQUEST_SIZE", str(config.max_request_size)))
        config.max_json_depth = int(os.getenv("MAX_JSON_DEPTH", str(config.max_json_depth)))
        config.max_json_size = int(os.getenv("MAX_JSON_SIZE", str(config.max_json_size)))
        
        # XSS Protection
        config.xss_protection_enabled = os.getenv("XSS_PROTECTION_ENABLED", "true").lower() == "true"
        config.xss_csp_enabled = os.getenv("XSS_CSP_ENABLED", "true").lower() == "true"
        config.xss_sanitization_enabled = os.getenv("XSS_SANITIZATION_ENABLED", "true").lower() == "true"
        
        # CSRF Protection
        config.csrf_protection_enabled = os.getenv("CSRF_PROTECTION_ENABLED", "true").lower() == "true"
        config.csrf_secret_key = os.getenv("CSRF_SECRET_KEY")
        config.csrf_token_expiry = int(os.getenv("CSRF_TOKEN_EXPIRY", str(config.csrf_token_expiry)))
        config.csrf_redis_url = os.getenv("CSRF_REDIS_URL")
        
        # SQL Injection Prevention
        config.sql_injection_prevention_enabled = os.getenv("SQL_INJECTION_PREVENTION_ENABLED", "true").lower() == "true"
        config.sql_parameterized_queries_only = os.getenv("SQL_PARAMETERIZED_QUERIES_ONLY", "true").lower() == "true"
        
        # Authentication & Authorization
        config.auth_jwt_secret = os.getenv("JWT_SECRET_KEY")
        config.auth_jwt_algorithm = os.getenv("JWT_ALGORITHM", config.auth_jwt_algorithm)
        config.auth_jwt_expiry = int(os.getenv("JWT_EXPIRY", str(config.auth_jwt_expiry)))
        config.auth_password_min_length = int(os.getenv("AUTH_PASSWORD_MIN_LENGTH", str(config.auth_password_min_length)))
        config.auth_password_require_special = os.getenv("AUTH_PASSWORD_REQUIRE_SPECIAL", "true").lower() == "true"
        config.auth_password_require_uppercase = os.getenv("AUTH_PASSWORD_REQUIRE_UPPERCASE", "true").lower() == "true"
        config.auth_password_require_lowercase = os.getenv("AUTH_PASSWORD_REQUIRE_LOWERCASE", "true").lower() == "true"
        config.auth_password_require_numbers = os.getenv("AUTH_PASSWORD_REQUIRE_NUMBERS", "true").lower() == "true"
        
        # Session Security
        config.session_secure = os.getenv("SESSION_SECURE", "true").lower() == "true"
        config.session_httponly = os.getenv("SESSION_HTTPONLY", "true").lower() == "true"
        config.session_samesite = os.getenv("SESSION_SAMESITE", config.session_samesite)
        config.session_max_age = int(os.getenv("SESSION_MAX_AGE", str(config.session_max_age)))
        
        # CORS Configuration
        cors_origins_str = os.getenv("CORS_ORIGINS")
        if cors_origins_str:
            config.cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]
        
        cors_methods_str = os.getenv("CORS_METHODS")
        if cors_methods_str:
            config.cors_methods = [method.strip() for method in cors_methods_str.split(",")]
        
        cors_headers_str = os.getenv("CORS_HEADERS")
        if cors_headers_str:
            config.cors_headers = [header.strip() for header in cors_headers_str.split(",")]
        
        config.cors_credentials = os.getenv("CORS_CREDENTIALS", "true").lower() == "true"
        
        # Security Headers
        config.security_headers_enabled = os.getenv("SECURITY_HEADERS_ENABLED", "true").lower() == "true"
        config.hsts_enabled = os.getenv("HSTS_ENABLED", "true").lower() == "true"
        config.hsts_max_age = int(os.getenv("HSTS_MAX_AGE", str(config.hsts_max_age)))
        config.hsts_include_subdomains = os.getenv("HSTS_INCLUDE_SUBDOMAINS", "true").lower() == "true"
        config.hsts_preload = os.getenv("HSTS_PRELOAD", "true").lower() == "true"
        
        # Logging & Monitoring
        config.security_logging_enabled = os.getenv("SECURITY_LOGGING_ENABLED", "true").lower() == "true"
        config.security_log_level = os.getenv("SECURITY_LOG_LEVEL", config.security_log_level)
        config.security_audit_logging = os.getenv("SECURITY_AUDIT_LOGGING", "true").lower() == "true"
        config.security_metrics_enabled = os.getenv("SECURITY_METRICS_ENABLED", "true").lower() == "true"
        
        # IP Whitelisting/Blacklisting
        ip_whitelist_str = os.getenv("IP_WHITELIST")
        if ip_whitelist_str:
            config.ip_whitelist = [ip.strip() for ip in ip_whitelist_str.split(",")]
        
        ip_blacklist_str = os.getenv("IP_BLACKLIST")
        if ip_blacklist_str:
            config.ip_blacklist = [ip.strip() for ip in ip_blacklist_str.split(",")]
        
        config.ip_geolocation_check = os.getenv("IP_GEOLOCATION_CHECK", "false").lower() == "true"
        
        # File Upload Security
        config.file_upload_enabled = os.getenv("FILE_UPLOAD_ENABLED", "true").lower() == "true"
        config.file_upload_max_size = int(os.getenv("FILE_UPLOAD_MAX_SIZE", str(config.file_upload_max_size)))
        
        file_upload_types_str = os.getenv("FILE_UPLOAD_ALLOWED_TYPES")
        if file_upload_types_str:
            config.file_upload_allowed_types = [file_type.strip() for file_type in file_upload_types_str.split(",")]
        
        config.file_upload_scan_viruses = os.getenv("FILE_UPLOAD_SCAN_VIRUSES", "false").lower() == "true"
        
        # API Security
        config.api_versioning_enabled = os.getenv("API_VERSIONING_ENABLED", "true").lower() == "true"
        config.api_documentation_enabled = os.getenv("API_DOCUMENTATION_ENABLED", "true").lower() == "true"
        
        # Validate configuration
        _validate_security_config(config)
        
        logger.info(f"Security configuration loaded for environment: {config.environment}")
        return config
        
    except Exception as e:
        logger.error(f"Error loading security configuration: {e}")
        raise

def _validate_security_config(config: SecurityConfig):
    """Validate security configuration"""
    errors = []
    
    # SSL Configuration
    if config.ssl_enabled:
        if not config.ssl_cert_path:
            errors.append("SSL certificate path is required when SSL is enabled")
        if not config.ssl_key_path:
            errors.append("SSL key path is required when SSL is enabled")
    
    # Database Security
    if config.db_connection_encrypted and not config.db_encryption_key:
        errors.append("Database encryption key is required when connection encryption is enabled")
    
    # Rate Limiting
    if config.rate_limiting_enabled and not config.rate_limiting_redis_url:
        errors.append("Redis URL is required when rate limiting is enabled")
    
    # CSRF Protection
    if config.csrf_protection_enabled and not config.csrf_secret_key:
        errors.append("CSRF secret key is required when CSRF protection is enabled")
    
    # Authentication
    if not config.auth_jwt_secret:
        errors.append("JWT secret key is required for authentication")
    
    # Password requirements
    if config.auth_password_min_length < 8:
        errors.append("Password minimum length must be at least 8 characters")
    
    # File upload
    if config.file_upload_enabled and config.file_upload_max_size <= 0:
        errors.append("File upload max size must be greater than 0")
    
    if errors:
        raise ValueError(f"Security configuration validation failed: {'; '.join(errors)}")

def get_security_config() -> SecurityConfig:
    """Get the current security configuration"""
    return load_security_config()

def update_security_config(**kwargs) -> SecurityConfig:
    """Update security configuration with new values"""
    config = get_security_config()
    
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            logger.warning(f"Unknown security configuration key: {key}")
    
    _validate_security_config(config)
    return config
