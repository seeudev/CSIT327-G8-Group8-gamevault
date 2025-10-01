/**
 * Admin JavaScript
 * Handles admin dashboard functionality
 */

const Admin = {
    // Initialize admin functionality
    init() {
        this.loadStats();
        this.loadRecentActivity();
        this.setupEventListeners();
    },
    
    // Load dashboard statistics
    async loadStats() {
        try {
            const response = await fetch('/api/admin/stats/');
            if (response.ok) {
                const stats = await response.json();
                this.updateStatsDisplay(stats);
            }
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    },
    
    // Update stats display
    updateStatsDisplay(stats) {
        const elements = {
            'total-games': stats.total_games || 0,
            'total-users': stats.total_users || 0,
            'total-orders': stats.total_orders || 0,
            'total-revenue': (stats.total_revenue || 0).toFixed(2)
        };
        
        Object.keys(elements).forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = elements[id];
            }
        });
    },
    
    // Load recent activity
    async loadRecentActivity() {
        try {
            const response = await fetch('/api/admin/activity/');
            if (response.ok) {
                const activity = await response.json();
                this.updateActivityDisplay(activity);
            }
        } catch (error) {
            console.error('Error loading activity:', error);
        }
    },
    
    // Update activity display
    updateActivityDisplay(activities) {
        const container = document.getElementById('recentActivity');
        if (!container) return;
        
        if (activities.length === 0) {
            container.innerHTML = '<p>No recent activity</p>';
            return;
        }
        
        container.innerHTML = activities.map(activity => `
            <div class="activity-item">
                <div class="activity-icon">
                    <i class="fas ${this.getActivityIcon(activity.type)}"></i>
                </div>
                <div class="activity-content">
                    <p class="activity-text">${activity.description}</p>
                    <span class="activity-time">${this.formatTime(activity.created_at)}</span>
                </div>
            </div>
        `).join('');
    },
    
    // Get icon for activity type
    getActivityIcon(type) {
        const icons = {
            'user_registered': 'fa-user-plus',
            'game_added': 'fa-gamepad',
            'order_created': 'fa-shopping-cart',
            'user_login': 'fa-sign-in-alt'
        };
        return icons[type] || 'fa-info-circle';
    },
    
    // Format time
    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)} minutes ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)} hours ago`;
        return `${Math.floor(diff / 86400000)} days ago`;
    },
    
    // Setup event listeners
    setupEventListeners() {
        // Refresh stats button
        const refreshBtn = document.getElementById('refreshStats');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadStats();
                this.loadRecentActivity();
            });
        }
        
        // Auto-refresh every 30 seconds
        setInterval(() => {
            this.loadStats();
            this.loadRecentActivity();
        }, 30000);
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    Admin.init();
});

// Make Admin globally available
window.Admin = Admin;
