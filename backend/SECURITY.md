# Security Implementation Guide

## Overview

This document outlines the comprehensive security measures implemented in the Crane Intelligence Platform. The security system includes SSL/TLS certificate management, database security, API rate limiting, input validation, SQL injection prevention, XSS protection, and CSRF protection.

## Security Components

### 1. SSL/TLS Certificate Management

**File**: `backend/app/security/ssl_manager.py`

**Features**:
- Self-signed certificate generation
- Certificate validation and monitoring
- SSL context configuration
- Certificate expiration tracking

**Usage**:
```python
from backend.app.security.ssl_manager import SSLManager

ssl_manager = SSLManager()
await ssl_manager.initialize()
cert_info = await ssl_manager.get_certificate_info()
```

### 2. Database Security

**File**: `backend/app/security/database_security.py`

**Features**:
- Secure connection string handling
- Password hashing with bcrypt
- Role-based access control (RBAC)
- Audit logging
- Connection encryption

**Usage**:
```python
from backend.app.security.database_security import DatabaseSecurityManager

db_security = DatabaseSecurityManager()
await db_security.initialize()
await db_security.log_audit_event(user_id, action, ip_address)
```

### 3. API Rate Limiting

**File**: `backend/app/security/rate_limiter.py`

**Features**:
- Redis-based rate limiting
- Multiple strategies (sliding window, token bucket)
- IP-based blocking
- Endpoint-specific limits
- Rate limit statistics

**Usage**:
```python
from backend.app.security.rate_limiter import RateLimiter

rate_limiter = RateLimiter()
await rate_limiter.initialize()
is_limited, details = await rate_limiter.is_rate_limited(identifier, endpoint, ip)
```

### 4. Input Validation

**File**: `backend/app/security/input_validator.py`

**Features**:
- String sanitization
- Email validation
- Password strength validation
- Alphanumeric validation
- UUID validation
- JSON validation

**Usage**:
```python
from backend.app.security.input_validator import InputValidator

validator = InputValidator()
sanitized = validator.sanitize_string(input_string)
is_valid = validator.validate_email(email)
```

### 5. SQL Injection Prevention

**File**: `backend/app/security/sql_injection_prevention.py`

**Features**:
- Parameterized query enforcement
- SQL query scanning
- Attack pattern detection
- Query whitelisting
- Prevention statistics

**Usage**:
```python
from backend.app.security.sql_injection_prevention import SQLInjectionPrevention

sql_prevention = SQLInjectionPrevention()
is_safe, threats = sql_prevention.scan_query(query)
```

### 6. XSS Protection

**File**: `backend/app/security/xss_protection.py`

**Features**:
- XSS attack detection
- HTML sanitization
- Content Security Policy (CSP) headers
- Output escaping
- Protection statistics

**Usage**:
```python
from backend.app.security.xss_protection import XSSProtection

xss_protection = XSSProtection()
is_xss, threats = xss_protection.detector.detect_xss(content)
```

### 7. CSRF Protection

**File**: `backend/app/security/csrf_protection.py`

**Features**:
- CSRF token generation
- Token validation
- Redis-based token storage
- Token expiration management
- Protection statistics

**Usage**:
```python
from backend.app.security.csrf_protection import CSRFProtection

csrf_protection = CSRFProtection()
token = csrf_protection.generate_token(user_id)
is_valid, message = csrf_protection.validate_token(token, user_id)
```

## Security Middleware

**File**: `backend/app/security/security_middleware.py`

The security middleware integrates all security components and provides:

- Request processing through security checks
- Rate limiting enforcement
- Input validation and sanitization
- XSS and CSRF protection
- Security header injection
- Audit logging
- Error handling

## Security Configuration

**File**: `backend/app/security/security_config.py`

Centralized configuration management with environment variable support:

- SSL/TLS settings
- Database security configuration
- Rate limiting configuration
- Input validation settings
- XSS protection settings
- CSRF protection settings
- Authentication settings
- Session security
- CORS configuration
- Security headers
- Logging and monitoring

## Security API Endpoints

**File**: `backend/app/api/v1/security.py`

RESTful API endpoints for security management:

- `/api/v1/security/status` - Overall security status
- `/api/v1/security/ssl/status` - SSL certificate status
- `/api/v1/security/database/status` - Database security status
- `/api/v1/security/rate-limiting/status` - Rate limiting status
- `/api/v1/security/xss/status` - XSS protection status
- `/api/v1/security/csrf/status` - CSRF protection status
- `/api/v1/security/input-validation/status` - Input validation status
- `/api/v1/security/sql-injection/status` - SQL injection prevention status
- `/api/v1/security/audit-logs` - Security audit logs
- `/api/v1/security/configuration` - Security configuration

