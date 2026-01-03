# Security Implementation Guide
## Step-by-Step Implementation for Production Security

This guide provides **actionable code changes** to implement the security measures outlined in `PRODUCTION_SECURITY_GUIDE.md`.

---

## 1. Payment Security Implementation

### Step 1.1: Update Payment Endpoint with Server-Side Validation

**File:** `backend/app/api/v1/fmv_reports.py`

**Location:** Around line 436 where `amount = request_data.amount`

**Change Required:**

```python
# BEFORE (VULNERABLE):
amount = request_data.amount  # Amount in cents
# ... rest of code uses this amount directly

# AFTER (SECURE):
from ...security.payment_validator import payment_validator

# Get user_id for logging
user_id = None
if current_user:
    try:
        user_id = int(current_user.get("sub"))
    except:
        pass

# CRITICAL: Validate payment amount server-side
is_valid, server_amount, error_message = payment_validator.validate_payment_amount(
    report_type=report_type,
    client_amount=request_data.amount,
    crane_data=crane_data,
    user_id=user_id
)

if not is_valid:
    logger.error(
        f"Payment manipulation attempt blocked: "
        f"User {user_id}, Client Amount: ${request_data.amount/100:.2f}, "
        f"Server Amount: ${server_amount/100:.2f}"
    )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=error_message
    )

# Use server-calculated amount (not client-submitted)
amount = server_amount
```

### Step 1.2: Add Price Calculation Endpoint

**File:** `backend/app/api/v1/fmv_reports.py`

**Add this endpoint BEFORE the create-payment-intent endpoint:**

```python
@router.post("/calculate-price")
async def calculate_price(
    request: CreatePaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate price server-side
    This endpoint allows frontend to get the correct price before creating payment intent
    """
    from ...security.payment_validator import payment_validator
    
    try:
        # Calculate server-side price
        server_amount = payment_validator.calculate_server_price(
            report_type=request.report_type,
            crane_data=request.crane_data
        )
        
        return {
            "success": True,
            "amount": server_amount,
            "amount_dollars": server_amount / 100,
            "currency": "usd",
            "report_type": request.report_type
        }
    except Exception as e:
        logger.error(f"Error calculating price: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error calculating price"
        )
```

### Step 1.3: Update Frontend to Use Server-Calculated Prices

**File:** `js/simplified_purchase.js`

**Replace price calculation logic:**

```javascript
// BEFORE (VULNERABLE):
const amount = calculatePrice(reportType, craneData); // Client-side calculation

// AFTER (SECURE):
async function getServerPrice(reportType, craneData) {
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
    
    if (!response.ok) {
        throw new Error('Failed to calculate price');
    }
    
    const data = await response.json();
    return data.amount; // Server-calculated amount in cents
}

// Use in payment flow
const amount = await getServerPrice(reportType, craneData);
```

---

## 2. SQL Injection Prevention

### Step 2.1: Replace Raw SQL Queries

**Find all instances of `db.execute(text(...))` and replace with ORM queries.**

**Example 1: Health Check Endpoint**

**File:** `backend/app/api/v1/health.py`

**BEFORE:**
```python
db.execute(text("SELECT 1"))
```

**AFTER:**
```python
# Use ORM query instead
from ...models.user import User
db.query(User).first()  # Simple query to test connection
```

**Example 2: Consultation Endpoint**

**File:** `backend/app/api/v1/consultation.py`

**BEFORE:**
```python
result = db.execute(text("""
    SELECT COUNT(*) as count
    FROM consultation_requests
    WHERE status = :status
"""), {"status": "pending"})
```

**AFTER:**
```python
from ...models.consultation import ConsultationRequest
count = db.query(ConsultationRequest).filter(
    ConsultationRequest.status == "pending"
).count()
```

### Step 2.2: Add Query Validation Middleware

**File:** `backend/app/core/database.py`

**Add at the top of the file:**

