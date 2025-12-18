#!/usr/bin/env python3
"""
Script to update all email templates to brand standard
"""
import os
import re
from pathlib import Path

# Standard brand template components
LOGO_SVG = '''            <div class="logo-container">
                <!-- Logo as inline SVG for better email client compatibility -->
                <svg width="200" height="40" viewBox="0 0 300 60" xmlns="http://www.w3.org/2000/svg" style="height: 40px; width: auto; max-width: 200px; display: block; margin: 0 auto;">
                    <defs>
                        <linearGradient id="yellowGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                            <stop offset="0%" style="stop-color:#FFD600;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#FF9800;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <rect x="8" y="12" width="6" height="36" fill="url(#yellowGradient)"/>
                    <text x="24" y="28" font-family="Roboto Condensed, Arial, sans-serif" font-size="18" font-weight="700" fill="#FFFFFF" letter-spacing="1px">CRANE</text>
                    <text x="24" y="44" font-family="Roboto Condensed, Arial, sans-serif" font-size="12" font-weight="500" fill="#FFFFFF" letter-spacing="2px" opacity="0.8">INTELLIGENCE</text>
                    <rect x="280" y="28" width="2" height="16" fill="#00FF85"/>
                </svg>
            </div>'''

BRAND_STYLES = '''        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 20px;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }
        .email-wrapper {
            max-width: 600px;
            margin: 0 auto;
            background-color: #0F0F0F;
        }
        .email-header {
            background: linear-gradient(135deg, #1A1A1A 0%, #121212 100%);
            padding: 40px 30px;
            text-align: center;
            border-bottom: 1px solid #333333;
        }
        .logo-container {
            text-align: center;
            margin-bottom: 20px;
        }
        .email-content {
            background-color: #1A1A1A;
            padding: 40px 30px;
            color: #FFFFFF;
        }
        .button-primary {
            display: inline-block;
            background-color: #00FF85;
            color: #0F0F0F;
            padding: 14px 32px;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            font-size: 16px;
            margin: 20px 0;
            text-align: center;
        }
        .button-secondary {
            display: inline-block;
            background-color: #FFD600;
            color: #0F0F0F;
            padding: 14px 32px;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            font-size: 16px;
            margin: 20px 0;
            text-align: center;
        }
        .info-box {
            background-color: rgba(0, 255, 133, 0.1);
            border-left: 4px solid #00FF85;
            padding: 16px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .warning-box {
            background-color: rgba(255, 214, 0, 0.1);
            border-left: 4px solid #FFD600;
            padding: 16px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .alert-box {
            background-color: rgba(255, 68, 68, 0.1);
            border-left: 4px solid #FF4444;
            padding: 16px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .success-box {
            background-color: rgba(0, 255, 133, 0.1);
            border-left: 4px solid #00FF85;
            padding: 16px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .email-footer {
            background-color: #121212;
            padding: 30px;
            text-align: center;
            border-top: 1px solid #333333;
            color: #B0B0B0;
            font-size: 12px;
        }
        h1, h2, h3 {
            font-family: 'Roboto Condensed', 'Inter', sans-serif;
            font-weight: 600;
            color: #FFFFFF;
            margin-top: 0;
        }
        h1 { font-size: 28px; }
        h2 { font-size: 24px; }
        h3 { font-size: 20px; }
        p {
            color: #B0B0B0;
            line-height: 1.6;
            margin: 16px 0;
        }
        ul {
            color: #B0B0B0;
            line-height: 1.8;
        }
        @media only screen and (max-width: 600px) {
            .email-content { padding: 30px 20px; }
            .email-header { padding: 30px 20px; }
        }'''

STANDARD_FOOTER = '''        <div class="email-footer">
            <p style="margin: 0 0 10px 0;">
                <strong style="color: #FFFFFF;">Crane Intelligence</strong><br>
                Professional Crane Valuation & Market Intelligence
            </p>
            <p style="margin: 10px 0; color: #808080; font-size: 11px;">
                © 2024 {{ platform_name|default('Crane Intelligence') }}. All rights reserved.
            </p>
            <p style="margin: 10px 0; color: #808080; font-size: 11px;">
                This email was sent to {{ user_email|default('your email') }}.
            </p>
        </div>'''

def extract_content_from_old_template(filepath):
    """Extract content from old template"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title
        title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
        title = title_match.group(1) if title_match else "Crane Intelligence"
        
        # Extract header text
        header_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
        header_text = re.sub(r'<[^>]+>', '', header_match.group(1) if header_match else "").strip()
        
        # Extract body content (between content/container divs)
        body_match = re.search(r'<div[^>]*class=["\'](?:content|email-content|container)[^>]*>(.*?)</div>\s*</div>\s*<div[^>]*class=["\']footer', content, re.IGNORECASE | re.DOTALL)
        if not body_match:
            body_match = re.search(r'<div[^>]*class=["\']content[^>]*>(.*?)</div>', content, re.IGNORECASE | re.DOTALL)
        
        body_content = body_match.group(1) if body_match else ""
        
        return title, header_text, body_content
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None, None, None

def create_brand_template(title, header_text, body_content, template_name):
    """Create brand-compliant template"""
    # Clean up header text
    header_text = re.sub(r'[⚙️📊💰🔐🛡️📋📧✅❌⚠️]', '', header_text).strip()
    if not header_text:
        header_text = title.replace(' - Crane Intelligence', '').replace('Crane Intelligence', '').strip()
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
{BRAND_STYLES}
    </style>
</head>
<body>
    <div class="email-wrapper">
        <div class="email-header">
{LOGO_SVG}
            <h1 style="color: #FFFFFF; margin: 0;">{header_text}</h1>
        </div>
        
        <div class="email-content">
{body_content}
        </div>
        
{STANDARD_FOOTER}
    </div>
</body>
</html>'''

# Templates that need updating
templates_to_update = [
    'fmv_report_in_progress.html',
    'fmv_report_in_review.html',
    'fmv_report_payment_pending.html',
    'fmv_report_cancelled.html',
    'fmv_report_completed.html',
    'profile_updated.html',
    'subscription_changed.html',
    'subscription_payment_failed.html',
    'subscription_payment_success.html',
    'notification_preferences_updated.html',
    'notification_system_maintenance.html',
    'account_deleted.html',
    'account_deletion_request.html',
    'equipment_inspection.html',
    'valuation_report.html',
    'welcome.html',
    'notification.html',
    'notification_general.html'
]

templates_dir = Path('/root/crane/backend/templates/emails')
updated_count = 0

print("Updating email templates to brand standard...")
print("=" * 60)

for template_name in templates_to_update:
    template_path = templates_dir / template_name
    if not template_path.exists():
        print(f"⚠️  {template_name} not found, skipping")
        continue
    
    try:
        title, header_text, body_content = extract_content_from_old_template(template_path)
        if not body_content:
            print(f"⚠️  Could not extract content from {template_name}, skipping")
            continue
        
        # Create new template
        new_template = create_brand_template(title, header_text, body_content, template_name)
        
        # Backup old template
        backup_path = template_path.with_suffix('.html.old')
        if not backup_path.exists():
            template_path.rename(backup_path)
        
        # Write new template
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(new_template)
        
        print(f"✅ Updated: {template_name}")
        updated_count += 1
    except Exception as e:
        print(f"❌ Error updating {template_name}: {e}")

print(f"\n✅ Updated {updated_count} templates")
print(f"📁 Backup files saved with .old extension")

