# Crane Intelligence - Deployment Guide

## 📋 Overview

This guide covers the complete deployment process for the Crane Intelligence platform, including frontend, backend services, and production configuration.

## 🏗️ Architecture

### Components

1. **Frontend** - Static HTML/CSS/JS files
   - Location: `/var/www/craneintelligence.tech/`
   - Served by: Nginx
   - Port: 80/443 (HTTPS)

2. **FMV API Server** - Node.js
   - Location: `/root/fmv-api/`
   - Port: 3000
   - Purpose: FMV report management, payments, email notifications

3. **Python Backend** - FastAPI
   - Location: `/home/ubuntu/`
   - Port: 8003
   - Purpose: Authentication, subscriptions, valuations

4. **Nginx** - Reverse Proxy
   - Configuration: `/etc/nginx/sites-available/craneintelligence-final.conf`
   - Purpose: SSL termination, static file serving, API proxying

## 🚀 Deployment Steps

### 1. Pull Latest Code from GitHub

```bash
# Navigate to project directory
cd /var/www/craneintelligence.tech

# Pull latest changes
git pull origin main

# Verify files
ls -la
```

### 2. Update FMV API Server

```bash
# Navigate to FMV API directory
cd /root/fmv-api

# Pull latest changes (if separate repo) or copy files
# Install/update dependencies
npm install

# Restart service
pkill -f "node server.js"
cd /root/fmv-api && nohup node server.js > server.log 2>&1 &

# Verify running
ps aux | grep "node server.js"
tail -f /root/fmv-api/server.log
```

### 3. Update Python Backend

```bash
# Navigate to backend directory
cd /home/ubuntu

# Activate virtual environment
source venv/bin/activate

# Update dependencies
pip install -r requirements.txt

# Restart service (using systemd or supervisor)
sudo systemctl restart crane-backend

# Verify running
ps aux | grep uvicorn
```

### 4. Reload Nginx

```bash
# Test configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx

# Check status
sudo systemctl status nginx
```

### 5. Verify Deployment

```bash
# Check all services
echo "=== FMV API ==="
ps aux | grep "node server.js" | grep -v grep

echo "=== Python Backend ==="
ps aux | grep uvicorn | grep -v grep

echo "=== Nginx ==="
systemctl status nginx | grep Active

# Test endpoints
curl https://craneintelligence.tech/homepage.html
curl https://craneintelligence.tech/api/v1/admin/fmv-reports
```

## 🔧 Service Management

### FMV API Server

**Start:**
```bash
cd /root/fmv-api && nohup node server.js > server.log 2>&1 &
```

**Stop:**
```bash
pkill -f "node server.js"
```

**View Logs:**
```bash
tail -f /root/fmv-api/server.log
```

**Check Status:**
```bash
ps aux | grep "node server.js" | grep -v grep
```

### Python Backend

**Start:**
```bash
cd /home/ubuntu && source venv/bin/activate && python run.py &
```

**Stop:**
```bash
pkill -f "uvicorn app.main:app"
```

**View Logs:**
```bash
# Logs location depends on your setup
journalctl -u crane-backend -f
```

**Check Status:**
```bash
ps aux | grep uvicorn | grep -v grep
```

### Nginx

**Start:**
```bash
sudo systemctl start nginx
```

**Stop:**
```bash
sudo systemctl stop nginx
```

**Restart:**
```bash
sudo systemctl restart nginx
```

**Reload (without downtime):**
```bash
sudo systemctl reload nginx
```

**Check Status:**
```bash
sudo systemctl status nginx
```

**Test Configuration:**
```bash
sudo nginx -t
```

## 🔐 Environment Variables

### FMV API (.env)

Location: `/root/fmv-api/.env`

```env
# Stripe
STRIPE_SECRET_KEY=sk_test_...

# Brevo (Email)
BREVO_API_KEY=xkeysib-...

# Server
PORT=3000
NODE_ENV=production
```

### Python Backend (.env)

Location: `/home/ubuntu/.env`

```env
# Database
DATABASE_URL=postgresql://...

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret

# API
API_PORT=8003
API_HOST=0.0.0.0

# Environment
ENVIRONMENT=production
```

## 📊 Database Management

### FMV Reports Database

Location: `/root/fmv-api/fmv-reports.json`

**Backup:**
```bash
cp /root/fmv-api/fmv-reports.json /root/fmv-api/fmv-reports.json.backup-$(date +%Y%m%d)
```

**View:**
```bash
cat /root/fmv-api/fmv-reports.json | python3 -m json.tool | less
```

### Users Database

Location: `/root/fmv-api/users.json`

**Backup:**
```bash
cp /root/fmv-api/users.json /root/fmv-api/users.json.backup-$(date +%Y%m%d)
```

## 🔍 Troubleshooting

### Frontend Issues

**Problem:** Pages not loading or 404 errors

**Solution:**
```bash
# Check nginx configuration
sudo nginx -t

# Check file permissions
ls -la /var/www/craneintelligence.tech/

# Fix permissions if needed
sudo chown -R www-data:www-data /var/www/craneintelligence.tech/
```

### FMV API Issues

**Problem:** API not responding on port 3000

**Solution:**
```bash
# Check if service is running
ps aux | grep "node server.js"

# Check logs
tail -50 /root/fmv-api/server.log

# Restart service
pkill -f "node server.js"
cd /root/fmv-api && nohup node server.js > server.log 2>&1 &
```

