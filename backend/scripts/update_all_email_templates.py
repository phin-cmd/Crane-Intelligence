#!/usr/bin/env python3
"""
Script to update all email templates with:
1. Inline SVG logo instead of external URL
2. Use first_name for greeting instead of username
3. Consistent branding
"""
import os
import re
from pathlib import Path

# Logo SVG (inline version)
LOGO_SVG = '''<!-- Logo as inline SVG for better email client compatibility -->
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
                </svg>'''

def update_template(file_path):
    """Update a single email template"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = []
        
        # 1. Replace external logo URL with inline SVG
        if 'craneintelligence.tech/images/logos' in content or 'logo-img' in content:
            # Find and replace logo img tags
            # Pattern for img tag with logo URL
            logo_pattern = r'<img[^>]*src=["\']https?://[^"\']*logo[^"\']*["\'][^>]*>'
            if re.search(logo_pattern, content, re.IGNORECASE):
                content = re.sub(logo_pattern, LOGO_SVG, content, flags=re.IGNORECASE)
                changes_made.append("Logo replaced with inline SVG")
            # Also check for logo-container divs
            if '<div class="logo-container">' in content and LOGO_SVG not in content:
                # Find logo-container and add SVG if missing
                logo_container_pattern = r'(<div[^>]*class=["\']logo-container["\'][^>]*>)(.*?)(</div>)'
                if re.search(logo_container_pattern, content, re.DOTALL):
                    content = re.sub(
                        logo_container_pattern,
                        r'\1\n                ' + LOGO_SVG + r'\n            \3',
                        content,
                        flags=re.DOTALL
                    )
                    changes_made.append("Added inline SVG logo to container")
        
        # 2. Replace username with first_name in greetings
        # Pattern: Hello {{ username }}! or Hello {{username}}!
        username_patterns = [
            (r'Hello\s+{{\s*username\s*}}!', 'Hello {{ first_name }}!'),
            (r'Hello\s+{{\s*username\s*}}', 'Hello {{ first_name }}'),
            (r'<h2>Hello\s+{{\s*username\s*}}!</h2>', '<h2>Hello {{ first_name }}!</h2>'),
            (r'<h2>Hello\s+{{\s*username\s*}}</h2>', '<h2>Hello {{ first_name }}</h2>'),
        ]
        for pattern, replacement in username_patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                changes_made.append("Changed username to first_name in greeting")
        
        # 3. Update expiration times from 7 days to 24 hours where applicable
        if 'expiry_days' in content or 'expires in' in content.lower():
            # Replace "7 days" with "24 hours" in expiration messages
            content = re.sub(r'(\d+)\s*days?', lambda m: '24 hours' if m.group(1) == '7' else m.group(0), content, flags=re.IGNORECASE)
            if '7 days' in content or '7 days' in original_content:
                changes_made.append("Updated expiration from 7 days to 24 hours")
        
        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, changes_made
        return False, []
    
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False, [str(e)]

def main():
    templates_dir = Path(__file__).parent.parent / "templates" / "emails"
    
    if not templates_dir.exists():
        print(f"Templates directory not found: {templates_dir}")
        return
    
    templates = list(templates_dir.glob("*.html"))
    print(f"Found {len(templates)} email templates\n")
    
    updated_count = 0
    for template in sorted(templates):
        if template.name == "base_email_template.html":
            continue  # Skip base template
        
        updated, changes = update_template(template)
        if updated:
            updated_count += 1
            print(f"✅ {template.name}")
            for change in changes:
                print(f"   - {change}")
        else:
            print(f"⏭️  {template.name} (no changes needed)")
    
    print(f"\n✅ Updated {updated_count} out of {len(templates)} templates")

if __name__ == "__main__":
    main()

