/**
 * Admin Portal Notification Integration
 * Extends the notification system with admin-specific functionality
 */

// Wait for notification system to load
document.addEventListener('DOMContentLoaded', function() {
    // Ensure notification system is available
    if (typeof notificationSystem === 'undefined') {
        console.error('Notification system not loaded');
        return;
    }

    // Add admin-specific notification methods
    window.adminNotifications = {
        // User management notifications
        userCreated: (userName) => {
            notificationSystem.showSuccess('User Created', `${userName} has been successfully added to the system`);
        },

        userUpdated: (userName) => {
            notificationSystem.showSuccess('User Updated', `${userName}'s information has been updated successfully`);
        },

        userDeleted: (count) => {
            notificationSystem.showSuccess('Users Deleted', `${count} user(s) have been permanently removed`);
        },

        userSuspended: (count) => {
            notificationSystem.showWarning('Users Suspended', `${count} user(s) have been suspended`);
        },

        userActivated: (count) => {
            notificationSystem.showSuccess('Users Activated', `${count} user(s) have been reactivated`);
        },

        // Content management notifications
        contentSaved: (contentType) => {
            notificationSystem.showSuccess('Content Saved', `${contentType} has been saved successfully`);
        },

        contentPublished: (contentType) => {
            notificationSystem.showSuccess('Content Published', `${contentType} has been published and is now live`);
        },

        contentDeleted: (contentType) => {
            notificationSystem.showSuccess('Content Deleted', `${contentType} has been permanently removed`);
        },

        // Analytics notifications
        reportGenerated: (reportType) => {
            notificationSystem.showSuccess('Report Generated', `${reportType} report has been generated successfully`);
        },

        dataExported: (dataType) => {
            notificationSystem.showSuccess('Data Exported', `${dataType} data has been exported successfully`);
        },

        // System notifications
        settingsSaved: () => {
            notificationSystem.showSuccess('Settings Saved', 'System settings have been updated successfully');
        },

        backupCreated: () => {
            notificationSystem.showSuccess('Backup Created', 'System backup has been created successfully');
        },

        systemRestarted: () => {
            notificationSystem.showInfo('System Restarted', 'The system has been restarted successfully');
        },

        // Security notifications
        securityAlert: (message) => {
            notificationSystem.showError('Security Alert', message);
        },

        loginAttempt: (ip, success) => {
            if (success) {
                notificationSystem.showInfo('Login Detected', `Successful login from ${ip}`);
            } else {
                notificationSystem.showWarning('Failed Login', `Failed login attempt from ${ip}`);
            }
        },

        // Form validation
        validateForm: (formId, rules = {}) => {
            const form = document.getElementById(formId);
            if (!form) return false;

            return notificationSystem.validateForm(form, rules);
        },

        // API error handling with admin context
        handleApiError: (error, context = '') => {
            let message = 'An error occurred';
            let title = 'Error';
            
            // Handle null or undefined error
            if (!error) {
                console.error('handleApiError called with null/undefined error');
                notificationSystem.showError('Error', 'An unknown error occurred');
                return;
            }
            
            if (error.response) {
                const status = error.response.status;
                const data = error.response.data || error.response;
                
                switch (status) {
                    case 400:
                        title = 'Invalid Request';
                        message = data.message || 'The request was invalid';
                        break;
                    case 401:
                        title = 'Authentication Required';
                        message = 'Please log in to continue';
                        break;
                    case 403:
                        title = 'Access Denied';
                        message = 'You do not have permission to perform this action';
                        break;
                    case 404:
                        title = 'Not Found';
                        message = 'The requested resource was not found';
                        break;
                    case 422:
                        title = 'Validation Error';
                        message = data.message || 'Please check your input and try again';
                        break;
                    case 500:
                        title = 'Server Error';
                        message = 'An internal server error occurred';
                        break;
                    default:
                        title = `Error ${status}`;
                        message = data.message || 'An unexpected error occurred';
                }
            } else if (error.request) {
                title = 'Network Error';
                message = 'Unable to connect to the server. Please check your connection.';
            } else {
                title = 'Error';
                message = error.message || 'An unexpected error occurred';
            }

            notificationSystem.showError(context ? `${context} - ${title}` : title, message);
        },

        // Confirmation dialogs for admin actions
        confirmUserDeletion: (userCount) => {
            return notificationSystem.confirmDangerous(
                'Delete Users',
                `Are you sure you want to permanently delete ${userCount} user(s)? This action cannot be undone.`,
                { confirmText: 'Delete Users' }
            );
        },

        confirmUserSuspension: (userCount) => {
            return notificationSystem.confirm(
                'Suspend Users',
                `Are you sure you want to suspend ${userCount} user(s)? They will not be able to access the system.`,
                { confirmText: 'Suspend Users', type: 'warning' }
            );
        },

        confirmContentDeletion: (contentType) => {
            return notificationSystem.confirmDangerous(
                'Delete Content',
                `Are you sure you want to permanently delete this ${contentType}? This action cannot be undone.`,
                { confirmText: 'Delete Content' }
            );
        },

        confirmSystemAction: (action) => {
            return notificationSystem.confirm(
                'Confirm System Action',
                `Are you sure you want to ${action}? This may affect system performance.`,
                { confirmText: 'Confirm', type: 'warning' }
            );
        },

        // Bulk operations
        confirmBulkAction: (action, count) => {
            return notificationSystem.confirm(
                `Bulk ${action}`,
                `Are you sure you want to ${action} ${count} item(s)?`,
                { confirmText: action, type: 'warning' }
            );
        },

        // Loading states
        showLoading: (message = 'Processing...') => {
            return notificationSystem.showLoading(message);
        },

        hideLoading: (loadingId) => {
            notificationSystem.hideLoading(loadingId);
        },

        // Success notifications
        showSuccess: (title, message) => {
            notificationSystem.showSuccess(title, message);
        },

        showError: (title, message) => {
            notificationSystem.showError(title, message);
        },

        showWarning: (title, message) => {
            notificationSystem.showWarning(title, message);
        },

        showInfo: (title, message) => {
            notificationSystem.showInfo(title, message);
        }
    };

    // Add global error handling for admin pages
    window.addEventListener('error', function(event) {
        adminNotifications.handleApiError(event.error, 'Admin System');
    });

    window.addEventListener('unhandledrejection', function(event) {
        adminNotifications.handleApiError(event.reason, 'Admin System');
    });

    // Add form validation to all admin forms
    const adminForms = document.querySelectorAll('form[data-validate]');
    adminForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const rules = JSON.parse(form.dataset.validate || '{}');
            if (!adminNotifications.validateForm(form.id, rules)) {
                e.preventDefault();
            }
        });
    });

    // Add confirmation to all destructive buttons
    const destructiveButtons = document.querySelectorAll('[data-confirm]');
    destructiveButtons.forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            const confirmMessage = this.dataset.confirm;
            const confirmed = await notificationSystem.confirm(
                'Confirm Action',
                confirmMessage,
                { confirmText: 'Confirm', type: 'danger' }
            );
            
            if (confirmed) {
                // Trigger the original action
                const originalAction = this.dataset.action;
                if (originalAction) {
                    eval(originalAction);
                }
            }
        });
    });

    // Add loading states to all form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                let loadingId;
                loadingId = adminNotifications.showLoading('Processing...');
                
                // Re-enable button after 5 seconds as fallback
                setTimeout(() => {
                    submitBtn.disabled = false;
                    adminNotifications.hideLoading(loadingId);
                }, 5000);
            }
        });
    });

    console.log('Admin notifications system initialized');
});
