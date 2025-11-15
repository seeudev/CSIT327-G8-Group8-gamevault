/**
 * Analytics Dashboard JavaScript - Module 15
 * Handles data fetching, chart rendering, and user interactions
 */

// Chart instances
let salesTrendChart = null;
let categoryChart = null;

// Current filter state
let currentFilters = {
    days: 30,
    category: '',
    period: 'daily'
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeFilters();
    loadAnalyticsData();
    
    // Set up event listeners
    document.getElementById('applyFilters').addEventListener('click', applyFilters);
    document.getElementById('refreshData').addEventListener('click', () => loadAnalyticsData());
    
    // Export button listeners
    document.querySelectorAll('.btn-export').forEach(btn => {
        btn.addEventListener('click', function() {
            const type = this.dataset.type;
            const format = this.dataset.format;
            exportData(type, format);
        });
    });
});

/**
 * Initialize filter values from URL params or defaults
 */
function initializeFilters() {
    const urlParams = new URLSearchParams(window.location.search);
    
    const days = urlParams.get('days') || '30';
    const category = urlParams.get('category') || '';
    const period = urlParams.get('period') || 'daily';
    
    document.getElementById('dateRange').value = days;
    document.getElementById('categoryFilter').value = category;
    document.getElementById('chartPeriod').value = period;
    
    currentFilters = { days, category, period };
}

/**
 * Apply filters and reload data
 */
function applyFilters() {
    currentFilters.days = document.getElementById('dateRange').value;
    currentFilters.category = document.getElementById('categoryFilter').value;
    currentFilters.period = document.getElementById('chartPeriod').value;
    
    // Update URL params
    const params = new URLSearchParams();
    params.set('days', currentFilters.days);
    if (currentFilters.category) params.set('category', currentFilters.category);
    params.set('period', currentFilters.period);
    
    // Update URL without reload
    window.history.pushState({}, '', `${window.location.pathname}?${params.toString()}`);
    
    // Reload data
    loadAnalyticsData();
}

/**
 * Load all analytics data
 */
async function loadAnalyticsData() {
    showLoading(true);
    
    try {
        // Load data in parallel
        await Promise.all([
            loadOverviewData(),
            loadSalesTrend(),
            loadCategoryPerformance(),
            loadTopGames()
        ]);
        
        showMessage('Analytics data loaded successfully', 'success');
    } catch (error) {
        console.error('Error loading analytics:', error);
        showMessage('Failed to load analytics data: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

/**
 * Load overview metrics
 */
async function loadOverviewData() {
    const params = new URLSearchParams();
    params.set('days', currentFilters.days);
    
    const response = await fetch(`/store/api/analytics/overview/?${params.toString()}`, {
        headers: {
            'X-CSRFToken': getCSRFToken(),
        }
    });
    
    if (!response.ok) {
        throw new Error('Failed to load overview data');
    }
    
    const result = await response.json();
    
    if (result.success) {
        updateMetrics(result.data.overview);
    } else {
        throw new Error(result.error || 'Unknown error');
    }
}

/**
 * Update metric cards
 */
function updateMetrics(data) {
    document.getElementById('totalRevenue').textContent = `$${data.total_revenue.toFixed(2)}`;
    document.getElementById('totalOrders').textContent = data.total_orders.toLocaleString();
    document.getElementById('itemsSold').textContent = data.total_items_sold.toLocaleString();
    document.getElementById('activeUsers').textContent = data.active_users.toLocaleString();
    document.getElementById('newUsers').textContent = data.new_users.toLocaleString();
    document.getElementById('avgOrderValue').textContent = `$${data.avg_order_value.toFixed(2)}`;
}

/**
 * Load sales trend data and render chart
 */
async function loadSalesTrend() {
    const params = new URLSearchParams();
    params.set('days', currentFilters.days);
    params.set('period', currentFilters.period);
    if (currentFilters.category) params.set('category', currentFilters.category);
    
    const response = await fetch(`/store/api/analytics/sales-trend/?${params.toString()}`, {
        headers: {
            'X-CSRFToken': getCSRFToken(),
        }
    });
    
    if (!response.ok) {
        throw new Error('Failed to load sales trend');
    }
    
    const result = await response.json();
    
    if (result.success) {
        renderSalesTrendChart(result.data.sales_trend);
    } else {
        throw new Error(result.error || 'Unknown error');
    }
}

/**
 * Render sales trend chart using Chart.js
 */
function renderSalesTrendChart(data) {
    const ctx = document.getElementById('salesTrendChart').getContext('2d');
    
    // Destroy existing chart
    if (salesTrendChart) {
        salesTrendChart.destroy();
    }
    
    // Format labels based on period
    const labels = data.map(item => {
        const date = new Date(item.date);
        if (currentFilters.period === 'monthly') {
            return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
        } else if (currentFilters.period === 'weekly') {
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        } else {
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        }
    });
    
    salesTrendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Revenue ($)',
                    data: data.map(item => item.revenue),
                    borderColor: '#e63946',
                    backgroundColor: 'rgba(230, 57, 70, 0.1)',
                    tension: 0.4,
                    fill: true,
                    yAxisID: 'y'
                },
                {
                    label: 'Orders',
                    data: data.map(item => item.orders),
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    tension: 0.4,
                    fill: true,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#e0e0e0',
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#e63946',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                if (context.dataset.yAxisID === 'y') {
                                    label += '$' + context.parsed.y.toFixed(2);
                                } else {
                                    label += context.parsed.y;
                                }
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#a0a0a0'
                    }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#a0a0a0',
                        callback: function(value) {
                            return '$' + value;
                        }
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    grid: {
                        drawOnChartArea: false
                    },
                    ticks: {
                        color: '#a0a0a0'
                    }
                }
            }
        }
    });
}

