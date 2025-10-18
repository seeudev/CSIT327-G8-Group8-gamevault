/**
 * Admin JavaScript
 * Handles admin dashboard functionality for GameVault Module 7
 */

const Admin = {
    // Initialize admin functionality
    init() {
        this.loadDashboardStats();
        this.setupEventListeners();
        this.initializeSidebar();
    },
    
    // Load dashboard statistics (Module 7)
    async loadDashboardStats() {
        try {
            const response = await fetch('/store/api/admin/stats/');
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.updateStatsDisplay(data.stats);
                }
            }
        } catch (error) {
            console.error('Error loading dashboard stats:', error);
        }
    },
    
    // Update stats display
    updateStatsDisplay(stats) {
        // Update metric cards if they exist on the page
        const metricElements = {
            'total-users': stats.total_users || 0,
            'total-sales': (stats.total_sales || 0).toFixed(2),
            'total-transactions': stats.total_transactions || 0,
            'total-games': stats.total_games || 0
        };
        
        Object.keys(metricElements).forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = metricElements[id];
            }
        });
        
        // Update most downloaded games if container exists
        if (stats.most_downloaded_games && stats.most_downloaded_games.length > 0) {
            this.updateMostDownloaded(stats.most_downloaded_games);
        }
    },
    
    // Update most downloaded games display
    updateMostDownloaded(games) {
        const container = document.getElementById('mostDownloadedGames');
        if (!container) return;
        
        container.innerHTML = games.map((game, index) => `
            <div class="download-item">
                <span class="rank">#${index + 1}</span>
                <span class="game-name">${this.escapeHtml(game.title)}</span>
                <span class="download-count">${game.downloads} downloads</span>
            </div>
        `).join('');
    },
    
    // Setup event listeners
    setupEventListeners() {
        // Refresh stats button
        const refreshBtn = document.getElementById('refreshStats');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadDashboardStats();
            });
        }
        
        // Auto-refresh every 60 seconds
        if (document.querySelector('.admin-dashboard-container')) {
            setInterval(() => {
                this.loadDashboardStats();
            }, 60000);
        }
    },
    
    // Initialize sidebar navigation
    initializeSidebar() {
        const sidebar = document.getElementById('adminSidebar');
        if (!sidebar) return;
        
        // Highlight active menu item based on current URL
        const currentPath = window.location.pathname;
        const menuItems = sidebar.querySelectorAll('.menu-item');
        
        menuItems.forEach(item => {
            const link = item.querySelector('a');
            if (link && link.getAttribute('href') === currentPath) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
    },
    
    // Utility: Escape HTML
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },
    
    // Utility: Format date
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    // Utility: Format time ago
    formatTimeAgo(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)} minutes ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)} hours ago`;
        return `${Math.floor(diff / 86400000)} days ago`;
    }
};

// Data table utilities
const DataTable = {
    sortState: {
        column: null,
        ascending: true
    },
    
    // Sort table by column
    sortByColumn(data, column) {
        const sorted = [...data];
        sorted.sort((a, b) => {
            let aVal = a[column];
            let bVal = b[column];
            
            // Handle different data types
            if (typeof aVal === 'string') {
                aVal = aVal.toLowerCase();
                bVal = bVal.toLowerCase();
            }
            
            if (aVal < bVal) return this.sortState.ascending ? -1 : 1;
            if (aVal > bVal) return this.sortState.ascending ? 1 : -1;
            return 0;
        });
        
        return sorted;
    },
    
    // Filter data by search query
    filterData(data, query, fields) {
        if (!query) return data;
        
        const lowerQuery = query.toLowerCase();
        return data.filter(item => {
            return fields.some(field => {
                const value = item[field];
                if (value === null || value === undefined) return false;
                return String(value).toLowerCase().includes(lowerQuery);
            });
        });
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    Admin.init();
});

// Make utilities globally available
window.Admin = Admin;
window.DataTable = DataTable;
