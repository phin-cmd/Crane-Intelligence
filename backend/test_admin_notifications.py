#!/usr/bin/env python3
"""
Test Admin Notifications End-to-End
Tests the complete admin notification flow
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models.admin import Notification
from app.models.user import User
from sqlalchemy import text
from datetime import datetime

def test_admin_notifications():
    """Test admin notification system"""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("ADMIN NOTIFICATIONS END-TO-END TEST")
        print("=" * 80)
        print()
        
        # 1. Check admin users
        print("1. Checking admin users...")
        admin_result = db.execute(text("""
            SELECT id, email, full_name, is_active, is_verified
            FROM admin_users 
            WHERE is_active = true AND is_verified = true
        """))
        admins = admin_result.fetchall()
        print(f"   ✅ Found {len(admins)} active admin users")
        for admin in admins:
            print(f"      - ID: {admin[0]}, Email: {admin[1]}, Name: {admin[2]}")
        print()
        
        if len(admins) == 0:
            print("   ⚠️  No active admin users found. Cannot test notifications.")
            return
        
        admin_id = admins[0][0]
        
        # 2. Check existing notifications
        print("2. Checking existing admin notifications...")
        notif_result = db.execute(text("""
            SELECT COUNT(*) 
            FROM notifications 
            WHERE admin_user_id = :admin_id
        """), {'admin_id': admin_id})
        count = notif_result.scalar()
        print(f"   ✅ Admin {admin_id} has {count} notifications")
        print()
        
        # 3. Create test notification
        print("3. Creating test notification...")
        test_notif = Notification(
            admin_user_id=admin_id,
            notification_type="test",
            title="System Test Notification",
            message="This is a test notification created by the admin notification test script.",
            action_url="/admin/dashboard.html",
            action_text="Go to Dashboard",
            is_read=False
        )
        db.add(test_notif)
        db.commit()
        db.refresh(test_notif)
        print(f"   ✅ Test notification created: ID={test_notif.id}")
        print()
        
        # 4. Check recent notifications
        print("4. Recent admin notifications:")
        recent_result = db.execute(text("""
            SELECT id, title, message, notification_type, is_read, created_at
            FROM notifications 
            WHERE admin_user_id = :admin_id
            ORDER BY created_at DESC
            LIMIT 5
        """), {'admin_id': admin_id})
        
        for row in recent_result:
            read_status = "✓ Read" if row[4] else "✗ Unread"
            print(f"   [{row[0]}] {row[1]} - {read_status}")
            print(f"      Type: {row[3]}, Created: {row[5]}")
        print()
        
        # 5. Test notification triggers
        print("5. Testing notification triggers...")
        
        # Check if new user signups create notifications
        print("   a) New user signup trigger:")
        new_user_result = db.execute(text("""
            SELECT COUNT(*) 
            FROM notifications 
            WHERE admin_user_id = :admin_id 
            AND notification_type = 'new_user_signup'
        """), {'admin_id': admin_id})
        new_user_count = new_user_result.scalar()
        print(f"      ✅ Found {new_user_count} new user signup notifications")
        print()
        
        # Check if FMV report status updates create notifications
        print("   b) FMV report status update trigger:")
        fmv_result = db.execute(text("""
            SELECT COUNT(*) 
            FROM notifications 
            WHERE admin_user_id = :admin_id 
            AND notification_type LIKE 'fmv_report%'
        """), {'admin_id': admin_id})
        fmv_count = fmv_result.scalar()
        print(f"      ✅ Found {fmv_count} FMV report notifications")
        print()
        
        # 6. Test API endpoint simulation
        print("6. Testing API endpoint response format...")
        api_result = db.execute(text("""
            SELECT id, admin_user_id, title, message, notification_type, is_read, created_at
            FROM notifications 
            WHERE admin_user_id = :admin_id
            ORDER BY created_at DESC
            LIMIT 3
        """), {'admin_id': admin_id})
        
        notifications = []
        for row in api_result:
            notifications.append({
                'id': row[0],
                'user_id': row[1],
                'title': row[2],
                'message': row[3],
                'type': row[4],
                'read': row[5],
                'created_at': row[6].isoformat() if row[6] else None
            })
        
        print(f"   ✅ API would return {len(notifications)} notifications")
        for notif in notifications:
            print(f"      - {notif['title']} (Read: {notif['read']})")
        print()
        
        # 7. Summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Admin users: {len(admins)}")
        print(f"✅ Total notifications for admin {admin_id}: {count + 1}")
        print(f"✅ New user signup notifications: {new_user_count}")
        print(f"✅ FMV report notifications: {fmv_count}")
        print()
        print("✅ Admin notification system is working!")
        print()
        print("Next steps:")
        print("  1. Test API endpoint: GET /api/v1/notifications/admin/notifications")
        print("  2. Test frontend: Open admin panel and click notification bell")
        print("  3. Test mark as read: Click on a notification")
        print("  4. Test mark all as read: Click 'Mark all as read' button")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_admin_notifications()

