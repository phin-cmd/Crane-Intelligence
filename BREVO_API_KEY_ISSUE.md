# Brevo API Key Issue

## Problem
The Brevo API is returning `401: Key not found` when trying to send emails.

## Current API Key
- Format: `xsmtpsib-<REDACTED>-<REDACTED>`
- Type: SMTP API Key (starts with `xsmtpsib-`)

## Issue
Brevo's Transactional Email API v3 requires a **Transactional API Key** (usually starts with `xkeysib-`), not an SMTP API key.

## Solutions

### Option 1: Get Transactional API Key (Recommended)
1. Log into Brevo Dashboard: https://app.brevo.com/
2. Go to **Settings** → **SMTP & API**
3. Under **API Keys**, create a new **Transactional API Key** (not SMTP)
4. The key should start with `xkeysib-`
5. Update `BREVO_API_KEY` in `docker-compose.yml` with the new key

### Option 2: Use SMTP Instead
If you want to use the SMTP key, we can configure the system to use SMTP instead of the API:
- Set `USE_BREVO_API=false` in docker-compose.yml
- The system will fall back to SMTP using the SMTP password

### Option 3: Verify Current Key
1. Check if the key is still valid in Brevo Dashboard
2. Ensure the sender email `pgenerelly@craneintelligence.tech` is verified
3. Check if the key has the correct permissions

## Current Configuration
- `BREVO_API_KEY`: Set in docker-compose.yml
- `BREVO_SMTP_PASSWORD`: CraneIntel123!
- `MAIL_FROM_EMAIL`: pgenerelly@craneintelligence.tech
- `USE_BREVO_API`: true

## Next Steps
1. Get a Transactional API Key from Brevo Dashboard
2. Update the API key in docker-compose.yml
3. Restart the backend container
4. Test email sending

