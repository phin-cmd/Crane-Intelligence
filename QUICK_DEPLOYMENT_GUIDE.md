# Quick Deployment Guide - Security Enabled

## 🚀 Quick Start: Deploy with All Security Measures

This guide provides the fastest path to deploy with all security measures active.

---

## Step 1: Set Environment Variable (2 minutes)

### For Production Environment File:
```bash
cd /root/crane
echo "ENVIRONMENT=production" >> config/prod.env
```

### Or for .env file:
```bash
cd /root/crane/backend
echo "ENVIRONMENT=production" >> .env
```

### Verify:
```bash
grep ENVIRONMENT config/prod.env  # or backend/.env
```

---

## Step 2: Run Security Tests (3 minutes)

```bash
cd /root/crane
chmod +x test_security.sh
./test_security.sh http://localhost:8003
```

**Expected:** All tests should pass ✅

---

## Step 3: Deploy Application (5 minutes)

### Option A: Docker Deployment
```bash
cd /root/crane
docker-compose down
docker-compose up -d --build
```

### Option B: Systemd Service
```bash
sudo systemctl restart crane-backend
sudo systemctl restart nginx
```

### Option C: Manual Start
```bash
cd /root/crane/backend
source venv/bin/activate  # if using virtualenv
uvicorn app.main:app --host 0.0.0.0 --port 8003
```

---

## Step 4: Verify Deployment (2 minutes)

### Check Application Health:
```bash
curl http://localhost:8003/api/v1/health
```

### Check Security Headers:
```bash
curl -I http://localhost:8003 | grep -i "x-frame\|strict-transport"
```

### Check API Docs are Disabled:
```bash
curl http://localhost:8003/docs
# Should return 404 in production
```

---

## Step 5: Start Security Monitoring (Ongoing)

```bash
cd /root/crane
chmod +x monitor_security.sh

# Monitor security events
./monitor_security.sh monitor

# Watch logs in real-time
./monitor_security.sh watch

# View statistics
./monitor_security.sh stats
```

---

## Quick Verification Checklist

Run these commands to verify everything is working:

```bash
# 1. Environment variable set
grep ENVIRONMENT config/prod.env || echo "⚠️ ENVIRONMENT not set"

# 2. Application running
curl -s http://localhost:8003/api/v1/health | grep -q "ok" && echo "✅ App running" || echo "❌ App not running"

# 3. API docs disabled
curl -s http://localhost:8003/docs | grep -q "404" && echo "✅ API docs disabled" || echo "⚠️ API docs accessible"

# 4. Security headers present
curl -sI http://localhost:8003 | grep -q "X-Frame-Options" && echo "✅ Security headers present" || echo "⚠️ Security headers missing"

# 5. Payment security working
curl -s -X POST http://localhost:8003/api/v1/fmv-reports/create-payment-intent \
  -H "Content-Type: application/json" \
  -d '{"report_type":"professional","amount":100,"crane_data":{}}' | grep -q "amount mismatch\|Payment amount" && echo "✅ Payment security active" || echo "⚠️ Payment security not working"
```

---

## Troubleshooting

### Issue: API docs still accessible
**Solution:** Restart the application after setting ENVIRONMENT=production

### Issue: Security tests failing
**Solution:** 
1. Check environment variable is set
2. Restart application
3. Check logs: `tail -f /var/log/app/app.log`

### Issue: Payment validation not working
**Solution:**
1. Verify `/api/v1/fmv-reports/calculate-price` endpoint is accessible
2. Check backend logs for errors
3. Verify payment_validator.py is in the correct location

---

## Production Checklist

Before going live, verify:

- [x] ENVIRONMENT=production is set
- [x] All security tests pass
- [x] API docs are disabled
- [x] Security headers are present
- [x] Payment validation is working
- [x] Monitoring is set up
- [x] Logs are being written
- [x] HTTPS is configured (if applicable)

---

## Next Steps

1. **Monitor Security Logs**: Use `monitor_security.sh` to watch for threats
2. **Review Logs Daily**: Check for any security events
3. **Run Tests Weekly**: Re-run `test_security.sh` to verify everything still works
4. **Update Regularly**: Keep dependencies and security measures updated

---

## Support

- **Security Documentation**: See `PRODUCTION_SECURITY_GUIDE.md`
- **Implementation Details**: See `SECURITY_IMPLEMENTATION_GUIDE.md`
- **Deployment Checklist**: See `DEPLOYMENT_SECURITY_CHECKLIST.md`

---

**Total Deployment Time**: ~15 minutes  
**Status**: ✅ Ready for Production

