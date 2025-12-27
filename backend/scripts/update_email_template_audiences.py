#!/usr/bin/env python3
"""
Update target_audience for all email templates based on template name and type
"""
import sys
import os
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import SessionLocal
from app.models.admin import EmailTemplate

def determine_target_audience(template_name, template_type):
    """Determine target audience based on template name and type"""
    name_lower = template_name.lower()
    
    # Admin templates are for admin users
    if 'admin_' in name_lower:
        return 'admin'
    
    # Guest-specific templates (if any)
    if 'guest' in name_lower:
        return 'guest'
    
    # User-specific templates (most common)
    if any(keyword in name_lower for keyword in [
        'fmv_report', 'payment', 'password', 'email_verification', 
        'email_changed', 'account_', 'profile_', 'subscription_',
        'user_registration', 'welcome', 'notification', 'valuation'
    ]):
        return 'user'
    
    # Marketing/newsletter can be for all or users
    if 'newsletter' in name_lower or 'marketing' in name_lower:
        return 'all'
    
    # Default to 'user' for most templates
    return 'user'

def update_audiences(db):
    """Update target_audience for all templates"""
    print("📝 Updating target_audience for email templates...")
    
    templates = db.query(EmailTemplate).all()
    updated = 0
    
    for template in templates:
        new_audience = determine_target_audience(template.name, template.template_type)
        
        if template.target_audience != new_audience:
            old_audience = template.target_audience or 'NULL'
            template.target_audience = new_audience
            updated += 1
            print(f"  ✅ {template.name:40s} {old_audience:10s} → {new_audience}")
        else:
            print(f"  ⏭️  {template.name:40s} {template.target_audience:10s} (no change)")
    
    try:
        db.commit()
        print(f"\n  ✅ Successfully updated {updated} templates")
        return updated
    except Exception as e:
        db.rollback()
        print(f"  ❌ Error updating templates: {e}")
        import traceback
        traceback.print_exc()
        return 0

def main():
    """Main function"""
    print("=" * 60)
    print("Update Email Template Target Audiences")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        updated_count = update_audiences(db)
        
        print("\n" + "=" * 60)
        print(f"Summary: {updated_count} templates updated")
        print("=" * 60)
        
        # Show summary by audience
        from collections import Counter
        audiences = Counter(t.target_audience for t in db.query(EmailTemplate).all())
        print("\nTemplates by target audience:")
        for audience, count in sorted(audiences.items()):
            print(f"  {audience or 'NULL':10s}: {count:2d}")
        
        print("\n✅ Update complete!")
        
    except Exception as e:
        print(f"\n❌ Error during update: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()

