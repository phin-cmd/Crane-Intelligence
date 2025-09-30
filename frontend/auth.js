// Authentication system for Crane Intelligence Platform
(function() {
    'use strict';
    
    const AuthSystem = {
        apiBase: 'http://159.65.186.73:8004/api/v1',
        currentUser: null,
        
        init: function() {
            this.loadUserFromStorage();
            this.updateUserInterface();
        },
        
        loadUserFromStorage: function() {
            const storedUser = localStorage.getItem('user');
            if (storedUser) {
                this.currentUser = JSON.parse(storedUser);
            }
        },
        
        async login(email, password) {
            try {
                const response = await fetch(`${this.apiBase}/auth/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email, password })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    localStorage.setItem('access_token', data.access_token);
                    localStorage.setItem('user', JSON.stringify(data.user));
                    this.currentUser = data.user;
                    this.updateUserInterface();
                    return { success: true, user: data.user };
                } else {
                    return { success: false, message: data.message };
                }
            } catch (error) {
                console.error('Login error:', error);
                return { success: false, message: 'Unable to connect to the server' };
            }
        },
        
        async register(userData) {
            try {
                const response = await fetch(`${this.apiBase}/auth/register`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(userData)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    localStorage.setItem('access_token', data.access_token);
                    localStorage.setItem('user', JSON.stringify(data.user));
                    this.currentUser = data.user;
                    this.updateUserInterface();
                    return { success: true, user: data.user };
                } else {
                    return { success: false, message: data.message };
                }
            } catch (error) {
                console.error('Registration error:', error);
                return { success: false, message: 'Unable to connect to the server' };
            }
        },
        
        logout: function() {
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
            this.currentUser = null;
            this.updateUserInterface();
        },
        
        updateUserInterface: function() {
            const authButtons = document.getElementById('authButtons');
            const userProfile = document.getElementById('userProfile');
            const userAvatar = document.getElementById('userAvatar');
            const userName = document.getElementById('userName');
            
            if (this.currentUser) {
                if (authButtons) authButtons.style.display = 'none';
                if (userProfile) {
                    userProfile.style.display = 'flex';
                    if (userAvatar) userAvatar.textContent = this.currentUser.full_name.charAt(0).toUpperCase();
                    if (userName) userName.textContent = this.currentUser.full_name;
                }
            } else {
                if (authButtons) authButtons.style.display = 'flex';
                if (userProfile) userProfile.style.display = 'none';
            }
        },
        
        isLoggedIn: function() {
            return this.currentUser !== null;
        },
        
        getCurrentUser: function() {
            return this.currentUser;
        }
    };
    
    // Make it globally available
    window.AuthSystem = AuthSystem;
    
    // Initialize when DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        AuthSystem.init();
    });
    
    console.log('Auth system initialized successfully');
})();
