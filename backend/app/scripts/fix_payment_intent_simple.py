#!/usr/bin/env python3
"""
Fix payment intent using direct SQL (no SQLAlchemy required)
Usage: python3 fix_payment_intent_simple.py pi_3Se8b1BME5ZRi6sp1lMYfUJa kankanamitra01@gmail.com
"""
import sys
import os
import subprocess
from datetime import datetime

def run_sql_command(sql_command, description):
    """Run a SQL command using psql"""
    database_url = os.getenv("DATABASE_URL", "postgresql://crane_user:crane_password@129.212.177.131:5432/crane_intelligence")
    
    # Parse database URL
    # Format: postgresql://user:password@host:port/database
    parts = database_url.replace("postgresql://", "").split("@")
    if len(parts) != 2:
        print(f"❌ Invalid DATABASE_URL format")
        return None
    
    user_pass = parts[0].split(":")
    host_db = parts[1].split("/")
    host_port = host_db[0].split(":")
    
    user = user_pass[0]
    password = user_pass[1] if len(user_pass) > 1 else ""
    host = host_port[0]
    port = host_port[1] if len(host_port) > 1 else "5432"
    database = host_db[1] if len(host_db) > 1 else "crane_intelligence"
    
    # Set PGPASSWORD environment variable
    env = os.environ.copy()
    env['PGPASSWORD'] = password
    
    # Run psql command
    cmd = [
        'psql',
        '-h', host,
        '-p', port,
        '-U', user,
        '-d', database,
        '-t',  # Tuples only
        '-A',  # Unaligned output
        '-c', sql_command
    ]
    
    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running SQL: {e.stderr}")
        return None
    except FileNotFoundError:
        print(f"❌ psql not found. Please install postgresql-client or use Python API approach")
        return None

def fix_payment_intent(payment_intent_id: str, user_email: str):
    """Fix a payment intent that succeeded but report wasn't created"""
    print(f"Looking up user: {user_email}")
    
    # Find user by email
    user_sql = f"SELECT id, email, full_name FROM users WHERE email = '{user_email}';"
    user_result = run_sql_command(user_sql, "Find user")
    
    if not user_result:
        print(f"❌ User not found: {user_email}")
        return False
    
    user_id = user_result.split('|')[0].strip()
    print(f"✅ Found user: {user_id} - {user_email}")
    
    # Check if report already exists for this payment intent
    check_sql = f"SELECT id, status, payment_status, amount_paid FROM fmv_reports WHERE payment_intent_id = '{payment_intent_id}';"
    existing = run_sql_command(check_sql, "Check existing report")
    
    if existing and existing.strip():
        report_id = existing.split('|')[0].strip()
        status = existing.split('|')[1].strip() if len(existing.split('|')) > 1 else ""
        print(f"✅ Report already exists: {report_id}")
        print(f"   Status: {status}")
        
        # If payment not marked, mark it
        if "succeeded" not in existing:
            amount = 495.00  # Default amount
            update_sql = f"""
                UPDATE fmv_reports 
                SET payment_status = 'succeeded',
                    amount_paid = {amount},
                    status = 'submitted',
                    submitted_at = NOW(),
                    paid_at = NOW()
                WHERE id = {report_id};
            """
            run_sql_command(update_sql, "Mark payment received")
            print(f"✅ Payment marked as received for report {report_id}")
        return True
    
    # Find most recent draft report for this user
    draft_sql = f"""
        SELECT id, created_at, amount_paid 
        FROM fmv_reports 
        WHERE user_id = {user_id} AND status = 'draft' 
        ORDER BY created_at DESC 
        LIMIT 1;
    """
    draft_result = run_sql_command(draft_sql, "Find draft report")
    
    if draft_result and draft_result.strip():
        report_id = draft_result.split('|')[0].strip()
        created_at = draft_result.split('|')[1].strip() if len(draft_result.split('|')) > 1 else ""
        amount = draft_result.split('|')[2].strip() if len(draft_result.split('|')) > 2 else "495.00"
        
        try:
            amount = float(amount) if amount else 495.00
        except:
            amount = 495.00
        
        print(f"✅ Found draft report: {report_id}")
        print(f"   Created: {created_at}")
        
        # Associate payment intent and mark payment received
        update_sql = f"""
            UPDATE fmv_reports 
            SET payment_intent_id = '{payment_intent_id}',
                payment_status = 'succeeded',
                amount_paid = {amount},
                status = 'submitted',
                submitted_at = NOW(),
                paid_at = NOW()
            WHERE id = {report_id};
        """
        run_sql_command(update_sql, "Associate payment and mark received")
        
        print(f"✅ Payment marked as received for report {report_id}")
        print(f"   Payment Intent ID: {payment_intent_id}")
        print(f"   Amount Paid: ${amount}")
        print(f"   Status: submitted")
        return True
    else:
        print(f"❌ No draft report found for user {user_id}")
        print("   Cannot automatically fix - report needs to be created manually")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 fix_payment_intent_simple.py <payment_intent_id> <user_email>")
        print("Example: python3 fix_payment_intent_simple.py pi_3Se8b1BME5ZRi6sp1lMYfUJa kankanamitra01@gmail.com")
        sys.exit(1)
    
    payment_intent_id = sys.argv[1]
    user_email = sys.argv[2]
    
    print("="*70)
    print("Fixing Payment Intent (Simple SQL Version)")
    print("="*70)
    print(f"Payment Intent ID: {payment_intent_id}")
    print(f"User Email: {user_email}")
    print("="*70)
    print()
    
    success = fix_payment_intent(payment_intent_id, user_email)
    
    if success:
        print("\n✅ Payment intent fixed successfully!")
    else:
        print("\n❌ Failed to fix payment intent")
        sys.exit(1)

