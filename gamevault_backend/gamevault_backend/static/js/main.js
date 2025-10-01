/**
 * Main JavaScript file for GameVault
 * Handles common functionality across the application
 */

// Global state management
const GameVault = {
    // User authentication state
    user: null,
    isAuthenticated: false,
    
    // Cart state
    cart: {
        items: [],
        totalItems: 0,
        totalPrice: 0
    },
    
    // Initialize the application
    init() {
        this.loadUser();
        this.loadCart();
        this.updateCartUI();
        this.setupEventListeners();
    },
    
    // Load user from localStorage
    loadUser() {
        const userData = localStorage.getItem('gamevault_user');
        if (userData) {
            this.user = JSON.parse(userData);
            this.isAuthenticated = true;
        }
    },
    
    // Load cart from localStorage
    loadCart() {
        const cartData = localStorage.getItem('gamevault_cart');
        if (cartData) {
            const cart = JSON.parse(cartData);
            this.cart = cart;
        }
    },
    
    // Save cart to localStorage
    saveCart() {
        localStorage.setItem('gamevault_cart', JSON.stringify(this.cart));
        this.updateCartUI();
    },
    
    // Update cart UI elements
    updateCartUI() {
        const cartCount = document.getElementById('cart-count');
        if (cartCount) {
            cartCount.textContent = this.cart.totalItems;
        }
    },
    
    // Setup global event listeners
    setupEventListeners() {
        // Handle form submissions
        document.addEventListener('submit', (e) => {
            if (e.target.classList.contains('auth-form')) {
                this.handleAuthForm(e);
            }
        });
        
        // Handle cart operations
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('add-to-cart-btn')) {
                e.preventDefault();
                const gameId = parseInt(e.target.dataset.gameId);
                this.addToCart(gameId);
            }
        });
    },
    
    // Handle authentication form submissions
    async handleAuthForm(e) {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        
        // Disable submit button
        submitBtn.disabled = true;
        submitBtn.textContent = 'Processing...';
        
        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    // Store user data
                    localStorage.setItem('gamevault_user', JSON.stringify(data.user));
                    this.user = data.user;
                    this.isAuthenticated = true;
                    
                    // Redirect to home
                    window.location.href = data.redirect_url || '/';
                } else {
                    this.showError(data.error || 'Authentication failed');
                }
            } else {
                this.showError('Authentication failed. Please try again.');
            }
        } catch (error) {
            console.error('Auth error:', error);
            this.showError('Network error. Please try again.');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = form.id === 'loginForm' ? 'Sign In' : 'Create Account';
        }
    },
    
    // Add item to cart
    addToCart(gameId) {
        // This will be implemented in store.js
        if (window.Store && window.Store.addToCart) {
            window.Store.addToCart(gameId);
        }
    },
    
    // Show error message
    showError(message) {
        // Remove existing error messages
        const existingError = document.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }
        
        // Create new error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message alert alert-danger';
        errorDiv.innerHTML = `<span>⚠️ ${message}</span>`;
        
        // Insert at the top of the form
        const form = document.querySelector('.auth-form');
        if (form) {
            form.insertBefore(errorDiv, form.firstChild);
        }
    },
    
    // Format currency
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    },
    
    // Logout user
    logout() {
        localStorage.removeItem('gamevault_user');
        localStorage.removeItem('gamevault_cart');
        this.user = null;
        this.isAuthenticated = false;
        this.cart = { items: [], totalItems: 0, totalPrice: 0 };
        window.location.href = '/login/';
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    GameVault.init();
});

// Make GameVault globally available
window.GameVault = GameVault;
