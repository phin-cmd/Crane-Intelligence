#!/usr/bin/env python3
"""
Script to integrate API client into all frontend HTML pages
"""
import os
import re
from pathlib import Path

frontend_dir = Path("/root/Crane-Intelligence/frontend")

# API client script tag to add
api_client_script = '<script src="js/api-client.js"></script>'

# List of HTML files to update
html_files = [
    'homepage.html',
    'dashboard.html',
    'valuation_terminal.html',
    'valuation-terminal.html',
    'valuation-terminal-new.html',
    'market-analysis.html',
    'advanced-analytics.html',
    'add-equipment.html',
    'account-settings.html',
    'login.html',
    'signup.html',
    'export-data.html',
    'generate-report.html',
    'report-generation.html'
]

def integrate_api_client(html_file):
    """Add API client script to HTML file if not already present"""
    file_path = frontend_dir / html_file
    
    if not file_path.exists():
        print(f"Skipping {html_file} - file not found")
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if API client is already included
        if 'api-client.js' in content:
            print(f"✓ {html_file} - API client already included")
            return
        
        # Find the closing body tag or closing html tag
        if '</body>' in content:
            # Add before closing body tag
            content = content.replace('</body>', f'    {api_client_script}\n</body>')
            print(f"✓ {html_file} - Added API client before </body>")
        elif '</html>' in content:
            # Add before closing html tag
            content = content.replace('</html>', f'    {api_client_script}\n</html>')
            print(f"✓ {html_file} - Added API client before </html>")
        else:
            # Append to end of file
            content += f'\n{api_client_script}\n'
            print(f"✓ {html_file} - Appended API client to end of file")
        
        # Write updated content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
    except Exception as e:
        print(f"✗ {html_file} - Error: {str(e)}")

def main():
    print("Integrating API Client into Frontend Pages...")
    print("=" * 60)
    
    for html_file in html_files:
        integrate_api_client(html_file)
    
    print("=" * 60)
    print("Integration complete!")
    
    # Also update the index.html if it exists
    index_path = frontend_dir / 'index.html'
    if index_path.exists():
        integrate_api_client('index.html')

if __name__ == '__main__':
    main()

