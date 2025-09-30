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
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 10000;
                    max-width: 400px;
                    pointer-events: none;
                }

                .notification {
                    background: #ffffff;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                    margin-bottom: 12px;
                    padding: 16px 20px;
                    display: flex;
                    align-items: flex-start;
                    gap: 12px;
                    pointer-events: auto;
                    animation: slideInRight 0.3s ease-out;
                    border-left: 4px solid #007BFF;
                    max-width: 100%;
                    word-wrap: break-word;
                }

                .notification.success {
                    border-left-color: #28A745;
                    background: #d4edda;
                }

                .notification.error {
                    border-left-color: #DC3545;
                    background: #f8d7da;
                }

                .notification.warning {
                    border-left-color: #FFC107;
                    background: #fff3cd;
                }

                .notification.info {
                    border-left-color: #17A2B8;
                    background: #d1ecf1;
                }

                .notification-icon {
                    flex-shrink: 0;
                    width: 20px;
                    height: 20px;
                    margin-top: 2px;
                }

                .notification-content {
                    flex: 1;
                    min-width: 0;
                }

                .notification-title {
                    font-weight: 600;
                    font-size: 14px;
                    margin: 0 0 4px 0;
                    color: #333;
                }

                .notification-message {
                    font-size: 13px;
                    margin: 0;
                    color: #666;
                    line-height: 1.4;
                }

                .notification-close {
                    background: none;
                    border: none;
                    font-size: 18px;
                    cursor: pointer;
                    color: #999;
                    padding: 0;
                    width: 20px;
                    height: 20px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    flex-shrink: 0;
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
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0, 0, 0, 0.5);
                    z-index: 10001;
                    display: none;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                }

                .confirmation-modal.show {
                    display: flex;
                }

                .confirmation-dialog {
                    background: white;
                    border-radius: 8px;
                    padding: 24px;
                    max-width: 500px;
                    width: 100%;
                    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
                    animation: modalSlideIn 0.3s ease-out;
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
                    font-size: 18px;
                    font-weight: 600;
                    margin: 0 0 12px 0;
                    color: #333;
                }

                .confirmation-message {
                    font-size: 14px;
                    margin: 0 0 20px 0;
                    color: #666;
                    line-height: 1.5;
                }

                .confirmation-actions {
                    display: flex;
                    gap: 12px;
                    justify-content: flex-end;
                }

                .confirmation-btn {
                    padding: 10px 20px;
                    border: none;
                    border-radius: 6px;
                    font-size: 14px;
                    cursor: pointer;
                    font-weight: 500;
                    min-width: 80px;
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
                        background: #2A2A2A;
                        color: #FFFFFF;
                    }

                    .confirmation-title {
                        color: #FFFFFF;
                    }

                    .confirmation-message {
                        color: #B0B0B0;
                    }
                }

                /* Mobile responsiveness */
                @media (max-width: 768px) {
                    .notification-container {
                        top: 10px;
                        right: 10px;
                        left: 10px;
                        max-width: none;
                    }

                    .notification {
                        padding: 12px 16px;
                    }

                    .confirmation-dialog {
                        margin: 20px;
                        padding: 20px;
                    }

                    .confirmation-actions {
                        flex-direction: column;
                    }

                    .confirmation-btn {
                        width: 100%;
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
