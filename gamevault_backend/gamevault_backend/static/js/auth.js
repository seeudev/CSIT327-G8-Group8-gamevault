/**
 * Authentication JavaScript
 * Handles login, registration, and password visibility toggles
 */

// Toggle password visibility
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const button = input.nextElementSibling;
    
    if (input.type === 'password') {
        input.type = 'text';
        button.textContent = '👁️';
    } else {
        input.type = 'password';
        button.textContent = '👁️‍🗨️';
    }
}

// Form validation
function validateForm(form) {
    const formData = new FormData(form);
    const errors = {};
    
    // Clear existing errors
    document.querySelectorAll('.field-error').forEach(error => error.remove());
    document.querySelectorAll('.error').forEach(input => input.classList.remove('error'));
    
    // Validate registration form
    if (form.id === 'registerForm') {
        const username = formData.get('username');
        const email = formData.get('email');
        const password = formData.get('password');
        const passwordConfirm = formData.get('password_confirm');
        
        // Username validation
        if (username.length < 3) {
            errors.username = 'Username must be at least 3 characters long';
        }
        
        // Email validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            errors.email = 'Please enter a valid email address';
        }
        
        // Password validation
        if (password.length < 8) {
            errors.password = 'Password must be at least 8 characters long';
        }
        
        // Password confirmation
        if (password !== passwordConfirm) {
            errors.password_confirm = 'Passwords do not match';
        }
    }
    
    // Display errors
    Object.keys(errors).forEach(field => {
        const input = document.getElementById(field);
        if (input) {
            input.classList.add('error');
            const errorSpan = document.createElement('span');
            errorSpan.className = 'field-error';
            errorSpan.textContent = errors[field];
            input.parentNode.appendChild(errorSpan);
        }
    });
    
    return Object.keys(errors).length === 0;
}

// Handle form submission with validation
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('.auth-form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
    });
});
