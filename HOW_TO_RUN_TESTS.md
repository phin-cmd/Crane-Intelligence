# How to Run Payment Flow Tests - Step by Step Guide

## Quick Start

All test scripts are now executable. Here's how to run them:

## Step-by-Step Instructions

### Step 1: Navigate to Project Directory

```bash
cd /root/crane
```

### Step 2: Make Scripts Executable (if needed)

If you get "Permission denied" errors, run:

```bash
chmod +x scripts/*.sh
```

This makes all shell scripts in the `scripts/` directory executable.

### Step 3: Test DEV Environment

```bash
./scripts/test-complete-payment-flow.sh dev
```

**What this does:**
- Tests backend health
- Verifies Stripe configuration
- Creates a payment intent
- Checks webhook configuration
- Provides frontend testing instructions

**Expected output:**
- ✓ Backend is running
- ✓ Stripe configuration correct
- ✓ Payment intent created successfully
- Payment Intent ID will be shown

### Step 4: Test UAT Environment

```bash
./scripts/test-complete-payment-flow.sh uat
```

**What this does:**
- Same tests as DEV but for UAT environment
- Uses UAT backend (port 8204)
- Tests UAT-specific configuration

**Expected output:**
- Same as DEV but for UAT environment

### Step 5: Test PRODUCTION Environment

⚠️ **WARNING**: This uses LIVE Stripe keys and will create REAL payment intents!

```bash
./scripts/test-complete-payment-flow.sh prod
```

**What this does:**
- Tests production environment
- Uses live Stripe keys
- Creates real payment intents (be careful!)

**Expected output:**
- Same as other environments but with live keys

### Step 6: Complete Verification

Run the comprehensive verification script:

```bash
./scripts/verify-payment-flow-complete.sh
```

**What this does:**
- Verifies webhook secrets in config files
- Restarts backend services
- Tests config endpoints
- Tests payment intent creation
- Verifies webhook secrets in containers
- Checks Stripe service status

**Expected output:**
- ✓ All checks passed!
- Summary of all verification steps

## Alternative: Run All Tests at Once

You can create a simple script to run all tests:

```bash
cd /root/crane

echo "=== Testing DEV ==="
./scripts/test-complete-payment-flow.sh dev
echo ""
echo "=== Testing UAT ==="
./scripts/test-complete-payment-flow.sh uat
echo ""
echo "=== Testing PROD ==="
./scripts/test-complete-payment-flow.sh prod
echo ""
echo "=== Complete Verification ==="
./scripts/verify-payment-flow-complete.sh
```

## Understanding the Output

### Success Indicators

Look for these in the output:
- ✓ Green checkmarks = Success
- ⚠ Yellow warnings = Needs attention but not critical
- ✗ Red X = Failure (needs fixing)

### Key Information in Output

1. **Payment Intent ID**: Shows the Stripe payment intent that was created
2. **Client Secret**: Used by frontend to complete payment
3. **Stripe Mode**: Should be "test" for dev/uat, "live" for prod
4. **Webhook Status**: Shows if webhook secret is configured

## Troubleshooting

### Permission Denied Error

```bash
chmod +x scripts/test-complete-payment-flow.sh
chmod +x scripts/verify-payment-flow-complete.sh
```

### Backend Not Running

If you see "Container not running" errors:

```bash
# Check if containers are running
docker ps | grep backend

# Restart if needed
./scripts/restart-backends-with-env-config.sh
```

### Endpoint Not Accessible

If config or payment endpoints fail:

```bash
# Check if backend is responding
curl http://localhost:8104/api/v1/config/public

# Check backend logs
docker logs crane-dev-backend-1 --tail 50
```

## Next Steps After Testing

Once all tests pass:

1. **Test Frontend Payment**
   - Open: https://dev.craneintelligence.tech/report-generation.html
   - Complete a test payment
   - Monitor webhook delivery

2. **Monitor Webhooks**
   ```bash
   docker logs crane-dev-backend-1 -f | grep -i webhook
   ```

3. **Verify Report Status**
   - Check that reports update from DRAFT to SUBMITTED
   - Verify payment status is succeeded

## Quick Reference

| Command | Purpose |
|---------|---------|
| `./scripts/test-complete-payment-flow.sh dev` | Test DEV environment |
| `./scripts/test-complete-payment-flow.sh uat` | Test UAT environment |
| `./scripts/test-complete-payment-flow.sh prod` | Test PROD environment |
| `./scripts/verify-payment-flow-complete.sh` | Complete verification |
| `./scripts/validate-stripe-config.sh` | Validate configuration |
| `./scripts/test-webhook-delivery.sh dev` | Test webhook delivery |

## Example Output

When everything works correctly, you should see:

```
==========================================
Complete Payment Flow Test - dev
==========================================

Environment: dev
API URL: http://localhost:8104
Frontend URL: https://dev.craneintelligence.tech

Step 1: Backend Health Check
✓ Backend is running

Step 2: Stripe Configuration
✓ Stripe test keys configured correctly

Step 3: Create Payment Intent
✓ Payment intent created successfully
  Payment Intent ID: pi_3SlD3kKH8wu63McV1X2I0Ycl
  Client Secret: pi_3SlD3kKH8wu63McV1X2I0Ycl_secret_...

Step 4: Webhook Configuration Check
✓ Webhook secret is configured

...

Test Summary
✓ Backend is running
✓ Stripe configuration correct
✓ Payment intent creation working
✓ Webhook secret configured
```

## Need Help?

If tests fail:
1. Check backend logs: `docker logs <container-name> --tail 100`
2. Verify configuration: `./scripts/validate-stripe-config.sh`
3. Check if backends are running: `docker ps | grep backend`
4. Review documentation: `FINAL_PAYMENT_FLOW_VERIFICATION.md`

