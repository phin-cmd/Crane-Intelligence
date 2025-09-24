/**
 * Crane Intelligence Admin Login JavaScript
 * Handles authentication and form interactions
 */

class AdminLogin {
    constructor() {
        this.api = window.adminAPI;
        this.isLoading = false;
        this.requiresTwoFactor = false;
        this.twoFactorToken = null;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkExistingAuth();
        this.initializeForm();
    }

    setupEventListeners() {
        // Login form submission
        const loginForm = document.getElementById('login-form');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }

        // Password toggle
        const passwordToggle = document.getElementById('password-toggle');
        if (passwordToggle) {
            passwordToggle.addEventListener('click', () => this.togglePasswordVisibility());
        }

        // Two-factor verification
        const verifyBtn = document.getElementById('verify-btn');
        if (verifyBtn) {
            verifyBtn.addEventListener('click', () => this.handleTwoFactorVerification());
        }

        // Two-factor code inputs
        const codeInputs = document.querySelectorAll('.code-input');
        codeInputs.forEach((input, index) => {
            input.addEventListener('input', (e) => this.handleCodeInput(e, index));
            input.addEventListener('keydown', (e) => this.handleCodeKeydown(e, index));
            input.addEventListener('paste', (e) => this.handleCodePaste(e));
        });

        // Form validation
        const emailInput = document.getElementById('email');
        const passwordInput = document.getElementById('password');
        
        if (emailInput) {
            emailInput.addEventListener('blur', () => this.validateEmail());
        }
        
        if (passwordInput) {
            passwordInput.addEventListener('blur', () => this.validatePassword());
        }

