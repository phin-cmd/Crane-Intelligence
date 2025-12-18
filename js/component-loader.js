/**
 * Centralized Component Loader System
 * Loads and injects reusable components across all pages
 */

class ComponentLoader {
    constructor() {
        this.components = {};
        this.loadedComponents = new Set();
        this.isReplacing = false;
        this.hasReplaced = false;
    }

    /**
     * Load a component from file
     */
    async loadComponent(componentName) {
        if (this.loadedComponents.has(componentName)) {
            return this.components[componentName];
        }

        try {
            const response = await fetch(`/components/${componentName}.html`);
            if (!response.ok) {
                throw new Error(`Failed to load component: ${componentName}`);
            }
            const html = await response.text();
            this.components[componentName] = html;
            this.loadedComponents.add(componentName);
            return html;
        } catch (error) {
            console.error(`Error loading component ${componentName}:`, error);
            return null;
        }
    }

    /**
     * Inject component into target element
     */
    async injectComponent(componentName, targetSelectorOrElement, options = {}) {
        const html = await this.loadComponent(componentName);
        if (!html) {
            console.error(`Component ${componentName} not loaded`);
            return false;
        }

        // Handle both selector strings and element objects
        let target;
        if (typeof targetSelectorOrElement === 'string') {
            target = document.querySelector(targetSelectorOrElement);
        } else if (targetSelectorOrElement instanceof Element) {
            target = targetSelectorOrElement;
        } else {
            console.error(`Invalid target: expected string selector or Element, got ${typeof targetSelectorOrElement}`);
            return false;
        }

        if (!target) {
            console.error(`Target element not found: ${targetSelectorOrElement}`);
            return false;
        }

        // Process template variables if provided
        let processedHtml = html;
        if (options.variables) {
            Object.entries(options.variables).forEach(([key, value]) => {
                processedHtml = processedHtml.replace(new RegExp(`{{${key}}}`, 'g'), value);
            });
        }

        // Insert component
        if (options.mode === 'replace') {
            target.innerHTML = processedHtml;
        } else if (options.mode === 'prepend') {
            target.insertAdjacentHTML('afterbegin', processedHtml);
        } else {
            target.insertAdjacentHTML('beforeend', processedHtml);
        }

        // Execute any scripts in the injected HTML (only once per component)
        // Use global flag to prevent duplicate execution
        const componentScriptKey = `component_script_executed_${componentName}`;
        if (window[componentScriptKey]) {
            console.log(`[ComponentLoader] Script for ${componentName} already executed, skipping`);
        } else {
            window[componentScriptKey] = true;
            
            // Find scripts in the processed HTML
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = processedHtml;
            const scripts = tempDiv.querySelectorAll('script');
            
            scripts.forEach(oldScript => {
                const newScript = document.createElement('script');
                // Copy all attributes
                Array.from(oldScript.attributes).forEach(attr => {
                    newScript.setAttribute(attr.name, attr.value);
                });
                // Copy script content
                newScript.textContent = oldScript.textContent;
                // Append to document head or body to execute
                (document.head || document.body).appendChild(newScript);
                console.log('[ComponentLoader] Executed script from component:', componentName);
            });
            
            // Also find and execute scripts in the actual injected content (only if not already executed)
            const injectedScripts = target.querySelectorAll('script');
            injectedScripts.forEach(oldScript => {
                // Only process if not already executed
                if (!oldScript.hasAttribute('data-executed')) {
                    const newScript = document.createElement('script');
                    Array.from(oldScript.attributes).forEach(attr => {
                        newScript.setAttribute(attr.name, attr.value);
                    });
                    newScript.textContent = oldScript.textContent;
                    oldScript.setAttribute('data-executed', 'true');
                    (document.head || document.body).appendChild(newScript);
                    console.log('[ComponentLoader] Executed injected script from component:', componentName);
                }
            });
        }

        // Initialize component scripts if any
        this.initializeComponent(componentName, target);
        
        // For unified-header, trigger auth UI update after injection (only once)
        if (componentName === 'unified-header') {
            // Check if already initialized to prevent duplicate calls
            if (window.unifiedHeaderAuthUIUpdateScheduled) {
                console.log('[ComponentLoader] unified-header auth UI update already scheduled, skipping');
                return true;
            }
            window.unifiedHeaderAuthUIUpdateScheduled = true;
            
            console.log('[ComponentLoader] unified-header injected, initializing auth UI...');
            // Single delayed call to avoid excessive updates
            setTimeout(() => {
                if (typeof window.updateAuthUI === 'function') {
                    console.log('[ComponentLoader] Calling updateAuthUI');
                    window.updateAuthUI();
                }
            }, 200);
        }

        return true;
    }