## Environment Variables

Create a `.env` file with the following security variables:

```bash
# SSL/TLS
SSL_ENABLED=true
SSL_CERT_PATH=certs/cert.pem
SSL_KEY_PATH=certs/key.pem

# Database Security
DB_ENCRYPTION_KEY=your-encryption-key
DB_CONNECTION_ENCRYPTED=true
DB_AUDIT_LOGGING=true

# Rate Limiting
RATE_LIMITING_ENABLED=true
REDIS_URL=redis://localhost:6379

# Input Validation
INPUT_VALIDATION_ENABLED=true
MAX_REQUEST_SIZE=10485760

# XSS Protection
XSS_PROTECTION_ENABLED=true
XSS_CSP_ENABLED=true

# CSRF Protection
CSRF_PROTECTION_ENABLED=true
CSRF_SECRET_KEY=your-csrf-secret

# Authentication
JWT_SECRET_KEY=your-jwt-secret
AUTH_PASSWORD_MIN_LENGTH=8

# CORS
CORS_ORIGINS=http://localhost:3000,https://craneintelligence.tech
CORS_CREDENTIALS=true

# Security Headers
SECURITY_HEADERS_ENABLED=true
HSTS_ENABLED=true
```

## Installation

1. Install security dependencies:
```bash
pip install -r backend/requirements.txt
```

2. Set up environment variables:
```bash
cp backend/.env.security backend/.env
# Edit .env with your actual values
```

3. Initialize security components:
```bash
python -c "from backend.app.security.security_middleware import SecurityMiddleware; print('Security components initialized')"
```

## Testing

Test security endpoints:

```bash
# Test overall security status
curl http://localhost:8003/api/v1/security/status

# Test SSL status
curl http://localhost:8003/api/v1/security/ssl/status

# Test rate limiting
curl http://localhost:8003/api/v1/security/rate-limiting/status

# Test XSS protection
curl -X POST http://localhost:8003/api/v1/security/xss/scan \
  -H "Content-Type: application/json" \
  -d '{"content": "<script>alert(\"xss\")</script>"}'

# Test CSRF protection
curl http://localhost:8003/api/v1/security/csrf/generate-token
```

## Monitoring

The security system provides comprehensive monitoring through:

- Security status endpoints
- Audit logging
- Rate limiting statistics
- Attack detection and logging
- Performance metrics

## Best Practices

1. **Regular Security Updates**: Keep all security dependencies updated
2. **Certificate Management**: Monitor SSL certificate expiration
3. **Rate Limiting**: Adjust limits based on usage patterns
4. **Input Validation**: Validate all user inputs
5. **Audit Logging**: Regularly review security logs
6. **Error Handling**: Implement proper error handling for security failures
7. **Testing**: Regularly test security measures
8. **Documentation**: Keep security documentation updated

## Troubleshooting

### Common Issues

1. **SSL Certificate Errors**: Ensure certificate paths are correct
2. **Redis Connection Issues**: Check Redis server status
3. **Rate Limiting False Positives**: Adjust rate limit configurations
4. **Input Validation Errors**: Check validation rules
5. **CSRF Token Issues**: Verify token generation and validation

### Debug Mode

Enable debug mode for detailed security logging:

```bash
export DEBUG=true
export SECURITY_LOG_LEVEL=DEBUG
```

## Security Updates

The security system is designed to be easily extensible. To add new security measures:

1. Create a new security module in `backend/app/security/`
2. Implement the required security logic
3. Add configuration options to `security_config.py`
4. Integrate with `security_middleware.py`
5. Add API endpoints to `security.py`
6. Update documentation

## Support

For security-related issues or questions:

1. Check the security logs
2. Review the security configuration
3. Test individual security components
4. Consult the security API documentation
5. Contact the security team

## Compliance

This security implementation helps with:

- **OWASP Top 10** compliance
- **GDPR** data protection requirements
- **SOC 2** security controls
- **ISO 27001** information security management
- **PCI DSS** payment card industry standards

## Conclusion

The comprehensive security system provides multiple layers of protection for the Crane Intelligence Platform. Regular monitoring, testing, and updates ensure continued security effectiveness.