```python
from sqlalchemy import event
from ..security.sql_injection_prevention import SQLInjectionPrevention

# Create global SQL injection prevention instance
sql_injection_prevention = SQLInjectionPrevention()

# Register event listener to intercept queries
@event.listens_for(engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Intercept SQL queries before execution"""
    try:
        # Validate query for SQL injection
        is_injection, threats = sql_injection_prevention.detector.detect_sql_injection(
            statement, 
            parameters
        )
        
        if is_injection:
            logger.critical(f"SQL INJECTION ATTEMPT BLOCKED: {threats}")
            raise ValueError("SQL injection attempt detected and blocked")
    except Exception as e:
        logger.error(f"Error in SQL injection prevention: {e}")
        raise
```

---

## 3. API Documentation Removal

### Step 3.1: Disable API Docs in Production

**File:** `backend/app/main.py`

**Find:**
```python
app = FastAPI(
    title="Crane Intelligence API",
    version="1.0.0",
    description="Professional Crane Valuation and Market Analysis Platform",
    docs_url="/docs",
    redoc_url="/redoc"
)
```

**Replace with:**
```python
from ...core.config import settings

# Disable docs in production
docs_url = "/docs" if settings.environment == "development" else None
redoc_url = "/redoc" if settings.environment == "development" else None
openapi_url = "/openapi.json" if settings.environment == "development" else None

app = FastAPI(
    title="Crane Intelligence API",
    version="1.0.0",
    description="Professional Crane Valuation and Market Analysis Platform",
    docs_url=docs_url,
    redoc_url=redoc_url,
    openapi_url=openapi_url
)
```

---

## 4. Error Message Sanitization

### Step 4.1: Create Secure Exception Handler

**File:** `backend/app/core/exceptions.py` (create new file)

```python
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
```

### Step 4.2: Update Error Handling

**File:** `backend/app/main.py`

**Add global exception handler:**

```python
from .core.exceptions import SecureHTTPException

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler that sanitizes errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Return generic error to client
    return JSONResponse(
        status_code=500,
        content={"error": "An internal error occurred. Please try again later."}
    )
```

---

## 5. Database Obfuscation

### Step 5.1: Update Model Table Names

**File:** `backend/app/models/fmv_report.py`

**Find:**
```python
class FMVReport(Base):
    __tablename__ = "fmv_reports"
```

**Replace with:**
```python
class FMVReport(Base):
    __tablename__ = "rpt_fmv"  # Obfuscated table name
```

**Note:** You'll need to create a database migration to rename the table:

```sql
ALTER TABLE fmv_reports RENAME TO rpt_fmv;
```

### Step 5.2: Update Column Names (Optional - Advanced)

**For maximum security, obfuscate column names:**

```python
class FMVReport(Base):
    __tablename__ = "rpt_fmv"
    
    id = Column(Integer, primary_key=True)
    usr_id = Column(Integer, ForeignKey("usr.id"), name="usr_id")  # Obfuscated
    rpt_type = Column(String, name="rpt_type")  # Obfuscated
    
    # Property accessors for code readability
    @property
    def user_id(self):
        return self.usr_id
    
    @user_id.setter
    def user_id(self, value):
        self.usr_id = value
```

---

## 6. Rate Limiting

### Step 6.1: Enable Rate Limiting Middleware

**File:** `backend/app/main.py`

**Add after CORS middleware:**

```python
from ..security.security_middleware import SecurityMiddleware

# Add security middleware
app.add_middleware(
    SecurityMiddleware,
    database_url=settings.database_url,
    secret_key=settings.SECRET_KEY
)
```

---

## 7. Bot Detection

### Step 7.1: Add Bot Detection Middleware

**File:** `backend/app/main.py`

**Add bot detection:**

