# 🧪 TESTING GUIDE - Unified Authentication System

## Quick Test Instructions

### **Test 1: Backend API**
```bash
cd /root/Crane-Intelligence

# Start backend
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &

# Wait 5 seconds
sleep 5

# Test API health
curl http://localhost:8000/api/v1/auth/health

# Test login API
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@craneintelligence.com","password":"DemoOnly123"}'
```

### **Test 2: Frontend (Browser)**

1. **Open Homepage:**
   ```
   http://your-domain/homepage.html
   ```

2. **Verify Initial State:**
   - ✅ Should see "Login" and "Sign Up" buttons
   - ✅ Should NOT see user profile

3. **Test Login:**
   - Click "Login" button
   - Enter credentials:
     - Email: `demo@craneintelligence.com`
     - Password: `DemoOnly123`
   - Click "Sign In"
   
4. **After Login, Verify:**
   - ✅ Login modal closes
   - ✅ Success notification appears
   - ✅ User profile dropdown appears with:
     - Avatar with initials
     - User name
     - Subscription tier
   - ✅ Login/Signup buttons disappear
   - ✅ Redirects to dashboard

5. **On Dashboard, Verify:**
   - ✅ User profile dropdown persists
   - ✅ Shows correct user info
   - ✅ No login buttons visible

6. **Test Logout:**
   - Click user profile dropdown
   - Click "Logout"
   - Verify:
     - ✅ Redirects to homepage
     - ✅ Login/Signup buttons appear
     - ✅ User profile disappears

### **Test 3: Browser Console Checks**

Open browser console (F12) and check:

```javascript
// Check tokens are stored
console.log('Access Token:', localStorage.getItem('access_token') ? 'YES' : 'NO');
console.log('User Data:', localStorage.getItem('user_data'));

// Check unified auth is loaded
console.log('Unified Auth:', typeof window.unifiedAuth);

// Test auth status
await window.unifiedAuth.checkAuthStatus();
```

## Expected Results

### **When NOT Logged In:**
```
Header: [Logo] [Nav Menu] [Login] [Sign Up]
localStorage: {empty}
API calls: None
```

### **When Logged In:**
```
Header: [Logo] [Nav Menu] [User Profile ▼]
localStorage: {
  access_token: "eyJ...",
  refresh_token: "eyJ...",
  user_data: "{...}"
}
API calls: GET /api/v1/auth/profile (on page load)
```

## Common Issues & Solutions

### Issue 1: "API not responding"
**Solution:**
```bash
# Check if backend is running
ps aux | grep uvicorn

# Restart backend
cd /root/Crane-Intelligence/backend
pkill -f uvicorn
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Issue 2: "Login button does nothing"
**Solution:**
- Check browser console for errors
- Verify unified-auth.js is loaded:
  ```javascript
  console.log(typeof window.unifiedAuth);
  ```
- Clear browser cache

### Issue 3: "User profile not showing after login"
**Solution:**
- Check localStorage:
  ```javascript
  console.log(localStorage.getItem('access_token'));
  console.log(localStorage.getItem('user_data'));
  ```
- If tokens are there, try:
  ```javascript
  window.unifiedAuth.updateHeaderUI(true);
  ```

### Issue 4: "Database connection error"
**Solution:**
- Backend may need database connection
- Check if using SQLite or PostgreSQL
- Verify database credentials in `.env` file

## Test Accounts

### Account 1: Demo User
- **Email:** `demo@craneintelligence.com`
- **Password:** `DemoOnly123`
- **Tier:** Pro
- **Status:** Active

### Account 2: Test User
- **Email:** `kankanamitra01@gmail.com`
- **Password:** `password123`
- **Tier:** Basic
- **Status:** Active

## Automated Test Script

```bash
#!/bin/bash
# Save as test_auth.sh

echo "🧪 Testing Crane Intelligence Authentication..."
echo ""

# Test 1: API Health
echo "Test 1: API Health Check"
response=$(curl -s http://localhost:8000/api/v1/auth/health)
if [ -n "$response" ]; then
    echo "✅ API is responding"
else
    echo "❌ API not responding"
    exit 1
fi
echo ""

# Test 2: Login API
echo "Test 2: Login API"
login_response=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@craneintelligence.com","password":"DemoOnly123"}')

if echo "$login_response" | grep -q "access_token"; then
    echo "✅ Login successful"
else
    echo "❌ Login failed"
    echo "Response: $login_response"
    exit 1
fi
echo ""

# Test 3: Profile API
echo "Test 3: Profile API"
token=$(echo "$login_response" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['tokens']['access_token'])")
profile_response=$(curl -s -H "Authorization: Bearer $token" http://localhost:8000/api/v1/auth/profile)

if echo "$profile_response" | grep -q "user"; then
    echo "✅ Profile retrieved successfully"
else
    echo "❌ Profile retrieval failed"
    exit 1
fi
echo ""

echo "🎉 All tests passed!"
```

## Manual Checklist

- [ ] Backend API is running on port 8000
- [ ] Homepage loads without errors
- [ ] Login button opens modal
- [ ] Login with demo credentials works
- [ ] User profile appears after login
- [ ] User name and tier are correct
- [ ] Dropdown menu shows all options
- [ ] Logout works and redirects to homepage
- [ ] Login buttons reappear after logout
- [ ] Header persists across page navigation
- [ ] Responsive design works on mobile
- [ ] No console errors in browser

## Success Criteria

✅ User can log in successfully  
✅ User profile appears in header  
✅ User info is correct  
✅ Header persists across pages  
✅ Logout works correctly  
✅ No duplicate login handlers  
✅ API uses relative paths  
✅ Tokens stored consistently  
✅ No console errors  

---

**Last Updated:** October 9, 2025  
**Status:** Ready for Testing

