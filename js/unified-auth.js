/**
 * CRANE INTELLIGENCE - UNIFIED AUTHENTICATION SYSTEM
 * This module provides centralized authentication logic for all pages
 * Handles: Login, Logout, Token Management, User Profile Display
 */

class UnifiedAuth {
    constructor() {
        this.apiBaseUrl = '/api/v1/auth';
        // Use consistent token keys with the backend
        this.tokenKey = 'access_token';
        this.refreshTokenKey = 'refresh_token';
        this.userKey = 'user_data';
        this.authInitialized = false;
    }

    /**
     * Initialize authentication system on page load
     * Call this from every page's DOMContentLoaded event
     */
    async initialize() {
        if (this.authInitialized) {
            // Already initialized, just return current auth status
            return this.isLoggedIn();
        }
        this.authInitialized = true;

        const isLoggedIn = await this.checkAuthStatus();
        this.updateHeaderUI(isLoggedIn);
        
        // Setup event listeners
        this.setupEventListeners();
        
        return isLoggedIn;
    }

    /**
     * Check if user is authenticated and token is valid
     */
    async checkAuthStatus() {
        const token = this.getToken();
        if (!token) {
            this.clearAuthData();
            return false;
        }

        try {
            // Verify token with backend
            const userData = await this.fetchUserData();
            if (userData) {
                this.setUserData(userData);
                return true;
            } else {
                this.clearAuthData();
                return false;
            }
        } catch (error) {
            console.error('Auth status check failed:', error);
            this.clearAuthData();
            return false;
        }
    }

    /**
     * Fetch current user data from backend or localStorage
     */
    async fetchUserData() {
        // First try to get from localStorage
        const storedUser = this.getUserData();
        if (storedUser) {
            return storedUser;
        }

        // If not in localStorage, try to validate token
        const token = this.getToken();
        if (!token) return null;

        // For now, if we have a token but no user data, clear everything
        // In production, you would want to fetch from a /profile endpoint
        console.warn('Token exists but no user data found. Clearing authentication.');
        this.clearAuthData();
        return null;
    }

