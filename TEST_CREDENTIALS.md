# 🔐 Test Credentials for Crane Intelligence Platform

## Demo/Test Account (Recommended)

Use this account for testing all features:

```
Email:    demo@craneintelligence.com
Username: demo
Password: demo123
```

**Features Available:**
- ✅ Login to dashboard
- ✅ Create valuations
- ✅ Browse crane listings
- ✅ Add items to watchlist
- ✅ Set price alerts
- ✅ View notifications
- ✅ Access all user features

---

## How to Login

### Method 1: Web Interface
1. Navigate to: http://localhost:3001/login.html
2. Enter email: `demo@craneintelligence.com`
3. Enter password: `demo123`
4. Click "Login"

### Method 2: API Direct
```bash
curl -X POST http://localhost:3001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@craneintelligence.com",
    "password": "demo123"
  }'
```

### Method 3: JavaScript Console
Open browser console on any page and run:
```javascript
const api = window.craneAPI;
const result = await api.login('demo@craneintelligence.com', 'demo123');
console.log(result);
```

---

## Other Available Test Accounts

### Test User
```
Email:    test@craneintelligence.com
Username: testuser
Password: (not set - use demo account instead)
```

### Admin User
```
Email:    admin@craneintelligence.com
Username: admin
Password: (not set - use demo account instead)
```

### Kankana Mitra (Existing User)
```
Email:    kankanamitra01@gmail.com
Username: kankanamitra01
Password: (user's own password)
```

---

## Quick Test Workflow

### 1. Login
Visit: http://localhost:3001/login.html
```
Email: demo@craneintelligence.com
Password: demo123
```

### 2. View Dashboard
After login, you'll be redirected to:
http://localhost:3001/dashboard.html

**You'll see:**
- Total crane listings (13)
- Your valuations (0 initially)
- Watchlist count (0 initially)
- Recent listings from database
- Notifications

### 3. Create a Valuation
Navigate to: http://localhost:3001/valuation_terminal.html

**Fill in the form:**
- Manufacturer: Liebherr
- Model: LTM 1200-5.1
- Year: 2018
- Condition: excellent
- Hours: 5000

Click "Calculate Valuation" and you'll get:
- Estimated value based on real market data
- Confidence score
- Comparable sales information

### 4. Browse Listings
Navigate to: http://localhost:3001/homepage.html

**Available listings:**
- 13 crane listings from database
- Filter by manufacturer, price, condition
- Add to watchlist
- View details

### 5. Check Market Data
Navigate to: http://localhost:3001/market-analysis.html

**You'll see:**
- 18 market data records
- Price trends by crane type
- Regional analysis
- Volume metrics

---

## API Testing with Demo Account

### Get Access Token
```bash
TOKEN=$(curl -s -X POST http://localhost:3001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@craneintelligence.com","password":"demo123"}' \
  | jq -r '.access_token')

echo $TOKEN
```

### Use Token for Protected Endpoints
```bash
# Get user profile
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:3001/api/v1/users/me

# Get valuations
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:3001/api/v1/valuations

# Get watchlist
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:3001/api/v1/watchlist

# Get notifications
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:3001/api/v1/notifications
```

---

## Testing Valuation API

### Create a Valuation
```bash
curl -X POST http://localhost:3001/api/v1/valuations \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "crane_make": "Liebherr",
    "crane_model": "LTM 1200-5.1",
    "crane_year": 2018,
    "crane_condition": "excellent",
    "crane_hours": 5000
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Valuation completed successfully",
  "valuation_id": 1,
  "estimated_value": 977500.0,
  "confidence_score": 0.85
}
```

---

## Testing Watchlist

### Add to Watchlist
```bash
curl -X POST http://localhost:3001/api/v1/watchlist \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"crane_listing_id": 4}'
```

### View Watchlist
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:3001/api/v1/watchlist
```

---

## Testing Price Alerts

### Create Price Alert
```bash
curl -X POST http://localhost:3001/api/v1/price-alerts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "crane_make": "Liebherr",
    "crane_model": "LTM 1200-5.1",
    "target_price": 800000,
    "condition": "below"
  }'
```

### View Price Alerts
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:3001/api/v1/price-alerts
```

---

## Verify Login Working

Run this quick test:
```bash
#!/bin/bash
echo "Testing demo account login..."

response=$(curl -s -X POST http://localhost:3001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@craneintelligence.com","password":"demo123"}')

if echo "$response" | grep -q "success.*true"; then
    echo "✅ Login successful!"
    echo ""
    echo "Response:"
    echo "$response" | python3 -m json.tool
else
    echo "❌ Login failed!"
    echo "Response: $response"
fi
```

---

## Database Verification

Check if demo user exists:
```bash
docker exec crane-intelligence-db-1 psql -U crane_user -d crane_intelligence \
  -c "SELECT id, email, username, full_name, is_active, is_verified FROM users WHERE email='demo@craneintelligence.com';"
```

**Expected Output:**
```
 id |           email            | username | full_name | is_active | is_verified 
----+----------------------------+----------+-----------+-----------+-------------
  8 | demo@craneintelligence.com | demo     | Demo User | t         | t
```

---

## Troubleshooting Login Issues

### Issue: "Invalid credentials"
**Solution:** 
```bash
# Reset demo user password
docker exec crane-intelligence-db-1 psql -U crane_user -d crane_intelligence -c "
UPDATE users 
SET hashed_password = '7179b193a56be2c442a5f112f400d35afe8e47c9459efb0bb6341765cc653a01:13ad5975dd5bad48c08cf66ec9c03f76'
WHERE email = 'demo@craneintelligence.com';
"
```

### Issue: "Account is deactivated"
**Solution:**
```bash
# Activate demo user
docker exec crane-intelligence-db-1 psql -U crane_user -d crane_intelligence -c "
UPDATE users 
SET is_active = true, is_verified = true
WHERE email = 'demo@craneintelligence.com';
"
```

### Issue: Login page not loading
**Solution:**
- Check if frontend is running: `docker ps | grep frontend`
- Access login directly: http://localhost:3001/login.html
- Check nginx logs: `docker logs crane-intelligence-frontend-1`

---

## Create Your Own Test User

If you want to create additional test users:

```bash
# Generate password hash
docker exec crane-intelligence-backend-1 python3 -c "
import hashlib, secrets
password = 'your_password_here'
salt = secrets.token_hex(16)
hashed = hashlib.sha256((password + salt).encode()).hexdigest() + ':' + salt
print(hashed)
"

# Then insert into database
docker exec crane-intelligence-db-1 psql -U crane_user -d crane_intelligence -c "
INSERT INTO users (email, username, full_name, hashed_password, is_active, is_verified, user_role)
VALUES ('your@email.com', 'username', 'Full Name', 'PASTE_HASH_HERE', true, true, 'user');
"
```

---

## Summary

**PRIMARY TEST ACCOUNT:**
```
🔑 Email:    demo@craneintelligence.com
👤 Username: demo
🔐 Password: demo123
```

**LOGIN URL:** http://localhost:3001/login.html

**✅ Account Status:** Active and Verified

**🎯 Ready to Use!**

---

**Last Updated:** October 10, 2025
**Status:** ✅ TESTED AND WORKING

