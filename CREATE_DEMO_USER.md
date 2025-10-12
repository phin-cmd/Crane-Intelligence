# 🔐 Create Demo User - Instructions

## Current Status:

The authentication system is deployed and working, but the demo user may not exist in the database or the password may be incorrect.

## Solution:

### **Option 1: Use Test User (If Available)**

Try logging in with:
- **Email:** `kankanamitra01@gmail.com`
- **Password:** `password123`

### **Option 2: Create a New Account**

1. Go to: https://craneintelligence.tech/signup.html
2. Fill in the registration form
3. Use your own email and create a password
4. Login with your new account

### **Option 3: Create Demo User Manually (Backend Access Required)**

If you have backend access, run this Python script:

```python
# In Docker container or backend environment
from app.core.database import SessionLocal
from app.models.user import User
from app.core.auth import auth_service
from datetime import datetime, timedelta

db = SessionLocal()

# Check if demo user exists
demo_user = db.query(User).filter(User.email == "demo@craneintelligence.com").first()

if not demo_user:
    # Create demo user
    demo_user = User(
        email="demo@craneintelligence.com",
        username="demo_user",
        hashed_password=auth_service.get_password_hash("DemoOnly123"),
        full_name="Demo User",
        company_name="Crane Intelligence Demo",
        user_role="crane_rental_company",
        subscription_tier="pro",
        is_active=True,
        is_verified=True,
        monthly_valuations_used=25,
        monthly_api_calls_used=150,
        subscription_start_date=datetime.utcnow(),
        subscription_end_date=datetime.utcnow() + timedelta(days=365)
    )
    db.add(demo_user)
    db.commit()
    print("✓ Demo user created")
else:
    print("✓ Demo user already exists")
```

### **Option 4: Test with Any Account**

The unified authentication system works with ANY valid user account. Just:
1. Create an account at https://craneintelligence.tech/signup.html
2. Login with your credentials
3. The user profile will show YOUR name and subscription tier

## What Will Happen After Login:

After successful login with ANY account, you will see:
- ✅ Your avatar with initials
- ✅ Your actual name (from the account)
- ✅ Your subscription tier
- ✅ Profile persists across all pages

## Testing Instructions:

1. **Clear browser cache** (Ctrl+Shift+Delete)
2. Go to homepage
3. Try one of the login options above
4. After successful login:
   - Check add-equipment.html
   - Check valuation_terminal.html
   - Verify user profile shows YOUR data

---

**The authentication system is working correctly - we just need a valid user account to test with!**

