/**
 * Unified Authentication Utilities for Crane Intelligence
 * Ensures consistent user tier display across all pages
 */

// Tier name mapping - converts tier codes to display names
const TIER_DISPLAY_NAMES = {
    'free': 'Free User',
    'basic': 'Basic User',  // Map 'basic' to 'Basic User'
    'starter': 'Starter User',
    'professional': 'Professional User',
    'pro': 'Professional User'  // Map 'pro' to 'Professional'
};

/**
 * Get the display name for a subscription tier
 * @param {string|object} tierData - Tier code string or subscription object
 * @returns {string} - Display name for the tier
 */
function getTierDisplayName(tierData) {
    if (!tierData) {
        return 'Free User';  // Default fallback
    }
    
    // If tierData is an object (subscription object)
    if (typeof tierData === 'object') {
        const tierCode = tierData.tier_code || tierData.tier || tierData.subscription_tier;
        const tierName = tierData.tier_name || tierData.tierName;
        
        // If tier_name is already formatted, use it
        if (tierName && tierName.includes('User')) {
            return tierName;
        }
        
        // Otherwise, map the tier code
        if (tierCode) {
            return TIER_DISPLAY_NAMES[tierCode.toLowerCase()] || `${tierCode} User`;
        }
    }
    
    // If tierData is a string (tier code)
    if (typeof tierData === 'string') {
        return TIER_DISPLAY_NAMES[tierData.toLowerCase()] || `${tierData} User`;
    }
    
    return 'Free User';  // Final fallback
}

/**
 * Update user display elements on the page
 * @param {object} userData - User data object from API
 */
function updateUserDisplay(userData) {
    if (!userData) {
        console.warn('No user data provided to updateUserDisplay');
        return;
    }
    
    // Update user name
    const userNameElement = document.getElementById('userDisplayName');
    if (userNameElement) {
        userNameElement.textContent = userData.full_name || userData.name || 'User';
    }
    
    // Update user role/tier
    const userRoleElement = document.getElementById('userRole');
    if (userRoleElement) {
        const tierDisplay = getTierDisplayName(userData.subscription || userData);
        userRoleElement.textContent = tierDisplay;
    }
    
    // Update user initials in avatar
    const userInitialsElement = document.getElementById('userInitials');
    if (userInitialsElement && userData.full_name) {
        const names = userData.full_name.split(' ');
        const initials = names.map(n => n[0]).join('').substring(0, 2).toUpperCase();
        userInitialsElement.textContent = initials;
    }
}

/**
 * Load and display user information from localStorage or API
 */
async function loadUserInfo() {
    try {
        // Check if user is logged in
        const accessToken = localStorage.getItem('access_token');
        if (!accessToken) {
            console.log('No access token found');
            return;
        }
        
        // Try to get user data from localStorage first
        const storedUserData = localStorage.getItem('user_data');
        if (storedUserData) {
            try {
                const userData = JSON.parse(storedUserData);
                updateUserDisplay(userData);
                console.log('User display updated from localStorage:', userData);
            } catch (e) {
                console.error('Error parsing stored user data:', e);
            }
        }
        
        // Fetch fresh user data from API
        const response = await fetch('https://craneintelligence.tech/api/v1/auth/profile', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const result = await response.json();
            if (result.user) {
                // Update localStorage with fresh data
                localStorage.setItem('user_data', JSON.stringify(result.user));
                
                // Fetch subscription info from working endpoint
                try {
                    const subResponse = await fetch('https://craneintelligence.tech/api/v1/subscriptions/info', {
                        method: 'GET',
                        headers: {
                            'Authorization': `Bearer ${accessToken}`,
                            'Content-Type': 'application/json'
                        }
                    });
                    
                    if (subResponse.ok) {
                        const subData = await subResponse.json();
                        // Update user data with correct tier from subscription info
                        if (subData.tier) {
                            result.user.subscription = {
                                tier: subData.tier,
                                tier_name: subData.tier_name,
                                tier_code: subData.tier
                            };
                            result.user.subscription_tier = subData.tier;
                            console.log('✅ Fetched subscription tier from API:', subData.tier, '-', subData.tier_name);
                        }
                    } else {
                        console.warn('⚠️ Subscription info endpoint returned:', subResponse.status);
                    }
                } catch (tierError) {
                    console.error('❌ Error fetching subscription info:', tierError);
                }
                
                // Update display
                updateUserDisplay(result.user);
                console.log('User display updated from API:', result.user);
            }
        } else if (response.status === 401) {
            // Token expired or invalid
            console.log('Authentication failed, clearing session');
            localStorage.removeItem('access_token');
            localStorage.removeItem('user_data');
        }
    } catch (error) {
        console.error('Error loading user info:', error);
    }
}

/**
 * Toggle user dropdown menu
 */
function toggleUserDropdown(event) {
    if (event) {
        event.stopPropagation();
    }
    const dropdown = document.getElementById('userDropdown');
    if (dropdown) {
        dropdown.classList.toggle('show');
    }
}

/**
 * Close dropdown when clicking outside
 */
document.addEventListener('click', function(event) {
    const wrapper = document.querySelector('.user-profile-wrapper') || document.querySelector('.user-section');
    const dropdown = document.getElementById('userDropdown');
    
    if (dropdown && wrapper && !wrapper.contains(event.target)) {
        dropdown.classList.remove('show');
    }
});

/**
 * Initialize user display on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    loadUserInfo();
    
    // Set up dropdown toggle - check for .user-profile (inside wrapper) or .user-section
    const userProfile = document.querySelector('.user-profile');
    const userSection = document.querySelector('.user-section');
    const targetElement = userProfile || userSection;
    
    if (targetElement) {
        // Add cursor pointer style to indicate clickability
        targetElement.style.cursor = 'pointer';
        
        // Only remove onclick from child elements, not from the target element itself
        const clickableChildren = targetElement.querySelectorAll('*[onclick]');
        clickableChildren.forEach(child => {
            // Don't remove onclick from the user-profile element itself
            if (child !== targetElement) {
                child.removeAttribute('onclick');
            }
        });
        
        // If the element doesn't have an onclick attribute, add event listener
        if (!targetElement.hasAttribute('onclick')) {
            targetElement.addEventListener('click', function(e) {
                e.stopPropagation();
                toggleUserDropdown(e);
            });
        }
    }
    
    // Make toggleUserDropdown available globally for onclick handlers
    window.toggleUserDropdown = toggleUserDropdown;
    
    // Also make it available as toggleDropdown for backward compatibility
    window.toggleDropdown = toggleUserDropdown;
});

// Export functions for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        getTierDisplayName,
        updateUserDisplay,
        loadUserInfo,
        toggleUserDropdown
    };
}

