#!/usr/bin/env python3
"""
Fix all pages to use unified authentication properly
Removes old updateUserInterface calls and ensures unified-auth.js is used
"""

import os
import re
from pathlib import Path

FRONTEND_DIR = Path("/root/Crane-Intelligence/frontend")

def fix_page_auth(file_path):
    """Fix authentication code in a single page"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        modified = False
        
        # Pattern 1: Remove updateUserInterface with hardcoded data
        pattern1 = r"updateUserInterface\(\s*\{\s*full_name:\s*['\"]John Doe['\"].*?\}\s*\);"
        if re.search(pattern1, content):
            content = re.sub(pattern1, "// Removed hardcoded user data - using unified auth", content)
            modified = True
            print(f"  - Removed hardcoded 'John Doe' data")
        
        # Pattern 2: Remove updateUserInterface(user) calls in DOMContentLoaded
        # But keep the ones that are actually fetching from API
        pattern2 = r"(document\.addEventListener\(['\"]DOMContentLoaded['\"],\s*(?:async\s+)?function\(\)\s*\{[^}]*?)updateUserInterface\(user\);([^}]*\}\);)"
        matches = re.finditer(pattern2, content, re.DOTALL)
        for match in matches:
            # Check if this block has API calls or localStorage checks
            block = match.group(0)
            if 'localStorage.getItem' in block or 'fetch(' in block:
                # This is trying to get real user data, replace with unified auth
                replacement = match.group(1) + "if(window.unifiedAuth){await window.unifiedAuth.initialize();}" + match.group(2)
                content = content.replace(match.group(0), replacement)
                modified = True
                print(f"  - Replaced updateUserInterface with unified auth init")
        
        # Pattern 3: Remove updateUserInterface(null) calls
        pattern3 = r"updateUserInterface\(null\);\s*//\s*Show auth buttons for guest users"
        if re.search(pattern3, content):
            content = re.sub(pattern3, "// Unified auth handles guest users automatically", content)
            modified = True
            print(f"  - Removed updateUserInterface(null) calls")
        
        # Pattern 4: Ensure DOMContentLoaded initializes unified auth
        # Look for DOMContentLoaded without unified auth initialization
        pattern4 = r"(document\.addEventListener\(['\"]DOMContentLoaded['\"],\s*function\(\)\s*\{(?:(?!window\.unifiedAuth\.initialize).)*?\}\);)"
        
        # Write back if modified
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    """Main execution"""
    print("=" * 70)
    print("Fixing Authentication on All Pages")
    print("=" * 70)
    print()
    
    # List of pages to fix
    pages_to_fix = [
        'add-equipment.html',
        'valuation_terminal.html',
        'valuation-terminal.html',
        'privacy-policy.html',
        'terms-of-service.html',
        'cookie-policy.html',
        'about-us.html',
        'contact.html',
        'blog.html',
        'security.html',
        'account-settings.html',
        'market-analysis.html',
        'advanced-analytics.html',
        'report-generation.html',
        'generate-report.html',
        'schedule-inspection.html',
        'export-data.html',
        'reset-password.html',
        'signup.html',
        'login.html'
    ]
    
    fixed_count = 0
    skipped_count = 0
    
    for page in pages_to_fix:
        file_path = FRONTEND_DIR / page
        
        if not file_path.exists():
            print(f"⊘ {page} - File not found")
            skipped_count += 1
            continue
        
        print(f"→ Processing: {page}")
        
        if fix_page_auth(file_path):
            print(f"✓ {page} - Fixed")
            fixed_count += 1
        else:
            print(f"○ {page} - No changes needed")
            skipped_count += 1
        
        print()
    
    print("=" * 70)
    print(f"Complete! Fixed: {fixed_count} | Skipped: {skipped_count}")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Test on a few pages to verify")
    print("2. Clear browser cache")
    print("3. Check that user profile shows real data after login")

if __name__ == "__main__":
    main()

