#!/usr/bin/env python3
"""
Populate email_templates table with all email templates from template files
Reads all HTML templates and adds them to the database
"""
import sys
import os
from pathlib import Path
from datetime import datetime
import json
import re

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import SessionLocal
from app.models.admin import EmailTemplate

def extract_variables_from_template(html_content):
    """Extract template variables from HTML content"""
    # Find all {{variable}} patterns
    variables = set(re.findall(r'\{\{(\w+)\}\}', html_content))
    # Also check for {% if variable %} patterns
    jinja_vars = set(re.findall(r'\{%\s*if\s+(\w+)', html_content))
    variables.update(jinja_vars)
    return sorted(list(variables))

def determine_template_type(template_name):
    """Determine template type based on name"""
    if 'admin' in template_name:
        return 'system'
    elif 'fmv_report' in template_name or 'payment' in template_name or 'report' in template_name:
        return 'notification'
    elif 'newsletter' in template_name or 'welcome' in template_name or 'marketing' in template_name:
        return 'marketing'
    elif 'password' in template_name or 'verification' in template_name or 'account' in template_name:
        return 'system'
    else:
        return 'notification'

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

def generate_subject_from_name(template_name):
    """Generate a default subject line from template name"""
    # Convert snake_case to Title Case
    subject = template_name.replace('_', ' ').replace('.html', '').title()
    
    # Special cases
    subject_map = {
        'Fmv Report': 'FMV Report',
        'Fmv': 'FMV',
        'Admin': 'Admin',
    }
    
    for key, value in subject_map.items():
        subject = subject.replace(key, value)
    
    return subject

def read_template_file(template_path):
    """Read template file and return content"""
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"  ❌ Error reading {template_path}: {e}")
        return None

def extract_text_from_html(html_content):
    """Extract plain text version from HTML"""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', html_content)
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text[:500]  # Limit length

def populate_all_templates(db):
    """Populate email_templates table with all templates from files"""
    print("📝 Populating email_templates table from template files...")
    
    # Get template directory
    template_dir = Path(__file__).parent.parent / "templates" / "emails"
    
    if not template_dir.exists():
        print(f"  ❌ Template directory not found: {template_dir}")
        return 0
    
    # Get all HTML template files (exclude base templates and partials)
    exclude_files = [
        '_brand_template_base.html',
        'base_email_template.html',
        'update_all_emails.py'
    ]
    
    template_files = [
        f for f in template_dir.glob("*.html")
        if f.name not in exclude_files
    ]
    
    print(f"  Found {len(template_files)} template files")
    
    count = 0
    skipped = 0
    errors = 0
    
    for template_file in sorted(template_files):
        template_name = template_file.stem  # filename without .html extension
        
        try:
            # Check if template already exists
            existing = db.query(EmailTemplate).filter(
                EmailTemplate.name == template_name
            ).first()
            
            if existing:
                print(f"  ⚠️  Template '{template_name}' already exists, skipping...")
                skipped += 1
                continue
            
            # Read template content
            html_content = read_template_file(template_file)
            if not html_content:
                errors += 1
                continue
            
            # Extract variables
            variables = extract_variables_from_template(html_content)
            
            # Determine template type
            template_type = determine_template_type(template_name)
            
            # Determine target audience
            target_audience = determine_target_audience(template_name, template_type)
            
            # Generate subject
            subject = generate_subject_from_name(template_name)
            
            # Extract text version
            text_content = extract_text_from_html(html_content)
            
            # Create template record
            template_data = {
                "name": template_name,
                "subject": subject,
                "body_html": html_content,
                "body_text": text_content,
                "template_type": template_type,
                "target_audience": target_audience,
                "variables": json.dumps(variables),
                "is_active": True,
                "usage_count": 0
            }
            
            template = EmailTemplate(**template_data)
            db.add(template)
            count += 1
            print(f"  ✅ Added template: {template_name} ({template_type})")
            
        except Exception as e:
            print(f"  ❌ Error processing template '{template_name}': {e}")
            errors += 1
            db.rollback()
            continue
    
    try:
        db.commit()
        print(f"\n  ✅ Successfully added {count} email templates")
        print(f"  ⚠️  Skipped {skipped} existing templates")
        if errors > 0:
            print(f"  ❌ {errors} errors encountered")
        return count
    except Exception as e:
        db.rollback()
        print(f"  ❌ Error committing templates: {e}")
        import traceback
        traceback.print_exc()
        return 0

def main():
    """Main function"""
    print("=" * 60)
    print("Populate All Email Templates")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        template_count = populate_all_templates(db)
        
        print("\n" + "=" * 60)
        print(f"Summary: {template_count} templates added")
        print("=" * 60)
        print("\n✅ Population complete!")
        
    except Exception as e:
        print(f"\n❌ Error during population: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()

