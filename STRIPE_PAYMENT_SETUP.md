# Stripe Payment Environment Separation - Complete Setup Guide

## Overview

This guide explains how to configure Stripe payment processing with proper environment separation:
- **Production**: Live mode with real payment processing (`pk_live_...` and `sk_live_...`)
- **Dev/UAT**: Test mode with dummy cards (`pk_test_...` and `sk_test_...`)

## Table of Contents

1. [Getting Stripe API Keys](#getting-stripe-api-keys)
2. [Environment Configuration](#environment-configuration)
3. [Webhook Setup](#webhook-setup)
4. [Validation and Testing](#validation-and-testing)
5. [Security Best Practices](#security-best-practices)
6. [Troubleshooting](#troubleshooting)

---

## Getting Stripe API Keys

### For Production (Live Keys)

1. **Log into Stripe Dashboard**: https://dashboard.stripe.com/
2. **Toggle to Live Mode**: Click the toggle in the top right (should show "Live mode")
3. **Navigate to API Keys**: Go to Developers → API keys
4. **Get Your Keys**:
   - **Publishable key**: Starts with `pk_live_...` (safe to expose in frontend)
   - **Secret key**: Starts with `sk_live_...` (keep secret, never expose)
5. **Copy both keys** - you'll need them for production configuration

### For Dev/UAT (Test Keys)

1. **Log into Stripe Dashboard**: https://dashboard.stripe.com/
2. **Toggle to Test Mode**: Click the toggle in the top right (should show "Test mode")
3. **Navigate to API Keys**: Go to Developers → API keys
4. **Get Your Keys**:
   - **Publishable key**: Starts with `pk_test_...`
   - **Secret key**: Starts with `sk_test_...`
5. **Note**: Test keys are already configured in `config/dev.env` and `config/uat.env`

---

## Environment Configuration

### Dev Environment (`config/dev.env`)

**Status**: ✅ Already configured with test keys

```bash
ENVIRONMENT=dev
STRIPE_PUBLISHABLE_KEY=pk_test_...  # Test key
STRIPE_SECRET_KEY=sk_test_...        # Test key
STRIPE_WEBHOOK_SECRET=whsec_...     # Get from Stripe dashboard (test mode)
```

**Action Required**: Update `STRIPE_WEBHOOK_SECRET` with actual webhook secret from Stripe dashboard (see Webhook Setup section)

### UAT Environment (`config/uat.env`)

**Status**: ✅ Already configured with test keys

```bash
ENVIRONMENT=uat
STRIPE_PUBLISHABLE_KEY=pk_test_...  # Test key
STRIPE_SECRET_KEY=sk_test_...        # Test key
STRIPE_WEBHOOK_SECRET=whsec_...     # Get from Stripe dashboard (test mode)
```

**Action Required**: Update `STRIPE_WEBHOOK_SECRET` with actual webhook secret from Stripe dashboard (see Webhook Setup section)

### Production Environment (`config/prod.env`)

**Status**: ⚠️ Needs live keys configuration

1. **Create production environment file** (if not exists):
   ```bash
   cp config/prod.env.template config/prod.env
   ```

2. **Edit `config/prod.env`** and update:
   ```bash
   ENVIRONMENT=prod
   STRIPE_PUBLISHABLE_KEY=pk_live_...  # Live key from Stripe dashboard
   STRIPE_SECRET_KEY=sk_live_...        # Live key from Stripe dashboard
   STRIPE_WEBHOOK_SECRET=whsec_...     # Get from Stripe dashboard (live mode)
   ```

3. **Important**: 
   - Never commit `config/prod.env` to version control
   - Keep live keys secure
   - Only use live keys in production environment

---

## Webhook Setup

Webhooks allow Stripe to notify your application about payment events. Each environment needs a separate webhook endpoint.

### Webhook Endpoints

- **Dev**: `https://dev.craneintelligence.tech/api/v1/payment-webhooks/stripe`
- **UAT**: `https://uat.craneintelligence.tech/api/v1/payment-webhooks/stripe`
- **Production**: `https://craneintelligence.tech/api/v1/payment-webhooks/stripe`

### Setup Instructions

#### For Dev/UAT (Test Mode)

1. Go to Stripe Dashboard: https://dashboard.stripe.com/webhooks
2. **Toggle to Test Mode** (top right)
3. Click **"Add endpoint"**
4. Enter webhook URL:
   - Dev: `https://dev.craneintelligence.tech/api/v1/payment-webhooks/stripe`
   - UAT: `https://uat.craneintelligence.tech/api/v1/payment-webhooks/stripe`
5. Select events to listen to:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `payment_intent.canceled`
6. Click **"Add endpoint"**
7. **Copy the Signing secret** (starts with `whsec_`)
8. Update environment file:
   ```bash
   # In config/dev.env or config/uat.env
   STRIPE_WEBHOOK_SECRET=whsec_...  # Paste the signing secret here
   ```

#### For Production (Live Mode)

1. Go to Stripe Dashboard: https://dashboard.stripe.com/webhooks
2. **Toggle to Live Mode** (top right)
3. Click **"Add endpoint"**
4. Enter webhook URL: `https://craneintelligence.tech/api/v1/payment-webhooks/stripe`
5. Select events to listen to:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `payment_intent.canceled`
6. Click **"Add endpoint"**
7. **Copy the Signing secret** (starts with `whsec_`)
8. Update `config/prod.env`:
   ```bash
   STRIPE_WEBHOOK_SECRET=whsec_...  # Paste the signing secret here
   ```

### Automated Setup Guide

Run the setup guide script for step-by-step instructions:
```bash
./scripts/setup-stripe-webhooks.sh
```

---

## Validation and Testing

### Validate Configuration

Before deploying, always validate your Stripe configuration:

```bash
# Validate all environments
./scripts/validate-stripe-config.sh

# Or use Python validator
python3 scripts/stripe-key-validator.py
```

**What it checks:**
- ✅ Keys are configured
- ✅ Key types match (test keys for dev/uat, live keys for prod)
- ✅ No key type mismatches (test + live keys together)
- ✅ Webhook secrets are configured
- ✅ Environment-key matching is correct

### Testing Payments

#### Dev/UAT Environments (Test Mode)

Use Stripe test cards:
- **Success**: `4242 4242 4242 4242`
- **Decline**: `4000 0000 0000 0002`
- **3D Secure**: `4000 0025 0000 3155`
- **Any future expiry date** (e.g., 12/34)
- **Any 3-digit CVC**

**Test cards never charge real money** - they're for testing only.

#### Production Environment (Live Mode)

**⚠️ WARNING**: Production uses real cards and will charge real money!

- Only use real credit/debit cards
- Test with small amounts first
- Monitor Stripe dashboard for transactions
- Check backend logs for payment processing

### Verify Webhook Delivery

1. Go to Stripe Dashboard → Webhooks
2. Click on your webhook endpoint
3. Click **"Send test webhook"**
4. Select event: `payment_intent.succeeded`
5. Click **"Send test webhook"**
6. Check backend logs to verify webhook was received:
   ```bash
   docker logs crane-backend-1 | grep -i webhook
   ```

---

## Security Best Practices

### Key Management

1. **Never commit live keys to version control**
   - Use `.gitignore` to exclude `config/prod.env`
   - Use environment variables in production
   - Keep keys in secure storage (password manager, secrets manager)

2. **Separate keys per environment**
   - Dev/UAT: Test keys only
   - Production: Live keys only
   - Never mix test and live keys

3. **Rotate keys regularly**
   - Rotate keys if compromised
   - Update all environments when rotating
   - Test after key rotation

4. **Monitor key usage**
   - Check Stripe dashboard for unusual activity
   - Review logs for key validation warnings
   - Set up alerts for key mismatches

### Webhook Security

1. **Always verify webhook signatures**
   - Webhook secret is required
   - Signature verification prevents spoofing
   - Never skip signature verification

2. **Use HTTPS for webhook endpoints**
   - All webhook URLs use HTTPS
   - Never use HTTP for webhooks

3. **Keep webhook secrets secure**
   - Different secrets for test vs live mode
   - Never share secrets between environments
   - Rotate secrets if compromised

---

## Troubleshooting

### Common Issues

#### Issue: "Stripe secret key not configured"

**Solution**:
1. Check environment file has `STRIPE_SECRET_KEY` set
2. Verify backend container has environment variables loaded
3. Restart backend: `docker restart crane-backend-1`

#### Issue: "Production using test keys" warning

**Solution**:
1. Verify `ENVIRONMENT=prod` in production config
2. Check keys start with `pk_live_` and `sk_live_`
3. Update `config/prod.env` with live keys from Stripe dashboard

#### Issue: "Dev/UAT using live keys" warning

**Solution**:
1. Verify environment is set correctly (`ENVIRONMENT=dev` or `ENVIRONMENT=uat`)
2. Check keys start with `pk_test_` and `sk_test_`
3. Update environment file with test keys

#### Issue: Webhook signature verification fails

**Solution**:
1. Verify `STRIPE_WEBHOOK_SECRET` is configured
2. Check webhook secret matches Stripe dashboard
3. Ensure webhook secret is for correct mode (test vs live)
4. Verify webhook endpoint URL matches Stripe dashboard

#### Issue: Payment processing fails

**Solution**:
1. Check Stripe dashboard for error details
2. Verify API keys are correct and active
3. Check backend logs for Stripe errors
4. Ensure correct mode (test vs live) for environment
5. Verify card details are correct

### Validation Scripts

Run validation scripts to diagnose issues:

```bash
# Validate configuration
./scripts/validate-stripe-config.sh

# Check key types
python3 scripts/stripe-key-validator.py

# View backend logs
docker logs crane-backend-1 | grep -i stripe
```

### Getting Help

1. **Check Stripe Dashboard**: https://dashboard.stripe.com/
   - View API logs
   - Check webhook delivery
   - Review payment events

2. **Check Backend Logs**:
   ```bash
   docker logs crane-backend-1 --tail 100 | grep -i stripe
   ```

3. **Stripe Documentation**: https://stripe.com/docs
4. **Stripe Support**: https://support.stripe.com/

---

## Quick Reference

### Key Prefixes

- **Test Publishable**: `pk_test_...`
- **Test Secret**: `sk_test_...`
- **Live Publishable**: `pk_live_...`
- **Live Secret**: `sk_live_...`
- **Webhook Secret**: `whsec_...`

### Environment Requirements

| Environment | Key Type | Mode | Webhook Mode |
|------------|----------|------|--------------|
| Dev | Test | Test | Test |
| UAT | Test | Test | Test |
| Prod | Live | Live | Live |

### Configuration Files

- `config/dev.env` - Dev environment (test keys)
- `config/uat.env` - UAT environment (test keys)
- `config/prod.env` - Production environment (live keys) - **DO NOT COMMIT**
- `config/prod.env.template` - Production template (placeholders)

### Validation Commands

```bash
# Validate all environments
./scripts/validate-stripe-config.sh

# Python validator
python3 scripts/stripe-key-validator.py

# Webhook setup guide
./scripts/setup-stripe-webhooks.sh

# Setup daily validation cron
./scripts/setup-stripe-validation-cron.sh
```

---

## Deployment Checklist

Before deploying to production:

- [ ] Live Stripe keys obtained from Stripe dashboard
- [ ] `config/prod.env` created with live keys
- [ ] Webhook endpoint configured in Stripe (live mode)
- [ ] Webhook secret added to `config/prod.env`
- [ ] Configuration validated: `./scripts/validate-stripe-config.sh`
- [ ] Backend services restarted with new config
- [ ] Webhook delivery tested
- [ ] Test payment processed successfully (small amount)
- [ ] Monitoring and alerts configured
- [ ] Team notified of live payment processing

---

## Monitoring

### Daily Validation

A cron job runs daily at 2 AM to validate Stripe configuration:
- Logs to: `/var/log/crane/stripe-validation.log`
- Alerts on key mismatches
- Verifies environment-key matching

### Backend Logs

The Stripe service logs key type detection on startup:
- Check logs for validation warnings
- Monitor for key type mismatches
- Review payment processing errors

### Stripe Dashboard

Monitor in Stripe dashboard:
- Payment events
- Webhook delivery status
- API usage and errors
- Customer activity

---

*Last updated: December 30, 2025*

