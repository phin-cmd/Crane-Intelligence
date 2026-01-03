# Production Deployment Security Checklist

## Pre-Deployment Security Verification

Use this checklist before deploying to production to ensure all security measures are active.

---

## 1. Environment Configuration ✅

- [ ] `.env` file created with `ENVIRONMENT=production`
- [ ] `SECRET_KEY` set to a strong, random value (minimum 32 characters)
- [ ] Database credentials are secure and not default values
- [ ] Stripe keys are production keys (not test keys)
- [ ] All API keys and secrets are set

**Command to verify:**
```bash
grep -E "ENVIRONMENT|SECRET_KEY" backend/.env
```

---

## 2. Payment Security ✅

- [ ] Payment amount validation is active
- [ ] Server-side price calculation endpoint is accessible
- [ ] Frontend uses server-calculated prices
- [ ] Payment manipulation attempts are logged

**Test:**
```bash
./test_security.sh http://your-production-url
```

---

## 3. SQL Injection Prevention ✅

- [ ] SQL injection prevention middleware is active
- [ ] All raw SQL queries replaced with ORM
- [ ] Database user has minimal permissions
- [ ] Query timeouts are configured

**Verify:**
```bash
# Check for any remaining raw SQL queries
grep -r "db.execute(text" backend/app/api/
```

---

## 4. API Documentation ✅

- [ ] API docs are disabled in production
- [ ] OpenAPI schema is not accessible
- [ ] `/docs` endpoint returns 404

**Test:**
```bash
curl -I https://your-domain.com/docs
# Should return 404
```

---

## 5. Error Handling ✅

- [ ] Global exception handler is active
- [ ] Error messages don't leak internal information
- [ ] Errors are logged securely

**Verify:**
```bash
# Check main.py has global exception handler
grep -A 5 "global_exception_handler" backend/app/main.py
```

---

## 6. Bot Detection ✅

- [ ] Bot detection middleware is active
- [ ] Bot user agents are blocked
- [ ] Bot detection events are logged

**Test:**
```bash
curl -H "User-Agent: python-requests/2.28.0" https://your-domain.com/api/v1/health
# Should return 403
```

---

## 7. Rate Limiting ✅

- [ ] Nginx rate limiting is configured
- [ ] Rate limits are appropriate (10 req/s)
- [ ] Burst protection is active (20 requests)

**Verify:**
```bash
# Check nginx.conf
grep -A 2 "limit_req" nginx.conf
```

---

## 8. Security Headers ✅

- [ ] Strict-Transport-Security header is set
- [ ] X-Frame-Options: DENY
- [ ] Content-Security-Policy is configured
- [ ] X-Content-Type-Options: nosniff

**Test:**
```bash
curl -I https://your-domain.com | grep -i "x-frame\|strict-transport\|content-security"
```

---

## 9. Database Security ✅

- [ ] Database connection uses SSL/TLS
- [ ] Database user has minimal permissions
- [ ] Connection pooling is configured
- [ ] Query timeouts are set

**Verify:**
```bash
# Check database.py
grep -A 5 "connect_args" backend/app/core/database.py
```

---

## 10. Security Logging ✅

- [ ] Security audit logger is active
- [ ] Logs are being written
- [ ] Log rotation is configured
- [ ] Alerts are set up for critical events

**Verify:**
```bash
# Check if security events are logged
tail -f /var/log/app/security.log
```

---

## 11. HTTPS/TLS ✅

- [ ] SSL certificate is valid
- [ ] HTTPS is enforced (HTTP redirects to HTTPS)
- [ ] TLS 1.2+ is required
- [ ] Certificate auto-renewal is configured

**Test:**
```bash
curl -I http://your-domain.com
# Should redirect to https://
```

---

## 12. Firewall Configuration ✅

- [ ] Firewall rules are configured
- [ ] Only necessary ports are open (80, 443, 22)
- [ ] Database port is not publicly accessible
- [ ] Rate limiting is active

**Verify:**
```bash
sudo ufw status
```

---

## Deployment Steps

### Step 1: Backup Current Production
```bash
# Backup database
pg_dump -h localhost -U crane_user crane_intelligence > backup_$(date +%Y%m%d).sql

# Backup application files
tar -czf app_backup_$(date +%Y%m%d).tar.gz /path/to/app
```

### Step 2: Update Environment Variables
```bash
# Copy .env.example to .env and update values
cp backend/.env.example backend/.env
nano backend/.env  # Edit with production values
```

### Step 3: Run Security Tests
```bash
# Run security test suite
chmod +x test_security.sh
./test_security.sh https://your-production-url
```

### Step 4: Deploy Application
```bash
# Pull latest code
git pull origin main

# Install dependencies
cd backend
pip install -r requirements.txt

# Run migrations (if any)
alembic upgrade head

# Restart application
sudo systemctl restart crane-backend
```

### Step 5: Update Nginx Configuration
```bash
# Copy nginx config
sudo cp nginx.conf /etc/nginx/sites-available/crane
sudo nginx -t  # Test configuration
sudo systemctl reload nginx
```

### Step 6: Verify Deployment
```bash
# Check application is running
curl https://your-domain.com/api/v1/health

# Check security headers
curl -I https://your-domain.com

# Run security tests
./test_security.sh https://your-domain.com
```

### Step 7: Monitor Security Logs
```bash
# Watch security logs
tail -f /var/log/app/security.log

# Check for any security events
grep -i "security\|injection\|manipulation" /var/log/app/app.log
```

---

## Post-Deployment Monitoring

### Immediate (First 24 hours)
- [ ] Monitor application logs for errors
- [ ] Check security logs for any attempts
- [ ] Verify all endpoints are accessible
- [ ] Verify payment processing works
- [ ] Check rate limiting is working

### Ongoing (Weekly)
- [ ] Review security logs
- [ ] Check for failed login attempts
- [ ] Monitor payment manipulation attempts
- [ ] Review bot detection events
- [ ] Check database performance

### Monthly
- [ ] Security audit
- [ ] Review and update security measures
- [ ] Check for security updates
- [ ] Review access logs
- [ ] Update dependencies

---

## Emergency Response

If a security incident is detected:

1. **Immediate Actions:**
   - Block the IP address if needed
   - Review security logs
   - Check for data breaches
   - Notify security team

2. **Investigation:**
   - Review all security events
   - Check database for unauthorized access
   - Review payment logs
   - Check user accounts

3. **Remediation:**
   - Patch vulnerabilities
   - Update security measures
   - Reset compromised credentials
   - Notify affected users (if required)

---

## Security Contact

For security concerns:
- Review security logs
- Check `SECURITY_IMPLEMENTATION_SUMMARY.md`
- Contact security team

---

**Last Updated:** December 2024  
**Status:** Ready for Production Deployment

