/**
 * Settings Management JavaScript
 * Handles platform configuration and settings
 */

class SettingsManager {
    constructor() {
        this.currentSettings = {};
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadSettings();
    }

    bindEvents() {
        // Tab navigation
        document.querySelectorAll('.settings-tab').forEach(tab => {
            tab.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });
        
        // Save settings
        document.getElementById('saveSettings').addEventListener('click', () => this.saveSettings());
        document.getElementById('resetSettings').addEventListener('click', () => this.resetSettings());
    }

    switchTab(tabName) {
        // Hide all panels
        document.querySelectorAll('.settings-panel').forEach(panel => {
            panel.classList.remove('active');
        });
        
        // Remove active class from all tabs
        document.querySelectorAll('.settings-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        
        // Show selected panel
        document.getElementById(`${tabName}-settings`).classList.add('active');
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    }

    async loadSettings() {
        try {
            const api = new AdminAPI();
            const settings = await api.getSettings();
            this.currentSettings = settings;
            this.populateSettings(settings);
        } catch (error) {
            console.error('Error loading settings:', error);
            this.showError('Failed to load settings');
        }
    }

    populateSettings(settings) {
        // General settings
        if (settings.general) {
            document.getElementById('siteName').value = settings.general.site_name || '';
            document.getElementById('siteDescription').value = settings.general.site_description || '';
            document.getElementById('timezone').value = settings.general.timezone || 'UTC';
            document.getElementById('language').value = settings.general.language || 'en';
            document.getElementById('maintenanceMode').checked = settings.general.maintenance_mode || false;
        }

        // API settings
        if (settings.api) {
            document.getElementById('apiVersion').value = settings.api.api_version || 'v1';
            document.getElementById('rateLimit').value = settings.api.rate_limit || 1000;
            document.getElementById('apiKeyExpiry').value = settings.api.api_key_expiry || 365;
            document.getElementById('corsOrigins').value = settings.api.cors_origins || '';
            document.getElementById('enableSwagger').checked = settings.api.enable_swagger || false;
        }

        // Email settings
        if (settings.email) {
            document.getElementById('smtpHost').value = settings.email.smtp_host || '';
            document.getElementById('smtpPort').value = settings.email.smtp_port || 587;
            document.getElementById('smtpUsername').value = settings.email.smtp_username || '';
            document.getElementById('smtpPassword').value = settings.email.smtp_password || '';
            document.getElementById('fromEmail').value = settings.email.from_email || '';
            document.getElementById('fromName').value = settings.email.from_name || '';
            document.getElementById('enableTLS').checked = settings.email.enable_tls || false;
        }

        // Billing settings
        if (settings.billing) {
            document.getElementById('currency').value = settings.billing.currency || 'USD';
            document.getElementById('taxRate').value = settings.billing.tax_rate || 8.5;
            document.getElementById('stripePublishableKey').value = settings.billing.stripe_publishable_key || '';
            document.getElementById('stripeSecretKey').value = settings.billing.stripe_secret_key || '';
            document.getElementById('webhookSecret').value = settings.billing.webhook_secret || '';
        }

        // Security settings
        if (settings.security) {
            document.getElementById('sessionTimeout').value = settings.security.session_timeout || 30;
            document.getElementById('maxLoginAttempts').value = settings.security.max_login_attempts || 5;
            document.getElementById('lockoutDuration').value = settings.security.lockout_duration || 15;
            document.getElementById('require2FA').checked = settings.security.require_2fa || false;
            document.getElementById('passwordMinLength').value = settings.security.password_min_length || 8;
            document.getElementById('enableAuditLog').checked = settings.security.enable_audit_log || false;
        }

        // Advanced settings
        if (settings.advanced) {
            document.getElementById('debugMode').checked = settings.advanced.debug_mode || false;
            document.getElementById('logLevel').value = settings.advanced.log_level || 'INFO';
            document.getElementById('cacheTimeout').value = settings.advanced.cache_timeout || 3600;
            document.getElementById('maxFileSize').value = settings.advanced.max_file_size || 10;
            document.getElementById('allowedFileTypes').value = settings.advanced.allowed_file_types || 'jpg,jpeg,png,gif,pdf,doc,docx';
        }
    }

    async saveSettings() {
        try {
            const settings = this.collectSettings();
            
            const api = new AdminAPI();
            await api.updateSettings(settings);
            this.showSuccess('Settings saved successfully');
            this.currentSettings = settings;
        } catch (error) {
            console.error('Error saving settings:', error);
            this.showError('Failed to save settings');
        }
    }

    collectSettings() {
        return {
            general: {
                site_name: document.getElementById('siteName').value,
                site_description: document.getElementById('siteDescription').value,
                timezone: document.getElementById('timezone').value,
                language: document.getElementById('language').value,
                maintenance_mode: document.getElementById('maintenanceMode').checked
            },
            api: {
                api_version: document.getElementById('apiVersion').value,
                rate_limit: parseInt(document.getElementById('rateLimit').value),
                api_key_expiry: parseInt(document.getElementById('apiKeyExpiry').value),
                cors_origins: document.getElementById('corsOrigins').value,
                enable_swagger: document.getElementById('enableSwagger').checked
            },
            email: {
                smtp_host: document.getElementById('smtpHost').value,
                smtp_port: parseInt(document.getElementById('smtpPort').value),
                smtp_username: document.getElementById('smtpUsername').value,
                smtp_password: document.getElementById('smtpPassword').value,
                from_email: document.getElementById('fromEmail').value,
                from_name: document.getElementById('fromName').value,
                enable_tls: document.getElementById('enableTLS').checked
            },
            billing: {
                currency: document.getElementById('currency').value,
                tax_rate: parseFloat(document.getElementById('taxRate').value),
                stripe_publishable_key: document.getElementById('stripePublishableKey').value,
                stripe_secret_key: document.getElementById('stripeSecretKey').value,
                webhook_secret: document.getElementById('webhookSecret').value
            },
            security: {
                session_timeout: parseInt(document.getElementById('sessionTimeout').value),
                max_login_attempts: parseInt(document.getElementById('maxLoginAttempts').value),
                lockout_duration: parseInt(document.getElementById('lockoutDuration').value),
                require_2fa: document.getElementById('require2FA').checked,
                password_min_length: parseInt(document.getElementById('passwordMinLength').value),
                enable_audit_log: document.getElementById('enableAuditLog').checked
            },
            advanced: {
                debug_mode: document.getElementById('debugMode').checked,
                log_level: document.getElementById('logLevel').value,
                cache_timeout: parseInt(document.getElementById('cacheTimeout').value),
                max_file_size: parseInt(document.getElementById('maxFileSize').value),
                allowed_file_types: document.getElementById('allowedFileTypes').value
            }
        };
    }

    async resetSettings() {
        if (!confirm('Are you sure you want to reset all settings to defaults? This action cannot be undone.')) {
            return;
        }

        try {
            const api = new AdminAPI();
            await api.resetSettings();
            this.showSuccess('Settings reset to defaults');
            this.loadSettings();
        } catch (error) {
            console.error('Error resetting settings:', error);
            this.showError('Failed to reset settings');
        }
    }

    showSuccess(message) {
        const notification = document.createElement('div');
        notification.className = 'notification success';
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 3000);
    }

    showError(message) {
        const notification = document.createElement('div');
        notification.className = 'notification error';
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 5000);
    }
}

// Initialize settings manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.settingsManager = new SettingsManager();
});
