# Email SMTP Configuration - Final Status

## Issue
Emails were not being sent because:
1. `FMVEmailService` was using `BrevoEmailService()` directly, which always tries the API
2. The Brevo API key was invalid (401 error)
3. SMTP was not being used as fallback

## Fixes Applied

1. **Updated `FMVEmailService`** to use `UnifiedEmailService` instead of `BrevoEmailService`
   - File: `/root/crane/backend/app/services/fmv_email_service.py`
   - Now respects `USE_BREVO_API` setting

2. **Added `send_template_email` method** to `UnifiedEmailService`
   - File: `/root/crane/backend/app/services/email_service_unified.py`
   - Provides compatibility with `FMVEmailService` expectations

3. **SMTP Configuration**
   - Server: `smtp-relay.brevo.com`
   - Port: `587`
   - Username: `99e09b001@smtp-brevo.com`
   - Password: `CraneIntel123!`
   - From: `pgenerelly@craneintelligence.tech`
   - `USE_BREVO_API=false`

## Current Status

- ✅ `UnifiedEmailService` is configured with `use_brevo_api: False`
- ✅ Backend has been rebuilt with the fixes
- ⚠️ SMTP connection test timed out (may be network/firewall issue)

## Next Steps

1. **Test email sending** by creating a new draft report
2. **Check backend logs** for SMTP connection attempts:
   ```bash
   docker compose logs backend | grep -i "smtp\|email sent"
   ```
3. **If SMTP connection fails**, check:
   - Firewall rules allowing outbound port 587
   - Network connectivity from container to `smtp-relay.brevo.com:587`
   - SMTP credentials are correct in Brevo dashboard

## Troubleshooting

If emails still don't send:
1. Check if SMTP port 587 is accessible from the server
2. Verify SMTP credentials in Brevo dashboard
3. Check backend logs for specific SMTP errors
4. Test SMTP connection manually from the container

