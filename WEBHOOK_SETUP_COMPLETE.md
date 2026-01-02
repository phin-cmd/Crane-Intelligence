# Webhook Setup & Payment Flow Testing - Complete Guide

## ✅ What's Been Completed

### 1. Stripe Keys Configuration
- ✅ DEV environment: Sandbox keys configured
- ✅ UAT environment: Sandbox keys configured  
- ✅ PROD environment: Live keys configured
- ✅ All backends restarted and using correct keys
- ✅ Payment intent creation tested and working

### 2. Scripts Created
- ✅ `scripts/configure-webhook-secrets.sh` - Easy webhook secret configuration
- ✅ `scripts/test-complete-payment-flow.sh` - Complete payment flow testing
- ✅ `scripts/test-webhook-delivery.sh` - Webhook delivery testing
- ✅ `scripts/test-payment-flow.sh` - Basic payment flow testing

### 3. Documentation Created
- ✅ `WEBHOOK_SETUP_GUIDE.md` - Detailed webhook setup instructions
- ✅ `PAYMENT_FLOW_TESTING_GUIDE.md` - Comprehensive testing guide
- ✅ `QUICK_START_WEBHOOK_SETUP.md` - Quick start guide
- ✅ `STRIPE_PAYMENT_COMPLETE_SETUP.md` - Complete setup summary

### 4. Testing Status
- ✅ Payment intent creation: **WORKING** in all environments
- ✅ Stripe service initialization: **WORKING** in all environments
- ✅ Config endpoints: **WORKING** in all environments
- ⚠️ Webhook secrets: **NEED TO BE CONFIGURED** (see below)

## 🔧 What Needs to Be Done

### Step 1: Get Webhook Secrets from Stripe Dashboard

You need to access the Stripe dashboard and get webhook secrets for each environment.

#### For DEV Environment (Test Mode)

1. Go to: https://dashboard.stripe.com/webhooks
2. **Toggle to "Test mode"** (top right)
3. Click **"Add endpoint"**
4. Enter URL: `https://dev.craneintelligence.tech/api/v1/payment-webhooks/stripe`
5. Select events: `payment_intent.succeeded`, `payment_intent.payment_failed`, `payment_intent.canceled`
6. Click **"Reveal"** next to "Signing secret"
7. Copy the secret (starts with `whsec_`)

#### For UAT Environment (Test Mode)

1. Still in **Test mode**
2. Create another endpoint: `https://uat.craneintelligence.tech/api/v1/payment-webhooks/stripe`
3. Same events as DEV
4. Copy the signing secret (different from DEV!)

#### For PRODUCTION Environment (Live Mode)

1. **Toggle to "Live mode"** (top right)
2. Create endpoint: `https://craneintelligence.tech/api/v1/payment-webhooks/stripe`
3. Same events
4. Copy the signing secret (different from test mode!)

### Step 2: Configure Webhook Secrets

Once you have the secrets, use the interactive script:

```bash
cd /root/crane
./scripts/configure-webhook-secrets.sh --interactive
```

The script will prompt you for each environment's secret.

Or update manually:

```bash
# Edit DEV
nano config/dev.env
# Change: STRIPE_WEBHOOK_SECRET=whsec_replace_with...
# To: STRIPE_WEBHOOK_SECRET=whsec_your_actual_secret

# Edit UAT
nano config/uat.env
# Same process

# Edit PROD
nano config/prod.env
# Same process
```

### Step 3: Restart Backend Services

After updating secrets:

```bash
cd /root/crane
./scripts/restart-backends-with-env-config.sh
```

### Step 4: Verify Configuration

```bash
./scripts/validate-stripe-config.sh
```

Should show: ✓ STRIPE_WEBHOOK_SECRET: Configured

### Step 5: Test Complete Payment Flow

```bash
# Test DEV
./scripts/test-complete-payment-flow.sh dev

# Test UAT
./scripts/test-complete-payment-flow.sh uat

# Test PROD (be careful - uses real payments!)
./scripts/test-complete-payment-flow.sh prod
```

