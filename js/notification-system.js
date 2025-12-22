/**
 * Unified Notification System for Crane Intelligence
 * Provides confirmation dialogs, error messages, and success notifications
 * across both main website and admin portals
 */

class NotificationSystem {
    constructor() {
        this.notifications = [];
        this.confirmationCallbacks = new Map();
        this.init();
    }

    init() {
        this.createNotificationContainer();
        this.createConfirmationModal();
        this.setupGlobalErrorHandling();
    }

    createNotificationContainer() {
        // Remove existing container if it exists
        const existingContainer = document.getElementById('notification-container');
        if (existingContainer) {
            existingContainer.remove();
        }

        // Ensure document.body exists before creating container
        if (!document.body) {
            console.warn('Document body not ready, retrying notification container creation');
            setTimeout(() => this.createNotificationContainer(), 100);
            return;
        }

        const container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'notification-container';
        container.innerHTML = `
            <style>
                .notification-container {
                    position: fixed !important;
                    top: 20px !important;
                    right: 20px !important;
                    z-index: 10000 !important;
                    max-width: 400px !important;
                    min-width: 300px !important;
                    width: auto !important;
                    pointer-events: none !important;
                    box-sizing: border-box !important;
                    display: flex !important;
                    flex-direction: column !important;
                    align-items: flex-end !important;
                }

                .notification {
                    background: #ffffff !important;
                    border-radius: 8px !important;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
                    margin-bottom: 12px !important;
                    padding: 16px 20px !important;
                    display: flex !important;
                    align-items: flex-start !important;
                    gap: 12px !important;
                    pointer-events: auto !important;
                    animation: slideInRight 0.3s ease-out !important;
                    border-left: 4px solid #007BFF !important;
                    width: 100% !important;
                    max-width: 400px !important;
                    min-width: 300px !important;
                    word-wrap: break-word !important;
                    box-sizing: border-box !important;
                    position: relative !important;
                    overflow: hidden !important;
                }

                .notification.success {
                    border-left-color: #28A745 !important;
                    background: #d4edda !important;
                }

                .notification.error {
                    border-left-color: #DC3545 !important;
                    background: #f8d7da !important;
                }

                .notification.warning {
                    border-left-color: #FFC107 !important;
                    background: #fff3cd !important;
                }

                .notification.info {
                    border-left-color: #17A2B8 !important;
                    background: #d1ecf1 !important;
                }

                .notification-icon {
                    flex-shrink: 0 !important;
                    width: 20px !important;
                    height: 20px !important;
                    margin-top: 2px !important;
                    display: block !important;
                }

                .notification-content {
                    flex: 1 !important;
                    min-width: 0 !important;
                    overflow: hidden !important;
                    word-wrap: break-word !important;
                    overflow-wrap: break-word !important;
                }

                .notification-title {
                    font-weight: 600 !important;
                    font-size: 14px !important;
                    margin: 0 0 4px 0 !important;
                    color: #333 !important;
                    line-height: 1.4 !important;
                    word-wrap: break-word !important;
                }

                .notification-message {
                    font-size: 13px !important;
                    margin: 0 !important;
                    color: #666 !important;
                    line-height: 1.4 !important;
                    word-wrap: break-word !important;
                    overflow-wrap: break-word !important;
                }

                .notification-close {
                    background: none !important;
                    border: none !important;
                    font-size: 18px !important;
                    cursor: pointer !important;
                    color: #999 !important;
                    padding: 0 !important;
                    width: 20px !important;
                    height: 20px !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    flex-shrink: 0 !important;
                    line-height: 1 !important;
                }

                .notification-close:hover {
                    color: #333;
                }

                .notification-actions {
                    margin-top: 12px;
                    display: flex;
                    gap: 8px;
                    justify-content: flex-end;
                }

                .notification-btn {
                    padding: 6px 12px;
                    border: none;
                    border-radius: 4px;
                    font-size: 12px;
                    cursor: pointer;
                    font-weight: 500;
                }

                .notification-btn-primary {
                    background: #007BFF;
                    color: white;
                }

                .notification-btn-secondary {
                    background: #6C757D;
                    color: white;
                }

                .notification-btn-danger {
                    background: #DC3545;
                    color: white;
                }

                @keyframes slideInRight {
                    from {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }

                @keyframes slideOutRight {
                    from {
                        transform: translateX(0);
                        opacity: 1;
                    }
                    to {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                }

                .notification.slide-out {
                    animation: slideOutRight 0.3s ease-in forwards;
                }

                /* Confirmation Modal Styles */
                .confirmation-modal {
                    position: fixed !important;
                    top: 0 !important;
                    left: 0 !important;
                    width: 100% !important;
                    height: 100% !important;
                    background: rgba(0, 0, 0, 0.5) !important;
                    z-index: 10001 !important;
                    display: none !important;
                    align-items: center !important;
                    justify-content: center !important;
                    padding: 20px !important;
                    box-sizing: border-box !important;
                }

                .confirmation-modal.show {
                    display: flex !important;
                }

                .confirmation-dialog {
                    background: white !important;
                    border-radius: 8px !important;
                    padding: 24px !important;
                    max-width: 500px !important;
                    width: 100% !important;
                    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2) !important;
                    animation: modalSlideIn 0.3s ease-out !important;
                    box-sizing: border-box !important;
                    position: relative !important;
                }

                @keyframes modalSlideIn {
                    from {
                        transform: scale(0.9);
                        opacity: 0;
                    }
                    to {
                        transform: scale(1);
                        opacity: 1;
                    }
                }

                .confirmation-title {
                    font-size: 18px !important;
                    font-weight: 600 !important;
                    margin: 0 0 12px 0 !important;
                    color: #333 !important;
                    line-height: 1.4 !important;
                    word-wrap: break-word !important;
                }

                .confirmation-message {
                    font-size: 14px !important;
                    margin: 0 0 20px 0 !important;
                    color: #666 !important;
                    line-height: 1.5 !important;
                    word-wrap: break-word !important;
                }

                .confirmation-actions {
                    display: flex !important;
                    gap: 12px !important;
                    justify-content: flex-end !important;
                    flex-wrap: wrap !important;
                }

                .confirmation-btn {
                    padding: 10px 20px !important;
                    border: none !important;
                    border-radius: 6px !important;
                    font-size: 14px !important;
                    cursor: pointer !important;
                    font-weight: 500 !important;
                    min-width: 80px !important;
                    box-sizing: border-box !important;
                    white-space: nowrap !important;
                }

                .confirmation-btn-primary {
                    background: #007BFF;
                    color: white;
                }

                .confirmation-btn-secondary {
                    background: #6C757D;
                    color: white;
                }

                .confirmation-btn-danger {
                    background: #DC3545;
                    color: white;
                }
                
                .confirmation-btn-danger:hover {
                    background: #C82333;
                }

                .confirmation-btn:hover {
                    opacity: 0.9;
                }

                /* Dark theme support */
                @media (prefers-color-scheme: dark) {
                    .notification {
                        background: #2A2A2A;
                        color: #FFFFFF;
                        border-left-color: #00FF85;
                    }

                    .notification.success {
                        background: #1A4D1A;
                        border-left-color: #28A745;
                    }

                    .notification.error {
                        background: #4D1A1A;
                        border-left-color: #DC3545;
                    }

                    .notification.warning {
                        background: #4D3D1A;
                        border-left-color: #FFC107;
                    }

                    .notification.info {
                        background: #1A3D4D;
                        border-left-color: #17A2B8;
                    }

                    .notification-title {
                        color: #FFFFFF;
                    }

                    .notification-message {
                        color: #B0B0B0;
                    }

                    .confirmation-dialog {
                        background: #1A1A1A;
                        color: #FFFFFF;
                        border: 1px solid #333;
                    }

                    .confirmation-title {
                        color: #FFFFFF;
                        font-weight: 600;
                    }

                    .confirmation-message {
                        color: #B0B0B0;
                    }
                    
                    .confirmation-btn-danger {
                        background: #DC3545;
                        color: white;
                    }
                    
                    .confirmation-btn-danger:hover {
                        background: #C82333;
                    }
                    
                    .confirmation-btn-secondary {
                        background: #444;
                        color: white;
                    }
                    
                    .confirmation-btn-secondary:hover {
                        background: #555;
                    }
                }

                /* Mobile responsiveness */
                @media (max-width: 768px) {
                    .notification-container {
                        top: 10px !important;
                        right: 10px !important;
                        left: 10px !important;
                        max-width: calc(100% - 20px) !important;
                        min-width: auto !important;
                        width: auto !important;
                    }

                    .notification {
                        padding: 12px 16px !important;
                        max-width: 100% !important;
                        min-width: auto !important;
                        width: 100% !important;
                    }

                    .confirmation-dialog {
                        margin: 20px !important;
                        padding: 20px !important;
                        max-width: calc(100% - 40px) !important;
                    }

                    .confirmation-actions {
                        flex-direction: column !important;
                    }

                    .confirmation-btn {
                        width: 100% !important;
                    }
                }
            </style>
        `;
        
        // Safely append to document body
        if (document.body) {
            document.body.appendChild(container);
        } else {
            console.error('Cannot append notification container: document.body is null');
        }
    }