```python
from ..security.bot_detector import BotDetector

@app.middleware("http")
async def bot_detection_middleware(request: Request, call_next):
    user_agent = request.headers.get("user-agent", "")
    client_ip = request.client.host if request.client else "unknown"
    
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

---

## 8. Security Headers

### Step 8.1: Update Nginx Configuration

**File:** `nginx.conf`

**Add security headers:**

```nginx
server {
    # ... existing config ...
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://js.stripe.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https://api.stripe.com;" always;
    
    # Hide server information
    server_tokens off;
}
```

---

## 9. Testing Security Implementation

### Step 9.1: Test Payment Manipulation Prevention

```bash
# Test with manipulated amount
curl -X POST http://localhost:8003/api/v1/fmv-reports/create-payment-intent \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "report_type": "professional",
    "amount": 100,  # Try to pay $1.00 instead of actual price
    "crane_data": {}
  }'

# Should return 400 error with message about amount mismatch
```

### Step 9.2: Test SQL Injection Prevention

```bash
# Test SQL injection attempt
curl -X GET "http://localhost:8003/api/v1/users?email=test@example.com' OR '1'='1" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Should be blocked by middleware
```

### Step 9.3: Test Bot Detection

```bash
# Test with bot user agent
curl -X GET http://localhost:8003/api/v1/health \
  -H "User-Agent: python-requests/2.28.0"

# Should return 403 Forbidden
```

---

## 10. Deployment Checklist

Before deploying to production, verify:

- [ ] Payment amount validation implemented
- [ ] All raw SQL queries replaced with ORM
- [ ] API documentation disabled
- [ ] Error messages sanitized
- [ ] Rate limiting enabled
- [ ] Bot detection active
- [ ] Security headers configured
- [ ] Database user has minimal permissions
- [ ] HTTPS/TLS configured
- [ ] Firewall rules set
- [ ] Monitoring and alerting configured

---

## 11. Monitoring Security Events

### Step 11.1: Set Up Security Event Logging

**File:** `backend/app/security/audit_logger.py` (create if doesn't exist)

```python
from datetime import datetime
import json
from sqlalchemy.orm import Session
from sqlalchemy import text

class SecurityAuditLogger:
    """Log all security events"""
    
    @staticmethod
    async def log_security_event(
        event_type: str,
        user_id: Optional[int],
        ip_address: str,
        details: dict,
        severity: str = "medium",
        db: Session = None
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
        
        # Log to database if available
        if db:
            try:
                db.execute(
                    text("""
                        INSERT INTO security_events (event_data, created_at)
                        VALUES (:data, NOW())
                    """),
                    {"data": json.dumps(event)}
                )
                db.commit()
            except Exception as e:
                logger.error(f"Failed to log security event: {e}")
        
        # Also log to application logs
        logger.warning(f"SECURITY EVENT: {json.dumps(event)}")
        
        # Alert on high severity
        if severity in ["high", "critical"]:
            # TODO: Send alert to security team
            logger.critical(f"CRITICAL SECURITY EVENT: {event_type} - {details}")
```

---

## 12. Quick Reference: Critical Files to Update

1. **Payment Security:**
   - `backend/app/api/v1/fmv_reports.py` - Add server-side validation
   - `js/simplified_purchase.js` - Use server-calculated prices

2. **SQL Injection:**
   - `backend/app/api/v1/health.py` - Replace raw SQL
   - `backend/app/api/v1/consultation.py` - Replace raw SQL
   - `backend/app/core/database.py` - Add query validation

3. **API Security:**
   - `backend/app/main.py` - Disable docs, add middleware

4. **Error Handling:**
   - `backend/app/core/exceptions.py` - Create secure exceptions
   - `backend/app/main.py` - Add global exception handler

5. **Infrastructure:**
   - `nginx.conf` - Add security headers
   - Database configuration - Set minimal permissions

---

## Conclusion

This guide provides step-by-step instructions to implement critical security measures. **Start with payment security and SQL injection prevention** as these are the highest priority.

For questions or issues during implementation, refer to `PRODUCTION_SECURITY_GUIDE.md` for detailed explanations.