**Problem:** Payment processing fails

**Solution:**
```bash
# Verify Stripe API key
grep STRIPE_SECRET_KEY /root/fmv-api/.env

# Check Stripe API status
curl https://status.stripe.com/
```

### Python Backend Issues

**Problem:** Backend not responding on port 8003

**Solution:**
```bash
# Check if service is running
ps aux | grep uvicorn

# Check logs
journalctl -u crane-backend -n 50

# Restart service
sudo systemctl restart crane-backend
```

### Email Notification Issues

**Problem:** Emails not being sent

**Solution:**
```bash
# Verify Brevo API key
grep BREVO_API_KEY /root/fmv-api/.env

# Check FMV API logs for email errors
grep -i "email\|brevo" /root/fmv-api/server.log | tail -20

# Test email function
# (Add test endpoint in server.js if needed)
```

### Database Issues

**Problem:** Data not persisting

**Solution:**
```bash
# Check file permissions
ls -la /root/fmv-api/*.json

# Fix permissions
chmod 644 /root/fmv-api/*.json

# Verify JSON syntax
python3 -m json.tool /root/fmv-api/fmv-reports.json
```

## 🔄 Rollback Procedure

If deployment fails, rollback to previous version:

```bash
# 1. Navigate to project directory
cd /var/www/craneintelligence.tech

# 2. View commit history
git log --oneline -10

# 3. Rollback to previous commit
git reset --hard HEAD~1

# 4. Force push (if needed)
git push origin main --force

# 5. Restart services
pkill -f "node server.js"
cd /root/fmv-api && nohup node server.js > server.log 2>&1 &
sudo systemctl restart crane-backend
sudo systemctl reload nginx
```

## 📦 Backup Strategy

### Automated Backups

Create a backup script:

```bash
#!/bin/bash
# /root/scripts/backup-crane-intelligence.sh

BACKUP_DIR="/root/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup frontend
tar -czf $BACKUP_DIR/frontend_$DATE.tar.gz /var/www/craneintelligence.tech/

# Backup FMV API
tar -czf $BACKUP_DIR/fmv-api_$DATE.tar.gz /root/fmv-api/

# Backup Python backend
tar -czf $BACKUP_DIR/backend_$DATE.tar.gz /home/ubuntu/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

**Schedule with cron:**
```bash
# Run daily at 2 AM
0 2 * * * /root/scripts/backup-crane-intelligence.sh
```

## 🔒 Security Checklist

- [ ] HTTPS enabled and enforced
- [ ] Environment variables secured (not in Git)
- [ ] File permissions set correctly
- [ ] Firewall configured (ports 80, 443, 22 only)
- [ ] SSH key authentication enabled
- [ ] Regular security updates applied
- [ ] Database files not publicly accessible
- [ ] API keys rotated regularly
- [ ] Nginx security headers configured
- [ ] Rate limiting enabled

## 📈 Monitoring

### Health Checks

```bash
# Check all services
curl https://craneintelligence.tech/homepage.html
curl https://craneintelligence.tech/api/v1/admin/fmv-reports

# Check disk space
df -h

# Check memory usage
free -h

# Check CPU usage
top -bn1 | head -20
```

### Log Monitoring

```bash
# Nginx access log
tail -f /var/log/nginx/access.log

# Nginx error log
tail -f /var/log/nginx/error.log

# FMV API log
tail -f /root/fmv-api/server.log

# System log
journalctl -f
```

## 🆘 Emergency Contacts

- **Technical Lead:** phin@accranes.com
- **GitHub:** https://github.com/phin-cmd/Crane-Intelligence
- **Production URL:** https://craneintelligence.tech

## 📝 Deployment Checklist

Before deploying:
- [ ] Code reviewed and tested locally
- [ ] All tests passing
- [ ] Environment variables updated
- [ ] Database backups created
- [ ] Deployment window scheduled
- [ ] Team notified

During deployment:
- [ ] Pull latest code
- [ ] Update dependencies
- [ ] Restart services
- [ ] Verify all endpoints
- [ ] Check logs for errors
- [ ] Test critical functionality

After deployment:
- [ ] Monitor logs for 30 minutes
- [ ] Test all major features
- [ ] Verify email notifications
- [ ] Check payment processing
- [ ] Update documentation
- [ ] Notify team of completion

## 🎯 Quick Reference

**Repository:** https://github.com/phin-cmd/Crane-Intelligence

**Production URL:** https://craneintelligence.tech

**Key Directories:**
- Frontend: `/var/www/craneintelligence.tech/`
- FMV API: `/root/fmv-api/`
- Backend: `/home/ubuntu/`
- Nginx Config: `/etc/nginx/sites-available/craneintelligence-final.conf`

**Key Commands:**
```bash
# Deploy frontend
cd /var/www/craneintelligence.tech && git pull origin main

# Restart FMV API
pkill -f "node server.js" && cd /root/fmv-api && nohup node server.js > server.log 2>&1 &

# Restart backend
sudo systemctl restart crane-backend

# Reload nginx
sudo nginx -t && sudo systemctl reload nginx

# Check all services
ps aux | grep -E "node server.js|uvicorn" | grep -v grep && systemctl status nginx | grep Active
```

---

**Last Updated:** November 13, 2025
**Version:** 1.0.0
