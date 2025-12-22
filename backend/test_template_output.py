#!/usr/bin/env python3
"""Test email template output"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

try:
    from app.services.email_template_service import EmailTemplateService
    
    # Test newsletter
    print("=" * 70)
    print("NEWSLETTER TEMPLATE TEST")
    print("=" * 70)
    newsletter_html = EmailTemplateService.newsletter_welcome('test@example.com', 'John')
    
    checks = {
        'Has DOCTYPE': '<!DOCTYPE html>' in newsletter_html,
        'Has logo image tag': '<img' in newsletter_html and 'crane-intelligence-logo' in newsletter_html,
        'Has logo URL': 'images/logos/crane-intelligence-logo-white.svg' in newsletter_html,
        'Has brand green': '#00FF85' in newsletter_html,
        'Has brand black': '#0F0F0F' in newsletter_html,
        'Has email-header class': 'email-header' in newsletter_html,
        'Has email-content class': 'email-content' in newsletter_html,
        'Has email-footer class': 'email-footer' in newsletter_html,
        'Has company name': 'Crane Intelligence' in newsletter_html,
    }
    
    for check, result in checks.items():
        print(f"{'✓' if result else '✗'} {check}: {result}")
    
    print(f"\nTemplate length: {len(newsletter_html)} characters")
    
    # Show logo section
    if 'logo-container' in newsletter_html:
        start = newsletter_html.find('logo-container')
        end = newsletter_html.find('</div>', start) + 6
        print(f"\nLogo section:\n{newsletter_html[start:end]}")
    
    # Test consultation
    print("\n" + "=" * 70)
    print("CONSULTATION TEMPLATE TEST")
    print("=" * 70)
    consultation_html = EmailTemplateService.consultation_user_confirmation(
        name='Test User',
        email='test@example.com',
        company='Test Company',
        subject=None,
        message='Test message',
        consultation_id=1,
        created_at='January 1, 2025 at 12:00 PM',
        is_contact_request=False
    )
    
    checks2 = {
        'Has DOCTYPE': '<!DOCTYPE html>' in consultation_html,
        'Has logo image tag': '<img' in consultation_html and 'crane-intelligence-logo' in consultation_html,
        'Has logo URL': 'images/logos/crane-intelligence-logo-white.svg' in consultation_html,
        'Has brand green': '#00FF85' in consultation_html,
        'Has brand black': '#0F0F0F' in consultation_html,
        'Has email-header class': 'email-header' in consultation_html,
        'Has email-content class': 'email-content' in consultation_html,
        'Has email-footer class': 'email-footer' in consultation_html,
    }
    
    for check, result in checks2.items():
        print(f"{'✓' if result else '✗'} {check}: {result}")
    
    print(f"\nTemplate length: {len(consultation_html)} characters")
    
    # Show logo section
    if 'logo-container' in consultation_html:
        start = consultation_html.find('logo-container')
        end = consultation_html.find('</div>', start) + 6
        print(f"\nLogo section:\n{consultation_html[start:end]}")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

