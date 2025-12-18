#!/usr/bin/env python3
"""
Fix payment intent using API endpoints (no database dependencies)
Usage: python3 fix_payment_intent_api.py pi_3Se8b1BME5ZRi6sp1lMYfUJa kankanamitra01@gmail.com
"""
import sys
import requests
import json

BASE_URL = "http://localhost:8000"  # Change if backend is on different host/port

def fix_payment_intent(payment_intent_id: str, user_email: str):
    """Fix a payment intent that succeeded but report wasn't created"""
    print(f"Looking up user: {user_email}")
    
    # First, try to mark payment received directly
    # This will work if report exists with payment_intent_id
    print("\n1. Attempting to mark payment received via payment-by-intent endpoint...")
    payment_data = {
        "payment_intent_id": payment_intent_id,
        "amount": 495.00  # Default amount for spot check
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/fmv-reports/payment-by-intent",
            json=payment_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            report = response.json()
            print(f"✅ Payment marked as received!")
            print(f"   Report ID: {report.get('id')}")
            print(f"   Status: {report.get('status')}")
            print(f"   Payment Status: {report.get('payment_status')}")
            return True
        elif response.status_code == 404:
            print(f"⚠️  Report not found for payment intent (this is expected if report wasn't created)")
        else:
            print(f"⚠️  API returned status {response.status_code}: {response.text}")
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to backend at {BASE_URL}")
        print(f"   Make sure backend is running: python -m uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"⚠️  Error calling API: {str(e)}")
    
    # If that didn't work, we need to find the user's draft report and update it
    print("\n2. Searching for user's draft reports...")
    
    # Try to get user reports by email
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/fmv-reports/user/{user_email}",
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            reports = response.json()
            print(f"✅ Found {len(reports)} reports for user")
            
            # Find draft reports
            draft_reports = [r for r in reports if r.get('status', '').lower() == 'draft']
            
            if draft_reports:
                # Sort by created_at descending
                draft_reports.sort(key=lambda r: r.get('created_at', ''), reverse=True)
                most_recent = draft_reports[0]
                report_id = most_recent.get('id')
                
                print(f"✅ Found draft report: {report_id}")
                print(f"   Created: {most_recent.get('created_at')}")
                
                # Try to mark payment received for this report
                print(f"\n3. Marking payment received for report {report_id}...")
                payment_data = {
                    "payment_intent_id": payment_intent_id,
                    "amount": 495.00
                }
                
                response = requests.post(
                    f"{BASE_URL}/api/v1/fmv-reports/{report_id}/payment",
                    json=payment_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    report = response.json()
                    print(f"✅ Payment marked as received!")
                    print(f"   Report ID: {report.get('id')}")
                    print(f"   Status: {report.get('status')}")
                    print(f"   Payment Status: {report.get('payment_status')}")
                    return True
                else:
                    print(f"❌ Failed to mark payment: {response.status_code} - {response.text}")
            else:
                print(f"❌ No draft reports found for user")
        else:
            print(f"⚠️  Could not get user reports: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n❌ Could not automatically fix payment intent")
    print("   Manual intervention required:")
    print("   1. Check if report exists in database")
    print("   2. If report exists, update it manually:")
    print(f"      UPDATE fmv_reports SET payment_intent_id = '{payment_intent_id}',")
    print(f"      payment_status = 'succeeded', amount_paid = 495.00,")
    print(f"      status = 'submitted', submitted_at = NOW(), paid_at = NOW()")
    print(f"      WHERE user_id = (SELECT id FROM users WHERE email = '{user_email}')")
    print(f"      AND status = 'draft' ORDER BY created_at DESC LIMIT 1;")
    return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 fix_payment_intent_api.py <payment_intent_id> <user_email>")
        print("Example: python3 fix_payment_intent_api.py pi_3Se8b1BME5ZRi6sp1lMYfUJa kankanamitra01@gmail.com")
        print("\nNote: This script requires the backend API to be running")
        sys.exit(1)
    
    payment_intent_id = sys.argv[1]
    user_email = sys.argv[2]
    
    print("="*70)
    print("Fixing Payment Intent (API Version)")
    print("="*70)
    print(f"Payment Intent ID: {payment_intent_id}")
    print(f"User Email: {user_email}")
    print(f"Backend URL: {BASE_URL}")
    print("="*70)
    print()
    
    success = fix_payment_intent(payment_intent_id, user_email)
    
    if success:
        print("\n✅ Payment intent fixed successfully!")
    else:
        print("\n❌ Failed to fix payment intent")
        print("\nAlternative: Use direct SQL if you have database access:")
        print(f"  psql -h 129.212.177.131 -U crane_user -d crane_intelligence -c \"")
        print(f"  UPDATE fmv_reports SET payment_intent_id = '{payment_intent_id}',")
        print(f"  payment_status = 'succeeded', amount_paid = 495.00,")
        print(f"  status = 'submitted', submitted_at = NOW(), paid_at = NOW()")
        print(f"  WHERE user_id = (SELECT id FROM users WHERE email = '{user_email}')")
        print(f"  AND status = 'draft' ORDER BY created_at DESC LIMIT 1;\"")
        sys.exit(1)

