# Admin API Implementation Guide
## Crane Intelligence Platform - Backend Endpoints Required

**Date:** October 12, 2025  
**Status:** Frontend Complete - Backend Implementation Needed

## 📋 Overview

The admin portal frontend is **100% ready** with a comprehensive API client. All that's needed is to implement the backend endpoints.

## 🎯 Priority Implementation Order

### PHASE 1: Critical Endpoints (Implement First)
These are required for basic admin portal functionality:

1. **Authentication** (`/admin/auth/*`)
   - Login
   - Logout  
   - Get current user profile

2. **Dashboard** (`/admin/dashboard/*`)
   - Get dashboard metrics
   - Get recent activity

3. **Users** (`/admin/users`)
   - List users (with pagination)
   - Get user by ID
   - Create/Update/Delete user

4. **Database Stats** (`/admin/database/stats`)
   - Table counts
   - Database size
   - Connection status

### PHASE 2: High Priority
- Valuation statistics
- System health monitoring
- User activity logs

### PHASE 3: Medium Priority
- Market data refresh
- Core logic settings
- Analytics endpoints

### PHASE 4: Nice to Have
- Advanced filtering
- Bulk operations
- Export functionality

## 📁 Where to Implement

**File:** `/root/Crane-Intelligence/backend/app/api/v1/admin_comprehensive.py`

### Template Structure:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ...database import get_db
from ...services.auth_service import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])

# ===== AUTHENTICATION =====
@router.post("/auth/login")
async def admin_login(credentials: dict):
    """Admin login endpoint"""
    # Verify admin credentials
    # Generate JWT token
    # Return access_token, refresh_token
    pass

@router.get("/auth/me")
async def get_current_admin(current_user = Depends(get_current_user)):
    """Get current admin user profile"""
    return current_user

# ===== DASHBOARD =====
@router.get("/dashboard/data")
async def get_dashboard_data(db: Session = Depends(get_db)):
    """Get dashboard metrics and stats"""
    return {
        "metrics": {
            "active_users": db.query(User).filter(User.is_active == True).count(),
            "total_valuations": db.query(Valuation).count(),
            "monthly_revenue": calculate_monthly_revenue(db),
            # ... more metrics
        },
        "charts": {
            # Chart data
        },
        "recent_activity": get_recent_activity(db)
    }

# ===== USERS =====
@router.get("/users")
async def list_users(
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all users with pagination and search"""
    query = db.query(User)
    
    if search:
        query = query.filter(User.email.contains(search))
    
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    
    return {
        "users": users,
        "total": total,
        "page": (skip // limit) + 1,
        "per_page": limit
    }

# ===== DATABASE =====
@router.get("/database/stats")
async def get_database_stats(db: Session = Depends(get_db)):
    """Get database statistics"""
    return {
        "tables": [
            {
                "name": "users",
                "count": db.query(User).count(),
                "size_mb": get_table_size(db, "users")
            },
            {
                "name": "valuations",
                "count": db.query(Valuation).count(),
                "size_mb": get_table_size(db, "valuations")
            },
            # ... more tables
        ],
        "total_size_mb": get_database_size(db),
        "connection_status": "healthy"
    }

# ===== VALUATIONS =====
@router.get("/valuations/stats")
async def get_valuation_stats(db: Session = Depends(get_db)):
    """Get valuation statistics"""
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    
    return {
        "total": db.query(Valuation).count(),
        "today": db.query(Valuation).filter(Valuation.created_at >= today).count(),
        "this_week": db.query(Valuation).filter(Valuation.created_at >= week_ago).count(),
        "by_type": get_valuations_by_type(db),
        "by_region": get_valuations_by_region(db)
    }

# Add more endpoints...
```

## 🔐 Security Considerations

1. **Authentication Required:**
   - All endpoints must require admin authentication
   - Use `Depends(get_current_admin_user)` dependency
   - Verify user has admin role

2. **Rate Limiting:**
   - Implement rate limiting on sensitive endpoints
   - Especially for login attempts

3. **Input Validation:**
   - Validate all input parameters
   - Use Pydantic models for request bodies

4. **Audit Logging:**
   - Log all admin actions (create, update, delete)
   - Store in audit_logs table

## 📊 Database Queries Needed

### Users Table
```sql
-- Active users
SELECT COUNT(*) FROM users WHERE is_active = true;

-- New users today  
SELECT COUNT(*) FROM users WHERE DATE(created_at) = CURRENT_DATE;

-- Users by subscription
SELECT subscription_type, COUNT(*) 
FROM users 
GROUP BY subscription_type;
```

### Valuations Table
```sql
-- Total valuations
SELECT COUNT(*) FROM valuations;

-- Today's valuations
SELECT COUNT(*) FROM valuations WHERE DATE(created_at) = CURRENT_DATE;

-- Valuations by crane type
SELECT crane_type, COUNT(*) 
FROM valuations 
GROUP BY crane_type;

-- Valuations by region
SELECT region, COUNT(*) 
FROM valuations 
GROUP BY region;
```

### Revenue Calculation
```sql
-- Monthly revenue (assuming subscriptions table)
SELECT SUM(amount) 
FROM payments 
WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE);
```

## 🧪 Testing Endpoints

### Using cURL:
```bash
# Test login
curl -X POST http://localhost:8003/api/v1/admin/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'

# Test dashboard (with token)
curl -X GET http://localhost:8003/api/v1/admin/dashboard/data \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Test users list
curl -X GET "http://localhost:8003/api/v1/admin/users?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Using Browser Console:
```javascript
// Test API client
window.adminAPI.getDashboardData()
  .then(data => console.log('Dashboard data:', data))
  .catch(err => console.error('Error:', err));

// Test user list
window.adminAPI.getUsers({limit: 10, search: 'john'})
  .then(data => console.log('Users:', data))
  .catch(err => console.error('Error:', err));
```

## ✅ Frontend Files Already Updated

These files are **complete** and ready to use:

- ✅ `/var/www/html/admin/js/admin-api.js` - Complete API client (825 lines)
- ✅ `/var/www/html/admin/js/admin-login.js` - Complete login logic (498 lines)
- ✅ `/var/www/html/admin/js/admin-dashboard.js` - Dashboard logic (needs backend)
- ✅ All HTML pages exist and are styled

## 🚀 Quick Start Implementation

1. Create `admin_comprehensive.py` file
2. Implement authentication endpoints first
3. Test login flow
4. Implement dashboard data endpoint
5. Test dashboard displays
6. Continue with remaining endpoints

## 📝 Response Format Examples

See the main status document at:
`https://craneintelligence.tech/admin/ADMIN_PORTAL_UPDATE_STATUS.html`

## 🐛 Debugging

If issues occur:

1. Check backend logs: `tail -f /root/api_final.log`
2. Check browser console for errors
3. Verify token in localStorage: `localStorage.getItem('admin_token')`
4. Test API directly with cURL
5. Check database connection

## 📞 Next Steps

1. Review this guide
2. Implement critical endpoints
3. Test authentication
4. Test dashboard
5. Continue with remaining endpoints

**Frontend is ready - just need backend! 🚀**
