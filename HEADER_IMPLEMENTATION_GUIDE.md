# Unified Header and Authentication Implementation Guide

## Overview
This guide explains how to implement the unified header and authentication system across all pages of the Crane Intelligence website.

## Quick Start

### Step 1: Include Required Files in HTML Head
Add these lines in the `<head>` section of every HTML page:

```html
<head>
    <!-- ... other meta tags ... -->
    
    <!-- Unified Header CSS -->
    <link rel="stylesheet" href="/css/unified-header.css">
    
    <!-- Unified Authentication Script -->
    <script src="/js/unified-auth.js" defer></script>
    
    <!-- ... other scripts ... -->
</head>
```

### Step 2: Add the Header Component
Replace any existing header with this structure in the `<body>`:

```html
<body>
    <!-- Unified Header -->
    <header class="header">
        <div class="header-container">
            <!-- Logo -->
            <div class="logo">
                <a href="/homepage.html" style="text-decoration: none; display: flex; align-items: center;">
                    <img src="/images/logos/crane-intelligence-logo.svg" alt="Crane Intelligence" class="logo-svg">
                </a>
            </div>

            <!-- Navigation Menu (Optional: show/hide based on page) -->
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
    </header>

    <!-- Your page content here -->
</body>
```

## Authentication Features

### Automatic Initialization
The unified authentication system initializes automatically on page load. It will:
1. Check if the user is logged in
2. Validate the authentication token
3. Show/hide the appropriate UI elements (login buttons or user profile)
4. Update user information in the header

### Manual Control (Optional)
If you need to manually control authentication:

```javascript
// Check if user is logged in
const isLoggedIn = await window.unifiedAuth.initialize();

// Get current user data
const user = window.unifiedAuth.getCurrentUser();

// Logout programmatically
await window.unifiedAuth.logout();

// Login programmatically
const result = await window.unifiedAuth.login(email, password);
```

## Page-Specific Customization

### Homepage
- Show navigation menu
- Show login/signup buttons when not logged in
- Show user profile when logged in

### Dashboard & App Pages
- Hide navigation menu (already logged in)
- Show user profile dropdown
- Redirect to homepage if not logged in (optional)

### Login/Signup Pages
- Hide both auth buttons and user profile
- Show custom login/signup forms

## Protected Pages

To make a page require authentication:

```javascript
// Add at the top of your page-specific JavaScript
document.addEventListener('DOMContentLoaded', async function() {
    const isLoggedIn = await window.unifiedAuth.checkAuthStatus();
    
    if (!isLoggedIn) {
        // Redirect to login page
        window.location.href = '/login.html?redirect=' + encodeURIComponent(window.location.pathname);
    }
});
```

## Login/Signup Integration

### Login Form Example

```html
<form id="loginForm">
    <input type="email" id="email" required>
    <input type="password" id="password" required>
    <button type="submit">Login</button>
</form>

<script>
document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    const result = await window.unifiedAuth.login(email, password);
    
    if (result.success) {
        // Redirect to dashboard or redirect URL
        const urlParams = new URLSearchParams(window.location.search);
        const redirect = urlParams.get('redirect') || '/dashboard.html';
        window.location.href = redirect;
    } else {
        // Show error message
        alert(result.error);
    }
});
</script>
```

## Styling Notes

- The unified header uses the existing `unified-header.css` file
- Responsive design is built-in (desktop, tablet, mobile)
- User avatar has a green gradient background
- Dropdown menu has hover effects
- All colors match the Crane Intelligence brand

## API Endpoints Used

The authentication system uses these backend API endpoints:
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/logout` - User logout
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user info
- `GET /api/v1/auth/profile` - Get user profile (alias for /me)

## Token Storage

Authentication tokens are stored in localStorage:
- `access_token` - JWT access token
- `refresh_token` - JWT refresh token
- `user_data` - User profile information (JSON)

## Troubleshooting

### User profile not showing after login
1. Check if tokens are stored in localStorage
2. Verify the API endpoint returns user data
3. Check browser console for errors

### Logout not working
1. Verify the logout button has `data-action="logout"` attribute
2. Check if unified-auth.js is loaded
3. Check network tab for API call

### Header looks different on some pages
1. Ensure unified-header.css is loaded
2. Check for conflicting CSS rules
3. Verify HTML structure matches the guide

## Migration Checklist

For each page:
- [ ] Add unified-auth.js script
- [ ] Add unified-header.css stylesheet
- [ ] Replace existing header HTML
- [ ] Remove old authentication JavaScript
- [ ] Test login/logout flow
- [ ] Test on mobile devices
- [ ] Verify responsive design

## Support

For issues or questions, refer to:
- `/frontend/js/unified-auth.js` - Authentication logic
- `/frontend/css/unified-header.css` - Header styles
- `/frontend/components/unified-header.html` - Header HTML template

