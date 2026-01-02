# Payment Flow Testing Guide

This guide provides comprehensive instructions for testing the complete payment flow end-to-end, including webhook handling.

## Prerequisites

1. ✅ Stripe keys configured in all environments
2. ✅ Backend services running
3. ✅ Frontend accessible
4. ⚠️ Webhook secrets configured (optional for basic testing, required for full webhook testing)

## Quick Test

Run the automated test script:

```bash
cd /root/crane
./scripts/test-payment-flow.sh dev    # Test DEV environment
./scripts/test-payment-flow.sh uat    # Test UAT environment
./scripts/test-payment-flow.sh prod    # Test PRODUCTION environment
```

## Manual Testing Steps

### Step 1: Verify Configuration

1. **Check Config Endpoint**
   ```bash
   # DEV
   curl http://localhost:8104/api/v1/config/public | jq
   
   # UAT
   curl http://localhost:8204/api/v1/config/public | jq
   
   # PROD
   curl http://localhost:8004/api/v1/config/public | jq
   ```

2. **Verify Stripe Keys**
   - DEV/UAT should return `pk_test_...` keys
   - PROD should return `pk_live_...` keys
   - `stripe_mode` should match the key type

### Step 2: Test Payment Intent Creation

1. **Create Payment Intent via API**
   ```bash
   curl -X POST http://localhost:8104/api/v1/fmv-reports/create-payment \
     -H "Content-Type: application/json" \
     -d '{
       "report_type": "spot_check",
       "amount": 10000,
       "crane_data": {
         "manufacturer": "Test",
         "model": "Test Model"
       },
       "cardholder_name": "Test User",
       "receipt_email": "test@example.com"
     }' | jq
   ```

2. **Expected Response**
   ```json
   {
     "success": true,
     "client_secret": "pi_..._secret_...",
     "payment_intent_id": "pi_...",
     "transaction_id": "...",
     "amount": 10000,
     "currency": "usd"
   }
   ```

### Step 3: Test Frontend Payment Flow

1. **Navigate to Report Generation Page**
   - DEV: https://dev.craneintelligence.tech/report-generation.html
   - UAT: https://uat.craneintelligence.tech/report-generation.html
   - PROD: https://craneintelligence.tech/report-generation.html

2. **Fill in Report Details**
   - Select report type (Spot Check, Professional, or Fleet Valuation)
   - Fill in crane details (manufacturer, model, etc.)
   - Click "Purchase Report" button

3. **Complete Payment**
   - Payment modal should open
   - Stripe Payment Element should load
   - Use test card: `4242 4242 4242 4242`
   - Expiry: Any future date (e.g., `12/34`)
   - CVC: Any 3 digits (e.g., `123`)
   - ZIP: Any 5 digits (e.g., `12345`)
   - Enter cardholder name
   - Enter receipt email
   - Click "Submit Payment"

4. **Verify Payment Success**
   - Success modal should appear
   - Payment should be processed
   - Report status should update

### Step 4: Test Webhook Delivery

1. **Monitor Backend Logs**
   ```bash
   # DEV
   docker logs crane-dev-backend-1 -f | grep -i webhook
   
   # UAT
   docker logs crane-uat-backend-1 -f | grep -i webhook
   
   # PROD
   docker logs crane-backend-1 -f | grep -i webhook
   ```

2. **Expected Webhook Events**
   - `payment_intent.created` - When payment intent is created
   - `payment_intent.succeeded` - When payment is successful
   - `payment_intent.payment_failed` - If payment fails

3. **Verify Webhook Processing**
   - Check logs for: "Received Stripe webhook: payment_intent.succeeded"
   - Check logs for: "Payment marked as received for report"
   - Check logs for: "Sent submission notification"

### Step 5: Verify Report Status Update

1. **Check Report Status**
   - After successful payment, report should move from `DRAFT` to `SUBMITTED`
   - Payment status should be `succeeded`
   - `amount_paid` should be set
   - `paid_at` timestamp should be set

2. **Check User Notifications**
   - User should receive email notification
   - User should see in-app notification
   - Report should appear in user's report list

## Test Cards

### Test Mode Cards (DEV/UAT)

| Card Number | Description |
|------------|-------------|
| `4242 4242 4242 4242` | Successful payment |
| `4000 0000 0000 0002` | Card declined |
| `4000 0000 0000 9995` | Insufficient funds |
| `4000 0025 0000 3155` | Requires authentication (3D Secure) |

### Live Mode Cards (PROD)

⚠️ **WARNING**: Only use real cards in production. Test cards will not work in live mode.

## Webhook Testing

### Using Stripe Dashboard

1. **Go to Stripe Dashboard**
   - https://dashboard.stripe.com/webhooks

