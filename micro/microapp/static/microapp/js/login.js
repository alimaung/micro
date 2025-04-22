/**
 * Login Page JavaScript
 * Microfilm Processing System
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize dark mode based on system preference
    initTheme();
    
    // Set up form validation and submission
    setupFormValidation();
    
    // Set up password visibility toggle
    setupPasswordToggle();
    
    // Set up OTP input handling
    setupOTPInputs();
    
    // Set up modal and toast events
    setupNotifications();
});

/**
 * Initialize theme based on saved preference or system setting
 */
function initTheme() {
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    const storedTheme = localStorage.getItem('theme');
    const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    // Set initial theme
    if (storedTheme) {
        document.documentElement.setAttribute('data-theme', storedTheme);
    } else if (prefersDarkMode) {
        document.documentElement.setAttribute('data-theme', 'dark');
    } else {
        document.documentElement.setAttribute('data-theme', 'light');
    }
    
    // Add event listener for theme toggle
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }
}

/**
 * Set up form validation and submission
 */
function setupFormValidation() {
    const loginForm = document.getElementById('login-form');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const usernameError = document.getElementById('username-error');
    const passwordError = document.getElementById('password-error');
    const loginButton = document.getElementById('login-button');
    
    if (!loginForm) return;
    
    // Real-time validation for username
    usernameInput.addEventListener('input', function() {
        validateUsername(this.value);
    });
    
    // Real-time validation for password
    passwordInput.addEventListener('input', function() {
        validatePassword(this.value);
    });
    
    // Form submission
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const username = usernameInput.value.trim();
        const password = passwordInput.value;
        
        const isUsernameValid = validateUsername(username);
        const isPasswordValid = validatePassword(password);
        
        if (isUsernameValid && isPasswordValid) {
            // Show loading state
            loginButton.classList.add('loading');
            
            // Simulate server validation (for demo)
            setTimeout(function() {
                // For demo purposes, check some mock credentials
                if (username === 'admin@example.com' && password === 'password123') {
                    // Show loading overlay
                    showLoadingOverlay();
                    
                    // Either redirect or show 2FA
                    const usesTwoFA = Math.random() > 0.5; // Randomly determine if 2FA is needed
                    
                    if (usesTwoFA) {
                        setTimeout(function() {
                            hideLoadingOverlay();
                            show2FAModal();
                        }, 1500);
                    } else {
                        // Redirect to dashboard
                        setTimeout(function() {
                            window.location.href = '/microapp/dashboard/';
                        }, 2000);
                    }
                } else {
                    // Show error
                    showToast('Invalid username or password');
                    loginButton.classList.remove('loading');
                    
                    // Shake form
                    loginForm.classList.add('shake');
                    setTimeout(function() {
                        loginForm.classList.remove('shake');
                    }, 600);
                }
            }, 1000);
        } else {
            // Shake form for invalid inputs
            loginForm.classList.add('shake');
            setTimeout(function() {
                loginForm.classList.remove('shake');
            }, 600);
        }
    });
    
    /**
     * Validate username/email format
     * @param {string} username - Username or email to validate
     * @returns {boolean} - Whether the username is valid
     */
    function validateUsername(username) {
        let isValid = true;
        let errorMessage = '';
        
        if (!username) {
            isValid = false;
            errorMessage = 'Username is required';
        } else if (username.includes('@')) {
            // Check email format
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(username)) {
                isValid = false;
                errorMessage = 'Invalid email format';
            }
        }
        
        // Update UI
        if (usernameInput) {
            if (isValid) {
                usernameInput.classList.remove('error');
            } else {
                usernameInput.classList.add('error');
            }
        }
        
        if (usernameError) {
            usernameError.textContent = errorMessage;
        }
        
        return isValid;
    }
    
    /**
     * Validate password
     * @param {string} password - Password to validate
     * @returns {boolean} - Whether the password is valid
     */
    function validatePassword(password) {
        let isValid = true;
        let errorMessage = '';
        
        if (!password) {
            isValid = false;
            errorMessage = 'Password is required';
        } else if (password.length < 8) {
            // Only show this validation in a real app
            // Here we keep it simple for demo purposes
        }
        
        // Update UI
        if (passwordInput) {
            if (isValid) {
                passwordInput.classList.remove('error');
            } else {
                passwordInput.classList.add('error');
            }
        }
        
        if (passwordError) {
            passwordError.textContent = errorMessage;
        }
        
        return isValid;
    }
}

/**
 * Set up password visibility toggle
 */
function setupPasswordToggle() {
    const togglePasswordBtn = document.querySelector('.toggle-password');
    const passwordInput = document.getElementById('password');
    
    if (!togglePasswordBtn || !passwordInput) return;
    
    togglePasswordBtn.addEventListener('click', function() {
        const type = passwordInput.type === 'password' ? 'text' : 'password';
        passwordInput.type = type;
        
        // Update icon
        const icon = this.querySelector('i');
        if (icon) {
            icon.className = type === 'password' ? 'fas fa-eye' : 'fas fa-eye-slash';
        }
    });
}

/**
 * Set up OTP input handling for 2FA
 */