        // Enter key handling
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !this.isLoading) {
                if (this.requiresTwoFactor) {
                    this.handleTwoFactorVerification();
                } else {
                    this.handleLogin(e);
                }
            }
        });
    }

    checkExistingAuth() {
        // Check if user is already authenticated
        if (this.api.isAuthenticated()) {
            // Redirect to dashboard
            window.location.href = 'dashboard.html';
        }
    }

    initializeForm() {
        // Focus on email input
        const emailInput = document.getElementById('email');
        if (emailInput) {
            emailInput.focus();
        }

        // Load saved email if exists
        const savedEmail = localStorage.getItem('admin_email');
        if (savedEmail) {
            emailInput.value = savedEmail;
            document.getElementById('remember-me').checked = true;
        }
    }

    async handleLogin(e) {
        e.preventDefault();
        
        if (this.isLoading) return;

        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        const rememberMe = document.getElementById('remember-me').checked;

        // Validate inputs
        if (!this.validateForm(email, password)) {
            return;
        }

        this.setLoading(true);
        this.hideMessages();

        try {
            const response = await this.api.login(email, password);
            
            // Save email if remember me is checked
            if (rememberMe) {
                localStorage.setItem('admin_email', email);
            } else {
                localStorage.removeItem('admin_email');
            }

            // Check if two-factor authentication is required
            if (response.requires_two_factor) {
                this.showTwoFactorAuth();
                this.twoFactorToken = response.two_factor_token;
            } else {
                // Login successful
                this.showSuccess('Login successful! Redirecting...');
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 1000);
            }

        } catch (error) {
            console.error('Login error:', error);
            this.handleLoginError(error);
        } finally {
            this.setLoading(false);
        }
    }

    async handleTwoFactorVerification() {
        if (this.isLoading) return;

        const code = this.getTwoFactorCode();
        
        if (!code || code.length !== 6) {
            this.showError('Please enter a valid 6-digit code');
            return;
        }

        this.setLoading(true);
        this.hideMessages();

        try {
            const response = await this.api.verifyTwoFactor(this.twoFactorToken, code);
            
            // Two-factor verification successful
            this.showSuccess('Two-factor authentication successful! Redirecting...');
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1000);

        } catch (error) {
            console.error('Two-factor verification error:', error);
            this.showError('Invalid verification code. Please try again.');
            this.clearTwoFactorCode();
        } finally {
            this.setLoading(false);
        }
    }

    handleCodeInput(e, index) {
        const input = e.target;
        const value = input.value;
        
        // Only allow digits
        if (!/^\d$/.test(value)) {
            input.value = '';
            return;
        }

        // Move to next input
        if (value && index < 5) {
            const nextInput = input.parentNode.children[index + 1];
            if (nextInput) {
                nextInput.focus();
            }
        }
    }

    handleCodeKeydown(e, index) {
        const input = e.target;
        
        // Handle backspace
        if (e.key === 'Backspace' && !input.value && index > 0) {
            const prevInput = input.parentNode.children[index - 1];
            if (prevInput) {
                prevInput.focus();
            }
        }
        
        // Handle arrow keys
        if (e.key === 'ArrowLeft' && index > 0) {
            const prevInput = input.parentNode.children[index - 1];
            if (prevInput) {
                prevInput.focus();
            }
        }
        
        if (e.key === 'ArrowRight' && index < 5) {
            const nextInput = input.parentNode.children[index + 1];
            if (nextInput) {
                nextInput.focus();
            }
        }
    }

    handleCodePaste(e) {
        e.preventDefault();
        const pastedData = e.clipboardData.getData('text');
        const digits = pastedData.replace(/\D/g, '').slice(0, 6);
        
        const codeInputs = document.querySelectorAll('.code-input');
        codeInputs.forEach((input, index) => {
            input.value = digits[index] || '';
        });
        
        // Focus last filled input
        const lastFilledIndex = Math.min(digits.length - 1, 5);
        codeInputs[lastFilledIndex].focus();
    }

    getTwoFactorCode() {
        const codeInputs = document.querySelectorAll('.code-input');
        return Array.from(codeInputs).map(input => input.value).join('');
    }

    clearTwoFactorCode() {
        const codeInputs = document.querySelectorAll('.code-input');
        codeInputs.forEach(input => {
            input.value = '';
        });
        codeInputs[0].focus();
    }

    togglePasswordVisibility() {
        const passwordInput = document.getElementById('password');
        const passwordToggle = document.getElementById('password-toggle');
        
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            passwordToggle.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                    <line x1="1" y1="1" x2="23" y2="23"></line>
                </svg>
            `;
        } else {
            passwordInput.type = 'password';
            passwordToggle.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                    <circle cx="12" cy="12" r="3"></circle>
                </svg>
            `;
        }
    }

    validateForm(email, password) {
        let isValid = true;

        if (!this.validateEmail(email)) {
            isValid = false;
        }

        if (!this.validatePassword(password)) {
            isValid = false;
        }

        return isValid;
    }

    validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const emailInput = document.getElementById('email');
        
        if (!email) {
            this.showFieldError(emailInput, 'Email is required');
            return false;
        }
        
        if (!emailRegex.test(email)) {
            this.showFieldError(emailInput, 'Please enter a valid email address');
            return false;
        }
        
        this.clearFieldError(emailInput);
        return true;
    }

    validatePassword(password) {
        const passwordInput = document.getElementById('password');
        
        if (!password) {
            this.showFieldError(passwordInput, 'Password is required');
            return false;
        }
        
        if (password.length < 6) {
            this.showFieldError(passwordInput, 'Password must be at least 6 characters');
            return false;
        }
        
        this.clearFieldError(passwordInput);
        return true;
    }

    showFieldError(input, message) {
        this.clearFieldError(input);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.textContent = message;
        
        input.parentNode.appendChild(errorDiv);
        input.classList.add('error');
    }

    clearFieldError(input) {
        const existingError = input.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
        input.classList.remove('error');
    }

    handleLoginError(error) {
        let errorMessage = 'Login failed. Please try again.';
        
        if (error.status === 401) {
            errorMessage = 'Invalid email or password';
        } else if (error.status === 403) {
            errorMessage = 'Account is locked or disabled';
        } else if (error.status === 429) {
            errorMessage = 'Too many login attempts. Please try again later';
        } else if (error.status === 500) {
            errorMessage = 'Server error. Please try again later';
        } else if (error.message) {
            errorMessage = error.message;
        }
        
        this.showError(errorMessage);
    }

    showTwoFactorAuth() {
        const twoFactorAuth = document.getElementById('two-factor-auth');
        const loginForm = document.getElementById('login-form');
        
        if (twoFactorAuth && loginForm) {
            loginForm.style.display = 'none';
            twoFactorAuth.style.display = 'block';
            twoFactorAuth.classList.add('fade-in');
            
            // Focus first code input
            const firstCodeInput = twoFactorAuth.querySelector('.code-input');
            if (firstCodeInput) {
                firstCodeInput.focus();
            }
        }
    }

    showError(message) {
        const errorMessage = document.getElementById('error-message');
        const errorText = document.getElementById('error-text');
        
        if (errorMessage && errorText) {
            errorText.textContent = message;
            errorMessage.style.display = 'flex';
            errorMessage.classList.add('fade-in');
        }
    }

    showSuccess(message) {
        const successMessage = document.getElementById('success-message');
        const successText = document.getElementById('success-text');
        
        if (successMessage && successText) {
            successText.textContent = message;
            successMessage.style.display = 'flex';
            successMessage.classList.add('fade-in');
        }
    }

    hideMessages() {
        const errorMessage = document.getElementById('error-message');
        const successMessage = document.getElementById('success-message');
        
        if (errorMessage) {
            errorMessage.style.display = 'none';
            errorMessage.classList.remove('fade-in');
        }
        
        if (successMessage) {
            successMessage.style.display = 'none';
            successMessage.classList.remove('fade-in');
        }
    }

    setLoading(loading) {
        this.isLoading = loading;
        const loginBtn = document.getElementById('login-btn');
        
        if (loginBtn) {
            loginBtn.disabled = loading;
            loginBtn.classList.toggle('loading', loading);
        }
    }

    // Utility methods
    formatTimeAgo(timestamp) {
        const now = new Date();
        const time = new Date(timestamp);
        const diffInSeconds = Math.floor((now - time) / 1000);
        
        if (diffInSeconds < 60) {
            return 'Just now';
        } else if (diffInSeconds < 3600) {
            const minutes = Math.floor(diffInSeconds / 60);
            return `${minutes}m ago`;
        } else if (diffInSeconds < 86400) {
            const hours = Math.floor(diffInSeconds / 3600);
            return `${hours}h ago`;
        } else {
            const days = Math.floor(diffInSeconds / 86400);
            return `${days}d ago`;
        }
    }
}

// Initialize login when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.adminLogin = new AdminLogin();
});

// Add CSS for field errors
const style = document.createElement('style');
style.textContent = `
    .field-error {
        color: var(--accent-red);
        font-size: 0.8rem;
        margin-top: 0.25rem;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }
    
    .field-error::before {
        content: '⚠';
        font-size: 0.7rem;
    }
    
    .form-input.error {
        border-color: var(--accent-red);
        box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.1);
    }
    
    .toast {
        position: fixed;
        top: 20px;
        right: 20px;
        background-color: var(--secondary-bg);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md);
        padding: var(--spacing-md);
        color: var(--text-primary);
        box-shadow: var(--shadow-lg);
        z-index: 1000;
        max-width: 300px;
    }
    
    .toast-success {
        border-color: var(--accent-green);
        background-color: rgba(40, 167, 69, 0.1);
    }
    
    .toast-error {
        border-color: var(--accent-red);
        background-color: rgba(220, 53, 69, 0.1);
    }
    
    .toast-warning {
        border-color: var(--warning);
        background-color: rgba(255, 193, 7, 0.1);
    }
`;
document.head.appendChild(style);