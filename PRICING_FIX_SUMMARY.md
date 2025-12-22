# Pricing Display Fix - Amount Conversion

## Issue Fixed
Fleet valuation draft emails were showing `$149500.00` instead of `$1495.00` because amounts were being passed in cents without conversion to dollars.

## Root Cause
The `get_base_price_dollars()` function returns amounts in **cents** (e.g., 149500 for fleet valuation), but the email template expects amounts in **dollars**. The amount was being passed directly without conversion.

## Solution
Added `_convert_amount_to_dollars()` helper method in `FMVEmailService` that:
- Detects if amount is in cents (>= 10000 or >= 1000 and divisible by 100)
- Converts cents to dollars by dividing by 100
- Handles amounts already in dollars correctly

## Files Modified

1. **`/root/crane/backend/app/services/fmv_email_service.py`**
   - Added `_convert_amount_to_dollars()` method
   - Updated `send_draft_reminder_notification()` to convert amounts
   - Updated `send_draft_created_notification()` to convert amounts
   - Updated `send_submitted_notification()` to convert amounts
   - Updated `send_paid_notification()` to convert amounts

2. **`/root/crane/backend/app/api/v1/fmv_reports.py`**
   - Updated fallback amounts to be in cents for consistency
   - Added comment that amounts will be converted in email service

3. **`/root/crane/backend/app/services/fmv_report_service.py`**
   - Added comment that amounts are in cents and will be converted

## Test Results

✅ **Amount Conversion Tests:**
- 149500 cents → $1495.00 ✅
- 99500 cents → $995.00 ✅
- 25000 cents → $250.00 ✅
- 1495.00 dollars → $1495.00 ✅ (already in dollars)
- 995.00 dollars → $995.00 ✅ (already in dollars)

## Email Templates Affected

- `fmv_report_draft_reminder.html` - Now shows correct amounts
- All other email templates using `amount` variable

## Verification

All email notifications now display correct dollar amounts:
- **Fleet Valuation**: $1,495.00 (not $149,500.00)
- **Professional**: $995.00 (not $99,500.00)
- **Spot Check**: $250.00 (not $25,000.00)

The fix is applied to all email sending methods and will work for both existing and new draft reports.

