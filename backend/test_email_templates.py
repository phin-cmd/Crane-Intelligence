#!/usr/bin/env python3
"""
Test script to verify email templates follow brand guidelines
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.services.email_template_service import EmailTemplateService

def test_newsletter_template():
    """Test newsletter welcome email template"""
    print("Testing Newsletter Welcome Email Template...")
    html = EmailTemplateService.newsletter_welcome('test@example.com', 'John')
    
    checks = {
        'Contains logo': 'crane-intelligence-logo' in html,
        'Has brand green (#00FF85)': '#00FF85' in html,
        'Has brand black (#0F0F0F)': '#0F0F0F' in html,
        'Has company name': 'Crane Intelligence' in html,
        'Has footer info': 'Professional Crane Valuation' in html,
        'Has unsubscribe info': 'Unsubscribe' in html,
        'Has proper structure': '<!DOCTYPE html>' in html and '</html>' in html,
        'Has email header': 'email-header' in html,
        'Has email content': 'email-content' in html,
        'Has email footer': 'email-footer' in html
    }
    
    print("\nNewsletter Template Checks:")
    all_passed = True
    for check, result in checks.items():
        status = '✓ PASS' if result else '✗ FAIL'
        print(f"  {status}: {check}")
        if not result:
            all_passed = False
    
    print(f"\nTemplate length: {len(html)} characters")
    return all_passed

def test_consultation_template():
    """Test consultation confirmation email template"""
    print("\n\nTesting Consultation Confirmation Email Template...")
    html = EmailTemplateService.consultation_user_confirmation(
        name='Test User',
        email='test@example.com',
        company='Test Company',
        subject=None,
        message='Test message',
        consultation_id=1,
        created_at='January 1, 2025 at 12:00 PM',
        is_contact_request=False
    )
    
    checks = {
        'Contains logo': 'crane-intelligence-logo' in html,
        'Has brand green (#00FF85)': '#00FF85' in html,
        'Has brand black (#0F0F0F)': '#0F0F0F' in html,
        'Has company name': 'Crane Intelligence' in html,
        'Has footer info': 'Professional Crane Valuation' in html,
        'Has proper structure': '<!DOCTYPE html>' in html and '</html>' in html,
        'Has email header': 'email-header' in html,
        'Has email content': 'email-content' in html,
        'Has email footer': 'email-footer' in html,
        'Has consultation title': 'Thank You for Your Consultation Request' in html,
        'Has request ID': 'Request ID' in html
    }
    
    print("\nConsultation Template Checks:")
    all_passed = True
    for check, result in checks.items():
        status = '✓ PASS' if result else '✗ FAIL'
        print(f"  {status}: {check}")
        if not result:
            all_passed = False
    
    print(f"\nTemplate length: {len(html)} characters")
    return all_passed

if __name__ == '__main__':
    print("=" * 60)
    print("Email Template Brand Guidelines Test")
    print("=" * 60)
    
    newsletter_ok = test_newsletter_template()
    consultation_ok = test_consultation_template()
    
    print("\n" + "=" * 60)
    if newsletter_ok and consultation_ok:
        print("✓ ALL TESTS PASSED - Templates follow brand guidelines")
    else:
        print("✗ SOME TESTS FAILED - Templates need review")
    print("=" * 60)

