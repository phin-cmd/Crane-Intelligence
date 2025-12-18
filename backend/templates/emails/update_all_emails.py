#!/usr/bin/env python3
"""
Script to update all email templates to use brand template
"""
import os
import re
from pathlib import Path

# Standard logo SVG
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

# Standard brand CSS
BRAND_CSS = '''        body {
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

def check_template_status(filepath):
    """Check if template has brand styling and logo"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        has_brand = '#0F0F0F' in content or '#1A1A1A' in content
        has_logo = 'yellowGradient' in content or 'CRANE' in content and 'INTELLIGENCE' in content
        
        return has_brand, has_logo
    except:
        return False, False

# Check all templates
templates_dir = Path('.')
templates = sorted([f for f in templates_dir.glob('*.html') if f.name not in ['_brand_template_base.html', 'base_email_template.html']])

print("Email Template Status:")
print("=" * 60)
needs_update = []
has_brand_no_logo = []

for template in templates:
    has_brand, has_logo = check_template_status(template)
    status = []
    if has_brand:
        status.append("✅ Brand")
    else:
        status.append("❌ No Brand")
        needs_update.append(template.name)
    
    if has_logo:
        status.append("✅ Logo")
    else:
        status.append("❌ No Logo")
        if has_brand:
            has_brand_no_logo.append(template.name)
        else:
            needs_update.append(template.name)
    
    print(f"{template.name:45} {' | '.join(status)}")

print(f"\n📊 Summary:")
print(f"  Templates with brand but no logo: {len(has_brand_no_logo)}")
print(f"  Templates needing complete update: {len(set(needs_update))}")
print(f"  Total templates: {len(templates)}")