    /**
     * Initialize component-specific scripts
     */
    initializeComponent(componentName, container) {
        switch (componentName) {
            case 'pricing-section':
                this.initPricingSection(container);
                break;
            case 'payment-module':
                this.initPaymentModule(container);
                break;
            case 'valuation-form':
                this.initValuationForm(container);
                break;
            case 'notification-system':
                this.initNotificationSystem(container);
                break;
            case 'user-profile-dropdown':
                this.initUserProfileDropdown(container);
                break;
        }
    }

    /**
     * Initialize user profile dropdown
     */
    initUserProfileDropdown(container) {
        console.log('[ComponentLoader] Initializing user-profile-dropdown');
        
        // Wait a bit for the component HTML to be fully injected
        setTimeout(() => {
            // Load user profile manager script if not already loaded
            if (typeof userProfileManager === 'undefined') {
                console.log('[ComponentLoader] Loading user-profile-manager.js...');
                const script = document.createElement('script');
                script.src = '/js/user-profile-manager.js';
                script.onload = () => {
                    console.log('[ComponentLoader] user-profile-manager.js loaded');
                    if (typeof userProfileManager !== 'undefined') {
                        userProfileManager.initialize();
                        // Trigger auth UI update after profile manager is ready
                        setTimeout(() => {
                            if (typeof window.updateAuthUI === 'function') {
                                console.log('[ComponentLoader] Triggering updateAuthUI after manager init');
                                window.updateAuthUI(true);
                            }
                        }, 200);
                    }
                };
                document.head.appendChild(script);
            } else {
                console.log('[ComponentLoader] user-profile-manager already loaded, initializing...');
                userProfileManager.initialize();
                // Trigger auth UI update immediately
                setTimeout(() => {
                    if (typeof window.updateAuthUI === 'function') {
                        console.log('[ComponentLoader] Triggering updateAuthUI');
                        window.updateAuthUI(true);
                    }
                }, 200);
            }
            
            // Update profile display if user is logged in
            if (typeof safeStorage !== 'undefined') {
                const userData = safeStorage.getItem('user_data');
                const token = safeStorage.getItem('access_token');
                if (userData && token) {
                    try {
                        const user = JSON.parse(userData);
                        if (typeof updateUserProfileDisplay === 'function') {
                            updateUserProfileDisplay(user);
                        } else if (typeof userProfileManager !== 'undefined') {
                            userProfileManager.updateProfileDisplay(user);
                        }
                    } catch (e) {
                        console.error('[ComponentLoader] Error parsing user data:', e);
                    }
                }
            }
            
            // Update auth UI visibility - single delayed call
            setTimeout(() => {
                if (typeof window.updateAuthUI === 'function') {
                    window.updateAuthUI(true);
                }
            }, 200);
        }, 100);
    }
    
    /**
     * Update auth buttons and user profile visibility
     * Delegates to centralized updateAuthUI function in unified-header
     */
    updateAuthUI() {
        // Use centralized function from unified-header component
        if (typeof window.updateAuthUI === 'function') {
            window.updateAuthUI();
        }
    }

