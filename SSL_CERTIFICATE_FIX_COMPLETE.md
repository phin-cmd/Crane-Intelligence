# SSL Certificate Issue - RESOLVED ✅

## Problem
The production website `https://www.craneintelligence.tech` was showing as "NOT SECURE" with error:
- `NET::ERR_CERT_AUTHORITY_INVALID`
- Self-signed certificate detected
- Browser security warnings

## Root Cause
1. **Certificate didn't include www subdomain**: The Let's Encrypt certificate only covered `craneintelligence.tech`, not `www.craneintelligence.tech`
2. **Nginx configuration issue**: The default server block was using self-signed certificates from `/etc/nginx/ssl/` instead of Let's Encrypt certificates
3. **Configuration mismatch**: The sites-enabled file had outdated configuration pointing to self-signed certificates

## Solution Applied

### 1. Updated Certificate to Include www Subdomain
```bash
certbot certonly --nginx -d craneintelligence.tech -d www.craneintelligence.tech --expand
```
- ✅ Certificate now includes both `craneintelligence.tech` and `www.craneintelligence.tech`
- ✅ Valid until: March 30, 2026 (89 days)

### 2. Fixed Nginx Configuration
- ✅ Updated `/etc/nginx/sites-available/craneinteligence.tech` to use Let's Encrypt certificate
- ✅ Updated `/etc/nginx/sites-enabled/craneinteligence.tech` to match
- ✅ Removed references to self-signed certificates
- ✅ Configured proper server_name directives for both domains

### 3. Verified Certificate
- ✅ Certificate issuer: Let's Encrypt (trusted CA)
- ✅ Certificate includes: `craneintelligence.tech` and `www.craneintelligence.tech`
- ✅ Verification code: 0 (ok) - Certificate is valid and trusted
- ✅ Website accessible via HTTPS

## Current Status

### Certificate Details
- **Domain**: `craneintelligence.tech` and `www.craneintelligence.tech`
- **Issuer**: Let's Encrypt (E7)
- **Type**: ECDSA
- **Valid Until**: March 30, 2026
- **Status**: ✅ Valid and trusted

### Website Access
- ✅ `https://www.craneintelligence.tech` - Working with valid SSL
- ✅ `https://craneintelligence.tech` - Working with valid SSL
- ✅ HTTP to HTTPS redirect working
- ✅ No security warnings in browsers

## Prevention Measures Implemented

### 1. Automatic Certificate Renewal
- ✅ Certbot timer configured (runs twice daily)
- ✅ Pre-renewal hook: Tests nginx config before renewal
- ✅ Post-renewal hook: Reloads nginx after renewal
- ✅ Certificates auto-renew 30 days before expiration

### 2. SSL Certificate Monitoring
- ✅ Daily monitoring script: `scripts/ssl-certificate-monitor.sh`
- ✅ Checks all domains (production, dev, UAT)
- ✅ Alerts if self-signed certificates detected
- ✅ Warns if certificates expire within 60 days
- ✅ Cron job runs daily at 2 AM

### 3. Monitoring Script Features
- Checks certificate validity
- Verifies certificate issuer (detects self-signed)
- Checks expiration dates
- Verifies certificate chain
- Provides alerts for issues

## Verification Commands

### Check Certificate Status
```bash
# Manual check
./scripts/ssl-certificate-monitor.sh

# Check specific domain
openssl s_client -connect www.craneintelligence.tech:443 -servername www.craneintelligence.tech < /dev/null | grep -E "subject=|issuer=|Verify return code"

# List all certificates
certbot certificates
```

### Test Website Access
```bash
# Test HTTPS access
curl -I https://www.craneintelligence.tech/homepage.html

# Test certificate validity
curl -vI https://www.craneintelligence.tech 2>&1 | grep -E "SSL|certificate"
```

## Maintenance

### Manual Certificate Renewal
If needed, manually renew certificates:
```bash
certbot renew
systemctl reload nginx
```

### Check Renewal Status
```bash
systemctl list-timers | grep certbot
certbot certificates
```

### Monitor Certificate Health
```bash
# Run monitoring script
./scripts/ssl-certificate-monitor.sh

# Check logs
tail -f /var/log/ssl-monitor.log
```

## Troubleshooting

### If Certificate Issues Occur Again

1. **Check certificate status**:
   ```bash
   certbot certificates
   ./scripts/ssl-certificate-monitor.sh
   ```

2. **Verify nginx configuration**:
   ```bash
   nginx -t
   grep -r "ssl_certificate" /etc/nginx/sites-enabled/
   ```

3. **Check for self-signed certificates**:
   ```bash
   # Should NOT find self-signed certs
   grep -r "Crane Intelligence" /etc/nginx/sites-enabled/
   ```

4. **Renew certificate if needed**:
   ```bash
   certbot renew --force-renewal
   systemctl restart nginx
   ```

5. **Verify fix**:
   ```bash
   openssl s_client -connect www.craneintelligence.tech:443 -servername www.craneintelligence.tech < /dev/null | grep "Verify return code"
   # Should show: Verify return code: 0 (ok)
   ```

## Files Modified

1. `/etc/nginx/sites-available/craneinteligence.tech` - Updated to use Let's Encrypt certificate
2. `/etc/nginx/sites-enabled/craneinteligence.tech` - Updated to match
3. `/etc/letsencrypt/live/craneintelligence.tech/` - Certificate updated to include www

## Scripts Created

1. `scripts/ssl-certificate-monitor.sh` - Daily monitoring script
2. `scripts/setup-ssl-auto-renewal.sh` - Auto-renewal setup script

## Status: ✅ RESOLVED

The SSL certificate issue has been completely resolved:
- ✅ Valid Let's Encrypt certificate installed
- ✅ Certificate includes www subdomain
- ✅ Website accessible without security warnings
- ✅ Automatic renewal configured
- ✅ Monitoring in place to prevent future issues

**The website is now secure and trusted by all browsers.**

---

*Issue resolved: December 30, 2025*
*Certificate valid until: March 30, 2026*

