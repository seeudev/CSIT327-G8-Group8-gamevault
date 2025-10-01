import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../services/api';
import './AdminDashboard.css';

/**
 * AdminDashboard Component
 * Main dashboard showing statistics and overview for admins
 */
const AdminDashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await api.get('/stats/');
      setStats(response.data);
    } catch (err) {
      setError('Failed to fetch dashboard statistics');
      console.error('Dashboard stats error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <div className="error-icon">⚠️</div>
        <h3>Error Loading Dashboard</h3>
        <p>{error}</p>
        <button onClick={fetchStats} className="retry-btn">
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      {/* Welcome Section */}
      <div className="dashboard-header">
        <div className="welcome-section">
          <h1>Welcome back, {user?.username}!</h1>
          <p>Here's what's happening with your GameVault store today.</p>
        </div>
        <div className="dashboard-actions">
          <button className="action-btn primary">
            📊 View Analytics
          </button>
          <button className="action-btn secondary">
            🎮 Add New Game
          </button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon games">🎮</div>
          <div className="stat-content">
            <h3>{stats?.games?.total || 0}</h3>
            <p>Total Games</p>
            <div className="stat-details">
              <span className="active">{stats?.games?.active || 0} active</span>
              <span className="featured">{stats?.games?.featured || 0} featured</span>
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon keys">🔑</div>
          <div className="stat-content">
            <h3>{stats?.keys?.total || 0}</h3>
            <p>Game Keys</p>
            <div className="stat-details">
              <span className="available">{stats?.keys?.available || 0} available</span>
              <span className="sold">{stats?.keys?.sold || 0} sold</span>
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon sales">💰</div>
          <div className="stat-content">
            <h3>${stats?.sales?.total_revenue?.toFixed(2) || '0.00'}</h3>
            <p>Total Revenue</p>
            <div className="stat-details">
              <span className="sales">{stats?.sales?.total_sales || 0} sales</span>
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon stock">📦</div>
          <div className="stat-content">
            <h3>{stats?.games?.out_of_stock || 0}</h3>
            <p>Out of Stock</p>
            <div className="stat-details">
              <span className="warning">Needs attention</span>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <h2>Quick Actions</h2>
        <div className="actions-grid">
          <div className="action-card">
            <div className="action-icon">🎮</div>
            <h3>Manage Games</h3>
            <p>Add, edit, or remove games from your store</p>
            <button className="action-btn">Manage Games</button>
          </div>

          <div className="action-card">
            <div className="action-icon">🔑</div>
            <h3>Add Game Keys</h3>
            <p>Bulk upload new game keys for existing games</p>
            <button className="action-btn">Add Keys</button>
          </div>

          <div className="action-card">
            <div className="action-icon">📊</div>
            <h3>View Analytics</h3>
            <p>Check sales performance and user engagement</p>
            <button className="action-btn">View Analytics</button>
          </div>

          <div className="action-card">
            <div className="action-icon">👥</div>
            <h3>Manage Users</h3>
            <p>View and manage user accounts and permissions</p>
            <button className="action-btn">Manage Users</button>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="recent-activity">
        <h2>Recent Activity</h2>
        <div className="activity-list">
          <div className="activity-item">
            <div className="activity-icon">🎮</div>
            <div className="activity-content">
              <h4>New game added</h4>
              <p>Cyberpunk 2077 was added to the store</p>
              <span className="activity-time">2 hours ago</span>
            </div>
          </div>

          <div className="activity-item">
            <div className="activity-icon">💰</div>
            <div className="activity-content">
              <h4>Sale completed</h4>
              <p>User purchased The Witcher 3: Wild Hunt</p>
              <span className="activity-time">4 hours ago</span>
            </div>
          </div>

          <div className="activity-item">
            <div className="activity-icon">🔑</div>
            <div className="activity-content">
              <h4>Keys added</h4>
              <p>50 new keys added for Grand Theft Auto V</p>
              <span className="activity-time">6 hours ago</span>
            </div>
          </div>

          <div className="activity-item">
            <div className="activity-icon">👤</div>
            <div className="activity-content">
              <h4>New user registered</h4>
              <p>New buyer account created</p>
              <span className="activity-time">8 hours ago</span>
            </div>
          </div>
        </div>
      </div>

      {/* Top Genres */}
      {stats?.genres && stats.genres.length > 0 && (
        <div className="top-genres">
          <h2>Top Genres</h2>
          <div className="genres-list">
            {stats.genres.slice(0, 5).map((genre, index) => (
              <div key={genre.genre} className="genre-item">
                <div className="genre-rank">#{index + 1}</div>
                <div className="genre-name">{genre.genre}</div>
                <div className="genre-count">{genre.count} games</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;