function setupOTPInputs() {
    const otpInputs = document.querySelectorAll('.otp-input');
    
    otpInputs.forEach(input => {
        input.addEventListener('keyup', function(e) {
            const index = parseInt(this.dataset.index);
            
            // Only allow numbers
            this.value = this.value.replace(/[^0-9]/g, '');
            
            // Move to next input when filled
            if (this.value && index < otpInputs.length) {
                const nextInput = document.querySelector(`.otp-input[data-index="${index + 1}"]`);
                if (nextInput) {
                    nextInput.focus();
                }
            }
            
            // Handle backspace
            if (e.key === 'Backspace' && !this.value && index > 1) {
                const prevInput = document.querySelector(`.otp-input[data-index="${index - 1}"]`);
                if (prevInput) {
                    prevInput.focus();
                }
            }
        });
        
        // Select all text on focus
        input.addEventListener('focus', function() {
            this.select();
        });
    });
    
    // Handle 2FA verification
    const verifyBtn = document.querySelector('.btn-verify');
    if (verifyBtn) {
        verifyBtn.addEventListener('click', function() {
            // Collect OTP
            let otp = '';
            otpInputs.forEach(input => {
                otp += input.value;
            });
            
            // Validate (for demo, any 6-digit code works)
            if (otp.length === 6 && /^\d+$/.test(otp)) {
                showLoadingOverlay();
                
                // Simulate verification
                setTimeout(function() {
                    hide2FAModal();
                    // Redirect to dashboard
                    window.location.href = '/microapp/dashboard/';
                }, 1500);
            } else {
                // Show error
                showToast('Invalid verification code');
                
                // Clear inputs
                otpInputs.forEach(input => {
                    input.value = '';
                });
                
                // Focus first input
                otpInputs[0].focus();
            }
        });
    }
    
    // Handle resend code
    const resendLink = document.querySelector('.resend-code a');
    if (resendLink) {
        resendLink.addEventListener('click', function(e) {
            e.preventDefault();
            showToast('A new code has been sent', 'success');
        });
    }
}

/**
 * Set up modal and toast notifications
 */
function setupNotifications() {
    // Handle 2FA modal close button
    const modalCloseBtn = document.querySelector('.modal-close');
    if (modalCloseBtn) {
        modalCloseBtn.addEventListener('click', function() {
            hide2FAModal();
        });
    }
    
    // Handle toast close button
    const toastCloseBtn = document.querySelector('.toast-close');
    if (toastCloseBtn) {
        toastCloseBtn.addEventListener('click', function() {
            hideToast();
        });
    }
}

/**
 * Show loading overlay
 */
function showLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.add('show');
    }
}

/**
 * Hide loading overlay
 */
function hideLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.remove('show');
    }
}

/**
 * Show 2FA modal
 */
function show2FAModal() {
    const modal = document.getElementById('twofa-modal');
    if (modal) {
        modal.classList.add('show');
        
        // Focus first OTP input
        const firstInput = modal.querySelector('.otp-input[data-index="1"]');
        if (firstInput) {
            setTimeout(() => {
                firstInput.focus();
            }, 300);
        }
    }
}

/**
 * Hide 2FA modal
 */
function hide2FAModal() {
    const modal = document.getElementById('twofa-modal');
    if (modal) {
        modal.classList.remove('show');
    }
}

/**
 * Show toast notification
 * @param {string} message - Message to display
 * @param {string} type - Type of notification (success, error, warning, info)
 */
function showToast(message, type = 'error') {
    const toast = document.getElementById('toast');
    if (!toast) return;
    
    const toastMessage = toast.querySelector('.toast-message');
    const toastIcon = toast.querySelector('.toast-icon');
    
    if (toastMessage) {
        toastMessage.textContent = message;
    }
    
    // Update border color
    toast.style.borderLeftColor = getColorForType(type);
    
    // Update icon
    if (toastIcon) {
        toastIcon.className = `toast-icon fas ${getIconForType(type)}`;
        toastIcon.style.color = getColorForType(type);
    }
    
    // Show toast
    toast.classList.add('show');
    
    // Auto hide after 5 seconds
    setTimeout(hideToast, 5000);
}

/**
 * Hide toast notification
 */
function hideToast() {
    const toast = document.getElementById('toast');
    if (toast) {
        toast.classList.remove('show');
    }
}

/**
 * Get color for notification type
 * @param {string} type - Type of notification
 * @returns {string} - CSS color value
 */
function getColorForType(type) {
    switch (type) {
        case 'success':
            return '#28a745';
        case 'error':
            return '#dc3545';
        case 'warning':
            return '#ffc107';
        case 'info':
            return '#17a2b8';
        default:
            return '#dc3545';
    }
}

/**
 * Get icon for notification type
 * @param {string} type - Type of notification
 * @returns {string} - FontAwesome icon class
 */
function getIconForType(type) {
    switch (type) {
        case 'success':
            return 'fa-check-circle';
        case 'error':
            return 'fa-exclamation-circle';
        case 'warning':
            return 'fa-exclamation-triangle';
        case 'info':
            return 'fa-info-circle';
        default:
            return 'fa-exclamation-circle';
    }
} 