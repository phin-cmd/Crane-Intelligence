# Production Security Guide
## Comprehensive Security Implementation for Crane Intelligence Platform

**Version:** 1.0  
**Last Updated:** December 2024  
**Status:** CRITICAL - Production Deployment Requirements

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [SQL Injection Prevention](#sql-injection-prevention)
3. [Payment Security & Manipulation Prevention](#payment-security--manipulation-prevention)
4. [Code Obfuscation & Information Disclosure Prevention](#code-obfuscation--information-disclosure-prevention)
5. [Database Security & Obfuscation](#database-security--obfuscation)
6. [API Security & Rate Limiting](#api-security--rate-limiting)
7. [Bot & Crawler Protection](#bot--crawler-protection)
8. [Authentication & Authorization](#authentication--authorization)
9. [Input Validation & Sanitization](#input-validation--sanitization)
10. [Network & Infrastructure Security](#network--infrastructure-security)
11. [Monitoring & Incident Response](#monitoring--incident-response)
12. [Security Checklist](#security-checklist)

---

## Executive Summary

This guide provides **enterprise-grade security measures** to protect the Crane Intelligence Platform from:
- SQL injection attacks
- Payment manipulation and fraud
- Code inspection and reverse engineering
- Database enumeration and discovery
- Bot, crawler, and AI-based attacks
- Human attackers attempting to exploit vulnerabilities

**Security Level:** Maximum (Military-Grade)

---

## 1. SQL Injection Prevention

### 1.1 Current Status
✅ **Good:** Most queries use SQLAlchemy ORM (parameterized queries)  
⚠️ **Risk:** Some raw SQL queries using `text()` found in codebase

### 1.2 Implementation Requirements

#### A. Eliminate All Raw SQL Queries
**CRITICAL:** Replace all `db.execute(text(...))` with ORM queries or parameterized statements.

**Before (VULNERABLE):**
```python
# VULNERABLE - DO NOT USE
db.execute(text(f"SELECT * FROM users WHERE email = '{user_email}'"))
```

**After (SECURE):**
```python
# SECURE - Use ORM
user = db.query(User).filter(User.email == user_email).first()

# OR if raw SQL is absolutely necessary, use parameters
db.execute(text("SELECT * FROM users WHERE email = :email"), {"email": user_email})
```

#### B. Implement Query Parameterization Middleware
Create a middleware that intercepts and validates all database queries:

```python
# backend/app/security/query_validator.py
from sqlalchemy import event
from sqlalchemy.engine import Engine
import re
import logging

logger = logging.getLogger(__name__)

class SQLInjectionValidator:
    """Validates SQL queries for injection attempts"""
    
    DANGEROUS_PATTERNS = [
        r"(--|#|\/\*|\*\/)",  # SQL comments
        r"(union|select|insert|update|delete|drop|create|alter|exec|execute)",  # SQL keywords
        r"(\bor\b|\band\b)\s*\d+\s*=\s*\d+",  # OR/AND injection
        r"('|;|\||&|\$|`|\\x)",  # Dangerous characters
        r"(xp_|sp_|cmdshell)",  # SQL Server procedures
    ]
    
    @staticmethod
    def validate_query(query_string: str) -> bool:
        """Validate query for SQL injection patterns"""
        query_lower = query_string.lower()
        
        for pattern in SQLInjectionValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, query_lower, re.IGNORECASE):
                logger.warning(f"Potential SQL injection detected: {pattern}")
                return False
        return True

# Register event listener
@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Intercept SQL queries before execution"""
    if not SQLInjectionValidator.validate_query(statement):
        raise ValueError("SQL injection attempt detected and blocked")
```

#### C. Database Connection Security
```python
# backend/app/core/database.py - ENHANCED VERSION
from sqlalchemy import create_engine, event
from sqlalchemy.pool import QueuePool
import logging

logger = logging.getLogger(__name__)

# Production database configuration
engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,  # Recycle connections every hour
    connect_args={
        "connect_timeout": 10,
        "sslmode": "require",  # Force SSL for PostgreSQL
        "options": "-c statement_timeout=30000"  # 30 second timeout
    },
    echo=False  # NEVER enable SQL echo in production
)

# Add query timeout
@event.listens_for(engine, "before_cursor_execute")
def set_query_timeout(conn, cursor, statement, parameters, context, executemany):
    """Set query timeout for all queries"""
    cursor.execute("SET statement_timeout = '30s'")
```

### 1.3 Database User Permissions
**CRITICAL:** Application database user must have MINIMAL permissions:

```sql
-- Create application user with minimal permissions
CREATE USER crane_app WITH PASSWORD 'STRONG_PASSWORD_HERE';
GRANT CONNECT ON DATABASE crane_db TO crane_app;
GRANT USAGE ON SCHEMA public TO crane_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO crane_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO crane_app;

-- REVOKE dangerous permissions
REVOKE CREATE ON SCHEMA public FROM crane_app;
REVOKE DROP ON DATABASE crane_db FROM crane_app;
REVOKE ALL ON SCHEMA information_schema FROM crane_app;
REVOKE ALL ON SCHEMA pg_catalog FROM crane_app;
```

---

## 2. Payment Security & Manipulation Prevention

### 2.1 Server-Side Price Validation
**CRITICAL:** NEVER trust client-submitted prices. Always calculate prices server-side.

#### A. Implement Server-Side Price Calculation
```python
# backend/app/api/v1/fmv_reports.py - ENHANCED

@router.post("/create-payment-intent")
async def create_payment_intent(
    request: CreatePaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create payment intent with SERVER-SIDE price validation"""
    
    # CRITICAL: Calculate price server-side - IGNORE client-submitted amount
    stripe_service = get_stripe_service()
    pricing_service = FMVReportService()
    
    # Calculate actual price based on report type
    if request.report_type == "fleet_valuation":
        unit_count = request.crane_data.get("unit_count", 1)
        actual_price, tier = pricing_service.calculate_fleet_price_by_units(unit_count)
        actual_amount_cents = int(actual_price * 100)
    else:
        actual_price = pricing_service.get_base_price_dollars(request.report_type)
        actual_amount_cents = int(actual_price * 100)
    
    # SECURITY CHECK: Verify client-submitted amount matches server calculation
    if request.amount != actual_amount_cents:
        logger.warning(
            f"Price manipulation attempt detected! "
            f"User {current_user.id} submitted {request.amount} cents, "
            f"but server calculated {actual_amount_cents} cents"
        )
        # Log security event
        await log_security_event(
            user_id=current_user.id,
            event_type="payment_manipulation_attempt",
            details={
                "submitted_amount": request.amount,
                "calculated_amount": actual_amount_cents,
                "report_type": request.report_type
            }
        )
        raise HTTPException(
            status_code=400,
            detail="Invalid payment amount. Price calculated server-side."
        )
    
    # Create payment intent with SERVER-CALCULATED amount
    payment_intent = stripe_service.create_payment_intent(
        amount=actual_amount_cents,  # Use server-calculated amount
        currency="usd",
        customer_id=None,
        description=f"{request.report_type} Report",
        metadata={
            "user_id": str(current_user.id),
            "report_type": request.report_type,
            "calculated_server_side": "true",
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    
    return payment_intent
```

#### B. Webhook Signature Verification
**CRITICAL:** Always verify Stripe webhook signatures:

```python
# backend/app/api/v1/payment_webhooks.py - ENHANCED

@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Stripe webhooks with signature verification"""
    
    payload = await request.body()
    signature = request.headers.get("stripe-signature")
    
    if not signature:
        raise HTTPException(status_code=400, detail="Missing signature")
    
    stripe_service = get_stripe_service()
    
    # CRITICAL: Verify webhook signature
    try:
        event = stripe_service.verify_webhook_signature(
            payload=payload,
            signature=signature
        )
    except Exception as e:
        logger.error(f"Webhook signature verification failed: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Process verified event
    if event.type == "payment_intent.succeeded":
        payment_intent = event.data.object
        
        # CRITICAL: Verify amount matches database record
        report = db.query(FMVReport).filter(
            FMVReport.payment_intent_id == payment_intent.id
        ).first()
        
        if report:
            expected_amount = int(report.expected_amount * 100)  # Convert to cents
            if payment_intent.amount != expected_amount:
                logger.critical(
                    f"CRITICAL: Payment amount mismatch! "
                    f"Expected: {expected_amount}, Received: {payment_intent.amount}"
                )
                # Alert security team
                await alert_security_team("payment_amount_mismatch", {
                    "payment_intent_id": payment_intent.id,
                    "expected": expected_amount,
                    "received": payment_intent.amount
                })
                raise HTTPException(
                    status_code=400,
                    detail="Payment amount verification failed"
                )
```

#### C. Payment Amount Verification Middleware
```python
# backend/app/security/payment_validator.py

class PaymentAmountValidator:
    """Validates payment amounts server-side"""
    
    @staticmethod
    async def validate_payment_request(
        report_type: str,
        client_amount: int,
        crane_data: dict,
        db: Session
    ) -> tuple[bool, int, str]:
        """
        Validate payment amount
        Returns: (is_valid, server_calculated_amount, error_message)
        """
        pricing_service = FMVReportService()
        
        # Calculate server-side price
        if report_type == "fleet_valuation":
            unit_count = crane_data.get("unit_count", 1)
            price, tier = pricing_service.calculate_fleet_price_by_units(unit_count)
            server_amount = int(price * 100)
        else:
            price = pricing_service.get_base_price_dollars(report_type)
            server_amount = int(price * 100)
        
        # Verify amounts match
        if client_amount != server_amount:
            return False, server_amount, "Amount mismatch - price calculated server-side"
        
        return True, server_amount, ""
```

### 2.2 Frontend Payment Security
**CRITICAL:** Never expose pricing logic in frontend JavaScript.

```javascript
// js/simplified_purchase.js - SECURE VERSION

// DO NOT calculate prices in frontend
// Always fetch price from server
async function getServerCalculatedPrice(reportType, craneData) {
    const response = await fetch('/api/v1/fmv-reports/calculate-price', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getAuthToken()}`
        },
        body: JSON.stringify({
            report_type: reportType,
            crane_data: craneData
        })
    });
    
    const data = await response.json();
    return data.amount; // Use server-calculated amount
}

// Create payment intent with server-calculated amount
async function createPaymentIntent(reportType, craneData) {
    // Get server-calculated price
    const amount = await getServerCalculatedPrice(reportType, craneData);
    
    const response = await fetch('/api/v1/fmv-reports/create-payment-intent', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getAuthToken()}`
        },
        body: JSON.stringify({
            report_type: reportType,
            amount: amount, // Server-calculated amount
            crane_data: craneData
        })
    });
    
    return await response.json();
}
```

---

## 3. Code Obfuscation & Information Disclosure Prevention

### 3.1 API Endpoint Obfuscation
**CRITICAL:** Prevent attackers from discovering API structure through URLs.

#### A. Implement API Versioning & Obfuscation
```python
# backend/app/main.py - ENHANCED

# Use non-obvious API prefixes
app.include_router(
    fmv_reports_router, 
    prefix="/api/v1/cr",  # Obfuscated: "cr" instead of "fmv-reports"
    tags=["Reports"]
)

# Use UUID-based endpoints for sensitive operations
@router.post("/{report_id:uuid}/process")
async def process_report(report_id: UUID):
    """Use UUIDs instead of sequential IDs"""
    pass
```

#### B. Remove Information Disclosure
```python
# backend/app/main.py - SECURE CONFIGURATION

app = FastAPI(
    title="Crane Intelligence API",
    version="1.0.0",
    description="Professional Crane Valuation Platform",
    docs_url=None,  # DISABLE in production
    redoc_url=None,  # DISABLE in production
    openapi_url=None  # DISABLE OpenAPI schema in production
)

# Only enable docs in development
if settings.environment == "development":
    app.docs_url = "/docs"
    app.redoc_url = "/redoc"
    app.openapi_url = "/openapi.json"
```

#### C. Response Sanitization
```python
# backend/app/security/response_sanitizer.py

class ResponseSanitizer:
    """Sanitize API responses to prevent information disclosure"""
    
    SENSITIVE_FIELDS = [
        "password", "secret", "key", "token", "api_key",
        "database_url", "connection_string", "internal_id",
        "admin", "debug", "error_stack", "traceback"
    ]
    
    @staticmethod
    def sanitize_response(data: dict) -> dict:
        """Remove sensitive information from responses"""
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                key_lower = key.lower()
                if any(field in key_lower for field in ResponseSanitizer.SENSITIVE_FIELDS):
                    sanitized[key] = "***REDACTED***"
                elif isinstance(value, dict):
                    sanitized[key] = ResponseSanitizer.sanitize_response(value)
                elif isinstance(value, list):
                    sanitized[key] = [
                        ResponseSanitizer.sanitize_response(item) 
                        if isinstance(item, dict) else item
                        for item in value
                    ]
                else:
                    sanitized[key] = value
            return sanitized
        return data
```

### 3.2 Error Message Obfuscation
**CRITICAL:** Never expose internal errors to clients.

```python
# backend/app/core/exceptions.py

class SecureHTTPException(HTTPException):
    """Secure HTTP exception that doesn't leak information"""
    
    def __init__(self, status_code: int, detail: str = None, internal_error: str = None):
        # Log internal error for debugging
        if internal_error:
            logger.error(f"Internal error: {internal_error}")
        
        # Return generic error to client
        super().__init__(
            status_code=status_code,
            detail=detail or "An error occurred. Please try again later."
        )

# Usage
try:
    user = db.query(User).filter(User.email == email).first()
except Exception as e:
    raise SecureHTTPException(
        status_code=500,
        detail="Unable to process request",
        internal_error=str(e)
    )
```

### 3.3 Email & Link Security
**CRITICAL:** Prevent information disclosure through emails and links.

```python
# backend/app/services/fmv_email_service.py - ENHANCED

class SecureEmailService:
    """Email service with security features"""
    
    def send_report_email(self, user: User, report: FMVReport):
        """Send report email with secure links"""
        
        # Generate secure, time-limited token
        token = self.generate_secure_token(
            user_id=user.id,
            report_id=report.id,
            expires_in=timedelta(hours=24)
        )
        
        # Use obfuscated URLs
        report_url = f"https://craneintelligence.tech/reports/{token}"
        # NOT: f"https://craneintelligence.tech/reports/{report.id}"
        
        # Email content
        email_content = f"""
        Your report is ready.
        View report: {report_url}
        (Link expires in 24 hours)
        """
        
        # Send email
        self.send_email(user.email, "Your Report is Ready", email_content)
    
    def generate_secure_token(self, user_id: int, report_id: int, expires_in: timedelta) -> str:
        """Generate secure, time-limited token"""
        payload = {
            "user_id": user_id,
            "report_id": report_id,
            "exp": datetime.utcnow() + expires_in,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
```

---

## 4. Database Security & Obfuscation

### 4.1 Table & Column Name Obfuscation
**CRITICAL:** Use non-obvious table and column names.

```python
# backend/app/models/fmv_report.py - OBFUSCATED

class FMVReport(Base):
    __tablename__ = "rpt_fmv"  # Obfuscated: "rpt_fmv" instead of "fmv_reports"
    
    id = Column(Integer, primary_key=True)
    usr_id = Column(Integer, ForeignKey("usr.id"), name="usr_id")  # Obfuscated column name
    rpt_type = Column(String, name="rpt_type")  # Obfuscated
    amt_paid = Column(Numeric, name="amt_paid")  # Obfuscated
    # ... other fields
    
    # Property accessors for code readability
    @property
    def user_id(self):
        return self.usr_id
    
    @user_id.setter
    def user_id(self, value):
        self.usr_id = value
```

### 4.2 Database Query Obfuscation
```python
# backend/app/core/database.py - ENHANCED

class ObfuscatedQuery:
    """Obfuscate database queries to prevent discovery"""
    
    # Map obfuscated names to real names
    TABLE_MAP = {
        "rpt": "fmv_reports",
        "usr": "users",
        "pay": "payments"
    }
    
    @staticmethod
    def obfuscate_table_name(table_name: str) -> str:
        """Convert real table name to obfuscated name"""
        for obf, real in ObfuscatedQuery.TABLE_MAP.items():
            if real == table_name:
                return obf
        return table_name
```

### 4.3 Database Connection String Security
**CRITICAL:** Never expose database connection strings.

```python
# backend/app/core/config.py - SECURE

class Settings(BaseSettings):
    # Store in environment variables, NEVER in code
    database_url: str = Field(..., env="DATABASE_URL")
    
    class Config:
        env_file = ".env"
        # Never commit .env to version control
        # Add to .gitignore
        
    @validator("database_url")
    def validate_database_url(cls, v):
        """Validate database URL format"""
        if "postgresql://" not in v and "sqlite://" not in v:
            raise ValueError("Invalid database URL format")
        
        # Log warning if using SQLite in production
        if "sqlite" in v and os.getenv("ENVIRONMENT") == "production":
            logger.critical("WARNING: SQLite detected in production!")
        
        return v
```

---

## 5. API Security & Rate Limiting

### 5.1 Enhanced Rate Limiting
```python
# backend/app/security/rate_limiter.py - ENHANCED

class AdvancedRateLimiter:
    """Advanced rate limiting with IP blocking"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.blocked_ips = set()
        
    async def check_rate_limit(
        self, 
        identifier: str, 
        endpoint: str,
        max_requests: int = 60,
        window_seconds: int = 60
    ) -> tuple[bool, dict]:
        """
        Check rate limit
        Returns: (is_allowed, details)
        """
        key = f"rate_limit:{identifier}:{endpoint}"
        
        # Get current count
        current = await self.redis.get(key)
        if current is None:
            await self.redis.setex(key, window_seconds, 1)
            return True, {"remaining": max_requests - 1}
        
        current = int(current)
        if current >= max_requests:
            # Block IP if exceeded multiple times
            if current >= max_requests * 2:
                await self.block_ip(identifier)
            
            return False, {
                "remaining": 0,
                "retry_after": window_seconds
            }
        
        await self.redis.incr(key)
        return True, {"remaining": max_requests - current - 1}
    
    async def block_ip(self, ip: str, duration: int = 3600):
        """Block IP address"""
        await self.redis.setex(f"blocked_ip:{ip}", duration, "1")
        self.blocked_ips.add(ip)
        logger.warning(f"IP {ip} blocked for {duration} seconds")
```

### 5.2 API Key Authentication
```python
# backend/app/security/api_key_auth.py

class APIKeyAuth:
    """API key authentication for additional security"""
    
    @staticmethod
    async def verify_api_key(api_key: str) -> bool:
        """Verify API key"""
        # Store API keys in database or environment
        valid_keys = os.getenv("API_KEYS", "").split(",")
        return api_key in valid_keys

# Usage in endpoints
@router.post("/sensitive-endpoint")
async def sensitive_endpoint(
    api_key: str = Header(..., alias="X-API-Key"),
    current_user: User = Depends(get_current_user)
):
    if not await APIKeyAuth.verify_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    # ... endpoint logic
```

---

## 6. Bot & Crawler Protection

### 6.1 CAPTCHA Integration
```python
# backend/app/security/captcha.py

import requests

class CAPTCHAVerifier:
    """Verify CAPTCHA tokens"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.verify_url = "https://www.google.com/recaptcha/api/siteverify"
    
    async def verify(self, token: str, remote_ip: str) -> bool:
        """Verify reCAPTCHA token"""
        response = requests.post(
            self.verify_url,
            data={
                "secret": self.secret_key,
                "response": token,
                "remoteip": remote_ip
            }
        )
        result = response.json()
        return result.get("success", False)

# Usage
@router.post("/register")
async def register(
    request: UserRegistrationRequest,
    captcha_token: str = Form(...),
    client_ip: str = Depends(get_client_ip)
):
    captcha = CAPTCHAVerifier(settings.RECAPTCHA_SECRET_KEY)
    if not await captcha.verify(captcha_token, client_ip):
        raise HTTPException(status_code=400, detail="CAPTCHA verification failed")
    # ... registration logic
```

### 6.2 Bot Detection Middleware
```python
# backend/app/security/bot_detector.py

class BotDetector:
    """Detect and block bots, crawlers, and AI agents"""
    
    BOT_USER_AGENTS = [
        "bot", "crawler", "spider", "scraper", "curl", "wget",
        "python-requests", "go-http-client", "java", "scrapy",
        "chatgpt", "gpt", "claude", "anthropic", "openai"
    ]
    
    @staticmethod
    def is_bot(user_agent: str) -> bool:
        """Detect if request is from a bot"""
        if not user_agent:
            return True  # No user agent = likely bot
        
        user_agent_lower = user_agent.lower()
        return any(bot in user_agent_lower for bot in BotDetector.BOT_USER_AGENTS)
    
    @staticmethod
    async def check_bot_behavior(
        ip: str,
        request_path: str,
        headers: dict
    ) -> tuple[bool, str]:
        """
        Check for bot-like behavior
        Returns: (is_bot, reason)
        """
        # Check user agent
        user_agent = headers.get("user-agent", "")
        if BotDetector.is_bot(user_agent):
            return True, f"Bot user agent detected: {user_agent}"
        
        # Check for missing common headers
        if not headers.get("accept-language"):
            return True, "Missing Accept-Language header"
        
        if not headers.get("accept"):
            return True, "Missing Accept header"
        
        # Check request frequency
        # (Implement rate limiting check here)
        
        return False, ""

# Middleware integration
@app.middleware("http")
async def bot_detection_middleware(request: Request, call_next):
    user_agent = request.headers.get("user-agent", "")
    client_ip = request.client.host
    
    is_bot, reason = await BotDetector.check_bot_behavior(
        client_ip,
        request.url.path,
        dict(request.headers)
    )
    
    if is_bot:
        logger.warning(f"Bot detected: {reason} from {client_ip}")
        return JSONResponse(
            status_code=403,
            content={"error": "Access denied"}
        )
    
    return await call_next(request)
```

### 6.3 Honeypot Fields
```python
# Frontend: Add hidden honeypot field
<input type="text" name="website" style="display:none" tabindex="-1" autocomplete="off">

# Backend: Check honeypot
@router.post("/contact")
async def contact_form(
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
    website: str = Form(None)  # Honeypot field
):
    # If honeypot is filled, it's a bot
    if website:
        logger.warning("Bot detected via honeypot field")
        return {"success": True}  # Fake success to not alert bot
    
    # Process legitimate request
    # ...
```

---

## 7. Authentication & Authorization

### 7.1 Enhanced JWT Security
```python
# backend/app/services/auth_service.py - ENHANCED

class SecureAuthService:
    """Enhanced authentication service"""
    
    def __init__(self):
        self.secret_key = os.getenv("SECRET_KEY")
        self.algorithm = "HS256"
        self.access_token_expire = timedelta(minutes=15)  # Short expiration
        self.refresh_token_expire = timedelta(days=7)
    
    def create_access_token(self, user_id: int, user_email: str) -> str:
        """Create JWT access token with enhanced security"""
        payload = {
            "sub": str(user_id),
            "email": user_email,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + self.access_token_expire,
            "type": "access",
            "jti": str(uuid.uuid4())  # JWT ID for revocation
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> dict:
        """Verify JWT token with additional checks"""
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            
            # Check token type
            if payload.get("type") != "access":
                raise ValueError("Invalid token type")
            
            # Check if token is revoked (store in Redis)
            jti = payload.get("jti")
            if await self.is_token_revoked(jti):
                raise ValueError("Token has been revoked")
            
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
```

### 7.2 Two-Factor Authentication (2FA)
```python
# backend/app/security/two_factor.py

import pyotp
import qrcode

class TwoFactorAuth:
    """Two-factor authentication implementation"""
    
    @staticmethod
    def generate_secret() -> str:
        """Generate 2FA secret"""
        return pyotp.random_base32()
    
    @staticmethod
    def generate_qr_code(secret: str, email: str) -> str:
        """Generate QR code for 2FA setup"""
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=email,
            issuer_name="Crane Intelligence"
        )
        return qrcode.make(totp_uri)
    
    @staticmethod
    def verify_token(secret: str, token: str) -> bool:
        """Verify 2FA token"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)

# Usage in login
@router.post("/login")
async def login(
    request: UserLoginRequest,
    two_factor_code: Optional[str] = None,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check if 2FA is enabled
    if user.two_factor_enabled:
        if not two_factor_code:
            raise HTTPException(status_code=400, detail="2FA code required")
        
        if not TwoFactorAuth.verify_token(user.two_factor_secret, two_factor_code):
            raise HTTPException(status_code=401, detail="Invalid 2FA code")
    
    # Generate token
    token = auth_service.create_access_token(user.id, user.email)
    return {"access_token": token}
```

---

## 8. Input Validation & Sanitization

### 8.1 Comprehensive Input Validation
```python
# backend/app/security/input_validator.py - ENHANCED

from pydantic import BaseModel, validator, Field
import re

class SecureInputValidator:
    """Comprehensive input validation"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, str]:
        """Validate password strength"""
        if len(password) < 12:
            return False, "Password must be at least 12 characters"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain digit"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain special character"
        
        return True, ""
    
    @staticmethod
    def sanitize_string(input_str: str) -> str:
        """Sanitize string input"""
        # Remove null bytes
        input_str = input_str.replace('\x00', '')
        
        # Remove control characters
        input_str = re.sub(r'[\x00-\x1F\x7F]', '', input_str)
        
        # Limit length
        if len(input_str) > 10000:
            input_str = input_str[:10000]
        
        return input_str.strip()

# Usage in Pydantic models
class SecureUserRegistration(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=12, max_length=128)
    
    @validator("email")
    def validate_email(cls, v):
        if not SecureInputValidator.validate_email(v):
            raise ValueError("Invalid email format")
        return SecureInputValidator.sanitize_string(v)
    
    @validator("password")
    def validate_password(cls, v):
        is_valid, error = SecureInputValidator.validate_password_strength(v)
        if not is_valid:
            raise ValueError(error)
        return v
```

---

## 9. Network & Infrastructure Security

### 9.1 HTTPS/TLS Configuration
```nginx
# nginx.conf - SECURE CONFIGURATION

server {
    listen 443 ssl http2;
    server_name craneintelligence.tech;
    
    # SSL Configuration
    ssl_certificate /etc/ssl/certs/craneintelligence.tech.crt;
    ssl_certificate_key /etc/ssl/private/craneintelligence.tech.key;
    
    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://js.stripe.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https://api.stripe.com;" always;
    
    # Hide server information
    server_tokens off;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;
    
    location / {
        proxy_pass http://localhost:8003;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name craneintelligence.tech;
    return 301 https://$server_name$request_uri;
}
```

### 9.2 Firewall Configuration
```bash
# UFW Firewall Rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP (redirects to HTTPS)
sudo ufw allow 443/tcp # HTTPS
sudo ufw enable
```

### 9.3 Database Firewall
```python
# PostgreSQL pg_hba.conf - SECURE CONFIGURATION

# Only allow local connections
host    all    all    127.0.0.1/32    scram-sha-256
host    all    all    ::1/128         scram-sha-256

# Deny all other connections
host    all    all    0.0.0.0/0       reject
```

---

## 10. Monitoring & Incident Response

### 10.1 Security Event Logging
```python
# backend/app/security/audit_logger.py

class SecurityAuditLogger:
    """Log all security events"""
    
    @staticmethod
    async def log_security_event(
        event_type: str,
        user_id: Optional[int],
        ip_address: str,
        details: dict,
        severity: str = "medium"
    ):
        """Log security event"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": ip_address,
            "details": details,
            "severity": severity
        }
        
        # Log to database
        await db.execute(
            text("INSERT INTO security_events (event_data) VALUES (:data)"),
            {"data": json.dumps(event)}
        )
        
        # Alert on high severity
        if severity == "high" or severity == "critical":
            await send_security_alert(event)
```

### 10.2 Intrusion Detection
```python
# backend/app/security/intrusion_detection.py

class IntrusionDetectionSystem:
    """Detect and respond to security threats"""
    
    THREAT_PATTERNS = [
        "sql_injection_attempt",
        "xss_attempt",
        "payment_manipulation",
        "brute_force_login",
        "unauthorized_access"
    ]
    
    async def detect_threat(self, event: dict) -> bool:
        """Detect security threats"""
        event_type = event.get("event_type")
        
        if event_type in self.THREAT_PATTERNS:
            # Block IP
            await self.block_ip(event["ip_address"], duration=3600)
            
            # Alert security team
            await self.send_alert(event)
            
            return True
        
        return False
```

---

## 11. Security Checklist

### Pre-Production Deployment

- [ ] **SQL Injection Prevention**
  - [ ] All raw SQL queries replaced with ORM or parameterized queries
  - [ ] Query validation middleware implemented
  - [ ] Database user has minimal permissions
  - [ ] SQL query logging disabled in production

- [ ] **Payment Security**
  - [ ] All prices calculated server-side
  - [ ] Client-submitted amounts validated against server calculations
  - [ ] Stripe webhook signatures verified
  - [ ] Payment amount verification in webhook handler
  - [ ] Payment logs include server-calculated amounts

- [ ] **Code Obfuscation**
  - [ ] API documentation disabled in production
  - [ ] OpenAPI schema disabled
  - [ ] Error messages don't leak internal information
  - [ ] API endpoints use non-obvious names
  - [ ] Sensitive data redacted from responses

- [ ] **Database Security**
  - [ ] Table and column names obfuscated
  - [ ] Database connection strings in environment variables
  - [ ] Database firewall configured
  - [ ] SSL required for database connections
  - [ ] Database backups encrypted

- [ ] **Authentication & Authorization**
  - [ ] JWT tokens with short expiration
  - [ ] 2FA enabled for admin users
  - [ ] Password strength requirements enforced
  - [ ] Account lockout after failed attempts
  - [ ] Session management implemented

- [ ] **Bot Protection**
  - [ ] CAPTCHA on sensitive endpoints
  - [ ] Bot detection middleware active
  - [ ] Honeypot fields in forms
  - [ ] Rate limiting configured
  - [ ] IP blocking for suspicious activity

- [ ] **Network Security**
  - [ ] HTTPS/TLS configured
  - [ ] Security headers set
  - [ ] Firewall rules configured
  - [ ] DDoS protection enabled
  - [ ] WAF (Web Application Firewall) configured

- [ ] **Monitoring**
  - [ ] Security event logging enabled
  - [ ] Intrusion detection system active
  - [ ] Alert system configured
  - [ ] Regular security audits scheduled

---

## 12. Implementation Priority

### Phase 1: Critical (Immediate)
1. SQL injection prevention
2. Payment amount validation
3. API documentation removal
4. Error message sanitization

### Phase 2: High Priority (Week 1)
1. Rate limiting
2. Bot detection
3. Database obfuscation
4. Enhanced authentication

### Phase 3: Medium Priority (Week 2-3)
1. CAPTCHA integration
2. 2FA implementation
3. Advanced monitoring
4. Intrusion detection

---

## 13. Security Testing

### Regular Security Audits
- [ ] Penetration testing (quarterly)
- [ ] Code security review (monthly)
- [ ] Dependency vulnerability scanning (weekly)
- [ ] Infrastructure security audit (quarterly)

### Automated Security Scanning
```bash
# Install security scanning tools
pip install bandit safety

# Run security scans
bandit -r backend/
safety check
```

---

## Conclusion

This guide provides comprehensive security measures for production deployment. **All critical items must be implemented before going live.**

**Remember:** Security is an ongoing process, not a one-time setup. Regularly review and update security measures.

---

**For questions or security concerns, contact the security team immediately.**

