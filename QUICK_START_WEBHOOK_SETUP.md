# Quick Start: Webhook Setup & Payment Flow Testing

This is a streamlined guide to complete webhook setup and test the payment flow.

## Part 1: Get Webhook Secrets from Stripe Dashboard

### For DEV Environment (Test Mode)

1. **Go to Stripe Dashboard**
   - Visit: https://dashboard.stripe.com/webhooks
   - **Important**: Toggle to **"Test mode"** (top right)

2. **Create Webhook Endpoint**
   - Click **"Add endpoint"**
   - Enter URL: `https://dev.craneintelligence.tech/api/v1/payment-webhooks/stripe`
   - Click **"Add endpoint"**

3. **Select Events**
   - Click **"Select events"**
   - Choose: `payment_intent.succeeded`, `payment_intent.payment_failed`, `payment_intent.canceled`
   - Click **"Add events"**

4. **Get Signing Secret**
   - In the webhook details, find **"Signing secret"**
   - Click **"Reveal"**
   - Copy the secret (starts with `whsec_`)

### For UAT Environment (Test Mode)

1. **Still in Test Mode** (same as DEV)
2. **Create another webhook endpoint**
   - URL: `https://uat.craneintelligence.tech/api/v1/payment-webhooks/stripe`
   - Same events as DEV
   - Copy the signing secret

### For PRODUCTION Environment (Live Mode)

1. **Toggle to Live Mode** (top right of Stripe dashboard)
2. **Create webhook endpoint**
   - URL: `https://craneintelligence.tech/api/v1/payment-webhooks/stripe`
   - Same events
   - Copy the signing secret (different from test mode!)

## Part 2: Configure Webhook Secrets

### Option A: Interactive Script (Recommended)

```bash
cd /root/crane
./scripts/configure-webhook-secrets.sh --interactive
```

The script will prompt you for each environment's webhook secret.

### Option B: Manual Update

Edit the environment files directly:

```bash
# DEV
nano /root/crane/config/dev.env
# Find: STRIPE_WEBHOOK_SECRET=whsec_replace_with...
# Replace with: STRIPE_WEBHOOK_SECRET=whsec_your_actual_secret

# UAT
nano /root/crane/config/uat.env
# Same process

# PROD
nano /root/crane/config/prod.env
# Same process
```

### Option C: Command Line

```bash
# DEV
./scripts/configure-webhook-secrets.sh dev whsec_your_dev_secret_here

# UAT
./scripts/configure-webhook-secrets.sh uat whsec_your_uat_secret_here

# PROD
./scripts/configure-webhook-secrets.sh prod whsec_your_prod_secret_here
```

## Part 3: Restart Backend Services

After updating webhook secrets, restart all backend services:

```bash
cd /root/crane
./scripts/restart-backends-with-env-config.sh
```

Or restart individually:

```bash
docker restart crane-dev-backend-1
docker restart crane-uat-backend-1
docker restart crane-backend-1
```

## Part 4: Verify Configuration

```bash
cd /root/crane
./scripts/validate-stripe-config.sh
```

You should see:
- ✓ STRIPE_WEBHOOK_SECRET: Configured (for all environments)

## Part 5: Test Complete Payment Flow

### Automated Test

```bash
# Test DEV environment
./scripts/test-complete-payment-flow.sh dev

# Test UAT environment
./scripts/test-complete-payment-flow.sh uat

# Test PROD environment
./scripts/test-complete-payment-flow.sh prod
```

### Manual Frontend Test

1. **Open Report Generation Page**
   - DEV: https://dev.craneintelligence.tech/report-generation.html
   - UAT: https://uat.craneintelligence.tech/report-generation.html
   - PROD: https://craneintelligence.tech/report-generation.html

2. **Fill in Report Details**
   - Select report type
   - Enter crane details
   - Click "Purchase Report"

3. **Complete Payment**
   - Use test card: **4242 4242 4242 4242**
   - Expiry: **12/34** (any future date)
   - CVC: **123** (any 3 digits)
   - ZIP: **12345** (any 5 digits)
   - Enter cardholder name
   - Enter receipt email
   - Click "Submit Payment"

4. **Monitor Webhook Delivery**

   ```bash
   # DEV
   docker logs crane-dev-backend-1 -f | grep -i webhook
   
   # UAT
   docker logs crane-uat-backend-1 -f | grep -i webhook
   
   # PROD
   docker logs crane-backend-1 -f | grep -i webhook
   ```

   You should see:
   - `Received Stripe webhook: payment_intent.succeeded`
   - `Payment marked as received for report`
   - `Sent submission notification`

5. **Verify Report Status**
   - Report status should change from `DRAFT` to `SUBMITTED`
   - Payment status should be `succeeded`
   - `amount_paid` should be set
   - User should receive email notification

## Part 6: Test Webhook Delivery (Optional)

### Using Stripe Dashboard

1. Go to your webhook endpoint in Stripe dashboard
2. Click **"Send test webhook"**
3. Select event: `payment_intent.succeeded`
4. Click **"Send test webhook"**
5. Check "Recent deliveries" for status
6. Monitor backend logs for processing

### Using Test Script

```bash
./scripts/test-webhook-delivery.sh dev
./scripts/test-webhook-delivery.sh uat
./scripts/test-webhook-delivery.sh prod
```

## Troubleshooting

### Webhook Not Received

1. **Check Webhook Secret**
   ```bash
   grep STRIPE_WEBHOOK_SECRET config/dev.env
   ```
   Should show: `STRIPE_WEBHOOK_SECRET=whsec_...` (not `replace_with`)

2. **Check Backend Logs**
   ```bash
   docker logs crane-dev-backend-1 --tail 100 | grep -i webhook
   ```

3. **Verify Endpoint URL**
   - Check Stripe dashboard webhook URL matches exactly
   - Must be HTTPS (not HTTP)

### Payment Succeeds but Report Not Updated

1. **Check Webhook Processing**
   - Verify webhook was received (check logs)
   - Check for webhook processing errors

2. **Check Database**
   - Verify `payment_intent_id` is linked to report
   - Check report status in database

## Quick Reference

| Task | Command |
|------|---------|
| Configure webhook secrets | `./scripts/configure-webhook-secrets.sh --interactive` |
| Restart backends | `./scripts/restart-backends-with-env-config.sh` |
| Validate config | `./scripts/validate-stripe-config.sh` |
| Test payment flow | `./scripts/test-complete-payment-flow.sh dev` |
| Test webhook | `./scripts/test-webhook-delivery.sh dev` |
| Monitor logs | `docker logs crane-dev-backend-1 -f \| grep -i webhook` |

## Success Criteria

✅ Webhook secrets configured in all environment files  
✅ Backend services restarted  
✅ Configuration validation passes  
✅ Payment intent creation works  
✅ Frontend payment completes successfully  
✅ Webhook is received and processed  
✅ Report status updates to SUBMITTED  
✅ User receives email notification  

## Need Help?

- See `WEBHOOK_SETUP_GUIDE.md` for detailed instructions
- See `PAYMENT_FLOW_TESTING_GUIDE.md` for comprehensive testing guide
- Check backend logs for detailed error messages