    createConfirmationModal() {
        const modal = document.createElement('div');
        modal.id = 'confirmation-modal';
        modal.className = 'confirmation-modal';
        modal.innerHTML = `
            <div class="confirmation-dialog">
                <h3 class="confirmation-title" id="confirmation-title">Confirm Action</h3>
                <p class="confirmation-message" id="confirmation-message">Are you sure you want to perform this action?</p>
                <div class="confirmation-actions">
                    <button class="confirmation-btn confirmation-btn-secondary" id="confirmation-cancel">Cancel</button>
                    <button class="confirmation-btn confirmation-btn-primary" id="confirmation-confirm">Confirm</button>
                </div>
            </div>
        `;
        
        // Safely append to document body
        if (document.body) {
            document.body.appendChild(modal);
        } else {
            console.error('Cannot append confirmation modal: document.body is null');
        }

        // Add event listeners
        document.getElementById('confirmation-cancel').addEventListener('click', () => {
            this.hideConfirmation();
        });

        document.getElementById('confirmation-confirm').addEventListener('click', () => {
            this.confirmAction();
        });

        // Close on backdrop click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.hideConfirmation();
            }
        });
    }

    setupGlobalErrorHandling() {
        // Global error handler
        window.addEventListener('error', (event) => {
            this.showError('An unexpected error occurred', event.error?.message || 'Unknown error');
        });

        // Unhandled promise rejection handler
        window.addEventListener('unhandledrejection', (event) => {
            this.showError('Request failed', event.reason?.message || 'Network error');
        });
    }

    // Notification methods
    showSuccess(title, message, duration = 5000) {
        this.showNotification('success', title, message, duration);
    }

    showError(title, message, duration = 7000) {
        this.showNotification('error', title, message, duration);
    }

    showWarning(title, message, duration = 6000) {
        this.showNotification('warning', title, message, duration);
    }

    showInfo(title, message, duration = 5000) {
        this.showNotification('info', title, message, duration);
    }

    showNotification(type, title, message, duration = 5000) {
        const container = document.getElementById('notification-container');
        if (!container) {
            console.warn('Notification container not found, attempting to create it');
            this.createNotificationContainer();
            const newContainer = document.getElementById('notification-container');
            if (!newContainer) {
                console.error('Failed to create notification container');
                return;
            }
        }

        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        const icon = this.getIcon(type);
        const id = Date.now() + Math.random();
        
        notification.innerHTML = `
            <div class="notification-icon">${icon}</div>
            <div class="notification-content">
                <div class="notification-title">${title}</div>
                <div class="notification-message">${message}</div>
            </div>
            <button class="notification-close" onclick="notificationSystem.removeNotification('${id}')">&times;</button>
        `;

        notification.id = id;
        const finalContainer = document.getElementById('notification-container');
        if (finalContainer) {
            finalContainer.appendChild(notification);
        } else {
            console.error('Cannot append notification: container not found');
        }

        // Auto-remove after duration
        if (duration > 0) {
            setTimeout(() => {
                this.removeNotification(id);
            }, duration);
        }

        return id;
    }

    removeNotification(id) {
        const notification = document.getElementById(id);
        if (notification) {
            notification.classList.add('slide-out');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }
    }

    getIcon(type) {
        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };
        return icons[type] || 'ℹ';
    }

    // Confirmation dialog methods
    confirm(title, message, options = {}) {
        return new Promise((resolve) => {
            const modal = document.getElementById('confirmation-modal');
            const titleEl = document.getElementById('confirmation-title');
            const messageEl = document.getElementById('confirmation-message');
            const confirmBtn = document.getElementById('confirmation-confirm');
            const cancelBtn = document.getElementById('confirmation-cancel');

            titleEl.textContent = title;
            messageEl.textContent = message;

            // Update button text and styles
            confirmBtn.textContent = options.confirmText || 'Confirm';
            cancelBtn.textContent = options.cancelText || 'Cancel';

            // Update button styles based on type
            confirmBtn.className = `confirmation-btn confirmation-btn-${options.type || 'primary'}`;

            // Store callback
            this.confirmationCallbacks.set('current', resolve);

            modal.classList.add('show');
        });
    }

    confirmDangerous(title, message, options = {}) {
        return this.confirm(title, message, {
            ...options,
            type: 'danger',
            confirmText: options.confirmText || 'Delete',
            cancelText: options.cancelText || 'Cancel'
        });
    }

    hideConfirmation() {
        const modal = document.getElementById('confirmation-modal');
        modal.classList.remove('show');
        
        const callback = this.confirmationCallbacks.get('current');
        if (callback) {
            callback(false);
            this.confirmationCallbacks.delete('current');
        }
    }

    confirmAction() {
        const modal = document.getElementById('confirmation-modal');
        modal.classList.remove('show');
        
        const callback = this.confirmationCallbacks.get('current');
        if (callback) {
            callback(true);
            this.confirmationCallbacks.delete('current');
        }
    }

    // Form validation methods
    validateForm(form, rules = {}) {
        const errors = [];
        const formData = new FormData(form);

        for (const [field, rule] of Object.entries(rules)) {
            const value = formData.get(field);
            const fieldElement = form.querySelector(`[name="${field}"]`);

            if (rule.required && (!value || value.trim() === '')) {
                errors.push({ field, message: rule.message || `${field} is required` });
                this.highlightField(fieldElement, true);
            } else if (rule.pattern && value && !rule.pattern.test(value)) {
                errors.push({ field, message: rule.message || `${field} format is invalid` });
                this.highlightField(fieldElement, true);
            } else if (rule.minLength && value && value.length < rule.minLength) {
                errors.push({ field, message: rule.message || `${field} must be at least ${rule.minLength} characters` });
                this.highlightField(fieldElement, true);
            } else if (rule.maxLength && value && value.length > rule.maxLength) {
                errors.push({ field, message: rule.message || `${field} must be no more than ${rule.maxLength} characters` });
                this.highlightField(fieldElement, true);
            } else {
                this.highlightField(fieldElement, false);
            }
        }

        if (errors.length > 0) {
            this.showError('Validation Error', errors.map(e => e.message).join(', '));
            return false;
        }

        return true;
    }

    highlightField(field, isError) {
        if (!field) return;

        if (isError) {
            field.style.borderColor = '#DC3545';
            field.style.boxShadow = '0 0 0 2px rgba(220, 53, 69, 0.25)';
        } else {
            field.style.borderColor = '';
            field.style.boxShadow = '';
        }
    }

    // API error handling
    handleApiError(error, context = '') {
        let message = 'An error occurred';
        
        if (error.response) {
            // Server responded with error status
            const status = error.response.status;
            const data = error.response.data;
            
            switch (status) {
                case 400:
                    message = data.message || 'Invalid request';
                    break;
                case 401:
                    message = 'Authentication required';
                    break;
                case 403:
                    message = 'Access denied';
                    break;
                case 404:
                    message = 'Resource not found';
                    break;
                case 422:
                    message = data.message || 'Validation error';
                    break;
                case 500:
                    message = 'Server error occurred';
                    break;
                default:
                    message = data.message || `Error ${status}`;
            }
        } else if (error.request) {
            // Network error
            message = 'Network error - please check your connection';
        } else {
            // Other error
            message = error.message || 'Unknown error occurred';
        }

        this.showError(context ? `${context} Failed` : 'Error', message);
    }

    // Utility methods
    clearAll() {
        const container = document.getElementById('notification-container');
        if (container) {
            container.innerHTML = '';
        }
    }

    // Loading state management
    showLoading(message = 'Loading...') {
        return this.showInfo('Loading', message, 0); // 0 duration = no auto-remove
    }

    hideLoading(notificationId) {
        if (notificationId) {
            this.removeNotification(notificationId);
        }
    }
}

// Create global instance with DOM ready check
function initializeNotificationSystem() {
    try {
        window.notificationSystem = new NotificationSystem();
        console.log('Notification system initialized successfully');
    } catch (error) {
        console.error('Failed to initialize notification system:', error);
        // Retry after a short delay
        setTimeout(initializeNotificationSystem, 100);
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeNotificationSystem);
} else {
    initializeNotificationSystem();
}

// Browser environment - no module exports needed
