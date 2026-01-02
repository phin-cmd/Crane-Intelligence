# Final Payment Flow Verification - Complete Guide

## ✅ Configuration Status

### Webhook Secrets - CONFIGURED ✅

All three environments have webhook secrets properly configured:

1. **DEV**: `whsec_DXUXxOMRn5lmk6TyP3sqVMZ1KseJZNQC` ✅
2. **UAT**: `whsec_YMmRv8dEYPszEgwGXYPoFegqwnsFZHPa` ✅
3. **PROD**: `whsec_jlJgNwmPZC2YeTzA02CeuVyLCf1JASpn` ✅

### Stripe Keys - CONFIGURED ✅

- DEV/UAT: Test keys (pk_test_... / sk_test_...) ✅
- PROD: Live keys (pk_live_... / sk_live_...) ✅

## 🔄 Required Actions

### Step 1: Restart Backend Services

The backends need to be restarted to load the new webhook secrets:

```bash
cd /root/crane

# Option A: Restart all at once
./scripts/restart-backends-with-env-config.sh

# Option B: Restart individually
docker restart crane-dev-backend-1
docker restart crane-uat-backend-1
docker restart crane-backend-1

# Wait for services to start
sleep 10
```

### Step 2: Verify Configuration

```bash
cd /root/crane

# Validate all configurations
./scripts/validate-stripe-config.sh
```

Expected output should show:
- ✓ STRIPE_WEBHOOK_SECRET: Configured (for all environments)
- ✓ Stripe keys match environment

### Step 3: Test Payment Flow

```bash
# Test DEV environment
./scripts/test-complete-payment-flow.sh dev

# Test UAT environment
./scripts/test-complete-payment-flow.sh uat

# Test PROD environment (be careful - uses real payments!)
./scripts/test-complete-payment-flow.sh prod
```

### Step 4: Verify Webhook Secrets in Containers

```bash
# Check DEV
docker exec crane-dev-backend-1 env | grep STRIPE_WEBHOOK_SECRET

# Check UAT
docker exec crane-uat-backend-1 env | grep STRIPE_WEBHOOK_SECRET

# Check PROD
docker exec crane-backend-1 env | grep STRIPE_WEBHOOK_SECRET
```

Each should show: `STRIPE_WEBHOOK_SECRET=whsec_...` (not placeholder)

### Step 5: Test Config Endpoints

```bash
# DEV
curl -s http://localhost:8104/api/v1/config/public | python3 -m json.tool

# UAT
curl -s http://localhost:8204/api/v1/config/public | python3 -m json.tool

# PROD
curl -s http://localhost:8004/api/v1/config/public | python3 -m json.tool
```

Expected:
- Returns correct Stripe publishable key
- `stripe_mode`: "test" for dev/uat, "live" for prod
- `environment`: matches the environment

### Step 6: Test Payment Intent Creation

```bash
# DEV
curl -X POST http://localhost:8104/api/v1/fmv-reports/create-payment \
  -H "Content-Type: application/json" \
  -d '{
    "report_type": "spot_check",
    "amount": 10000,
    "crane_data": {"manufacturer": "Test", "model": "Test Model"},
    "cardholder_name": "Test User",
    "receipt_email": "test@example.com"
  }' | python3 -m json.tool

# UAT (change port to 8204)
curl -X POST http://localhost:8204/api/v1/fmv-reports/create-payment ...

# PROD (change port to 8004)
curl -X POST http://localhost:8004/api/v1/fmv-reports/create-payment ...
```

Expected response:
```json
{
  "success": true,
  "client_secret": "pi_..._secret_...",
  "payment_intent_id": "pi_...",
  "amount": 10000,
  "currency": "usd"
}
```

### Step 7: Test Frontend Payment Flow

1. **Open Frontend**
   - DEV: https://dev.craneintelligence.tech/report-generation.html
   - UAT: https://uat.craneintelligence.tech/report-generation.html
   - PROD: https://craneintelligence.tech/report-generation.html

2. **Complete Payment**
   - Fill in report details
   - Click "Purchase Report"
   - Use test card: **4242 4242 4242 4242**
   - Expiry: **12/34**
   - CVC: **123**
   - ZIP: **12345**
   - Complete payment

3. **Monitor Webhook Delivery**

   ```bash
   # DEV
   docker logs crane-dev-backend-1 -f | grep -i webhook
   
   # UAT
   docker logs crane-uat-backend-1 -f | grep -i webhook
   
   # PROD
   docker logs crane-backend-1 -f | grep -i webhook
   ```

   Expected logs:
   ```
   INFO:app.api.v1.payment_webhooks:Received Stripe webhook: payment_intent.succeeded
   INFO:app.api.v1.payment_webhooks:✅ Found report ... for payment intent ...
   INFO:app.api.v1.payment_webhooks:✅ Payment marked as received for report ...
   INFO:app.api.v1.payment_webhooks:✅ Sent submission notification for report ...
   ```

4. **Verify Report Status**
   - Report status should be `SUBMITTED`
   - Payment status should be `succeeded`
   - `amount_paid` should be set
   - User should receive email notification

## 📊 Verification Checklist

### Configuration ✅
- [x] DEV webhook secret: `whsec_DXUXxOMRn5lmk6TyP3sqVMZ1KseJZNQC`
- [x] UAT webhook secret: `whsec_YMmRv8dEYPszEgwGXYPoFegqwnsFZHPa`
- [x] PROD webhook secret: `whsec_jlJgNwmPZC2YeTzA02CeuVyLCf1JASpn`
- [x] All Stripe keys configured correctly

### Backend Services ⏳
- [ ] Backend services restarted
- [ ] Webhook secrets loaded in containers
- [ ] Stripe service initialized
- [ ] No errors in logs

### API Testing ⏳
- [ ] Config endpoints working
- [ ] Payment intent creation working
- [ ] All environments accessible

### End-to-End Flow ⏳
- [ ] Frontend payment completes
- [ ] Webhook received and processed
- [ ] Report status updates
- [ ] Email notification sent

## 🎯 Success Criteria

Once all steps are completed, you should have:

1. ✅ **Payment Intent Creation**: Working in all environments
2. ✅ **Webhook Processing**: Webhooks received and processed correctly
3. ✅ **Report Status Updates**: Reports automatically move from DRAFT to SUBMITTED
4. ✅ **Email Notifications**: Users receive confirmation emails
5. ✅ **Complete Flow**: End-to-end payment flow working seamlessly

## 🚀 Quick Start Commands

```bash
# 1. Restart all backends
cd /root/crane && ./scripts/restart-backends-with-env-config.sh

# 2. Validate configuration
./scripts/validate-stripe-config.sh

# 3. Test payment flow
./scripts/test-complete-payment-flow.sh dev

# 4. Monitor webhooks
docker logs crane-dev-backend-1 -f | grep -i webhook
```

## 📝 Summary

**Configuration Status**: ✅ **COMPLETE**
- All webhook secrets configured
- All Stripe keys configured
- All environment files updated

**Next Steps**: 
1. Restart backend services
2. Run verification scripts
3. Test frontend payment flow
4. Monitor webhook delivery

**Expected Result**: Complete end-to-end payment flow working in all environments! 🎉

