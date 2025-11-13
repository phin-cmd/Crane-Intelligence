/**
 * Authentication System for Crane Intelligence Platform
 * Handles user login, logout, and token management
 */

class AuthSystem {
    constructor() {
        this.apiBaseUrl = '/api/v1/auth';
        this.tokenKey = 'crane_auth_token';
        this.userKey = 'crane_user_data';
        this.init();
    }

    init() {
        // Check for existing token on initialization
        const token = this.getToken();
        if (token) {
            // Verify token is still valid
            this.verifyToken();
        }
    }

    /**
     * Login user with email and password
     */
    async login(email, password) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });

            const data = await response.json();

            if (response.ok) {
                // Store token and user data
                this.setToken(data.access_token);
                
                // Get user info
                const userInfo = await this.getCurrentUser();
                if (userInfo.success) {
                    this.setUserData(userInfo.user);
                }

                return {
                    success: true,
                    message: 'Login successful',
                    user: userInfo.user
                };
            } else {
                return {
                    success: false,
                    error: data.detail || 'Login failed'
                };
            }
        } catch (error) {
            console.error('Login error:', error);
            return {
                success: false,
                error: 'Network error. Please try again.'
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
                await fetch(`${this.apiBaseUrl}/logout`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json',
                    }
                });
            }
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            // Clear local storage regardless of API call result
            this.clearAuthData();
        }
    }

    /**
     * Get current user information
     */
    async getCurrentUser() {
        try {
            const token = this.getToken();
            if (!token) {
                return { success: false, error: 'No token found' };
            }

            const response = await fetch(`${this.apiBaseUrl}/me`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                const user = await response.json();
                return { success: true, user: user };
            } else {
                // Token might be expired
                this.clearAuthData();
                return { success: false, error: 'Token expired' };
            }
        } catch (error) {
            console.error('Get current user error:', error);
            return { success: false, error: 'Network error' };
        }
    }

    /**
     * Verify if current token is valid
     */
    async verifyToken() {
        const result = await this.getCurrentUser();
        if (!result.success) {
            this.clearAuthData();
        }
        return result.success;
    }

    /**
     * Check if user is logged in
     */
    isLoggedIn() {
        const token = this.getToken();
        const user = this.getUserData();
        return !!(token && user);
    }

    /**
     * Get current user data from localStorage
     */
    getCurrentUser() {
        return this.getUserData();
    }

    /**
     * Token management methods
     */
    setToken(token) {
        localStorage.setItem(this.tokenKey, token);
    }

    getToken() {
        return localStorage.getItem(this.tokenKey);
    }

    setUserData(user) {
        localStorage.setItem(this.userKey, JSON.stringify(user));
    }

    getUserData() {
        const userData = localStorage.getItem(this.userKey);
        return userData ? JSON.parse(userData) : null;
    }

    clearAuthData() {
        localStorage.removeItem(this.tokenKey);
        localStorage.removeItem(this.userKey);
    }

    /**
     * Register new user
     */
    async register(email, password, fullName) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    password: password,
                    full_name: fullName
                })
            });

            const data = await response.json();

            if (response.ok) {
                return {
                    success: true,
                    message: 'Registration successful',
                    user: data
                };
            } else {
                return {
                    success: false,
                    error: data.detail || 'Registration failed'
                };
            }
        } catch (error) {
            console.error('Registration error:', error);
            return {
                success: false,
                error: 'Network error. Please try again.'
            };
        }
    }
}

// Make AuthSystem globally available
window.AuthSystem = AuthSystem;
