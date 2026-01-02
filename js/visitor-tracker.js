/**
 * Visitor Tracking Script
 * Tracks website visitors, page views, and user behavior
 * Automatically included on all pages to collect analytics data
 */

(function() {
    'use strict';
    
    // Configuration
    // Only enable tracking on production (craneintelligence.tech, not dev/uat)
    const hostname = window.location.hostname;
    const isProduction = hostname === 'craneintelligence.tech' && 
                         !hostname.includes('dev.') && 
                         !hostname.includes('uat.') &&
                         !hostname.includes('staging.');
    
    const TRACKING_ENABLED = isProduction; // Only track in production
    
    // Log tracking status (only in console, not sent anywhere)
    if (!TRACKING_ENABLED) {
        console.debug('Visitor tracking disabled - not in production environment');
    }
    const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:8004'
        : 'https://craneintelligence.tech/api/v1';
    
    const TRACKING_ENDPOINT = `${API_BASE}/visitor-tracking/track`;
    const UPDATE_ENDPOINT = `${API_BASE}/visitor-tracking/update`;
    
    // Get or create visitor ID
    function getVisitorId() {
        let visitorId = getCookie('visitor_id');
        if (!visitorId) {
            visitorId = generateUUID();
            setCookie('visitor_id', visitorId, 365); // 1 year
        }
        return visitorId;
    }
    
    // Get or create session ID
    function getSessionId() {
        let sessionId = getCookie('session_id');
        if (!sessionId) {
            sessionId = generateUUID();
            setCookie('session_id', sessionId, 0.5); // 30 minutes
        }
        return sessionId;
    }
    
    // Cookie helpers
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }
    
    function setCookie(name, value, days) {
        const expires = new Date();
        expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
        document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/;SameSite=Lax`;
    }
    
    // Generate UUID
    function generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
    
    // Get user ID if logged in
    function getUserId() {
        try {
            const userData = localStorage.getItem('user_data');
            if (userData) {
                const user = JSON.parse(userData);
                return user.id || null;
            }
        } catch (e) {
            // Ignore errors
        }
        return null;
    }
    
    // Get screen dimensions
    function getScreenInfo() {
        return {
            width: window.screen.width,
            height: window.screen.height,
            resolution: `${window.screen.width}x${window.screen.height}`
        };
    }
    
    // Get timezone
    function getTimezone() {
        try {
            return Intl.DateTimeFormat().resolvedOptions().timeZone;
        } catch (e) {
            return null;
        }
    }
    
    // Track page view
    let trackingId = null;
    let startTime = Date.now();
    let maxScroll = 0;
    
    async function trackPageView() {
        if (!TRACKING_ENABLED) return;
        
        try {
            const screenInfo = getScreenInfo();
            const userId = getUserId();
            
            const trackingData = {
                page_url: window.location.href,
                page_title: document.title,
                referrer: document.referrer || null,
                user_agent: navigator.userAgent,
                screen_width: screenInfo.width,
                screen_height: screenInfo.height,
                language: navigator.language || navigator.userLanguage,
                timezone: getTimezone(),
                metadata: {
                    viewport_width: window.innerWidth,
                    viewport_height: window.innerHeight,
                    color_depth: screen.colorDepth,
                    pixel_ratio: window.devicePixelRatio || 1
                }
            };
            
            const response = await fetch(`${TRACKING_ENDPOINT}${userId ? `?user_id=${userId}` : ''}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(trackingData)
            });
            
            if (response.ok) {
                const data = await response.json();
                trackingId = data.tracking_id;
                
                // Update cookies if returned
                if (data.visitor_id) {
                    setCookie('visitor_id', data.visitor_id, 365);
                }
                if (data.session_id) {
                    setCookie('session_id', data.session_id, 0.5);
                }
            }
        } catch (error) {
            // Silently fail - don't interrupt user experience
            console.debug('Visitor tracking error:', error);
        }
    }
    
    // Track scroll depth
    function trackScroll() {
        const scrollPercent = Math.round(
            ((window.scrollY + window.innerHeight) / document.documentElement.scrollHeight) * 100
        );
        if (scrollPercent > maxScroll) {
            maxScroll = scrollPercent;
        }
    }
    
    // Update tracking on page unload
    async function updateTracking() {
        if (!trackingId) return;
        
        try {
            const timeOnPage = Math.round((Date.now() - startTime) / 1000);
            
            await fetch(`${UPDATE_ENDPOINT}/${trackingId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    time_on_page: timeOnPage,
                    scroll_depth: maxScroll,
                    exit_page: true
                })
            });
        } catch (error) {
            // Silently fail
            console.debug('Visitor tracking update error:', error);
        }
    }
    
    // Initialize tracking
    if (TRACKING_ENABLED && document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            trackPageView();
        });
    } else {
        trackPageView();
    }
    
    // Track scrolling
    let scrollTimeout;
    window.addEventListener('scroll', function() {
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(trackScroll, 100);
    }, { passive: true });
    
    // Update on page unload
    window.addEventListener('beforeunload', function() {
        // Use sendBeacon for more reliable tracking on page unload
        if (trackingId && navigator.sendBeacon) {
            const timeOnPage = Math.round((Date.now() - startTime) / 1000);
            const data = JSON.stringify({
                time_on_page: timeOnPage,
                scroll_depth: maxScroll,
                exit_page: true
            });
            
            const blob = new Blob([data], { type: 'application/json' });
            navigator.sendBeacon(`${UPDATE_ENDPOINT}/${trackingId}`, blob);
        } else {
            updateTracking();
        }
    });
    
    // Periodic update (every 30 seconds)
    setInterval(function() {
        if (trackingId) {
            const timeOnPage = Math.round((Date.now() - startTime) / 1000);
            fetch(`${UPDATE_ENDPOINT}/${trackingId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    time_on_page: timeOnPage,
                    scroll_depth: maxScroll
                })
            }).catch(() => {
                // Silently fail
            });
        }
    }, 30000);
    
    // Expose tracking function for manual tracking
    window.trackEvent = function(eventName, eventData) {
        if (trackingId) {
            // Could extend this to track custom events
            console.log('Event tracked:', eventName, eventData);
        }
    };
    
})();

