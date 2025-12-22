# Email Configuration Fix Summary

## Issues Fixed

1. **Missing `settings` import**: Fixed `NameError: name 'settings' is not defined` in `fmv_report_service.py`
2. **Brevo API Key Issue**: The API key was returning 401 "Key not found" - switched to SMTP instead
3. **Duplicate Environment Variable**: Removed duplicate `USE_BREVO_API=true` that was overriding `USE_BREVO_API=false`
4. **SMTP Configuration**: Updated to use correct SMTP credentials

## Current SMTP Configuration

- **SMTP Server**: `smtp-relay.brevo.com`
- **Port**: `587`
- **Username**: `99e09b001@smtp-brevo.com`
- **Password**: `CraneIntel123!` (from BREVO_SMTP_PASSWORD)
- **From Email**: `pgenerelly@craneintelligence.tech`
- **From Name**: `Crane Intelligence Platform`
- **Use TLS**: `True`
- **Use SSL**: `False`
- **USE_BREVO_API**: `false` (using SMTP, not API)

## Files Modified

1. `/root/crane/backend/app/services/fmv_report_service.py`
   - Added: `from ..core.config import settings`

2. `/root/crane/backend/app/core/config.py`
   - Updated `mail_server` to read from `MAIL_SERVER` env var
   - Updated `mail_port` to read from `MAIL_PORT` env var
   - Updated `mail_username` to read from `MAIL_USERNAME` env var
   - Updated `use_brevo_api` to read from `USE_BREVO_API` env var

3. `/root/crane/docker-compose.yml`
   - Added `MAIL_USERNAME=99e09b001@smtp-brevo.com`
   - Added `MAIL_SERVER=smtp-relay.brevo.com`
   - Added `MAIL_PORT=587`
   - Set `USE_BREVO_API=false`
   - Removed duplicate `USE_BREVO_API=true`

## Testing

The system is now configured to use SMTP for sending emails. When a draft report is created, it should:
1. Send a draft reminder email via SMTP
2. Create an in-app notification
3. Log email sending status

## Next Steps

1. Test by creating a new draft report
2. Check backend logs for email sending status
3. Verify emails are received in the recipient's inbox
4. If emails still fail, check SMTP connection logs for authentication errors

## Troubleshooting

If emails are not being sent:
- Check backend logs: `docker compose logs backend | grep -i email`
- Verify SMTP credentials are correct in Brevo dashboard
- Ensure sender email `pgenerelly@craneintelligence.tech` is verified in Brevo
- Check firewall/network allows outbound SMTP connections on port 587

