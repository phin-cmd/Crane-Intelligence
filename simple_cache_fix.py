#!/usr/bin/env python3
"""
Simple Cache-Busting Script for Crane Intelligence Platform
"""

import subprocess
import time
import os

def run_ssh_command(command):
    """Run SSH command on the server"""
    try:
        result = subprocess.run([
            'ssh', '-o', 'StrictHostKeyChecking=no', 
            'root@159.65.186.73', command
        ], capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def main():
    print("RADICAL CACHE-BUSTING APPROACH")
    print("=" * 50)
    
    timestamp = int(time.time())
    print(f"Timestamp: {timestamp}")
    
    # Step 1: Stop all services
    print("\n1. Stopping all services...")
    commands = [
        "docker-compose down",
        "systemctl stop nginx"
    ]
    
    for cmd in commands:
        success, stdout, stderr = run_ssh_command(cmd)
        if success:
            print(f"OK: {cmd}")
        else:
            print(f"WARN: {cmd}: {stderr}")
    
    # Step 2: Clear all caches
    print("\n2. Clearing all caches...")
    cache_commands = [
        "rm -rf /var/cache/nginx/*",
        "rm -rf /tmp/*",
        "docker system prune -f"
    ]
    
    for cmd in cache_commands:
        success, stdout, stderr = run_ssh_command(cmd)
        if success:
            print("OK: Cache cleared")
        else:
            print(f"WARN: Cache clear: {stderr}")
    
    # Step 3: Create new homepage with timestamp
    print("\n3. Creating new homepage with timestamp...")
    
    homepage_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crane Intelligence - Professional Crane Valuation Platform</title>
    <link rel="stylesheet" href="styles.css?v={timestamp}">
    <style>
        .notification {{
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 5px;
            color: white;
            font-weight: bold;
            z-index: 10000;
            max-width: 300px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .notification.success {{ background-color: #4CAF50; }}
        .notification.error {{ background-color: #f44336; }}
        .notification.info {{ background-color: #2196F3; }}
        .notification.warning {{ background-color: #ff9800; }}
        
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }}
        
        .modal-content {{
            background-color: #fefefe;
            margin: 5% auto;
            padding: 0;
            border: none;
            width: 90%;
            max-width: 400px;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }}
        
        .auth-form {{
            padding: 30px;
        }}
        
        .form-group {{
            margin-bottom: 20px;
        }}
        
        .form-group label {{
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #333;
        }}
        
        .form-group input {{
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            box-sizing: border-box;
        }}
        
        .form-group input:focus {{
            outline: none;
            border-color: #007bff;
        }}
        
        .btn {{
            width: 100%;
            padding: 12px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s;
        }}
        
        .btn:hover {{
            background-color: #0056b3;
        }}
        
        .btn:disabled {{
            background-color: #ccc;
            cursor: not-allowed;
        }}
        
        .auth-buttons {{
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        
        .auth-btn {{
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s;
        }}
        
        .btn-login {{
            background-color: #007bff;
            color: white;
        }}
        
        .btn-login:hover {{
            background-color: #0056b3;
        }}
        
        .btn-register {{
            background-color: #28a745;
            color: white;
        }}
        
        .btn-register:hover {{
            background-color: #1e7e34;
        }}
        
        .btn-logout {{
            background-color: #dc3545;
            color: white;
        }}
        
        .btn-logout:hover {{
            background-color: #c82333;
        }}
        
        .user-profile {{
            display: none;
            align-items: center;
            gap: 15px;
        }}
        
        .user-info {{
            color: #333;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <!-- Notification Container -->
    <div id="notification-container"></div>
    
    <!-- Login Modal -->
    <div id="loginModal" class="modal">
        <div class="modal-content">
            <div class="auth-form">
                <h2 style="text-align: center; margin-bottom: 20px; color: #333;">Login to Crane Intelligence</h2>
                <form id="loginForm">
                    <div class="form-group">
                        <label for="email">Email:</label>
                        <input type="email" id="email" name="email" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Password:</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    <button type="submit" class="btn" id="loginBtn">Login</button>
                </form>
                <p style="text-align: center; margin-top: 15px;">
                    <a href="#" id="closeModal" style="color: #007bff; text-decoration: none;">Close</a>
                </p>
            </div>
        </div>
    </div>

    <header>
        <nav>
            <div class="nav-container">
                <div class="nav-brand">
                    <img src="images/logos/crane-intelligence-logo.svg" alt="Crane Intelligence" class="logo">
                    <span class="brand-text">Crane Intelligence</span>
                </div>
                <div class="nav-links">
                    <a href="#home">Home</a>
                    <a href="#features">Features</a>
                    <a href="#pricing">Pricing</a>
                    <a href="#contact">Contact</a>
                </div>
                <div class="nav-auth" id="navAuth">
                    <div class="auth-buttons" id="authButtons">
                        <button class="auth-btn btn-login" onclick="openLoginModal()">Login</button>
                        <a href="signup.html" class="auth-btn btn-register">Get Started</a>
                    </div>
                    <div class="user-profile" id="userProfile">
                        <span class="user-info" id="userInfo"></span>
                        <button class="auth-btn btn-logout" onclick="auth.logout()">Logout</button>
                    </div>
                </div>
            </div>
        </nav>
    </header>

    <main>
        <section id="home" class="hero">
            <div class="hero-content">
                <h1>Professional Crane Valuation Platform - UPDATED {timestamp}</h1>
                <p>Advanced analytics, real-time market data, and comprehensive equipment valuation for the construction industry.</p>
                <div class="hero-buttons">
                    <button class="btn btn-primary" onclick="openLoginModal()">Launch Terminal</button>
                    <a href="#features" class="btn btn-secondary">Learn More</a>
                </div>
            </div>
        </section>

        <section id="features" class="features">
            <div class="container">
                <h2>Platform Features</h2>
                <div class="features-grid">
                    <div class="feature-card">
                        <h3>Real-Time Market Data</h3>
                        <p>Live market feeds and pricing data for accurate valuations.</p>
                    </div>
                    <div class="feature-card">
                        <h3>Advanced Analytics</h3>
                        <p>Comprehensive reporting and data analysis tools.</p>
                    </div>
                    <div class="feature-card">
                        <h3>Equipment Management</h3>
                        <p>Complete crane inventory and maintenance tracking.</p>
                    </div>
                </div>
            </div>
        </section>
    </main>

    <footer>
        <div class="container">
            <p>&copy; 2024 Crane Intelligence. All rights reserved. Updated: {timestamp}</p>
        </div>
    </footer>

    <!-- Scripts with timestamp -->
    <script src="js/notification-system.js?v={timestamp}"></script>
    <script src="js/auth.js?v={timestamp}"></script>
    <script>
        // Initialize systems
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('Crane Intelligence Platform Loaded - Timestamp: {timestamp}');
            
            // Initialize notification system
            if (typeof window.NotificationSystem !== 'undefined') {{
                window.NotificationSystem.init();
                console.log('Notification System Initialized');
            }}
            
            // Initialize auth system
            if (typeof window.AuthSystem !== 'undefined') {{
                window.auth = new window.AuthSystem();
                console.log('Auth System Initialized');
            }}
            
            // Update UI based on auth status
            updateUserInterface();
        }});
        
        function openLoginModal() {{
            document.getElementById('loginModal').style.display = 'block';
        }}
        
        function closeLoginModal() {{
            document.getElementById('loginModal').style.display = 'none';
        }}
        
        // Close modal when clicking outside
        window.onclick = function(event) {{
            const modal = document.getElementById('loginModal');
            if (event.target === modal) {{
                closeLoginModal();
            }}
        }}
        
        // Close modal handlers
        document.getElementById('closeModal').onclick = closeLoginModal;
        
        // Login form handler
        document.getElementById('loginForm').addEventListener('submit', async function(e) {{
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const loginBtn = document.getElementById('loginBtn');
            
            loginBtn.disabled = true;
            loginBtn.textContent = 'Logging in...';
            
            try {{
                if (window.auth) {{
                    window.NotificationSystem.show('info', 'Loading', 'Signing you in...', 0);
                    const result = await window.auth.login(email, password);
                    
                    if (result.success) {{
                        window.NotificationSystem.show('success', 'Login Successful', 'Welcome back!');
                        closeLoginModal();
                        updateUserInterface();
                    }} else {{
                        window.NotificationSystem.show('error', 'Login Failed', result.error || 'Invalid email or password');
                    }}
                }} else {{
                    window.NotificationSystem.show('error', 'Login Failed', 'Authentication system not available');
                }}
            }} catch (error) {{
                console.error('Login error:', error);
                window.NotificationSystem.show('error', 'Login Failed', 'Invalid email or password');
            }} finally {{
                loginBtn.disabled = false;
                loginBtn.textContent = 'Login';
            }}
        }});
        
        function updateUserInterface() {{
            const user = window.auth ? window.auth.getCurrentUser() : null;
            console.log('updateUserInterface called with user:', user);
            
            const authButtons = document.getElementById('authButtons');
            const userProfile = document.getElementById('userProfile');
            const userInfo = document.getElementById('userInfo');
            
            console.log('Elements found:', {{ authButtons, userProfile, userInfo }});
            
            if (user) {{
                // User is logged in
                authButtons.style.display = 'none';
                userProfile.style.display = 'flex';
                userInfo.textContent = `Welcome, ${{user.email}}`;
                console.log('User logged in, showing profile, hiding auth buttons');
            }} else {{
                // User is not logged in
                authButtons.style.display = 'flex';
                userProfile.style.display = 'none';
                console.log('User not logged in, showing auth buttons, hiding profile');
            }}
            
            // Force style updates
            authButtons.style.visibility = authButtons.style.display === 'flex' ? 'visible' : 'hidden';
            userProfile.style.visibility = userProfile.style.display === 'flex' ? 'visible' : 'hidden';
            
            console.log('Updated inline styles - authButtons:', authButtons.style.display, authButtons.style.visibility);
            console.log('Updated inline styles - userProfile:', userProfile.style.display, userProfile.style.visibility);
        }}
        
        // Make functions globally available
        window.openLoginModal = openLoginModal;
        window.closeLoginModal = closeLoginModal;
        window.updateUserInterface = updateUserInterface;
    </script>
</body>
</html>'''

    # Write the new homepage
    print(f"\n4. Creating new homepage with timestamp {timestamp}...")
    
    # Create the file content as a command
    file_creation_cmd = f'''cat > /var/www/crane-intelligence/frontend/homepage.html << 'EOF'
{homepage_content}
EOF'''
    
    success, stdout, stderr = run_ssh_command(file_creation_cmd)
    if success:
        print("OK: New homepage created with timestamp")
    else:
        print(f"ERROR: Failed to create homepage: {stderr}")
        return
    
    # Step 5: Update Nginx with aggressive cache busting
    print("\n5. Updating Nginx with radical cache busting...")
    
    nginx_config = f'''server {{
    listen 80;
    server_name craneintelligence.tech www.craneintelligence.tech;
    return 301 https://$server_name$request_uri;
}}

server {{
    listen 443 ssl http2;
    server_name craneintelligence.tech www.craneintelligence.tech;

    ssl_certificate /etc/letsencrypt/live/craneintelligence.tech/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/craneintelligence.tech/privkey.pem;

    # RADICAL CACHE BUSTING - Force no caching everywhere
    add_header Cache-Control "no-cache, no-store, must-revalidate, max-age=0, private" always;
    add_header Pragma "no-cache" always;
    add_header Expires "Thu, 01 Jan 1970 00:00:00 GMT" always;
    add_header Last-Modified "Thu, 01 Jan 1970 00:00:00 GMT" always;
    add_header ETag "" always;
    add_header X-Timestamp "{timestamp}" always;

    # Serve frontend
    location / {{
        proxy_pass http://127.0.0.1:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Timestamp "{timestamp}";

        # Disable ALL caching
        proxy_cache_bypass 1;
        proxy_no_cache 1;
        proxy_buffering off;
        proxy_cache off;
        
        # Force fresh content
        proxy_set_header Cache-Control "no-cache, no-store, must-revalidate";
        proxy_set_header Pragma "no-cache";
        proxy_set_header Expires "0";
    }}

    # API endpoints
    location /api/ {{
        proxy_pass http://127.0.0.1:8004;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Timestamp "{timestamp}";
    }}
}}'''
    
    nginx_cmd = f'''cat > /etc/nginx/sites-available/crane-intelligence << 'EOF'
{nginx_config}
EOF'''
    
    success, stdout, stderr = run_ssh_command(nginx_cmd)
    if success:
        print("OK: Nginx configuration updated with radical cache busting")
    else:
        print(f"ERROR: Failed to update Nginx: {stderr}")
        return
    
    # Step 6: Restart services
    print("\n6. Restarting services...")
    
    restart_commands = [
        "nginx -t",
        "systemctl reload nginx",
        "cd /var/www/crane-intelligence && docker-compose up -d"
    ]
    
    for cmd in restart_commands:
        success, stdout, stderr = run_ssh_command(cmd)
        if success:
            print(f"OK: {cmd}")
        else:
            print(f"WARN: {cmd}: {stderr}")
    
    # Step 7: Verify deployment
    print("\n7. Verifying deployment...")
    
    time.sleep(5)  # Wait for services to start
    
    # Test the domain
    test_commands = [
        f"curl -s https://craneintelligence.tech | grep -i '{timestamp}'",
        "curl -s https://craneintelligence.tech | grep -i 'auth.login'",
        "curl -s https://craneintelligence.tech | grep -i 'NotificationSystem'"
    ]
    
    for cmd in test_commands:
        success, stdout, stderr = run_ssh_command(cmd)
        if success and stdout.strip():
            print(f"OK: {cmd}: {stdout.strip()}")
        else:
            print(f"WARN: {cmd}: No output")
    
    print(f"\nRADICAL CACHE-BUSTING COMPLETE!")
    print(f"Timestamp: {timestamp}")
    print(f"Domain: https://craneintelligence.tech")
    print(f"Force refresh your browser (Ctrl+F5 or Cmd+Shift+R)")
    print(f"Try incognito/private mode")

if __name__ == "__main__":
    main()
