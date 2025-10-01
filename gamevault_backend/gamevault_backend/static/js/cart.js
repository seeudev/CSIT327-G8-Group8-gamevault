/**
 * Cart JavaScript
 * Handles shopping cart functionality
 */

const Cart = {
    // Cart data
    items: [],
    totalItems: 0,
    totalPrice: 0,
    
    // Initialize cart
    init() {
        this.loadCart();
        this.renderCart();
        this.setupEventListeners();
    },
    
    // Load cart from localStorage
    loadCart() {
        const cartData = localStorage.getItem('gamevault_cart');
        if (cartData) {
            const cart = JSON.parse(cartData);
            this.items = cart.items || [];
            this.totalItems = cart.totalItems || 0;
            this.totalPrice = cart.totalPrice || 0;
        }
    },
    
    // Save cart to localStorage
    saveCart() {
        const cartData = {
            items: this.items,
            totalItems: this.totalItems,
            totalPrice: this.totalPrice
        };
        localStorage.setItem('gamevault_cart', JSON.stringify(cartData));
        this.updateCartCount();
    },
    
    // Render cart items
    renderCart() {
        const cartContent = document.getElementById('cartContent');
        const cartSummary = document.getElementById('cartSummary');
        const emptyCart = document.getElementById('emptyCart');
        
        if (this.items.length === 0) {
            if (cartContent) cartContent.style.display = 'none';
            if (cartSummary) cartSummary.style.display = 'none';
            if (emptyCart) emptyCart.style.display = 'block';
            return;
        }
        
        if (emptyCart) emptyCart.style.display = 'none';
        if (cartSummary) cartSummary.style.display = 'block';
        
        if (cartContent) {
            cartContent.innerHTML = `
                <div class="cart-items">
                    ${this.items.map(item => this.renderCartItem(item)).join('')}
                </div>
            `;
        }
        
        this.updateSummary();
    },
    
    // Render individual cart item
    renderCartItem(item) {
        return `
            <div class="cart-item" data-item-id="${item.id}">
                <div class="item-image">
                    <img src="${item.cover_image_url || '/static/images/placeholder.png'}" 
                         alt="${item.title}" 
                         onerror="this.src='/static/images/placeholder.png'">
                </div>
                
                <div class="item-details">
                    <h3 class="item-title">
                        <a href="/store/game/${item.slug || '#'}">${item.title}</a>
                    </h3>
                    <p class="item-developer">${item.developer || ''}</p>
                    <p class="item-genre">${item.genre || ''}</p>
                    <p class="item-price">$${item.price.toFixed(2)}</p>
                </div>
                
                <div class="item-quantity">
                    <label>Quantity:</label>
                    <div class="quantity-controls">
                        <button onclick="Cart.updateQuantity(${item.id}, ${item.quantity - 1})" 
                                class="quantity-btn" ${item.quantity <= 1 ? 'disabled' : ''}>-</button>
                        <input type="number" min="1" value="${item.quantity}" 
                               onchange="Cart.updateQuantity(${item.id}, parseInt(this.value) || 1)"
                               class="quantity-input">
                        <button onclick="Cart.updateQuantity(${item.id}, ${item.quantity + 1})" 
                                class="quantity-btn">+</button>
                    </div>
                </div>
                
                <div class="item-total">
                    <p class="item-total-price">$${(item.price * item.quantity).toFixed(2)}</p>
                    <button onclick="Cart.removeItem(${item.id})" 
                            class="remove-item-btn" title="Remove item">×</button>
                </div>
            </div>
        `;
    },
    
    // Update item quantity
    updateQuantity(itemId, newQuantity) {
        if (newQuantity < 1) {
            this.removeItem(itemId);
            return;
        }
        
        const item = this.items.find(item => item.id === itemId);
        if (item) {
            item.quantity = newQuantity;
            this.calculateTotals();
            this.saveCart();
            this.renderCart();
        }
    },
    
    // Remove item from cart
    removeItem(itemId) {
        if (confirm('Are you sure you want to remove this item from your cart?')) {
            this.items = this.items.filter(item => item.id !== itemId);
            this.calculateTotals();
            this.saveCart();
            this.renderCart();
        }
    },
    
    // Calculate totals
    calculateTotals() {
        this.totalItems = this.items.reduce((sum, item) => sum + item.quantity, 0);
        this.totalPrice = this.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    },
    
    // Update summary section
    updateSummary() {
        const subtotalText = document.getElementById('subtotal-text');
        const subtotalPrice = document.getElementById('subtotal-price');
        const totalPrice = document.getElementById('total-price');
        const cartItemsCount = document.getElementById('cart-items-count');
        
        if (subtotalText) {
            subtotalText.textContent = `Subtotal (${this.totalItems} items):`;
        }
        if (subtotalPrice) {
            subtotalPrice.textContent = `$${this.totalPrice.toFixed(2)}`;
        }
        if (totalPrice) {
            totalPrice.textContent = `$${this.totalPrice.toFixed(2)}`;
        }
        if (cartItemsCount) {
            cartItemsCount.textContent = `${this.totalItems} item${this.totalItems !== 1 ? 's' : ''} in your cart`;
        }
    },
    
    // Update cart count in navigation
    updateCartCount() {
        const cartCount = document.getElementById('cart-count');
        if (cartCount) {
            cartCount.textContent = this.totalItems;
        }
    },
    
    // Clear entire cart
    clearCart() {
        if (confirm('Are you sure you want to clear your cart?')) {
            this.items = [];
            this.totalItems = 0;
            this.totalPrice = 0;
            this.saveCart();
            this.renderCart();
        }
    },
    
    // Proceed to checkout
    proceedToCheckout() {
        if (this.items.length === 0) {
            this.showError('Your cart is empty');
            return;
        }
        
        // Check if user is authenticated
        const user = JSON.parse(localStorage.getItem('gamevault_user') || 'null');
        if (!user) {
            window.location.href = '/login/';
            return;
        }
        
        // Show loading state
        const checkoutBtn = document.getElementById('checkoutBtn');
        if (checkoutBtn) {
            checkoutBtn.disabled = true;
            checkoutBtn.textContent = 'Processing...';
        }
        
        // Simulate checkout process
        setTimeout(() => {
            // Clear cart
            this.clearCart();
            
            // Redirect to success page
            window.location.href = '/store/checkout/success/';
        }, 2000);
    },
    
    // Show error message
    showError(message) {
        const errorDiv = document.getElementById('checkout-error');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
            
            setTimeout(() => {
                errorDiv.style.display = 'none';
            }, 5000);
        }
    },
    
    // Setup event listeners
    setupEventListeners() {
        // Handle quantity input changes
        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('quantity-input')) {
                const itemId = parseInt(e.target.closest('.cart-item').dataset.itemId);
                const newQuantity = parseInt(e.target.value) || 1;
                this.updateQuantity(itemId, newQuantity);
            }
        });
    }
};

// Global functions called from HTML
function clearCart() {
    Cart.clearCart();
}

function proceedToCheckout() {
    Cart.proceedToCheckout();
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    Cart.init();
});

// Make Cart globally available
window.Cart = Cart;
