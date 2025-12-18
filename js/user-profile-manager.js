/**
 * User Profile Manager - Centralized Management
 * Handles user profile display, dropdown, and updates across all pages
 */

class UserProfileManager {
    constructor() {
        this.userProfile = null;
        this.userDropdown = null;
        this.isInitialized = false;
    }

    /**
     * Initialize user profile manager
     */
    initialize(retryCount = 0) {
        const MAX_RETRIES = 20;
        
        if (this.isInitialized && this.userProfile) return;
        
        this.userProfile = document.getElementById('userProfile');
        this.userDropdown = document.getElementById('userDropdown');
        
        if (!this.userProfile) {
            if (retryCount < MAX_RETRIES) {
                setTimeout(() => this.initialize(retryCount + 1), 200);
                return;
            }
            console.warn('[userProfileManager] User profile element not found after', MAX_RETRIES, 'retries');
            // Try to trigger component loading
            if (typeof componentLoader !== 'undefined') {
                const headerRight = document.querySelector('.header-right');
                if (headerRight) {
                    componentLoader.injectComponent('user-profile-dropdown', headerRight, { mode: 'append' });
                }
            }
            return;
        }
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Update profile display
        this.updateProfileFromStorage();
        
        this.isInitialized = true;
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Close dropdown when clicking outside
        document.addEventListener('click', (event) => {
            if (this.userProfile && !this.userProfile.contains(event.target)) {
                this.closeDropdown();
            }
        });
        
        // Handle dropdown item clicks
        if (this.userDropdown) {
            const items = this.userDropdown.querySelectorAll('.dropdown-item');
            items.forEach(item => {
                item.addEventListener('click', (e) => {
                    if (item.getAttribute('data-action') !== 'logout') {
                        setTimeout(() => this.closeDropdown(), 100);
                    }
                });
            });
        }
    }

    /**
     * Toggle dropdown
     */
    toggleDropdown() {
        console.log('[userProfileManager] toggleDropdown called');
        if (!this.userDropdown || !this.userProfile) {
            console.error('[userProfileManager] userDropdown or userProfile not found', {
                dropdown: !!this.userDropdown,
                profile: !!this.userProfile
            });
            // Try to re-initialize
            this.userDropdown = document.getElementById('userDropdown');
            this.userProfile = document.getElementById('userProfile');
            if (!this.userDropdown || !this.userProfile) {
                console.error('[userProfileManager] Still not found after re-initialization');
                return;
            }
        }
        
        const isOpen = this.userDropdown.classList.contains('show');
        console.log('[userProfileManager] Dropdown isOpen:', isOpen);
        this.closeAllDropdowns();
        
        if (!isOpen) {
            this.userDropdown.classList.add('show');
            this.userProfile.classList.add('active');
            console.log('[userProfileManager] Dropdown opened');
        } else {
            console.log('[userProfileManager] Dropdown closed');
        }
    }

    /**
     * Close dropdown
     */
    closeDropdown() {
        if (this.userDropdown) {
            this.userDropdown.classList.remove('show');
        }
        if (this.userProfile) {
            this.userProfile.classList.remove('active');
        }
    }

    /**
     * Close all dropdowns
     */
    closeAllDropdowns() {
        const allDropdowns = document.querySelectorAll('.user-dropdown.show');
        const allProfiles = document.querySelectorAll('.user-profile.active');
        
        allDropdowns.forEach(dd => dd.classList.remove('show'));
        allProfiles.forEach(profile => profile.classList.remove('active'));
    }

    /**
     * Update profile display from storage
     */
    updateProfileFromStorage() {
        if (typeof safeStorage === 'undefined') {
            console.warn('safeStorage not available');
            return;
        }
        
        const userData = safeStorage.getItem('user_data');
        if (userData) {
            try {
                const user = JSON.parse(userData);
                this.updateProfileDisplay(user);
            } catch (e) {
                console.error('Error parsing user data:', e);
            }
        } else {
            this.hideProfile();
        }
    }

    /**
     * Update profile display with user data
     */
    updateProfileDisplay(user) {
        if (!user) {
            this.hideProfile();
            return;
        }
        
        this.showProfile();
        
        // Update name
        const userDisplayName = document.getElementById('userDisplayName');
        if (userDisplayName) {
            const fullName = user.full_name || user.email || user.username || 'User';
            userDisplayName.textContent = fullName;
        }
        
        // Update initials
        const userInitials = document.getElementById('userInitials');
        if (userInitials) {
            const fullName = user.full_name || user.email || user.username || 'U';
            const initials = fullName
                .split(' ')
                .map(name => name.charAt(0))
                .join('')
                .toUpperCase()
                .substring(0, 2);
            userInitials.textContent = initials;
        }
        
        // Update user role (shown under user name)
        const userRole = document.getElementById('userRole');
        if (userRole) {
            this.updateRoleDisplay(user, userRole);
        }
    }

    /**
     * Update role display - shows only user role
     */
    updateRoleDisplay(user, element) {
        if (!user || !element) return;
        
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
        element.textContent = roleName;
    }

    /**
     * DEPRECATED: Update subscription tier display - use updateRoleDisplay instead
     */
    async updateSubscriptionTierDisplay(user, element) {
        this.updateRoleDisplay(user, element);
    }

    /**
     * Show profile, hide auth buttons
     */
    showProfile() {
        if (this.userProfile) {
            this.userProfile.style.display = 'flex';
        }
        const authButtons = document.getElementById('authButtons');
        if (authButtons) {
            authButtons.style.display = 'none';
        }
    }

    /**
     * Hide profile, show auth buttons
     */
    hideProfile() {
        if (this.userProfile) {
            this.userProfile.style.display = 'none';
        }
        const authButtons = document.getElementById('authButtons');
        if (authButtons) {
            authButtons.style.display = 'flex';
        }
    }

    /**
     * Handle logout
     */
    handleLogout() {
        this.closeDropdown();
        
        // Clear storage
        if (typeof safeStorage !== 'undefined') {
            safeStorage.removeItem('access_token');
            safeStorage.removeItem('refresh_token');
            safeStorage.removeItem('user_data');
        }
        
        // Update UI
        this.hideProfile();
        
        // Show notification
        if (typeof notificationSystem !== 'undefined') {
            notificationSystem.showSuccess('Logged Out', 'You have been logged out successfully');
        }
        
        // Redirect
        setTimeout(() => {
            window.location.href = '/homepage.html';
        }, 1000);
    }
}

// Create global instance
window.userProfileManager = new UserProfileManager();

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.userProfileManager.initialize();
    });
} else {
    window.userProfileManager.initialize();
}

// Global functions for backward compatibility
window.toggleUserDropdown = function() {
    window.userProfileManager.toggleDropdown();
};

window.closeUserDropdown = function() {
    window.userProfileManager.closeDropdown();
};

window.updateUserProfileDisplay = function(user) {
    window.userProfileManager.updateProfileDisplay(user);
};

