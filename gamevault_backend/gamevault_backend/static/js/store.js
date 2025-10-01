/**
 * Store JavaScript
 * Handles game library, search, filtering, and cart operations
 */

const Store = {
    // Game data
    games: [],
    filteredGames: [],
    
    // Filter state
    filters: {
        search: '',
        genre: '',
        sort: 'featured'
    },
    
    // Initialize store functionality
    init() {
        this.loadGames();
        this.setupEventListeners();
        this.applyFilters();
    },
    
    // Load games from the page
    loadGames() {
        const gameCards = document.querySelectorAll('.game-card');
        this.games = Array.from(gameCards).map(card => ({
            id: parseInt(card.dataset.gameId),
            element: card,
            title: card.querySelector('.game-title').textContent,
            genre: card.querySelector('.game-genre').textContent,
            developer: card.querySelector('.game-developer').textContent,
            price: parseFloat(card.querySelector('.current-price').textContent.replace('$', '')),
            inStock: !card.querySelector('.out-of-stock-overlay')
        }));
        this.filteredGames = [...this.games];
    },
    
    // Setup event listeners
    setupEventListeners() {
        // Search input
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filters.search = e.target.value.toLowerCase();
                this.applyFilters();
            });
        }
        
        // Genre filter
        const genreFilter = document.getElementById('genreFilter');
        if (genreFilter) {
            genreFilter.addEventListener('change', (e) => {
                this.filters.genre = e.target.value;
                this.applyFilters();
            });
        }
        
        // Sort filter
        const sortFilter = document.getElementById('sortFilter');
        if (sortFilter) {
            sortFilter.addEventListener('change', (e) => {
                this.filters.sort = e.target.value;
                this.applyFilters();
            });
        }
    },
    
    // Apply filters and update display
    applyFilters() {
        let filtered = [...this.games];
        
        // Apply search filter
        if (this.filters.search) {
            filtered = filtered.filter(game => 
                game.title.toLowerCase().includes(this.filters.search) ||
                game.developer.toLowerCase().includes(this.filters.search) ||
                game.genre.toLowerCase().includes(this.filters.search)
            );
        }
        
        // Apply genre filter
        if (this.filters.genre) {
            filtered = filtered.filter(game => game.genre === this.filters.genre);
        }
        
        // Apply sorting
        filtered.sort((a, b) => {
            switch (this.filters.sort) {
                case 'title':
                    return a.title.localeCompare(b.title);
                case '-title':
                    return b.title.localeCompare(a.title);
                case 'price':
                    return a.price - b.price;
                case '-price':
                    return b.price - a.price;
                default:
                    return 0; // Keep original order for featured
            }
        });
        
        this.filteredGames = filtered;
        this.updateDisplay();
    },
    
    // Update the display
    updateDisplay() {
        const gamesGrid = document.getElementById('gamesGrid');
        if (!gamesGrid) return;
        
        // Hide all games
        this.games.forEach(game => {
            game.element.style.display = 'none';
        });
        
        // Show filtered games
        this.filteredGames.forEach(game => {
            game.element.style.display = 'block';
        });
        
        // Update footer
        const footer = document.querySelector('.library-footer p');
        if (footer) {
            const count = this.filteredGames.length;
            footer.textContent = `Showing ${count} game${count !== 1 ? 's' : ''}`;
        }
        
        // Show/hide no games message
        const noGames = document.querySelector('.no-games');
        if (noGames) {
            noGames.style.display = this.filteredGames.length === 0 ? 'block' : 'none';
        }
    },
    
    // Add game to cart
    addToCart(gameId) {
        const game = this.games.find(g => g.id === gameId);
        if (!game || !game.inStock) {
            this.showMessage('Game is not available for purchase', 'error');
            return;
        }
        
        // Get cart from localStorage
        let cart = JSON.parse(localStorage.getItem('gamevault_cart') || '{"items": [], "totalItems": 0, "totalPrice": 0}');
        
        // Check if item already in cart
        const existingItem = cart.items.find(item => item.id === gameId);
        
        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            cart.items.push({
                id: gameId,
                title: game.title,
                price: game.price,
                quantity: 1
            });
        }
        
        // Update totals
        cart.totalItems = cart.items.reduce((sum, item) => sum + item.quantity, 0);
        cart.totalPrice = cart.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        
        // Save to localStorage
        localStorage.setItem('gamevault_cart', JSON.stringify(cart));
        
        // Update UI
        this.updateCartButton(gameId);
        this.updateCartCount();
        this.showMessage('Game added to cart!', 'success');
    },
    
    // Update cart button state
    updateCartButton(gameId) {
        const button = document.querySelector(`[data-game-id="${gameId}"]`);
        if (button) {
            button.textContent = 'In Cart';
            button.classList.remove('btn-primary');
            button.classList.add('btn-success');
            button.disabled = true;
        }
    },
    
    // Update cart count in navigation
    updateCartCount() {
        const cart = JSON.parse(localStorage.getItem('gamevault_cart') || '{"items": [], "totalItems": 0, "totalPrice": 0}');
        const cartCount = document.getElementById('cart-count');
        if (cartCount) {
            cartCount.textContent = cart.totalItems;
        }
    },
    
    // Show message to user
    showMessage(message, type = 'info') {
        // Remove existing messages
        const existingMessage = document.querySelector('.store-message');
        if (existingMessage) {
            existingMessage.remove();
        }
        
        // Create new message
        const messageDiv = document.createElement('div');
        messageDiv.className = `store-message alert alert-${type === 'error' ? 'danger' : 'success'}`;
        messageDiv.textContent = message;
        
        // Insert at the top of the page
        const container = document.querySelector('.game-library');
        if (container) {
            container.insertBefore(messageDiv, container.firstChild);
            
            // Auto-remove after 3 seconds
            setTimeout(() => {
                messageDiv.remove();
            }, 3000);
        }
    }
};

// Clear filters function (called from HTML)
function clearFilters() {
    Store.filters = { search: '', genre: '', sort: 'featured' };
    
    // Reset form elements
    const searchInput = document.getElementById('searchInput');
    const genreFilter = document.getElementById('genreFilter');
    const sortFilter = document.getElementById('sortFilter');
    
    if (searchInput) searchInput.value = '';
    if (genreFilter) genreFilter.value = '';
    if (sortFilter) sortFilter.value = 'featured';
    
    Store.applyFilters();
}

// Add to cart function (called from HTML)
function addToCart(gameId) {
    Store.addToCart(gameId);
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    Store.init();
});

// Make Store globally available
window.Store = Store;