    /**
     * Initialize pricing section
     */
    initPricingSection(container) {
        // Update pricing buttons based on user status
        if (typeof updatePricingForLoggedInUser === 'function') {
            updatePricingForLoggedInUser();
        }

        // Attach event listeners
        const pricingButtons = container.querySelectorAll('.pricing-cta');
        pricingButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const tier = button.getAttribute('data-tier');
                if (typeof handlePricingAction === 'function') {
                    handlePricingAction(tier);
                }
            });
        });
    }

    /**
     * Initialize payment module
     */
    initPaymentModule(container) {
        // Stripe initialization if available
        if (typeof Stripe !== 'undefined') {
            const stripeKey = container.getAttribute('data-stripe-key');
            if (stripeKey) {
                window.stripeInstance = Stripe(stripeKey);
            }
        }
    }

    /**
     * Initialize valuation form
     */
    initValuationForm(container) {
        const form = container.querySelector('form');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                if (typeof handleValuationSubmit === 'function') {
                    handleValuationSubmit(e);
                }
            });
        }
    }

    /**
     * Initialize notification system
     */
    initNotificationSystem(container) {
        // Notification system is already global, just ensure it's available
        if (typeof notificationSystem === 'undefined') {
            console.warn('Notification system not loaded');
        }
    }

    /**
     * Load multiple components in parallel
     */
    async loadComponents(componentNames) {
        const promises = componentNames.map(name => this.loadComponent(name));
        return Promise.all(promises);
    }

    /**
     * Replace all component placeholders in the document
     */
    async replaceAllPlaceholders() {
        // Prevent multiple simultaneous replacements
        if (this.isReplacing) {
            console.log('[ComponentLoader] Already replacing placeholders, skipping duplicate call');
            return;
        }
        
        // Only replace once per page load
        if (this.hasReplaced) {
            console.log('[ComponentLoader] Placeholders already replaced, skipping duplicate call');
            return;
        }
        
        this.isReplacing = true;
        console.log('[ComponentLoader] Starting to replace placeholders...');
        
        const placeholders = document.querySelectorAll('[data-component]');
        const promises = Array.from(placeholders).map(async (placeholder) => {
            const componentName = placeholder.getAttribute('data-component');
            const targetSelector = placeholder.getAttribute('data-target') || null;
            const mode = placeholder.getAttribute('data-mode') || 'replace';
            
            // Get variables from data attributes
            const variables = {};
            Array.from(placeholder.attributes).forEach(attr => {
                if (attr.name.startsWith('data-var-')) {
                    const key = attr.name.replace('data-var-', '');
                    variables[key] = attr.value;
                }
            });

            // Special handling for user-profile-dropdown - always append to .header-right
            if (componentName === 'user-profile-dropdown') {
                console.log('[ComponentLoader] Loading user-profile-dropdown component...');
                const headerRight = document.querySelector('.header-right');
                if (headerRight) {
                    console.log('[ComponentLoader] .header-right found, injecting component');
                    const result = await this.injectComponent(componentName, headerRight, { mode: 'append', variables });
                    if (result) {
                        console.log('[ComponentLoader] user-profile-dropdown injected successfully');
                        // Trigger auth UI update after component is loaded
                        setTimeout(() => {
                            if (typeof window.updateAuthUI === 'function') {
                                window.updateAuthUI(true);
                            }
                        }, 100);
                    }
                } else {
                    console.warn('[ComponentLoader] .header-right not found, retrying...');
                    setTimeout(async () => {
                        const retryHeaderRight = document.querySelector('.header-right');
                        if (retryHeaderRight) {
                            console.log('[ComponentLoader] .header-right found on retry, injecting component');
                            await this.injectComponent(componentName, retryHeaderRight, { mode: 'append', variables });
                            setTimeout(() => {
                                if (typeof window.updateAuthUI === 'function') {
                                    window.updateAuthUI(true);
                                }
                            }, 100);
                        } else {
                            console.error('[ComponentLoader] .header-right still not found after retry');
                        }
                    }, 500);
                }
            } else if (targetSelector) {
                await this.injectComponent(componentName, targetSelector, { mode, variables });
            } else {
                await this.injectComponent(componentName, placeholder, { mode, variables });
            }
        });

        await Promise.all(promises);
        
        this.isReplacing = false;
        this.hasReplaced = true;
        console.log('[ComponentLoader] Finished replacing placeholders');
        
        // Update auth UI after all components are loaded (only once)
        // Use centralized function from unified-header component
        setTimeout(() => {
            if (typeof window.updateAuthUI === 'function') {
                window.updateAuthUI(true);
            }
        }, 300);
    }
}

// Create global instance
window.componentLoader = new ComponentLoader();

// Auto-load components on DOM ready (only once)
if (!window.componentLoaderInitialized) {
    window.componentLoaderInitialized = true;
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            window.componentLoader.replaceAllPlaceholders();
        });
    } else {
        window.componentLoader.replaceAllPlaceholders();
    }
}