### Step 6: Test Frontend Payment

1. Open: https://dev.craneintelligence.tech/report-generation.html
2. Fill in report details
3. Click "Purchase Report"
4. Use test card: **4242 4242 4242 4242**
5. Complete payment
6. Monitor webhook delivery:

```bash
docker logs crane-dev-backend-1 -f | grep -i webhook
```

You should see:
- `Received Stripe webhook: payment_intent.succeeded`
- `Payment marked as received for report`
- `Sent submission notification`

## 📊 Current Status

| Component | DEV | UAT | PROD |
|-----------|-----|-----|------|
| Stripe Keys | ✅ | ✅ | ✅ |
| Payment Intents | ✅ | ✅ | ✅ |
| Webhook Secrets | ⚠️ | ⚠️ | ⚠️ |
| Webhook Delivery | ⏳ | ⏳ | ⏳ |

**Legend:**
- ✅ Working
- ⚠️ Needs configuration
- ⏳ Waiting for webhook secrets

## 🧪 Test Results

### Payment Intent Creation
```
✓ DEV: Payment intents created successfully
✓ UAT: Payment intents created successfully
✓ PROD: Payment intents created successfully
```

### Stripe Service
```
✓ DEV: Stripe service initialized, test keys validated
✓ UAT: Stripe service initialized, test keys validated
✓ PROD: Stripe service initialized, live keys validated
```

### Webhook Configuration
```
⚠ DEV: Webhook secret needs to be configured
⚠ UAT: Webhook secret needs to be configured
⚠ PROD: Webhook secret needs to be configured
```

## 📝 Quick Commands Reference

```bash
# Configure webhook secrets (interactive)
./scripts/configure-webhook-secrets.sh --interactive

# Restart all backends
./scripts/restart-backends-with-env-config.sh

# Validate configuration
./scripts/validate-stripe-config.sh

# Test payment flow
./scripts/test-complete-payment-flow.sh dev

# Test webhook delivery
./scripts/test-webhook-delivery.sh dev

# Monitor webhook logs
docker logs crane-dev-backend-1 -f | grep -i webhook

# Check Stripe service status
docker logs crane-dev-backend-1 --tail 50 | grep -i stripe
```

## 🎯 Success Criteria

Once webhook secrets are configured, you should be able to:

- [x] Create payment intents ✅
- [ ] Receive webhook events ⏳
- [ ] Process payment success webhooks ⏳
- [ ] Update report status automatically ⏳
- [ ] Send email notifications ⏳
- [ ] Complete end-to-end payment flow ⏳

## 🆘 Troubleshooting

### Webhook Secret Not Working

1. **Verify secret format**
   ```bash
   grep STRIPE_WEBHOOK_SECRET config/dev.env
   ```
   Should start with `whsec_`

2. **Check backend logs**
   ```bash
   docker logs crane-dev-backend-1 --tail 100 | grep -i webhook
   ```

3. **Verify endpoint URL in Stripe**
   - Must match exactly: `https://dev.craneintelligence.tech/api/v1/payment-webhooks/stripe`
   - Must be HTTPS

### Payment Succeeds but Webhook Not Received

1. Check Stripe dashboard → Webhooks → Recent deliveries
2. Check if webhook endpoint is active
3. Verify webhook secret matches
4. Check backend logs for signature verification errors

## 📚 Documentation

- **Quick Start**: `QUICK_START_WEBHOOK_SETUP.md`
- **Detailed Guide**: `WEBHOOK_SETUP_GUIDE.md`
- **Testing Guide**: `PAYMENT_FLOW_TESTING_GUIDE.md`
- **Complete Setup**: `STRIPE_PAYMENT_COMPLETE_SETUP.md`

## ✨ Summary

**Status**: Payment flow is **fully functional** except for webhook processing, which requires webhook secrets from Stripe dashboard.

**Next Action**: Get webhook secrets from Stripe dashboard and configure them using:
```bash
./scripts/configure-webhook-secrets.sh --interactive
```

Once configured, the complete payment flow will work end-to-end including automatic report status updates and email notifications.