/**
 * Load category performance data
 */
async function loadCategoryPerformance() {
    const params = new URLSearchParams();
    params.set('days', currentFilters.days);
    
    const response = await fetch(`/store/api/analytics/category-performance/?${params.toString()}`, {
        headers: {
            'X-CSRFToken': getCSRFToken(),
        }
    });
    
    if (!response.ok) {
        throw new Error('Failed to load category performance');
    }
    
    const result = await response.json();
    
    if (result.success) {
        renderCategoryChart(result.data.categories);
    } else {
        throw new Error(result.error || 'Unknown error');
    }
}

/**
 * Render category performance chart
 */
function renderCategoryChart(data) {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    
    // Destroy existing chart
    if (categoryChart) {
        categoryChart.destroy();
    }
    
    // Colors for categories
    const colors = [
        '#e63946',
        '#3498db',
        '#2ecc71',
        '#f39c12',
        '#9b59b6',
        '#1abc9c',
        '#e74c3c',
        '#34495e'
    ];
    
    categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(item => item.name),
            datasets: [{
                label: 'Revenue',
                data: data.map(item => item.revenue),
                backgroundColor: colors.slice(0, data.length),
                borderColor: '#1a1a1a',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'right',
                    labels: {
                        color: '#e0e0e0',
                        font: {
                            size: 12
                        },
                        padding: 15
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#e63946',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const percentage = data[context.dataIndex].percentage;
                            return `${label}: $${value.toFixed(2)} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Load top games data
 */
async function loadTopGames() {
    const params = new URLSearchParams();
    params.set('days', currentFilters.days);
    if (currentFilters.category) params.set('category', currentFilters.category);
    params.set('limit', 10);
    
    const response = await fetch(`/store/api/analytics/top-games/?${params.toString()}`, {
        headers: {
            'X-CSRFToken': getCSRFToken(),
        }
    });
    
    if (!response.ok) {
        throw new Error('Failed to load top games');
    }
    
    const result = await response.json();
    
    if (result.success) {
        renderTopGamesTable(result.data.top_games);
    } else {
        throw new Error(result.error || 'Unknown error');
    }
}

/**
 * Render top games table
 */
function renderTopGamesTable(games) {
    const tbody = document.getElementById('topGamesTable');
    
    if (games.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="empty-state">No sales data available for this period</td></tr>';
        return;
    }
    
    tbody.innerHTML = games.map((game, index) => `
        <tr>
            <td data-label="Rank">${index + 1}</td>
            <td data-label="Game Title">${escapeHtml(game.title)}</td>
            <td data-label="Category">${escapeHtml(game.category || 'N/A')}</td>
            <td data-label="Price">$${game.price.toFixed(2)}</td>
            <td data-label="Quantity Sold">${game.quantity_sold}</td>
            <td data-label="Revenue">$${game.revenue.toFixed(2)}</td>
            <td data-label="Avg Rating">${game.avg_rating ? game.avg_rating.toFixed(1) + ' ★' : 'N/A'}</td>
        </tr>
    `).join('');
}

/**
 * Export data in specified format
 */
function exportData(type, format) {
    const params = new URLSearchParams();
    params.set('days', currentFilters.days);
    params.set('type', type);
    if (currentFilters.category) params.set('category', currentFilters.category);
    
    const endpoint = format === 'csv' 
        ? `/store/api/analytics/export/csv/?${params.toString()}`
        : `/store/api/analytics/export/json/?${params.toString()}`;
    
    // Create temporary link and trigger download
    const link = document.createElement('a');
    link.href = endpoint;
    link.download = `gamevault_${type}_${new Date().toISOString().split('T')[0]}.${format}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showMessage(`Exporting ${type} data as ${format.toUpperCase()}...`, 'info');
}

/**
 * Show/hide loading indicator
 */
function showLoading(show) {
    const loading = document.getElementById('analyticsLoading');
    if (loading) {
        loading.style.display = show ? 'block' : 'none';
    }
}

/**
 * Get CSRF token from cookies
 */
function getCSRFToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

/**
 * Show toast message (uses global function from base.html)
 */
function showMessage(message, type) {
    if (typeof showToast === 'function') {
        showToast(message, type);
    } else {
        console.log(`[${type}] ${message}`);
    }
}
