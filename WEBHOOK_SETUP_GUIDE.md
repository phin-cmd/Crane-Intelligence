# Stripe Webhook Setup Guide

This guide provides step-by-step instructions for configuring Stripe webhooks for all environments.

## Webhook Endpoints

Each environment has its own webhook endpoint:

- **DEV**: `https://dev.craneintelligence.tech/api/v1/payment-webhooks/stripe`
- **UAT**: `https://uat.craneintelligence.tech/api/v1/payment-webhooks/stripe`
- **PROD**: `https://craneintelligence.tech/api/v1/payment-webhooks/stripe`

## Step 1: Access Stripe Dashboard

1. Go to [Stripe Dashboard](https://dashboard.stripe.com)
2. Log in with your Stripe account credentials

## Step 2: Configure DEV Environment Webhooks (Test Mode)

1. **Toggle to Test Mode**
   - Click the toggle in the top right of the Stripe dashboard
   - Ensure it shows "Test mode" (not "Live mode")

2. **Create Webhook Endpoint**
   - Navigate to: **Developers** → **Webhooks**
   - Click **"Add endpoint"** button
   - Enter endpoint URL: `https://dev.craneintelligence.tech/api/v1/payment-webhooks/stripe`
   - Click **"Add endpoint"**

3. **Select Events to Listen To**
   - In the webhook endpoint settings, click **"Select events"**
   - Select the following events:
     - `payment_intent.created`
     - `payment_intent.succeeded`
     - `payment_intent.payment_failed`
     - `payment_intent.canceled`
     - `charge.refunded`
   - Click **"Add events"**

4. **Copy Signing Secret**
   - After creating the endpoint, you'll see a **"Signing secret"** section
   - Click **"Reveal"** to show the secret
   - Copy the secret (it starts with `whsec_`)
   - **Important**: Keep this secret secure and never commit it to version control

5. **Update Environment File**
   - Open `/root/crane/config/dev.env`
   - Find the line: `STRIPE_WEBHOOK_SECRET=whsec_replace_with_dev_webhook_secret_from_stripe_dashboard`
   - Replace with: `STRIPE_WEBHOOK_SECRET=whsec_your_actual_secret_here`
   - Save the file

## Step 3: Configure UAT Environment Webhooks (Test Mode)

1. **Ensure Test Mode is Active**
   - The toggle should still show "Test mode"

2. **Create Webhook Endpoint**
   - Navigate to: **Developers** → **Webhooks**
   - Click **"Add endpoint"** button
   - Enter endpoint URL: `https://uat.craneintelligence.tech/api/v1/payment-webhooks/stripe`
   - Click **"Add endpoint"**

3. **Select Events to Listen To**
   - Select the same events as DEV:
     - `payment_intent.created`
     - `payment_intent.succeeded`
     - `payment_intent.payment_failed`
     - `payment_intent.canceled`
     - `charge.refunded`
   - Click **"Add events"**

4. **Copy Signing Secret**
   - Copy the signing secret (starts with `whsec_`)

5. **Update Environment File**
   - Open `/root/crane/config/uat.env`
   - Find the line: `STRIPE_WEBHOOK_SECRET=whsec_replace_with_uat_webhook_secret_from_stripe_dashboard`
   - Replace with: `STRIPE_WEBHOOK_SECRET=whsec_your_actual_secret_here`
   - Save the file

## Step 4: Configure PRODUCTION Environment Webhooks (Live Mode)

⚠️ **CRITICAL**: Production uses LIVE mode - real payments will be processed!

1. **Toggle to Live Mode**
   - Click the toggle in the top right of the Stripe dashboard
   - Ensure it shows **"Live mode"** (not "Test mode")

2. **Create Webhook Endpoint**
   - Navigate to: **Developers** → **Webhooks**
   - Click **"Add endpoint"** button
   - Enter endpoint URL: `https://craneintelligence.tech/api/v1/payment-webhooks/stripe`
   - Click **"Add endpoint"**

3. **Select Events to Listen To**
   - Select the same events:
     - `payment_intent.created`
     - `payment_intent.succeeded`
     - `payment_intent.payment_failed`
     - `payment_intent.canceled`
     - `charge.refunded`
   - Click **"Add events"**

4. **Copy Signing Secret**
   - Copy the signing secret (starts with `whsec_`)
   - **Important**: This is different from the test mode secret!

5. **Update Environment File**
   - Open `/root/crane/config/prod.env`
   - Find the line: `STRIPE_WEBHOOK_SECRET=whsec_replace_with_production_webhook_secret_from_stripe_dashboard`
   - Replace with: `STRIPE_WEBHOOK_SECRET=whsec_your_actual_secret_here`
   - Save the file

## Step 5: Restart Backend Services

After updating all environment files, restart the backend services to load the new webhook secrets:

```bash
cd /root/crane
./scripts/restart-backends-with-env-config.sh
```

## Step 6: Verify Configuration

Run the validation script to verify all configurations:

```bash
cd /root/crane
./scripts/validate-stripe-config.sh
```

Expected output should show:
- ✓ STRIPE_WEBHOOK_SECRET: Configured (for all environments)

## Step 7: Test Webhook Delivery

### Using Stripe Dashboard (Recommended)

1. **For DEV/UAT (Test Mode)**
   - Go to **Developers** → **Webhooks**
   - Click on your webhook endpoint
   - Click **"Send test webhook"** button
   - Select event: `payment_intent.succeeded`
   - Click **"Send test webhook"**
   - Check the **"Recent deliveries"** section to see if it was successful

2. **For PROD (Live Mode)**
   - Toggle to **Live mode**
   - Follow the same steps as above
   - **Note**: Only test with real payment intents in production

### Using Test Script

Run the webhook test script:

```bash
cd /root/crane
./scripts/test-webhook-delivery.sh dev
./scripts/test-webhook-delivery.sh uat
./scripts/test-webhook-delivery.sh prod
```

## Step 8: Monitor Backend Logs

Check backend logs to verify webhooks are being received:

```bash
# DEV environment
docker logs crane-dev-backend-1 --tail 50 | grep -i webhook

# UAT environment
docker logs crane-uat-backend-1 --tail 50 | grep -i webhook

# PROD environment
docker logs crane-backend-1 --tail 50 | grep -i webhook
```

## Troubleshooting

### Webhook Not Received

1. **Check Webhook Secret**
   - Verify the secret in the environment file matches the one in Stripe dashboard
   - Ensure you're using the correct secret for the correct mode (test vs live)

2. **Check Endpoint URL**
   - Verify the webhook URL is correct and accessible
   - Test the endpoint: `curl https://dev.craneintelligence.tech/api/v1/payment-webhooks/stripe`

3. **Check Backend Logs**
   - Look for errors related to webhook signature verification
   - Check for "Invalid webhook signature" errors

4. **Verify SSL Certificate**
   - Stripe requires HTTPS for webhook endpoints
   - Ensure SSL certificate is valid and not expired

### Webhook Signature Verification Failed

- **Error**: "Invalid webhook signature"
- **Solution**: 
  - Verify the webhook secret is correct
  - Ensure the secret matches the environment (test vs live)
  - Check that the webhook secret hasn't been rotated in Stripe dashboard

### Webhook Events Not Processing

- **Check Event Selection**: Ensure the correct events are selected in Stripe dashboard
- **Check Backend Logs**: Look for errors in webhook event handlers
- **Verify Database Connection**: Ensure the backend can connect to the database

## Security Best Practices

1. **Never commit webhook secrets to version control**
   - Use `.env` files that are in `.gitignore`
   - Or use environment variables in your deployment platform

2. **Rotate webhook secrets regularly**
   - Update secrets in Stripe dashboard
   - Update environment files
   - Restart backend services

3. **Use different secrets for each environment**
   - Never reuse the same webhook secret across environments
   - Test mode and Live mode have different secrets

4. **Monitor webhook deliveries**
   - Regularly check webhook delivery status in Stripe dashboard
   - Set up alerts for failed webhook deliveries

## Quick Reference

| Environment | Mode | Webhook URL | Secret Location |
|------------|------|-------------|-----------------|
| DEV | Test | `https://dev.craneintelligence.tech/api/v1/payment-webhooks/stripe` | `config/dev.env` |
| UAT | Test | `https://uat.craneintelligence.tech/api/v1/payment-webhooks/stripe` | `config/uat.env` |
| PROD | Live | `https://craneintelligence.tech/api/v1/payment-webhooks/stripe` | `config/prod.env` |

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review backend logs for detailed error messages
3. Verify Stripe dashboard webhook configuration
4. Test webhook delivery using Stripe dashboard test feature

