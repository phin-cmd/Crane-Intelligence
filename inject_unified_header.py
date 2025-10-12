#!/usr/bin/env python3
"""
Crane Intelligence - Unified Header Injection Script
Automatically replaces headers in all HTML files with the unified header
"""

import os
import re
from pathlib import Path

# Configuration
FRONTEND_DIR = Path("/root/Crane-Intelligence/frontend")

# Unified Header Template
UNIFIED_HEADER = '''    <!-- Unified Header -->
    <header class="header">
        <div class="header-container">
            <!-- Logo -->
            <div class="logo">
                <a href="/homepage.html" style="text-decoration: none; display: flex; align-items: center;">
                    <img src="/images/logos/crane-intelligence-logo.svg" alt="Crane Intelligence" class="logo-svg">
                </a>
            </div>

            <!-- Navigation Menu (visible on homepage, hidden on other pages when logged in) -->
            <nav class="nav-menu" id="navMenu">
                <a href="/homepage.html#features" class="nav-link">FEATURES</a>
                <a href="/homepage.html#pricing" class="nav-link">PRICING</a>
                <a href="/homepage.html#about" class="nav-link">ABOUT</a>
                <a href="/homepage.html#contact" class="nav-link">CONTACT</a>
            </nav>

            <!-- Right Side: Auth Buttons OR User Profile -->
            <div class="header-right">
                <!-- Login/Signup Buttons (shown when NOT logged in) -->
                <div class="auth-buttons" id="authButtons" style="display: none;">
                    <a href="/login.html" class="auth-btn login">Login</a>
                    <a href="/signup.html" class="auth-btn signup">Sign Up</a>
                </div>

                <!-- User Profile Dropdown (shown when logged in) -->
                <div class="user-profile" id="userProfile" style="display: none;">
                    <div class="user-avatar">
                        <span id="userInitials">U</span>
                    </div>
                    <div class="user-info">
                        <div class="user-name" id="userDisplayName">User Name</div>
                        <div class="user-role" id="userRole">Free User</div>
                    </div>
                    <span class="dropdown-arrow">▼</span>
                    
                    <!-- Dropdown Menu -->
                    <div class="user-dropdown" id="userDropdown">
                        <a href="/dashboard.html" class="dropdown-item">
                            <span class="dropdown-icon">📊</span>
                            Dashboard
                        </a>
                        <a href="/valuation-terminal.html" class="dropdown-item">
                            <span class="dropdown-icon">⚡</span>
                            Valuation Terminal
                        </a>
                        <a href="/account-settings.html" class="dropdown-item">
                            <span class="dropdown-icon">⚙️</span>
                            Account Settings
                        </a>
                        <div class="dropdown-divider"></div>
                        <a href="#" class="dropdown-item" data-action="logout">
                            <span class="dropdown-icon">🚪</span>
                            Logout
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </header>'''

def should_skip_file(file_path):
    """Check if file should be skipped"""
    file_name = file_path.name
    
    # Skip these files
    if file_name in ['index.html', 'unified-header.html']:
        return True
    
    # Skip admin directory
    if 'admin' in str(file_path):
        return True
    
    return False

def inject_header(content, file_name):
    """Replace existing header with unified header"""
    
    # Pattern to match header section (from <header to </header>)
    header_pattern = r'<header[^>]*>.*?</header>'
    
    # Check if header exists
    if not re.search(header_pattern, content, re.DOTALL):
        return content, False
    
    # Replace header
    new_content = re.sub(header_pattern, UNIFIED_HEADER, content, count=1, flags=re.DOTALL)
    
    # Fix image paths for pages not in root
    if 'src="/images/' not in new_content and 'src="images/' in new_content:
        # Keep relative paths as is
        pass
    elif 'src="/images/' not in new_content:
        # Update to absolute paths
        new_content = new_content.replace('src="images/', 'src="/images/')
    
    return new_content, True

def main():
    """Main execution function"""
    print("=" * 60)
    print("Crane Intelligence - Unified Header Injection")
    print("=" * 60)
    print()
    
    # Find all HTML files
    html_files = list(FRONTEND_DIR.glob("**/*.html"))
    print(f"Found {len(html_files)} HTML files\n")
    
    # Track statistics
    injected_count = 0
    skipped_count = 0
    error_count = 0
    no_header_count = 0
    
    print("Processing files...")
    print("-" * 60)
    
    for html_file in html_files:
        file_name = html_file.name
        
        # Skip certain files
        if should_skip_file(html_file):
            print(f"⊘ Skipping: {file_name}")
            skipped_count += 1
            continue
        
        try:
            # Read file content
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Inject unified header
            new_content, was_injected = inject_header(content, file_name)
            
            if was_injected:
                # Write updated content
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"✓ Injected header: {file_name}")
                injected_count += 1
            else:
                print(f"○ No header found: {file_name}")
                no_header_count += 1
                
        except Exception as e:
            print(f"✗ Error processing {file_name}: {e}")
            error_count += 1
    
    # Print summary
    print()
    print("=" * 60)
    print("Injection Complete!")
    print("=" * 60)
    print(f"Total files: {len(html_files)}")
    print(f"Headers injected: {injected_count}")
    print(f"No header found: {no_header_count}")
    print(f"Files skipped: {skipped_count}")
    print(f"Errors: {error_count}")
    print()
    print("All HTML files now have the unified authentication header!")
    print()

if __name__ == "__main__":
    main()