2. **Select Environment**
   - Toggle to Test mode for DEV/UAT
   - Toggle to Live mode for PROD

3. **Find Webhook Endpoint**
   - Click on your webhook endpoint

4. **Send Test Webhook**
   - Click "Send test webhook"
   - Select event: `payment_intent.succeeded`
   - Click "Send test webhook"

5. **Check Delivery Status**
   - View "Recent deliveries" section
   - Check HTTP response code (should be 200)
   - Check backend logs for processing

### Using Test Script

```bash
cd /root/crane
./scripts/test-webhook-delivery.sh dev
./scripts/test-webhook-delivery.sh uat
./scripts/test-webhook-delivery.sh prod
```

## Monitoring and Logs

### Check Stripe Service Status

```bash
# Check all environments
docker logs crane-dev-backend-1 --tail 50 | grep -i stripe
docker logs crane-uat-backend-1 --tail 50 | grep -i stripe
docker logs crane-backend-1 --tail 50 | grep -i stripe
```

### Check for Errors

```bash
# Check for Stripe errors
docker logs crane-dev-backend-1 --tail 200 | grep -iE "(stripe.*error|payment.*error)"

# Check for webhook errors
docker logs crane-dev-backend-1 --tail 200 | grep -iE "(webhook.*error|invalid.*webhook)"
```

### Monitor Real-time

```bash
# Monitor all payment-related activity
docker logs crane-dev-backend-1 -f | grep -iE "(stripe|payment|webhook)"
```

## Expected Log Messages

### Successful Payment Flow

```
INFO:app.services.stripe_service:Stripe service initialized
INFO:app.services.stripe_service:✓ DEV environment using test Stripe keys (correct)
INFO:stripe:message='Request to Stripe api' method=post url=https://api.stripe.com/v1/payment_intents
INFO:app.services.stripe_service:Payment intent created: pi_...
INFO:app.api.v1.payment_webhooks:Received Stripe webhook: payment_intent.succeeded
INFO:app.api.v1.payment_webhooks:✅ Found report ... for payment intent ...
INFO:app.api.v1.payment_webhooks:✅ Payment marked as received for report ...
```

### Webhook Processing

```
INFO:app.api.v1.payment_webhooks:Received Stripe webhook: payment_intent.succeeded
INFO:app.services.fmv_report_service:✅ Payment received for FMV report ...
INFO:app.api.v1.payment_webhooks:✅ Sent submission notification for report ...
```

## Troubleshooting

### Payment Intent Creation Fails

1. **Check Stripe Keys**
   - Verify keys are correct in environment files
   - Check backend logs for key validation messages

2. **Check Network**
   - Ensure backend can reach Stripe API
   - Check firewall rules

3. **Check Stripe Account**
   - Verify Stripe account is active
   - Check for account restrictions

### Webhook Not Received

1. **Check Webhook Secret**
   - Verify secret is configured in environment file
   - Ensure secret matches Stripe dashboard

2. **Check Endpoint URL**
   - Verify URL is correct and accessible
   - Test endpoint: `curl https://dev.craneintelligence.tech/api/v1/payment-webhooks/stripe`

3. **Check SSL Certificate**
   - Stripe requires HTTPS
   - Verify SSL certificate is valid

### Payment Succeeds but Report Not Updated

1. **Check Webhook Processing**
   - Verify webhook was received
   - Check logs for webhook processing errors

2. **Check Database**
   - Verify database connection
   - Check for database errors in logs

3. **Check Report Association**
   - Verify `payment_intent_id` is linked to report
   - Check report exists in database

## Test Checklist

- [ ] Config endpoint returns correct Stripe key
- [ ] Payment intent creation works
- [ ] Frontend payment modal opens
- [ ] Stripe Payment Element loads
- [ ] Test card payment succeeds
- [ ] Webhook is received (if configured)
- [ ] Report status updates to SUBMITTED
- [ ] Payment status is succeeded
- [ ] User receives email notification
- [ ] User sees in-app notification
- [ ] Report appears in user's report list

## Next Steps

1. **Configure Webhooks** (if not done)
   - See `WEBHOOK_SETUP_GUIDE.md` for instructions

2. **Test All Report Types**
   - Spot Check
   - Professional
   - Fleet Valuation

3. **Test Error Scenarios**
   - Failed payments
   - Declined cards
   - Network errors

4. **Monitor Production**
   - Set up alerts for failed payments
   - Monitor webhook delivery rates
   - Track payment success rates

## Support

If you encounter issues:
1. Check this guide's troubleshooting section
2. Review backend logs for detailed errors
3. Verify Stripe dashboard configuration
4. Test webhook delivery using Stripe dashboard