    /**
     * Login user with email and password
     */
    async login(email, password) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });

            // Check if the response is OK (status 200-299)
            if (!response.ok) {
                let errorMessage = 'Login failed. Please try again.';
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.error || errorData.message || errorMessage;
                } catch (e) {
                    // If JSON parsing fails, use status text
                    errorMessage = `Login failed: ${response.statusText || 'Server error'}`;
                }
                
                console.error('Login HTTP error:', response.status, errorMessage);
                return {
                    success: false,
                    error: errorMessage
                };
            }

            const result = await response.json();

            // Handle API response - check for success
            if (result.success) {
                // API returns: { success, message, access_token, user }
                const accessToken = result.access_token || result.data?.tokens?.access_token;
                const refreshToken = result.refresh_token || result.data?.tokens?.refresh_token;
                const user = result.user || result.data?.user;
                
                if (accessToken && user) {
                    this.setToken(accessToken);
                    if (refreshToken) {
                        this.setRefreshToken(refreshToken);
                    }
                    this.setUserData(user);
                    
                    // Update header UI immediately after successful login
                    this.updateHeaderUI(true);

                    return {
                        success: true,
                        message: result.message || 'Login successful',
                        user: user
                    };
                }
            }

            return {
                success: false,
                error: result.error || result.message || 'Login failed'
            };
        } catch (error) {
            console.error('Login error:', error);
            return {
                success: false,
                error: error.message || 'Network error. Please check your connection and try again.'
            };
        }
    }

    /**
     * Register new user
     */
    async register(userData) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(userData)
            });

            // Check if the response is OK (status 200-299)
            if (!response.ok) {
                let errorMessage = 'Registration failed. Please try again.';
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.error || errorData.message || errorMessage;
                } catch (e) {
                    // If JSON parsing fails, use status text
                    errorMessage = `Registration failed: ${response.statusText || 'Server error'}`;
                }
                
                console.error('Registration HTTP error:', response.status, errorMessage);
                return {
                    success: false,
                    error: errorMessage
                };
            }

            const result = await response.json();

            // Handle API response - check for success
            if (result.success) {
                // API returns: { success, message, access_token, user }
                const accessToken = result.access_token || result.data?.tokens?.access_token;
                const refreshToken = result.refresh_token || result.data?.tokens?.refresh_token;
                const user = result.user || result.data?.user;
                
                if (accessToken && user) {
                    this.setToken(accessToken);
                    if (refreshToken) {
                        this.setRefreshToken(refreshToken);
                    }
                    this.setUserData(user);
                    
                    // Update header UI immediately after successful registration
                    this.updateHeaderUI(true);

                    return {
                        success: true,
                        message: result.message || 'Registration successful',
                        user: user
                    };
                }
            }

            return {
                success: false,
                error: result.error || result.message || 'Registration failed'
            };
        } catch (error) {
            console.error('Registration error:', error);
            return {
                success: false,
                error: error.message || 'Network error. Please check your connection and try again.'
            };
        }
    }

    /**
     * Logout user
     */
    async logout() {
        try {
            const token = this.getToken();
            if (token) {
                // Notify backend
                await fetch(`${this.apiBaseUrl}/logout`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });
            }
        } catch (error) {
            console.error('Logout API error:', error);
        } finally {
            // Clear local data regardless
            this.clearAuthData();
            
            // Update UI
            this.updateHeaderUI(false);
            
            // Redirect to homepage
            window.location.href = '/homepage.html';
        }
    }

    /**
     * Refresh access token using refresh token
     */
    async refreshToken() {
        const refreshToken = this.getRefreshToken();
        if (!refreshToken) return false;

        try {
            const response = await fetch(`${this.apiBaseUrl}/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ refresh_token: refreshToken })
            });

            const result = await response.json();

            if (result.success && result.data) {
                this.setToken(result.data.access_token);
                if (result.data.refresh_token) {
                    this.setRefreshToken(result.data.refresh_token);
                }
                return true;
            }

            return false;
        } catch (error) {
            console.error('Token refresh error:', error);
            return false;
        }
    }

    /**
     * Update header UI based on authentication status
     */
    updateHeaderUI(isLoggedIn) {
        console.log('🔄 updateHeaderUI called, isLoggedIn:', isLoggedIn);
        
        const authButtons = document.getElementById('authButtons');
        const userProfile = document.getElementById('userProfile');
        
        console.log('📍 Elements found:', {
            authButtons: !!authButtons,
            userProfile: !!userProfile
        });

        if (isLoggedIn) {
            // User is logged in - show profile dropdown
            console.log("✅ Showing user profile, hiding auth buttons");
            if (authButtons) {
                authButtons.classList.add("hidden");
                authButtons.classList.remove("visible");
            }
            if (userProfile) {
                userProfile.classList.remove("hidden");
                userProfile.classList.add("visible");
                this.updateUserProfileDisplay();
                // Force update display
                setTimeout(() => {
                    if (authButtons) {
                        authButtons.style.display = "none";
                        authButtons.style.visibility = "hidden";
                    }
                    if (userProfile) {
                        userProfile.style.display = "flex";
                        userProfile.style.visibility = "visible";
                    }
                }, 100);
            }
        } else {
            // User is not logged in - show login/signup buttons
            console.log("❌ Showing auth buttons, hiding user profile");
            if (authButtons) {
                authButtons.classList.remove("hidden");
                authButtons.classList.add("visible");
            }
            if (userProfile) {
                userProfile.classList.add("hidden");
                userProfile.classList.remove("visible");
            }
        }
    }

    /**
     * Update user profile display with user data
     */
    updateUserProfileDisplay() {
        const user = this.getUserData();
        if (!user) {
            console.warn('⚠️ No user data found for profile display');
            return;
        }

        console.log('👤 Updating profile display with user:', user.full_name || user.email);

        // Update user display name
        const userDisplayName = document.getElementById('userDisplayName');
        if (userDisplayName) {
            const displayName = user.full_name || user.username || user.email || 'User';
            userDisplayName.textContent = displayName;
            console.log('📝 Display name set to:', displayName);
        }

        // Update user role display - show user_role instead of subscription tier
        const userRole = document.getElementById('userRole');
        if (userRole) {
            // Get user data from parameter or localStorage
            let user = null;
            if (userData) {
                user = userData;
            } else {
                const storedUserData = localStorage.getItem('user_data');
                if (storedUserData) {
                    try {
                        user = JSON.parse(storedUserData);
                    } catch (e) {
                        console.error('Error parsing user data:', e);
                    }
                }
            }
            
            if (user) {
                try {
                    // Display user_role (not subscription tier)
                    let roleName = 'User';
                    if (user.user_role) {
                        const role = user.user_role.toLowerCase();
                        const roleMap = {
                            'crane_rental_company': 'Crane Rental Company',
                            'equipment_dealer': 'Equipment Dealer',
                            'financial_institution': 'Financial Institution',
                            'others': 'Other'
                        };
                        roleName = roleMap[role] || role.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
                    }
                    userRole.textContent = roleName;
                    console.log('🏷️ User role:', roleName);
                } catch (error) {
                    console.error('❌ Error parsing user data:', error);
                    userRole.textContent = 'User';
                }
            } else {
                userRole.textContent = 'User';
            }
        }

        // Update user initials in avatar
        const userInitials = document.getElementById('userInitials');
        if (userInitials) {
            const fullName = user.full_name || user.username || user.email || 'User';
            const initials = fullName.split(' ')
                .filter(word => word.length > 0)
                .map(word => word.charAt(0).toUpperCase())
                .join('')
                .substring(0, 2);
            userInitials.textContent = initials;
            console.log('🔤 Initials set to:', initials);
        }
    }

    /**
     * Setup event listeners for dropdown and logout
     */
    setupEventListeners() {
        // User profile dropdown toggle
        const userProfile = document.getElementById('userProfile');
        const userDropdown = document.getElementById('userDropdown');
        
        if (userProfile && userDropdown) {
            userProfile.addEventListener('click', (e) => {
                e.stopPropagation();
                userDropdown.classList.toggle('show');
            });

            // Close dropdown when clicking outside
            document.addEventListener('click', (e) => {
                if (!userProfile.contains(e.target)) {
                    userDropdown.classList.remove('show');
                }
            });
        }

        // Logout button
        const logoutButtons = document.querySelectorAll('[data-action="logout"]');
        logoutButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.logout();
            });
        });
    }

    /**
     * Token management methods
     */
    getToken() {
        return localStorage.getItem(this.tokenKey);
    }

    setToken(token) {
        localStorage.setItem(this.tokenKey, token);
    }

    getRefreshToken() {
        return localStorage.getItem(this.refreshTokenKey);
    }

    setRefreshToken(token) {
        localStorage.setItem(this.refreshTokenKey, token);
    }

    getUserData() {
        const userData = localStorage.getItem(this.userKey);
        if (!userData) return null;
        try {
            return JSON.parse(userData);
        } catch (e) {
            console.error('Failed to parse user data:', e);
            return null;
        }
    }

    setUserData(user) {
        localStorage.setItem(this.userKey, JSON.stringify(user));
    }

    clearAuthData() {
        localStorage.removeItem(this.tokenKey);
        localStorage.removeItem(this.refreshTokenKey);
        localStorage.removeItem(this.userKey);
        // Also clear old token keys for compatibility
        localStorage.removeItem('crane_auth_token');
        localStorage.removeItem('crane_user_data');
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
    }

    /**
     * Check if user is logged in (synchronous)
     */
    isLoggedIn() {
        const token = this.getToken();
        const user = this.getUserData();
        return !!(token && user);
    }

    /**
     * Get current user (synchronous)
     */
    getCurrentUser() {
        return this.getUserData();
    }
}

// Create and export global instance
window.unifiedAuth = new UnifiedAuth();

// Auto-initialize on DOM load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.unifiedAuth.initialize();
    });
} else {
    // DOM already loaded
    window.unifiedAuth.initialize();
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UnifiedAuth;
}

